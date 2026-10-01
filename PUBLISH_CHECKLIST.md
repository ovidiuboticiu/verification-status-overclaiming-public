# Publication checklist

Release snapshot: `1.0.0`.

Completed during clean bootstrap:
- exact frozen E3 artifact assembled and hash-verified;
- exact official E3-A output restored and hash-verified;
- browseable frozen and result trees retained;
- clean orphan Git history created with GitHub noreply author identity;
- artifact/privacy validation passed;
- independent E3-A recomputation passed with 0 scoring mismatches;
- all nine frozen offline tests passed.

Before changing repository visibility to Public:
- confirm `main` points to the single clean release commit;
- confirm the clean commit uses the account's GitHub `users.noreply.github.com` author address;
- remove the remaining private bootstrap workflow run from Actions history;
- optionally create tag/release `v1.0.0`.

A reusable CI workflow example is preserved at `ci/validate-release.yml`. It can be installed later under `.github/workflows/` if desired.

Suggested description:

> Reproducible research artifact for testing evidence-status overclaiming in an LLM agent; closed experiment, no novelty or prevalence claim.
