# E3 v0.7r1 technical preflight evidence

**Date:** 2026-09-26  
**Scientific data:** no  
**Status:** TECHNICAL PREFLIGHT COMPLETE / PASS

## Live non-scientific fixture

Archived raw result:
`NON_SCIENTIFIC_PREFLIGHT_RESULT_v0.1.json`

Raw-result SHA-256:
`5ad6493ef337d4d697fe6a3e2a4154ad2733802e06462d4559b4629f4ed6eee4`

Observed result:
- fixture status: PASS;
- endpoint: `http://127.0.0.1:1234/v1`;
- expected model `qwen3-4b-instruct-2507` listed by `/v1/models`;
- exact echo tool call: PASS;
- request fields accepted: PASS;
- exact final text `PREFLIGHT_STATUS: OK`: PASS;
- completion tokens: 7, within requested max_tokens=512.

This fixture is explicitly non-scientific and contains no E3 family mechanism.

## Local model-file identity

PowerShell `Get-FileHash -Algorithm SHA256` was rerun on the local GGUF.

Observed SHA-256:
`8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC`

This exactly matches the canonical model hash already recorded in `MODEL_IDENTITY.md`.

## Loaded-model/context evidence

LM Studio 0.4.24 Developer / Local Server view showed:
- server status: Running;
- loaded model: `qwen3-4b-instruct-2507`;
- model status: READY;
- server address: `http://127.0.0.1:1234`;
- loaded Context Length: `8192`;
- GPU Offload: `0`.

Screenshot supplied by investigator; local screenshot SHA-256:
`095c9dd3b5fd28c467aa451b73cdaf1285d41b207b9cb8a61e6fb846f1b72cd2`

## Runtime-selection evidence

LM Studio Runtime settings showed:
- GGUF runtime selection: `CPU llama.cpp (Windows)`;
- selected runtime version: `v2.41.0`;
- auto-update selected Runtime Extension Packs: disabled.

This corresponds to the protocol runtime identity:
`llama.cpp-win-x86_64-avx2@2.41.0`.

Screenshot supplied by investigator; local screenshot SHA-256:
`ee16ce31c399c2e895affcb14b4d21c45605e2b597dee023469d72e5248e91b1`

## What is verified

The evidence chain now directly supports:
- exact local GGUF hash;
- loaded Qwen model identity;
- local server reachability;
- context length 8192 for the loaded Qwen model;
- selected CPU llama.cpp runtime version 2.41.0;
- successful tool-call round trip;
- API acceptance of temperature=0, top_p=1, top_k=1, max_tokens=512;
- exact expected final preflight text.

## Limitation retained

The non-scientific fixture verifies acceptance of `max_tokens=512` and observed completion well below that limit. It does not independently inspect the server's internal token-limit enforcement implementation.

No E3-A or E3-B scientific prompt was sent during this preflight.
