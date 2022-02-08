import gc
import os
from copy import deepcopy

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from data_loading import DataLoading
from tqdm import tqdm


class BaseCluster:
    def __init__(self,data:DataLoading,multiplier=100000) -> None:
        '''
        This function is used to initialize the class.
        
        :param data: The DataLoading object that contains the data
        :type data: DataLoading
        :param multiplier: The multiplier is used to scale the data, defaults to 100000 (optional)
        '''
        # self.data=data.multiply_value(multiplier)

        if not os.path.exists('.dump_model/'):
            os.makedirs('.dump_model/')

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

    def _set_output_folder(self,keyword):
        '''
        If the folder does not exist, create it
        
        :param keyword: the keyword of the output folder
        '''
        # if not os.path.exists(f'{keyword}/'):
        #     os.makedirs(f'{keyword}/')
        for data_keyword in ['case','death']:
            for type_keyword in ['DF','DHF','DSS','ALL']:
                if not os.path.exists(f'{self.data.base_output_path}/{keyword}/{data_keyword}/{type_keyword}/'):
                    os.makedirs(f'{self.data.base_output_path}/{keyword}/{data_keyword}/{type_keyword}/')
                    print(f'\t{self.data.base_output_path}/{keyword}/{data_keyword}/{type_keyword}/ not existed, create it')

    def _get_multiplier(self):
        '''
        The function is used to multiply the value of the dataframe by a certain factor
        :return: Nothing.
        '''
        if not self.data.load_ratio:
            return ;
        for type_keyword in self.data.list_type_keyword:
            self.data.list_case_map[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_case_map[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_death_map[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_death_map[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_case_df[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_case_df[self.data.list_type_keyword.index(type_keyword)],self.multiplier)
            self.data.list_death_df[self.data.list_type_keyword.index(type_keyword)]=self.data._multiply_value_one(self.data.list_death_df[self.data.list_type_keyword.index(type_keyword)],self.multiplier)

        self.data.list_case_minmax_value=self.data._get_list_minmax_value(data_keyword='case')
        self.data.list_death_minmax_value=self.data._get_list_minmax_value(data_keyword='death')
        self.data.case_max_value=max([i[1] for i in self.data.list_case_minmax_value[:-1]])
        self.data.death_max_value=max([i[1] for i in self.data.list_death_minmax_value[:-1]])
        # return self.data

    def process_global_cluster(self):
        '''
        The function is to process the global cluster for each data_keyword and type_keyword
        :return: A dictionary of dictionaries. The first level of keys is the data type (case or death).
        The second level of keys is the type of data (confirmed, recovered, or death). The third level
        of keys is the cluster number. The value of the third level of keys is a list of the country
        names
        '''
        global_cluster=dict()
        for data_keyword in ['case','death']:
            global_cluster[data_keyword]=dict()
            for type_keyword in self.data.list_type_keyword:
                global_cluster[data_keyword][type_keyword]=dict()
                global_cluster=self._process_global_cluster(global_cluster,data_keyword,type_keyword)
        return global_cluster

    def _process_global_cluster(self,global_cluster,data_keyword,type_keyword):
        '''
        This function is used to process the global cluster
        
        :param global_cluster: the global cluster dictionary
        :param data_keyword: the keyword of the data to be processed
        :param type_keyword: The type of data we are looking at
        :return: A dictionary with the following structure:
            {
                "data_keyword":{
                    "type_keyword":{
                        "year":cluster_value
                    }
                }
            }
        '''
        for year in tqdm(self.range_year,desc=f"{self.global_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            cluster_value=None
            global_cluster[data_keyword][type_keyword][year]=cluster_value
        return global_cluster

    def process_local_cluster(self):
        '''
        This function is used to process the local cluster
        :return: A dictionary of dictionaries of dictionaries.
        '''
        local_cluster=dict()
        for data_keyword in ['case','death']:
            local_cluster[data_keyword]=dict()
            for type_keyword in self.data.list_type_keyword:
                local_cluster[data_keyword][type_keyword]=dict()
                local_cluster=self._process_local_cluster(local_cluster,data_keyword,type_keyword)
        return local_cluster

    def _process_local_cluster(self,local_cluster,data_keyword,type_keyword):
        '''
        This function is used to process the local cluster data
        
        :param local_cluster: a dictionary that contains the cluster value for each year for each
        data_keyword and type_keyword
        :param data_keyword: the keyword of the data that you want to cluster
        :param type_keyword: The type of data we are looking at
        :return: A dictionary with the following structure:
            {
                "local_keyword":{
                    "data_keyword":{
                        "type_keyword":{
                            "year":cluster_value
                        }
                    }
                }
            }
        '''
        for year in tqdm(self.range_year,desc=f"{self.local_keyword} {data_keyword} {type_keyword}"):
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]
            cluster_value=None
            local_cluster[data_keyword][type_keyword][year]=cluster_value
        return local_cluster

    def save_global_cluster_csv(self):
        '''
        For each data_keyword and type_keyword, save the global cluster dataframe as a csv file
        '''
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                self._save_global_cluster_csv(data_keyword,type_keyword)

        del data_keyword,type_keyword
        gc.collect()

    def _save_global_cluster_csv(self,data_keyword,type_keyword):
        '''
        # Python
        def _save_global_cluster_csv(self,data_keyword,type_keyword):
                global_g_df=pd.DataFrame()
                for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword}
        {type_keyword}"):
                    pass;
               
        global_g_df.to_csv(self.global_path.format(self.data.base_output_path,data_keyword,type_keyword),index=False)
        
        :param data_keyword: the keyword of the data set that you want to analyze
        :param type_keyword: The type of the data. For example, if the data is the result of a query,
        then the type is "query"
        '''
        global_g_df=pd.DataFrame()
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            pass;
        global_g_df.to_csv(self.global_path.format(self.data.base_output_path,data_keyword,type_keyword),index=False)

    def save_local_cluster_csv(self):
        '''
        This function saves the dataframe of the cluster data to a csv file
        '''
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                self._save_local_cluster_csv(data_keyword,type_keyword)
        
        del data_keyword,type_keyword
        gc.collect()

    def _save_local_cluster_csv(self,data_keyword,type_keyword):
        '''
        # Python
        def _save_local_cluster_csv(self,data_keyword,type_keyword):
                for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword}
        {type_keyword}"):
                    local_g_df=pd.DataFrame()
                   
        local_g_df.to_csv(self.local_path.format(data_keyword,type_keyword,year),index=False)
        
        :param data_keyword: the keyword of the data, e.g. "global"
        :param type_keyword: the type of data you want to download
        '''
        for year in tqdm(self.range_year,desc=f"sav {self.global_keyword} {data_keyword} {type_keyword}"):
            local_g_df=pd.DataFrame()
            local_g_df.to_csv(self.local_path.format(data_keyword,type_keyword,year),index=False)

# The BasePlot class is the parent class of all the plot classes.
# 
# The BasePlot class has the following attributes:
# 
# cluster: a BaseCluster object
# data: a BaseData object
# range_year: a list of years
# list_case_minmax_value: a list of min and max values of case
# list_death_minmax_value: a list of min and max values of death
# keyword: a string of the keyword of the plot
# path: a string of the path of the plot
# 
# The BasePlot
class BasePlot:
    def __init__(self,cluster:BaseCluster) -> None:
        '''
        The __init__ function is called when an instance of the class is created. 
        used to initialize the attributes of the class.
        
        :param cluster: the cluster object that is being used to generate the plot
        :type cluster: BaseCluster
        '''
        self.cluster=deepcopy(cluster)
        self.data=self.cluster.data
        self.range_year=self.data.range_year
        self.list_case_minmax_value=self.data.list_case_minmax_value
        self.list_death_minmax_value=self.data.list_death_minmax_value
        self.keyword="BasePlot"
        self.path=""

    def save_local_cluster_plot_png(self,bbox_inches=None):
        '''
        This function is used to save the local cluster plot as png file
        
        :param bbox_inches: 
        '''
        for data_keyword in ['case','death']:
            for type_keyword in self.data.list_type_keyword:
                for year in tqdm(self.range_year,desc=f"{self.keyword} {data_keyword} {type_keyword}"):
                    try:
                        self._make_local_cluster_plot(year,data_keyword,type_keyword,self.data.list_type_keyword.index(type_keyword))
                        plt.savefig(self.path.format(self.data.base_output_path,data_keyword,type_keyword,year),dpi=300,bbox_inches=bbox_inches)
                    except:
                        print(f"{self.keyword} in {data_keyword} {type_keyword} year {year} error, skipped it")
                        continue;
        
        del data_keyword,type_keyword,year
        gc.collect()

    def _make_local_cluster_plot(self,year:int,data_keyword,type_keyword,idx):
        '''
        The function creates a plot of the local cluster for a given year
        
        :param year: the year of the data we want to plot
        :type year: int
        :param data_keyword: the name of the dataframe that you want to plot
        :param type_keyword: 'confirmed' or 'deaths'
        :param idx: the index of the cluster you want to plot
        '''
        fig,ax=plt.subplots(1,figsize=(9,12))

    def plot_preview(self,bbox_inches=None):
        '''
        It creates a plot of the DF data for the year 2011.
        
        :param bbox_inches: 
        '''
        self._make_local_cluster_plot(2011,'case','DF',self.data.list_type_keyword.index('DF'))
        plt.savefig("plot_preview.png",dpi=300,bbox_inches=bbox_inches)
