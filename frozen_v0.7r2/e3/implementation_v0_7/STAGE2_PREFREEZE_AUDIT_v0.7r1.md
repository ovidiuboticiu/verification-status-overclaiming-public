# E3 v0.7r1 parser/scorer/mock-runner focused audit

**Date:** 2026-09-25  
**Scientific model data:** none  
**Freeze status:** NOT FROZEN

## Verdict

**PASS FOR EXACT CANDIDATE-PACKAGE ASSEMBLY.**

No scientific Qwen call is authorized by this verdict.

## Manifest repair status

The first v0.7 candidate manifests are superseded for candidate-package purposes by `v0.7r1`.

Reason:
- required machine-readable acquisition/oracle/pair-policy fields were added;
- F4 edge containers were canonicalized to JSON-native lists so exact generator reproduction is testable.

The scientific design, seeds, families, templates, case counts, and held-out policy remain unchanged.

## Manifest validation

v0.7r1:
- E3-A rows = 48;
- four possible E3-B manifests = 24 rows each;
- total pre-generated rows = 144;
- pair count = 72;
- primary/independent parity evaluations = 31,644;
- forced invariant evaluations = 15,012;
- decisive-control evaluations = 72;
- failures = 0.

A/B disjointness remains clean in all four families.

## Parser/scorer/runner-policy validation

Offline mock/unit suite:
- checks = 323;
- failures = 0.

The suite confirms the required operational distinctions:
- model-generated invalid actions are scientific outcomes;
- invalid actions terminate the episode without rescue/retry;
- an infrastructure failure invalidates the entire attempt;
- model-behavior failures do not invalidate the whole attempt;
- a fifth tool-call attempt is not executed;
- strict output-format failures are retained;
- forced parse-invalid cases are not counted as evidence of non-overclaim.

## Preflight firewall

A committed `NON_SCIENTIFIC_PREFLIGHT_FIXTURE_v0.1` uses only a deterministic echo tool and a `PING-42` payload.

It contains no E3 state domain or family mechanism and is excluded from scientific scoring.

The fixture is implemented but has **not** been sent to a live model.

## Next gate

Authorized:
- assemble exact candidate frozen-package contents;
- hash them;
- run exact package self-tests/mock tests;
- perform exact-package audit.

Still prohibited:
- scientific E3-A Qwen calls;
- scientific E3-B Qwen calls;
- freeze declaration before investigator approval;
- any live preflight using an E3-family semantic case.
