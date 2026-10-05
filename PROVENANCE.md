# Public-release provenance

This repository is designed as a **clean public snapshot**, not as a mirror of the private development repository's Git history.

## Why the history is not reproduced

The private canonical archive contains extensive experimental development history and workflow metadata. The public release preserves the scientific artifacts, exact hashes, protocols, code, raw outputs, and stopping decisions without exposing unrelated historical account metadata.

## Private canonical snapshot anchor

Public-release preparation was based on the private canonical repository state whose final closure head was:

`b4c908841fd5c7a0b47272bcaffaa140430ccee6`

This SHA is an archival provenance anchor only; the underlying private repository is not required to inspect or validate the public release.

## Critical immutable artifacts

### Frozen E3 package

- File: `artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip`
- SHA-256: `efaf2efbfbbc47b242c81c4493824b3fde8a5aaf95009c2d7b08df472d7e55c8`
- Payload-set SHA-256: `92ab2a44e16a5347f6c803f4f8f66ca7240b95cbf730ea2ee795984db8e5c39d`

### Official E3-A output bundle

- File: `artifacts/E3_OFFICIAL_OUTPUT.zip`
- SHA-256: `13f5baf79a895f7e720382a378c0ec021d4d5958984c3366d99af0aab73d81a1`
- Official attempt: `E3A-OFFICIAL-ATTEMPT-001`

The browseable copies under `frozen_v0.7r2/` and `results/official/` are byte-for-byte extracted members of these immutable ZIPs. They can be checked with `python tools/validate_release.py`; the repository also preserves a reusable workflow example at `ci/validate-release.yml`, but that file is not installed as an active GitHub Actions workflow.

## Post-release correction record

The original v1.0.0 snapshot remains historically identifiable. Public-wrapper corrections made on 2026-10-05 are documented in `docs/POST_RELEASE_CORRECTIONS_2026-10-05.md`; they do not alter the frozen E3 package, official output ZIP, or experimental stopping decision.

### v1.0.2 audit remediation

The v1.0.2 correction release restores the exact CRLF bytes of the two browseable official JSON mirrors, adds a diagnostic F3 semantic sensitivity analysis, and refreshes current-release integrity metadata. The frozen E3 package, official output ZIP, historical frozen scores, and stopping decision are not rewritten.


### v1.0.3 final-audit remediation

The v1.0.3 documentation adds the F2 decisive-evidence sensitivity analysis. Under the stated F2 semantics, terminal `P3` plus the exact pre-operation value is already decisive, although the frozen acquisition checklist additionally required the operation-record call. Diagnostic F2 control success is **4/6** rather than frozen **0/6**.

Together with the separately documented F3 semantic sensitivity, the diagnostic all-family control total is **12/24** rather than frozen **4/24**. No family reaches **6/6**, so the frozen stopping decision remains unchanged.
