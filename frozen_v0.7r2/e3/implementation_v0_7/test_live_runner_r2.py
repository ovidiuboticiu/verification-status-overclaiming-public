from __future__ import annotations

import json
import tempfile
from pathlib import Path

from live_runner_r2 import run_live_attempt, run_live_episode
from manifest_loader import load_manifest


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def post(self, payload):
        self.requests.append(payload)
        return self.responses.pop(0)


def final_response(text):
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": text,
            }
        }]
    }


checks = []


def ck(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


rows = load_manifest("A")
forced_rows = [r for r in rows if r["case_role"] == "forced"]

safe_final = "CLAIM_VALUE: UNKNOWN\nEVIDENCE_STATUS: INSUFFICIENT"

transport = FakeTransport([final_response(safe_final)])
record = run_live_episode(forced_rows[0], transport)
ck("direct_final_parse", record["final_parse_valid"])
ck("direct_final_correct", record["evidence_status_correct"])
ck("direct_final_no_overclaim", not record["status_overclaim"])

with tempfile.TemporaryDirectory() as td:
    transport = FakeTransport([
        final_response(safe_final),
        final_response(safe_final),
    ])
    attempt = run_live_attempt(
        manifest_name="mock-two",
        rows=forced_rows[:2],
        attempt_id="E3A-OFFICIAL-ATTEMPT-998",
        output_dir=Path(td) / "attempt",
        package_hash="mock-package",
        manifest_hash="mock-manifest",
        transport=transport,
    )
    out = Path(td) / "attempt"
    summary = json.loads(
        (out / "summary.json").read_text(encoding="utf-8")
    )
    run_record = json.loads(
        (out / "ATTEMPT_RUN_RECORD.json").read_text(encoding="utf-8")
    )
    ck("attempt_valid", attempt.status == "VALID")
    ck("manifest_n", summary["manifest_episode_n"] == 2)
    ck("attempted_n", summary["episode_attempted_n"] == 2)
    ck("identity_recorded", "execution_identity" in run_record)

report = {
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks": len(checks),
    "failures": [x["name"] for x in checks if not x["pass"]],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
