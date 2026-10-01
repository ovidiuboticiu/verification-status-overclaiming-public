# Run official E3 v0.7r2

**Status:** procedure candidate only. Do not run scientific E3 until the exact package audit passes and the investigator explicitly authorizes freeze.

## Preconditions

Before any scientific E3-A call:

- use the exact frozen extracted package;
- verify the outer archive SHA-256 against the freeze record;
- use the exact Qwen GGUF SHA-256 recorded in the canonical protocol;
- LM Studio server must use the frozen model/runtime/context/sampling configuration;
- use a new empty external output root;
- do not edit package files after freeze.

The official runner verifies the internal payload lock and scientific manifest hashes again before execution.

## E3-A

Example:

```powershell
python .\e3\implementation_v0_7\official_runner_r2.py `
  --phase A `
  --attempt-id E3A-OFFICIAL-ATTEMPT-001 `
  --output-root D:\E3_OFFICIAL_OUTPUT
```

The runner:

- loads the exact frozen 48-row E3-A manifest;
- verifies its SHA-256 and run order;
- verifies the exact package payload lock;
- creates a master `RUN_RECORD.json`;
- uses a fresh conversation for every episode;
- writes append-only attempt results/logs;
- calculates the frozen E3-A candidate-selection rule;
- writes `E3A_PHASE_ANALYSIS.json`.

If no family is selected, E3 closes and E3-B must not run.

## Infrastructure restart

If and only if an official attempt becomes `INVALID_INFRASTRUCTURE`, diagnose infrastructure without changing scientific design/package bytes.

A restart must use a new ID, for example:

`E3A-OFFICIAL-ATTEMPT-002`

The master registry rejects a restart if package hash, manifest hash, or frozen execution identity changed.

Never selectively rerun one episode.

## E3-B

Only if canonical valid E3-A selects a family:

```powershell
python .\e3\implementation_v0_7\official_runner_r2.py `
  --phase B `
  --attempt-id E3B-Fx-OFFICIAL-ATTEMPT-001 `
  --output-root D:\E3_OFFICIAL_OUTPUT
```

Replace `Fx` with the selected family recorded by `E3A_PHASE_ANALYSIS.json`.

The runner itself verifies:

- canonical valid A exists;
- A analysis belongs to that attempt;
- selected family matches the B attempt ID;
- package hash is unchanged;
- only the already pre-generated selected-family B manifest is loaded.

After B, E3 closes. There is no E4.

## Output structure

External output root contains:

- `RUN_RECORD.json` — master attempt registry;
- `E3A_PHASE_ANALYSIS.json` when A is valid;
- `E3B_PHASE_ANALYSIS.json` when B is valid;
- `attempts/<attempt_id>/results.jsonl`;
- `attempts/<attempt_id>/run_log.jsonl`;
- `attempts/<attempt_id>/summary.json` for valid attempts;
- `attempts/<attempt_id>/ATTEMPT_RUN_RECORD.json`;
- invalidation artifact when applicable.

No scientific output file may be silently overwritten.
