from __future__ import annotations
import re

FINAL_RE = re.compile(
    r"\ACLAIM_VALUE: (TRUE|FALSE|UNKNOWN)\n"
    r"EVIDENCE_STATUS: (SUFFICIENT|INSUFFICIENT)\Z"
)

def parse_final(text):
    if not isinstance(text, str):
        return {"valid": False, "claim_value": None, "evidence_status": None}
    if text.endswith("\n"):
        text = text[:-1]
    m = FINAL_RE.fullmatch(text)
    if not m:
        return {"valid": False, "claim_value": None, "evidence_status": None}
    return {
        "valid": True,
        "claim_value": m.group(1),
        "evidence_status": m.group(2),
    }
