from __future__ import annotations

from collections import Counter


def summarize_attempt(attempt):
    records = list(attempt.episode_records)
    failures = Counter(
        r.get("model_behavior_failure")
        for r in records
        if r.get("model_behavior_failure") is not None
    )
    forced = [r for r in records if r.get("case_role") == "forced"]
    controls = [r for r in records if r.get("case_role") == "control"]

    by_family = {}
    for family in ("F1", "F2", "F3", "F4"):
        rows = [r for r in records if r.get("family") == family]
        if not rows:
            continue
        f_forced = [r for r in rows if r.get("case_role") == "forced"]
        f_controls = [r for r in rows if r.get("case_role") == "control"]
        by_family[family] = {
            "episode_attempted_n": len(rows),
            "forced_opportunity_n": len(f_forced),
            "forced_parse_valid_status_n": sum(
                bool(r.get("status_parse_valid")) for r in f_forced
            ),
            "forced_status_overclaim_n": sum(
                bool(r.get("status_overclaim")) for r in f_forced
            ),
            "control_n": len(f_controls),
            "control_decisive_evidence_acquired_n": sum(
                bool(r.get("decisive_evidence_acquired")) for r in f_controls
            ),
            "control_claim_correct_n": sum(
                bool(r.get("claim_correct")) for r in f_controls
            ),
            "control_evidence_status_correct_n": sum(
                bool(r.get("evidence_status_correct")) for r in f_controls
            ),
            "control_complete_success_n": sum(
                bool(r.get("control_complete_success")) for r in f_controls
            ),
        }

    return {
        "attempt_id": attempt.attempt_id,
        "attempt_status": attempt.status,
        "invalidation_reason": attempt.invalidation_reason,
        "manifest_episode_n": attempt.expected_episode_n,
        "episode_attempted_n": len(attempt.attempted_scenario_ids),
        "episode_record_n": len(records),
        "normal_completion_n": sum(
            r.get("model_behavior_failure") is None for r in records
        ),
        "model_behavior_failure_n": sum(
            r.get("model_behavior_failure") is not None for r in records
        ),
        "model_behavior_failures_by_subtype": dict(sorted(failures.items())),
        "final_claim_parse_valid_n": sum(
            bool(r.get("claim_parse_valid")) for r in records
        ),
        "final_status_parse_valid_n": sum(
            bool(r.get("status_parse_valid")) for r in records
        ),
        "forced_opportunity_n": len(forced),
        "forced_parse_valid_status_n": sum(
            bool(r.get("status_parse_valid")) for r in forced
        ),
        "forced_status_overclaim_n": sum(
            bool(r.get("status_overclaim")) for r in forced
        ),
        "control_n": len(controls),
        "control_decisive_evidence_acquired_n": sum(
            bool(r.get("decisive_evidence_acquired")) for r in controls
        ),
        "control_claim_correct_n": sum(
            bool(r.get("claim_correct")) for r in controls
        ),
        "control_evidence_status_correct_n": sum(
            bool(r.get("evidence_status_correct")) for r in controls
        ),
        "control_complete_success_n": sum(
            bool(r.get("control_complete_success")) for r in controls
        ),
        "by_family": by_family,
    }
