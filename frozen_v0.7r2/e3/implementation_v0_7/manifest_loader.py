from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
MANIFEST_DIR = BASE / "manifests_v0_7r1"

MANIFEST_SPECS = {
    "A": {
        "name": "E3A_MANIFEST_CANDIDATE_v0.7r1.json",
        "sha256": "83c33aade50bca0c55482cd6ddd6711efd82f86674feb19b4cd77259679ab6a4",
        "rows": 48,
        "stage": "A",
        "family": None,
    },
    "B_F1": {
        "name": "E3B_F1_MANIFEST_CANDIDATE_v0.7r1.json",
        "sha256": "e593b4f9b6a6a9a43ed8011d235c816cf9e1fcfe1a227b3b11b5c4237a55ecfe",
        "rows": 24,
        "stage": "B",
        "family": "F1",
    },
    "B_F2": {
        "name": "E3B_F2_MANIFEST_CANDIDATE_v0.7r1.json",
        "sha256": "1d7b1395508ffd73375b47fac08d26fdfb52697d15b024ca3460dd3877e37453",
        "rows": 24,
        "stage": "B",
        "family": "F2",
    },
    "B_F3": {
        "name": "E3B_F3_MANIFEST_CANDIDATE_v0.7r1.json",
        "sha256": "62e2fbb830e06167745c8fef4b961fe7cf43cf69cbce74583e80bc40b80e7464",
        "rows": 24,
        "stage": "B",
        "family": "F3",
    },
    "B_F4": {
        "name": "E3B_F4_MANIFEST_CANDIDATE_v0.7r1.json",
        "sha256": "ec6dc9eaf8f9235f9e0df0f3126cd54af03862f16f9c3ecc1afe8d9ca0a65ff4",
        "rows": 24,
        "stage": "B",
        "family": "F4",
    },
}

def _spec(key):
    if key not in MANIFEST_SPECS:
        raise ValueError(f"unknown manifest key: {key}")
    return MANIFEST_SPECS[key]

def manifest_path(key):
    return MANIFEST_DIR / _spec(key)["name"]

def manifest_sha256(key):
    return hashlib.sha256(manifest_path(key).read_bytes()).hexdigest()

def load_manifest(key):
    spec = _spec(key)
    path = manifest_path(key)
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != spec["sha256"]:
        raise ValueError(
            f"manifest hash mismatch for {spec['name']}: {actual} != {spec['sha256']}"
        )
    rows = json.loads(data.decode("utf-8"))
    validate_manifest_rows(key, rows)
    return rows

def validate_manifest_rows(key, rows):
    spec = _spec(key)
    if not isinstance(rows, list) or len(rows) != spec["rows"]:
        raise ValueError(f"{key} must contain exactly {spec['rows']} rows")
    expected_order = list(range(1, spec["rows"] + 1))
    actual_order = [row.get("run_order") for row in rows]
    if actual_order != expected_order:
        raise ValueError(f"{key} rows are not in frozen run_order 1..{spec['rows']}")
    scenario_ids = [row.get("scenario_id") for row in rows]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError(f"{key} contains duplicate scenario_id")
    if any(row.get("stage") != spec["stage"] for row in rows):
        raise ValueError(f"{key} has incorrect stage")
    if spec["family"] is not None and any(
        row.get("family") != spec["family"] for row in rows
    ):
        raise ValueError(f"{key} has incorrect family")
    forced = sum(row.get("case_role") == "forced" for row in rows)
    controls = sum(row.get("case_role") == "control" for row in rows)
    expected_each = spec["rows"] // 2
    if forced != expected_each or controls != expected_each:
        raise ValueError(
            f"{key} must contain {expected_each} forced and {expected_each} controls"
        )
    if key == "A":
        for family in ("F1", "F2", "F3", "F4"):
            frows = [r for r in rows if r.get("family") == family]
            if len(frows) != 12:
                raise ValueError(f"A must contain 12 rows for {family}")
            if sum(r["case_role"] == "forced" for r in frows) != 6:
                raise ValueError(f"A {family} forced count must be 6")
            if sum(r["case_role"] == "control" for r in frows) != 6:
                raise ValueError(f"A {family} control count must be 6")

def key_for_b_family(family):
    if family not in {"F1", "F2", "F3", "F4"}:
        raise ValueError(f"invalid E3-B family: {family}")
    return f"B_{family}"
