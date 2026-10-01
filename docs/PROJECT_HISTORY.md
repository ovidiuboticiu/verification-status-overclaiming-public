# Project history and scope

This public repository is a clean release snapshot of the completed Verification-Status Overclaiming (VSO) experiment. It intentionally does not reproduce the private development Git history.

## High-level sequence

- **E0:** exploratory phase. Operational VSO-like events were observed, but the original procedural `VERIFIED` construct was later judged too weak for the intended scientific claim.
- **E1:** redesigned objective evidence-sufficiency construct and diagnostic gates.
- **E2:** predefined stress test under the redesigned construct; 0/12 forced opportunities produced `STATUS_OVERCLAIM`.
- **E3-A:** final adversarial discovery sweep. 18/24 forced opportunities produced the prospectively defined `STATUS_OVERCLAIM` event, but matched-control complete success was only 4/24 overall and no family passed the required 6/6 competence gate.
- **E3-B:** not run because no family was eligible under the frozen selection rule.
- **E4:** not permitted by the frozen protocol.

## Final scope

The project supports a descriptive occurrence result within the exact tested E3-A environment. It does not establish prevalence, cross-model generalization, deployed-agent prevalence, family-level causal mechanisms, or internal model belief.

The canonical final interpretation is in `docs/E3_FINAL_CONCLUSION.md`.
