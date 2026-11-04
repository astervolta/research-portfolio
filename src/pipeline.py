"""Real-data reconstruction of Aster Volta's historical NASA/JPL Mongolia analyses.
All input paths are repository relative. No simulated observations or external tokens.
"""
from __future__ import annotations
import math
from pathlib import Path
import unicodedata
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask as raster_mask
from rasterio.enums import Resampling
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
RESULTS=ROOT/'results'
RESULTS.mkdir(parents=True,exist_ok=True)
MONTHS=['June','July','August']
MONTHS_SMAP=['March','April','May','June','July','August']

# Only historical spelling aliases in the user's archived workbook/geojson.
ALIASES={'Central':'Tuv','East':'Dornod','South Gobi':'Umnugovi',
'Gobi-Altai':'GoviAltai','Bayan-Ölgii':'Bayan-Ulgii','Ömnögovi':'Umnugovi',
'Övörkhangai':'Uvurkhangai','Töv':'Tuv','Khövsgöl':'Khuvsgul','Hovd':'Khovd',
'Uvs':'uvs'}
def key(x):
    x=ALIASES.get(str(x).strip(),str(x).strip())
    return ''.join(c for c in unicodedata.normalize('NFKD',x.lower()) if not unicodedata.combining(c) and c.isalnum())

def provinces():
    g=gpd.read_file(DATA/'mongolia_provinces/mongolia.prefectures.geojson')
    # Some original GeoJSON polygons are self-intersecting. Repair geometry, not attributes.
    n_invalid=int((~g.is_valid).sum())
    g.geometry=g.geometry.make_valid()
    g=g.loc[~g.prefecture.isin(['Bagakhangai','Baganuur'])].copy()
    g['province_key']=g.prefecture.map(key)
    assert len(g)==22 and g.province_key.is_unique and g.is_valid.all()
    g.attrs['original_invalid_count']=n_invalid
    return g

def mortality():
    t=pd.read_csv(DATA/'mongolia_provinces/livestock_2021_rates_recomputed.csv')
    t['province_key']=t.original_aimag_name.map(key)
    assert len(t)==22 and t.province_key.is_unique and t.mortality_fraction_2021.between(0,1).all()
    assert abs(t.deaths_2021_thousands.sum()-3012.35)<1e-5
    assert abs(t.livestock_population_2020_thousands.sum()-67068.486)<1e-5
    return t

def _prov_valid_values(src, geom, *, drop_zero=False, valid_bounds=None):
    """Crop raster to one valid province, mask outside, weight latitude for geographic grid."""
    crop, transform=raster_mask(src,[geom],crop=True,filled=False,all_touched=False)
    a=crop[0]
    vals=np.asarray(a.data,dtype=np.float64)
    good=~np.ma.getmaskarray(a)&np.isfinite(vals)
    if drop_zero:good &= vals!=0
    if valid_bounds is not None:good &= (vals>=valid_bounds[0])&(vals<=valid_bounds[1])
    yy=transform.f+(np.arange(vals.shape[0])+0.5)*transform.e
    weights=np.cos(np.deg2rad(yy))
    valid_n=int(good.sum())
    total_n=int((~np.ma.getmaskarray(a)).sum())
    if valid_n==0:return dict(mean=np.nan,n_valid=0,n_masked=total_n,valid_fraction=0.0)
    return dict(mean=float(np.average(vals[good],weights=np.broadcast_to(weights[:,None],vals.shape)[good])),
                n_valid=valid_n,n_masked=total_n,valid_fraction=float(valid_n/max(1,total_n)))

def raster_files_ndvi():
    result={}
    for year in (2019,2020):
        for m in (6,7,8):
            candidates=list((DATA/'ndvi_2019_2020').glob(f'*NDVI.{year}{m:02d}*.tif'))
            assert len(candidates)==1,(year,m,candidates)
            result[year,m]=candidates[0]
    return result

def raster_files_smap():
    return {month:DATA/'smap_2020'/f'geemap_average_SMAP_SSMA_{month.lower()}2020.tif' for month in MONTHS_SMAP}

def ensure_ndvi_grid():
    files=raster_files_ndvi()
    ref=None
    for path in files.values():
        with rasterio.open(path) as s:
            assert s.crs.to_epsg()==4326
            if ref is None:ref=(s.shape,s.transform)
            assert (s.shape,s.transform)==ref
            sample=s.read(1,masked=True)
            v=sample.compressed()
            # Giovanni exports already contain scaled NDVI, not raw MODIS int16.
            assert np.nanquantile(v,0.99)<=1.0 and np.nanquantile(v,.01)>=-.2
    return True

def compute_ndvi():
    ensure_ndvi_grid()
    g=provinces();files=raster_files_ndvi();records=[]
    for (year,month),path in sorted(files.items()):
        with rasterio.open(path) as src:
            for _,region in g.iterrows():
                stat=_prov_valid_values(src,region.geometry,valid_bounds=(-.2,1.0))
                records.append({'province_key':region.province_key,'province':region.prefecture,
                                'year':year,'month':month,'ndvi_mean':stat['mean'],
                                'valid_cells':stat['n_valid'],'valid_fraction':stat['valid_fraction']})
    tab=pd.DataFrame(records)
    assert len(tab)==22*6 and tab.ndvi_mean.notna().all()
    tab.to_csv(RESULTS/'ndvi_provincial_monthly_2019_2020.csv',index=False)
    seasons=tab.groupby(['province_key','province','year'],as_index=False).agg(ndvi_jja_mean=('ndvi_mean','mean'),min_valid_fraction=('valid_fraction','min'))
    a=seasons.pivot(index=['province_key','province'],columns='year',values='ndvi_jja_mean').reset_index()
    a.columns=['province_key','province','ndvi_2019_JJA','ndvi_2020_JJA']
    a['ndvi_difference_2020_minus_2019']=a.ndvi_2020_JJA-a.ndvi_2019_JJA
    assert len(a)==22
    a.to_csv(RESULTS/'ndvi_summer_comparison_by_province.csv',index=False)
    plot_ndvi(files,g)
    return tab,a

def plot_ndvi(files,g):
    fig,axes=plt.subplots(2,3,figsize=(14.5,7.7),constrained_layout=True)
    for j,year in enumerate((2019,2020)):
        for k,month in enumerate((6,7,8)):
            ax=axes[j,k]
            with rasterio.open(files[year,month]) as s:
                a=s.read(1,masked=True)
                arr=np.ma.masked_where((a<-.2)|(a>1),a)
                ax.imshow(arr,extent=(s.bounds.left,s.bounds.right,s.bounds.bottom,s.bounds.top),origin='upper',vmin=0,vmax=.75,cmap='YlGn')
            g.boundary.plot(ax=ax,color='black',linewidth=.25)
            ax.set(title=f'{year} {MONTHS[k]}  •  MODIS NDVI',xlabel='Longitude',ylabel='Latitude')
    fig.suptitle('Historical NASA/JPL study area: observed summer NDVI, 2019 and 2020',fontsize=14)
    fig.colorbar(axes[-1,-1].images[-1],ax=axes.ravel().tolist(),shrink=.67,label='NDVI, unitless (already scaled in Giovanni source)')
    fig.savefig(RESULTS/'01_ndvi_2019_2020_actual_observations.png',dpi=125)
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14.5,4.5),constrained_layout=True)
    for k,month in enumerate((6,7,8)):
        with rasterio.open(files[2020,month]) as s20,rasterio.open(files[2019,month]) as s19:
            x=s20.read(1,masked=True);y=s19.read(1,masked=True)
            a=np.ma.masked_where((x<-.2)|(x>1)|(y<-.2)|(y>1),x-y)
            axes[k].imshow(a,extent=(s20.bounds.left,s20.bounds.right,s20.bounds.bottom,s20.bounds.top),origin='upper',vmin=-.4,vmax=.4,cmap='RdBu')
        g.boundary.plot(ax=axes[k],color='black',linewidth=.25)
        axes[k].set(title=f'{MONTHS[k]}: 2020 − 2019',xlabel='Longitude',ylabel='Latitude')
    fig.suptitle('Actual year-over-year NDVI differences (NOT climatological anomalies)',fontsize=13)
    fig.colorbar(axes[-1].images[-1],ax=axes.ravel().tolist(),shrink=.7,label='NDVI difference, unitless; red = decline')
    fig.savefig(RESULTS/'02_ndvi_year_over_year_difference.png',dpi=125)
    plt.close(fig)

def check_smap_common_zero_mask():
    files=raster_files_smap();base=None;count=None
    for p in files.values():
        with rasterio.open(p) as src:
            assert src.crs.to_epsg()==4326
            a=src.read(1)
            if base is None:base=(a==0);count=base.sum()
            # All 6 exports contain the same exact zeros, typical pre-filled no-data.
            else:assert np.array_equal(base,a==0),'SMAP zero pattern changed; revisit missing-value handling.'
    assert count>0
    return int(count)

def compute_smap():
    common_zeros=check_smap_common_zero_mask()
    g=provinces();files=raster_files_smap();rows=[]
    for mon,path in files.items():
        with rasterio.open(path) as src:
            for _,region in g.iterrows():
                stat=_prov_valid_values(src,region.geometry,drop_zero=True)
                rows.append({'province_key':region.province_key,'province':region.prefecture,'month':mon,
                             'ssma_mean':stat['mean'],'valid_cells':stat['n_valid'],
                             'valid_fraction':stat['valid_fraction']})
    df=pd.DataFrame(rows)
    assert len(df)==22*6 and df.ssma_mean.notna().all()
    df.to_csv(RESULTS/'smap_2020_provincial_monthly_means.csv',index=False)
    plot_smap(files,g)
    return df,common_zeros

def plot_smap(files,g):
    fig,axes=plt.subplots(2,3,figsize=(15,8.3),constrained_layout=True)
    for ax,month in zip(axes.flat,MONTHS_SMAP):
        with rasterio.open(files[month]) as src:
            a=src.read(1,out_shape=(320,960),resampling=Resampling.nearest)
            a=np.ma.masked_where((a==0)|~np.isfinite(a),a)
            ax.imshow(a,extent=(src.bounds.left,src.bounds.right,src.bounds.bottom,src.bounds.top),origin='upper',vmin=-2,vmax=2,cmap='RdBu')
        g.boundary.plot(ax=ax,color='black',linewidth=.25)
        ax.set(title=f'2020 {month} • NASA-USDA SMAP ssma',xlabel='Longitude',ylabel='Latitude')
    fig.suptitle('2020 NASA–USDA SMAP-enhanced soil-moisture anomaly • common zero export mask excluded',fontsize=13)
    fig.colorbar(axes[-1,-1].images[-1],ax=axes.ravel().tolist(),shrink=.65,label='ssma, dimensionless; red = drier than baseline')
    fig.savefig(RESULTS/'03_smap_2020_march_august.png',dpi=125)
    plt.close(fig)

def compute_ecostress():
    series=[];charts=[]
    for year in (2019,2020):
        path=DATA/'ecostress_scene_stats'/f'ECOSTRESS_ET_{year}_scene_statistics.csv'
        a=pd.read_csv(path)
        a['timestamp']=pd.to_datetime(a.Date,utc=True,errors='raise')
        a=a.loc[a.timestamp.dt.year==year].copy()
        assert len(a)>150 and a['Mean'].between(0,2000).all() and a.Count.gt(0).all()
        a['year']=year;a['month']=a.timestamp.dt.month
        assert a.month.isin([6,7,8]).all()
        series.append(a[['year','month','timestamp','Count','Mean','Median','Standard Deviation','File Name']].rename(columns={'Count':'scene_valid_pixel_count','Mean':'scene_etdaily_mean_W_m2','Median':'scene_etdaily_median_W_m2','Standard Deviation':'scene_etdaily_sd_W_m2','File Name':'scene_source_name'}))
    out=pd.concat(series,ignore_index=True)
    out.to_csv(RESULTS/'ecostress_2019_2020_scene_statistics_checked.csv',index=False)
    summary=out.groupby(['year','month'],as_index=False).agg(n_scenes=('scene_etdaily_mean_W_m2','size'),median_of_scene_means_W_m2=('scene_etdaily_mean_W_m2','median'),sum_scene_valid_pixels=('scene_valid_pixel_count','sum'))
    summary.to_csv(RESULTS/'ecostress_scene_sampling_summary.csv',index=False)
    # Two illustrative original granules have different locations; compare footprints only.
    raster_info=[]
    for year in (2019,2020):
        p=DATA/'ecostress_scene_stats'/f'ECOSTRESS_ET_{year}_sample_scene.tif'
        with rasterio.open(p) as s:
            assert s.crs.to_epsg()==4326
            raster_info.append({'year':year,'source_filename':p.name,'left':s.bounds.left,'right':s.bounds.right,'bottom':s.bounds.bottom,'top':s.bounds.top,'rows':s.height,'columns':s.width,'unit':'W/m²'})
    overlap_x=max(raster_info[0]['left'],raster_info[1]['left'])<min(raster_info[0]['right'],raster_info[1]['right'])
    overlap_y=max(raster_info[0]['bottom'],raster_info[1]['bottom'])<min(raster_info[0]['top'],raster_info[1]['top'])
    assert not (overlap_x and overlap_y),'Scene footprints overlap; re-evaluate simple comparison.'
    pd.DataFrame(raster_info).to_csv(RESULTS/'ecostress_2019_2020_sample_scene_footprints.csv',index=False)
    fig,axes=plt.subplots(1,2,figsize=(12,4.7),constrained_layout=True)
    for ax,year in zip(axes,(2019,2020)):
        df=out[out.year==year]
        ax.boxplot([df[df.month==m].scene_etdaily_mean_W_m2.to_numpy() for m in (6,7,8)],tick_labels=['June','July','August'],showfliers=False)
        ax.set_title(f'{year} archived scene means (n={len(df)})')
        ax.set_ylabel('ECOSTRESS ETdaily latent heat flux (W/m²)')
    fig.suptitle('Observational scene distributions; NOT matched geographic sampling',fontsize=12)
    fig.savefig(RESULTS/'04_ecostress_scene_sample_distribution.png',dpi=130)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,6),constrained_layout=True)
    g=provinces();g.boundary.plot(ax=ax,linewidth=.45,color='gray')
    for k,info in enumerate(raster_info):
        from matplotlib.patches import Rectangle
        ax.add_patch(Rectangle((info['left'],info['bottom']),info['right']-info['left'],info['top']-info['bottom'],edgecolor=['blue','red'][k],facecolor='none',linewidth=2,label=f"{info['year']} illustrative granule footprint"))
    ax.legend(loc='upper left',fontsize=9);ax.set(xlabel='Longitude',ylabel='Latitude',title='Different ECOSTRESS scene footprints: subtraction would be invalid')
    fig.savefig(RESULTS/'05_ecostress_footprints_do_not_overlap.png',dpi=130)
    plt.close(fig)
    return out,summary,raster_info

def compute_joint_indicators():
    npath=RESULTS/'ndvi_summer_comparison_by_province.csv';spath=RESULTS/'smap_2020_provincial_monthly_means.csv'
    if not npath.exists():compute_ndvi()
    if not spath.exists():compute_smap()
    nd=pd.read_csv(npath)
    sm=pd.read_csv(spath)
    if not (RESULTS/'ndvi_2020_true_historical_anomaly_jja_by_province.csv').exists():
        from .climatology import compute_gee_2020_anomalies
        compute_gee_2020_anomalies()
    nd_hist=pd.read_csv(RESULTS/'ndvi_2020_true_historical_anomaly_jja_by_province.csv')
    if not (RESULTS/'fldas_et_anomaly_2020_provincial_monthly.csv').exists():
        from .fldas import calculate_fldas
        calculate_fldas()
    et=pd.read_csv(RESULTS/'fldas_et_anomaly_2020_provincial_monthly.csv')
    smspring=sm[sm.month.isin(['March','April','May'])].groupby('province_key',as_index=False).agg(smap_ssma_spring_mean=('ssma_mean','mean'),smap_spring_min_valid_fraction=('valid_fraction','min'))
    smsummer=sm[sm.month.isin(['June','July','August'])].groupby('province_key',as_index=False).agg(smap_ssma_summer_mean=('ssma_mean','mean'),smap_summer_min_valid_fraction=('valid_fraction','min'))
    etspring=et[et.month.isin(['March','April','May'])].groupby('province_key',as_index=False).agg(fldas_et_anomaly_spring_mm_day=('et_anomaly_mm_per_day','mean'))
    etsummer=et[et.month.isin(['June','July','August'])].groupby('province_key',as_index=False).agg(fldas_et_anomaly_summer_mm_day=('et_anomaly_mm_per_day','mean'))
    t=mortality();t['province_key']=t.original_aimag_name.map(key)
    merged=t.merge(nd,on='province_key',validate='one_to_one').merge(nd_hist,on='province_key',validate='one_to_one').merge(smspring,on='province_key',validate='one_to_one').merge(smsummer,on='province_key',validate='one_to_one').merge(etspring,on='province_key',validate='one_to_one').merge(etsummer,on='province_key',validate='one_to_one')
    assert len(merged)==22 and merged.province_key.is_unique and merged.notna().all().all()
    merged.to_csv(RESULTS/'joint_2020_satellite_indicators_vs_2021_mortality.csv',index=False)
    # Exploratory correlations only: no causality, spatial independence or multiple-testing claims.
    from scipy.stats import spearmanr
    cols=['ndvi_true_anomaly_jja_2020','ndvi_2020_JJA','ndvi_difference_2020_minus_2019','smap_ssma_spring_mean','smap_ssma_summer_mean','fldas_et_anomaly_spring_mm_day','fldas_et_anomaly_summer_mm_day']
    rows=[]
    for col in cols:
        rho=float(spearmanr(merged[col],merged.mortality_percent_2021).statistic)
        loo=[float(spearmanr(merged.drop(i)[col],merged.drop(i).mortality_percent_2021).statistic) for i in merged.index]
        rows.append({'metric':col,'n_provinces':len(merged),'spearman_rho_exploratory':rho,'leave_one_out_rho_min':min(loo),'leave_one_out_rho_max':max(loo)})
    corr=pd.DataFrame(rows);corr.to_csv(RESULTS/'exploratory_province_correlations_and_LOO.csv',index=False)
    # Missing-coverage sensitivity: western/southern arid provinces have up to 53% original zero/masked raster cells.
    sensitivity=[]
    for threshold in (0.0,0.75,0.90):
        subset=merged[(merged.smap_spring_min_valid_fraction>=threshold)&(merged.smap_summer_min_valid_fraction>=threshold)]
        for col in cols:
            sensitivity.append({'smap_min_valid_fraction_threshold':threshold,'metric':col,'n_provinces':len(subset),'spearman_rho_exploratory':float(spearmanr(subset[col],subset.mortality_percent_2021).statistic)})
    pd.DataFrame(sensitivity).to_csv(RESULTS/'coverage_sensitivity_exploratory_correlations.csv',index=False)
    fig,axes=plt.subplots(1,3,figsize=(14.5,4.8),constrained_layout=True)
    for ax,col,xlab in zip(axes,['ndvi_true_anomaly_jja_2020','smap_ssma_spring_mean','fldas_et_anomaly_summer_mm_day'],['JJA 2020 NDVI anomaly (2002–2019)','Mar–May 2020 SMAP ssma (mean)','Jun–Aug 2020 FLDAS ET anomaly (mm/day)']):
        ax.scatter(merged[col],merged.mortality_percent_2021)
        for _,r in merged.nlargest(4,'mortality_percent_2021').iterrows():ax.annotate(str(r.original_aimag_name),(r[col],r.mortality_percent_2021),fontsize=7)
        ax.set(xlabel=xlab,ylabel='2021 deaths / 2020 livestock population (%)',title='Exploratory province comparison')
    fig.suptitle('Temporal association only; no causal or predictive validation')
    fig.savefig(RESULTS/'06_exploratory_satellite_mortality_province_scatter.png',dpi=130)
    plt.close(fig)
    return merged,corr

def run_all():
    import json
    n,a=compute_ndvi();s,n_zeros=compute_smap();e,es,fp=compute_ecostress();from .climatology import compute_gee_2020_anomalies
    historical_anomaly,_=compute_gee_2020_anomalies();from .fldas import calculate_fldas
    fldas_monthly=calculate_fldas();j,c=compute_joint_indicators()
    report={'input_type':'real archived NASA/JPL satellite and livestock records','province_count':len(j),'ndvi_month_province_records':len(n),'ndvi_historical_2002_2019_anomaly_records':len(historical_anomaly),'fldas_month_province_records':len(fldas_monthly),'smap_month_province_records':len(s),'smap_identical_zero_cells_excluded':n_zeros,'ecostress_scene_rows':len(e),'ecostress_year_counts':{str(year):int((e.year==year).sum()) for year in (2019,2020)},'national_2021_livestock_losses_thousands':float(j.deaths_2021_thousands.sum()),'national_2020_livestock_population_thousands':float(j.livestock_population_2020_thousands.sum()),'mean_2020_ndvi_summer':float(j.ndvi_2020_JJA.mean()),'mean_2020_ndvi_true_anomaly_JJA_across_provinces':float(j.ndvi_true_anomaly_jja_2020.mean()),'mean_2020_smap_spring_ssma':float(j.smap_ssma_spring_mean.mean()),'ecostress_sample_scenes_overlap':False,'correlations':c.to_dict('records')}
    (RESULTS/'VERIFIED_EXECUTION_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    import json
    print(json.dumps(run_all(),indent=2))
