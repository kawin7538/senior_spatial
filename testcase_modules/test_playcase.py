import os
import gc
from esda.getisord import G, G_Local
from esda.moran import Moran, Moran_Local
from esda.geary import Geary
from esda import Geary_Local
from libpysal.weights.weights import W
from splot.libpysal import plot_spatial_weights
from splot._viz_utils import mask_local_auto
from splot.esda import (lisa_cluster, moran_scatterplot,
                        plot_local_autocorrelation)

from matplotlib import colors, pyplot as plt
import pandas as pd
from tqdm import tqdm

from data_loading import geopackage
from testcase_modules.test_dataloading import TestDataLoading
from testcase_modules.test_geopackage import TestGEOPackage


class TestPlayCase:
    def __init__(self, full_precision=True, startwith100=True) -> None:
        print("Running Testcase with full_precision =", full_precision)
        self.full_precision = full_precision
        self.startwith100=startwith100
        self.list_file_name = sorted(set([i for i in os.listdir("testcase_modules/testcase_input")]), key=lambda x: int(x.split('.')[0])%100)
        self._check_count_files()
        self._play_case()

    def _check_count_files(self):
        number_files = len(self.list_file_name)
        print(f"{number_files} test case(s).")

    def _play_case(self):
        if self.full_precision:
            if self.startwith100:
                list_precision = [100, 95, 90, 75]
            else:
                list_precision=[90,75]
        else:
            list_precision = [100]
        for precision in list_precision:
            for file_name in tqdm(sorted(self.list_file_name), desc=f"Precision{precision}"):
                input_value = self._read_file(
                    "testcase_modules/testcase_input", file_name)
                num_layer, selected_layer, selected_name = input_value[0][:-1]
                geopackage_obj = TestGEOPackage(
                    num_layer, selected_layer, selected_name)
                # dataloading_obj=TestDataLoading(geopackage_obj,input_value[1],input_value[0][-1])
                dataloading_obj = TestDataLoading(
                    geopackage_obj, input_value[1], precision)
                dataloading_obj.to_csv(os.path.join(
                    "output/testcase_output", file_name.split('.')[0]+f"_precision{precision}"+".csv"))

                file_name = file_name.split('.')[0]+f"_precision{precision}"
                self._plot_dist(dataloading_obj, file_name)
                self._plot_map_with_name(dataloading_obj, file_name, num_layer)
                self._plot_weight(geopackage_obj, file_name)
                self._plot_local_gi(dataloading_obj, geopackage_obj, file_name)
                self._plot_local_gistar(
                    dataloading_obj, geopackage_obj, file_name)
                self._plot_moran(dataloading_obj, geopackage_obj, file_name)
                self._plot_geary(dataloading_obj, geopackage_obj, file_name)

                del input_value, num_layer, selected_layer, selected_name, geopackage_obj, dataloading_obj
                gc.collect()
                # break;
            # break;

    def _read_file(self, dir_path, file_name):
        with open(os.path.join(dir_path, file_name), "r") as file:
            temp_ans = file.readlines()
            for i in [0, 1]:
                temp_ans[i] = temp_ans[i].replace('\n', '').split(',')
                temp_ans[i] = [int(item) if item.isdigit()
                               else item for item in temp_ans[i]]
            return temp_ans

    def _plot_map_with_name(self, dataloading_obj: TestDataLoading, file_name, num_layer):
        fig, ax = plt.subplots(1, figsize=(12, 12))
        temp_map_with_data = dataloading_obj.map_with_data.copy()
        # print(temp_map_with_data)
        # print(temp_map_with_data.columns)
        # print(temp_map_with_data[f'NAME_{num_layer}'])
        temp_map_with_data.apply(lambda x: ax.annotate(
            s=x[f'NAME_{num_layer}'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=20), axis=1)
        temp_map_with_data.boundary.plot(ax=ax, color='Black', linewidth=.4)
        temp_map_with_data.plot(ax=ax, cmap='Pastel2')
        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                    [0]+".name.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _plot_weight(self, geopackage_obj: TestGEOPackage, file_name):
        fig, ax = plt.subplots(1, figsize=(12, 12))
        plot_spatial_weights(geopackage_obj.w, geopackage_obj.map, ax=ax)
        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                    [0]+".weight.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _plot_dist(self, dataloading_obj: TestDataLoading, file_name):
        fig, ax = plt.subplots(1, figsize=(12, 12))
        dataloading_obj.map_with_data.plot(
            column='value', legend=True, cmap='Oranges', edgecolor=(0, 0, 0, 1), linewidth=1, ax=ax)
        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                    [0]+".dist.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _plot_local_gi(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage, file_name):
        G_global = G(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), permutations=999)
        global_g_df = pd.DataFrame(columns=['G', 'G_z_sim', 'p_z_sim'])
        global_g_df.loc[len(global_g_df)] = [G_global.G,
                                             G_global.z_sim, G_global.p_z_sim]
        global_g_df.to_csv(os.path.join(
            "output/testcase_output", file_name.split('.')[0]+".g.global.csv"), index=False)

        gistar_local = G_Local(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), star=False, transform="B", permutations=999)

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
            [f'NAME_{dataloading_obj.num_layer}', 'gistar_Z', 'gistar_p_value', 'cl']].round(4).to_csv(os.path.join("output/testcase_output", file_name.split('.')[0]+".gi.csv"), index=False)
        dataloading_obj.map_with_data.assign(cl=labels).assign(spot=hotcoldspot).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='white', cmap=hmap, k=7, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output",
                    file_name.split('.')[0]+".gi.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _plot_local_gistar(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage, file_name):

        # G_global=G(dataloading_obj.map_with_data['value'],geopackage_obj.get_weight(),permutations=9999)
        # global_g_df=pd.DataFrame(columns=['G','G_z_sim','p_z_sim'])
        # global_g_df.loc[len(global_g_df)]=[G_global.G, G_global.z_sim,G_global.p_z_sim]
        # global_g_df.to_csv(os.path.join("output/testcase_output",file_name.split('.')[0]+".g_global.csv"),index=False)

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
            [f'NAME_{dataloading_obj.num_layer}', 'gistar_Z', 'gistar_p_value', 'cl']].round(4).to_csv(os.path.join("output/testcase_output", file_name.split('.')[0]+".gistar.csv"), index=False)
        dataloading_obj.map_with_data.assign(cl=labels).assign(spot=hotcoldspot).plot(
            column='cl', categorical=True, linewidth=1, ax=ax, edgecolor='white', cmap=hmap, k=7, categories=spots[::-1], legend=True)

        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                    [0]+".gistar.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

    def _plot_moran(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage, file_name):

        moran_global = Moran(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), two_tailed=True, transformation="B", permutations=999)
        global_moran_df = pd.DataFrame(
            columns=['moran_value', 'moran_z_sim', 'moran_p_sim'])
        global_moran_df.loc[len(global_moran_df)] = [
            moran_global.I, moran_global.z_sim, moran_global.p_sim]
        global_moran_df.to_csv(os.path.join(
            "output/testcase_output", file_name.split('.')[0]+".moran.global.csv"), index=False)

        moran_local = Moran_Local(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), transformation="B", permutations=999)
        temp_result = dataloading_obj.map_with_data.assign(
            moran_value=moran_local.Is, moran_z_sim=moran_local.z_sim, moran_p_sim_value=moran_local.p_sim, cl=mask_local_auto(moran_local, p=0.1)[3])
        temp_result[[f'NAME_{dataloading_obj.num_layer}', 'moran_value', 'moran_z_sim', 'moran_p_sim_value', 'cl']].round(
            4).to_csv(os.path.join("output/testcase_output", file_name.split('.')[0]+".lisa.csv"), index=False)

        fig, ax = plt.subplots(1, figsize=(12, 12))
        lisa_cluster(moran_local, dataloading_obj.map_with_data, ax=ax, p=0.1)
        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                    [0]+".lisa.png"), dpi=300, bbox_inches='tight')
        plt.close('all')

        try:
            fig, ax = plt.subplots(1, figsize=(12, 12))
            moran_scatterplot(moran_local, p=0.1, ax=ax,
                              scatter_kwds={'s': 500})
            ax.set_axis_off()
            plt.savefig(os.path.join("output/testcase_output", file_name.split('.')
                        [0]+".moran.scatter.png"), dpi=300, bbox_inches='tight')
            plt.close('all')
        except:
            pass

    def _plot_geary(self, dataloading_obj: TestDataLoading, geopackage_obj: TestGEOPackage, file_name):
        c_global = Geary(dataloading_obj.map_with_data['value'], geopackage_obj.get_weight(
        ), transformation="B", permutations=999)
        global_c_df = pd.DataFrame(columns=['c_value', 'c_z_sim', 'c_p_z_sim'])
        global_c_df.loc[len(global_c_df)] = [c_global.C,
                                             c_global.z_sim, c_global.p_z_sim]
        global_c_df.to_csv(os.path.join(
            "output/testcase_output", file_name.split('.')[0]+".c.global.csv"), index=False)

        c_local = Geary_Local(geopackage_obj.get_weight(
        ), labels=True, sig=0.1, permutations=999, keep_simulations=False)
        c_local.fit(dataloading_obj.map_with_data['value'])
        local_c_df = pd.DataFrame()
        # local_c_df=pd.DataFrame(columns=[f'NAME_{geopackage_obj.num_layer}','c_value','c_p_sim','c_label'])
        local_c_df[f'NAME_{geopackage_obj.num_layer}'] = geopackage_obj.map[f'NAME_{geopackage_obj.num_layer}']
        local_c_df['c_value'] = list(c_local.localG)
        local_c_df['c_p_sim'] = list(c_local.p_sim)
        local_c_df['c_label'] = list(c_local.labs)
        local_c_df['c_label'] = local_c_df['c_label'].astype(int).replace(
            {1: 'outlier', 2: 'cluster', 3: 'other', 4: 'not-significant'})
        local_c_df.to_csv(os.path.join("output/testcase_output",
                          file_name.split('.')[0]+".c.local.csv"), index=False)

        fig, ax = plt.subplots(1, figsize=(12, 12))
        spots = ['not-significant', 'other', 'cluster', 'outlier']
        color_list = ['lightgrey', 'lightblue', 'red', 'orange'][::-1]
        hmap = colors.ListedColormap(color_list)
        geopackage_obj.map.assign(c_label=local_c_df['c_label']).plot(
            column='c_label', categorical=True, linewidth=1, ax=ax, edgecolor='black', legend=True, cmap=hmap, k=4, categories=spots[::-1])
        ax.set_axis_off()
        plt.savefig(os.path.join("output/testcase_output",
                    file_name.split('.')[0]+".c.png"), dpi=300, bbox_inches='tight')
        plt.close('all')
