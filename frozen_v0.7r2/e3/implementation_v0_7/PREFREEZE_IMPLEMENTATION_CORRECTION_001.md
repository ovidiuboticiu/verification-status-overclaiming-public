# E3 pre-freeze implementation correction 001 — manifest machine-readable metadata + canonical JSON reproduction

**Date:** 2026-09-25  
**Status:** RESOLVED PRE-DATA  
**Scientific model data:** none

## Finding

While implementing the parser/scorer layer, two pre-freeze implementation gaps were found in the first v0.7 candidate manifests.

1. The JSON rows did not carry several machine-readable fields already required by the pre-freeze protocol:
   - `environment_oracle_claim`;
   - `environment_oracle_status`;
   - `required_decisive_observation_set`;
   - `allowed_visible_difference_fields`;
   - `allowed_hidden_difference_fields`.

2. The F4 generator used Python tuples for edge structures in memory. JSON serialization converted them to lists, so a strict `loaded_manifest == generator_build()` reproduction check failed for manifests containing F4 even though the serialized semantic content was equivalent.

No scientific model output existed when these issues were found.

## Repair

A superseding candidate-manifest revision `v0.7r1` was generated.

Changes:
- add the required machine-readable oracle/acquisition/pair-policy fields;
- normalize F4 edge structures to JSON-native lists before serialization;
- preserve all v0.7 scientific semantics, seeds, family/template counts, pairing, A/B instance selection, and run order;
- retain the original v0.7 candidate manifests as provenance rather than overwriting them.

## Result

`v0.7r1` exact generator reproduction: PASS.

Full offline validation:
- 72 forced/control pairs;
- 31,644 primary/independent oracle parity sequences;
- 15,012 forced invariant sequences;
- 72 decisive-control checks;
- A/B tuple overlap = 0 for every family;
- A/B instance overlap = 0 for every family;
- A/B observable-signature collisions = 0 for every family;
- failures = 0.

This correction does not freeze E3 and does not authorize scientific Qwen calls.
