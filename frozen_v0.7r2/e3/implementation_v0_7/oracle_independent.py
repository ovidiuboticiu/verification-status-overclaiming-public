from __future__ import annotations
from itertools import permutations
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

        if head is not None:
            head_candidates = [head]
        else:
            versions = set(snapshots)
            later = (max(versions) if versions else 0) + 1
            head_candidates = list(versions) + [later]

        reachable = set()
        for h in head_candidates:
            for hv in DOMAIN:
                if h in snapshots and snapshots[h] != hv:
                    continue
                reachable.add(hv)
        return frozenset(reachable)

    if family == "F2":
        pre_obs = requested_obs = phase_obs = None
        for obs in transcript:
            if obs["tool"] == "read_preop_snapshot":
                pre_obs = obs["result"]["value"]
            elif obs["tool"] == "read_operation_record":
                requested_obs = obs["result"]["requested_value"]
            elif obs["tool"] == "read_operation_phase":
                phase_obs = obs["result"]["phase_code"]

        phase_by_hidden = {"Q": "P1", "A": "P1", "C": "P2", "F": "P3"}
        reachable = set()

        for pre in DOMAIN:
            if pre_obs is not None and pre != pre_obs:
                continue
            for requested in DOMAIN:
                if requested_obs is not None and requested != requested_obs:
                    continue
                for hidden_state, phase in phase_by_hidden.items():
                    if phase_obs is not None and phase != phase_obs:
                        continue
                    current = pre if hidden_state in {"Q", "F"} else requested
                    reachable.add(current)

        return frozenset(reachable)

    if family == "F3":
        bundle = None
        meta_observed = False
        token = None
        resolutions = {}

        for obs in transcript:
            if obs["tool"] == "read_source_bundle":
                bundle = obs["result"]
            elif obs["tool"] == "read_authority_meta":
                meta_observed = True
                token = obs["result"]["authority_token"]
            elif obs["tool"] == "resolve_authority_token":
                resolutions[obs["args"][0]] = obs["result"]["authoritative_source_id"]

        if bundle is None:
            return DOMAIN

        value_by_source = {x["source_id"]: x["value"] for x in bundle}
        authority_candidates = list(value_by_source)

        if meta_observed and token is not None and token in resolutions:
            source = resolutions[token]
            authority_candidates = [source] if source in value_by_source else []

        return frozenset(value_by_source[x] for x in authority_candidates)

    if family == "F4":
        events = None
        edges = None
        for obs in transcript:
            if obs["tool"] == "read_event_bundle":
                events = obs["result"]
            elif obs["tool"] == "read_order_graph":
                edges = [tuple(x) for x in obs["result"]["edges"]]
            # The frozen contract places all prefix history strictly before
            # every listed event, so prefix history is excluded from the
            # topological permutations of potentially latest listed writes.

        if events is None:
            return DOMAIN

        ids = tuple(x["event_id"] for x in events)
        value_by_event = {x["event_id"]: x["value"] for x in events}
        observed_edges = edges or []

        reachable = set()
        for order in permutations(ids):
            position = {event_id: i for i, event_id in enumerate(order)}
            if all(position[a] < position[b] for a, b in observed_edges):
                reachable.add(value_by_event[order[-1]])

        if not reachable:
            raise ValueError("no compatible topological order")

        return frozenset(reachable)

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
