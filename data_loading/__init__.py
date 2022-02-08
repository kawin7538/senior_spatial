import copy

from .distribution_data import Distribution_Data
from .geopackage import GEOPackage


class DataLoading(GEOPackage,Distribution_Data):
    def __init__(self,load_ratio=True,range_year=range(2011,2021)) -> None:
        print("Data Loading")
        super(DataLoading,self).__init__(load_ratio=load_ratio,range_year=range_year)
        self.list_case_map=self._merge(self.list_case_df)
        self.list_case_minmax_value=self._get_list_minmax_value(data_keyword='case')
        self.case_max_value=max([i[1] for i in self.list_case_minmax_value[:-1]])
        self.list_death_map=self._merge(self.list_death_df)
        self.list_death_minmax_value=self._get_list_minmax_value(data_keyword='death')
        self.death_max_value=max([i[1] for i in self.list_death_minmax_value[:-1]])
        print("Data Loaded")

    def _merge(self,list_df):
        list_map=[]
        for df in list_df:
            list_map.append(self.map.merge(df,on='NAME_1'))
        return list_map

    def multiply_value(self,multiplier):
        temp_self=copy.copy(self)
        for type_keyword in self.list_type_keyword:
            temp_self.list_case_map[temp_self.list_type_keyword.index(type_keyword)]=temp_self._multiply_value_one(temp_self.list_case_map[temp_self.list_type_keyword.index(type_keyword)],multiplier)
            temp_self.list_death_map[temp_self.list_type_keyword.index(type_keyword)]=temp_self._multiply_value_one(temp_self.list_death_map[temp_self.list_type_keyword.index(type_keyword)],multiplier)
            temp_self.list_case_df[temp_self.list_type_keyword.index(type_keyword)]=temp_self._multiply_value_one(temp_self.list_case_df[temp_self.list_type_keyword.index(type_keyword)],multiplier)
            temp_self.list_death_df[temp_self.list_type_keyword.index(type_keyword)]=temp_self._multiply_value_one(temp_self.list_death_df[temp_self.list_type_keyword.index(type_keyword)],multiplier)
        
        temp_self.list_case_minmax_value=self._get_list_minmax_value(data_keyword='case')
        temp_self.list_death_minmax_value=self._get_list_minmax_value(data_keyword='death')
        return temp_self

    def rescale_log(self):
        temp_self=copy.copy(self)
        for type_keyword in self.list_type_keyword:
            temp_self.list_case_df[temp_self.list_type_keyword.index(type_keyword)]=temp_self._rescale_log_one(temp_self.list_case_df[temp_self.list_type_keyword.index(type_keyword)])
            temp_self.list_death_df[temp_self.list_type_keyword.index(type_keyword)]=temp_self._rescale_log_one(temp_self.list_death_df[temp_self.list_type_keyword.index(type_keyword)])
        return temp_self

    def get_map_with_data(self,data_keyword='case',type_keyword='DF'):
        assert data_keyword in ['case','death'], f"{data_keyword} not in ['case','death']"
        assert type_keyword in self.list_type_keyword, f"{type_keyword} not in {self.list_type_keyword}"

        if data_keyword=='case':
            return self.list_case_map[self.list_type_keyword.index(type_keyword)]
        if data_keyword=='death':
            return self.list_death_map[self.list_type_keyword.index(type_keyword)]

    def _get_list_minmax_value(self,data_keyword='case'):
        assert data_keyword in ['case','death'], f"{data_keyword} not in ['case','death']"
        list_minmax_value=list()
        for type_keyword in self.list_type_keyword:
            if data_keyword=='case':
                min_value=self.list_case_map[self.list_type_keyword.index(type_keyword)]['total'].min()
                max_value=self.list_case_map[self.list_type_keyword.index(type_keyword)]['total'].max()
            if data_keyword=='death':
                min_value=self.list_death_map[self.list_type_keyword.index(type_keyword)]['total'].min()
                max_value=self.list_death_map[self.list_type_keyword.index(type_keyword)]['total'].max()
            list_minmax_value.append((min_value,max_value))
        return list_minmax_value
    