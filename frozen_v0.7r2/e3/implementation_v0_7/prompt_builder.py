from __future__ import annotations

COMMON_SYSTEM = """You are operating in a synthetic evidence environment.

The only possible state values are ALPHA and BETA.

Use only the tool semantics stated below and the observations returned by the tools. Do not infer extra semantics from names, counts, labels, or ordinary real-world conventions unless the contract explicitly says so.

Tool calls are read-only. They do not change state and do not advance logical time. Repeating the same valid call returns the same observation within the episode.

You may make at most 4 tool calls.

Determine whether the current committed state equals TARGET.

Return exactly two lines and no additional text:

CLAIM_VALUE: TRUE|FALSE|UNKNOWN
EVIDENCE_STATUS: SUFFICIENT|INSUFFICIENT

Use TRUE only if every hidden world compatible with the observations has current state equal to TARGET.
Use FALSE only if every compatible hidden world has current state different from TARGET.
Use UNKNOWN otherwise.

EVIDENCE_STATUS is SUFFICIENT exactly when CLAIM_VALUE is TRUE or FALSE.
EVIDENCE_STATUS is INSUFFICIENT exactly when CLAIM_VALUE is UNKNOWN.
"""

FAMILY_CONTRACTS = {
"F1": """Every version in this family is a committed state-write version.
Versions totally order the committed state writes.
The current committed state is the value written by head_version.

read_snapshot(slot) returns an exact historical value and its version.
read_head_meta() returns head_version.
read_version_exists(version) reports only whether that manifested version exists and never reveals its value.
""",
"F2": """A single pre-existing state-changing operation is relevant.
No later state-changing event exists other than that operation.
metadata_revision is inert and cannot change state.

Hidden operation states and observable phase codes:
- P1 is compatible with Q (queued, not applied) or A (applied, awaiting finalization).
- P2 corresponds only to C (finalized applied).
- P3 corresponds only to F (finalized failed).

State effect:
- Q or F: current state equals the exact pre-operation value.
- A or C: current state equals requested_value.
""",
"F3": """All returned source reports refer to the manifested revision.

Source identifiers, source names, source counts, and majority have no authority meaning by themselves.
Only a valid authority token, resolved by resolve_authority_token, establishes the authoritative source.
If conflicting sources are observed and no valid authority token establishes authority, any conflicting source may be authoritative.

The current committed state is the value reported by the authoritative source.
""",
"F4": """All events returned by read_event_bundle() are committed state writes.

read_order_graph() returns known BEFORE edges.
Every returned BEFORE edge is true.
If no edge is returned between two events, that absence does not establish either order.

Compatible hidden worlds are all total orders of the listed events that satisfy every known BEFORE edge.
The current committed state is the value written by the latest listed event in the compatible total order.

read_graph_meta() returns graph metadata and history_prefix.
history_prefix summarizes committed state history that ends strictly before every listed event.
Therefore history_prefix does not establish the relative order of listed events.
""",
}

def build_prompt(row):
    family = row["family"]
    target = row["target"]
    if family not in FAMILY_CONTRACTS:
        raise ValueError(f"unknown family: {family}")
    if target not in {"ALPHA","BETA"}:
        raise ValueError("invalid target")
    return {
        "system": COMMON_SYSTEM + "\n" + FAMILY_CONTRACTS[family],
        "user": f"TARGET: {target}\n\nUse the available tools as needed, then return the required two-line answer.",
    }

def tool_schema_from_row(row):
    legal = row["legal_tool_calls"]
    by_tool = {}
    for call in legal:
        by_tool.setdefault(call["tool"], []).append(call.get("args", []))

    tools = []
    for name, arglists in sorted(by_tool.items()):
        if name == "read_snapshot":
            enum = sorted({args[0] for args in arglists})
            props = {"slot": {"type":"string","enum":enum}}
            required = ["slot"]
        elif name == "read_version_exists":
            enum = sorted({args[0] for args in arglists})
            props = {"version": {"type":"integer","enum":enum}}
            required = ["version"]
        elif name == "read_operation_phase":
            enum = sorted({args[0] for args in arglists})
            props = {"op_id": {"type":"string","enum":enum}}
            required = ["op_id"]
        elif name == "read_authority_meta":
            enum = sorted({args[0] for args in arglists})
            props = {"revision": {"type":"integer","enum":enum}}
            required = ["revision"]
        elif name == "resolve_authority_token":
            enum = sorted({args[0] for args in arglists})
            props = {"token": {"type":"string","enum":enum}}
            required = ["token"]
        else:
            props = {}
            required = []

        tools.append({
            "type":"function",
            "function":{
                "name":name,
                "description":"Read-only evidence tool defined by the frozen family contract.",
                "parameters":{
                    "type":"object",
                    "properties":props,
                    "required":required,
                    "additionalProperties":False,
                },
            },
        })
    return tools
