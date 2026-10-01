from __future__ import annotations

import importlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_ZIP = ROOT / "artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip"
RESULTS_PATH = ROOT / "results/official/attempts/E3A-OFFICIAL-ATTEMPT-001/results.jsonl"
OFFICIAL_PHASE = ROOT / "results/official/E3A_PHASE_ANALYSIS.json"
OFFICIAL_SUMMARY = ROOT / "results/official/attempts/E3A-OFFICIAL-ATTEMPT-001/summary.json"

SCORE_KEYS = {
    "scenario_id", "stage", "run_order", "family", "template_id", "instance_id",
    "pair_id", "parameter_tuple_id", "semantic_template_signature",
    "observable_case_signature", "mirror", "target", "case_role", "oracle_states",
    "oracle_claim_value", "oracle_evidence_status", "final_parse_valid",
    "claim_parse_valid", "status_parse_valid", "agent_claim_value",
    "agent_evidence_status", "model_behavior_failure", "decisive_evidence_acquired",
    "claim_correct", "evidence_status_correct", "status_overclaim", "status_underclaim",
    "claim_overclaim", "claim_underclaim", "joint_incoherence", "control_complete_success",
}

def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def final_text(record: dict) -> str | None:
    for message in reversed(record.get("raw_model_messages", [])):
        if message.get("role") == "assistant" and message.get("content") is not None:
            content = message.get("content")
            if content:
                return content
    return None

def independent_summary(records: list[dict]) -> dict:
    forced = [r for r in records if r["case_role"] == "forced"]
    controls = [r for r in records if r["case_role"] == "control"]
    by_family = {}
    for family in ("F1", "F2", "F3", "F4"):
        rows = [r for r in records if r["family"] == family]
        ff = [r for r in rows if r["case_role"] == "forced"]
        fc = [r for r in rows if r["case_role"] == "control"]
        by_family[family] = {
            "episode_attempted_n": len(rows),
            "forced_opportunity_n": len(ff),
            "forced_parse_valid_status_n": sum(bool(r["status_parse_valid"]) for r in ff),
            "forced_status_overclaim_n": sum(bool(r["status_overclaim"]) for r in ff),
            "control_n": len(fc),
            "control_decisive_evidence_acquired_n": sum(bool(r["decisive_evidence_acquired"]) for r in fc),
            "control_claim_correct_n": sum(bool(r["claim_correct"]) for r in fc),
            "control_evidence_status_correct_n": sum(bool(r["evidence_status_correct"]) for r in fc),
            "control_complete_success_n": sum(bool(r["control_complete_success"]) for r in fc),
        }
    return {
        "manifest_episode_n": 48,
        "episode_attempted_n": len(records),
        "episode_record_n": len(records),
        "normal_completion_n": sum(r["model_behavior_failure"] is None for r in records),
        "model_behavior_failure_n": sum(r["model_behavior_failure"] is not None for r in records),
        "model_behavior_failures_by_subtype": {},
        "final_claim_parse_valid_n": sum(bool(r["claim_parse_valid"]) for r in records),
        "final_status_parse_valid_n": sum(bool(r["status_parse_valid"]) for r in records),
        "forced_opportunity_n": len(forced),
        "forced_parse_valid_status_n": sum(bool(r["status_parse_valid"]) for r in forced),
        "forced_status_overclaim_n": sum(bool(r["status_overclaim"]) for r in forced),
        "control_n": len(controls),
        "control_decisive_evidence_acquired_n": sum(bool(r["decisive_evidence_acquired"]) for r in controls),
        "control_claim_correct_n": sum(bool(r["claim_correct"]) for r in controls),
        "control_evidence_status_correct_n": sum(bool(r["evidence_status_correct"]) for r in controls),
        "control_complete_success_n": sum(bool(r["control_complete_success"]) for r in controls),
        "by_family": by_family,
    }

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vso_e3_recalc_") as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(FROZEN_ZIP, "r") as zf:
            zf.extractall(tmp)

        module_dir = tmp / "e3/implementation_v0_7"
        sys.path.insert(0, str(module_dir))
        try:
            manifest_loader = importlib.import_module("manifest_loader")
            scorer = importlib.import_module("scorer")
            phase_analysis = importlib.import_module("phase_analysis")

            manifest_rows = manifest_loader.load_manifest("A")
            by_id = {row["scenario_id"]: row for row in manifest_rows}
            stored_records = load_jsonl(RESULTS_PATH)

            if len(stored_records) != 48:
                raise AssertionError(f"expected 48 stored records, got {len(stored_records)}")
            if [r["scenario_id"] for r in stored_records] != [r["scenario_id"] for r in manifest_rows]:
                raise AssertionError("stored scenario IDs/order differ from frozen manifest")

            recomputed = []
            mismatches = []
            for stored in stored_records:
                row = by_id[stored["scenario_id"]]
                rescored = scorer.score_episode(
                    row,
                    stored["tool_transcript"],
                    final_text(stored),
                    stored.get("model_behavior_failure"),
                )
                recomputed.append(rescored)
                for key in sorted(SCORE_KEYS):
                    if rescored.get(key) != stored.get(key):
                        mismatches.append({
                            "scenario_id": stored["scenario_id"],
                            "field": key,
                            "stored": stored.get(key),
                            "recomputed": rescored.get(key),
                        })

            phase = phase_analysis.analyze_e3a(recomputed)
            stored_phase = json.loads(OFFICIAL_PHASE.read_text(encoding="utf-8"))
            phase_reference = {k: stored_phase[k] for k in phase}
            phase_exact_match = phase == phase_reference

            summary = independent_summary(recomputed)
            stored_summary = json.loads(OFFICIAL_SUMMARY.read_text(encoding="utf-8"))
            summary_reference = {k: stored_summary[k] for k in summary}
            summary_exact_match = summary == summary_reference

            report = {
                "status": "PASS" if not mismatches and phase_exact_match and summary_exact_match else "FAIL",
                "raw_episode_records": len(stored_records),
                "per_episode_rescoring_mismatch_n": len(mismatches),
                "phase_analysis_exact_match": phase_exact_match,
                "summary_exact_match": summary_exact_match,
                "forced_status_overclaim_n": summary["forced_status_overclaim_n"],
                "forced_opportunity_n": summary["forced_opportunity_n"],
                "control_complete_success_n": summary["control_complete_success_n"],
                "control_n": summary["control_n"],
                "eligible_candidate_families": phase["eligible_candidate_families"],
                "selected_family": phase["selected_family"],
                "e3b_required": phase["e3b_required"],
                "mismatches": mismatches,
            }
            print(json.dumps(report, indent=2))
            return 0 if report["status"] == "PASS" else 1
        finally:
            sys.path.remove(str(module_dir))
            for name in ["manifest_loader", "scorer", "phase_analysis", "oracle_primary", "parser"]:
                sys.modules.pop(name, None)

if __name__ == "__main__":
    raise SystemExit(main())
