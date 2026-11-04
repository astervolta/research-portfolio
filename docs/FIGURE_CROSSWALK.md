# Figure-to-JPL-presentation crosswalk

This inventory distinguishes **reconstructed numerical results** from original slides only documenting work attempted, proposed, or visualized in 2022.

Original presentation sources:

- [JPL end-of-internship presentation, Aug 25 2022](https://docs.google.com/presentation/d/19wAsaKdcFd3E0QNRk4AYJDTarnEOLpjN/edit)
- [ECOSTRESS lightning talk, Apr 14 2022](https://docs.google.com/presentation/d/1LE4C7oxO9BnXLuX4W2WOp4urGNouWlea/edit)
- [ECOSTRESS progress presentation, Aug 1 2022](https://docs.google.com/presentation/d/18_2f_hyC_zAakHXXHYiNQR-6Uojo_1xV/edit)
- [Updated ECOSTRESS SMAP/FLDAS figures, Aug 12 2022](https://docs.google.com/presentation/d/1JEXDlDj0u49TERQ5NgxwmWHo2C1iQ0sJ/edit)

| Original topic and figures | Current recreated evidence | Notes |
|---|---|---|
| Aug 25: summer 2020 MODIS NDVI monthly observations and anomalies (slides ~9–10) | Notebooks **01** and **05**; `results/01_`, `02_`, `07_` images and 3 real NDVI anomaly TIFFs | Notebook 05 uses true independently reconstructed monthly **2002–2019** reference; do not confuse with simple 2019-vs-2020 comparison in 01 |
| Aug 25: March–August 2020 SMAP soil-moisture anomaly maps (slides ~11–16) | Notebook **02**; `results/03_smap_2020_march_august.png` | Real data, missing mask and valid provincial fraction analyzed |
| Aug 25: March–August 2020 FLDAS anomaly maps (slides ~17–22) | Notebook **06**; `results/08_fldas_et_anomalies_mar_aug_2020.png` | Source band verifies anomaly relative to 1982–2016 reference; now correctly mapped and unit-converted |
| Aug 25: 2021 livestock losses and summer risk indicator investigation | Notebook **04**; reconstructed 22-province mortality and exploratory statistics | National totals checked; no unsupported province-level prediction claims |
| Apr 14: 2009–2010 GLDAS temperature contrasts and cold-snap plots | Historical presentation **only** | Not independently reconstructed from the required aligned original GLDAS archive, therefore not claimed validated by these notebooks |
| Apr 14: proposed ECOSTRESS ET/LST/ESI, SMAP FT, MODIS NDVI and GPM IMERG multisensor strategy | Notebook **03** for real ECOSTRESS ET statistics and scene footprints; other notebook evidence above | Lightning talk distinguishes preliminary examples from **planned** product analyses; no unsupported LST/ESI model claims |
| Aug 1: Jun 14 2020 / Feb 28 2021 ECOSTRESS and MODIS LST/cloud mask views | Historical presentation **only** | Requires exact cloud and emissivity masks and scene co-location for an independent scientific rerun |

The original slides remain preserved in the academic Drive and are **not** substituted for executable data analysis. Outputs in the current repository were independently reconstructed using the listed original inputs.
