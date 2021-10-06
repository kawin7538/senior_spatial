import pandas as pd

class Distribution_Data:
    def __init__(self,load_ratio=True,range_year=range(2011,2021),**kwargs) -> None:
        super().__init__(**kwargs)
        print("\tDistribition Data Loading",end='\r')
        self.load_ratio=load_ratio
        self.ratio_keyword='_ratio' if load_ratio else ''
        self.range_year=range_year
        self.list_path=[
            f'preprocessed_data/DF/monthly{self.ratio_keyword}',
            f'preprocessed_data/DHF/monthly{self.ratio_keyword}',
            f'preprocessed_data/DSS/monthly{self.ratio_keyword}',
        ]
        self.list_type_keyword=['DF','DHF','DSS']
        self.list_case_df=self._custom_edit_data(self._read_csv_list(data_keyword='case'))
        # self.list_case_minmax_value=self._get_list_minmax_value(data_keyword='case')
        self.list_death_df=self._custom_edit_data(self._read_csv_list(data_keyword='death'))
        # self.list_death_minmax_value=self._get_list_minmax_value(data_keyword='death')
        print("\tDistribution Data Loaded---")

    def _read_csv_list(self,data_keyword='case'):
        list_df=[]
        for keyword,path in zip(self.list_type_keyword,self.list_path):
            temp_path=f'{path}/all{data_keyword}{self.ratio_keyword if self.ratio_keyword=="_ratio" else "_mcd"}_{keyword}{"" if self.ratio_keyword=="_ratio" else "_"}.csv'
            list_df.append(pd.read_csv(temp_path))
        return list_df

    def _custom_edit_data(self,list_df):
        for df in list_df:
            df.loc[df['area']=='Bangkok','area']='Bangkok Metropolis'
            df.loc[df['area']=='Bungkan','area']='Bueng Kan'
            df.loc[df['area']=='P.Nakhon S.Ayutthaya','area']='Phra Nakhon Si Ayutthaya'
            df.rename(columns={'area':'NAME_1'},inplace=True)
        return list_df

    def _multiply_value_one(self,df,multiplier):
        copy_df=df.copy()
        copy_df.iloc[:,range(-13,0)]*=multiplier
        return copy_df

    def get_df(self,data_keyword='case',type_keyword='DF'):
        assert data_keyword in ['case','death'], f"{data_keyword} not in ['case','death']"
        assert type_keyword in self.list_type_keyword, f"{type_keyword} not in {self.list_type_keyword}"

        if data_keyword=='case':
            return self.list_case_df[self.list_type_keyword.index(type_keyword)]
        if data_keyword=='death':
            return self.list_death_df[self.list_type_keyword.index(type_keyword)]
    
    def __repr__(self) -> str:
        return f'Distribution_Data(load_ratio={self.load_ratio},range_year={self.range_year},**kwargs)'

if __name__ == '__main__':
    data=Distribution_Data()
    print(data.get_df())
    data.multiply_value(100000)
    print(data.get_df())
    print([i for i in range(-12,0)])