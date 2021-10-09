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
        load_ratio=True,
        range_year=range(2011,2021),
    )

    # cluster_obj=NoCluster(data,100000)
    # plot_obj=NoPlot(cluster_obj,0.35)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # cluster_obj=GStarCluster(data,100000)
    # cluster_obj.save_global_cluster_csv()
    # cluster_obj.save_local_cluster_csv()
    # plot_obj=GStarPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # cluster_obj=MoranCluster(data,100000,p_value=0.05)
    # cluster_obj.save_global_cluster_csv()
    # cluster_obj.save_local_cluster_csv()
    # plot_obj=LISAPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()
    # plot_obj=MoranLocalScatterPlot(cluster_obj)
    # # plot_obj.plot_preview()
    # plot_obj.save_local_cluster_plot_png()

    # df_a=pd.read_csv("preprocessed_data/DF/monthly_ratio/allcase_ratio_DF.csv")
    # df_b=pd.read_csv("preprocessed_data/DHF/monthly_ratio/allcase_ratio_DHF.csv")
    # df_c=pd.read_csv("preprocessed_data/DSS/monthly_ratio/allcase_ratio_DSS.csv")
    # df_d=df_a+df_b+df_c
    # print(df_a.head())
    # print(df_b.head())
    # print(df_c.head())
    # print(df_d.head())
