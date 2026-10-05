from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/official/attempts/E3A-OFFICIAL-ATTEMPT-001/results.jsonl"


def load_records() -> list[dict]:
    return [
        json.loads(line)
        for line in RESULTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def direct_f3_oracle(record: dict) -> tuple[str, str] | None:
    if record.get("family") != "F3":
        return None

    bundle = None
    resolved_source = None

    for obs in record.get("tool_transcript", []):
        if obs.get("tool") == "read_source_bundle":
            bundle = obs.get("result")
        elif obs.get("tool") == "resolve_authority_token":
            result = obs.get("result") or {}
            resolved_source = result.get("authoritative_source_id")

    if bundle is None or resolved_source is None:
        return None

    value_by_source = {
        item["source_id"]: item["value"]
        for item in bundle
        if "source_id" in item and "value" in item
    }
    if resolved_source not in value_by_source:
        return None

    authoritative_value = value_by_source[resolved_source]
    target = record["target"]
    claim = "TRUE" if authoritative_value == target else "FALSE"
    return claim, "SUFFICIENT"


def main() -> int:
    records = load_records()
    controls = [r for r in records if r.get("case_role") == "control"]
    f3_controls = [r for r in controls if r.get("family") == "F3"]

    rows = []
    semantic_success = 0
    for record in f3_controls:
        semantic = direct_f3_oracle(record)
        if semantic is None:
            raise AssertionError(
                f"F3 control lacks directly resolved authority: {record['scenario_id']}"
            )
        oracle_claim, oracle_status = semantic
        claim_correct = record.get("agent_claim_value") == oracle_claim
        status_correct = record.get("agent_evidence_status") == oracle_status
        complete = (
            record.get("model_behavior_failure") is None
            and claim_correct
            and status_correct
        )
        semantic_success += int(complete)
        rows.append(
            {
                "scenario_id": record["scenario_id"],
                "frozen_oracle_claim": record.get("oracle_claim_value"),
                "frozen_oracle_status": record.get("oracle_evidence_status"),
                "diagnostic_oracle_claim": oracle_claim,
                "diagnostic_oracle_status": oracle_status,
                "agent_claim": record.get("agent_claim_value"),
                "agent_status": record.get("agent_evidence_status"),
                "diagnostic_complete_success": complete,
            }
        )

    frozen_total = sum(bool(r.get("control_complete_success")) for r in controls)
    frozen_non_f3 = sum(
        bool(r.get("control_complete_success"))
        for r in controls
        if r.get("family") != "F3"
    )
    diagnostic_total = frozen_non_f3 + semantic_success

    report = {
        "status": "DIAGNOSTIC_ONLY",
        "frozen_scores_changed": False,
        "f3_control_n": len(f3_controls),
        "f3_frozen_complete_success_n": sum(
            bool(r.get("control_complete_success")) for r in f3_controls
        ),
        "f3_diagnostic_complete_success_n": semantic_success,
        "all_controls_frozen_complete_success_n": frozen_total,
        "all_controls_diagnostic_complete_success_n": diagnostic_total,
        "competence_gate_threshold_per_family": 6,
        "f3_reaches_gate_under_diagnostic_semantics": semantic_success == 6,
        "rows": rows,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
