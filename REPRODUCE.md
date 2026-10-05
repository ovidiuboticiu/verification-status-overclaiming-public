# Reproduction and verification

The release separates three different activities:

1. **artifact verification** — confirm that the published bytes match the frozen experiment;
2. **offline recomputation** — recompute scoring and phase analysis from the raw stored traces;
3. **independent model rerun** — rerun the frozen E3-A protocol against a compatible local model endpoint.

Only the third activity contacts a model.

## 1. Verify the release

From the repository root:

```bash
python tools/validate_release.py
```

This checks the critical immutable SHA-256 identities, verifies that browseable files match the exact ZIP members, validates the current `RELEASE_MANIFEST.json` and complete `SHA256SUMS.txt` list against the working tree, validates JSON/JSONL syntax, and scans the release for common credential patterns.

## 2. Recompute E3-A from raw traces

```bash
python tools/recalculate_e3a.py
```

The script extracts the exact frozen package into a temporary directory, imports the frozen oracle/parser/scorer, rescoring all 48 raw official episode traces from `results/official/`, and compares the recomputed phase analysis to the stored official analysis.

Expected final values include:

- episode records: 48
- scoring mismatches: 0
- forced `STATUS_OVERCLAIM`: 18/24
- matched-control complete success: 4/24
- eligible candidate families: none
- selected family: null
- E3-B required: false

## 3. Run the F3 semantic sensitivity diagnostic

```bash
python tools/diagnose_f3_semantics.py
```

This does not alter the frozen scoring record. It follows the stated F3 interface contract and the successful `resolve_authority_token` observations in the stored traces. Expected diagnostic values are:

- F3 controls: 6
- frozen F3 complete success: 0/6
- diagnostic F3 complete success: 4/6
- frozen all-family control complete success: 4/24
- diagnostic all-family control complete success: 8/24
- F3 diagnostic competence gate: fail (4/6 < 6/6)

See `docs/F3_SEMANTIC_SENSITIVITY_2026-10-05.md`.

## 4. Run the F2 decisive-evidence sensitivity diagnostic

```bash
python tools/diagnose_f2_semantics.py
```

This also leaves the frozen scoring record untouched. It applies the stated F2 contract to the already-published traces. In the six F2 matched controls, terminal phase `P3` plus the exact pre-operation value already determines current state even though the frozen acquisition checklist additionally required `read_operation_record()`.

Expected values include:

- F2 controls: 6
- frozen F2 complete success: 0/6
- diagnostic F2 complete success: 4/6
- F2 diagnostic competence gate: fail (4/6 < 6/6)
- combined F2 + documented F3 semantic diagnostic: 12/24

See `docs/F2_DECISIVE_EVIDENCE_SENSITIVITY_2026-10-05.md`.

## 5. Rerun the model experiment

The exact frozen source and official runner are preserved in:

`frozen_v0.7r2/`

The original run procedure is:

`frozen_v0.7r2/e3/implementation_v0_7/RUN_OFFICIAL_E3_v0.7r2.md`

The frozen scientific identity includes:

- model family: `Qwen3-4B-Instruct-2507`
- quantization: `Q4_K_M`
- GGUF SHA-256: `8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC`
- runtime: `llama.cpp-win-x86_64-avx2@2.41.0`
- context length: 8192
- temperature: 0.0
- top_p: 1.0
- top_k: 1
- max generated tokens: 512
- max valid tool calls: 4
- GPU offload: 0
- cold start per episode: true

A rerun by another investigator is an independent reproduction attempt. It is **not** a continuation of the original closed VSO sequence. Under the original frozen result, E3-B was not authorized because no family passed the 6/6 matched-control gate.
