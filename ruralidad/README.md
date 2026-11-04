# Ruralidad Metropolitana, 2026: H1 validation evidence and audit notebook

**Aster Volta with Dr. Francisco de Aguinaga Padilla · Project 2 of the [research portfolio](../README.md)**

This is a **separate 2026 geospatial research project** developed by Aster Volta in collaboration with Dr. Francisco de Aguinaga Padilla. Its book chapter is **in preparation**. It has not been accepted or published. It is not part of the NASA/JPL Mongolia research documented in [`docs/MONGOLIA.md`](../docs/MONGOLIA.md).

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

From [`results/ruralidad_audited_real_h1_figures.csv`](results/ruralidad_audited_real_h1_figures.csv). Areas in hectares, 1985–2025.

| Metro | Sample points | Loss | Gain | Net change | Unresolved area | Net minus unresolved |
|---|---|---|---|---|---|---|
| ZMVM | 1,100 | 8,579 | 58,643 | 50,064 | 1,967 | 48,096 |
| AMG | 1,100 | 6,951 | 25,246 | 18,295 | 1,880 | 16,415 |

**Interpretation.** These figures are areas of natural vegetation cover. They are not measures of ecological recovery, ecosystem condition, carbon mass or a climate-mitigation effect.

Other outputs: [`results/ruralidad_real_1985_source_comparison.csv`](results/ruralidad_real_1985_source_comparison.csv) and the summary figure [`results/ruralidad_REAL_data_results.png`](results/ruralidad_REAL_data_results.png).

## How to run the audit

This workflow is separate from the Mongolia project: `run_all.py` and the `tests/` suite do not run or check it.

1. Install the dependencies once from the repository root: `pip install -r requirements.txt`. The audit itself uses only NumPy, pandas and Matplotlib.
2. Start JupyterLab with this `ruralidad/` folder as the working directory (the notebook also finds its data when started from the repository root).
3. Open `Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb` and run it top to bottom. It reads the two files in `data/` and writes its tables and figure to `results/`. Saved outputs are visible on GitHub without running anything.

## Attribution

Ruralidad Metropolitana is independent collaborative research by Aster Volta and Dr. Francisco de Aguinaga Padilla, 2026. A book chapter is in preparation and has not been accepted or published. Source datasets (MapBiomas, INEGI) remain attributable to their providers.
