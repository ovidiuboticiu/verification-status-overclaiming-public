from __future__ import annotations
from prompt_builder import build_prompt, tool_schema_from_row

MODEL_ID = "qwen3-4b-instruct-2507"
TEMPERATURE = 0.0
TOP_P = 1.0
TOP_K = 1
MAX_TOKENS = 512

def initial_request(row):
    prompt = build_prompt(row)
    return {
        "model": MODEL_ID,
        "messages": [
            {"role":"system","content":prompt["system"]},
            {"role":"user","content":prompt["user"]},
        ],
        "tools": tool_schema_from_row(row),
        "tool_choice":"auto",
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_tokens": MAX_TOKENS,
        "stream": False,
    }

def continuation_request(base_request, messages):
    req = dict(base_request)
    req["messages"] = list(messages)
    return req
