import geopandas
from matplotlib import pyplot as plt
from matplotlib import colors
import pandas as pd 

year=2015

total_rain_df=pd.read_csv("preprocessed_data/mean_total_rain.csv")
total_rain_df.rename(columns={'Area':'NAME_1'},inplace=True)
total_rain_df.loc[total_rain_df['NAME_1']=='Bangkok','NAME_1']='Bangkok Metropolis'

thai_map=geopandas.read_file("gadm36_THA.gpkg",layer="gadm36_THA_1")

# print(set_rain_province.difference(set_province))

thai_map_with_data=thai_map.merge(total_rain_df,on='NAME_1',how='left')
print(thai_map_with_data)

fig,ax=plt.subplots(1,figsize=(9,12))
thai_map_with_data.plot(column=str(year),ax=ax,legend=True,cmap='RdYlGn_r',edgecolor=(0,0,0,1),norm=colors.PowerNorm(1),linewidth=1,missing_kwds={'color':'white','edgecolor':'blue','hatch':'///'})
plt.savefig('plot_preview.png',dpi=300)