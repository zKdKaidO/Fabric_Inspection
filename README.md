# RAW-FABRID Fabric Inspection

## 1. What is this?

A local textile anomaly inspection demonstration. **Frozen Solution 1 with seven roll-specific normal reference profiles** produces an anomaly map and image score; a separate frozen policy requests PASS, REVIEW or HOLD. Human review is required to confirm a defect. No new-model fitting or algorithm controls are available.

## 2. Dataset

RAW-FABRID contains seven rolls. The fixed test set has 5,656 tiles (687 defective, 4,969 normal). Original images and dataset remain outside this application: `A:\RAW_FABRID\images`, `A:\RAW_FABRID\MVTec`, plus the parent metadata/COCO files. Catalog inspection uses authoritative parent offsets, not filename grid numbers. Upload full parent frames rather than detached dataset crops.

## 3. Final Classical CV pipeline

Actual parent context → grayscale → tile P5/P95 normalization → 12 complex-Gabor magnitudes → 24D energy/dispersion + 1D center-surround contrast → robust feature standardization → frozen normal PCA → retained-eigenvalue whitening → RMS distance → normal median/MAD calibration → bilinear resize → Gaussian σ=1.5 → clip [0,25] → q0.999 image score → frozen business policy

Read [FINAL_PIPELINE.md](docs/FINAL_PIPELINE.md) for exact dimensions and stage explanations.

## 4. Project structure

```text
configs/classical_solution1.yaml       frozen algorithm and policy
models/classical_solution1.joblib      seven frozen reference profiles
src/fabric_inspection/vision/classical/  one inference entry point
src/fabric_inspection/product/         API, commissioning, decisions, evidence, SQLite
src/fabric_inspection/data/            optional external demo catalog adapter
src/fabric_inspection/evaluation/      fixed benchmark metric utilities
frontend/                             five-page React/Vite console
tests/                                compact tests and fixed regression fixtures
scripts/                              start, commission/inspect, verify benchmark
docs/                                 final explanation, metrics, report and audit
inspection_store/product/             persistent operational data and evidence
```

## 5. Installation

Use Python 3.11+ and Node/npm. The original environment is preserved; the checked package versions are pinned in `requirements-lock.txt` and `frontend/package-lock.json`.

```powershell
cd A:\RAW_FABRID\fabric_inspection
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
cd frontend
npm ci
cd ..
```

## 6. Start the application

```powershell
cd A:\RAW_FABRID\fabric_inspection
.\scripts\start_product.ps1
```

UI: `http://127.0.0.1:5173`. API: `http://127.0.0.1:8000/docs`. The script prints process IDs and saves logs under `inspection_store/logs`. Keep the local ports free before starting another instance.

## 7. Commission a fabric

Register a fabric and explicitly identify one of Rollo1A–Rollo7A. In Commissioning, upload/select at least four verified normal samples and validate them against that frozen profile. Every reference must stay below the unchanged review cutoff for activation. Validation failure does not activate it. **New-fabric model fitting is not supported in this frozen research release.** No nearest-profile fallback or refit occurs.

## 8. Inspect an image

Select a ready fabric in Inspect. Upload a full source frame or select a catalog test image. Run inspection; view original, anomaly heatmap, evidence overlay, image score and explanation. PASS means consistent with the selected profile, REVIEW recommends review, and HOLD requires human confirmation. Open History to record a human review.

A scripted demonstration is available via `.\.venv\Scripts\python.exe scripts/commission_and_inspect.py --help`.

## 9. Where results are stored

`inspection_store/product/inspection.db` contains fabric registrations, validation summaries, inspection records and human reviews. `inspections/<id>/` stores original PNG, raw anomaly NPY, heatmap and overlay. Uploaded files go under `uploads/`. Historical evidence is preserved; old fabric registrations require revalidation under a frozen profile.

## 10. Run tests

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q
cd frontend
npm run build
cd ..
.\.venv\Scripts\python.exe -B scripts/verify_frozen_benchmark.py
```

The last command is a reproduction check, not a research experiment, and requires the complete external dataset. The golden test also needs its fixed external source frame and explicitly skips if that dataset is absent. See `docs/verification` for the completed local test/benchmark evidence.

## 11. Final performance

Pixel AP **0.339632** · AUPRO@0.30 **0.764635** · Q1 Pixel AP **0.169904** · Pixel AUROC **0.903287** · Image AP **0.648075** · Image AUROC **0.846547**.

Frozen-policy recall **34.93%**, precision **90.23%**, normal alarms **26/4,969 (0.52%)**. [FINAL_METRICS.md](docs/FINAL_METRICS.md) explains these metrics and the documentation-only C1/SingleNet comparison.

## 12. Limitations

This is not production-certified. The fixed policy misses 447 of 687 defective test tiles. PASS is not a guarantee of defect-free fabric. Seven known profiles do not establish unseen-fabric generalization; full-frame assembly has no separate industrial acceptance validation. The corpus was repeatedly used during development. Accuracy is not the primary metric in this imbalanced localization problem.

Start with [FINAL_PROJECT_REPORT.md](docs/FINAL_PROJECT_REPORT.md), [PRODUCT_ARCHITECTURE.md](docs/PRODUCT_ARCHITECTURE.md), [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) and [FINAL_CHECKLIST.md](docs/FINAL_CHECKLIST.md). Research is closed; the original workspace is preserved outside the application, as documented in [CLEANUP_MANIFEST.md](docs/CLEANUP_MANIFEST.md).
