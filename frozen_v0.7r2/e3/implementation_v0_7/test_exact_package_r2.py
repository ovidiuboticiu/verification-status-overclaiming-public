from __future__ import annotations

import json
from pathlib import Path

from execution_identity import get_execution_identity
from manifest_loader import MANIFEST_SPECS, load_manifest, manifest_sha256
from package_integrity_r2 import verify_payload_lock

BASE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
LOCK = BASE / "E3_PACKAGE_PAYLOAD_LOCK_v0.7r2.json"

failures = []


def ck(name, condition):
    if not condition:
        failures.append(name)


verified = verify_payload_lock(ROOT, LOCK)
ck("payload_file_count_positive", verified["payload_file_count"] > 0)
ck("payload_hash_length", len(verified["payload_set_sha256"]) == 64)

for key, spec in MANIFEST_SPECS.items():
    rows = load_manifest(key)
    ck(f"{key}:rows", len(rows) == spec["rows"])
    ck(f"{key}:hash", manifest_sha256(key) == spec["sha256"])

protocol = ROOT / "e3/E3_CANONICAL_PROTOCOL_CANDIDATE_v0.7r2.md"
ck("canonical_protocol_present", protocol.is_file())

runner = BASE / "official_runner_r2.py"
ck("official_runner_present", runner.is_file())

preflight = json.loads(
    (BASE / "NON_SCIENTIFIC_PREFLIGHT_RESULT_v0.1.json").read_text(
        encoding="utf-8"
    )
)
ck("preflight_non_scientific", preflight.get("scientific_data") is False)
ck("preflight_pass", preflight.get("status") == "PASS")

identity = get_execution_identity()
ck("context_8192", identity["context_length"] == 8192)
ck("max_tokens_512", identity["max_generated_tokens"] == 512)
ck("max_tool_calls_4", identity["max_tool_calls"] == 4)
ck(
    "gguf_hash",
    identity["gguf_sha256"]
    == "8CDB57CBB880D313736A9BC4E3D3D2485F145B5E19CF33783746E753E82641FC",
)
ck(
    "runtime",
    identity["runtime"] == "llama.cpp-win-x86_64-avx2@2.41.0",
)

report = {
    "status": "PASS" if not failures else "FAIL",
    "scientific_model_data": False,
    "payload_file_count": verified["payload_file_count"],
    "payload_set_sha256": verified["payload_set_sha256"],
    "manifest_count": len(MANIFEST_SPECS),
    "failures": failures,
}
print(json.dumps(report, indent=2))
raise SystemExit(0 if not failures else 1)
