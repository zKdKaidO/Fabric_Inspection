# RAW-FABRID: final textile anomaly inspection project

## Industrial problem and scope

Woven textiles contain repetitive local structure, but yarn breaks, local brightness changes and small or elongated irregularities can be hard to inspect consistently. This project provides a local anomaly map and review workflow. It supports human inspection; it does not identify physical defect causes or autonomously reject material.

## Dataset and evaluation

The audited dataset comprises seven rolls, 709 captured source frames and 19,852 256×256 tiles. The test set contains 5,656 tiles from 202 parents: 687 defective and 4,969 normal. Of 507 normal-training parents, 406 were used for fitting and 101 for validation. The final normal model used 1,624 selected normal tiles and 89,632 sampled feature rows under the frozen sampling/cap conventions. Normal validation contains 2,828 tiles. Parent groups are disjoint. Defect foreground is exactly mask value 255. Small Q1, elongated, weak-contrast and boundary-crossing defects make aggregate image classification insufficient to describe localization quality.

Source images remain outside the application. Authoritative COCO offsets connect each tile to its real parent; filename grid numbers must not substitute for those offsets.

## Classical CV rationale and final method

The selected method is **Frozen Solution 1 with seven roll-specific normal reference profiles**. It uses fixed interpretable image operators and normal-only statistics. There is no universal PCA state, defect-trained classifier, deep-learning inference path or runtime parameter search.

Actual parent context → grayscale → tile P5/P95 normalization → 12 complex-Gabor magnitudes → 24D energy/dispersion + 1D center-surround contrast → robust feature standardization → frozen normal PCA → retained-eigenvalue whitening → RMS distance → normal median/MAD calibration → bilinear resize → Gaussian σ=1.5 → clip [0,25] → q0.999 image score → frozen business policy

Gabor magnitudes measure weave orientation/frequency. Local energy and dispersion provide 24 texture coordinates, while robust center-surround luminance supplies the 25th. Normal feature scaling, PCA and retained-space whitening produce a normal-relative RMS distance. The calibrated continuous map is resized and smoothed with the frozen settings. The detailed shapes, formulas, bank values, boundary rules and fitting convention are in `FINAL_PIPELINE.md`.

## Model development and selection

**C1 → H1 → Solution 1.** C1 established normal-only Gabor/PCA distance. H1 introduced real parent-image context for inference. Solution 1 retained that context and added one center-surround contrast coordinate. Solution 1 was selected for improved defect localization on the evaluated corpus. Subsequent research did not establish a validated replacement and is closed. The final source retains the selected method, not the research branches. A complete pre-cleanup snapshot is outside the application for historical audit.

## Architecture and operator workflow

The React/Vite console has Dashboard, Fabric Management, Commissioning, Inspect and History. FastAPI connects one `ClassicalInspectionEngine` to SQLite metadata and filesystem evidence. Normal commissioning selects an existing profile, checks a small normal-reference set at the unchanged review cutoff, and activates that profile only on validation success. It never fits a model or silently chooses another profile. New-fabric model fitting is unsupported in this frozen release.

For inspection the operator selects a ready fabric and a full source frame or catalog patch. Catalog inference uses the true parent and offsets. Full frames use overlapping tiles with real parent context and the existing mean map assembly. The model produces a map and score; a separate business policy produces PASS, REVIEW or HOLD. HOLD retains the earlier numerical hold boundary and requires human confirmation. Saved evidence includes original, raw map, fixed-scale heatmap and overlay. Human review and history remain available.

## Performance

Frozen Solution 1: Pixel AP **0.339632**, AUPRO@0.30 **0.764635**, Q1 Pixel AP **0.169904**, Pixel AUROC **0.903287**, Image AP **0.648075**, Image AUROC **0.846547**. At the unchanged policy it flags 240 of 687 defective images and 26 of 4,969 normal images: recall **34.93%**, precision **90.23%**, normal FPR **0.52%**. There are **447 missed defective patches**. Accuracy is not the primary measure for this imbalanced localization problem.

The archived original C1 and SingleNet baselines are documented in `FINAL_METRICS.md`, with the native-versus-harmonized image-score conventions made explicit. SingleNet is a documentation-only comparison. Its implementation and checkpoint are absent from the active project. CPU-versus-GPU timings do not establish equivalent-hardware speed superiority.

## Reproducibility and software verification

The original 25D model artifact is copied byte-for-byte, not fitted again. Its hash is `85c2b9102a4d38aade01ec84595eb9d1db1360e700ed359f9ac3ac7ccae9d81e`. The consolidated final configuration contains the unchanged numerical algorithm and operating parameters; its frozen hash is `90c1c9e0494df987675f6f8622ee6fb9c005e91d5461a89fcc7152e94733dca0`. Packaging a new consolidated YAML necessarily changes its bytes relative to the old experiment YAML; no claim is made that those different files have equal hashes. The final YAML is hash-checked before and after tests.

A fixed real-parent golden image checks shape, finiteness, deterministic output, native score and reference map. The compact tests cover preprocessing, Gabor, 24D/25D descriptors, contrast, PCA loading, distance, map generation, commissioning, policy, API, evidence and history. Full-corpus regression starts from source images, never cached descriptor substitution, and compares maps/scores and the frozen metric protocol. Final results and import audit are recorded in `FINAL_CHECKLIST.md` and `docs/verification`.

## Limitations

The low recall limits automated acceptance claims. A normal-looking score cannot prove defect absence. Fixed operators may miss very small or weak evidence; the image score may omit sparse peaks. No independent acquisition/factory validation or new-fabric generalization has been established, and the test cohort was repeatedly examined during research. The patch benchmark does not automatically transfer to whole frames or a production line. Annotation-negative pixels may include unrecorded anomalies. Physical sensor noise, illumination changes and line throughput require separate industrial validation.

## Final release work

The remaining presentation work is limited to usability refinement of the small web interface, editorial polishing of this report and rehearsal of the reproducible demonstration. Algorithm research, metric optimization and new parameter searches are outside this release.
