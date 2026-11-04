# Mongolia Dzud Research | NASA/JPL Fellowship, 2022

**Aster Volta · Research code portfolio**  
Satellite-derived summer environmental indicators, winter dzud research, and livestock mortality in Mongolia.

This is a **reconstructed, executable research portfolio** derived from my 2022 NASA/JPL fellowship and archived observations, supplemented by a separate 2026 geospatial validation project. It does not purport to be the exact original 2022 computational environment, a published study, or a validated dzud prediction model.

## The research question

Can remotely sensed vegetation, soil moisture, and evapotranspiration help characterize summer conditions that precede severe winter livestock losses in Mongolia? My JPL work explored the possibility of combining MODIS, SMAP, GLDAS, FLDAS and ECOSTRESS for dzud risk characterization. The notebooks here reproduce the parts for which the original observations and necessary spatial metadata could be recovered and independently checked.

## Start here: the figures tell the story

**[Visual research narrative: question → methods → figures → findings → interpretations → limitations](docs/RESULTS_AT_A_GLANCE.md)**

Read the visual overview first for the five main satellite and livestock findings. The notebooks, archived input data, source crosswalk, and tests remain available if you want to examine the computational details.

## Open a notebook

| Notebook | Actual research evidence | Result |
|---|---|---|
| [01 · MODIS summer NDVI](notebooks/01_MODIS_NDVI_Actual_2019_2020.ipynb) | Archived monthly MODIS/MOD13C2 2019 and 2020 rasters | Georeferenced monthly maps, provincial means, **2020 minus 2019** comparisons |
| [02 · SMAP soil moisture](notebooks/02_NASA_USDA_SMAP_2020_Actual_Maps.ipynb) | NASA–USDA soil-moisture anomaly rasters, March–August 2020 | Maps, valid-area diagnostics, provincial statistics |
| [03 · ECOSTRESS evapotranspiration](notebooks/03_ECOSTRESS_ET_Real_2019_2020.ipynb) | Original ECO3ETPTJPL.001 2019/2020 granule statistics and two sample scenes | Scene-level summaries and mapped scene coverage (no spurious across-location differences) |
| [04 · Satellite–livestock comparison](notebooks/04_Mongolia_Mortality_and_Multisensor_Comparison.ipynb) | Recomputed livestock rates; MODIS, SMAP, FLDAS indicators | 22-province table, exploratory correlations, leave-one-out and coverage checks |
| [05 · MODIS historical NDVI anomalies](notebooks/05_MODIS_NDVI_True_2002_2019_Anomalies.ipynb) | 54 independently archived 2002–2019 GEE NDVI rasters summarized into three historical reference rasters; 2020 source rasters | **2020 minus 2002–2019**, separate June/July/August anomaly maps and provincial statistics |
| [06 · FLDAS ET anomalies](notebooks/06_FLDAS_ET_True_2020_Anomalies.ipynb) | Original NASA FLDAS March–August 2020 *anomaly* GeoTIFFs | Correctly labeled anomalies and provincial estimates in mm/day equivalent |
| [Ruralidad 2026 · research audit](ruralidad/Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb) | Audited H1 baseline and independently archived validation evidence | Reproduced aggregate calculations; **not** the full 1985–2025 image-processing pipeline |

**The result is exploratory, not predictive.** For example, the Spearman association between province-level summer 2020 NDVI departures from the 2002–2019 reference and 2021 mortality is close to zero in this simple 22-province comparison. This does not establish or refute causal dzud processes; it demonstrates why climate mechanisms, geographic coverage, and statistical assumptions require careful interpretation.

## Run and reproduce

Python 3.11+ recommended. Data required by the seven notebooks is already packaged under `data/` and `ruralidad/data/`; there are **no simulated observations**. From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
python -m unittest discover -s tests -v
jupyter lab
```

Open `notebooks/` from JupyterLab. Execute top-to-bottom. The standalone Ruralidad audit should be opened with JupyterLab launched **inside** `ruralidad/` or at repository root with current working directory set to `ruralidad/` (see its README). The notebooks contain saved genuine outputs so they can also be viewed on GitHub without executing anything.

`run_all.py` recreates the maps, sample summaries, provincial joins, and exploratory tables in `results/`. It consumes **packaged** historical baseline rasters; reconstructing those three baseline rasters *from the original 54 yearly files* requires the separate archival source collection, described in [provenance](docs/SOURCE_PROVENANCE.md).

## What is and isn't reconstructed

Reproduced: **MODIS**, **SMAP**, **FLDAS**, **ECOSTRESS ET statistics/footprint examples**, and **national livestock mortality counts/rates**. Methods and observations are explicitly distinguished from historical slide conclusions. A GLDAS **2009–2010 cold-snap** figure and several ECOSTRESS LST/ESI demonstrations appear in the original presentations but are **not represented here as independently rerun analyses** because a complete corresponding scientific input/validation pipeline was not verified.

- [Figure-to-presentation crosswalk](docs/FIGURE_CROSSWALK.md)
- [Source provenance and reproducibility](docs/SOURCE_PROVENANCE.md)
- [Scientific scope and interpretation](docs/SCIENTIFIC_SCOPE.md)
- [Independent execution and test report](results/NOTEBOOK_EXECUTION_REPORT.json)

## Attribution

Original 2022 JPL fellowship work by **Aster Volta**, advised by Dr. Erika Podest, Dr. Kerry Cawse-Nicholson, and Dr. Kyle McDonald, with ECOSTRESS-team involvement. This personal scientific portfolio is not an official NASA/JPL publication or institutional endorsement. Source satellite products remain attributable to their providers. Ruralidad 2026 is separate collaborative research with Dr. Francisco de Aguinaga Padilla, with a book chapter in preparation, **not published/accepted**. Reference the linked scientific products and the original presentations for further background.
