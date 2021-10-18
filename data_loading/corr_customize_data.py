import gc
import pandas as pd
from data_loading import DataLoading
from scipy.stats import pearsonr


class CorrCustomizeData:
    def __init__(self,raw_data:DataLoading):
        self.raw_data=raw_data
        self.corr_data=self._process_corr()

    def _process_corr(self):
        result_dict=dict()
        list_type_keyword=[i for i in self.raw_data.list_type_keyword if i not in ['ALL']]
        for data_keyword in ['case','death']:
            for i in range(len(list_type_keyword)):
                for j in range(i+1,len(list_type_keyword)):
                    temp_data1=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[i])[['NAME_1','year','total']]
                    temp_data2=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[j])[['NAME_1','year','total']]
                    temp_data_merge=temp_data1.merge(temp_data2,on=['NAME_1','year'],suffixes=(f'_{list_type_keyword[i]}',f'_{list_type_keyword[j]}'))

                    rho_df=temp_data_merge.groupby('NAME_1')[[f'total_{list_type_keyword[i]}',f'total_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: pearsonr(x,y)[0]
                    ).iloc[0::2][[f'total_{list_type_keyword[j]}']].reset_index()
                    rho_df=rho_df[['NAME_1',f'total_{list_type_keyword[j]}']].rename({f'total_{list_type_keyword[j]}':'rho'},axis=1)

                    pval_df=temp_data_merge.groupby('NAME_1')[[f'total_{list_type_keyword[i]}',f'total_{list_type_keyword[j]}']].corr(
                        method=lambda x,y: pearsonr(x,y)[1]
                    ).iloc[0::2][[f'total_{list_type_keyword[j]}']].reset_index()
                    pval_df=pval_df[['NAME_1',f'total_{list_type_keyword[j]}']].rename({f'total_{list_type_keyword[j]}':'pval'},axis=1)

                    result_df=pval_df.merge(rho_df,on='NAME_1')

                    result_dict[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}']=result_df.copy()

                    del temp_data1, temp_data2, temp_data_merge, rho_df, pval_df, result_df
                    gc.collect()
        return result_dict
