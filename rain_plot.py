import geopandas
from matplotlib import pyplot as plt
from matplotlib import colors
import pandas as pd 
import os

from tqdm import tqdm, tqdm_gui

from data_loading import DataLoading
import seaborn as sns
from scipy import stats

def r2(x,y):
    return stats.spearmanr(x,y)
def r2_1(x,y):
    return stats.pearsonr(x,y)

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
    # for year in tqdm(range(2011,2016)):
    #     plot_some_rain(year,'total_rain')
    #     plot_some_rain(year,'cnt_day_rain')
    #     plot_some_rain(year,'totalperday_rain')

    total_rain_df=pd.read_csv("preprocessed_data/mean_totalperday_rain.csv")[['Area','2011','2012','2013','2014','2015']]
    total_rain_df=pd.melt(total_rain_df,id_vars='Area',var_name='year',value_name='rain_total')
    total_rain_df['year']=total_rain_df['year'].astype(int)
    total_rain_df.rename(columns={'Area':'NAME_1'},inplace=True)
    total_rain_df.loc[total_rain_df['NAME_1']=='Bangkok','NAME_1']='Bangkok Metropolis'
    data=DataLoading(
        load_ratio=True,
        range_year=range(2011,2021),
    )
    allcase_df=data.list_case_df[-1][['NAME_1','year','total']]
    # print(allcase_df.info())
    # print(total_rain_df.info())
    sum_df=total_rain_df.merge(allcase_df,on=['NAME_1','year'],how='inner')
    # sum_df=pd.concat([allcase_df,total_rain_df],join='inner',axis=1,)
    # print(sum_df)
    sns.lmplot(x='rain_total',y='total',data=sum_df)
    plt.annotate(f"Spearman R2 = {round(r2(sum_df['rain_total'],sum_df['total'])[0]**2,5)}\nPearson R2 = {round(r2_1(sum_df['rain_total'],sum_df['total'])[0]**2,5)}",(0,0.01))
    plt.savefig("output/totalperday_rain/scatter.png",dpi=300)