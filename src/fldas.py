"""Original 2020 NASA FLDAS monthly evapotranspiration anomalies (1982–2016 climatology)."""
from __future__ import annotations
import numpy as np
import pandas as pd
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .pipeline import DATA,RESULTS,provinces,MONTHS_SMAP,_prov_valid_values

SECONDS_DAY=86400.0

def calculate_fldas():
    g=provinces();records=[];fig,axes=plt.subplots(2,3,figsize=(15,8),constrained_layout=True)
    for ax,month in zip(axes.flat,MONTHS_SMAP):
        m=MONTHS_SMAP.index(month)+3
        path=DATA/'fldas_et_anomaly_2020'/f'FLDAS_ET_Anomaly_2020{m:02d}.tif'
        with rasterio.open(path) as src:
            assert src.crs.to_epsg()==4326 and src.shape==(107,324)
            tags=src.tags(1)
            # The source is the Anomaly dataset, not the FLDAS raw monthly-average dataset.
            assert tags.get('long_name')=='Anomaly of Total evapotranspiration',tags
            assert tags.get('units')=='kg m-2 s-1',tags
            a=src.read(1,masked=True)
            vals=np.ma.masked_invalid(a)*SECONDS_DAY
            im=ax.imshow(vals,extent=(src.bounds.left,src.bounds.right,src.bounds.bottom,src.bounds.top),origin='upper',cmap='RdBu',vmin=-2,vmax=2)
            for _,r in g.iterrows():
                stat=_prov_valid_values(src,r.geometry)
                records.append({'province_key':r.province_key,'province':r.prefecture,'month':month,
                    'et_flux_anomaly_kg_m2_s':stat['mean'],'et_anomaly_mm_per_day':stat['mean']*SECONDS_DAY,
                    'valid_cells':stat['n_valid'],'valid_fraction':stat['valid_fraction']})
        g.boundary.plot(ax=ax,color='black',linewidth=.3)
        ax.set(title=f'2020 {month}',xlabel='Longitude',ylabel='Latitude')
    fig.suptitle('NASA FLDAS evapotranspiration anomalies • 2020 vs 1982–2016 monthly climatology',fontsize=12)
    fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.6,label='ET flux anomaly equivalent (mm/day); red = below reference')
    fig.savefig(RESULTS/'08_fldas_et_anomalies_mar_aug_2020.png',dpi=130)
    plt.close(fig)
    df=pd.DataFrame(records)
    assert len(df)==132 and df.et_anomaly_mm_per_day.notna().all()
    df.to_csv(RESULTS/'fldas_et_anomaly_2020_provincial_monthly.csv',index=False)
    return df

if __name__=='__main__':
    x=calculate_fldas();print(x.groupby('month').et_anomaly_mm_per_day.agg(['min','mean','max']).to_string())
