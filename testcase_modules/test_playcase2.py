import gc
import os
from matplotlib import colors, pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm
from esda.getisord import G, G_Local
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

            dataloading_obj=TestDataLoading2(input_df,n_sim=100)
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
        for file_name in tqdm(os.listdir(self.output_simdf_path),desc="Actioning Case"):
            input_df=pd.read_csv(os.path.join(self.output_simdf_path,file_name))
            temp_input_df=input_df[['NAME_1']].copy()
            temp_input_df['total']=input_df.set_index("NAME_1").mean(axis=1).values
            # print(temp_input_df[['NAME_1','total']])
            dataloading_obj=TestDataLoading(geopackage_obj,temp_input_df,100)
            temp_file_name="".join(file_name.split(".")[0])

            self._plot_mean_dist(dataloading_obj, temp_file_name)

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

    def _plot_local_gistar(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage, file_name):

        gistar_local = G_Local(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), star=True, transform="B", permutations=999)

        hotspot90 = (gistar_local.Zs > 0) & (gistar_local.p_sim <= 0.1)
        hotspot95 = (gistar_local.Zs > 0) & (gistar_local.p_sim <= 0.05)
        hotspot99 = (gistar_local.Zs > 0) & (gistar_local.p_sim <= 0.01)
        hotspot90 = hotspot90 & ~hotspot95
        hotspot95 = hotspot95 & ~hotspot99
        notsig = (gistar_local.p_sim > 0.1)
        coldspot90 = (gistar_local.Zs < 0) & (gistar_local.p_sim <= 0.1)
        coldspot95 = (gistar_local.Zs < 0) & (gistar_local.p_sim <= 0.05)
        coldspot99 = (gistar_local.Zs < 0) & (gistar_local.p_sim <= 0.01)
        coldspot90 = coldspot90 & ~coldspot95
        coldspot95 = coldspot95 & ~coldspot99
        hotcoldspot = hotspot99*1+hotspot95*2+hotspot90 * \
            3+coldspot90*4+coldspot95*5+coldspot99*6
        spots = ['not-significant', 'hotspot-0.01', 'hotspot-0.05',
                 'hotspot-0.1', 'coldspot-0.1', 'coldspot-0.05', 'coldspot-0.01']
        labels = [spots[i] for i in hotcoldspot]
        color_list = ['lightgrey', 'red',
                      (1, 0.3, 0.3), (1, 0.6, 0.6), (0.6, 0.6, 1), (0.3, 0.3, 1), 'blue'][::-1]
        hmap = colors.ListedColormap(color_list)
        color_labels = [color_list[::-1][i] for i in hotcoldspot]

        fig, ax = plt.subplots(1, figsize=(12, 12))
        dataloading_obj.map_with_data.assign(gistar_Z=gistar_local.Zs, gistar_p_value=gistar_local.p_sim, cl=labels)[
            [f'NAME_{dataloading_obj.num_layer}', 'gistar_Z', 'gistar_p_value', 'cl']].round(4).to_csv(os.path.join(self.output_path, file_name.split('.')[0]+".gistar.csv"), index=False)
        dataloading_obj.map_with_data.assign(cl=labels).assign(spot=hotcoldspot).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='white', cmap=hmap, k=7, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join(self.output_path, file_name.split('.')
                    [0]+".gistar.png"), dpi=300, bbox_inches='tight')
        plt.close('all')