import geopandas
from matplotlib import pyplot as plt
from matplotlib import colors
import pandas as pd 
import os

from tqdm import tqdm, tqdm_gui

def plot_some_rain(year,keyword):

    if not os.path.exists(f"output/{keyword}"):
        print(f"output/{keyword} not exist, create it")
        os.makedirs(f"output/{keyword}")

    total_rain_df=pd.read_csv(f"preprocessed_data/mean_{keyword}.csv")
    total_rain_df.rename(columns={'Area':'NAME_1'},inplace=True)
    total_rain_df.loc[total_rain_df['NAME_1']=='Bangkok','NAME_1']='Bangkok Metropolis'

    thai_map=geopandas.read_file("gadm36_THA.gpkg",layer="gadm36_THA_1")

    thai_map_with_data=thai_map.merge(total_rain_df,on='NAME_1',how='left')

    fig,ax=plt.subplots(1,figsize=(9,12))
    thai_map_with_data.plot(column=str(year),ax=ax,legend=True,cmap='RdYlGn_r',edgecolor=(0,0,0,1),norm=colors.PowerNorm(1,vmin=0,vmax=thai_map_with_data.iloc[:,-6:].max().max()),linewidth=1,missing_kwds={'color':'white','edgecolor':'blue','hatch':'///'})
    ax.set_axis_off()
    # plt.savefig('plot_preview.png',dpi=300,bbox_inches='tight')
    plt.savefig(f'output/{keyword}/{year}.png',dpi=300,bbox_inches='tight')

if __name__=='__main__':
    for year in tqdm(range(2011,2016)):
        plot_some_rain(year,'total_rain')
        plot_some_rain(year,'cnt_day_rain')
        plot_some_rain(year,'totalperday_rain')