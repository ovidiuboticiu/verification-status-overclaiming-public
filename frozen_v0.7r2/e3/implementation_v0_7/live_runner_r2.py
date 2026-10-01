from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from accounting_r2 import summarize_attempt
from attempts_r2 import AttemptRecord, InfrastructureFailure
from execution_identity import get_execution_identity
from live_request_builder import initial_request, continuation_request
from live_response_adapter import adapt_assistant_message, tool_result_message
from parser import parse_final
from runner_policy import classify_action
from scorer import score_episode
from simulator import execute_tool

DEFAULT_ENDPOINT = "http://127.0.0.1:1234/v1/chat/completions"


class UrllibTransport:
    def __init__(self, endpoint=DEFAULT_ENDPOINT, timeout_seconds=120):
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def post(self, payload):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise InfrastructureFailure("CONNECTION_LOSS", str(exc)) from exc
        except Exception as exc:
            raise InfrastructureFailure("RUNNER_EXCEPTION", str(exc)) from exc

        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise InfrastructureFailure(
                "RUNNER_EXCEPTION",
                "invalid JSON response",
            ) from exc


def _extract_message(response):
    try:
        message = response["choices"][0]["message"]
        if not isinstance(message, dict):
            raise TypeError
        return message
    except Exception as exc:
        raise InfrastructureFailure(
            "RUNNER_EXCEPTION",
            "response missing choices[0].message",
        ) from exc


def run_live_episode(row, transport):
    transcript = []
    raw_model_messages = []
    valid_tool_count = 0
    final_text = None
    model_failure = None

    base_request = initial_request(row)
    messages = list(base_request["messages"])

    while True:
        payload = continuation_request(base_request, messages)
        response = transport.post(payload)
        message = _extract_message(response)
        raw_model_messages.append(message)
        actions = adapt_assistant_message(message)
        messages.append(message)

        if len(actions) == 1 and actions[0]["kind"] == "final":
            final_text = actions[0].get("text")
            if not parse_final(final_text)["valid"]:
                model_failure = "FINAL_FORMAT_FAILURE"
            break

        terminate = False
        pending_tool_messages = []

        for action in actions:
            decision = classify_action(action, row, valid_tool_count)

            if decision.kind == "MODEL_BEHAVIOR_FAILURE":
                model_failure = decision.failure_subtype
                if isinstance(action.get("text"), str):
                    final_text = action["text"]
                terminate = True
                break

            if decision.kind != "VALID_TOOL":
                raise InfrastructureFailure(
                    "RUNNER_EXCEPTION",
                    f"unexpected live action decision: {decision}",
                )

            call = {"tool": action["tool"], "args": action["args"]}
            try:
                observation = execute_tool(row["case"], call)
            except Exception as exc:
                raise InfrastructureFailure(
                    "TOOL_DISPATCHER_BUG",
                    str(exc),
                ) from exc

            transcript.append(observation)
            valid_tool_count += 1
            pending_tool_messages.append(
                tool_result_message(
                    action.get("tool_call_id"),
                    observation["result"],
                )
            )

        if terminate:
            break

        messages.extend(pending_tool_messages)

    result = score_episode(
        row=row,
        transcript=transcript,
        final_text=final_text,
        model_behavior_failure=model_failure,
    )
    result.update(
        {
            "raw_model_messages": raw_model_messages,
            "tool_transcript": transcript,
            "valid_tool_call_n": valid_tool_count,
            "episode_terminated_after_model_failure": (
                model_failure is not None
            ),
        }
    )
    return result


def _append_jsonl(path, obj):
    line = json.dumps(obj, sort_keys=True, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def _write_new_json(path, obj):
    if path.exists():
        raise InfrastructureFailure(
            "ARTIFACT_IO_FAILURE",
            f"refusing overwrite: {path}",
        )
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_live_attempt(
    manifest_name,
    rows,
    attempt_id,
    output_dir,
    package_hash,
    manifest_hash,
    transport=None,
):
    if not rows:
        raise ValueError("official attempt cannot use empty manifest rows")

    transport = transport or UrllibTransport()
    output_dir = Path(output_dir)

    if output_dir.exists():
        raise InfrastructureFailure(
            "ARTIFACT_IO_FAILURE",
            f"attempt output directory already exists: {output_dir}",
        )
    output_dir.mkdir(parents=True, exist_ok=False)

    results_path = output_dir / "results.jsonl"
    log_path = output_dir / "run_log.jsonl"
    identity = get_execution_identity()

    attempt = AttemptRecord(
        attempt_id=attempt_id,
        manifest_name=manifest_name,
        expected_episode_n=len(rows),
    )
    started = time.time()

    _append_jsonl(
        log_path,
        {
            "event": "ATTEMPT_START",
            "attempt_id": attempt_id,
            "manifest_name": manifest_name,
            "package_hash": package_hash,
            "manifest_hash": manifest_hash,
            "execution_identity": identity,
            "unix_time": started,
        },
    )

    try:
        for row in rows:
            attempt.begin_episode(row["scenario_id"])
            _append_jsonl(
                log_path,
                {
                    "event": "EPISODE_START",
                    "attempt_id": attempt_id,
                    "scenario_id": row["scenario_id"],
                    "run_order": row["run_order"],
                    "unix_time": time.time(),
                },
            )

            record = run_live_episode(row, transport)
            attempt.append_episode(record)
            _append_jsonl(results_path, record)
            _append_jsonl(
                log_path,
                {
                    "event": "EPISODE_END",
                    "attempt_id": attempt_id,
                    "scenario_id": row["scenario_id"],
                    "model_behavior_failure": record["model_behavior_failure"],
                    "unix_time": time.time(),
                },
            )

        attempt.complete()

    except InfrastructureFailure as exc:
        attempt.invalidate(exc.subtype)
        _append_jsonl(
            log_path,
            {
                "event": "ATTEMPT_INVALIDATED",
                "attempt_id": attempt_id,
                "subtype": exc.subtype,
                "message": str(exc),
                "unix_time": time.time(),
            },
        )
        invalidation = {
            "attempt_id": attempt_id,
            "manifest_name": manifest_name,
            "status": "INVALID_INFRASTRUCTURE",
            "reason": exc.subtype,
            "message": str(exc),
            "package_hash": package_hash,
            "manifest_hash": manifest_hash,
            "execution_identity": identity,
            "attempted_scenario_ids": sorted(
                attempt.attempted_scenario_ids
            ),
            "episode_attempted_n": len(attempt.attempted_scenario_ids),
            "episode_record_n": len(attempt.episode_records),
            "canonical": False,
            "started_unix_time": started,
            "ended_unix_time": time.time(),
        }
        _write_new_json(
            output_dir / "INVALIDATION.json",
            invalidation,
        )
        _write_new_json(
            output_dir / "ATTEMPT_RUN_RECORD.json",
            invalidation,
        )
        return attempt

    summary = summarize_attempt(attempt)
    _write_new_json(output_dir / "summary.json", summary)
    _write_new_json(
        output_dir / "ATTEMPT_RUN_RECORD.json",
        {
            "attempt_id": attempt_id,
            "manifest_name": manifest_name,
            "status": attempt.status,
            "canonical": True,
            "package_hash": package_hash,
            "manifest_hash": manifest_hash,
            "execution_identity": identity,
            "attempted_scenario_ids": sorted(
                attempt.attempted_scenario_ids
            ),
            "episode_attempted_n": len(attempt.attempted_scenario_ids),
            "episode_record_n": len(attempt.episode_records),
            "started_unix_time": started,
            "ended_unix_time": time.time(),
        },
    )
    _append_jsonl(
        log_path,
        {
            "event": "ATTEMPT_END",
            "attempt_id": attempt_id,
            "status": attempt.status,
            "unix_time": time.time(),
        },
    )
    return attempt
