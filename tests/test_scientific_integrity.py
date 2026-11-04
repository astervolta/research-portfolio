"""Independent acceptance checks using archived non-synthetic data."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from src.pipeline import DATA, RESULTS, ensure_ndvi_grid, raster_files_ndvi, raster_files_smap, check_smap_common_zero_mask, mortality, provinces

class RealDataTests(unittest.TestCase):
    def test_six_ndvi_scenes_and_aligned_grid(self):
        self.assertTrue(ensure_ndvi_grid())
        self.assertEqual(len(raster_files_ndvi()),6)
    def test_smap_months_and_common_zero_export_mask(self):
        self.assertEqual(len(raster_files_smap()),6)
        self.assertGreater(check_smap_common_zero_mask(),500000)
    def test_livestock_rates_and_original_counts(self):
        t=mortality()
        self.assertEqual(len(t),22)
        o=t[t.original_aimag_name=='Orkhon'].iloc[0]
        self.assertAlmostEqual(o.deaths_2021_thousands,0.58,places=6)
        self.assertAlmostEqual(o.livestock_population_2020_thousands,136.988,places=6)
        self.assertAlmostEqual(o.mortality_percent_2021,100*0.58/136.988,places=8)
        self.assertAlmostEqual(t.deaths_2021_thousands.sum(),3012.35,places=5)
    def test_repaired_province_geometries(self):
        g=provinces()
        self.assertEqual(len(g),22)
        self.assertTrue(g.is_valid.all())
    def test_source_ecostress_scene_years(self):
        for year,count in [(2019,283),(2020,358)]:
            s=pd.read_csv(DATA/'ecostress_scene_stats'/f'ECOSTRESS_ET_{year}_scene_statistics.csv')
            self.assertEqual(len(s),count)
            self.assertTrue(pd.to_datetime(s.Date).dt.year.eq(year).all())
            self.assertTrue(s['Mean'].between(0,2000).all())
    def test_ecostress_scenes_not_same_place(self):
        ss=[]
        for year in [2019,2020]:
            with rasterio.open(DATA/'ecostress_scene_stats'/f'ECOSTRESS_ET_{year}_sample_scene.tif') as src:ss.append(src.bounds)
        a,b=ss
        self.assertTrue(a.left>b.right or b.left>a.right or a.bottom>b.top or b.bottom>a.top)
    def test_18_year_true_ndvi_baseline_and_fldas_metadata(self):
        manifest=pd.read_csv(DATA/'ndvi_gee_climatology/historical_54_file_SHA256_source_manifest.csv')
        self.assertEqual(len(manifest),54)
        self.assertNotIn(2020,manifest.year.values)
        for m in (3,4,5,6,7,8):
            with rasterio.open(DATA/'fldas_et_anomaly_2020'/f'FLDAS_ET_Anomaly_2020{m:02d}.tif') as x:
                self.assertIn('Anomaly of Total evapotranspiration',x.tags(1).get('long_name',''))
                self.assertEqual(x.tags(1).get('units'),'kg m-2 s-1')

    def test_computed_output_tables(self):
        n=pd.read_csv(RESULTS/'ndvi_provincial_monthly_2019_2020.csv')
        s=pd.read_csv(RESULTS/'smap_2020_provincial_monthly_means.csv')
        j=pd.read_csv(RESULTS/'joint_2020_satellite_indicators_vs_2021_mortality.csv')
        self.assertEqual(len(n),132)
        self.assertEqual(len(s),132)
        self.assertEqual(len(j),22)
        self.assertIn('ndvi_true_anomaly_jja_2020',j.columns)
        self.assertIn('fldas_et_anomaly_summer_mm_day',j.columns)
        self.assertTrue((j.mortality_percent_2021>=0).all())
        self.assertTrue(j.province_key.is_unique)
    def test_missing_coverage_sensitivity(self):
        c=pd.read_csv(RESULTS/'coverage_sensitivity_exploratory_correlations.csv')
        self.assertEqual(set(c.smap_min_valid_fraction_threshold),{0,.75,.90})
        self.assertEqual(len(c),21)
        self.assertEqual(c[c.smap_min_valid_fraction_threshold==.75].n_provinces.unique().tolist(),[19])

if __name__=='__main__': unittest.main()
