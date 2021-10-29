import gc
import matplotlib.pyplot as plt
from data_loading.corr_customize_data import CorrCustomizeData
from matplotlib import colors
from tqdm import tqdm
import seaborn as sns
import scipy.stats as stat


class SpatialCorrPlot:
    def __init__(self,corr_data:CorrCustomizeData):
        self.corr_data=corr_data
        self.data=self.corr_data.raw_data
        self.geomap=self.data.get_map()

    def make_plot(self):
        list_type_keyword=[i for i in self.data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death'],desc="Corr Plot"):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    fig, ax= plt.subplots(1,figsize=(9,12))
                    map_with_data=self.geomap.copy()
                    map_with_data[['rho','pval']]=self.corr_data.corr_data[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}'][['rho','pval']]
                    map_with_data.plot(column='rho',legend=True,ax=ax,cmap='seismic',edgecolor=(0,0,0,0.8),vmin=-1,vmax=1,missing_kwds= dict(color = "lightgrey",label='Cant calculate'))
                    ax.set_axis_off()
                    plt.title(f"{self.corr_data.func_keyword} {data_keyword} {list_type_keyword[i]}-{list_type_keyword[j]}")
                    # plt.savefig(self.path.format(self.data.base_output_path,data_keyword,type_keyword,year),dpi=300)
                    plt.savefig(f"{self.data.base_output_path}/{self.corr_data.keyword}/{data_keyword}/{self.corr_data.func_keyword}_{list_type_keyword[i]}_{list_type_keyword[j]}",dpi=300)

    def make_abs_plot(self):
        list_type_keyword=[i for i in self.data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death'],desc="ABS Corr Plot"):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    fig, ax= plt.subplots(1,figsize=(9,12))
                    map_with_data=self.geomap.copy()
                    map_with_data[['rho','pval']]=self.corr_data.corr_data[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}'][['rho','pval']]
                    map_with_data['rho']=map_with_data['rho'].abs()
                    map_with_data.plot(column='rho',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),vmin=0,vmax=1,missing_kwds= dict(color = "lightgrey",label='Cant calculate'))
                    ax.set_axis_off()
                    plt.title(f"{self.corr_data.func_keyword} abs {data_keyword} {list_type_keyword[i]}-{list_type_keyword[j]}")
                    # plt.savefig(self.path.format(self.data.base_output_path,data_keyword,type_keyword,year),dpi=300)
                    plt.savefig(f"{self.data.base_output_path}/{self.corr_data.keyword}/{data_keyword}/{self.corr_data.func_keyword}_abs_{list_type_keyword[i]}_{list_type_keyword[j]}",dpi=300)
    
    def make_pval_plot(self):
        list_type_keyword=[i for i in self.data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death'],desc="pval Corr Plot"):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    fig, ax= plt.subplots(1,figsize=(9,12))
                    map_with_data=self.geomap.copy()
                    map_with_data[['rho','pval']]=self.corr_data.corr_data[f'{data_keyword}_{list_type_keyword[i]}-{list_type_keyword[j]}'][['rho','pval']]
                    map_with_data.plot(column='pval',legend=True,ax=ax,cmap='Greens_r',edgecolor=(0,0,0,0.8),vmin=0, vmax=1 ,missing_kwds= dict(color = "lightgrey",label='Cant calculate'),norm=colors.PowerNorm(0.05,vmin=0,vmax=1))
                    ax.set_axis_off()
                    plt.title(f"{self.corr_data.func_keyword} pval {data_keyword} {list_type_keyword[i]}-{list_type_keyword[j]}")
                    # plt.savefig(self.path.format(self.data.base_output_path,data_keyword,type_keyword,year),dpi=300)
                    plt.savefig(f"{self.data.base_output_path}/{self.corr_data.keyword}/{data_keyword}/{self.corr_data.func_keyword}_pval_{list_type_keyword[i]}_{list_type_keyword[j]}",dpi=300)

    def make_scatter_plot(self):
        # temp_data1=self.raw_data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[i]).drop(columns='total')
        # temp_data1=self.data.get_df(data_keyword=)
        list_type_keyword=[i for i in self.data.list_type_keyword if i not in ['ALL']]
        for data_keyword in tqdm(['case','death'],desc="value scatter Plot"):
            for i in tqdm(range(len(list_type_keyword)),leave=False):
                for j in tqdm(range(i+1,len(list_type_keyword)),leave=False):
                    fig, ax= plt.subplots(1,figsize=(12,9))
                    temp_data1=self.data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[i]).drop(columns='total')
                    temp_data1=self.corr_data._process_corr_get_monthly(temp_data1)
                    temp_data2=self.data.get_df(data_keyword=data_keyword,type_keyword=list_type_keyword[j]).drop(columns='total')
                    temp_data2=self.corr_data._process_corr_get_monthly(temp_data2)
                    temp_data_merge=temp_data1.merge(temp_data2,on=['NAME_1','year','month'],suffixes=(f'_{list_type_keyword[i]}',f'_{list_type_keyword[j]}'))

                    # temp_data_merge.plot.scatter(x=f'value_{list_type_keyword[i]}',y=f'value_{list_type_keyword[j]}',s=5)
                    g=sns.jointplot(data=temp_data_merge,x=f'value_{list_type_keyword[i]}',y=f'value_{list_type_keyword[j]}',kind='reg',joint_kws={'line_kws':{'color':'red'}})
                    # g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=6)
                    # g.plot_marginals(sns.rugplot, color="r", height=-.15, clip_on=False)
                    # g.ax_joint.set_xscale('log')
                    # g.ax_joint.set_yscale('log')
                    g.ax_joint.set(xlabel=f"{data_keyword}_{list_type_keyword[i]}",ylabel=f"{data_keyword}_{list_type_keyword[j]}")

                    # plt.xlabel(f"{data_keyword}_{list_type_keyword[i]}")
                    # plt.ylabel(f"{data_keyword}_{list_type_keyword[j]}")
                    # plt.title(f"scatterplot {data_keyword} {list_type_keyword[i]}-{list_type_keyword[j]}")

                    # print(f"{self.data.base_output_path}/{self.corr_data.keyword}/{data_keyword}/scatter_{list_type_keyword[i]}_{list_type_keyword[j]}")

                    plt.savefig(f"{self.data.base_output_path}/{self.corr_data.keyword}/{data_keyword}/scatter_{list_type_keyword[i]}_{list_type_keyword[j]}",dpi=300)

                    del fig,ax,temp_data1,temp_data2,temp_data_merge,g
                    gc.collect()
