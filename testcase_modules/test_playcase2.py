import gc
import os
import numpy as np
import pandas as pd

from tqdm import tqdm
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
            # geopackage_obj = TestGEOPackage(
            #     1, 1, "Thailand")
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