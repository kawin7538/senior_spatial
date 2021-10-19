from numpy import little_endian
from data_loading.corr_customize_data import CorrCustomizeData
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import colors

class SpatialCorrPlot:
    def __init__(self,corr_data:CorrCustomizeData):
        self.corr_data=corr_data
        self.data=self.corr_data.raw_data
        self.geomap=self.data.get_map()

    def make_plot(self):
        list_type_keyword=[i for i in self.data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death']):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    fig, ax= plt.subplots(1,figsize=(9,12))
                    map_with_data=self.geomap.copy()
                    map_with_data[['rho','pval']]=self.corr_data.corr_data[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}'][['rho','pval']]
                    map_with_data.plot(column='rho',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),vmin=-1,vmax=1,missing_kwds= dict(color = "lightgrey",label='Cant calculate'))
                    ax.set_axis_off()
                    plt.title(f"{self.corr_data.func_keyword} {data_keyword} {list_type_keyword[i]}-{list_type_keyword[j]}")
                    # plt.savefig(self.path.format(self.data.base_output_path,data_keyword,type_keyword,year),dpi=300)
                    plt.savefig(f"{self.data.base_output_path}/corr/{data_keyword}/{self.corr_data.func_keyword}_{list_type_keyword[i]}_{list_type_keyword[j]}",dpi=300)