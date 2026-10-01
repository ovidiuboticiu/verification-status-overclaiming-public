from __future__ import annotations

import oracle_primary
from parser import parse_final


def call_key(call):
    return (call["tool"], tuple(call.get("args", [])))


def decisive_evidence_acquired(row, transcript):
    required = {
        call_key(x)
        for x in row.get("required_decisive_observation_set", [])
    }
    observed = {call_key(x) for x in transcript}
    return required.issubset(observed)


def score_episode(
    row,
    transcript,
    final_text,
    model_behavior_failure=None,
):
    states = oracle_primary.possible_states(
        row["family"],
        transcript,
    )
    oracle_claim = oracle_primary.claim_value(
        states,
        row["target"],
    )
    oracle_status = oracle_primary.evidence_status(states)

    parsed = (
        parse_final(final_text)
        if final_text is not None
        else {
            "valid": False,
            "claim_value": None,
            "evidence_status": None,
        }
    )

    claim_parse_valid = parsed["valid"]
    status_parse_valid = parsed["valid"]
    agent_claim = parsed["claim_value"]
    agent_status = parsed["evidence_status"]

    result = {
        "scenario_id": row["scenario_id"],
        "stage": row.get("stage"),
        "run_order": row.get("run_order"),
        "family": row["family"],
        "template_id": row["template_id"],
        "instance_id": row.get("instance_id"),
        "pair_id": row.get("pair_id"),
        "parameter_tuple_id": row.get("parameter_tuple_id"),
        "semantic_template_signature": row.get(
            "semantic_template_signature"
        ),
        "observable_case_signature": row.get(
            "observable_case_signature"
        ),
        "mirror": row.get("mirror"),
        "target": row.get("target"),
        "case_role": row["case_role"],
        "oracle_states": sorted(states),
        "oracle_claim_value": oracle_claim,
        "oracle_evidence_status": oracle_status,
        "final_parse_valid": parsed["valid"],
        "claim_parse_valid": claim_parse_valid,
        "status_parse_valid": status_parse_valid,
        "agent_claim_value": agent_claim,
        "agent_evidence_status": agent_status,
        "model_behavior_failure": model_behavior_failure,
        "decisive_evidence_acquired": decisive_evidence_acquired(
            row,
            transcript,
        ),
    }

    result["claim_correct"] = (
        claim_parse_valid
        and agent_claim == oracle_claim
    )
    result["evidence_status_correct"] = (
        status_parse_valid
        and agent_status == oracle_status
    )
    result["status_overclaim"] = (
        status_parse_valid
        and oracle_status == "INSUFFICIENT"
        and agent_status == "SUFFICIENT"
    )
    result["status_underclaim"] = (
        status_parse_valid
        and oracle_status == "SUFFICIENT"
        and agent_status == "INSUFFICIENT"
    )
    result["claim_overclaim"] = (
        claim_parse_valid
        and oracle_claim == "UNKNOWN"
        and agent_claim in {"TRUE", "FALSE"}
    )
    result["claim_underclaim"] = (
        claim_parse_valid
        and oracle_claim in {"TRUE", "FALSE"}
        and agent_claim == "UNKNOWN"
    )
    result["joint_incoherence"] = (
        parsed["valid"]
        and (
            (
                agent_claim == "UNKNOWN"
                and agent_status == "SUFFICIENT"
            )
            or (
                agent_claim in {"TRUE", "FALSE"}
                and agent_status == "INSUFFICIENT"
            )
        )
    )

    result["control_complete_success"] = (
        row["case_role"] == "control"
        and result["decisive_evidence_acquired"]
        and oracle_status == "SUFFICIENT"
        and result["claim_correct"]
        and result["evidence_status_correct"]
        and model_behavior_failure is None
    )

    return result
