import matplotlib.pyplot as plt
import numpy as np
from data_loading import DataLoading
from matplotlib import colors
from libpysal.weights import W, full

from .base import BaseCluster, BasePlot

class NoCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier) -> None:
        super().__init__(data, multiplier=multiplier)
        self.global_keyword="No_Cluster"
        self.local_keyword="No_Cluster"

        self._set_output_folder('distribution')

class NoPlot(BasePlot):
    def __init__(self, cluster: BaseCluster,gamma) -> None:
        super(NoPlot,self).__init__(cluster)
        self.gamma=gamma
        self.keyword="Distribution Plot"
        self.path="{}/distribution/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        # print(y)
        # if data_keyword=='case':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_case_minmax_value[idx][0],vmax=self.list_case_minmax_value[idx][1]))
        # if data_keyword=='death':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_death_minmax_value[idx][0],vmax=self.list_death_minmax_value[idx][1]))
        if data_keyword=='case':
            y.plot(column='total',legend=False,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=2,norm=colors.PowerNorm(self.gamma[0],vmin=0,vmax=self.data.case_max_value))
        if data_keyword=='death':
            y.plot(column='total',legend=False,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=2,norm=colors.PowerNorm(self.gamma[1],vmin=0,vmax=self.data.death_max_value))
        ax.set_axis_off()
        # plt.title('{} {} {} {} {}'.format('ratio' if self.data.load_ratio else 'raw',data_keyword,type_keyword,self.keyword,year))
        # return fig,ax

class NoPlotNoScale(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        super(NoPlotNoScale,self).__init__(cluster)
        self.keyword="Distribution Plot (No Scale)"
        self.path="{}/distribution/{}/{}/{}.noscale.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=1)
        ax.set_axis_off()
        # plt.title('{} {} {} {} {}'.format('ratio' if self.data.load_ratio else 'raw',data_keyword,type_keyword,self.keyword,year))
        # return fig,ax

class NoVPlot(BasePlot):
    def __init__(self, cluster: BaseCluster,gamma) -> None:
        super(NoVPlot,self).__init__(cluster)
        self.gamma=gamma
        self.keyword="Distribution Variance Plot"
        self.path="{}/distribution/{}/{}/{}.V.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        a=np.array(y['total'].values)
        b,_=full(self.cluster.data.get_weight())
        y['var']=np.var(a*b,axis=1)
        # print(y['var'])
        # print(y)
        # if data_keyword=='case':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_case_minmax_value[idx][0],vmax=self.list_case_minmax_value[idx][1]))
        # if data_keyword=='death':
        #     y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_death_minmax_value[idx][0],vmax=self.list_death_minmax_value[idx][1]))
        if data_keyword=='case':
            y.plot(column='var',legend=True,ax=ax,cmap='RdYlGn_r',edgecolor=(0,0,0,1),linewidth=1)
        if data_keyword=='death':
            y.plot(column='var',legend=True,ax=ax,cmap='RdYlGn_r',edgecolor=(0,0,0,1),linewidth=1)
        ax.set_axis_off()
        # plt.title('{} {} {} {} {}'.format('ratio' if self.data.load_ratio else 'raw',data_keyword,type_keyword,self.keyword,year))
        # return fig,ax