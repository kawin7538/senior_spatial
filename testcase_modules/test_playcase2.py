import gc
import os
from matplotlib import colors, pyplot as plt
import folium
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import time
import io
from PIL import Image
import numpy as np
import pandas as pd
import geopandas
import cartopy.crs as ccrs

from tqdm import tqdm
from esda.getisord import G, G_Local
from esda.moran import Moran, Moran_Local
from splot._viz_utils import mask_local_auto
from sklearn.metrics import classification_report,accuracy_score
from testcase_modules.test_custom_confusion_matrix import CustomConfusionMatrix
from testcase_modules.test_dataloading import TestDataLoading
from testcase_modules.test_dataloading2 import TestDataLoading2
from testcase_modules.test_geopackage import TestGEOPackage
from testcase_modules.test_playcase import TestPlayCase

import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

from rpy2.robjects.conversion import localconverter

r = robjects.r
r['source']('R_sources/_test_playcase2_source.r')

r_run_besag=robjects.globalenv['run_besag']
r_run_bym=robjects.globalenv['run_bym']
r_run_satscan=robjects.globalenv['run_satscan']

class TestPlayCase2(TestPlayCase):
    def __init__(self,n_sim=100,high_mode=3) -> None:
        # super(TestPlayCase2,self).__init__()
        assert high_mode in [2,3], "High Mode should be 2 or 3"
        self.n_sim=n_sim
        self.high_mode=high_mode
        self.input_path="testcase_modules/testcase_input2"
        self.output_simdf_path=f"output/testcase_output2/high{self.high_mode}/dataframe_sim_output/"
        self.output_path=f"output/testcase_output2/high{self.high_mode}"

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            print(f'\t{self.output_path} not existed, create it')
        if not os.path.exists(self.output_simdf_path):
            os.makedirs(self.output_simdf_path)
            print(f'\t{self.output_simdf_path} not existed, create it')

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
            self._action_besag(input_df,geopackage_obj,temp_file_name,1)
            self._plot_besag(geopackage_obj,temp_file_name,1)
            self._action_besag(input_df,geopackage_obj,temp_file_name,2)
            self._plot_besag(geopackage_obj,temp_file_name,2)
            self._action_bym(input_df,geopackage_obj,temp_file_name,1)
            self._plot_bym(geopackage_obj,temp_file_name,1)
            self._action_bym(input_df,geopackage_obj,temp_file_name,2)
            self._plot_bym(geopackage_obj,temp_file_name,2)
            self._action_satscan(input_df,geopackage_obj,temp_file_name)
            self._plot_satscan(geopackage_obj,temp_file_name)
            # self._plot_satscan_center(geopackage_obj,temp_file_name)

            del input_df, temp_input_df, dataloading_obj, temp_file_name
            gc.collect()

    def _plot_exp_dist(self,dataloading_obj: TestDataLoading, file_name):
        if self.high_mode==3:
            theta_dict={
                'low':1,
                'mid':2,
                'high':3
            }
            vmax=4
        else:
            theta_dict={
                'low':1,
                'mid':1,
                'high':2
            }
            vmax=3
        fig, ax = plt.subplots(1, figsize=(12, 12))
        temp_list=dataloading_obj.map_with_data['value'].map(theta_dict).values
        dataloading_obj.map_with_data.assign(value=temp_list).plot(column='value', legend=True, cmap='seismic', edgecolor=(0, 0, 0, 1), linewidth=1, ax=ax,norm=colors.PowerNorm(1,vmin=0,vmax=vmax))
        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name+".exp_dist.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

        del theta_dict, temp_list
        gc.collect()

    def _plot_mean_dist(self, dataloading_obj: TestDataLoading, file_name):
        if self.high_mode==3:
            vmax=4
        else:
            vmax=3
        fig, ax = plt.subplots(1, figsize=(12, 12))
        dataloading_obj.map_with_data.plot(column='value', legend=True, cmap='seismic', edgecolor=(0, 0, 0, 1), linewidth=1, ax=ax,norm=colors.PowerNorm(1,vmin=0,vmax=vmax))
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

        hotspot95 = (gistar_local.Zs > 0) & (gistar_local.p_sim <= 0.05)
        notsig = (gistar_local.p_sim > 0.05)
        coldspot95 = (gistar_local.Zs < 0) & (gistar_local.p_sim <= 0.05)
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
                    [0]+".gistar.png"), dpi=150, bbox_inches='tight')
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
                    [0]+".localmoran.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

    def _action_besag(self, input_df:pd.DataFrame, geopackage_obj: TestGEOPackage, file_name,q: int):
        temp_list_df=[]
        for i in tqdm(range(self.n_sim),desc=f"Action BESAG q={q}",leave=False):
            temp_input_df=input_df[['NAME_1',f'total_{i+1}']].rename(columns={f'total_{i+1}':'total'}).copy()
            # dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_list_df.append(self._action_besag_one(temp_input_df,q).rename(columns={'cl':f'cl_{i+1}'}))
        besag_df=pd.concat(temp_list_df,axis=1)
        # print(gistar_df.apply(pd.Series.value_counts,axis=1))
        besag_df['most_cl']=besag_df.apply(pd.Series.value_counts,axis=1).idxmax(axis=1).values
        besag_df=besag_df.reset_index()
        besag_df.to_csv(os.path.join(self.output_path,file_name+f".besag-q{q}.csv"),index=False)
        del temp_list_df,besag_df,temp_input_df
        gc.collect()

    def _action_besag_one(self, input_df:pd.DataFrame,q:int) -> pd.DataFrame:
        with localconverter(robjects.default_converter + pandas2ri.converter):
            input_df_r = robjects.conversion.py2rpy(input_df)
        ans_df_r=r_run_besag(input_df_r,q)
        with localconverter(robjects.default_converter + pandas2ri.converter):
            ans_df = robjects.conversion.rpy2py(ans_df_r)
        return ans_df[['NAME_1','cl']].set_index("NAME_1").replace({1:'hotspot',0:'not-hotspot'})

    def _plot_besag(self, geopackage_obj: TestGEOPackage, file_name,q:int):
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+f".besag-q{q}.csv"))[['NAME_1','most_cl']]
        color_list = ['red', 'lightgrey']
        spots = ['hotspot','not-hotspot'][::-1]
        hmap = colors.ListedColormap(color_list)
        hotcoldspot=input_df['most_cl'].map({
            'hotspot':0,
            'not-hotspot':1
        }).values
        color_labels = [color_list[i] for i in hotcoldspot]
        dataloading_obj=TestDataLoading(geopackage_obj,input_df.rename(columns={'most_cl':'total'}),100)

        fig, ax = plt.subplots(1, figsize=(12, 12))

        dataloading_obj.map_with_data.assign(spot=hotcoldspot,cl=input_df['most_cl']).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='black', cmap=hmap, k=2, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')
                    [0]+f".besag-q{q}.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

    def _action_bym(self, input_df:pd.DataFrame, geopackage_obj: TestGEOPackage, file_name,q:int):
        temp_list_df=[]
        for i in tqdm(range(self.n_sim),desc=f"Action BYM q={q}",leave=False):
            temp_input_df=input_df[['NAME_1',f'total_{i+1}']].rename(columns={f'total_{i+1}':'total'}).copy()
            # dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_list_df.append(self._action_bym_one(temp_input_df,q).rename(columns={'cl':f'cl_{i+1}'}))
        bym_df=pd.concat(temp_list_df,axis=1)
        # print(gistar_df.apply(pd.Series.value_counts,axis=1))
        bym_df['most_cl']=bym_df.apply(pd.Series.value_counts,axis=1).idxmax(axis=1).values
        bym_df=bym_df.reset_index()
        bym_df.to_csv(os.path.join(self.output_path,file_name+f".bym-q{q}.csv"),index=False)
        del temp_list_df,bym_df,temp_input_df
        gc.collect()

    def _action_bym_one(self, input_df:pd.DataFrame,q:int) -> pd.DataFrame:
        with localconverter(robjects.default_converter + pandas2ri.converter):
            input_df_r = robjects.conversion.py2rpy(input_df)
        ans_df_r=r_run_bym(input_df_r,q)
        with localconverter(robjects.default_converter + pandas2ri.converter):
            ans_df = robjects.conversion.rpy2py(ans_df_r)
        return ans_df[['NAME_1','cl']].set_index("NAME_1").replace({1:'hotspot',0:'not-hotspot'})

    def _plot_bym(self, geopackage_obj: TestGEOPackage, file_name,q:int):
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+f".bym-q{q}.csv"))[['NAME_1','most_cl']]
        color_list = ['red', 'lightgrey']
        spots = ['hotspot','not-hotspot'][::-1]
        hmap = colors.ListedColormap(color_list)
        hotcoldspot=input_df['most_cl'].map({
            'hotspot':0,
            'not-hotspot':1
        }).values
        color_labels = [color_list[i] for i in hotcoldspot]
        dataloading_obj=TestDataLoading(geopackage_obj,input_df.rename(columns={'most_cl':'total'}),100)

        fig, ax = plt.subplots(1, figsize=(12, 12))

        dataloading_obj.map_with_data.assign(spot=hotcoldspot,cl=input_df['most_cl']).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='black', cmap=hmap, k=2, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')
                    [0]+f".bym-q{q}.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

    def _action_satscan(self, input_df:pd.DataFrame, geopackage_obj: TestGEOPackage, file_name):
        temp_list_df=[]
        temp_list_center_df=[]
        for i in tqdm(range(self.n_sim),desc="Action SaTScan",leave=False):
            temp_input_df=input_df[['NAME_1',f'total_{i+1}']].rename(columns={f'total_{i+1}':'total'}).copy()
            # dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_df, temp_center_df=self._action_satscan_one(temp_input_df)
            # temp_list_df.append(self._action_satscan_one(temp_input_df).rename(columns={'cl':f'cl_{i+1}'}))
            temp_list_df.append(temp_df.rename(columns={'cl':f'cl_{i+1}'}))
            temp_center_df['n']=i+1
            temp_list_center_df.append(temp_center_df)
        satscan_df=pd.concat(temp_list_df,axis=1)
        # print(gistar_df.apply(pd.Series.value_counts,axis=1))
        satscan_df['most_cl']=satscan_df.apply(pd.Series.value_counts,axis=1).idxmax(axis=1).values
        satscan_df=satscan_df.reset_index()
        satscan_df.to_csv(os.path.join(self.output_path,file_name+".satscan.csv"),index=False)

        satscan_center_df=pd.concat(temp_list_center_df,axis=0)
        satscan_center_df=satscan_center_df.groupby(["LOC_ID"]).agg({'RADIUS':np.mean,'X':np.mean,'Y':np.mean}).reset_index()
        satscan_center_df.to_csv(os.path.join(self.output_path,file_name+".satscan.center.csv"),index=False)
        del temp_list_df,satscan_df,temp_input_df,temp_df,temp_center_df,satscan_center_df
        gc.collect()

    def _action_satscan_one(self, input_df:pd.DataFrame) -> pd.DataFrame:
        with localconverter(robjects.default_converter + pandas2ri.converter):
            input_df_r = robjects.conversion.py2rpy(input_df)
        ans_df_r,cluster_center_r=r_run_satscan(input_df_r)
        with localconverter(robjects.default_converter + pandas2ri.converter):
            ans_df = robjects.conversion.rpy2py(ans_df_r)
        with localconverter(robjects.default_converter + pandas2ri.converter):
            cluster_center = robjects.conversion.rpy2py(cluster_center_r)
        return ans_df[['NAME_1','cl']].set_index("NAME_1").replace({1:'hotspot',0:'not-hotspot'}), \
            cluster_center[['LOC_ID','P_VALUE','X','Y','RADIUS']]

    def _plot_satscan(self, geopackage_obj: TestGEOPackage, file_name):
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+".satscan.csv"))[['NAME_1','most_cl']]
        color_list = ['red', 'lightgrey']
        spots = ['hotspot','not-hotspot'][::-1]
        hmap = colors.ListedColormap(color_list)
        hotcoldspot=input_df['most_cl'].map({
            'hotspot':0,
            'not-hotspot':1
        }).values
        color_labels = [color_list[i] for i in hotcoldspot]
        dataloading_obj=TestDataLoading(geopackage_obj,input_df.rename(columns={'most_cl':'total'}),100)

        fig, ax = plt.subplots(1, figsize=(12, 12))

        dataloading_obj.map_with_data.assign(spot=hotcoldspot,cl=input_df['most_cl']).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='black', cmap=hmap, k=2, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')[0]+".satscan.png"), dpi=150, bbox_inches='tight')
        plt.close('all')

    def _plot_satscan_center(self, geopackage_obj: TestGEOPackage, file_name):
        #unfinished
        input_df=pd.read_csv(os.path.join(self.output_path,file_name+".satscan.csv"))[['NAME_1','most_cl']]
        temp_map=geopackage_obj.get_map()
        temp_map=temp_map.to_crs(3395)
        temp_map['cl']=input_df['most_cl']
        # fig, ax = plt.subplots(1, figsize=(12, 12))
        fig=plt.figure(figsize=(12, 12))
        ax=fig.add_subplot(111,projection=ccrs.epsg(3395))
        temp_map.plot(column="cl",ax=ax)
        # ax.tissot(radius_deg=2.5,lons=[100,],lats=[13,])
        ax.tissot(lon_0=100, lat_0=13, radius_deg=2.5)
        # ax.scatter([100,],[13,],s=2.5)
        # plt.savefig(os.path.join(self.output_path,file_name+".satscan.center.png"))
        # plt.close('all')
        fig.savefig(os.path.join(self.output_path,file_name+".satscan.center.png"))
        fig.close('all')
        

    def evaluate_case(self):
        geopackage_obj=TestGEOPackage(1,1,"Thailand")
        for file_name in tqdm(self.list_file_name,desc="Evaluating Case",leave=True):
            temp_file_name=file_name.split('.')[0]
            # input_df=pd.read_json(os.path.join(self.input_path,file_name))
            true_df=self._read_file(self.input_path,file_name)
            self._evaluate_local_gistar(true_df.copy(),temp_file_name)
            self._plot_evaluate_local_gistar(geopackage_obj,temp_file_name)
            self._evaluate_local_moran(true_df.copy(),temp_file_name)
            self._plot_evaluate_local_moran(geopackage_obj,temp_file_name)
            self._evaluate_besag(true_df.copy(),temp_file_name,1)
            self._plot_evaluate_besag(geopackage_obj,temp_file_name,1)
            self._evaluate_besag(true_df.copy(),temp_file_name,2)
            self._plot_evaluate_besag(geopackage_obj,temp_file_name,2)
            self._evaluate_bym(true_df.copy(),temp_file_name,1)
            self._plot_evaluate_bym(geopackage_obj,temp_file_name,1)
            self._evaluate_bym(true_df.copy(),temp_file_name,2)
            self._plot_evaluate_bym(geopackage_obj,temp_file_name,2)
            self._evaluate_satscan(true_df.copy(),temp_file_name)
            self._plot_evaluate_satscan(geopackage_obj,temp_file_name)
            # break;
        
        del geopackage_obj
        gc.collect()

    def _evaluate_local_gistar(self,true_df,temp_file_name):
        pred_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.gistar.csv'))
        pred_df=pred_df.drop(columns=['most_cl','NAME_1'])
        true_df['total']=true_df['total'].map({'mid':'not-hotspot','high':'hotspot','low':'not-hotspot'})
        y_true=true_df['total'].values
        pred_df=pred_df.replace({
            'not-significant':'not-hotspot',
            'coldspot':'not-hotspot',
            'hotspot':'hotspot'
        })
        y_pred=pred_df.values

        metrics_df=pd.DataFrame(true_df['NAME_1'])
        metrics_df[CustomConfusionMatrix.get_column_names()]=0
        for i in tqdm(range(len(y_true)),desc="Evaluate GiStar",leave=False):
            cm=CustomConfusionMatrix(np.array([y_true[i]]*self.n_sim),y_pred[i],labels=['not-hotspot','hotspot'])
            metrics_df.iloc[i,1:]=cm.get_values()
        metrics_df.to_csv(os.path.join(self.output_path,temp_file_name+'.gistar.metrics.csv'),index=False)
        
        del pred_df,y_true,y_pred,metrics_df
        gc.collect()

    def _plot_evaluate_local_gistar(self,geopackage_obj:TestGEOPackage,temp_file_name):

        def _plot_evaluate_one(keyword,cmaps):
            fig, ax = plt.subplots(1, figsize=(12, 12))
            temp_map_with_data.assign(value=metrics_df[keyword].values).plot(ax=ax,column='value',cmap=cmaps,norm=colors.PowerNorm(1,vmin=0,vmax=1),legend=True)
            temp_map_with_data.boundary.plot(edgecolor='black',ax=ax)
            ax.set_axis_off()
            plt.savefig(os.path.join(self.output_path, temp_file_name+f".gistar.metrics.{keyword}.png"), dpi=150, bbox_inches='tight')
            plt.close('all')    

        metrics_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.gistar.metrics.csv'))
        temp_map_with_data=geopackage_obj.get_map()
        _plot_evaluate_one('precision','Reds')

        _plot_evaluate_one('recall','Oranges')

        _plot_evaluate_one('specificity','Blues')

        _plot_evaluate_one('npv','Purples')

        _plot_evaluate_one('accuracy','Greens')

        del temp_map_with_data,metrics_df
        gc.collect()

    def _evaluate_local_moran(self,true_df,temp_file_name):
        pred_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.localmoran.csv'))
        pred_df=pred_df.drop(columns=['most_cl','NAME_1'])
        true_df['total']=true_df['total'].map({
            'mid':'not-hotspot',
            'high':'hotspot',
            'low':'not-hotspot'})
        y_true=true_df['total'].values
        pred_df=pred_df.replace({
            'ns':'not-hotspot',
            'LH':'not-hotspot',
            'LL':'not-hotspot',
            'HH':'hotspot',
            'HL':'hotspot'
        })
        y_pred=pred_df.values

        metrics_df=pd.DataFrame(true_df['NAME_1'])
        metrics_df[CustomConfusionMatrix.get_column_names()]=0
        for i in tqdm(range(len(y_true)),desc="Evaluate localmoran",leave=False):
            cm=CustomConfusionMatrix(np.array([y_true[i]]*self.n_sim),y_pred[i],labels=['not-hotspot','hotspot'])
            metrics_df.iloc[i,1:]=cm.get_values()
        metrics_df.to_csv(os.path.join(self.output_path,temp_file_name+'.localmoran.metrics.csv'),index=False)
        
        del pred_df,y_true,y_pred,metrics_df
        gc.collect()

    def _plot_evaluate_local_moran(self,geopackage_obj:TestGEOPackage,temp_file_name):

        def _plot_evaluate_one(keyword,cmaps):
            fig, ax = plt.subplots(1, figsize=(12, 12))
            temp_map_with_data.assign(value=metrics_df[keyword].values).plot(ax=ax,column='value',cmap=cmaps,norm=colors.PowerNorm(1,vmin=0,vmax=1),legend=True)
            temp_map_with_data.boundary.plot(edgecolor='black',ax=ax)
            ax.set_axis_off()
            plt.savefig(os.path.join(self.output_path, temp_file_name+f".localmoran.metrics.{keyword}.png"), dpi=150, bbox_inches='tight')
            plt.close('all')    

        metrics_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.localmoran.metrics.csv'))
        temp_map_with_data=geopackage_obj.get_map()
        _plot_evaluate_one('precision','Reds')

        _plot_evaluate_one('recall','Oranges')

        _plot_evaluate_one('specificity','Blues')

        _plot_evaluate_one('npv','Purples')

        _plot_evaluate_one('accuracy','Greens')

        del temp_map_with_data,metrics_df
        gc.collect()

    def _evaluate_besag(self,true_df,temp_file_name,q:int):
        pred_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+f'.besag-q{q}.csv'))
        pred_df=pred_df.drop(columns=['most_cl','NAME_1'])
        true_df['total']=true_df['total'].map({
            'mid':'not-hotspot',
            'high':'hotspot',
            'low':'not-hotspot'})
        y_true=true_df['total'].values
        # pred_df=pred_df.replace({
        #     'not-hotspot':'not-hotspot',
        #     'hotspot':'hotspot'
        # })
        y_pred=pred_df.values

        metrics_df=pd.DataFrame(true_df['NAME_1'])
        metrics_df[CustomConfusionMatrix.get_column_names()]=0
        for i in tqdm(range(len(y_true)),desc=f"Evaluate BESAG q={q}",leave=False):
            cm=CustomConfusionMatrix(np.array([y_true[i]]*self.n_sim),y_pred[i],labels=['not-hotspot','hotspot'])
            metrics_df.iloc[i,1:]=cm.get_values()
        metrics_df.to_csv(os.path.join(self.output_path,temp_file_name+f'.besag-q{q}.metrics.csv'),index=False)
        
        del pred_df,y_true,y_pred,metrics_df
        gc.collect()

    def _plot_evaluate_besag(self,geopackage_obj:TestGEOPackage,temp_file_name,q:int):

        def _plot_evaluate_one(keyword,cmaps):
            fig, ax = plt.subplots(1, figsize=(12, 12))
            temp_map_with_data.assign(value=metrics_df[keyword].values).plot(ax=ax,column='value',cmap=cmaps,norm=colors.PowerNorm(1,vmin=0,vmax=1),legend=True)
            temp_map_with_data.boundary.plot(edgecolor='black',ax=ax)
            ax.set_axis_off()
            plt.savefig(os.path.join(self.output_path, temp_file_name+f".besag-q{q}.metrics.{keyword}.png"), dpi=150, bbox_inches='tight')
            plt.close('all')    

        metrics_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+f'.besag-q{q}.metrics.csv'))
        temp_map_with_data=geopackage_obj.get_map()
        _plot_evaluate_one('precision','Reds')

        _plot_evaluate_one('recall','Oranges')

        _plot_evaluate_one('specificity','Blues')

        _plot_evaluate_one('npv','Purples')

        _plot_evaluate_one('accuracy','Greens')

        del temp_map_with_data,metrics_df
        gc.collect()

    def _evaluate_bym(self,true_df,temp_file_name,q:int):
        pred_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+f'.bym-q{q}.csv'))
        pred_df=pred_df.drop(columns=['most_cl','NAME_1'])
        true_df['total']=true_df['total'].map({
            'mid':'not-hotspot',
            'high':'hotspot',
            'low':'not-hotspot'})
        y_true=true_df['total'].values
        # pred_df=pred_df.replace({
        #     'not-hotspot':'not-hotspot',
        #     'hotspot':'hotspot'
        # })
        y_pred=pred_df.values

        metrics_df=pd.DataFrame(true_df['NAME_1'])
        metrics_df[CustomConfusionMatrix.get_column_names()]=0
        for i in tqdm(range(len(y_true)),desc=f"Evaluate BYM q={q}",leave=False):
            cm=CustomConfusionMatrix(np.array([y_true[i]]*self.n_sim),y_pred[i],labels=['not-hotspot','hotspot'])
            metrics_df.iloc[i,1:]=cm.get_values()
        metrics_df.to_csv(os.path.join(self.output_path,temp_file_name+f'.bym-q{q}.metrics.csv'),index=False)
        
        del pred_df,y_true,y_pred,metrics_df
        gc.collect()

    def _plot_evaluate_bym(self,geopackage_obj:TestGEOPackage,temp_file_name,q:int):

        def _plot_evaluate_one(keyword,cmaps):
            fig, ax = plt.subplots(1, figsize=(12, 12))
            temp_map_with_data.assign(value=metrics_df[keyword].values).plot(ax=ax,column='value',cmap=cmaps,norm=colors.PowerNorm(1,vmin=0,vmax=1),legend=True)
            temp_map_with_data.boundary.plot(edgecolor='black',ax=ax)
            ax.set_axis_off()
            plt.savefig(os.path.join(self.output_path, temp_file_name+f".bym-q{q}.metrics.{keyword}.png"), dpi=150, bbox_inches='tight')
            plt.close('all')    

        metrics_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+f'.bym-q{q}.metrics.csv'))
        temp_map_with_data=geopackage_obj.get_map()
        _plot_evaluate_one('precision','Reds')

        _plot_evaluate_one('recall','Oranges')

        _plot_evaluate_one('specificity','Blues')

        _plot_evaluate_one('npv','Purples')

        _plot_evaluate_one('accuracy','Greens')

        del temp_map_with_data,metrics_df
        gc.collect()

    def _evaluate_satscan(self,true_df,temp_file_name):
        pred_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.satscan.csv'))
        pred_df=pred_df.drop(columns=['most_cl','NAME_1'])
        true_df['total']=true_df['total'].map({
            'mid':'not-hotspot',
            'high':'hotspot',
            'low':'not-hotspot'})
        y_true=true_df['total'].values
        # pred_df=pred_df.replace({
        #     'not-hotspot':'not-hotspot',
        #     'hotspot':'hotspot'
        # })
        y_pred=pred_df.values

        metrics_df=pd.DataFrame(true_df['NAME_1'])
        metrics_df[CustomConfusionMatrix.get_column_names()]=0
        for i in tqdm(range(len(y_true)),desc="Evaluate SaTScan",leave=False):
            cm=CustomConfusionMatrix(np.array([y_true[i]]*self.n_sim),y_pred[i],labels=['not-hotspot','hotspot'])
            metrics_df.iloc[i,1:]=cm.get_values()
        metrics_df.to_csv(os.path.join(self.output_path,temp_file_name+'.satscan.metrics.csv'),index=False)
        
        del pred_df,y_true,y_pred,metrics_df
        gc.collect()

    def _plot_evaluate_satscan(self,geopackage_obj:TestGEOPackage,temp_file_name):

        def _plot_evaluate_one(keyword,cmaps):
            fig, ax = plt.subplots(1, figsize=(12, 12))
            temp_map_with_data.assign(value=metrics_df[keyword].values).plot(ax=ax,column='value',cmap=cmaps,norm=colors.PowerNorm(1,vmin=0,vmax=1),legend=True)
            temp_map_with_data.boundary.plot(edgecolor='black',ax=ax)
            ax.set_axis_off()
            plt.savefig(os.path.join(self.output_path, temp_file_name+f".satscan.metrics.{keyword}.png"), dpi=150, bbox_inches='tight')
            plt.close('all')    

        metrics_df=pd.read_csv(os.path.join(self.output_path,temp_file_name+'.satscan.metrics.csv'))
        temp_map_with_data=geopackage_obj.get_map()
        _plot_evaluate_one('precision','Reds')

        _plot_evaluate_one('recall','Oranges')

        _plot_evaluate_one('specificity','Blues')

        _plot_evaluate_one('npv','Purples')

        _plot_evaluate_one('accuracy','Greens')

        del temp_map_with_data,metrics_df
        gc.collect()