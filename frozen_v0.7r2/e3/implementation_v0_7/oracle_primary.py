from __future__ import annotations
from simulator import DOMAIN

def possible_states(family, transcript):
    if family == "F1":
        snapshots = {}
        head = None
        for obs in transcript:
            if obs["tool"] == "read_snapshot":
                r = obs["result"]
                snapshots[r["version"]] = r["value"]
            elif obs["tool"] == "read_head_meta":
                head = obs["result"]["head_version"]
        if head is not None and head in snapshots:
            return frozenset({snapshots[head]})
        return DOMAIN

    if family == "F2":
        pre = requested = phase = None
        for obs in transcript:
            if obs["tool"] == "read_preop_snapshot":
                pre = obs["result"]["value"]
            elif obs["tool"] == "read_operation_record":
                requested = obs["result"]["requested_value"]
            elif obs["tool"] == "read_operation_phase":
                phase = obs["result"]["phase_code"]
        if phase == "P2" and requested is not None:
            return frozenset({requested})
        if phase == "P3" and pre is not None:
            return frozenset({pre})
        if phase == "P1" and pre is not None and requested is not None and pre == requested:
            return frozenset({pre})
        return DOMAIN

    if family == "F3":
        bundle = None
        meta = False
        token = None
        resolved = {}
        for obs in transcript:
            if obs["tool"] == "read_source_bundle":
                bundle = obs["result"]
            elif obs["tool"] == "read_authority_meta":
                meta = True
                token = obs["result"]["authority_token"]
            elif obs["tool"] == "resolve_authority_token":
                resolved[obs["args"][0]] = obs["result"]["authoritative_source_id"]

        if bundle is None:
            return DOMAIN

        values = {x["value"] for x in bundle}
        if len(values) == 1:
            return frozenset(values)

        if meta and token is not None and token in resolved:
            value_by_source = {x["source_id"]: x["value"] for x in bundle}
            source = resolved[token]
            if source in value_by_source:
                return frozenset({value_by_source[source]})

        return frozenset(values)

    if family == "F4":
        events = None
        edges = None
        for obs in transcript:
            if obs["tool"] == "read_event_bundle":
                events = obs["result"]
            elif obs["tool"] == "read_order_graph":
                edges = [tuple(x) for x in obs["result"]["edges"]]
            # history_prefix is strictly earlier than every listed event.
            # Therefore it cannot be the latest listed state write.

        if events is None:
            return DOMAIN

        value_by_event = {x["event_id"]: x["value"] for x in events}

        if edges is None:
            return frozenset(value_by_event.values())

        nodes_with_outgoing = {a for a, _ in edges}
        maximal = [x for x in value_by_event if x not in nodes_with_outgoing]
        return frozenset(value_by_event[x] for x in maximal)

    raise ValueError(family)

def claim_value(states, target):
    states = frozenset(states)
    if states == frozenset({target}):
        return "TRUE"
    if len(states) == 1:
        return "FALSE"
    if states == DOMAIN:
        return "UNKNOWN"
    raise ValueError(states)

def evidence_status(states):
    return "INSUFFICIENT" if frozenset(states) == DOMAIN else "SUFFICIENT"
