from __future__ import annotations

import json

from accounting_r2 import summarize_attempt
from attempts_r2 import (
    AttemptRecord,
    InfrastructureFailure,
    validate_attempt_id,
)
from manifest_loader import MANIFEST_SPECS, load_manifest, manifest_sha256
from phase_analysis import analyze_e3a, analyze_e3b


checks = []


def ck(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def scored_shell(row):
    return {
        "scenario_id": row["scenario_id"],
        "stage": row["stage"],
        "run_order": row["run_order"],
        "family": row["family"],
        "template_id": row["template_id"],
        "instance_id": row.get("instance_id"),
        "case_role": row["case_role"],
        "status_parse_valid": True,
        "claim_parse_valid": True,
        "model_behavior_failure": None,
        "decisive_evidence_acquired": row["case_role"] == "control",
        "claim_correct": True,
        "evidence_status_correct": True,
        "control_complete_success": row["case_role"] == "control",
        "status_overclaim": False,
    }


for key, spec in MANIFEST_SPECS.items():
    rows = load_manifest(key)
    ck(f"{key}:row_count", len(rows) == spec["rows"])
    ck(f"{key}:hash", manifest_sha256(key) == spec["sha256"])
    ck(
        f"{key}:run_order",
        [r["run_order"] for r in rows] == list(range(1, spec["rows"] + 1)),
    )

ck(
    "attempt_id:A_valid",
    validate_attempt_id("E3A-OFFICIAL-ATTEMPT-001", "A"),
)
ck(
    "attempt_id:A_reject_B",
    not validate_attempt_id("E3B-F1-OFFICIAL-ATTEMPT-001", "A"),
)
ck(
    "attempt_id:B_F3_valid",
    validate_attempt_id(
        "E3B-F3-OFFICIAL-ATTEMPT-002",
        "B",
        family="F3",
    ),
)
ck(
    "attempt_id:B_family_mismatch",
    not validate_attempt_id(
        "E3B-F2-OFFICIAL-ATTEMPT-002",
        "B",
        family="F3",
    ),
)

attempt = AttemptRecord(
    "E3A-OFFICIAL-ATTEMPT-001",
    "mock",
    expected_episode_n=2,
)
attempt.begin_episode("s1")
attempt.append_episode({"scenario_id": "s1"})
try:
    attempt.complete()
    incomplete_rejected = False
except InfrastructureFailure:
    incomplete_rejected = True
ck("attempt:incomplete_rejected", incomplete_rejected)

attempt.begin_episode("s2")
attempt.append_episode({"scenario_id": "s2"})
attempt.complete()
ck("attempt:complete_valid", attempt.status == "VALID")

a_rows = load_manifest("A")
a_records = [scored_shell(r) for r in a_rows]
a0 = analyze_e3a(a_records)
ck("A:no_candidate", a0["selected_family"] is None)
ck("A:closure_no_candidate", a0["closure_if_no_candidate"] is True)

tie_records = [dict(x) for x in a_records]
for family in ("F2", "F3"):
    changed = 0
    for row in tie_records:
        if row["family"] == family and row["case_role"] == "forced":
            row["status_overclaim"] = True
            changed += 1
            if changed == 2:
                break
tie = analyze_e3a(tie_records)
ck("A:tie_break_F2", tie["selected_family"] == "F2")

max_records = [dict(x) for x in a_records]
for row in max_records:
    if row["family"] == "F1" and row["case_role"] == "forced":
        row["status_overclaim"] = True
        break
count = 0
for row in max_records:
    if row["family"] == "F4" and row["case_role"] == "forced":
        row["status_overclaim"] = True
        count += 1
        if count == 3:
            break
mx = analyze_e3a(max_records)
ck("A:max_count_over_priority", mx["selected_family"] == "F4")

ineligible = [dict(x) for x in a_records]
for row in ineligible:
    if row["family"] == "F1" and row["case_role"] == "control":
        row["control_complete_success"] = False
        break
for row in ineligible:
    if row["family"] == "F1" and row["case_role"] == "forced":
        row["status_overclaim"] = True
        break
ie = analyze_e3a(ineligible)
ck("A:ineligible_cannot_nominate", ie["selected_family"] is None)

b_rows = load_manifest("B_F1")
b_records = [scored_shell(r) for r in b_rows]
b0 = analyze_e3b(b_records, "F1")
ck("B:no_overclaim_label", b0["e3b_result"] == "NOT_REPLICATED_HELD_OUT")
ck("B:no_overclaim_boolean", b0["held_out_occurrence"] is False)

one = [dict(x) for x in b_records]
for row in one:
    if row["case_role"] == "forced":
        row["status_overclaim"] = True
        break
b1 = analyze_e3b(one, "F1")
ck("B:held_out_occurrence", b1["held_out_occurrence"] is True)
ck("B:one_not_template_rep", b1["template_instance_replication"] is False)
ck("B:one_not_family_rep", b1["family_level_replication"] is False)

same_template = [dict(x) for x in b_records]
chosen_template = "T1"
seen_instances = set()
for row in same_template:
    if (
        row["case_role"] == "forced"
        and row["template_id"] == chosen_template
        and row["instance_id"] not in seen_instances
    ):
        row["status_overclaim"] = True
        seen_instances.add(row["instance_id"])
        if len(seen_instances) == 2:
            break
bt = analyze_e3b(same_template, "F1")
ck("B:template_instance_rep", bt["template_instance_replication"] is True)
ck("B:template_not_family_rep", bt["family_level_replication"] is False)

cross_template = [dict(x) for x in b_records]
seen_templates = set()
for row in cross_template:
    if row["case_role"] == "forced" and row["template_id"] not in seen_templates:
        row["status_overclaim"] = True
        seen_templates.add(row["template_id"])
        if len(seen_templates) == 2:
            break
bf = analyze_e3b(cross_template, "F1")
ck("B:family_level_rep", bf["family_level_replication"] is True)

control_fail = [dict(x) for x in b_records]
for row in control_fail:
    if row["case_role"] == "control":
        row["control_complete_success"] = False
        break
bc = analyze_e3b(control_fail, "F1")
ck(
    "B:control_failure",
    bc["e3b_result"] == "INCONCLUSIVE_CONTROL_FAILURE",
)

summary_attempt = AttemptRecord(
    "E3B-F1-OFFICIAL-ATTEMPT-001",
    "mock",
    expected_episode_n=2,
)
summary_attempt.begin_episode("f")
summary_attempt.append_episode(
    {
        "scenario_id": "f",
        "family": "F1",
        "case_role": "forced",
        "model_behavior_failure": None,
        "claim_parse_valid": True,
        "status_parse_valid": True,
        "status_overclaim": True,
        "decisive_evidence_acquired": False,
        "claim_correct": False,
        "evidence_status_correct": False,
        "control_complete_success": False,
    }
)
summary_attempt.begin_episode("c")
summary_attempt.append_episode(
    {
        "scenario_id": "c",
        "family": "F1",
        "case_role": "control",
        "model_behavior_failure": None,
        "claim_parse_valid": True,
        "status_parse_valid": True,
        "status_overclaim": False,
        "decisive_evidence_acquired": True,
        "claim_correct": True,
        "evidence_status_correct": True,
        "control_complete_success": True,
    }
)
summary_attempt.complete()
summary = summarize_attempt(summary_attempt)
ck("OL3:manifest_episode_n", summary["manifest_episode_n"] == 2)
ck("OL3:episode_attempted_n", summary["episode_attempted_n"] == 2)
ck("OL3:forced_opportunity_n", summary["forced_opportunity_n"] == 1)
ck("OL3:forced_overclaim_n", summary["forced_status_overclaim_n"] == 1)
ck(
    "OL3:control_acquisition",
    summary["control_decisive_evidence_acquired_n"] == 1,
)
ck("OL3:control_claim_correct", summary["control_claim_correct_n"] == 1)
ck(
    "OL3:control_status_correct",
    summary["control_evidence_status_correct_n"] == 1,
)
ck("OL3:control_complete", summary["control_complete_success_n"] == 1)

report = {
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks": len(checks),
    "failures": [x["name"] for x in checks if not x["pass"]],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
