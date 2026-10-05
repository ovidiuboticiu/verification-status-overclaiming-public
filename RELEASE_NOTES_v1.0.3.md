# VSO v1.0.3 — final-audit remediation

**Date:** 2026-10-05

This patch release documents a final post-closure construct-validity issue in the F2 matched-control competence gate. It does not alter the frozen experimental package, official model outputs, frozen per-episode scores, forced STATUS_OVERCLAIM counts, or stopping decision.

## Changes

- Adds `docs/F2_DECISIVE_EVIDENCE_SENSITIVITY_2026-10-05.md`.
- Adds `tools/diagnose_f2_semantics.py`.
- Documents that in the observed F2 controls, terminal phase `P3` plus the exact pre-operation value already determines current state under the stated F2 contract.
- Records that the frozen acquisition checklist nevertheless required `read_operation_record()` as well.
- Diagnostic F2 complete-control success is **4/6** rather than frozen **0/6**.
- Combined with the v1.0.2 F3 semantic sensitivity, the diagnostic all-family complete-control total is **12/24** rather than frozen **4/24**.
- Clarifies that `ci/validate-release.yml` is a preserved reusable workflow example, not an installed active GitHub Actions workflow.

## Scientific status

The frozen E3-A result remains:

- **18/24** forced `STATUS_OVERCLAIM` events;
- F1 forced: **6/6**;
- F2 forced: **6/6**;
- F3 forced: **0/6**;
- F4 forced: **6/6**.

Under the post-closure semantic diagnostics, both F2 and F3 reach **4/6** matched-control complete success, still below the prospectively frozen **6/6** family competence gate. No family qualifies for held-out E3-B.

Therefore the historical stopping decision is unchanged.

The project still does not support a robust family-specific mechanism, population prevalence, cross-model generalization, deployed-agent prevalence, or a claim that the 18/24 forced count reflects condition-specific sensitivity.
