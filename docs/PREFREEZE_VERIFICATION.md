# E3 v0.7r2 pre-freeze verification record

The public release preserves the exact E3 v0.7r2 frozen package used to bind the final E3-A experiment.

## Frozen identity

- Exact package: `artifacts/VSO_E3_v0.7r2_EXACT_CANDIDATE.zip`
- ZIP SHA-256: `efaf2efbfbbc47b242c81c4493824b3fde8a5aaf95009c2d7b08df472d7e55c8`
- Frozen payload-set SHA-256: `92ab2a44e16a5347f6c803f4f8f66ca7240b95cbf730ea2ee795984db8e5c39d`
- Locked payload files: 47
- ZIP entries: 48
- Exact E3-A manifest SHA-256: `83c33aade50bca0c55482cd6ddd6711efd82f86674feb19b4cd77259679ab6a4`

## External build/isolation evidence

The exact package was built and tested by GitHub Actions run `36267374646` before scientific execution.

- Workflow result: success
- Head commit in the private canonical archive: `12d917cb27afd0f9f69c2af636e6e5e02c1a8bc0`
- GitHub Actions artifact digest: `sha256:6b09c1b92ddbc1d4bed334794f1395c0eef0e9ec59bf3139b648b1b0ebe1b37f`

The Actions artifact contained the exact inner package above. Its build and archive-isolation reports are preserved under `artifacts/actions/`.

## Offline test status

The exact frozen archive was re-extracted during preparation of this public release and the following frozen offline tests were rerun successfully:

1. `test_exact_package_r2.py`
2. `prove_f4_history_prefix_neutrality.py`
3. `test_frozen_manifests_r2.py`
4. `test_r2_repair.py`
5. `test_live_response_adapter.py`
6. `test_live_runner_r2.py`
7. `test_attempt_registry_r2.py`
8. `test_runner_policy_r2.py`
9. `test_official_runner_prepare_r2.py`

These are infrastructure/oracle/runner tests. They do not constitute additional scientific model runs.
