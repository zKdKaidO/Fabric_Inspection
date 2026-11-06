# Cleanup manifest — archived outside the active project

6 November 2026. Cleanup uses a non-destructive, same-volume quarantine. **Archived outside the active project.** No deletion, file-content rewrite, recompression, copy or overwrite was used for the registered targets.

## Completed scope

|Check|Result|
|---|---:|
|Registered targets|6,586|
|Successfully archived|6,586|
|Unresolved / could not be moved|0|
|Active files in the project experiments tree|0|
|SHA-256 and sizes before/after move|PASS for all 6,586|
|Protected source/model/config/product/history/evidence files|75 unchanged immediately after move|
|Deletion/copy/overwrite operations|0 / 0 / 0|

Archive: `A:\RAW_FABRID\_archive\fabric_inspection_research_20261106`. Every original relative path is retained. `verification/cleanup_archive_manifest.json` records original path, archive path, relative path, size, SHA-256 before and after, dependency check and status for every target. `verification/cleanup_archive_move_receipt.json` records the same-volume move. `verification/cleanup_archive_verification.json` records source absence and protected-file checks.

## Original inventory and exact registration

`CLEANUP_INVENTORY.csv` remains the original full file/directory classification: A final code; B final model/config; C product; D tests; E documentation; F experiment-only; G generated/duplicate; H uncertain. Its original `DELETE` action describes the earlier proposed classification only. **Execution used archive moves, not deletion.** No new targets were added. The exact 6,586-file registration has SHA256 `94009997091b1f4a67b992ef8ebc83791df6d80570a559d339aa5ddcb4023cd4`.

Only the 6,450 registered F entries and 136 registered G entries were moved. All other source, final artifact/configuration, final tests, final documentation, frontend source, operational metadata/history/evidence and installed local dependencies were retained. No uncertain item was moved. No protected dependency was silently reclassified.

## Dependency-aware extraction and nine clarified files

Solution 1's actual parent-context extraction, original Gabor/texture/center-surround operations and frozen normal model now reside under `src/fabric_inspection/vision/classical`. `ClassicalInspectionEngine` is the single inference entry point. The unchanged artifact is `models/classical_solution1.joblib`; `configs/classical_solution1.yaml` contains the consolidated, unchanged numerical policy and settings.

The user explicitly authorized archiving the nine registered files in otherwise protected folders after dependency verification:

- Eight frontend files were generated prior deployment output, TypeScript build caches, or redundant generated Vite config/declaration files. No final React/source asset imports them as a source dependency. The retained `vite.config.ts` and generated JS have identical tokens apart from whitespace and optional semicolons. Source favicon and all React/CSS/HTML/package/build inputs remain. The fresh production build succeeded after archiving.
- `inspection_store/product/models/demo-rollo4a.classical.joblib` was an obsolete model. No READY registration or final engine loads it. The final engine uses the SHA-verified Solution 1 artifact. SQLite metadata, inspection history, source uploads and evidence were retained; commissioning/inspection/evidence/history passed again afterward.

Their individual dependency decisions and before/after hashes are included in the archive manifest. `verification/frontend_archive_dependency_check.json` records the frontend review. The original source paths were absent immediately after the move. Mandatory tests and the frontend rebuild subsequently created **new generated output/cache files** at some of those paths; those are fresh outputs, not unarchived original research artifacts. They were not moved again or substituted into the archive.

## What was archived

Research-only implementations and artifacts: obsolete C0/C1/C2 engines and models/configs, low-rank/refinement/NCSR/TVSL/Gabor-LR and periodic candidates, failed scoring/aggregation candidates, H-A/H-B/H-C diagnostics, attribution/forensic/sequential/search/ablation runners, SingleNet/PatchCore and other candidate implementations, and historical research documents. Final metric comparisons and model/split/golden provenance were extracted before quarantine.

Final fitting/test/golden records remain under `tests/fixtures`; concise final metrics and documentation-only C1/SingleNet comparisons remain under final docs/verification. Historical product decisions are preserved rather than relabeled as new Solution 1 results. Old fabric registrations require explicit frozen-profile validation before new inference.

## Archive and original backup

The archive preserves the original relative tree for recovery. The separate, earlier full backup at `A:/RAW_FABRID/archive/pre_finalization_20261106` remains untouched: 47,441 files / 63.49 GiB, originally verified file-by-file with SHA-256. Its verification record remains outside the application at `A:/RAW_FABRID/finalization_work_20261106/backup_verified.json`.

No directory deletion was attempted. Empty old directories, including `experiments`, may remain because deletion is restricted. They contain no active research files and are omitted from the important-file tree except where explicitly noted. Installed `.venv` and `frontend/node_modules` are generated runtime dependencies retained for local use; the final application imports no deep-learning engine.

## Post-cleanup verification

- Final dependency audit: PASS, 29 Python source/script/test files; no runtime dependency on research code. Historical docstrings, negative import assertions and documentation-only provenance are distinguished from imports.
- Final tests:13passed, including the real-parent golden regression.
- Frontend production build: PASS using the retained TypeScript config.
- Live product: PASS for seven-profile enumeration, successful and failed validation, explicit unseen-fabric rejection, real catalog and full-parent upload inspection, saved evidence, retrieval and history. Real HOLD remains a request for human confirmation.
- Full 5,656-image source regression: PASS; see verification/post_cleanup_benchmark.json.
- Model and final-config hashes are checked before/after verification; no refit or parameter/threshold change occurred.

Final verification receipts are under `docs/verification`; the final state is recorded in `verification/final_verification.json`.
