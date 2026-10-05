# Post-release corrections — 2026-10-05

**Scope:** public repository wrapper and interpretation only  
**Frozen experimental package changed:** no  
**Official model outputs changed:** no  
**Frozen scores changed:** no  
**Stopping decision changed:** no

## 1. Checkout line-ending defect in release validation

The v1.0.0 public snapshot declared `*.json text eol=lf` globally in `.gitattributes`.

Two browseable official-output JSON files are exact mirrors of ZIP members whose preserved bytes use CRLF line endings:

- `results/official/E3A_PHASE_ANALYSIS.json`
- `results/official/RUN_RECORD.json`

A normal Git checkout could therefore normalize these two files to LF, causing `tools/validate_release.py` to report a byte/hash mismatch even though the repository and ZIP contained logically identical JSON.

**Correction:** the two exact-mirror paths are now marked `-text` so Git does not normalize their bytes. The official ZIP, its SHA-256, the stored result rows, and all scientific scores are unchanged.

## 2. Response-tendency interpretive clarification

A descriptive aggregation of the already-published 48 final responses shows:

- `EVIDENCE_STATUS: SUFFICIENT` in **42/48** responses overall;
- **18/24** forced responses;
- **24/24** control responses.

This broad response tendency is now stated explicitly in the README and in `E3A_RESPONSE_BIAS_CLARIFICATION_2026-10-05.md`.

The clarification does not alter the prospectively frozen result or stopping rule. It narrows interpretation: the 18/24 forced count is not evidence of condition-specific sensitivity, and the failed matched-control competence gate remains central.

## 3. AI-assistance disclosure

`AI_USE.md` was added to make the substantial role of AI assistance and the human responsibility boundary explicit.

## Historical record

The original v1.0.0 release record and audit remain part of the repository history. These corrections are additive and are not presented as if they had existed in the original tagged snapshot.
