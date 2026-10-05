# VSO v1.0.1 — correction release

**Date:** 2026-10-05

This patch release corrects the public repository wrapper and makes an important descriptive interpretation guardrail explicit. It does **not** alter the frozen E3 package, official model outputs, per-episode scores, selection rule, or stopping decision.

## Changes

- Fixed Git checkout line-ending handling for two official JSON files that must remain byte-for-byte identical to their CRLF ZIP members.
- Updated `tools/validate_release.py` for the corrected documentation state.
- Added the post-closure response-tendency clarification: `EVIDENCE_STATUS: SUFFICIENT` occurred in 42/48 final responses overall (18/24 forced; 24/24 controls).
- Added `AI_USE.md` with the substantial-AI-assistance and human-responsibility disclosure.
- Added an explicit post-release correction record.

## Scientific status

The frozen E3-A observation remains 18/24 forced `STATUS_OVERCLAIM` events. No family passed the prospectively frozen 6/6 matched-control competence gate; no family-specific mechanism, prevalence estimate, cross-model generalization, or deployed-agent prevalence claim is supported.
