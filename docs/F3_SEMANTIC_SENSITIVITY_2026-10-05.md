# F3 semantic sensitivity analysis — 2026-10-05

**Status:** post-closure diagnostic correction  
**Frozen E3-A scores changed:** no  
**Official 18/24 forced STATUS_OVERCLAIM count changed:** no  
**Stopping decision changed:** no

## Issue

The frozen F3 contract states that a valid authority token, once resolved by `resolve_authority_token`, establishes the authoritative source.

The public tool interface also exposes `resolve_authority_token` only when a valid token exists, and its argument schema contains the valid token as an allowed enum value. Therefore an agent can obtain a decisive authoritative-source observation by calling:

1. `read_source_bundle`; and
2. `resolve_authority_token(valid_token)`.

However, both frozen F3 oracle implementations only narrow the state after successful token resolution if `read_authority_meta` was also called first. The scorer's frozen `required_decisive_observation_set` likewise requires that metadata call.

This creates an implementation/contract mismatch: a successful direct resolution can be semantically decisive under the stated interface contract while the frozen oracle still labels the episode UNKNOWN / INSUFFICIENT.

## Observed effect in the published E3-A data

All six F3 matched controls read the source bundle and successfully resolved the authority token without first calling `read_authority_meta`.

Under a diagnostic interpretation that follows the actual tool observation and the stated F3 contract:

- F3 matched controls with correct claim and status: **4/6**;
- frozen F3 complete-success count: **0/6**;
- total complete matched controls across all families would change descriptively from **4/24** to **8/24** if only this F3 semantic mismatch were corrected.

Two F3 controls still have the wrong final claim even after recognizing the successful authority resolution.

Therefore F3 still does **not** meet the prospectively frozen 6/6 competence gate.

## Consequences

The following remain unchanged:

- the historical frozen score record;
- the **18/24** forced `STATUS_OVERCLAIM` count;
- F3's forced `STATUS_OVERCLAIM` count of **0/6**;
- the project stopping decision;
- the conclusion that no family qualified for held-out E3-B.

The F3 control failures must nevertheless not all be interpreted as semantic insufficiency. Four of the six were scored insufficient because of the oracle/interface mismatch described above.

## Recompute

Run:

```bash
python tools/diagnose_f3_semantics.py
```

The script reads only the already-published E3-A `results.jsonl` and performs no model calls.

## Record-preservation rule

The frozen package and official scores are preserved as historical experimental artifacts. This document is a post-closure sensitivity analysis and does not silently overwrite the frozen endpoint.
