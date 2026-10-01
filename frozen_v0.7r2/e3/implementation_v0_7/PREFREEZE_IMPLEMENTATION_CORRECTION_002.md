# E3 pre-freeze implementation correction 002 — CI consistency findings

**Date:** 2026-09-26  
**Status:** CORRECTED BEFORE FREEZE / NO SCIENTIFIC E3 DATA

## Trigger

The first isolated E3 pre-freeze CI run executed the offline component tests successfully but failed the exact-package self-test.

This exposed three bookkeeping/harness consistency issues.

## C1 — payload-set hash sort semantics

The initial `E3_PACKAGE_PAYLOAD_LOCK_v0.7r1.json` payload-set SHA-256 was generated with JavaScript locale collation while the Python self-test used Python lexical/code-point sorting.

The per-file Git blob SHAs were not implicated.

Correction:
- regenerate the payload-set hash using the exact ordering implemented by the Python self-test;
- retain the documented canonical record format:
  `path + NUL + git_blob_sha + NUL + size + LF`.

## C2 — context evidence predicate too literal

The exact-package self-test searched for the literal text:

`Context Length: 8192`

while the canonical identity record states:

`loaded context length: 8192`

across adjacent Markdown lines.

Correction:
- use a case-insensitive regular expression matching the actual canonical field and value.

This changes only the evidence-checking predicate, not the required context length.

## C3 — stale static live-runner check count

The executable `test_live_runner_candidate.py` contains and executed **9** checks.

The previously written static JSON report incorrectly stated **10** checks.

Correction:
- `LIVE_RUNNER_FAKE_TRANSPORT_TEST_REPORT_v0.7r1.json` now records 9 checks.

The CI execution itself showed all 9 executable checks PASS.

## Scientific boundary

These corrections:
- were made before E3 freeze;
- use no E3-A/E3-B scientific model output;
- do not change the VSO construct;
- do not change families/templates/manifests/oracles;
- do not change the scientific prompt;
- do not change the live-model preflight result.

The exact package payload lock must be regenerated after these byte-level corrections and then re-tested.


## Follow-up CI correction

The first rerun after C1-C3 exposed a harness-only Python error: the revised context predicate used `re.search` but the module import was omitted.

Correction:
- add `import re` to `test_exact_package_v0_7r1.py`;
- regenerate the package payload lock again because the self-test byte identity changed;
- rerun the isolated E3 pre-freeze workflow.

This was a self-test implementation error. It did not execute or alter scientific E3 data.


## Second follow-up CI correction

The next isolated rerun showed that the raw-string pattern contained a double-escaped `\\s`, so it searched for a literal backslash instead of whitespace.

Correction:
- remove regex dependence from this predicate;
- normalize Markdown whitespace with `" ".join(identity.split()).lower()`;
- match the exact normalized field/value `loaded context length: \`8192\``.

Again, this affects only the self-test evidence predicate and no scientific configuration or data.


## Third follow-up CI correction

The previous text replacement inserted the two intended Python statements with a literal `\\n` sequence, producing a SyntaxError.

Correction:
- rewrite `test_exact_package_v0_7r1.py` cleanly as a complete file rather than applying another textual patch;
- keep the same package checks and scientific requirements;
- regenerate the payload lock and rerun isolated CI.

This remains a harness-only pre-freeze correction with no scientific model data.
