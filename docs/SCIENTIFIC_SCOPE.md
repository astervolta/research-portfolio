# Scientific interpretation

> Part of the **Mongolia Dzud (NASA/JPL, 2022)** project. Project overview: [MONGOLIA.md](MONGOLIA.md) · Portfolio home: [README](../README.md) · The closing Ruralidad note refers to the separate project documented in [ruralidad/README.md](../ruralidad/README.md).

The objective is transparent exploratory analysis of original NASA/JPL Mongolia observations, not a finished or independently externally validated dzud prediction model.

**Temporal scale:** satellite anomalies from March–August 2020 are compared with *annual* 2021 livestock mortality. This is an exploratory temporal association; mortality can reflect other weather extremes, disease, livestock management, exposure and socioeconomic factors.

**Spatial scale:** the mapping unit is Mongolia's 22 historical reporting areas and a set of archived provincial polygons. These are not independent replicates of the climate system. Simple Spearman coefficients should not be used as causal or predictive evidence, particularly with small sample sizes, correlated variables, possible spatial dependence, and unquantified selection effects.

**Vegetation:** a 2019-versus-2020 NDVI difference is **not a climate anomaly**. Notebook 05 uses separate June, July, August 2002–2019 NDVI reference rasters and the 2020 images from the same GEE NDVI source. At province resolution, the 2020 summer anomaly/mortality Spearman coefficient is near zero. Both positive and negative regional NDVI anomalies occur. The original slideshow's broad conclusion should not be taken as an established causal finding.

**Water stress:** NASA–USDA SMAP `ssma` is dimensionless, and exported zero-filled cells were excluded as missing. Valid pixel fractions differ by location; results are tested under ≥75% and ≥90% coverage filters. FLDAS `Evap_tavg` in this particular archive is an *anomaly* product, not raw ET flux; pixel metadata has been validated and correct 1982–2016 climatology reference identified. Negative anomalies are valid, not nodata.

**ECOSTRESS:** 641 archived 2019/2020 ETdaily granule statistics were inspected. Their geographic footprints, time distribution and valid-pixel counts are not fixed across years. Two preserved sample scenes do not geographically overlap; comparing their means as environmental change would be scientifically invalid. The notebook plots scene-level distributions, not regional time series or change detection. Original ECOSTRESS LST/ESI analyses cannot be independently confirmed from those ET tables alone.

**Historical work:** the original presentations are primary evidence that the researcher performed and presented related preliminary work; the reconstructed notebooks preserve original project lineage but contain independently checked revisions. All reproduced figures and claims are tied to the actual input files.

**Ruralidad:** included separately as an audit of real stratified geospatial results from research in preparation, not as a claim that a full map-processing pipeline can be rerun from the summarized audit file. This project has a different study area, methodology and authorship.
