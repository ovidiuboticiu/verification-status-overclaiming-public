from __future__ import annotations

import json
import tempfile
from pathlib import Path

from attempt_registry_r2 import finalize_attempt, reserve_attempt
from official_runner_r2 import prepare_official_phase

checks = []


def ck(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


with tempfile.TemporaryDirectory() as td:
    root = Path(td)

    prepared_a = prepare_official_phase(
        phase="A",
        attempt_id="E3A-OFFICIAL-ATTEMPT-001",
        output_root=root,
    )
    ck("A_rows_48", len(prepared_a["rows"]) == 48)
    ck("A_key", prepared_a["manifest_key"] == "A")
    ck("A_manifest_hash_len", len(prepared_a["manifest_hash"]) == 64)
    ck("package_hash_len", len(prepared_a["package_hash"]) == 64)

    invalid_id_rejected = False
    try:
        prepare_official_phase(
            phase="A",
            attempt_id="BAD-ID",
            output_root=root,
        )
    except ValueError:
        invalid_id_rejected = True
    ck("invalid_A_id_rejected", invalid_id_rejected)

    reserve_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "A",
        prepared_a["package_hash"],
        prepared_a["manifest_hash"],
        prepared_a["execution_identity"],
    )
    finalize_attempt(
        root,
        "E3A-OFFICIAL-ATTEMPT-001",
        "VALID",
        None,
    )

    a_analysis = {
        "phase": "E3-A",
        "attempt_id": "E3A-OFFICIAL-ATTEMPT-001",
        "package_hash": prepared_a["package_hash"],
        "manifest_hash": prepared_a["manifest_hash"],
        "selected_family": "F3",
        "e3b_required": True,
    }
    (root / "E3A_PHASE_ANALYSIS.json").write_text(
        json.dumps(a_analysis, indent=2) + "\n",
        encoding="utf-8",
    )

    prepared_b = prepare_official_phase(
        phase="B",
        attempt_id="E3B-F3-OFFICIAL-ATTEMPT-001",
        output_root=root,
    )
    ck("B_family_selected_from_A", prepared_b["family"] == "F3")
    ck("B_rows_24", len(prepared_b["rows"]) == 24)
    ck("B_manifest_key", prepared_b["manifest_key"] == "B_F3")

    wrong_family_id_rejected = False
    try:
        prepare_official_phase(
            phase="B",
            attempt_id="E3B-F2-OFFICIAL-ATTEMPT-001",
            output_root=root,
        )
    except ValueError:
        wrong_family_id_rejected = True
    ck("wrong_B_family_id_rejected", wrong_family_id_rejected)

report = {
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks": len(checks),
    "failures": [x["name"] for x in checks if not x["pass"]],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
