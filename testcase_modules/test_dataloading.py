import numpy as np
import pandas as pd
import random
from testcase_modules.test_geopackage import TestGEOPackage


class TestDataLoading:
    def __init__(self, geopackagedata: TestGEOPackage, list_value: list, percent_adjust: float) -> None:
        self.num_layer = geopackagedata.num_layer
        self.percent_adjust = percent_adjust
        self.map_with_data = self._insert_data(
            geopackagedata, self._generate_value(list_value, geopackagedata.get_map()['centroid']))

    def _insert_data(self, geopackagedata, list_value):
        temp_map = geopackagedata.get_map()
        if isinstance(list_value,pd.DataFrame):
            temp_map['value']=list_value['total']
        else:
            temp_map['value'] = list_value
        return temp_map

    def _generate_from_centroid(self, keyword, list_centroid):
        list_classification = []
        if keyword == 'random':
            return [random.choice(['high', 'mid', 'low']) for _ in list_centroid]
        if keyword == 'random2':
            return [random.choice(['high2', 'mid', 'low2']) for _ in list_centroid]
        if keyword == 'random3':
            return [random.choice(['high3', 'mid2', 'low']) for _ in list_centroid]
        if keyword == 'random4':
            return [random.choice(['high', 'mid3', 'low3']) for _ in list_centroid]
        for centroid in list_centroid:
            # split right with Nakhon Ratchasima
            if centroid.x > 102.097771:
                list_classification.append(1)
            # split right with Pichit
            elif centroid.x > 100.34879:
                # split upper with Prachin Buri
                if centroid.y > 14.04992:
                    list_classification.append(2)
                # split upper with Chumphon
                elif centroid.y > 10.4957:
                    list_classification.append(3)
                else:
                    list_classification.append(6)
            else:
                # split upper with Pichit
                if centroid.y > 16.44184:
                    list_classification.append(4)
                # split upper with Chumphon
                elif centroid.y > 10.4957:
                    list_classification.append(5)
                else:
                    list_classification.append(6)
        if keyword == 'outside-high':
            dict_value = {
                1: 'high',
                2: 'high',
                3: 'high',
                4: 'high',
                5: 'low',
                6: 'high'
            }
        elif keyword == 'outside-high2':
            dict_value = {
                1: 'high2',
                2: 'high2',
                3: 'high2',
                4: 'high2',
                5: 'low2',
                6: 'high2'
            }
        elif keyword == 'outside-high3':
            dict_value = {
                1: 'high3',
                2: 'high3',
                3: 'high3',
                4: 'high3',
                5: 'low',
                6: 'high3'
            }
        elif keyword == 'outside-high4':
            dict_value = {
                1: 'high',
                2: 'high',
                3: 'high',
                4: 'high',
                5: 'low3',
                6: 'high'
            }
        elif keyword == 'outside-low':
            dict_value = {
                1: 'low',
                2: 'low',
                3: 'low',
                4: 'low',
                5: 'high',
                6: 'low'
            }
        elif keyword == 'outside-low2':
            dict_value = {
                1: 'low2',
                2: 'low2',
                3: 'low2',
                4: 'low2',
                5: 'high2',
                6: 'low2'
            }
        elif keyword == 'outside-low3':
            dict_value = {
                1: 'low',
                2: 'low',
                3: 'low',
                4: 'low',
                5: 'high3',
                6: 'low'
            }
        elif keyword == 'outside-low4':
            dict_value = {
                1: 'low3',
                2: 'low3',
                3: 'low3',
                4: 'low3',
                5: 'high',
                6: 'low3'
            }
        elif keyword == 'flower-high':
            dict_value = {
                1: 'high',
                2: 'high',
                3: 'low',
                4: 'low',
                5: 'mid',
                6: 'high'
            }
        elif keyword == 'flower-high2':
            dict_value = {
                1: 'high2',
                2: 'high2',
                3: 'low2',
                4: 'low2',
                5: 'mid',
                6: 'high2'
            }
        elif keyword == 'flower-high3':
            dict_value = {
                1: 'high3',
                2: 'high3',
                3: 'low',
                4: 'low',
                5: 'mid2',
                6: 'high3'
            }
        elif keyword == 'flower-high4':
            dict_value = {
                1: 'high',
                2: 'high',
                3: 'low3',
                4: 'low3',
                5: 'mid3',
                6: 'high'
            }
        elif keyword == 'flower-low':
            dict_value = {
                1: 'low',
                2: 'high',
                3: 'high',
                4: 'high',
                5: 'mid',
                6: 'low'
            }
        elif keyword == 'flower-low2':
            dict_value = {
                1: 'low2',
                2: 'high2',
                3: 'high2',
                4: 'high2',
                5: 'mid',
                6: 'low2'
            }
        elif keyword == 'flower-low3':
            dict_value = {
                1: 'low',
                2: 'high3',
                3: 'high3',
                4: 'high3',
                5: 'mid2',
                6: 'low'
            }
        elif keyword == 'flower-low4':
            dict_value = {
                1: 'low3',
                2: 'high',
                3: 'high',
                4: 'high',
                5: 'mid3',
                6: 'low3'
            }
        return [*map(dict_value.get, list_classification)]

    def _generate_value(self, list_value, list_centroid):
        if isinstance(list_value,pd.DataFrame):
            return list_value
        ans_list = []
        if len(list_value) == 1:
            if list_value[0]=='real':
                temp_df=pd.read_csv("preprocessed_data/DF/monthly_ratio/allcase_ratio_DF.csv")
                ans_list=list(temp_df[temp_df['year']==2013]['total'].values)
                return ans_list
            list_value = self._generate_from_centroid(
                list_value[0], list_centroid)
        for word in list_value:
            # assert word in ["high","high2","mid","low2",'low','mid2'], "word should be high,high2,mid,low2,low"
            temp_value = np.random.uniform(
                0.5-((1-self.percent_adjust/100)*0.5), 0.5+((1-self.percent_adjust/100)*0.5), 1)[0]
            # temp_value=0.5
            if word == "high":
                ans_list.append(temp_value*10000)
            elif word == 'high2':
                ans_list.append(temp_value*5550)
            elif word == 'high3':
                ans_list.append(temp_value*120)
            elif word == "mid":
                ans_list.append(temp_value*5050)
            elif word == 'mid2':
                ans_list.append(temp_value*110)
            elif word == 'mid3':
                ans_list.append(temp_value*9000)
            elif word == 'low3':
                ans_list.append(temp_value*8000)
            elif word == 'low2':
                ans_list.append(temp_value*4550)
            elif word == "low":
                ans_list.append(temp_value*100)
        return ans_list

    def to_csv(self, filename):
        temp_df = self.map_with_data[[f'NAME_{self.num_layer}', 'value']]
        temp_df.to_csv(filename,index=False)
