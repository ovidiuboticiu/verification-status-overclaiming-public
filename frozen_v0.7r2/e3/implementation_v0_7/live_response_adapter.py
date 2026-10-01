from __future__ import annotations
import json

ARG_ORDER = {
    "read_snapshot": ["slot"],
    "read_version_exists": ["version"],
    "read_operation_phase": ["op_id"],
    "read_authority_meta": ["revision"],
    "resolve_authority_token": ["token"],
    "read_head_meta": [],
    "read_preop_snapshot": [],
    "read_operation_record": [],
    "read_source_bundle": [],
    "read_event_bundle": [],
    "read_order_graph": [],
    "read_graph_meta": [],
}

def _parse_tool_call(tc):
    try:
        function = tc["function"]
        name = function["name"]
        raw_args = function.get("arguments", "{}")
        args_obj = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        if not isinstance(name, str) or not isinstance(args_obj, dict):
            raise ValueError
        if name not in ARG_ORDER:
            # Preserve enough structure for runner_policy to classify UNKNOWN_TOOL.
            return {"kind":"tool_call","tool":name,"args":[],"tool_call_id":tc.get("id")}
        order = ARG_ORDER[name]
        if set(args_obj) != set(order):
            return {
                "kind":"tool_call",
                "tool":name,
                "args":"__MALFORMED_ARGS__",
                "tool_call_id":tc.get("id"),
            }
        return {
            "kind":"tool_call",
            "tool":name,
            "args":[args_obj[key] for key in order],
            "tool_call_id":tc.get("id"),
        }
    except Exception:
        return {"kind":"tool_call","tool":None,"args":None,"tool_call_id":tc.get("id") if isinstance(tc,dict) else None}

def adapt_assistant_message(message):
    if not isinstance(message, dict):
        return [{"kind":"tool_call","tool":None,"args":None,"text":None}]

    content = message.get("content")
    tool_calls = message.get("tool_calls")

    if tool_calls:
        if not isinstance(tool_calls, list):
            return [{"kind":"tool_call","tool":None,"args":None,"text":content}]
        actions=[]
        for tc in tool_calls:
            action=_parse_tool_call(tc)
            # If an invalid action terminates the episode, runner may parse the
            # same assistant message content as a final under the frozen rule.
            action["text"]=content if isinstance(content,str) else None
            actions.append(action)
        return actions

    return [{"kind":"final","text":content if isinstance(content,str) else ""}]

def tool_result_message(tool_call_id, result):
    return {
        "role":"tool",
        "tool_call_id":tool_call_id,
        "content":json.dumps(result, sort_keys=True, separators=(",",":")),
    }
