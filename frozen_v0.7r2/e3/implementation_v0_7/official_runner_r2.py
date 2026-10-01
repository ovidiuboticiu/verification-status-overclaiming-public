from __future__ import annotations

import argparse
import json
from pathlib import Path

from attempt_registry_r2 import (
    exclusive_registry_lock,
    finalize_attempt,
    load_registry,
    reserve_attempt,
)
from attempts_r2 import validate_attempt_id
from execution_identity import get_execution_identity
from live_runner_r2 import run_live_attempt
from manifest_loader import (
    MANIFEST_SPECS,
    key_for_b_family,
    load_manifest,
    manifest_sha256,
)
from package_integrity_r2 import verify_payload_lock
from phase_analysis import analyze_e3a, analyze_e3b

BASE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK = BASE / "E3_PACKAGE_PAYLOAD_LOCK_v0.7r2.json"


def _write_new_json(path: Path, obj):
    if path.exists():
        raise ValueError(f"refusing overwrite: {path}")
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _load_a_analysis(output_root: Path):
    path = output_root / "E3A_PHASE_ANALYSIS.json"
    if not path.is_file():
        raise ValueError(
            "E3-B requires canonical E3A_PHASE_ANALYSIS.json in output root"
        )
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("phase") != "E3-A":
        raise ValueError("invalid E3-A analysis artifact")
    return obj


def prepare_official_phase(
    phase,
    attempt_id,
    output_root,
    lock_path=DEFAULT_LOCK,
):
    output_root = Path(output_root)
    lock_path = Path(lock_path)

    package = verify_payload_lock(ROOT, lock_path)
    package_hash = package["payload_set_sha256"]
    identity = get_execution_identity()

    if phase == "A":
        family = None
        manifest_key = "A"
        phase_key = "A"
        if not validate_attempt_id(attempt_id, "A"):
            raise ValueError("invalid E3-A official attempt_id")
    elif phase == "B":
        a_analysis = _load_a_analysis(output_root)
        family = a_analysis.get("selected_family")
        if family is None:
            raise ValueError(
                "E3-B prohibited: E3-A did not select a candidate family"
            )
        manifest_key = key_for_b_family(family)
        phase_key = f"B_{family}"
        if not validate_attempt_id(attempt_id, "B", family=family):
            raise ValueError(
                f"invalid E3-B attempt_id for selected family {family}"
            )

        registry = load_registry(output_root)
        canonical_a = registry.get(
            "canonical_valid_attempts",
            {},
        ).get("A")
        if canonical_a is None:
            raise ValueError(
                "E3-B prohibited without canonical VALID E3-A attempt"
            )
        if a_analysis.get("attempt_id") != canonical_a:
            raise ValueError(
                "E3-A analysis does not belong to canonical VALID A attempt"
            )
        if a_analysis.get("package_hash") != package_hash:
            raise ValueError(
                "E3-A analysis package hash differs from current package"
            )
    else:
        raise ValueError("phase must be A or B")

    rows = load_manifest(manifest_key)
    manifest_hash = manifest_sha256(manifest_key)
    manifest_name = MANIFEST_SPECS[manifest_key]["name"]

    return {
        "phase": phase,
        "family": family,
        "phase_key": phase_key,
        "manifest_key": manifest_key,
        "manifest_name": manifest_name,
        "manifest_hash": manifest_hash,
        "rows": rows,
        "package_hash": package_hash,
        "execution_identity": identity,
    }


def run_official_phase(
    phase,
    attempt_id,
    output_root,
    lock_path=DEFAULT_LOCK,
    transport=None,
):
    output_root = Path(output_root)

    with exclusive_registry_lock(output_root):
        prepared = prepare_official_phase(
            phase=phase,
            attempt_id=attempt_id,
            output_root=output_root,
            lock_path=lock_path,
        )

        reserve_attempt(
            output_root=output_root,
            attempt_id=attempt_id,
            phase_key=prepared["phase_key"],
            package_hash=prepared["package_hash"],
            manifest_hash=prepared["manifest_hash"],
            execution_identity=prepared["execution_identity"],
        )

        attempt_dir = output_root / "attempts" / attempt_id

        try:
            attempt = run_live_attempt(
                manifest_name=prepared["manifest_name"],
                rows=prepared["rows"],
                attempt_id=attempt_id,
                output_dir=attempt_dir,
                package_hash=prepared["package_hash"],
                manifest_hash=prepared["manifest_hash"],
                transport=transport,
            )

            if attempt.status == "INVALID_INFRASTRUCTURE":
                finalize_attempt(
                    output_root,
                    attempt_id,
                    "INVALID_INFRASTRUCTURE",
                    attempt.invalidation_reason,
                )
                return {
                    "attempt_status": attempt.status,
                    "attempt_id": attempt_id,
                    "analysis": None,
                }

            if phase == "A":
                analysis = analyze_e3a(attempt.episode_records)
                analysis.update(
                    {
                        "attempt_id": attempt_id,
                        "package_hash": prepared["package_hash"],
                        "manifest_hash": prepared["manifest_hash"],
                    }
                )
                analysis_path = output_root / "E3A_PHASE_ANALYSIS.json"
            else:
                analysis = analyze_e3b(
                    attempt.episode_records,
                    prepared["family"],
                )
                analysis.update(
                    {
                        "attempt_id": attempt_id,
                        "package_hash": prepared["package_hash"],
                        "manifest_hash": prepared["manifest_hash"],
                    }
                )
                analysis_path = output_root / "E3B_PHASE_ANALYSIS.json"

            _write_new_json(analysis_path, analysis)
            finalize_attempt(
                output_root,
                attempt_id,
                "VALID",
                None,
            )
            return {
                "attempt_status": "VALID",
                "attempt_id": attempt_id,
                "analysis": analysis,
            }

        except Exception as exc:
            attempt_dir.mkdir(parents=True, exist_ok=True)
            wrapper_invalidation = attempt_dir / "WRAPPER_INVALIDATION.json"
            if not wrapper_invalidation.exists():
                _write_new_json(
                    wrapper_invalidation,
                    {
                        "attempt_id": attempt_id,
                        "status": "INVALID_INFRASTRUCTURE",
                        "reason": "RUNNER_EXCEPTION",
                        "message": str(exc),
                        "package_hash": prepared["package_hash"],
                        "manifest_hash": prepared["manifest_hash"],
                        "execution_identity": prepared["execution_identity"],
                        "canonical": False,
                    },
                )
            registry = load_registry(output_root)
            row = next(
                (
                    x for x in registry.get("attempts", [])
                    if x.get("attempt_id") == attempt_id
                ),
                None,
            )
            if row is not None and row.get("status") == "RUNNING":
                finalize_attempt(
                    output_root,
                    attempt_id,
                    "INVALID_INFRASTRUCTURE",
                    "RUNNER_EXCEPTION",
                )
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Official frozen E3 v0.7r2 phase runner."
    )
    parser.add_argument("--phase", choices=["A", "B"], required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument(
        "--lock",
        default=str(DEFAULT_LOCK),
    )
    args = parser.parse_args()

    result = run_official_phase(
        phase=args.phase,
        attempt_id=args.attempt_id,
        output_root=Path(args.output_root),
        lock_path=Path(args.lock),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
