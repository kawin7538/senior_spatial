import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
from tqdm import tqdm
from data_loading import DataLoading

class BaseCluster:
    def __init__(self,data:DataLoading,multiplier=100000) -> None:
        # self.data=data.multiply_value(multiplier)
        self.data=deepcopy(data)
        self.multiplier=multiplier
        self._get_multiplier()
        self.global_cluster=None
        self.local_cluster=None
        self.global_keyword="Base_Cluster"
        self.local_keyword="Base_Cluster"
        self.global_path="output/g_global_test.csv"
        self.global_path="output/g_local_test.csv"
        self.range_year=self.data.range_year

    def _get_multiplier(self):
        for type_keyword in self.data.list_type_keyword:
            self.data.list_case_map[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_case_map[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_death_map[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_death_map[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_case_df[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_case_df[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_death_df[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_death_df[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
        
        self.data.list_case_minmax_value=self.data._get_list_minmax_value(data_keyword='case')
        self.data.list_death_minmax_value=self.data._get_list_minmax_value(data_keyword='death')
        # return self.data

    def process_global_cluster(self):
        global_cluster=dict()
        for data_keyword in ['case','death']:
            global_cluster[data_keyword]=dict()
            for type_keyword in self.data.list_type_keyword:
                global_cluster[data_keyword][type_keyword]=dict()
                global_cluster=self._process_global_cluster(global_cluster,data_keyword,type_keyword)
        return global_cluster

    def _process_global_cluster(self,global_cluster,data_keyword,type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.global_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            cluster_value=None
            global_cluster[data_keyword][type_keyword][year]=cluster_value
        return global_cluster

    def process_local_cluster(self):
        local_cluster=dict()
        for data_keyword in ['case','death']:
            local_cluster[data_keyword]=dict()
            for type_keyword in self.data.list_type_keyword:
                local_cluster[data_keyword][type_keyword]=dict()
                local_cluster=self._process_local_cluster(local_cluster,data_keyword,type_keyword)
        return local_cluster

    def _process_local_cluster(self,local_cluster,data_keyword,type_keyword):
        for year in tqdm(self.range_year,desc=f"{self.local_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            cluster_value=None
            local_cluster[data_keyword][type_keyword][year]=cluster_value
        return local_cluster

    def save_global_cluster_csv(self):
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                self._save_global_cluster_csv(data_keyword,type_keyword)

    def _save_global_cluster_csv(self,data_keyword,type_keyword):
        global_g_df=pd.DataFrame()
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            pass;
        global_g_df.to_csv(self.global_path.format(data_keyword,type_keyword),index=False)

    def save_local_cluster_csv(self):
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                self._save_local_cluster_csv(data_keyword,type_keyword)

    def _save_local_cluster_csv(self,data_keyword,type_keyword):
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            local_g_df=pd.DataFrame()
            local_g_df.to_csv(self.local_path.format(data_keyword,type_keyword,year),index=False)

class BasePlot:
    def __init__(self,cluster:BaseCluster) -> None:
        self.cluster=deepcopy(cluster)
        self.data=self.cluster.data
        self.range_year=self.data.range_year
        self.list_case_minmax_value=self.data.list_case_minmax_value
        self.list_death_minmax_value=self.data.list_death_minmax_value
        self.keyword="BasePlot"
        self.path=""

    def save_local_cluster_plot_png(self):
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                for year in tqdm(self.range_year,desc=f"{self.keyword} {data_keyword} {type_keyword}"):
                    self._make_local_cluster_plot(year,data_keyword,type_keyword,self.data.list_type_keyword.index(type_keyword))
                    plt.savefig(self.path.format(data_keyword,type_keyword,year))

    def _make_local_cluster_plot(self,year:int,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))

    def plot_preview(self):
        self._make_local_cluster_plot(2011,'case','DF',self.data.list_type_keyword.index('DF'))
        plt.savefig("plot_preview.png")