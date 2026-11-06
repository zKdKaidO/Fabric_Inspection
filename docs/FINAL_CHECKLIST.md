# Final verification checklist

Finalization results are recorded in `docs/verification/final_verification.json`, `post_cleanup_benchmark.json`, `post_cleanup_tests.txt`, `post_cleanup_frontend_build.txt` and the import audit. This checklist is finalized after cleanup and all required checks complete.

- Original model copied, no refit; original SHA preserved.
- Final consolidated config frozen before regression; parameter values preserved.
- Seven profiles; normal-sample validation only; unknown fabric rejected.
- Golden image: deterministic, finite map, unchanged score within tight tolerance.
- Full source-image benchmark: fixed maps/scores and all main metrics reproduced.
- Compact final unit/product/API tests pass.
- API starts; commissioning, inspection, saved evidence, history and human-review path verified.
- Frontend production build succeeds; five pages, no research/parameter controls.
- No active import depends on research directories or removed engines.
- Full external backup verified before removal; every archived target is classified in CLEANUP_MANIFEST/CLEANUP_INVENTORY.
- Historical product records/evidence retained; obsolete profiles cannot run without frozen-profile revalidation.

See the final machine-readable verification result for actual pass/fail evidence rather than treating this checklist as a standalone test log.

## Post-quarantine verification

- Registered 6,586 files archived outside the active project, all sizes/SHA-256 verified; no unresolved targets.
- No deletions, copies or overwrites; original full backup untouched.
- Retained final source/model/config/history/evidence checked unchanged immediately after move.
- Dependency audit: PASS; experiments contains 0 files.
- Final tests: 13 passed, 0 failures, 0 skipped; golden image included.
- Frontend production build: PASS.
- Live product commissioning, rejection/inactivation, unseen-fabric rejection, inspection, evidence and history: PASS.
- Full 5,656-image post-cleanup regression: PASS; see verification/post_cleanup_benchmark.json.
- Detailed records: `verification/cleanup_archive_manifest.json`, `verification/post_cleanup_tests.xml`, `verification/post_cleanup_product_smoke.json`, `verification/post_cleanup_dependency_audit.json`, `verification/final_verification.json`.

Empty old directories were retained; mandatory test/build output is newly generated. No original research files returned to the active project.
