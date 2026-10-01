from __future__ import annotations
import json

from live_response_adapter import adapt_assistant_message, tool_result_message

checks=[]
def ck(name, cond):
    checks.append({"name":name,"pass":bool(cond)})

ck("final_response",
   adapt_assistant_message({"content":"CLAIM_VALUE: UNKNOWN\nEVIDENCE_STATUS: INSUFFICIENT"})[0]["kind"]=="final")

a=adapt_assistant_message({
    "content":None,
    "tool_calls":[{"id":"tc1","function":{"name":"read_snapshot","arguments":"{\"slot\":\"S1\"}"}}],
})[0]
ck("valid_tool_call",a["tool"]=="read_snapshot" and a["args"]==["S1"] and a["tool_call_id"]=="tc1")

a=adapt_assistant_message({
    "tool_calls":[{"id":"tc1","function":{"name":"invented_tool","arguments":"{}"}}],
})[0]
ck("unknown_tool_preserved_for_policy",a["tool"]=="invented_tool")

a=adapt_assistant_message({
    "tool_calls":[{"id":"tc1","function":{"name":"read_snapshot","arguments":"{"}}],
})[0]
ck("malformed_json_arguments",a["tool"] is None and a["args"] is None)

a=adapt_assistant_message({
    "tool_calls":[{"id":"tc1","function":{"name":"read_snapshot","arguments":"{\"slot\":\"S1\",\"x\":1}"}}],
})[0]
ck("extra_argument_marked_malformed",a["args"]=="__MALFORMED_ARGS__")

a=adapt_assistant_message({
    "tool_calls":[
        {"id":"tc1","function":{"name":"read_head_meta","arguments":"{}"}},
        {"id":"tc2","function":{"name":"read_head_meta","arguments":"{}"}},
    ],
})
ck("multiple_tool_calls_preserve_order",len(a)==2 and a[0]["tool_call_id"]=="tc1" and a[1]["tool_call_id"]=="tc2")

m=tool_result_message("tc9",{"b":2,"a":1})
ck("tool_result_deterministic_json",m["content"]=='{"a":1,"b":2}')

report={
    "status":"PASS" if all(x["pass"] for x in checks) else "FAIL",
    "checks":len(checks),
    "failures":[x["name"] for x in checks if not x["pass"]],
    "scientific_model_data":False,
    "live_model_contacted":False,
}
print(json.dumps(report,indent=2))
