import cv2
from tqdm import tqdm
import gc
import numpy as np
from clustering_ploting.base import BaseCluster, BasePlot


class SummaryDistPlot:
    def __init__(self, plot_obj:BasePlot):
        self.plot_obj=plot_obj
        self.path=self.plot_obj.path
        self.list_type_keyword=self.plot_obj.data.list_type_keyword
        self.range_year=self.plot_obj.data.range_year

    def save_png_all(self):
        for data_keyword in ['case','death']:
            list_image=[]
            for type_keyword in self.list_type_keyword:
                temp_list_image=[]
                for year in self.range_year:
                    temp_list_image.append(cv2.imread(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)))
                list_image.append(temp_list_image)
                del temp_list_image
                gc.collect()
            for i in range(len(list_image)):
                list_image[i]=np.concatenate(list_image[i],axis=0)
                temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
                temp_path="/".join(temp_path.split('/')[:4])
                cv2.imwrite(f"{temp_path}/{2011+i}.png",list_image[i])
            # final_image=np.concatenate(list_image,axis=1)
            # temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
            # temp_path="/".join(temp_path.split('/')[:4])
            # print(f"{temp_path}/summary_preview.png")
            # cv2.imwrite(f"{temp_path}/summary_preview.png",final_image)
            # del list_image, final_image
            del list_image
            gc.collect()

    def save_png_split(self):
        for data_keyword in ['case','death']:
            for type_keyword in self.list_type_keyword:
                self._save_png_split_one(data_keyword=data_keyword,type_keyword=type_keyword,range_year=self.range_year)

    def _save_png_split_one(self,data_keyword,type_keyword,range_year):
        temp_list_image=[]
        for year in tqdm(range_year,desc=f"Process Summarize {data_keyword} {type_keyword}"):
            temp_list_image.append(cv2.imread(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)))
        temp_img1=np.concatenate(temp_list_image[0:5],axis=1)
        temp_img2=np.concatenate(temp_list_image[5:],axis=1)
        del temp_list_image
        gc.collect()
        img=np.concatenate((temp_img1,temp_img2),axis=0)
        print(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year))
        temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
        temp_path="/".join(temp_path.split('/')[:5])
        cv2.imwrite(f"{temp_path}/summary.png",img)
        del img
        gc.collect()