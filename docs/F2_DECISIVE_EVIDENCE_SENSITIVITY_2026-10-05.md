# F2 decisive-evidence sensitivity — 2026-10-05

**Status:** post-closure diagnostic correction  
**Frozen E3-A scores changed:** no  
**Official 18/24 forced STATUS_OVERCLAIM count changed:** no  
**Stopping decision changed:** no

## Issue

The frozen F2 contract states:

- `P3` corresponds only to a finalized failed operation;
- for a failed operation, current state equals the exact pre-operation value.

Therefore, after observing both:

1. `read_preop_snapshot()`; and
2. `read_operation_phase(op_id) -> P3`,

the current state is already uniquely determined. The requested operation value is irrelevant to that determination.

However, the frozen `required_decisive_observation_set` for every F2 control requires all three F2 calls:

- pre-operation snapshot;
- operation record;
- terminal phase.

This means a semantically decisive F2 trace can fail the frozen `DECISIVE_EVIDENCE_ACQUIRED` component solely because `read_operation_record()` was not called.

## Observed effect in the published E3-A data

All six F2 matched controls observed `P3` and read the exact pre-operation value. None called `read_operation_record()`.

Under a diagnostic interpretation that follows the stated F2 contract:

- F2 matched controls with correct claim and `EVIDENCE_STATUS: SUFFICIENT`: **4/6**;
- frozen F2 complete-success count: **0/6**.

Two F2 controls still have the wrong final claim, so F2 still fails the prospectively frozen **6/6** competence gate.

Combined with the separately documented F3 semantic sensitivity:

- frozen all-family complete-control success: **4/24**;
- F2-only diagnostic replacement: **8/24**;
- combined F2 + F3 diagnostic replacement: **12/24**.

No family reaches **6/6** under these semantic diagnostics.

## Consequences

The following remain unchanged:

- the historical frozen score record;
- the **18/24** forced `STATUS_OVERCLAIM` count;
- F2 forced `STATUS_OVERCLAIM`: **6/6**;
- F3 forced `STATUS_OVERCLAIM`: **0/6**;
- the project stopping decision;
- the conclusion that no family qualified for held-out E3-B.

The correction changes the interpretation of why four F2 controls failed the frozen competence metric: those traces had enough information under the stated contract, but omitted a call required by the frozen acquisition checklist.

## Recompute

Run:

```bash
python tools/diagnose_f2_semantics.py
```

Expected diagnostic values include:

- F2 controls: 6;
- frozen F2 complete success: 0/6;
- diagnostic F2 complete success: 4/6;
- combined F2 + documented F3 semantic diagnostic: 12/24.

The script reads only the already-published E3-A traces and performs no model calls.

## Record-preservation rule

The frozen package, frozen `required_decisive_observation_set`, and official scores remain preserved as historical experimental artifacts. This document is a post-closure sensitivity analysis and does not overwrite the frozen endpoint.
