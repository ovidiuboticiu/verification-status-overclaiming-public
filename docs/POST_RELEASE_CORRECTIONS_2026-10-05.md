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

**v1.0.1 correction attempt:** the two paths were marked `-text` so future Git operations would stop normalizing them. A later adversarial audit correctly found that this did **not** restore CRLF bytes that had already been committed as LF.

**v1.0.2 correction:** the two browseable files were rewritten from their exact ZIP-member text with CRLF bytes while the paths remained `-text`. The validator now checks byte equality against the ZIP on a fresh checkout. The official ZIP, its SHA-256, the stored result rows, and all scientific scores are unchanged.

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

## 4. F3 oracle/interface mismatch

A post-closure adversarial audit found that the frozen F3 oracle only treats a successful `resolve_authority_token` observation as decisive when `read_authority_meta` was also called first. The stated F3 contract and exposed tool interface do not require that extra discovery call once the valid token has been successfully resolved.

A diagnostic rescoring of the six published F3 controls therefore gives **4/6** complete semantic successes rather than the frozen **0/6**. Across all 24 controls, the descriptive total becomes **8/24** rather than frozen **4/24**. F3 still fails the frozen **6/6** family competence gate, F3 still has **0/6** forced overclaims, the global **18/24** forced result is unchanged, and the stopping decision remains unchanged.

The frozen scorer and official result files are preserved rather than silently rewritten. See `F3_SEMANTIC_SENSITIVITY_2026-10-05.md` and `../tools/diagnose_f3_semantics.py`.

## 5. Release-integrity refresh

For v1.0.2, `RELEASE_MANIFEST.json` and `SHA256SUMS.txt` are regenerated after all remediation changes. The release validator checks the checksum list against the working tree in addition to the immutable frozen ZIP identities.


## 6. F2 decisive-evidence checklist sensitivity

A final adversarial audit found that the frozen F2 acquisition checklist was stricter than the stated F2 semantics for the observed control traces.

All six F2 matched controls observed terminal phase `P3` and read the exact pre-operation value. Under the frozen F2 contract, `P3` means the operation failed and current state therefore equals the pre-operation value. Those observations already determine current state without needing `read_operation_record()`.

The frozen `required_decisive_observation_set` nevertheless required the operation-record call as well. Consequently all six F2 controls received `decisive_evidence_acquired=false`.

Diagnostic interpretation of the published traces gives:

- frozen F2 complete success: **0/6**;
- diagnostic F2 complete semantic success: **4/6**;
- two remaining F2 controls still have incorrect final claims.

Combined with the previously documented F3 sensitivity, the all-family diagnostic control total becomes **12/24** rather than frozen **4/24**. Neither F2 nor F3 reaches the required **6/6** family gate, so no family qualifies for E3-B and the stopping decision remains unchanged.

See `F2_DECISIVE_EVIDENCE_SENSITIVITY_2026-10-05.md` and `../tools/diagnose_f2_semantics.py`.

## 7. v1.0.3 integrity refresh

For v1.0.3, release metadata are refreshed after the F2 sensitivity documentation. The frozen package, official output ZIP, raw traces, frozen scores, and historical stopping decision remain unchanged.
