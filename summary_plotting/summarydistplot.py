import copy
import cv2
from tqdm import tqdm
import gc
import numpy as np
from clustering_ploting.base import BaseCluster, BasePlot
from PIL import Image, ImageFont, ImageDraw
import matplotlib.pyplot as plt
from matplotlib import colors


class SummaryDistPlot:
    def __init__(self, plot_obj:BasePlot):
        self.plot_obj=plot_obj
        self.path=self.plot_obj.path
        self.list_type_keyword=self.plot_obj.data.list_type_keyword
        self.range_year=self.plot_obj.data.range_year
        self.summary_keyword='distribution'

    # def save_png_all(self):
    #     for data_keyword in ['case','death']:
    #         list_image=[]
    #         for type_keyword in self.list_type_keyword:
    #             temp_list_image=[]
    #             for year in self.range_year:
    #                 temp_list_image.append(cv2.imread(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)))
    #             list_image.append(temp_list_image)
    #             del temp_list_image
    #             gc.collect()
    #         for i in range(len(list_image)):
    #             list_image[i]=np.concatenate(list_image[i],axis=0)
    #             temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
    #             temp_path="/".join(temp_path.split('/')[:4])
    #             cv2.imwrite(f"{temp_path}/{2011+i}.png",list_image[i])
    #         # final_image=np.concatenate(list_image,axis=1)
    #         # temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
    #         # temp_path="/".join(temp_path.split('/')[:4])
    #         # print(f"{temp_path}/summary_preview.png")
    #         # cv2.imwrite(f"{temp_path}/summary_preview.png",final_image)
    #         # del list_image, final_image
    #         del list_image
    #         gc.collect()

    # def save_png_split(self):
    #     for data_keyword in ['case','death']:
    #         for type_keyword in self.list_type_keyword:
    #             self._save_png_split_one(data_keyword=data_keyword,type_keyword=type_keyword,range_year=self.range_year)

    # def _save_png_split_one(self,data_keyword,type_keyword,range_year):
    #     temp_list_image=[]
    #     for year in tqdm(range_year,desc=f"Process Summarize {data_keyword} {type_keyword}"):
    #         temp_list_image.append(cv2.imread(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)))
    #     temp_img1=np.concatenate(temp_list_image[0:5],axis=1)
    #     temp_img2=np.concatenate(temp_list_image[5:],axis=1)
    #     del temp_list_image
    #     gc.collect()
    #     img=np.concatenate((temp_img1,temp_img2),axis=0)
    #     print(self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year))
    #     temp_path=self.path.format(self.plot_obj.data.base_output_path,data_keyword,type_keyword,year)
    #     temp_path="/".join(temp_path.split('/')[:5])
    #     cv2.imwrite(f"{temp_path}/summary.png",img)
    #     del img
    #     gc.collect()

    def _create_vert_label(self,img_arr,img_width,text,font):
        
        copy_img_arr=copy.deepcopy(img_arr)

        img=Image.new("RGB",(img_width,1000),(255,255,255))
        draw=ImageDraw.Draw(img)
        draw.text((1200,250),text=text,font=font,fill=(0,0,0))
        img=img.rotate(90,expand=1)
        img=np.array(img)

        copy_img_arr.append(img)

        del img
        gc.collect()

        return copy_img_arr

    def _create_custom_legend_one(self,max_value,keyword,gamma):
        f,ax=plt.subplots(1,figsize=(9,12))
        ax.remove()
        cax = f.add_axes([0.2, 0.08, 1, 0.01]) #[left, bottom, width, height]
        sm = plt.cm.ScalarMappable(cmap='Oranges', norm=colors.PowerNorm(gamma,vmin=0,vmax=max_value))
        # fake up the array of the scalar mappable.
        sm._A = []
        if self.plot_obj.data.load_ratio:
            lgd=f.colorbar(sm, cax=cax,orientation="horizontal").set_label(f"Proportion of {keyword} per 100,000", rotation=0, y=1.05, labelpad=0)
        else:
            lgd=f.colorbar(sm, cax=cax,orientation="horizontal").set_label(f"Number of {keyword} (person)", rotation=0, y=1.05, labelpad=0)
        # lgd=f.colorbar(sm, cax=cax,orientation="horizontal").set_label(f"Number of {keyword} (person)", rotation=0, labelpad=0.5)
        # lgd=f.colorbar(sm, cax=cax,orientation="horizontal")
        plt.xticks(rotation=30)
        plt.savefig('{}/label.png'.format(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{keyword}"),dpi=2400,bbox_inches='tight')

        plt.close('all')

    def _create_custom_legend(self,data_keyword):
        if data_keyword=='case':
            self._create_custom_legend_one(self.plot_obj.data.case_max_value,data_keyword,self.plot_obj.gamma[0])
        else:
            self._create_custom_legend_one(self.plot_obj.data.death_max_value,data_keyword,self.plot_obj.gamma[1])

    def save_png_horizontal(self):
        # 1568 * 2832 each
        font = ImageFont.truetype("fonts/times.ttf", 256)

        for data_keyword in tqdm(['case','death'],desc=f"summary {self.summary_keyword} png horizontal"):

            # if data_keyword=='case':
            #     self._create_custom_legend(self.plot_obj.data.case_max_value,data_keyword,self.plot_obj.gamma[0])
            # else:
            #     self._create_custom_legend(self.plot_obj.data.death_max_value,data_keyword,self.plot_obj.gamma[1])

            self._create_custom_legend(data_keyword)

            img_arr=img_arr2=img_arr3=year_img_arr=[]

            img_arr=self._create_vert_label(img_arr,2832,"DF",font)
            img_arr2=self._create_vert_label(img_arr2,2832,"DHF",font)
            img_arr3=self._create_vert_label(img_arr3,2832,"DSS",font)

            img=np.array(Image.new("RGB",(1000,1000),(255,255,255)))
            year_img_arr.append(img)
            del img

            legend_img=Image.open('{}/label.png'.format(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}"))
            # print(legend_img.size)
            legend_new_size=(16680,int(legend_img.size[1]/legend_img.size[0]*16680))
            legend_img=legend_img.resize(legend_new_size)
            legend_img=legend_img.convert("RGB")
            legend_img=np.array(legend_img)
            legend_img=legend_img[:,:,::-1]

            for year in range(2011,2021):
                img=Image.new("RGB",(1568,1000),(255,255,255))
                draw=ImageDraw.Draw(img)
                draw.text((400,250),text=str(year),font=font,fill=(0,0,0))
                img=np.array(img)
                year_img_arr.append(img)
                del img
                
                img=cv2.imread(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}/DF/{year}.png")
                img_arr.append(img)
                del img

                img=cv2.imread(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}/DHF/{year}.png")
                img_arr2.append(img)
                del img

                img=cv2.imread(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}/DSS/{year}.png")
                img_arr3.append(img)

                del img

            img_yearly=np.concatenate(year_img_arr,axis=1)
            img_df=np.concatenate(img_arr,axis=1)
            img_dhf=np.concatenate(img_arr2,axis=1)
            img_dss=np.concatenate(img_arr3,axis=1)

            # print(img_yearly.shape,img_df.shape,img_dhf.shape,img_dss.shape,legend_img.shape)

            img_final=np.concatenate([img_yearly,img_df,img_dhf,img_dss,legend_img],axis=0)
            cv2.imwrite(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}/three_disease_horz.png",img_final)

            del img_df, img_dhf, img_dss, img_final, img_arr, img_arr2, img_arr3, legend_img
            gc.collect()