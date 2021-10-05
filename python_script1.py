from matplotlib.pyplot import plot
from clustering_ploting.gstarclustering import GStarCluster, GStarPlot
import warnings
warnings.filterwarnings("ignore")

from data_loading import DataLoading
from clustering_ploting.noclustering import NoCluster, NoPlot

if __name__ == '__main__':

    data=DataLoading(
        load_ratio=True,
        range_year=range(2011,2021),
    )

    cluster_obj=NoCluster(data,100000)
    plot_obj=NoPlot(cluster_obj,0.35)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()

    cluster_obj=GStarCluster(data,100000)
    cluster_obj.save_global_cluster_csv()
    cluster_obj.save_local_cluster_csv()
    plot_obj=GStarPlot(cluster_obj)
    # plot_obj.plot_preview()
    plot_obj.save_local_cluster_plot_png()