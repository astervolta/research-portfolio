# Ruralidad Metropolitana, 2026: H1 validation evidence and audit notebook

**Aster Íñigo Volta with Dr. Francisco de Aguinaga Padilla · Project 2 of the [research portfolio](../README.md)**

This is a **separate 2026 geospatial research project** developed by Aster Íñigo Volta in collaboration with Dr. Francisco de Aguinaga Padilla. Its book chapter is **in preparation**. It has not been accepted or published. It is not part of the NASA/JPL Mongolia research documented in [`docs/MONGOLIA.md`](../docs/MONGOLIA.md).

Do not combine this research directly with Mongolia climate data: the projects investigate different places and questions.

## Research focus

The study examines 1985–2025 transitions in natural vegetation cover in two Mexican metropolitan areas: the Zona Metropolitana del Valle de México (ZMVM) and the Área Metropolitana de Guadalajara (AMG). The H1 analysis audited here estimates the net change in natural-vegetation area over that period from a stratified sample of 1,100 points per metropolitan area (2,200 in total).

## What is in this folder, and what is not

| Included here: the audit | Not included: the upstream pipeline |
|---|---|
| `Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb`, an inspectable audit of the archived H1 results | The complete multi-stage Landsat/MapBiomas/INEGI processing pipeline that produced those results |
| Two preserved research files in `data/`: the audited H1 baseline (run of 2026-09-21) and aggregated INEGI Serie I evidence for all 2,200 points | Satellite imagery, classification, Earth Engine processing and point-level sample interpretation |
| Recomputation of sample-count invariants, net-area arithmetic, unresolved-point bounds and 1985 source agreement | Any regeneration of the 1985–2025 change estimates from raw imagery |

The notebook is neither a dummy-data exercise nor a rerun of the complete original pipeline. In this portfolio it is an example of transparent quantitative auditing and scientific validation: it checks that the archived results are internally consistent and documents how well two independent historical sources agree for 1985.

## What the audit checks

1. **Design and arithmetic.** Each metropolitan area has exactly 1,100 sample points; net change equals gain minus loss to full precision; unresolved points are carried through as a worst-case bound.
2. **Historical cross-source evidence.** MapBiomas 1985 classes are compared with INEGI Serie I across all 2,200 points, without dropping observations. Hydrological classes are kept as not comparable. This describes **1985 source agreement only**. It does not validate the final 1985–2025 transitions.
3. **Area weighting.** Agreement is weighted by stratum area, because raw point percentages are not estimates of area shares.

## Audited H1 figures

Areas in hectares, 1985–2025, with 95% confidence intervals from the stratified area estimator.

| Metro | Sample points | Loss (95% CI) | Gain (95% CI) | Net change (95% CI) | Unresolved area | Net minus unresolved |
|---|---|---|---|---|---|---|
| ZMVM | 1,100 | 8,579 (4,749–12,409) | 58,643 (48,313–68,973) | **50,064 (38,846–61,281)** | 1,967 | 48,096 |
| AMG | 1,100 | 6,951 (4,160–9,743) | 25,246 (20,135–30,358) | **18,295 (12,294–24,296)** | 1,880 | 16,415 |

Point estimates, unresolved area and the worst-case column are recomputed by the audit notebook and saved in [`results/ruralidad_audited_real_h1_figures.csv`](results/ruralidad_audited_real_h1_figures.csv). The confidence intervals come from the archived H1 validation summary for the same run (2026-09-21); they are not recomputed here, because the per-point standard-error inputs are not part of this public repository.

**Interpretation.** These figures are areas of natural vegetation cover. They are not measures of ecological recovery, ecosystem condition, carbon mass or a climate-mitigation effect.

### Sensitivity to reclassified points

The estimated magnitude depends heavily on a subset of reclassified sample points. In the initial multi-source reference ensemble, many points could not be assigned a 1985–2025 transition and were left as unknown. These points were then classified using Landsat imagery from 1985–1989 and 2021–2025, which resolved most of them. In the final classification, fewer than 1% of each study area remains unresolved.

| Metro | Points reclassified (of 1,100) | Final gain / loss points that were reclassified | Share of net change contributed by reclassified points | Net change from ensemble labels alone |
|---|---|---|---|---|
| ZMVM | 374 | 115 of 165 / 34 of 50 | 76% | about 11,800 ha |
| AMG | 345 | 97 of 124 / 23 of 40 | 98% | about 400 ha |

The last column is not an alternative estimate, since it simply leaves the unknown points unassigned. It shows how strongly the reported magnitude, especially in AMG, rests on the Landsat-based classification of those points. The confidence intervals above reflect sampling uncertainty only; they do not capture uncertainty in how the reclassified points were labeled. These sensitivity figures were computed from the archived point-level H1 outputs, which contain sample coordinates and are not included in this repository.

Other outputs: [`results/ruralidad_real_1985_source_comparison.csv`](results/ruralidad_real_1985_source_comparison.csv) and the summary figure [`results/ruralidad_REAL_data_results.png`](results/ruralidad_REAL_data_results.png).

## How to run the audit

This workflow is separate from the Mongolia project: `run_all.py` and the `tests/` suite do not run or check it.

1. Install the dependencies once from the repository root: `pip install -r requirements.txt`. The audit itself uses only NumPy, pandas and Matplotlib.
2. Start JupyterLab with this `ruralidad/` folder as the working directory (the notebook also finds its data when started from the repository root).
3. Open `Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb` and run it top to bottom. It reads the two files in `data/` and writes its tables and figure to `results/`. Saved outputs are visible on GitHub without running anything.

## Attribution

Ruralidad Metropolitana is independent collaborative research by Aster Íñigo Volta and Dr. Francisco de Aguinaga Padilla, 2026. A book chapter is in preparation and has not been accepted or published. Source datasets (MapBiomas, INEGI) remain attributable to their providers.
