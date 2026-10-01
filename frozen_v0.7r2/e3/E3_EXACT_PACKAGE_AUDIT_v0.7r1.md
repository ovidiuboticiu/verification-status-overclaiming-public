# E3 v0.7r1 exact-package audit

**Date:** 2026-09-26  
**Audited archive:** `VSO_E3_v0.7r1_EXACT_CANDIDATE.zip`  
**Archive SHA-256:** `2ba72051e7cf0bcd98d10a54f2d01ff914b3f1568f0eb030e95ae2d45183e10e`  
**Scientific model data inspected:** none  
**Freeze status:** NOT FROZEN

## Verdict

**NOT READY FOR FREEZE — IMPLEMENTATION/PACKAGING REPAIR REQUIRED.**

The archive itself is deterministic and byte-integral, and the isolated E3 CI suite passes in the repository. However, exact-package audit found several execution/reproducibility blockers that must be repaired before an official scientific run can be authorized.

No conceptual redesign of the four E3 families is required.

---

## What passed

### A1 — exact payload lock

PASS.

- locked payload files: 41;
- payload-set SHA-256:
  `5d0d30e5cd6dc46378bd7cb853882005ab4ed238a36a9d48e65be2d254131a43`;
- exact-package payload self-test: PASS;
- five scientific manifests match their frozen SHA-256/byte counts;
- archived non-scientific preflight status: PASS.

### A2 — isolated E3 CI

PASS.

Workflow:
`E3 pre-freeze integrity`

Successful run:
`36263157233`

The following all passed before archive creation:
- F4 history-prefix neutrality;
- stage-1 oracle parity / forced invariants;
- stage-2 parser/scorer/mock-runner suite;
- live-response adapter offline test;
- live-runner fake-transport test;
- exact-package payload self-test.

The separate general `VSO integrity` workflow has historical E1 artifact/hash failures. Those are not used as evidence for E3 package validity and must not be described as a repository-wide green CI state.

### A3 — deterministic archive construction

PASS.

The archive build:
- used ZIP_STORED;
- used fixed 1980-01-01 timestamps;
- verified ZIP CRC;
- verified every archived entry byte-for-byte against its repository source;
- produced 42 entries = 41 locked payload files + the payload-lock file.

Downloaded artifact verification reproduced the same inner archive SHA-256.

---

# Freeze blockers

## B1 — HIGH — archive is not self-contained for its own archived tests

Directly executing the archived tests after extracting the exact ZIP produced:

- `prove_f4_history_prefix_neutrality.py`: PASS;
- `test_live_response_adapter.py`: PASS;
- `test_live_runner_candidate.py`: PASS;
- `test_exact_package_v0_7r1.py`: PASS;
- `test_stage1.py`: FAIL because `generate_a_manifest.py` is absent;
- `test_stage2.py`: FAIL because `generate_manifests_v0_7r1.py` depends on the older `implementation_v0_7/manifests/*.v0.7.json` files, which are absent.

The package therefore cannot reproduce all of the tests it contains without external repository files.

Required repair:
- either package the declared generator dependencies;
- or replace the archived stage-1/stage-2 tests/generator with frozen-manifest tests that are self-contained.

Do not label the current ZIP a self-contained frozen scientific package.

---

## B2 — HIGH — no official execution entry point binds the run to the exact package and manifest

The package contains the lower-level function:

`run_live_attempt(manifest_name, rows, attempt_id, output_dir, package_hash, manifest_hash)`

but no official CLI/entry point that:

- loads the immutable E3-A manifest itself;
- verifies its SHA-256 before execution;
- verifies the package/payload lock before execution;
- requires exactly all 48 E3-A rows;
- enforces the frozen run order;
- prevents a subset/arbitrary row list from being marked VALID;
- selects only a pre-generated E3-B manifest after frozen A analysis.

The current lower-level runner accepts caller-supplied `rows`, `package_hash`, and `manifest_hash`; those hashes are recorded but not validated.

Required repair:
add an official frozen runner wrapper that verifies package + manifest bytes, full manifest cardinality and order, and then invokes the lower-level episode runner.

---

## B3 — HIGH — E3-A candidate selection and E3-B result logic are not implemented in the exact package

The prospectively defined protocol requires:

E3-A family eligibility:
- 6/6 matched controls complete-success;
- forced STATUS_OVERCLAIM count >=1.

If multiple families qualify:
- highest forced overclaim count;
- fixed tie-break `F1 > F2 > F3 > F4`.

E3-B then uses only the pre-existing selected-family manifest.

The current exact package has no deterministic phase-analysis component implementing:
- per-family eligibility;
- candidate selection;
- no-candidate closure;
- E3-B control-failure result;
- HELD_OUT_OCCURRENCE;
- TEMPLATE_INSTANCE_REPLICATION;
- FAMILY_LEVEL_REPLICATION.

Required repair:
implement and test deterministic A/B phase-analysis code before freeze.

---

## B4 — HIGH — official attempt identity / RUN_RECORD enforcement is incomplete

Protocol OL-4 requires immutable official attempt IDs and a RUN_RECORD containing:
- every attempt_id;
- start/end timestamps;
- frozen package hash;
- manifest hash;
- model/runtime identity;
- VALID / INVALID_INFRASTRUCTURE status;
- invalidation reason;
- canonical valid attempt.

Current package:
- does not validate the official attempt-id pattern;
- does not enforce uniqueness of attempt_id across output directories;
- prevents output-directory overwrite, but that is not equivalent to attempt-id uniqueness;
- RUN_RECORD records package/manifest hashes but does not record the full model/GGUF/runtime/context/sampling identity.

Required repair:
add attempt-id validation/uniqueness and complete execution-identity recording.

---

## B5 — MEDIUM — official summary does not fully implement OL-3 accounting

Protocol OL-3 requires separate reporting of:
- `manifest_episode_n`;
- `episode_attempted_n`;
- normal/model-failure counts;
- final parse-valid counts;
- forced opportunity / parse-valid / overclaim numerator;
- control acquisition/correctness counts.

Current `summarize_attempt` uses:
- `manifest_episode_n = len(attempted_scenario_ids)`, which is actually an attempted count;
- no explicit `episode_attempted_n`;
- no per-family control acquisition / claim correctness / evidence-status correctness breakdown.

Required repair:
make the official summary schema match the frozen accounting vocabulary exactly and add tests.

---

## B6 — HIGH — exact package does not contain a self-contained canonical protocol

The only top-level design document in the archive is v0.7, which is explicitly a narrow delta and says that major scientific/operational rules are retained from v0.6/v0.5/v0.4.

The archive omits those predecessor protocol files.

Consequently, a reader of the exact ZIP cannot recover from the ZIP alone:
- the complete F1/F2/F3/F4 canonical grammar;
- family eligibility/candidate selection;
- attempt/restart locks;
- full stopping/closure rules;
- the complete implementation gate.

Required repair:
either include the full protocol chain v0.4-v0.7, or preferably add one consolidated canonical E3 protocol document whose content is frozen with the execution package.

---

# Non-blocking observation

The runtime evidence shows the selected LM Studio GGUF runtime `CPU llama.cpp (Windows) v2.41.0`, loaded Qwen model, Context Length 8192, GGUF SHA-256, and successful non-scientific transport preflight.

The API preflight proves acceptance of `max_tokens=512` and observed completion within that limit; it does not independently inspect LM Studio's internal enforcement implementation. This limitation is already recorded and does not by itself block freeze.

---

# Repair scope recommendation

A narrow implementation revision is sufficient. Do not alter:
- the VSO construct;
- four families;
- semantic templates;
- A/B manifests;
- A/B seeds/order;
- oracles;
- prompts;
- sampling configuration;
- episode counts;
- held-out instances.

Recommended next revision: **v0.7r2 implementation/package repair only**.

It should add:
1. consolidated canonical protocol or missing canonical protocol chain;
2. self-contained frozen-manifest test path;
3. official A/B execution entry point with package/manifest verification;
4. attempt-ID and full RUN_RECORD enforcement;
5. deterministic E3-A selection + E3-B result analyzer;
6. exact OL-3 summary schema;
7. new payload lock, deterministic archive, isolated CI, and exact-package audit.

No scientific Qwen E3-A/E3-B calls are authorized until the repaired package passes this audit and the investigator explicitly approves freeze.
