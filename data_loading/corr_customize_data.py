import gc
import os
from copy import deepcopy

import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr
from scipy.stats.stats import weightedtau
from tqdm import tqdm

from data_loading import DataLoading


class CorrCustomizeData:
    def __init__(self,raw_data:DataLoading, func_keyword='pearsonr'):
        self.raw_data=self._rescale_data(raw_data)
        self._set_output_folder('corr')
        self.keyword='corr'
        self.func_keyword=func_keyword
        self.corr_func=self._set_corr_func(func_keyword)
        self.corr_data=self._process_corr()

    def _rescale_data(self,data):
        return data

    def _set_corr_func(self,func_keyword):
        func_dict={
            'pearsonr':pearsonr,
            'spearmanr':spearmanr,
            'kendalltau':kendalltau,
            'weightedtau':weightedtau
        }
        assert func_keyword in func_dict.keys(), f"{func_keyword} not in avaiable keywords"
        return func_dict[func_keyword]

    def _set_output_folder(self,keyword):
        # if not os.path.exists(f'{keyword}/'):
        #     os.makedirs(f'{keyword}/')
        list_type_keyword=[i for i in self.raw_data.list_type_keyword if i not in ['ALL']]
        for data_keyword in ['case','death']:
            for i in range(len(list_type_keyword)):
                for j in range(i+1,len(list_type_keyword)):
                    if not os.path.exists(f'{self.raw_data.base_output_path}/{keyword}/{data_keyword}/'):
                        os.makedirs(f'{self.raw_data.base_output_path}/{keyword}/{data_keyword}/')
                        print(f'\t{self.raw_data.base_output_path}/{keyword}/{data_keyword}/ not existed, create it')

    def _process_corr_get_monthly(self):
        pass;

    def _process_corr(self):
        result_dict=dict()
        list_type_keyword=[i for i in self.raw_data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death']):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    temp_data1=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[i])[['NAME_1','year','total']]
                    temp_data2=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[j])[['NAME_1','year','total']]
                    temp_data_merge=temp_data1.merge(temp_data2,on=['NAME_1','year'],suffixes=(f'_{list_type_keyword[i]}',f'_{list_type_keyword[j]}'))

                    rho_df=temp_data_merge.groupby('NAME_1')[[f'total_{list_type_keyword[i]}',f'total_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: self.corr_func(x,y)[0]
                    ).iloc[0::2][[f'total_{list_type_keyword[j]}']].reset_index()
                    rho_df=rho_df[['NAME_1',f'total_{list_type_keyword[j]}']].rename({f'total_{list_type_keyword[j]}':'rho'},axis=1)

                    pval_df=temp_data_merge.groupby('NAME_1')[[f'total_{list_type_keyword[i]}',f'total_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: self.corr_func(x,y)[1]
                    ).iloc[0::2][[f'total_{list_type_keyword[j]}']].reset_index()
                    pval_df=pval_df[['NAME_1',f'total_{list_type_keyword[j]}']].rename({f'total_{list_type_keyword[j]}':'pval'},axis=1)

                    result_df=pval_df.merge(rho_df,on='NAME_1')

                    result_dict[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}']=result_df.copy()

                    del temp_data1, temp_data2, temp_data_merge, rho_df, pval_df, result_df
                    gc.collect()
        return result_dict

    def save_csv(self):
        list_type_keyword=[i for i in self.raw_data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death']):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    self.corr_data[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}'].to_csv(
                        f'{self.raw_data.base_output_path}/{self.keyword}/{data_keyword}/{self.func_keyword}_{list_type_keyword[i]}_{list_type_keyword[j]}.csv',
                        index=False
                    )
