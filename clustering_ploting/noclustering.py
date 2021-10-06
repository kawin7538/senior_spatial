import matplotlib.pyplot as plt
from data_loading import DataLoading
from matplotlib import colors

from .base import BaseCluster, BasePlot


class NoCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier) -> None:
        super().__init__(data, multiplier=multiplier)
        self.global_keyword="No_Cluster"
        self.local_keyword="No_Cluster"

class NoPlot(BasePlot):
    def __init__(self, cluster: BaseCluster,gamma) -> None:
        super(NoPlot,self).__init__(cluster)
        self.gamma=gamma
        self.keyword="Distribution Plot"
        self.path="output/distribution/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        if data_keyword=='case':
            y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_case_minmax_value[idx][0],vmax=self.list_case_minmax_value[idx][1]))
        if data_keyword=='death':
            y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,0.8),norm=colors.PowerNorm(self.gamma,vmin=self.list_death_minmax_value[idx][0],vmax=self.list_death_minmax_value[idx][1]))
        ax.set_axis_off()
        plt.title('{} {} {}'.format(type_keyword,self.keyword,year))
        # return fig,ax
