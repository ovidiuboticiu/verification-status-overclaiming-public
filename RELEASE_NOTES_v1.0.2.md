# VSO v1.0.2 — audit-remediation release

**Date:** 2026-10-05

This patch release completes the public-repository remediation identified by adversarial review. It preserves the frozen experimental package, official model outputs, frozen per-episode scores, selection rule, and stopping decision.

## Changes

- Restores the exact CRLF bytes of the two browseable official JSON mirrors so they again match the immutable official-output ZIP byte-for-byte.
- Regenerates current-release integrity metadata and validates the complete `SHA256SUMS.txt` list.
- Adds `tools/diagnose_f3_semantics.py` and `docs/F3_SEMANTIC_SENSITIVITY_2026-10-05.md`.
- Documents the F3 oracle/interface mismatch: successful direct authority-token resolution is semantically decisive under the stated interface contract even when `read_authority_meta` was skipped.
- Diagnostic F3 control complete success is **4/6** rather than frozen **0/6**; the all-family descriptive control total is **8/24** rather than frozen **4/24**.
- Keeps the historical frozen scores intact and labels the diagnostic as post-closure sensitivity analysis.

## Scientific status

The published frozen result remains **18/24 forced STATUS_OVERCLAIM** events. F3 still has **0/6** forced overclaims and still fails the **6/6** matched-control competence gate under the diagnostic semantics. No family qualifies for held-out E3-B, so the historical stopping decision is unchanged.

The project still does not support a robust family-specific mechanism, a prevalence estimate, cross-model generalization, or deployed-agent prevalence.
