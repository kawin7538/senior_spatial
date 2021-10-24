import gc

import pandas as pd
from data_loading import DataLoading
from data_loading.corr_customize_data import CorrCustomizeData
from tqdm import tqdm

class CorrCustomizeDataMonthly(CorrCustomizeData):
    def __init__(self, raw_data: DataLoading, func_keyword='pearsonr'):
        super().__init__(raw_data, func_keyword=func_keyword)
        self._set_output_folder('corr_monthly')
        self.keyword='corr_monthly'

    def _process_corr_get_monthly(self,df):
        df=pd.melt(df,id_vars=['NAME_1','year'],var_name='month',value_name='value')
        df.month=pd.to_datetime(df.month.str.upper(),format='%b').dt.month
        return df

    def _process_corr(self):
        # return super()._process_corr()
        result_dict=dict()
        list_type_keyword=[i for i in self.raw_data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death'],desc="Corr Data Process"):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    temp_data1=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[i]).drop(columns='total')
                    # temp_data1=pd.melt(temp_data1,id_vars=['NAME_1','year'],var_name='month',value_name='value')
                    # temp_data1.month=pd.to_datetime(temp_data1.month.str.upper(),format='%b').dt.month
                    temp_data1=self._process_corr_get_monthly(temp_data1)
                    # print(temp_data1.info())
                    # print(temp_data1)
                    temp_data2=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[j]).drop(columns='total')
                    temp_data2=self._process_corr_get_monthly(temp_data2)
                    temp_data_merge=temp_data1.merge(temp_data2,on=['NAME_1','year','month'],suffixes=(f'_{list_type_keyword[i]}',f'_{list_type_keyword[j]}'))
                    tmep_data_merge=temp_data_merge.sort_values(by=['NAME_1','year','month'])

                    rho_df=temp_data_merge.groupby('NAME_1')[[f'value_{list_type_keyword[i]}',f'value_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: self.corr_func(x,y)[0]
                    ).iloc[0::2][[f'value_{list_type_keyword[j]}']].reset_index()
                    rho_df=rho_df[['NAME_1',f'value_{list_type_keyword[j]}']].rename({f'value_{list_type_keyword[j]}':'rho'},axis=1)

                    pval_df=temp_data_merge.groupby('NAME_1')[[f'value_{list_type_keyword[i]}',f'value_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: self.corr_func(x,y)[1]
                    ).iloc[0::2][[f'value_{list_type_keyword[j]}']].reset_index()
                    pval_df=pval_df[['NAME_1',f'value_{list_type_keyword[j]}']].rename({f'value_{list_type_keyword[j]}':'pval'},axis=1)

                    result_df=pval_df.merge(rho_df,on='NAME_1')

                    result_dict[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}']=result_df.copy()

                    del temp_data1, temp_data2, temp_data_merge, rho_df, pval_df, result_df
                    gc.collect()
        return result_dict