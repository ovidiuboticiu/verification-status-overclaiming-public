from __future__ import annotations

import itertools
import json

import oracle_independent
import oracle_primary
from manifest_loader import MANIFEST_SPECS, load_manifest
from simulator import DOMAIN, execute_tool, legal_tool_calls


checks = 0
failures = []
parity_sequences = 0
forced_sequences = 0
control_decisive_checks = 0


def ck(name, condition):
    global checks
    checks += 1
    if not condition:
        failures.append(name)


for key in MANIFEST_SPECS:
    rows = load_manifest(key)

    for row in rows:
        calls = legal_tool_calls(row["case"])

        for length in range(5):
            for seq in itertools.product(calls, repeat=length):
                transcript = [
                    execute_tool(row["case"], call)
                    for call in seq
                ]
                p = oracle_primary.possible_states(
                    row["family"],
                    transcript,
                )
                q = oracle_independent.possible_states(
                    row["family"],
                    transcript,
                )
                parity_sequences += 1
                ck(
                    f"{key}/{row['scenario_id']}/oracle_parity",
                    p == q,
                )
                ck(
                    f"{key}/{row['scenario_id']}/claim_parity",
                    oracle_primary.claim_value(p, row["target"])
                    == oracle_independent.claim_value(q, row["target"]),
                )
                ck(
                    f"{key}/{row['scenario_id']}/status_parity",
                    oracle_primary.evidence_status(p)
                    == oracle_independent.evidence_status(q),
                )

                if row["case_role"] == "forced":
                    forced_sequences += 1
                    ck(
                        f"{key}/{row['scenario_id']}/forced_domain",
                        p == DOMAIN,
                    )

        if row["case_role"] == "control":
            decisive = row["required_decisive_observation_set"]
            ck(
                f"{key}/{row['scenario_id']}/decisive_budget",
                len(decisive) <= 4,
            )
            transcript = [
                execute_tool(row["case"], call)
                for call in decisive
            ]
            p = oracle_primary.possible_states(
                row["family"],
                transcript,
            )
            q = oracle_independent.possible_states(
                row["family"],
                transcript,
            )
            control_decisive_checks += 1
            ck(
                f"{key}/{row['scenario_id']}/decisive_parity",
                p == q,
            )
            ck(
                f"{key}/{row['scenario_id']}/decisive_status",
                oracle_primary.evidence_status(p)
                == row["environment_oracle_status"]
                == "SUFFICIENT",
            )
            ck(
                f"{key}/{row['scenario_id']}/decisive_claim",
                oracle_primary.claim_value(p, row["target"])
                == row["environment_oracle_claim"],
            )

report = {
    "status": "PASS" if not failures else "FAIL",
    "manifest_count": len(MANIFEST_SPECS),
    "all_row_action_sequences_primary_independent_parity": parity_sequences,
    "forced_action_sequences_invariant_checked": forced_sequences,
    "control_decisive_transcript_checks": control_decisive_checks,
    "assertion_checks": checks,
    "failures": failures[:50],
    "scientific_model_data": False,
    "live_model_contacted": False,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if not failures else 1)
