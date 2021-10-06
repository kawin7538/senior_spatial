from matplotlib import pyplot as plt
import pandas as pd
from data_loading import DataLoading
from tqdm import tqdm
import pickle
import gc
from .base import BaseCluster, BasePlot
from esda.moran import Moran, Moran_Local
from splot._viz_utils import mask_local_auto
from splot.esda import plot_local_autocorrelation,lisa_cluster

class MoranCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier=100000,permutations=9999,p_value=0.05) -> None:
        super().__init__(data, multiplier=multiplier)
        self.global_keyword="Moran_Global"
        self.global_dump_model_path=".dump_model/moran_global_{}_{}_{}"
        self.global_path="output/moran/{}/{}/moran_global.csv"
        self.local_keyword="Moran_local"
        self.local_dump_model_path=".dump_model/LISA_{}_{}_{}"
        self.local_path="output/moran/{}/{}/LISA_{}.csv"
        self.local_path_sig="output/moran/{}/{}/LISA_{}_sig.csv"
        self.p_value=p_value
        self.permutations=permutations
        self.range_year=self.data.range_year
        self.global_cluster=self.process_global_cluster()
        self.local_cluster=self.process_local_cluster()

        self._set_output_folder('moran')

    def _process_global_cluster(self,global_cluster,data_keyword,type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.global_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            # G_global=G(y["total"],self.data.get_weight(),permutations=self.permutations)
            moran_global=Moran(y["total"],self.data.get_weight(),transformation='B',two_tailed=True,permutations=self.permutations)
            
            file = open(self.global_dump_model_path.format(data_keyword,type_keyword,year),'wb')
            pickle.dump(moran_global,file)
            file.close()

            global_cluster[data_keyword][type_keyword][year]=self.global_dump_model_path.format(data_keyword,type_keyword,year)

            del map_with_data,y,moran_global,file
            gc.collect()
            
        return global_cluster

    def _process_local_cluster(self, local_cluster, data_keyword, type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.local_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]

            moran_local=Moran_Local(y['total'],self.data.get_weight(),transformation='B',permutations=self.permutations)

            file = open(self.local_dump_model_path.format(data_keyword,type_keyword,year),'wb')
            pickle.dump(moran_local,file)
            file.close()

            # local_cluster[data_keyword][type_keyword][year]=gistar_local
            local_cluster[data_keyword][type_keyword][year]=self.local_dump_model_path.format(data_keyword,type_keyword,year)

            del map_with_data,y,moran_local,file
            gc.collect()

        return local_cluster

    def _save_global_cluster_csv(self, data_keyword, type_keyword):
        global_moran_df=pd.DataFrame(columns=['year','moran_value','moran_z','moran_p_value'])
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            
            # g_global=self.global_cluster[data_keyword][type_keyword][year]
            file=open(self.global_cluster[data_keyword][type_keyword][year],'rb')
            moran_global=pickle.load(file)
            file.close()
            
            global_moran_df.loc[len(global_moran_df)]=[year,moran_global.I,moran_global.z_rand,moran_global.p_rand]

            del moran_global,file
            gc.collect()

        global_moran_df.to_csv(self.global_path.format(data_keyword,type_keyword),index=False)

        del global_moran_df
        gc.collect()

    def _save_local_cluster_csv(self, data_keyword, type_keyword):
        for year in tqdm(self.range_year,desc=f"sav {self.local_keyword} {data_keyword} {type_keyword}"):

            # gistar_local=self.local_cluster[data_keyword][type_keyword][year]
            file=open(self.local_cluster[data_keyword][type_keyword][year],'rb')
            moran_local=pickle.load(file)
            file.close()

            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]

            temp_result=y.assign(moran_value=moran_local.Is,moran_z=moran_local.z,moran_p_value=moran_local.p_sim,cl=mask_local_auto(moran_local,p=self.p_value)[3])
            temp_result[['NAME_1','year','moran_value','moran_z','moran_p_value','cl']].round(4).to_csv(self.local_path.format(data_keyword,type_keyword,year),index=False)
            temp_result.loc[temp_result['moran_p_value']<=self.p_value,['NAME_1','year','moran_value','moran_z','moran_p_value','cl']].round(4).to_csv(self.local_path_sig.format(data_keyword,type_keyword,year),index=False)

            del file,moran_local,map_with_data,y,temp_result
            gc.collect()

class LISAPlot(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        super().__init__(cluster)
        self.keyword="LISA Plot"
        self.path="output/moran/{}/{}/{}.png"
    
    def _make_local_cluster_plot(self, year: int, data_keyword, type_keyword, idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]

        file=open(self.cluster.local_cluster[data_keyword][type_keyword][year],'rb')
        moran_local=pickle.load(file)
        file.close()

        lisa_cluster(moran_local,y,ax=ax,p=self.cluster.p_value)
        ax.set_axis_off()

        plt.title('{} {} {} {}'.format(data_keyword,type_keyword,self.keyword,year))

        del moran_local,map_with_data,y
        gc.collect()