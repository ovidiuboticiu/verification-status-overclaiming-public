from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_HASHES = {
    "artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip": "efaf2efbfbbc47b242c81c4493824b3fde8a5aaf95009c2d7b08df472d7e55c8",
    "artifacts/E3_OFFICIAL_OUTPUT.zip": "13f5baf79a895f7e720382a378c0ec021d4d5958984c3366d99af0aab73d81a1",
    "artifacts/actions/E3_EXACT_PACKAGE_BUILD_REPORT_v0.7r2.json": "9be28fe32b00903d652c4c52b6366c3364cfc0b815d02bd94004668f65b7cdac",
    "artifacts/actions/E3_EXACT_ARCHIVE_ISOLATION_REPORT_v0.7r2.json": "ffef79af0b263b8649b80771b5b174fffbc0c8a5363c68c7e94f3251e2111a09",
    "docs/E3A_POST_RUN_AUDIT.md": "240e39d8d217fed1a23f73ac7d158069c0ef2d13fdf01c342a33d09e265ce098",
    "docs/E3_FINAL_CONCLUSION.md": "63834892ba593912bed297295b5370e39fc6021ae31b601c5fec2b2477751f43",
}

EXPECTED_OUTPUT_MEMBERS = {
    "E3A_PHASE_ANALYSIS.json": "291f4774e841849028e918f683308947f698b27827872ec0b07acc158176e7a8",
    "RUN_RECORD.json": "c09dfe9d81be2f1fff8006645e022b73b1dcf47cb10108709dad258b4bbe5089",
    "attempts/E3A-OFFICIAL-ATTEMPT-001/ATTEMPT_RUN_RECORD.json": "125854367ed438bbbff44bf3bb6d6e8f093f9b7518e6d1a3074bf973f3fa0fdd",
    "attempts/E3A-OFFICIAL-ATTEMPT-001/results.jsonl": "14556d7030118983ee7293016c03c737d4cc10f459563eaa55b9674d55f53fcb",
    "attempts/E3A-OFFICIAL-ATTEMPT-001/run_log.jsonl": "6876ebf8182f35329ad6af5cb0a774fa085b16b4c8d2429fe3eb066746d8d425",
    "attempts/E3A-OFFICIAL-ATTEMPT-001/summary.json": "2ec648b49738c7ace88bd55a30faea2b44a489992344741f090efeb16fdc5bc9",
}

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def fail(errors: list[str], message: str) -> None:
    errors.append(message)

def validate_critical_hashes(errors: list[str]) -> None:
    for rel, expected in EXPECTED_HASHES.items():
        path = ROOT / rel
        if not path.exists():
            fail(errors, f"missing critical artifact: {rel}")
            continue
        got = sha256_file(path)
        if got != expected:
            fail(errors, f"SHA-256 mismatch {rel}: {got} != {expected}")

def validate_frozen_extraction(errors: list[str]) -> None:
    archive = ROOT / "artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip"
    extracted = ROOT / "frozen_v0.7r2"
    with zipfile.ZipFile(archive, "r") as zf:
        if zf.testzip() is not None:
            fail(errors, "frozen package ZIP CRC failure")
            return
        names = zf.namelist()
        if len(names) != 48:
            fail(errors, f"frozen package entry count {len(names)} != 48")
        for name in names:
            target = extracted / name
            if not target.is_file():
                fail(errors, f"browseable frozen member missing: {name}")
                continue
            if target.read_bytes() != zf.read(name):
                fail(errors, f"browseable frozen member differs from ZIP: {name}")
        extracted_files = sorted(
            p.relative_to(extracted).as_posix()
            for p in extracted.rglob("*")
            if p.is_file()
        )
        if extracted_files != sorted(names):
            fail(errors, "browseable frozen tree has missing or extra files")

    lock = json.loads(
        (extracted / "e3/implementation_v0_7/E3_PACKAGE_PAYLOAD_LOCK_v0.7r2.json").read_text(encoding="utf-8")
    )
    if lock.get("file_count") != 47:
        fail(errors, f"payload lock file_count {lock.get('file_count')} != 47")
    if lock.get("payload_set_sha256") != "92ab2a44e16a5347f6c803f4f8f66ca7240b95cbf730ea2ee795984db8e5c39d":
        fail(errors, "payload-set SHA-256 differs from frozen identity")
    manifest = extracted / "e3/implementation_v0_7/manifests_v0_7r1/E3A_MANIFEST_CANDIDATE_v0.7r1.json"
    if sha256_file(manifest) != "83c33aade50bca0c55482cd6ddd6711efd82f86674feb19b4cd77259679ab6a4":
        fail(errors, "E3-A manifest SHA-256 mismatch")

def validate_output_extraction(errors: list[str]) -> None:
    archive = ROOT / "artifacts/E3_OFFICIAL_OUTPUT.zip"
    extracted = ROOT / "results/official"
    with zipfile.ZipFile(archive, "r") as zf:
        if zf.testzip() is not None:
            fail(errors, "official output ZIP CRC failure")
            return
        files = [n for n in zf.namelist() if not n.endswith("/")]
        prefix = "E3_OFFICIAL_OUTPUT/"
        normalized = {}
        for name in files:
            if not name.startswith(prefix):
                fail(errors, f"unexpected official output member prefix: {name}")
                continue
            rel = name[len(prefix):]
            normalized[rel] = zf.read(name)
        if set(normalized) != set(EXPECTED_OUTPUT_MEMBERS):
            fail(errors, f"official output member set mismatch: {sorted(normalized)}")
        for rel, expected_hash in EXPECTED_OUTPUT_MEMBERS.items():
            data = normalized.get(rel)
            if data is None:
                continue
            got = sha256_bytes(data)
            if got != expected_hash:
                fail(errors, f"official ZIP member SHA-256 mismatch {rel}")
            target = extracted / rel
            if not target.is_file():
                fail(errors, f"browseable official result missing: {rel}")
            elif target.read_bytes() != data:
                fail(errors, f"browseable official result differs from ZIP: {rel}")
        extracted_files = sorted(
            p.relative_to(extracted).as_posix()
            for p in extracted.rglob("*")
            if p.is_file()
        )
        if extracted_files != sorted(EXPECTED_OUTPUT_MEMBERS):
            fail(errors, "browseable official result tree has missing or extra files")

def validate_json(errors: list[str]) -> None:
    for path in ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(errors, f"invalid JSON {path.relative_to(ROOT)}: {exc}")
    for path in ROOT.rglob("*.jsonl"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            fail(errors, f"invalid UTF-8 JSONL {path.relative_to(ROOT)}: {exc}")
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except Exception as exc:
                fail(errors, f"invalid JSONL {path.relative_to(ROOT)}:{line_no}: {exc}")

def scan_text(errors: list[str], label: str, text: str) -> None:
    patterns = {
        "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
        "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
        "GitHub token": re.compile(r"\b(?:ghp|github_pat|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{10,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Bearer credential": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.I),
    }
    for kind, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            fail(errors, f"privacy/credential scan: {kind} found in {label}: {match.group(0)[:80]}")
    for match in re.finditer(r"[A-Z]:\\Users\\([^\\\r\n]+)\\", text, re.I):
        username = match.group(1)
        if username.lower() not in {"user", "runneradmin"}:
            fail(errors, f"privacy scan: non-generic Windows username in {label}: {username}")

def validate_privacy(errors: list[str]) -> None:
    text_suffixes = {".md", ".txt", ".json", ".jsonl", ".py", ".yml", ".yaml", ".cff", ""}
    skip_dirs = {".git", "release_tmp", "__pycache__"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in text_suffixes and path.name not in {"VERSION", "LICENSE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scan_text(errors, path.relative_to(ROOT).as_posix(), text)
    for zip_rel in [
        "artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip",
        "artifacts/E3_OFFICIAL_OUTPUT.zip",
    ]:
        with zipfile.ZipFile(ROOT / zip_rel, "r") as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue
                try:
                    text = zf.read(name).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                scan_text(errors, f"{zip_rel}!{name}", text)

def main() -> int:
    errors: list[str] = []
    validate_critical_hashes(errors)
    validate_frozen_extraction(errors)
    validate_output_extraction(errors)
    validate_json(errors)
    validate_privacy(errors)
    required = [
        "README.md", "LICENSE", "CITATION.cff", "PROVENANCE.md", "REPRODUCE.md",
        "docs/E3_FINAL_CONCLUSION.md", "docs/E3A_POST_RUN_AUDIT.md",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(errors, f"missing public-release file: {rel}")
    if errors:
        print("FAIL public release validation")
        for error in errors:
            print("-", error)
        return 1
    print("PASS public release validation")
    print("- frozen package SHA-256: efaf2efbfbbc47b242c81c4493824b3fde8a5aaf95009c2d7b08df472d7e55c8")
    print("- official output SHA-256: 13f5baf79a895f7e720382a378c0ec021d4d5958984c3366d99af0aab73d81a1")
    print("- browseable artifacts match exact ZIP members")
    print("- JSON/JSONL syntax valid")
    print("- credential/privacy scan passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
