# Model identity — local GGUF captured

**Capture date:** 2026-09-25  
**Status:** SHA-256 captured from the experiment laptop before the E2 official run.

## Exact local model file

- Model family: `Qwen3-4B-Instruct-2507`
- Quantization: `Q4_K_M`
- Filename: `Qwen3-4B-Instruct-2507-Q4_K_M.gguf`
- Local path:
  `C:\Users\User\.lmstudio\models\lmstudio-community\Qwen3-4B-Instruct-2507-GGUF\Qwen3-4B-Instruct-2507-Q4_K_M.gguf`
- SHA-256:
  `8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC`

## Runtime identity used for current E2 protocol

- LM Studio model identifier: `qwen3-4b-instruct-2507`
- CPU runtime: `llama.cpp-win-x86_64-avx2@2.41.0`
- Quantization: `Q4_K_M`

## Evidence note

The SHA-256 was obtained locally with PowerShell `Get-FileHash ... -Algorithm SHA256` and supplied before any official E2 model data were collected.

The PowerShell table view shown during capture truncated the displayed Length field, so this file does **not** assert an exact byte count from that screenshot. The cryptographic hash is the canonical model-file identity.

Historical E0/E1 runs predate this hash capture. This capture strongly identifies the local GGUF currently used for E2, but it is not retroactive proof that an unchanged file was used in every historical run.


## E3 v0.7r1 technical re-verification — 2026-09-26

Before E3 freeze, the investigator re-verified the current local setup:

- exact GGUF SHA-256:
  `8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC`
- loaded LM Studio model id:
  `qwen3-4b-instruct-2507`
- loaded context length:
  `8192`
- selected GGUF runtime:
  `CPU llama.cpp (Windows) v2.41.0`
- GPU Offload:
  `0`
- local server:
  `http://127.0.0.1:1234`
- live non-scientific preflight:
  `PASS`

Evidence record:
`e3/implementation_v0_7/TECHNICAL_PREFLIGHT_EVIDENCE_v0.7r1.md`

This re-verification is prospective to E3 scientific data. It does not retroactively alter or reinterpret E2.
