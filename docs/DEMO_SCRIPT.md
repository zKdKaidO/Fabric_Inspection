# Demonstration script

1. From PowerShell run `cd A:\RAW_FABRID\fabric_inspection`, then `.\scripts\start_product.ps1`. Open `http://127.0.0.1:5173`; API documentation is at port 8000 `/docs`.
2. In **Fabric Management**, create a fabric ID/name and explicitly select **Rollo1A**. Explain that the file contains seven frozen roll-specific profiles, not one universal PCA model.
3. In **Commissioning**, choose that fabric. Select four normal demo references or upload verified normal full source frames. Select **Validate and activate frozen profile**. Explain that this checks existing scores against the existing review cutoff; it does not train or change thresholds.
4. In **Inspect**, choose the now-ready fabric. Select a demo test patch, which automatically supplies its authoritative parent context, or upload a full parent frame. Run inspection.
5. Show original, anomaly heatmap and overlay. Explain the scalar model score separately from PASS/REVIEW/HOLD. Never call an automatic flag a confirmed defect.
6. Open **History**, reopen the saved evidence, and, for a flagged image, record a human review. Refresh and show that history and review persist.
7. Show `FINAL_METRICS.md`: Pixel AP 0.339632, AUPRO 0.764635, Image AP 0.648075; at the fixed policy recall 34.93%, precision 90.23%, 26 normal alarms. Acknowledge the 447 misses and lack of independent production validation.
8. Show `FINAL_CHECKLIST.md` and the golden/full benchmark verification. Do not run a tuning experiment during the demo.

If normal validation fails, do not force activation or lower a threshold. Verify fabric identity, sample condition and selected frozen profile. New-fabric fitting is unsupported. The startup script prints process IDs; use those specific IDs to stop the local services when finished.
