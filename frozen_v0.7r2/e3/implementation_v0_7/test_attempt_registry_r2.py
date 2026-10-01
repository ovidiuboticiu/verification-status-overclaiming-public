from __future__ import annotations

import json
import tempfile
from pathlib import Path

from attempt_registry_r2 import (
    finalize_attempt,
    load_registry,
    reserve_attempt,
)
from execution_identity import get_execution_identity

checks = []


def ck(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


identity = get_execution_identity()

with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    reserve_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "A",
        "pkg",
        "man",
        identity,
    )
    registry = load_registry(root)
    ck("reserve_recorded", len(registry["attempts"]) == 1)
    ck("reserve_running", registry["attempts"][0]["status"] == "RUNNING")

    duplicate_rejected = False
    try:
        reserve_attempt(
            root,
            "E3A-OFFICIAL-ATTEMPT-001",
            "A",
            "pkg",
            "man",
            identity,
        )
    except ValueError:
        duplicate_rejected = True
    ck("duplicate_attempt_id_rejected", duplicate_rejected)

    finalize_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "INVALID_INFRASTRUCTURE",
        "CONNECTION_LOSS",
    )

    reserve_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-002",
        "A",
        "pkg",
        "man",
        identity,
    )
    finalize_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-002",
        "VALID",
        None,
    )

    registry = load_registry(root)
    ck(
        "canonical_valid_recorded",
        registry["canonical_valid_attempts"]["A"]
        == "E3A-OFFICIAL-ATTEMPT-002",
    )
    ck("all_attempts_retained", len(registry["attempts"]) == 2)

    after_valid_rejected = False
    try:
        reserve_attempt(
            root,
            "E3A-OFFICIAL-ATTEMPT-003",
            "A",
            "pkg",
            "man",
            identity,
        )
    except ValueError:
        after_valid_rejected = True
    ck("second_after_valid_rejected", after_valid_rejected)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    reserve_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "A",
        "pkg",
        "man",
        identity,
    )
    finalize_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "INVALID_INFRASTRUCTURE",
        "HOST_FAILURE",
    )

    package_change_rejected = False
    try:
        reserve_attempt(
            root,
            "E3A-OFFICIAL-ATTEMPT-002",
            "A",
            "different-pkg",
            "man",
            identity,
        )
    except ValueError:
        package_change_rejected = True
    ck("restart_package_change_rejected", package_change_rejected)

    manifest_change_rejected = False
    try:
        reserve_attempt(
            root,
            "E3A-OFFICIAL-ATTEMPT-002",
            "A",
            "pkg",
            "different-man",
            identity,
        )
    except ValueError:
        manifest_change_rejected = True
    ck("restart_manifest_change_rejected", manifest_change_rejected)

report = {
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks": len(checks),
    "failures": [x["name"] for x in checks if not x["pass"]],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
