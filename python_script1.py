import warnings

warnings.filterwarnings("ignore")
import pandas as pd

from clustering_ploting.gstarclustering import GStarCluster, GStarPlot
from clustering_ploting.moranclustering import (LISAPlot, MoranCluster,
                                                MoranLocalScatterPlot)
from clustering_ploting.noclustering import NoCluster, NoPlot
from data_loading import DataLoading

if __name__ == '__main__':

    data=DataLoading(
        load_ratio=False,
        range_year=range(2011,2021),
    )

    cluster_obj=NoCluster(data,100000)
    plot_obj=NoPlot(cluster_obj,1)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()

    cluster_obj=GStarCluster(data,100000)
    cluster_obj.save_global_cluster_csv()
    cluster_obj.save_local_cluster_csv()
    plot_obj=GStarPlot(cluster_obj)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()

    cluster_obj=MoranCluster(data,100000,p_value=0.05)
    cluster_obj.save_global_cluster_csv()
    cluster_obj.save_local_cluster_csv()
    plot_obj=LISAPlot(cluster_obj)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()
    plot_obj=MoranLocalScatterPlot(cluster_obj)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()
