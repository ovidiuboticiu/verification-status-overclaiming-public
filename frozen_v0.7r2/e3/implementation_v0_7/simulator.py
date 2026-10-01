from __future__ import annotations
from copy import deepcopy

DOMAIN = frozenset({"ALPHA", "BETA"})

def call(tool, *args):
    return {"tool": tool, "args": list(args)}

def call_key(c):
    return (c["tool"], tuple(c.get("args", [])))

def legal_tool_calls(case):
    f = case["family"]
    if f == "F1":
        calls = [call("read_snapshot", slot) for slot in sorted(case["snapshots"])]
        calls.append(call("read_head_meta"))
        versions = sorted({x["version"] for x in case["snapshots"].values()})
        calls.extend(call("read_version_exists", v) for v in versions)
        return calls
    if f == "F2":
        return [
            call("read_preop_snapshot"),
            call("read_operation_record"),
            call("read_operation_phase", case["operation"]["op_id"]),
        ]
    if f == "F3":
        calls = [
            call("read_source_bundle"),
            call("read_authority_meta", case["revision"]),
        ]
        if case.get("authority_token") is not None:
            calls.append(call("resolve_authority_token", case["authority_token"]))
        return calls
    if f == "F4":
        return [
            call("read_event_bundle"),
            call("read_order_graph"),
            call("read_graph_meta"),
        ]
    raise ValueError(f)

def execute_tool(case, c):
    if call_key(c) not in {call_key(x) for x in legal_tool_calls(case)}:
        raise ValueError(f"out-of-domain tool call: {c}")

    tool = c["tool"]
    args = tuple(c.get("args", []))
    f = case["family"]

    if f == "F1":
        if tool == "read_snapshot":
            result = deepcopy(case["snapshots"][args[0]])
        elif tool == "read_head_meta":
            result = {"head_version": case["head_version"]}
        elif tool == "read_version_exists":
            result = {"exists": True}
        else:
            raise ValueError(tool)

    elif f == "F2":
        if tool == "read_preop_snapshot":
            result = deepcopy(case["preop"])
        elif tool == "read_operation_record":
            result = deepcopy(case["operation"])
        elif tool == "read_operation_phase":
            result = {"phase_code": case["phase_code"]}
        else:
            raise ValueError(tool)

    elif f == "F3":
        if tool == "read_source_bundle":
            result = deepcopy(case["sources"])
        elif tool == "read_authority_meta":
            result = {"authority_token": case.get("authority_token")}
        elif tool == "resolve_authority_token":
            token = args[0]
            result = {
                "authoritative_source_id": case["authority_resolution"][token]
            }
        else:
            raise ValueError(tool)

    elif f == "F4":
        if tool == "read_event_bundle":
            result = deepcopy(case["events"])
        elif tool == "read_order_graph":
            result = {"edges": [list(x) for x in case["order_edges"]]}
        elif tool == "read_graph_meta":
            result = {
                "acyclic": True,
                "event_count": len(case["events"]),
                "history_prefix": deepcopy(case["history_prefix"]),
            }
        else:
            raise ValueError(tool)
    else:
        raise ValueError(f)

    return {"tool": tool, "args": list(args), "result": result}

def full_valid_transcript(case):
    return [execute_tool(case, c) for c in legal_tool_calls(case)]
