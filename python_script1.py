import gc
import warnings

import pandas as pd

from clustering_ploting.gstarclustering import GStarCluster, GStarPlot
from clustering_ploting.moranclustering import (LISAPlot, MoranCluster,
                                                MoranLocalScatterPlot)
from clustering_ploting.noclustering import NoCluster, NoPlot
from data_loading import DataLoading
from data_loading.corr_customize_data import CorrCustomizeData
from summary_plotting.summarydistplot import SummaryDistPlot

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    
    data=DataLoading(
        load_ratio=True,
        range_year=range(2011,2021),
    )

    corr_data=CorrCustomizeData(data)

    # print(corr_data.corr_data)

    corr_data.save_csv()

    # cluster_obj=NoCluster(data,100000)
    # plot_obj=NoPlot(cluster_obj,1)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # SummaryDistPlot(plot_obj).save_png()

    # del cluster_obj,plot_obj
    # gc.collect()

    # cluster_obj=GStarCluster(data,100000)
    # cluster_obj.save_global_cluster_csv()
    # cluster_obj.save_local_cluster_csv()
    # plot_obj=GStarPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # del cluster_obj,plot_obj
    # gc.collect()

    # cluster_obj=MoranCluster(data,100000,p_value=0.05)
    # cluster_obj.save_global_cluster_csv()
    # cluster_obj.save_local_cluster_csv()
    # plot_obj=LISAPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()
    # plot_obj=MoranLocalScatterPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # del cluster_obj,plot_obj
    # gc.collect()
