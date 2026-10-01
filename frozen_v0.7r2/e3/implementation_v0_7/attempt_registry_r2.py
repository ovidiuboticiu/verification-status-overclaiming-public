from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from attempts_r2 import InfrastructureFailure


def _registry_path(output_root: Path):
    return output_root / "RUN_RECORD.json"


def _empty_registry():
    return {
        "schema": "E3_RUN_RECORD_v0.7r2",
        "attempts": [],
        "canonical_valid_attempts": {},
    }


def load_registry(output_root: Path):
    path = _registry_path(output_root)
    if not path.exists():
        return _empty_registry()
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temp, path)


@contextmanager
def exclusive_registry_lock(output_root: Path):
    output_root.mkdir(parents=True, exist_ok=True)
    lock_path = output_root / ".official_runner.lock"
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise InfrastructureFailure(
            "ARTIFACT_IO_FAILURE",
            "another official runner appears active; lock exists",
        ) from exc
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def reserve_attempt(
    output_root: Path,
    attempt_id: str,
    phase_key: str,
    package_hash: str,
    manifest_hash: str,
    execution_identity: dict,
):
    registry = load_registry(output_root)
    if any(x.get("attempt_id") == attempt_id for x in registry["attempts"]):
        raise ValueError(f"attempt_id already exists: {attempt_id}")

    if registry["canonical_valid_attempts"].get(phase_key):
        raise ValueError(
            f"canonical valid attempt already exists for {phase_key}; "
            "a second scientific execution is prohibited"
        )

    prior = [
        x for x in registry["attempts"]
        if x.get("phase_key") == phase_key
    ]
    for row in prior:
        if row.get("package_hash") != package_hash:
            raise ValueError("restart package hash differs from prior attempt")
        if row.get("manifest_hash") != manifest_hash:
            raise ValueError("restart manifest hash differs from prior attempt")
        if row.get("execution_identity") != execution_identity:
            raise ValueError("restart execution identity differs from prior attempt")
        if row.get("status") not in {"INVALID_INFRASTRUCTURE"}:
            raise ValueError(
                "restart allowed only after INVALID_INFRASTRUCTURE"
            )

    record = {
        "attempt_id": attempt_id,
        "phase_key": phase_key,
        "status": "RUNNING",
        "started_unix_time": time.time(),
        "ended_unix_time": None,
        "package_hash": package_hash,
        "manifest_hash": manifest_hash,
        "execution_identity": execution_identity,
        "invalidation_reason": None,
        "canonical": False,
    }
    registry["attempts"].append(record)
    _atomic_write_json(_registry_path(output_root), registry)
    return record


def finalize_attempt(
    output_root: Path,
    attempt_id: str,
    status: str,
    invalidation_reason=None,
):
    registry = load_registry(output_root)
    matches = [x for x in registry["attempts"] if x.get("attempt_id") == attempt_id]
    if len(matches) != 1:
        raise ValueError("attempt registry entry missing or duplicated")
    row = matches[0]
    if row.get("status") != "RUNNING":
        raise ValueError("attempt registry entry already finalized")

    if status not in {"VALID", "INVALID_INFRASTRUCTURE"}:
        raise ValueError("invalid final attempt status")

    row["status"] = status
    row["ended_unix_time"] = time.time()
    row["invalidation_reason"] = invalidation_reason
    row["canonical"] = status == "VALID"

    if status == "VALID":
        phase_key = row["phase_key"]
        if registry["canonical_valid_attempts"].get(phase_key):
            raise ValueError("canonical valid attempt already registered")
        registry["canonical_valid_attempts"][phase_key] = attempt_id

    _atomic_write_json(_registry_path(output_root), registry)
    return row
