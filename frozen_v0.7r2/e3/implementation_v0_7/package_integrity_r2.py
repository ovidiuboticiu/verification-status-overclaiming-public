from __future__ import annotations

import hashlib
import json
from pathlib import Path


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def payload_set_hash(entries) -> str:
    canonical = "".join(
        f"{row['path']}\0{row['git_blob_sha']}\0{row['size']}\n"
        for row in sorted(entries, key=lambda r: r["path"])
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def verify_payload_lock(root: Path, lock_path: Path):
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("status") != "LOCKED_EXACT_PACKAGE_PAYLOAD":
        raise ValueError("package payload lock is not in locked state")

    entries = lock.get("files")
    if not isinstance(entries, list) or len(entries) != lock.get("file_count"):
        raise ValueError("package payload lock file count mismatch")

    failures = []
    for row in entries:
        path = root / row["path"]
        if not path.is_file():
            failures.append(f"missing:{row['path']}")
            continue
        if path.stat().st_size != row["size"]:
            failures.append(f"size:{row['path']}")
        if git_blob_sha(path) != row["git_blob_sha"]:
            failures.append(f"blob:{row['path']}")

    actual_set_hash = payload_set_hash(entries)
    if actual_set_hash != lock.get("payload_set_sha256"):
        failures.append("payload_set_sha256")

    if failures:
        raise ValueError(
            "package payload verification failed: " + ", ".join(failures)
        )

    return {
        "payload_file_count": len(entries),
        "payload_set_sha256": actual_set_hash,
    }
