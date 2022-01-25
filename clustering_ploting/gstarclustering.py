import gc
import pickle

import pandas as pd
from data_loading import DataLoading
from esda import G
from esda.getisord import G_Local
from matplotlib import colors
from matplotlib import pyplot as plt
from tqdm import tqdm

from .base import BaseCluster, BasePlot


class GStarCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier,permutations=9999) -> None:
        super().__init__(data, multiplier=multiplier)
        # self.data.set_inner_loop(77,1)
        self.global_keyword="G_Global"
        self.global_dump_model_path=".dump_model/g_global_{}_{}_{}"
        self.global_path="{}/gstar/{}/{}/g_global.csv"
        self.local_keyword="GStar_local"
        self.local_dump_model_path=".dump_model/gistar_local_{}_{}_{}"
        self.local_path="{}/gstar/{}/{}/gistar_local_{}.csv"
        self.local_path_sig="{}/gstar/{}/{}/gistar_local_{}_sig.csv"
        self.permutations=permutations
        self.range_year=self.data.range_year

        self._set_output_folder('gstar')
        
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
            try:
                map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
                y=map_with_data[map_with_data['year']==year]
                # print(y.info())
                y['total']=y['total'].astype(float).fillna(0)
                # print(y.info())
                # print(y)

                # self.data.set_inner_loop(77,1)
                gistar_local=G_Local(y["total"],self.data.get_weight(),transform='B',star=True,permutations=self.permutations)
                # self.data.set_inner_loop(77,0)

                file = open(self.local_dump_model_path.format(data_keyword,type_keyword,year),'wb')
                pickle.dump(gistar_local,file)
                file.close()

                # local_cluster[data_keyword][type_keyword][year]=gistar_local
                local_cluster[data_keyword][type_keyword][year]=self.local_dump_model_path.format(data_keyword,type_keyword,year)

                del map_with_data,y,gistar_local,file
                gc.collect()

            except Exception as e:
                s=str(e)
                err_file=open(f"output/log/error/_process_local_cluster_{self.data.load_ratio}_{self.local_keyword}_{data_keyword}_{type_keyword}_{year}.err",'w')
                err_file.write(s)
                err_file.close()
                print(f"{self.local_keyword} in {data_keyword} {type_keyword} year {year} error, skipped it")

        return local_cluster

    def _save_global_cluster_csv(self,data_keyword,type_keyword):
        global_g_df=pd.DataFrame(columns=['year','G','EG_sim','VG_sim','G_z_sim','G_p_value'])
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            
            # g_global=self.global_cluster[data_keyword][type_keyword][year]
            file=open(self.global_cluster[data_keyword][type_keyword][year],'rb')
            g_global=pickle.load(file)
            file.close()
            
            global_g_df.loc[len(global_g_df)]=[year,g_global.G,g_global.EG_sim,g_global.VG_sim,g_global.z_sim,g_global.p_sim]

            del g_global,file
            gc.collect()

        global_g_df.to_csv(self.global_path.format(self.data.base_output_path,data_keyword,type_keyword),index=False)

        del global_g_df
        gc.collect()

    def _save_local_cluster_csv(self,data_keyword,type_keyword):
        spots=['not-significant','hotspot-0.01','hotspot-0.05','hotspot-0.1','coldspot-0.1','coldspot-0.05','coldspot-0.01']
        for year in tqdm(self.range_year,desc=f"sav {self.local_keyword} {data_keyword} {type_keyword}"):

            try:

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
                y.assign(gistar_G=gistar_local.Gs,gistar_E=gistar_local.EG_sim,gistar_V=gistar_local.VG_sim,gistar_Z=gistar_local.Zs,gistar_p_value=gistar_local.p_sim,cl=labels)[['NAME_1','year','gistar_G','gistar_E','gistar_V','gistar_Z','gistar_p_value','cl']].round(4).to_csv(self.local_path.format(self.data.base_output_path,data_keyword,type_keyword,year),index=False)
                y.assign(gistar_G=gistar_local.Gs,gistar_E=gistar_local.EG_sim,gistar_V=gistar_local.VG_sim,gistar_Z=gistar_local.Zs,gistar_p_value=gistar_local.p_sim,cl=labels).loc[~notsig,['NAME_1','year','gistar_G','gistar_E','gistar_V','gistar_Z','gistar_p_value','cl']].round(4).to_csv(self.local_path_sig.format(self.data.base_output_path,data_keyword,type_keyword,year),index=False)

                del file,gistar_local,hotspot90,hotspot95,hotspot99,notsig,coldspot90,coldspot95,coldspot99,hotcoldspot,labels,map_with_data,y
                gc.collect()

            except Exception as e:
                s=str(e)
                err_file=open(f"output/log/error/_save_local_cluster_csv_{self.data.load_ratio}_{self.local_keyword}_{data_keyword}_{type_keyword}_{year}.err",'w')
                err_file.write(s)
                err_file.close()
                print(f"{self.local_keyword} in {data_keyword} {type_keyword} year {year} error, skipped it")

class GStarPlot(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        super(GStarPlot,self).__init__(cluster)
        self.keyword="GStar Plot"
        self.path="{}/gstar/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):

        try:

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

            y.assign(cl=labels).assign(spot=hotcoldspot).plot(column='cl',categorical=True,linewidth=0.1,ax=ax,edgecolor='white',cmap=hmap,k=7,categories=spots[::-1],legend=True)
            ax.set_axis_off()
            plt.title('{} {} {} {} {}'.format('ratio' if self.data.load_ratio else 'raw',data_keyword,type_keyword,self.keyword,year))

            del gistar_local,hotspot90,hotspot95,hotspot99,notsig,coldspot90,coldspot95,coldspot99,hotcoldspot,labels,map_with_data,y
            gc.collect()

        except Exception as e:
            s=str(e)
            err_file=open(f"output/log/error/_make_local_cluster_plot_{self.data.load_ratio}_{self.keyword}_{data_keyword}_{type_keyword}_{year}.err",'w')
            err_file.write(s)
            err_file.close()
            print(f"{self.keyword} in {data_keyword} {type_keyword} year {year} error, skipped it")
