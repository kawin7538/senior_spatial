import numpy as np
import pandas as pd
from testcase_modules.test_geopackage import TestGEOPackage


class TestDataLoading:
    def __init__(self,geopackagedata:TestGEOPackage, list_value:list, percent_adjust:float) -> None:
        self.num_layer=geopackagedata.num_layer
        self.percent_adjust=percent_adjust
        self.map_with_data=self._insert_data(geopackagedata,self._generate_value(list_value))

    def _insert_data(self,geopackagedata, list_value):
        temp_map=geopackagedata.get_map()
        temp_map['value']=list_value
        return temp_map

    def _generate_value(self,list_value):
        ans_list=[]
        for word in list_value:
            assert word in ["high","mid",'low'], "word should be low,mid,high"
            temp_value=np.random.uniform(0.5-((1-self.percent_adjust/100)*0.5),0.5+((1-self.percent_adjust/100)*0.5),1)[0]
            # temp_value=0.5
            if word=="high":
                ans_list.append(temp_value*10000)
            elif word=="mid":
                ans_list.append(temp_value*5005)
            elif word=="low":
                ans_list.append(temp_value*10)
        return ans_list

    def to_csv(self,filename):
        temp_df=self.map_with_data[[f'NAME_{self.num_layer}','value']]
        temp_df.to_csv(filename)