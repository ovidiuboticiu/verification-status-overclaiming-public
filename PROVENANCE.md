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

The browseable copies under `frozen_v0.7r2/` and `results/official/` are byte-for-byte extracted members of these immutable ZIPs and are checked by CI.
