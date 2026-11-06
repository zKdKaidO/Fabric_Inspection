# Product architecture

The local product has one inference engine: Frozen Solution 1 with seven roll-specific normal reference profiles. FastAPI coordinates the engine, a SQLite product database and filesystem evidence. React/Vite provides five small pages: Dashboard, Fabric Management, Commissioning, Inspect and History.

`product/api.py` → `product/service.py` → `vision/classical/engine.py` → map and score → `product/decision.py` → `product/evidence.py` + `product/database.py`.

## Frozen commissioning

An operator explicitly identifies Rollo1A–Rollo7A when registering a fabric. Commissioning requires at least four normal reference images. Each is scored against that selected frozen profile using the existing score and review cutoff. **Every reference must be below the cutoff** to activate the profile. Validation failure leaves it inactive. An uploaded reference is a full physical source frame; catalog patches use their actual parent and COCO offsets. Known training-normal catalog samples are the only selectable demo validation samples; defective/test labels never fit or calibrate a model.

There is no nearest-profile fallback, no universal PCA and no fitting operation in commissioning. For an unseen fabric: **“New-fabric model fitting is not supported in this frozen research release.”** Passing a small reference set is an operational compatibility check, not proof of generalization.

## Model versus business policy

The engine emits the map and q0.999 scalar. The policy maps score < review to PASS, review ≤ score < hold to REVIEW, and score ≥ hold to HOLD. The original numerical hold boundary is retained; only the earlier FAIL presentation wording is replaced. The operator cannot edit Gabor, PCA, thresholds, q, smoothing or weights. Only a human review can record CONFIRMED_DEFECT.

## Data and persistence

External images and dataset stay under `A:/RAW_FABRID/images` and `A:/RAW_FABRID/MVTec`. The application stores product metadata in `inspection_store/product/inspection.db`, normal/inspection uploads under `uploads`, and each inspection's original PNG, raw float32 NPY, heatmap PNG and overlay PNG under `inspections/<id>`. Heatmaps use a fixed 0–25 display scale and never replace or modify the saved numeric map. Connected regions are display evidence, not a separate scoring engine.

Historical inspection and review rows/evidence remain intact. Legacy fabric registrations must be revalidated under an explicitly identified frozen profile before new inference. The database retains compatibility with historical columns; old model artifacts are not loadable through the product path. Only the evidence directory is served through HTTP; the SQLite database is not a static download.

## Scope

This is a local research demonstration, bound to loopback. Multi-user authentication, PLC/camera integration, line-speed commissioning and independent acceptance validation are outside this release. Full-frame map assembly preserves the existing 32-pixel-overlap mean merge but has no separate industrial performance claim. No module imports research directories or deep-learning packages.
