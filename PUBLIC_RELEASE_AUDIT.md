# Public-release audit

**Audit date:** 2026-09-30  
**Prepared release:** 1.0.0  
**Verdict:** PASS FOR CREATION OF A NEW CLEAN PUBLIC REPOSITORY

## 1. Scientific-state check

The public release preserves the closed project result without changing the protocol, raw outputs, scoring, selection rule, or stopping decision.

Final E3-A result preserved in the release:

- official attempt: `E3A-OFFICIAL-ATTEMPT-001`;
- attempt status: `VALID`;
- 48/48 official episode records;
- 24 forced opportunities;
- 18/24 forced `STATUS_OVERCLAIM`;
- 24 matched controls;
- 4/24 matched-control complete success;
- no family achieved the frozen 6/6 control gate;
- `selected_family = null`;
- `e3b_required = false`;
- E3-B not run;
- no E4 under the frozen protocol.

## 2. Exact-artifact verification

Verified during release preparation:

- frozen E3 ZIP SHA-256: `efaf2efbfbbc47b242c81c4493824b3fde8a5aaf95009c2d7b08df472d7e55c8`;
- frozen payload-set SHA-256: `92ab2a44e16a5347f6c803f4f8f66ca7240b95cbf730ea2ee795984db8e5c39d`;
- E3-A manifest SHA-256: `83c33aade50bca0c55482cd6ddd6711efd82f86674feb19b4cd77259679ab6a4`;
- official output ZIP SHA-256: `13f5baf79a895f7e720382a378c0ec021d4d5958984c3366d99af0aab73d81a1`.

The browseable `frozen_v0.7r2/` tree was verified byte-for-byte against the 48 members of the frozen ZIP. The browseable `results/official/` tree was verified byte-for-byte against the six files in the exact official-output ZIP.

## 3. Recalculation check

`tools/recalculate_e3a.py` was run against the prepared release using the oracle/parser/scorer imported from the exact frozen package.

Result:

- raw episode records: 48;
- per-episode rescoring mismatches: 0;
- phase analysis exact match: true;
- summary exact match: true;
- forced `STATUS_OVERCLAIM`: 18/24;
- complete matched controls: 4/24;
- eligible candidate families: none.

## 4. Frozen offline tests

All nine frozen v0.7r2 offline tests were re-run from the exact archive during release preparation and passed. No additional scientific model calls were made.

## 5. Privacy / credential check

The clean public snapshot and the UTF-8-readable contents of both exact ZIP artifacts were scanned for common credential and privacy patterns, including:

- personal email addresses;
- OpenAI-style API keys;
- GitHub access tokens;
- AWS access keys;
- Bearer credentials;
- private-key blocks;
- non-generic Windows user-profile paths.

No such sensitive material was found in the prepared release. The frozen package contains the generic historical path `C:\Users\User\...`, which does not identify a person.

The private canonical repository's Git history is intentionally excluded because its commit metadata contains the investigator's personal email address.

## 6. CI check

The clean release is validated before publication by the one-time private bootstrap workflow. It validates artifact hashes and ZIP/extracted-tree equality, performs the privacy/credential scan, independently recomputes the final E3-A scoring from raw traces, and reruns the frozen offline test suite.

A reusable workflow example is preserved at `ci/validate-release.yml`. It is intentionally not installed under `.github/workflows/` in the clean snapshot because the GitHub App token used for preparation is not permitted to push workflow-file changes. The equivalent validation commands ran successfully during release preparation.

## 7. Publication boundary

This PASS applies to creating a **new clean public repository from this snapshot**. It does not authorize changing the visibility of the private canonical repository, because that would expose historical Git/workflow metadata that the clean export intentionally excludes.
