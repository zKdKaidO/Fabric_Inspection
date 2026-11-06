# Final model provenance

- Final model: `models/classical_solution1.joblib`.
- Model SHA256: `85c2b9102a4d38aade01ec84595eb9d1db1360e700ed359f9ac3ac7ccae9d81e`; exactly equal to the original frozen 25D artifact.
- Final configuration: `configs/classical_solution1.yaml`.
- Final config SHA256: `90c1c9e0494df987675f6f8622ee6fb9c005e91d5461a89fcc7152e94733dca0`; frozen before regression and unchanged afterward.
- Original experiment config SHA256: `31fd62cc5de5f0053388c991d63b8801dd65a746b428cb6d142417770d0a177d`. The new config consolidates original bank settings, unchanged numerical policy and inference constants; equal file hashes are not expected across this packaging migration.
- Seven roll-specific normal profiles; normal-only PCA ≥95% variance, ranks 19 for Rollo1A–Rollo6A and 18 for Rollo7A.
- Source fit date 3 November 2026; final packaging 6 November 2026.
- 406 fitting parents / 101 normal validation parents / 202 test parents; 1,624 selected normal fitting tiles; 89,632 sampled rows; 2,828 normal validation tiles; 5,656 test tiles.
- Artifact class paths remain serialization-compatible in `vision/classical/normal_model.py`; inference has no dependency on an experiment directory. Unused historical residual fields remain in the serialized artifact only; there is no residual-score engine or fitting API.
- Original texture fitting used tile context; the contrast column used parent context at the same sites. This original convention is preserved by using the unchanged artifact.
- Full model/parameter/threshold refitting during cleanup: **none**.
- Final benchmark and exact reproduction: `tests/fixtures/frozen_metrics.json`, `docs/verification/post_cleanup_benchmark.json`.
- Model/config identity record: `tests/fixtures/model_identity.json`; golden reference: `tests/fixtures/golden_solution1.json` and `golden_map.npy`.
- Complete external pre-cleanup snapshot: `A:\RAW_FABRID\archive\pre_finalization_20261106`. Its full-file verification manifest is in `A:\RAW_FABRID\finalization_work_20261106\backup_verified.json`.

The concise fitting manifest and fixed test manifest are retained under `tests/fixtures` for reproducibility. Data pixels remain external, except the small generated golden anomaly-map reference used by the test. No deep-learning implementation is retained.
