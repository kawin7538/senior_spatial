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
        '''
        This function is used to load the data and set the output folder.
        
        :param data: The DataLoading object that contains the data
        :type data: DataLoading
        :param multiplier: The number of times to run the model
        :param permutations: The number of permutations to run, defaults to 9999 (optional)
        '''
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
        '''
        This function is used to create the global graph for each year and save it in a pickle file
        
        :param global_cluster: a dictionary that will be used to store the global cluster models
        :param data_keyword: the keyword of the data to be used
        :param type_keyword: The type of the data. For example, if the data is the number of patents,
        then the type_keyword is "patent"
        :return: A dictionary with the following structure:
            {
                "data_keyword":{
                    "type_keyword":{
                        "year":path_to_file
                    }
                }
            }
        '''
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
        '''
        This function is used to calculate the local cluster for each year. 
        
        The input is the local cluster, which is a dictionary. 
        
        The output is the local cluster, which is a dictionary. 
        
        The function will loop through the year range, and calculate the local cluster for each year. 
        
        The function will save the local cluster in the local_dump_model_path. 
        
        The function will return the local cluster.
        
        :param local_cluster: a dictionary that stores the local cluster models
        :param data_keyword: the keyword of the data set that you want to analyze
        :param type_keyword: the type of the data, e.g. "income"
        :return: A dictionary of dictionaries of dictionaries.
        '''
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
        '''
        This function is used to save the global cluster dataframe to csv file
        
        :param data_keyword: the keyword of the data set that you want to analyze
        :param type_keyword: the type of the graph, e.g. 'co_occurrence'
        '''
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
        '''
        Save the local cluster results to csv files
        
        :param data_keyword: the keyword of the data set that you want to analyze
        :param type_keyword: the type of the data, e.g. 'GDP'
        '''
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

# The code above is the core of the G* algorithm. It is the code that actually runs the G* algorithm
# on the data. 
# 
# The code above is the core of the G* algorithm. It is the code that actually runs the G* algorithm
# on the data. 
# 
# The code above is the core of the G* algorithm. It is the code that actually runs the G* algorithm
# on the data. 
# 
# The code above is the core of the G* algorithm. It is the code that actually runs the G* algorithm
# on the data.
class GStarPlot(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        '''
        This function is the constructor of the class
        
        :param cluster: the cluster object that this plotter is associated with
        :type cluster: BaseCluster
        '''
        super(GStarPlot,self).__init__(cluster)
        self.keyword="GStar Plot"
        self.path="{}/gstar/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        '''
        It makes a plot of the local cluster map
        
        :param year: the year of the data
        :param data_keyword: the keyword of the data set, e.g. 'GHS2000'
        :param type_keyword: 'all' or 'type'
        :param idx: the index of the cluster
        '''

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

# The GStarVPlot class is a subclass of BasePlot. 
# It inherits the BasePlot attributes and methods. 
# used to plot the variance of the G* values of the local cluster. 
# The plot is a map with the G* values of the local cluster as the color. 
# The map is generated by the get_map_with_data method of the Data class. 
# The G* values are calculated by the GStar class. 
# The G* values are stored in the local cluster. 
# The G*
class GStarVPlot(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        '''
        The __init__ function is called when an instance of the class is created. 
        used to initialize the attributes of the class. 
        
        The super function is used to call the __init__ function of the parent class. 
        
        The keyword argument is used to define the name of the class. 
        
        The path argument is used to define the path where the plot will be saved.
        
        :param cluster: the cluster object that is being used
        :type cluster: BaseCluster
        '''
        super(GStarVPlot,self).__init__(cluster)
        self.keyword="GStar Variance Plot"
        self.path="{}/gstar/{}/{}/{}.V.png"

    def _make_local_cluster_plot(self, year: int, data_keyword, type_keyword, idx):
        '''
        It makes a plot of the local cluster of a given year
        
        :param year: the year of the data
        :type year: int
        :param data_keyword: the keyword of the data set, e.g. 'GDP'
        :param type_keyword: 'all', 'type1', 'type2', 'type3', 'type4', 'type5', 'type6', 'type7',
        'type8', 'type9', 'type10', 'type11', 'type12', 'type13', 'type14', '
        :param idx: the index of the map in the list of maps
        '''

        try:

            fig,ax=plt.subplots(1,figsize=(9,12))
            map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
            y=map_with_data[map_with_data['year']==year]

            # gistar_local=self.local_cluster[data_keyword][type_keyword][year]
            file=open(self.cluster.local_cluster[data_keyword][type_keyword][year],'rb')
            gistar_local=pickle.load(file)
            file.close()

            y.assign(V=gistar_local.VG_sim).plot(column='V',ax=ax,cmap='RdYlGn_r',edgecolor=(0,0,0,1),linewidth=1,legend=True)
            ax.set_axis_off()
            plt.title('{} {} {} {} {}'.format('ratio' if self.data.load_ratio else 'raw',data_keyword,type_keyword,self.keyword,year))

            del gistar_local,map_with_data,y
            gc.collect()

        except Exception as e:
            s=str(e)
            err_file=open(f"output/log/error/_make_local_cluster_plot_{self.data.load_ratio}_{self.keyword}_{data_keyword}_{type_keyword}_{year}.err",'w')
            err_file.write(s)
            err_file.close()
            print(f"{self.keyword} in {data_keyword} {type_keyword} year {year} error, skipped it")