from __future__ import annotations
from dataclasses import dataclass

MAX_TOOL_CALLS = 4
KNOWN_TOOLS = {
    "read_snapshot", "read_head_meta", "read_version_exists",
    "read_preop_snapshot", "read_operation_record", "read_operation_phase",
    "read_source_bundle", "read_authority_meta", "resolve_authority_token",
    "read_event_bundle", "read_order_graph", "read_graph_meta",
}

MODEL_FAILURES = {
    "UNKNOWN_TOOL",
    "OUT_OF_DOMAIN_ARGUMENT",
    "MALFORMED_TOOL_CALL",
    "TOOL_LIMIT_ATTEMPT",
    "FINAL_FORMAT_FAILURE",
}

INFRASTRUCTURE_FAILURES = {
    "CONNECTION_LOSS",
    "RUNTIME_CRASH",
    "RUNNER_EXCEPTION",
    "TOOL_DISPATCHER_BUG",
    "ARTIFACT_IO_FAILURE",
    "HOST_FAILURE",
}

@dataclass
class ActionDecision:
    kind: str
    failure_subtype: str | None = None

def classify_action(action, row, valid_tool_count):
    if not isinstance(action, dict) or action.get("kind") not in {"tool_call", "final"}:
        return ActionDecision("MODEL_BEHAVIOR_FAILURE", "MALFORMED_TOOL_CALL")

    if action["kind"] == "final":
        return ActionDecision("FINAL")

    tool = action.get("tool")
    args = action.get("args")
    if not isinstance(tool, str) or not isinstance(args, list):
        return ActionDecision("MODEL_BEHAVIOR_FAILURE", "MALFORMED_TOOL_CALL")

    if valid_tool_count >= MAX_TOOL_CALLS:
        return ActionDecision("MODEL_BEHAVIOR_FAILURE", "TOOL_LIMIT_ATTEMPT")

    if tool not in KNOWN_TOOLS:
        return ActionDecision("MODEL_BEHAVIOR_FAILURE", "UNKNOWN_TOOL")

    proposed = (tool, tuple(args))
    allowed = {(x["tool"], tuple(x.get("args", []))) for x in row["legal_tool_calls"]}
    if proposed not in allowed:
        return ActionDecision("MODEL_BEHAVIOR_FAILURE", "OUT_OF_DOMAIN_ARGUMENT")

    return ActionDecision("VALID_TOOL")
