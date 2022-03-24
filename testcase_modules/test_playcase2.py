import gc
import os
from matplotlib import colors, pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm
from esda.getisord import G, G_Local
from esda.moran import Moran, Moran_Local
from splot._viz_utils import mask_local_auto
from testcase_modules.test_dataloading import TestDataLoading
from testcase_modules.test_dataloading2 import TestDataLoading2
from testcase_modules.test_geopackage import TestGEOPackage
from testcase_modules.test_playcase import TestPlayCase


class TestPlayCase2(TestPlayCase):
    def __init__(self,n_sim=100) -> None:
        # super(TestPlayCase2,self).__init__()
        self.n_sim=n_sim
        self.input_path="testcase_modules/testcase_input2"
        self.output_simdf_path="output/testcase_output2/dataframe_sim_output/"
        self.output_path="output/testcase_output2"
        self.list_file_name = sorted(set([i for i in os.listdir(
            self.input_path)]), key=lambda x: x.split('.')[0])
        self._check_count_files()

    def _read_file(self,dir_path,file_name):
        return pd.read_json(os.path.join(dir_path, file_name)).rename(columns={'val':'total'}).sort_values(by='NAME_1').reset_index(drop=True)

    def simulate_case(self):
        for file_name in tqdm(sorted(self.list_file_name), desc="Simulating Case"):
            input_df = self._read_file(
                self.input_path, file_name)
            geopackage_obj = TestGEOPackage(
                1, 1, "Thailand")

            dataloading_obj=TestDataLoading(geopackage_obj,input_df,100)
            self._plot_exp_dist(dataloading_obj,f"{file_name.split('.')[0]}")

            dataloading_obj=TestDataLoading2(input_df,n_sim=self.n_sim)
            dataloading_obj.to_csv(f"{self.output_simdf_path}/{file_name.split('.')[0]}")

            # file_name = file_name.split('.')[0]
            # self._plot_dist(dataloading_obj, file_name)
            # self._plot_local_gi(dataloading_obj, geopackage_obj, file_name)
            # self._plot_local_gistar(dataloading_obj, geopackage_obj, file_name)
            # self._plot_moran(dataloading_obj, geopackage_obj, file_name)
            # self._plot_geary(dataloading_obj, geopackage_obj, file_name)

            del input_df, dataloading_obj
            gc.collect()

    def action_case(self):
        geopackage_obj=TestGEOPackage(1,1,"Thailand")
        for file_name in tqdm(sorted(os.listdir(self.output_simdf_path)),desc="Actioning Case"):
            input_df=pd.read_csv(os.path.join(self.output_simdf_path,file_name))
            temp_input_df=input_df[['NAME_1']].copy()
            temp_input_df['total']=input_df.set_index("NAME_1").mean(axis=1).values
            # print(temp_input_df[['NAME_1','total']])
            dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_file_name="".join(file_name.split(".")[0])

            self._plot_mean_dist(dataloading_obj, temp_file_name)
            self._action_local_gistar(input_df,geopackage_obj,temp_file_name)
            self._plot_local_gistar(geopackage_obj,temp_file_name)
            self._action_local_moran(input_df,geopackage_obj,temp_file_name)
            self._plot_local_moran(geopackage_obj,temp_file_name)

            del input_df, temp_input_df, dataloading_obj, temp_file_name
            gc.collect()
            # break;

    def _plot_exp_dist(self,dataloading_obj: TestDataLoading, file_name):
        theta_dict={
            'low':1,
            'mid':2,
            'high':3
        }
        fig, ax = plt.subplots(1, figsize=(12, 12))
        temp_list=dataloading_obj.map_with_data['value'].map(theta_dict).values
        dataloading_obj.map_with_data.assign(value=temp_list).plot(column='value', legend=True, cmap='seismic', edgecolor=(0, 0, 0, 1), linewidth=1, ax=ax,norm=colors.PowerNorm(1,vmin=0,vmax=4))
        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name+".exp_dist.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

        del theta_dict, temp_list
        gc.collect()

    def _plot_mean_dist(self, dataloading_obj: TestDataLoading, file_name):
        fig, ax = plt.subplots(1, figsize=(12, 12))
        dataloading_obj.map_with_data.plot(column='value', legend=True, cmap='seismic', edgecolor=(0, 0, 0, 1), linewidth=1, ax=ax,norm=colors.PowerNorm(1,vmin=0,vmax=4))
        ax.set_axis_off()
        # plt.savefig(os.path.join(self.output_path, file_name.split('.')
        #             [0]+".dist.png"), dpi=300, bbox_inches='tight')
        plt.savefig(os.path.join(self.output_path, file_name+".mean_dist.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

    def _action_local_gistar(self, input_df:pd.DataFrame, geopackage_obj: TestGEOPackage, file_name):
        temp_list_df=[]
        for i in tqdm(range(self.n_sim),desc="Action Local GiStar",leave=False):
            temp_input_df=input_df[['NAME_1',f'total_{i+1}']].rename(columns={f'total_{i+1}':'total'}).copy()
            dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_list_df.append(self._action_local_gistar_one(dataloading_obj,geopackage_obj).rename(columns={'cl':f'cl_{i+1}'}))
        gistar_df=pd.concat(temp_list_df,axis=1)
        # print(gistar_df.apply(pd.Series.value_counts,axis=1))
        gistar_df['most_cl']=gistar_df.apply(pd.Series.value_counts,axis=1).idxmax(axis=1).values
        gistar_df=gistar_df.reset_index()
        gistar_df.to_csv(os.path.join(self.output_path,file_name+".gistar.csv"),index=False)
        
        del temp_list_df,gistar_df,temp_input_df,dataloading_obj
        gc.collect()
        
    def _action_local_gistar_one(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage):
        gistar_local = G_Local(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), star=True, transform="B", permutations=999)

        hotspot95 = (gistar_local.Zs > 0) & (gistar_local.p_sim < 0.05)
        notsig = (gistar_local.p_sim >= 0.05)
        coldspot95 = (gistar_local.Zs < 0) & (gistar_local.p_sim < 0.05)
        hotcoldspot = hotspot95*1+coldspot95*2
        spots = ['not-significant', 'hotspot','coldspot']
        labels = [spots[i] for i in hotcoldspot]
        return dataloading_obj.map_with_data[['NAME_1']].assign(cl=labels).set_index('NAME_1')

    def _plot_local_gistar(self, geopackage_obj: TestGEOPackage, file_name):
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+".gistar.csv"))[['NAME_1','most_cl']]
        color_list = ['lightgrey', 'red', 'blue'][::-1]
        spots = ['not-significant', 'hotspot','coldspot']
        hmap = colors.ListedColormap(color_list)
        hotcoldspot=input_df['most_cl'].map({
            'not-significant':0,
            'hotspot':1,
            'coldspot':2
        }).values
        color_labels = [color_list[::-1][i] for i in hotcoldspot]
        dataloading_obj=TestDataLoading(geopackage_obj,input_df.rename(columns={'most_cl':'total'}),100)

        fig, ax = plt.subplots(1, figsize=(12, 12))

        dataloading_obj.map_with_data.assign(spot=hotcoldspot,cl=input_df['most_cl']).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='black', cmap=hmap, k=3, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')
                    [0]+".gistar.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _action_local_moran(self, input_df:pd.DataFrame, geopackage_obj: TestGEOPackage, file_name):
        temp_list_df=[]
        for i in tqdm(range(self.n_sim),desc="Action Local Moran",leave=False):
            temp_input_df=input_df[['NAME_1',f'total_{i+1}']].rename(columns={f'total_{i+1}':'total'}).copy()
            dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_list_df.append(self._action_local_moran_one(dataloading_obj,geopackage_obj).rename(columns={'cl':f'cl_{i+1}'}))
        localmoran_df=pd.concat(temp_list_df,axis=1)
        # print(gistar_df.apply(pd.Series.value_counts,axis=1))
        localmoran_df['most_cl']=localmoran_df.apply(pd.Series.value_counts,axis=1).idxmax(axis=1).values
        localmoran_df=localmoran_df.reset_index()
        localmoran_df.to_csv(os.path.join(self.output_path,file_name+".localmoran.csv"),index=False)
        
        del temp_list_df,localmoran_df,temp_input_df,dataloading_obj
        gc.collect()

    def _action_local_moran_one(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage):
        moran_local = Moran_Local(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), transformation="B", permutations=999)
        return dataloading_obj.map_with_data[['NAME_1']].assign(cl=mask_local_auto(moran_local, p=0.05)[3]).set_index('NAME_1')

    def _plot_local_moran(self, geopackage_obj: TestGEOPackage, file_name):
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+".localmoran.csv"))[['NAME_1','most_cl']]
        color_list = ['red', 'darkturquoise', 'orange', 'blue','lightgrey']
        spots = ['HH','LH','HL','LL','ns'][::-1]
        hmap = colors.ListedColormap(color_list)
        hotcoldspot=input_df['most_cl'].map({
            'HH':0,
            'LH':1,
            'HL':2,
            'LL':3,
            'ns':4
        }).values
        color_labels = [color_list[i] for i in hotcoldspot]
        dataloading_obj=TestDataLoading(geopackage_obj,input_df.rename(columns={'most_cl':'total'}),100)

        fig, ax = plt.subplots(1, figsize=(12, 12))

        dataloading_obj.map_with_data.assign(spot=hotcoldspot,cl=input_df['most_cl']).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='black', cmap=hmap, k=5, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')
                    [0]+".localmoran.png"), dpi=300, bbox_inches='tight')
        plt.close('all')