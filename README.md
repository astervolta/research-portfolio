# Aster Íñigo Volta · Research Portfolio

Geoscience and Earth-observation research: code, archived data, notebooks and documented findings.

This repository holds **two independent research projects**. They have different study areas, data, methods, collaborators and timelines, and are not one combined analysis. They share this repository only so the work can be inspected in one place.

| | [Mongolia Dzud](#1-mongolia-dzud--nasajpl-fellowship-2022) | [Ruralidad Metropolitana](#2-ruralidad-metropolitana-2026) |
|---|---|---|
| **Period** | Original research 2022; computational reconstruction 2026 | 2026, ongoing |
| **Context** | NASA/JPL fellowship | Independent collaborative research with Dr. Francisco de Aguinaga Padilla |
| **Study area** | Mongolia (22 provincial reporting units) | Mexico City (ZMVM) and Guadalajara (AMG) metropolitan areas |
| **Question** | Do summer satellite indicators relate to dzud livestock losses? | How did natural vegetation cover change from 1985 to 2025? |
| **Data** | MODIS, SMAP, FLDAS, ECOSTRESS; livestock statistics | Audited H1 outputs; MapBiomas and INEGI Serie I historical evidence |
| **In this repo** | Six notebooks, packaged data, `run_all.py` pipeline, nine integrity tests | One audit notebook and its two input files |
| **Documentation** | [`docs/MONGOLIA.md`](docs/MONGOLIA.md) | [`ruralidad/README.md`](ruralidad/README.md) |

---

## 1. Mongolia Dzud · NASA/JPL Fellowship, 2022

Dzud is a severe winter that can prevent livestock from reaching pasture. This project asks whether the *preceding summer's* vegetation, soil moisture and evapotranspiration, observed from satellites, help characterize vulnerability, and how those indicators relate to reported 2021 livestock mortality across Mongolia's 22 provincial reporting units.

**Main finding.** Summer 2020 vegetation and water conditions were geographically heterogeneous rather than a single national drought. The province-level association between June–August 2020 NDVI anomalies (relative to 2002–2019) and 2021 livestock mortality was essentially zero (Spearman ρ ≈ 0.0006, 22 units). This is an exploratory, single-year comparison: it neither establishes nor rules out causal dzud mechanisms, and it is not a forecasting model.

- **Visual summary of findings:** [Results at a glance](docs/RESULTS_AT_A_GLANCE.md) (question → methods → figures → findings → limitations)
- **Full project documentation:** [docs/MONGOLIA.md](docs/MONGOLIA.md) (notebooks, figures, reproduction, scope)
- **Notebooks:** [`notebooks/`](notebooks/) (six notebooks, 01–06, with saved outputs viewable on GitHub)
- **Methods and data provenance:** [Source provenance](docs/SOURCE_PROVENANCE.md)
- **Interpretation and limitations:** [Scientific scope](docs/SCIENTIFIC_SCOPE.md)
- **What was and was not reconstructed from the 2022 presentations:** [Figure crosswalk](docs/FIGURE_CROSSWALK.md)

---

## 2. Ruralidad Metropolitana, 2026

A separate study of natural-vegetation transitions between 1985 and 2025 in the Mexico City (ZMVM) and Guadalajara (AMG) metropolitan areas, carried out with Dr. Francisco de Aguinaga Padilla. A book chapter is **in preparation; it has not been accepted or published**.

**What this repository contains.** One audit notebook that independently rechecks the archived H1 results: sample-count invariants, full-precision net-area arithmetic, and agreement between MapBiomas and INEGI Serie I for 1985 across all 2,200 sampling points. It reproduces the audit, not the study's complete upstream image-processing pipeline, which is not included in this public repository.

**Audited H1 net change in natural-vegetation area, 1985–2025:** about 50,064 ha (ZMVM) and 18,295 ha (AMG). These are areas of natural vegetation cover. They are not measures of ecological recovery, ecosystem condition or carbon.

- **Project page:** [ruralidad/README.md](ruralidad/README.md) (scope, audit vs. full pipeline, how to run)
- **Audit notebook:** [Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb](ruralidad/Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb)
- **Audited figures:** [`ruralidad/results/`](ruralidad/results/)

---

## Repository layout

```
README.md                  This page
requirements.txt           Python dependencies (covers both projects)

Mongolia Dzud (NASA/JPL, 2022)
├── docs/                  MONGOLIA.md, results summary, provenance, scope, crosswalk
├── notebooks/             Notebooks 01–06
├── data/                  Archived satellite, livestock and boundary inputs
├── src/                   Analysis pipeline
├── results/               Figures, tables and anomaly rasters produced by run_all.py
├── tests/                 Nine scientific-integrity tests
└── run_all.py             Rebuilds everything in results/

Ruralidad Metropolitana (2026)
└── ruralidad/
    ├── README.md          Project page
    ├── Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb
    ├── data/              Audited H1 baseline and aggregated 1985 evidence
    └── results/           Audit tables and figure

RELEASE_FILE_MANIFEST_SHA256.csv   SHA-256 checksums for every released file
```

## Running the code

Install once (Python 3.11+ recommended):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

The two projects then run separately:

- **Mongolia:** `python run_all.py` rebuilds `results/`, and `python -m unittest discover -s tests -v` runs the nine integrity tests. Details in [docs/MONGOLIA.md](docs/MONGOLIA.md#run-and-reproduce).
- **Ruralidad:** open `ruralidad/Ruralidad_H1_REAL_RESEARCH_AUDIT.ipynb` in JupyterLab and run it top to bottom. It writes to `ruralidad/results/`. It is not part of `run_all.py` or the test suite. Details in [ruralidad/README.md](ruralidad/README.md#how-to-run-the-audit).

## Attribution

- **Original research, 2022 (Mongolia):** NASA/JPL fellowship research by Aster Volta, advised by Dr. Erika Podest, Dr. Kerry Cawse-Nicholson and Dr. Kyle McDonald, with ECOSTRESS-team involvement.
- **Computational reconstruction, 2026 (Mongolia):** the recoverable 2022 analyses were re-implemented, checked against archived inputs and documented by Aster Volta.
- **Independent collaborative research, 2026 (Ruralidad):** Aster Volta with Dr. Francisco de Aguinaga Padilla. Not part of the NASA/JPL work.

This is a personal research portfolio. It is not an official NASA or JPL publication, and nothing here is a peer-reviewed paper. Satellite and statistical source products remain attributable to their original providers.

Academic website: <https://aster-volta-academic.web.app>
