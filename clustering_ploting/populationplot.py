import gc
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
from matplotlib import pyplot as plt
import numpy as np
from clustering_ploting.base import BaseCluster
from data_loading import DataLoading
from tqdm import tqdm
from matplotlib import colors
import matplotlib.ticker as ticker

class PopulationPlot:
    def __init__(self,data:DataLoading) -> None:
        self.data=data
        self.pop10year=data.pop10year
        self.max_value=self.pop10year.max().values[1:].max()
        self.geomap=data.get_map()

        if not os.path.exists('output/pop_dist/'):
            os.makedirs('output/pop_dist/')
            print(f'\toutput/pop_dist/ not existed, create it')

    def make_plot(self,gamma=1):
        for year in tqdm(range(2011,2021)):
            fig, ax= plt.subplots(1,figsize=(9,12))
            map_with_data=self.geomap.copy()
            map_with_data=map_with_data.merge(self.pop10year[['NAME_1',str(year)]]).rename(columns={str(year):'y'})
            map_with_data.plot(column='y',legend=False,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=2,norm=colors.PowerNorm(gamma,vmin=0,vmax=self.max_value))
            ax.set_axis_off()
            plt.savefig(f"output/pop_dist/{year}.png",dpi=300,bbox_inches='tight')

    def fmt(self, x, pos):
        a, b = '{:.0e}'.format(x).split('e')
        b = int(b)
        answer=int(float(a)*np.power(10,b))
        # return r'${} \times 10^{{{}}}$'.format(a, b)
        return f"{answer:,}"

    def _create_custom_legend(self,gamma):
        f,ax=plt.subplots(1,figsize=(9,12))
        ax.remove()
        cax = f.add_axes([0.2, 0.08, 1, 0.02]) #[left, bottom, width, height]
        sm = plt.cm.ScalarMappable(cmap='Oranges', norm=colors.PowerNorm(gamma,vmin=0,vmax=self.max_value))
        # fake up the array of the scalar mappable.
        sm._A = []
        lgd=f.colorbar(sm, cax=cax,orientation="horizontal", format=ticker.FuncFormatter(self.fmt)).set_label("Population count (persons)", rotation=0, y=1.05, labelpad=0)
        # lgd=f.colorbar(sm, cax=cax,orientation="horizontal").set_label(f"Number of {keyword} (person)", rotation=0, labelpad=0.5)
        # lgd=f.colorbar(sm, cax=cax,orientation="horizontal")
        plt.xticks(rotation=30)
        plt.savefig('output/pop_dist/label.png',dpi=600,bbox_inches='tight')

        plt.close('all')

    def summary_plot(self,gamma=1):
        self.make_plot(gamma)
        self._create_custom_legend(gamma)

        font = ImageFont.truetype("fonts/times.ttf", 256)
        legend_img=Image.open('output/pop_dist/label.png')
        print(legend_img.size)
        legend_new_size=(1568*5,int(legend_img.size[1]/legend_img.size[0]*1568*5))
        legend_img=legend_img.resize(legend_new_size)
        legend_img=legend_img.convert("RGB")
        legend_img=np.array(legend_img)
        legend_img=legend_img[:,:,::-1]

        img_arr=[]
        year_img_arr=[]

        for year in tqdm(range(2011,2021)):
            img=cv2.imread(f"output/pop_dist/{year}.png")
            img_arr.append(img)
            del img

            img=Image.new("RGB",(1568,1000),(255,255,255))
            draw=ImageDraw.Draw(img)
            draw.text((400,650),text=str(year),font=font,fill=(0,0,0))
            img=np.array(img)
            year_img_arr.append(img)
            del img

        img_yearly=[np.concatenate(year_img_arr[:5],axis=1),np.concatenate(year_img_arr[5:],axis=1)]
        img=[np.concatenate(img_arr[:5],axis=1),np.concatenate(img_arr[5:],axis=1)]

        img_final=np.concatenate([img_yearly[0],img[0],img_yearly[1],img[1],legend_img ],axis=0)
        cv2.imwrite("output/pop_dist/summary.png",img_final)

        del img,img_yearly,img_final,img_arr,year_img_arr,font
        gc.collect()

