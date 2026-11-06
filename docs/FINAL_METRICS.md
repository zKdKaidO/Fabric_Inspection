# Final frozen performance

The evaluated set has 5,656 patches: 687 defective and 4,969 normal, from 202 test parents and seven rolls. Ground-truth foreground is exactly mask value 255. Models and operating cutoffs were learned/calibrated from normal data; this final cleanup does not refit them. Repeated research use of the test cohort limits independence of model selection claims.

|Method|Pixel AP|AUPRO@0.30|Q1 Pixel AP|Pixel AUROC|Image AP|Image AUROC|
|---|---:|---:|---:|---:|---:|---:|
|Solution 1|0.339632|0.764635|0.169904|0.903287|0.648075|0.846547|
|C1|0.209819|0.697520|0.103554|0.871469|0.511171|0.770310|
|SingleNet|0.176641|0.725336|0.027514|0.882596|0.458312|0.843143|

Solution 1 uses original native image scores; pixel metrics use the preserved float16 evaluation-map convention. Documentation-only C1 and SingleNet comparison values use the archived common histogram evaluation and harmonized q0.999 image scores. The original published native C1 image AP was 0.511196 and SingleNet maximum-score image AP was 0.456267; harmonizing the SingleNet score gives 0.458312. These small protocol distinctions are not new experiments. C1/SingleNet code and artifacts are not active product dependencies.

Frozen Solution 1 operating point: **240/687 detected defects**, **447 misses**, **26/4,969 normal alarms**; recall **34.93%**, precision **90.23%**, normal FPR **0.5232%**. REVIEW and HOLD together form the flagged set for these benchmark counts. Thresholds remain numeric-identical to the original per-roll policy.

## What the metrics mean

- **Pixel AP:** precision–recall ranking quality for defect pixels across score levels; higher means a better concentration of real defect pixels near the top of the ranking.
- **AUPRO@0.30:** average defect-region coverage as the false-positive rate is increased, integrated only up to 30% and normalized. It weights defect regions rather than just their pixel counts.
- **Image AP:** precision–recall ranking quality for defective versus normal images.
- **AUROC:** how consistently a positive pixel/image ranks above a negative one across thresholds. High AUROC can coexist with low precision on an imbalanced dataset.
- **Recall:** the fraction of defective images flagged at the frozen operating cutoff.
- **Precision:** the fraction of flagged images that are labeled defective.
- **FPR:** the fraction of normal images that trigger an alarm.

**Accuracy is not the primary metric for this highly imbalanced defect-localization problem.** Predicting normal most of the time can appear accurate while missing many defects. Ranking/localization metrics and the actual alarm burden are more informative.

These are research-benchmark results, not certification of a production inspection line. The conservative operating point misses approximately two thirds of defective patches. Independent acquisition validation is unavailable.

Machine-readable sources: `tests/fixtures/frozen_metrics.json`, `docs/verification/baseline_comparison.json`. The cleaned implementation's reproduction is recorded in `docs/verification/post_cleanup_benchmark.json`.
