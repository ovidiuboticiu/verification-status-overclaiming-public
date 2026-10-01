from __future__ import annotations

EXECUTION_IDENTITY = {
    "model_family": "Qwen3-4B-Instruct-2507",
    "lm_studio_model_id": "qwen3-4b-instruct-2507",
    "quantization": "Q4_K_M",
    "gguf": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
    "gguf_sha256": "8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC",
    "runtime": "llama.cpp-win-x86_64-avx2@2.41.0",
    "lm_studio_version_observed": "0.4.24",
    "context_length": 8192,
    "temperature": 0.0,
    "top_p": 1.0,
    "top_k": 1,
    "min_p": None,
    "max_generated_tokens": 512,
    "max_tool_calls": 4,
    "gpu_offload": 0,
    "cold_start_per_episode": True,
}

def get_execution_identity():
    return dict(EXECUTION_IDENTITY)
