"""Rebuild 2002–2019 GEE NDVI baseline and the 2020 anomalies from archived real monthly rasters.
Historical product: GEE MODIS/MOD09GA_006_NDVI, monthly means from daily index.
Do not mix with Giovanni MOD13C2 monthly product, which has a different algorithm/grid.
"""
from __future__ import annotations
import argparse, hashlib, csv
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rasterio.mask import mask as raster_mask
from .pipeline import DATA,RESULTS,provinces,MONTHS,_prov_valid_values

ORIGINAL_DIRNAME='mean_ndvi-{month} {year}.tif.tiff'
CLIM=DATA/'ndvi_gee_climatology'
TARGET=DATA/'ndvi_gee_2020'
SOURCE_MANIFEST=CLIM/'historical_54_file_SHA256_source_manifest.csv'


def filehash(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(2**20),b''):h.update(chunk)
    return h.hexdigest()

def build_baselines_from_full_archive(source_folder:Path):
    """One-time private full-archive regeneration, using 54 independently archived 2002–2019 TIFFs."""
    source_folder=Path(source_folder);CLIM.mkdir(parents=True,exist_ok=True)
    TARGET.mkdir(parents=True,exist_ok=True)
    manifest=[];qc=[]
    for mon in MONTHS:
        paths=[source_folder/ORIGINAL_DIRNAME.format(month=mon.lower(),year=y) for y in range(2002,2020)]
        missing=[str(p) for p in paths if not p.exists()]
        if missing:raise FileNotFoundError('Missing historical source files: '+', '.join(missing))
        raw20=source_folder/ORIGINAL_DIRNAME.format(month=mon.lower(),year=2020)
        if not raw20.exists():raise FileNotFoundError(str(raw20))
        # Source GeoTIFFs share a fixed zero-filled export mask across all 18 years.
        acc=None;count=None;reference=None;static_zero=None
        for year,path in zip(range(2002,2020),paths):
            with rasterio.open(path) as s:
                if reference is None:
                    reference=s.profile.copy();geometry=(s.shape,s.transform,s.crs);acc=np.zeros(s.shape,dtype=np.float64);count=np.zeros(s.shape,dtype=np.uint8);static_zero=(s.read(1)==0)
                assert (s.shape,s.transform,s.crs)==geometry,('grid mismatch',str(path))
                a=s.read(1)
                assert np.array_equal(a==0,static_zero),('zero-export-mask pattern differs',str(path))
                valid=(~static_zero)&np.isfinite(a)&(a>=-1)&(a<=1)
                acc[valid]+=a[valid]
                count[valid]+=1
                manifest.append({'year':year,'month':mon,'original_filename':path.name,'sha256':filehash(path),'pixels_accepted':int(valid.sum()),'source_dataset':'GEE MODIS/MOD09GA_006_NDVI monthly mean'})
        assert np.count_nonzero(count==18)>2000000
        ave=np.full(reference['height'],0,dtype=np.float32) if False else np.full(geometry[0],-9999,dtype=np.float32)
        ok=count==18
        ave[ok]=(acc[ok]/18).astype(np.float32)
        profile=reference.copy();profile.update(dtype='float32',nodata=-9999,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256)
        out=CLIM/f'NDVI_{mon.lower()}_2002_2019_mean_EXCLUDES_2020.tif'
        with rasterio.open(out,'w',**profile) as ds:ds.write(ave,1)
        # Retain the actual corresponding 2020 observations in repo, so notebook is self-contained.
        from shutil import copy2
        copy2(raw20,TARGET/f'NDVI_{mon.lower()}_2020_original_GEE.tif')
        with rasterio.open(raw20) as s:
            assert (s.shape,s.transform,s.crs)==geometry
            z=s.read(1)
            assert np.array_equal(z==0,static_zero)
            good=ok&np.isfinite(z)&(z>=-1)&(z<=1)
        qc.append({'month':mon,'historical_years':18,'source_rasters':18,'output_2020_raster_file':raw20.name,'historical_reference_excludes_2020':True,'source_zero_mask_cells':int(static_zero.sum()),'fully_valid_reference_cells':int(ok.sum()),'valid_2020_anomaly_cells':int(good.sum()),'zero_mask_fraction':float(np.mean(static_zero))})
        print(mon,'18-year baseline:',int(ok.sum()),'valid grid cells; sample avg',round(float(np.mean(ave[ok])),4),flush=True)
    with SOURCE_MANIFEST.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
    pd.DataFrame(qc).to_csv(CLIM/'baseline_generation_QA.csv',index=False)
    return pd.DataFrame(qc)


def compute_gee_2020_anomalies():
    """Compare 2020 monthly source raster to genuine 2002–2019 month-specific NDVI climatology."""
    geo=provinces();rows=[];fig,axes=plt.subplots(1,3,figsize=(15,4.8),constrained_layout=True)
    for i,mon in enumerate(MONTHS):
        pbase=CLIM/f'NDVI_{mon.lower()}_2002_2019_mean_EXCLUDES_2020.tif'
        pt=TARGET/f'NDVI_{mon.lower()}_2020_original_GEE.tif'
        with rasterio.open(pbase) as b,rasterio.open(pt) as t:
            assert b.crs==t.crs and b.shape==t.shape and b.transform==t.transform
            baseline=b.read(1,masked=True)
            value=t.read(1)
            invalid=(np.ma.getmaskarray(baseline)|(~np.isfinite(value))|(value < -1)|(value>1))
            anom=np.asarray(value-baseline.filled(np.nan),dtype='float32')
            anom[invalid]=-9999
            profile=t.profile.copy();profile.update(dtype='float32',nodata=-9999,compress='deflate',predictor=3,tiled=True,blockxsize=256,blockysize=256)
            p=RESULTS/f'NDVI_{mon.lower()}_2020_anomaly_vs_2002_2019.tif'
            with rasterio.open(p,'w',**profile) as s:s.write(anom,1)
            arr=np.ma.masked_where(anom==-9999,anom)
            im=axes[i].imshow(arr,extent=(t.bounds.left,t.bounds.right,t.bounds.bottom,t.bounds.top),origin='upper',cmap='RdBu',vmin=-.28,vmax=.28)
            geo.boundary.plot(ax=axes[i],linewidth=.28,color='black')
            axes[i].set(title=f'{mon} 2020 anomaly',xlabel='Longitude',ylabel='Latitude')
        with rasterio.open(p) as src:
            for _,r in geo.iterrows():
                st=_prov_valid_values(src,r.geometry,valid_bounds=(-1,1))
                rows.append({'province_key':r.province_key,'province':r.prefecture,'month':mon,'observed_2020_minus_2002_2019_mean_NDVI':st['mean'],'n_valid_pixels':st['n_valid'],'valid_fraction':st['valid_fraction']})
    fig.suptitle('MODIS daily-derived NDVI • 2020 minus 2002–2019 monthly reference',fontsize=13)
    fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.75,label='NDVI anomaly (unitless); red = below reference')
    fig.savefig(RESULTS/'07_ndvi_2020_true_historical_anomaly.png',dpi=140)
    plt.close(fig)
    res=pd.DataFrame(rows)
    assert len(res)==66 and res.observed_2020_minus_2002_2019_mean_NDVI.notna().all()
    res.to_csv(RESULTS/'ndvi_2020_historical_anomaly_by_province.csv',index=False)
    jja=res.groupby('province_key',as_index=False).agg(ndvi_true_anomaly_jja_2020=('observed_2020_minus_2002_2019_mean_NDVI','mean'))
    jja.to_csv(RESULTS/'ndvi_2020_true_historical_anomaly_jja_by_province.csv',index=False)
    return res,jja

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--original-folder',type=Path,required=True,help='The 54 original 2002–2019 and three 2020 GEE monthly TIFFs')
    args=parser.parse_args()
    print(build_baselines_from_full_archive(args.original_folder))
    print(compute_gee_2020_anomalies()[1])
