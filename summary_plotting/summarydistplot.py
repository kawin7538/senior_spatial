import cv2
from tqdm import tqdm
import numpy as np
from clustering_ploting.base import BaseCluster, BasePlot


class SummaryDistPlot:
    def __init__(self, plot_obj:BasePlot):
        self.plot_obj=plot_obj
        self.base_output_path=self.plot_obj.data.base_output_path
        self.path=self.plot_obj.path
        self.list_type_keyword=self.plot_obj.data.list_type_keyword
        self.range_year=self.plot_obj.data.range_year

    def save_png(self):
        for data_keyword in ['case','death']:
            list_image=[]
            for type_keyword in self.list_type_keyword:
                temp_list_image=[]
                for year in self.range_year:
                    temp_list_image.append(cv2.imread(self.path.format(self.base_output_path,data_keyword,type_keyword,year)))
                list_image.append(temp_list_image)
            for i in range(len(list_image)):
                list_image[i]=np.concatenate(list_image[i],axis=0)
            final_image=np.concatenate(list_image,axis=1)
            temp_path="/".join(self.base_output_path.split('/')[:3])
            print(f"{temp_path}/summary_preview.png")
            cv2.imwrite(f"{temp_path}/summary_preview.png",final_image)
