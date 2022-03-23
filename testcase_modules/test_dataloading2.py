import gc
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from testcase_modules.test_dataloading import TestDataLoading
from testcase_modules.test_geopackage import TestGEOPackage


class TestDataLoading2:
    def __init__(self, input_df:pd.DataFrame, n_sim=100):
        self.input_df=input_df
        self.exp_df=pd.read_csv("testcase_modules/DF_case_mean_allyears.csv")
        self.n_sim=n_sim
        self.list_sim_df=[]
        self._generate_sim()
        
    def _generate_sim(self):
        theta_dict={
            'low':1,
            'mid':2,
            'high':3
        }
        for i in tqdm(range(self.n_sim),desc="Randomizing Sim",leave=False):
            rng=np.random.default_rng(12345)
            exp_arr=self.exp_df['total'].values*100000
            theta_arr=self.input_df['total'].values
            theta_arr=np.vectorize(theta_dict.get)(theta_arr)
            # print(theta_arr)
            mu_arr=exp_arr*theta_arr
            # print(mu_arr)
            pois_arr=rng.poisson(mu_arr)
            # print(pois_arr)
            pois_arr=pois_arr/exp_arr
            # print(pois_arr)
            output_df=self.input_df.copy()
            output_df['total']=np.copy(pois_arr)
            self.list_sim_df.append(output_df)
            del rng, exp_arr, theta_arr, mu_arr, pois_arr
            gc.collect()
            # break;

    def to_csv(self,filepath):
        for i in tqdm(range(self.n_sim),desc="Exporting Sim",leave=False):
            self.list_sim_df[i].to_csv(f"{filepath}.{i+1}.csv",index=False)
            # break;