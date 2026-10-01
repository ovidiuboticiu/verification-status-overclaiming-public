from __future__ import annotations

import json

from manifest_loader import load_manifest
from runner_policy import (
    INFRASTRUCTURE_FAILURES,
    MODEL_FAILURES,
    classify_action,
)

checks = []


def ck(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


row = load_manifest("A")[0]
legal = row["legal_tool_calls"][0]

valid = {
    "kind": "tool_call",
    "tool": legal["tool"],
    "args": legal.get("args", []),
}
ck("valid_tool", classify_action(valid, row, 0).kind == "VALID_TOOL")

malformed = {"kind": "tool_call", "tool": legal["tool"], "args": "bad"}
d = classify_action(malformed, row, 0)
ck(
    "malformed_tool_call",
    d.kind == "MODEL_BEHAVIOR_FAILURE"
    and d.failure_subtype == "MALFORMED_TOOL_CALL",
)

unknown = {
    "kind": "tool_call",
    "tool": "not_a_frozen_tool",
    "args": [],
}
d = classify_action(unknown, row, 0)
ck(
    "unknown_tool",
    d.kind == "MODEL_BEHAVIOR_FAILURE"
    and d.failure_subtype == "UNKNOWN_TOOL",
)

wrong_args = {
    "kind": "tool_call",
    "tool": legal["tool"],
    "args": ["OUTSIDE_FROZEN_DOMAIN"],
}
d = classify_action(wrong_args, row, 0)
ck(
    "out_of_domain_argument",
    d.kind == "MODEL_BEHAVIOR_FAILURE"
    and d.failure_subtype == "OUT_OF_DOMAIN_ARGUMENT",
)

d = classify_action(valid, row, 4)
ck(
    "fifth_tool_attempt",
    d.kind == "MODEL_BEHAVIOR_FAILURE"
    and d.failure_subtype == "TOOL_LIMIT_ATTEMPT",
)

d = classify_action(
    {
        "kind": "final",
        "text": "CLAIM_VALUE: UNKNOWN\nEVIDENCE_STATUS: INSUFFICIENT",
    },
    row,
    0,
)
ck("final_action", d.kind == "FINAL")

ck(
    "model_infra_failure_sets_disjoint",
    MODEL_FAILURES.isdisjoint(INFRASTRUCTURE_FAILURES),
)

required_model_failures = {
    "UNKNOWN_TOOL",
    "OUT_OF_DOMAIN_ARGUMENT",
    "MALFORMED_TOOL_CALL",
    "TOOL_LIMIT_ATTEMPT",
    "FINAL_FORMAT_FAILURE",
}
ck(
    "required_model_failure_subtypes",
    required_model_failures.issubset(MODEL_FAILURES),
)

report = {
    "status": "PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks": len(checks),
    "failures": [x["name"] for x in checks if not x["pass"]],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
