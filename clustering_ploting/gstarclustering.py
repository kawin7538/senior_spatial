import gc
from esda.getisord import G_Local
from matplotlib import colors, pyplot as plt
import pandas as pd
import pickle
from esda import G
from tqdm import tqdm
from data_loading import DataLoading
from .base import BaseCluster, BasePlot

class GStarCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier,permutations=9999) -> None:
        super().__init__(data, multiplier=multiplier)
        # self.data.set_inner_loop(77,1)
        self.global_keyword="G_Global"
        self.global_dump_model_path=".dump_model/g_global_{}_{}_{}"
        self.global_path="output/gstar/{}/{}/g_global.csv"
        self.local_keyword="GStar_local"
        self.local_dump_model_path=".dump_model/gistar_local_{}_{}_{}"
        self.local_path="output/gstar/{}/{}/gistar_local_{}.csv"
        self.local_path_sig="output/gstar/{}/{}/gistar_local_{}_sig.csv"
        self.permutations=permutations
        self.range_year=self.data.range_year
        self.global_cluster=self.process_global_cluster()
        self.local_cluster=self.process_local_cluster()

    def _process_global_cluster(self,global_cluster,data_keyword,type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.global_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            G_global=G(y["total"],self.data.get_weight(),permutations=self.permutations)
            
            file = open(self.global_dump_model_path.format(data_keyword,type_keyword,year),'wb')
            pickle.dump(G_global,file)
            file.close()

            global_cluster[data_keyword][type_keyword][year]=self.global_dump_model_path.format(data_keyword,type_keyword,year)

            del map_with_data,y,G_global,file
            gc.collect()
            
        return global_cluster

    def _process_local_cluster(self, local_cluster, data_keyword, type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.local_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]

            self.data.set_inner_loop(77,1)
            gistar_local=G_Local(y["total"],self.data.get_weight(),transform='b',star=True,permutations=self.permutations)
            self.data.set_inner_loop(77,0)

            file = open(self.local_dump_model_path.format(data_keyword,type_keyword,year),'wb')
            pickle.dump(gistar_local,file)
            file.close()

            # local_cluster[data_keyword][type_keyword][year]=gistar_local
            local_cluster[data_keyword][type_keyword][year]=self.local_dump_model_path.format(data_keyword,type_keyword,year)

            del map_with_data,y,gistar_local,file
            gc.collect()

        return local_cluster

    def _save_global_cluster_csv(self,data_keyword,type_keyword):
        global_g_df=pd.DataFrame(columns=['year','G','G_z','G_p_value'])
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            
            # g_global=self.global_cluster[data_keyword][type_keyword][year]
            file=open(self.global_cluster[data_keyword][type_keyword][year],'rb')
            g_global=pickle.load(file)
            file.close()
            
            global_g_df.loc[len(global_g_df)]=[year,g_global.G,g_global.z_sim,g_global.p_sim]

            del g_global,file
            gc.collect()

        global_g_df.to_csv(self.global_path.format(data_keyword,type_keyword),index=False)

        del global_g_df
        gc.collect()

    def _save_local_cluster_csv(self,data_keyword,type_keyword):
        spots=['not-significant','hotspot-0.01','hotspot-0.05','hotspot-0.1','coldspot-0.1','coldspot-0.05','coldspot-0.01']
        for year in tqdm(self.range_year,desc=f"sav {self.local_keyword} {data_keyword} {type_keyword}"):

            # gistar_local=self.local_cluster[data_keyword][type_keyword][year]
            file=open(self.local_cluster[data_keyword][type_keyword][year],'rb')
            gistar_local=pickle.load(file)
            file.close()
            
            hotspot90=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.1)
            hotspot95=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.05)
            hotspot99=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.01)
            hotspot90=hotspot90&~hotspot95
            hotspot95=hotspot95&~hotspot99
            notsig=(gistar_local.p_sim>0.1)
            coldspot90=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.1)
            coldspot95=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.05)
            coldspot99=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.01)
            coldspot90=coldspot90&~coldspot95
            coldspot95=coldspot95&~coldspot99
            hotcoldspot=hotspot99*1+hotspot95*2+hotspot90*3+coldspot90*4+coldspot95*5+coldspot99*6
            labels=[spots[i] for i in hotcoldspot]

            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            y.assign(gistar_Z=gistar_local.Zs,gistar_p_value=gistar_local.p_sim,cl=labels)[['NAME_1','year','gistar_Z','gistar_p_value','cl']].round(4).to_csv(self.local_path.format(data_keyword,type_keyword,year),index=False)
            y.assign(gistar_Z=gistar_local.Zs,gistar_p_value=gistar_local.p_sim,cl=labels).loc[~notsig,['NAME_1','year','gistar_Z','gistar_p_value','cl']].round(4).to_csv(self.local_path_sig.format(data_keyword,type_keyword,year),index=False)

            del file,gistar_local,hotspot90,hotspot95,hotspot99,notsig,coldspot90,coldspot95,coldspot99,hotcoldspot,labels,map_with_data,y
            gc.collect()

class GStarPlot(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        super(GStarPlot,self).__init__(cluster)
        self.keyword="GStar Plot"
        self.path="output/gstar/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]

        # gistar_local=self.local_cluster[data_keyword][type_keyword][year]
        file=open(self.cluster.local_cluster[data_keyword][type_keyword][year],'rb')
        gistar_local=pickle.load(file)
        file.close()

        hotspot90=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.1)
        hotspot95=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.05)
        hotspot99=(gistar_local.Zs>0)&(gistar_local.p_sim<=0.01)
        hotspot90=hotspot90&~hotspot95
        hotspot95=hotspot95&~hotspot99
        notsig=(gistar_local.p_sim>0.1)
        coldspot90=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.1)
        coldspot95=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.05)
        coldspot99=(gistar_local.Zs<0)&(gistar_local.p_sim<=0.01)
        coldspot90=coldspot90&~coldspot95
        coldspot95=coldspot95&~coldspot99
        hotcoldspot=hotspot99*1+hotspot95*2+hotspot90*3+coldspot90*4+coldspot95*5+coldspot99*6
        spots=['not-significant','hotspot-0.01','hotspot-0.05','hotspot-0.1','coldspot-0.1','coldspot-0.05','coldspot-0.01']
        labels=[spots[i] for i in hotcoldspot]
        color_list=['lightgrey','red',(1,0.3,0.3),(1,0.6,0.6),(0.6,0.6,1),(0.3,0.3,1),'blue'][::-1]
        hmap=colors.ListedColormap(color_list)
        color_labels=[color_list[::-1][i] for i in hotcoldspot]

        # if data_keyword=='case':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_case_minmax_value[idx][0],vmax=self.list_case_minmax_value[idx][1]))
        #     y.assign(cl=labels).assign(spot=hotcoldspot).plot(column='cl',categorical=True,linewidth=0.1,ax=ax,edgecolor='white',cmap=hmap,k=7,categories=spots[::-1],legend=False)
        # if data_keyword=='death':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_death_minmax_value[idx][0],vmax=self.list_death_minmax_value[idx][1]))
        y.assign(cl=labels).assign(spot=hotcoldspot).plot(column='cl',categorical=True,linewidth=0.1,ax=ax,edgecolor='white',cmap=hmap,k=7,categories=spots[::-1],legend=True)
        ax.set_axis_off()
        plt.title(' {} {} {} {}'.format(data_keyword,type_keyword,self.keyword,year))

        del gistar_local,hotspot90,hotspot95,hotspot99,notsig,coldspot90,coldspot95,coldspot99,hotcoldspot,labels,map_with_data,y
        gc.collect()