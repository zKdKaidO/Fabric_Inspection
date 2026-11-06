# Teacher questions and answers

**Is this supervised defect classification?** No. The normal-reference models were fitted from normal samples. Labeled defects and masks measure performance; they do not enter inference.

**Why seven profiles?** Different rolls have different normal texture statistics. The same algorithm uses one of seven frozen PCA/normal-reference states, chosen explicitly by the operator.

**Why Gabor?** Its oriented spatial-frequency responses match the periodic and directional nature of woven fabric. Quadrature magnitude reduces sensitivity to phase.

**Why energy and dispersion?** Energy measures strength of a local filter response; dispersion measures how variable it is within the neighborhood.

**Why the center-surround feature?** It adds robust local luminance contrast to the texture descriptor. It is one fixed 15×15-versus-surrounding-25×25 feature, not a learned defect template.

**Why PCA and whitening?** PCA represents correlated normal variation; eigenvalue scaling expresses deviation relative to normal variability. Retained ranks are 19 for six profiles and 18 for Rollo7A. They are never chosen per inspection.

**What happens at a crop edge?** The engine reads actual pixels from the parent image. It reflects each stage's input only at a physical frame boundary, preserving the validated context handling.

**What does q0.999 do?** It selects an extreme order statistic; on a 256×256 map it lies between the 66th and 67th largest values. It is not a tail mean, and it can omit isolated peaks.

**Does commissioning train anything?** No. It verifies at least four normal samples against an explicitly selected frozen profile and activates it only if all remain below the unchanged review cutoff. Unseen-fabric fitting is not supported.

**Does PASS mean no defects?** No. The frozen benchmark recall is only 34.93%. This is an evidence/review aid, not a guarantee. HOLD also needs human confirmation.

**Why not accuracy?** Normal examples dominate. High accuracy can hide large numbers of missed defects; AP, region overlap and actual recall/FPR are more useful.

**How does it compare with deep learning?** The archived SingleNet baseline is documented with comparable q0.999 scores. Solution 1 has higher AP on this benchmark; hardware, model selection and test reuse limit broad superiority claims. The final product contains no deep-learning engine.

**Is it production-ready?** No. Independent acquisitions, new fabrics, sensor/illumination variation and actual line throughput have not been validated.

**What changed in finalization?** Software boundaries, one-engine routing, documentation and operator workflow. The frozen artifact bytes, bank, PCA ranks, numerical policy and scientific benchmark were not refitted or optimized.
