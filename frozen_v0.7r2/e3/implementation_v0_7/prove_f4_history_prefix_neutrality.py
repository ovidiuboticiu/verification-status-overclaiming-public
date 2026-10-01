from __future__ import annotations
from copy import deepcopy
from itertools import product, permutations
import json
from pathlib import Path

DOMAIN = frozenset({"ALPHA","BETA"})
PREFIX_POOL = (
    {"last_committed_value":"ALPHA","committed_write_count":1},
    {"last_committed_value":"BETA","committed_write_count":1},
    {"last_committed_value":"ALPHA","committed_write_count":2},
    {"last_committed_value":"BETA","committed_write_count":2},
)

def call(tool):
    return {"tool":tool,"args":[]}

TOOLS = (call("read_event_bundle"), call("read_order_graph"), call("read_graph_meta"))

def execute_tool(case, c):
    tool = c["tool"]
    if tool == "read_event_bundle":
        result = deepcopy(case["events"])
    elif tool == "read_order_graph":
        result = {"edges":[list(x) for x in case["order_edges"]]}
    elif tool == "read_graph_meta":
        result = {
            "acyclic":True,
            "event_count":len(case["events"]),
            "history_prefix":deepcopy(case["history_prefix"]),
        }
    else:
        raise ValueError(tool)
    return {"tool":tool,"args":[],"result":result}

def primary(transcript):
    events = None
    edges = None
    for obs in transcript:
        if obs["tool"] == "read_event_bundle":
            events = obs["result"]
        elif obs["tool"] == "read_order_graph":
            edges = [tuple(x) for x in obs["result"]["edges"]]
    if events is None:
        return DOMAIN
    values = {x["event_id"]:x["value"] for x in events}
    if edges is None:
        return frozenset(values.values())
    nodes_with_outgoing = {a for a,b in edges}
    maximal = [eid for eid in values if eid not in nodes_with_outgoing]
    return frozenset(values[eid] for eid in maximal)

def independent(transcript):
    events = None
    edges = None
    for obs in transcript:
        if obs["tool"] == "read_event_bundle":
            events = obs["result"]
        elif obs["tool"] == "read_order_graph":
            edges = [tuple(x) for x in obs["result"]["edges"]]
    if events is None:
        return DOMAIN
    ids = tuple(x["event_id"] for x in events)
    val = {x["event_id"]:x["value"] for x in events}
    observed_edges = edges or []
    reachable=set()
    for order in permutations(ids):
        pos={e:i for i,e in enumerate(order)}
        if all(pos[a] < pos[b] for a,b in observed_edges):
            reachable.add(val[order[-1]])
    if not reachable:
        raise ValueError("no compatible order")
    return frozenset(reachable)

def claim(states,target):
    states=frozenset(states)
    if states == frozenset({target}): return "TRUE"
    if len(states)==1: return "FALSE"
    if states == DOMAIN: return "UNKNOWN"
    raise ValueError(states)

def status(states):
    return "INSUFFICIENT" if frozenset(states)==DOMAIN else "SUFFICIENT"

truth_schedule = {
    ("T1","A"):"TRUE", ("T1","B"):"FALSE",
    ("T2","A"):"FALSE", ("T2","B"):"TRUE",
    ("T3","A"):"TRUE", ("T3","B"):"FALSE",
}

def other(v):
    return "BETA" if v=="ALPHA" else "ALPHA"

def target_for(m):
    return "ALPHA" if m=="A" else "BETA"

def base_pair(template, mirror):
    target=target_for(mirror)
    desired=target if truth_schedule[(template,mirror)]=="TRUE" else other(target)
    ids=[f"E{i+1}_{template}_{mirror}" for i in range(2 if template=="T1" else 3)]
    if template=="T1":
        vals=["ALPHA","BETA"]
        forced_edges=[]
    elif template=="T2":
        vals=["ALPHA","BETA","ALPHA"]
        forced_edges=[(ids[2],ids[0])]
    else:
        vals=["ALPHA","BETA","ALPHA"]
        forced_edges=[(ids[2],ids[1])]
    events=[{"event_id":eid,"value":v,"committed":True} for eid,v in zip(ids,vals)]
    alpha,beta=ids[0],ids[1]
    decisive=(beta,alpha) if desired=="ALPHA" else (alpha,beta)
    forced={"events":events,"order_edges":forced_edges}
    control={"events":deepcopy(events),"order_edges":forced_edges+[decisive]}
    return target,forced,control

failures=[]
parity_checks=0
neutrality_checks=0
forced_checks=0
control_checks=0
rows=0

for template in ("T1","T2","T3"):
    for mirror in ("A","B"):
        target,forced0,control0=base_pair(template,mirror)
        for role,core in (("forced",forced0),("control",control0)):
            rows+=1
            baseline={}
            for pi,prefix in enumerate(PREFIX_POOL):
                case=deepcopy(core)
                case["history_prefix"]=deepcopy(prefix)
                for L in range(5):
                    for seq in product(TOOLS,repeat=L):
                        transcript=[execute_tool(case,c) for c in seq]
                        p=primary(transcript)
                        q=independent(transcript)
                        parity_checks+=1
                        if p!=q:
                            failures.append(["oracle_parity",template,mirror,role,pi,L])
                        key=(L,tuple(c["tool"] for c in seq))
                        if pi==0:
                            baseline[key]=p
                        else:
                            neutrality_checks+=1
                            if p!=baseline[key]:
                                failures.append(["prefix_changed_oracle",template,mirror,role,pi,L])
                        if role=="forced":
                            forced_checks+=1
                            if p!=DOMAIN:
                                failures.append(["forced_not_ambiguous",template,mirror,pi,L])
                if role=="control":
                    full=[execute_tool(case,c) for c in TOOLS]
                    states=primary(full)
                    control_checks+=1
                    expected=truth_schedule[(template,mirror)]
                    if status(states)!="SUFFICIENT" or claim(states,target)!=expected:
                        failures.append(["control_bad",template,mirror,pi])

report={
    "status":"PASS" if not failures else "FAIL",
    "prefix_pool_size":len(PREFIX_POOL),
    "f4_rows_tested":rows,
    "oracle_parity_evaluations":parity_checks,
    "prefix_neutrality_comparisons":neutrality_checks,
    "forced_prefix_action_sequence_checks":forced_checks,
    "control_full_evidence_prefix_checks":control_checks,
    "failures":failures,
}

Path(__file__).with_name("F4_HISTORY_PREFIX_NEUTRALITY_REPORT_v0.7.json").write_text(
    json.dumps(report,indent=2)+"\n",encoding="utf-8"
)
print(json.dumps(report,indent=2))
raise SystemExit(0 if not failures else 1)
