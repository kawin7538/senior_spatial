from datetime import datetime
import sys
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%Y%m%d_%H%M%S%f")
fh = open(f'output/log/log_{timestampStr}.log', 'w')
original_stderr = sys.stderr
sys.stderr = fh
original_stdout = sys.stdout
sys.stdout = fh

import gc
import warnings

import pandas as pd

from clustering_ploting.gstarclustering import GStarCluster, GStarPlot
from clustering_ploting.moranclustering import (LISAPlot, MoranCluster,
                                                MoranLocalScatterPlot)
from clustering_ploting.noclustering import NoCluster, NoPlot
from clustering_ploting.spatialcorrplot import SpatialCorrPlot
from data_loading import DataLoading
from data_loading.corr_customize_data import CorrCustomizeData
from data_loading.corr_customize_data_log_monthly import CorrCustomizeDataLogMonthly
from data_loading.corr_customize_data_monthly import CorrCustomizeDataMonthly
from summary_plotting.summarydistplot import SummaryDistPlot

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    load_ratio=False

    print("Program Started with load_ratio =",load_ratio)

    data=DataLoading(
        load_ratio=load_ratio,
        range_year=range(2011,2021),
    )

    print(data.list_case_minmax_value)
    print(data.case_max_value)
    print(data.list_death_minmax_value)
    print(data.death_max_value)

    # corr_data=CorrCustomizeData(data,func_keyword='pearsonr')
    # corr_data.save_csv()

    # # print(corr_data.corr_data)

    # corr_plot=SpatialCorrPlot(corr_data)
    # corr_plot.make_plot()

    # corr_data=CorrCustomizeDataMonthly(data,func_keyword='spearmanr')
    # corr_data.save_csv()

    # corr_plot=SpatialCorrPlot(corr_data)
    # corr_plot.make_plot()
    # corr_plot.make_abs_plot()
    # corr_plot.make_pval_plot()
    # corr_plot.make_scatter_plot()

    # corr_data=CorrCustomizeDataLogMonthly(data,func_keyword='spearmanr')
    # # print(corr_data.raw_data.get_df(data_keyword='case',type_keyword='DF').min())
    # # print(corr_data.raw_data.get_df(data_keyword='case',type_keyword='DF').max())
    # corr_data.save_csv()

    # corr_plot=SpatialCorrPlot(corr_data)
    # corr_plot.make_plot()
    # corr_plot.make_abs_plot()
    # corr_plot.make_pval_plot()
    # corr_plot.make_scatter_plot()

    cluster_obj=NoCluster(data,100000)
    plot_obj=NoPlot(cluster_obj,(0.4,0.4))
    # plot_obj.plot_preview(bbox_inches='tight')
    plot_obj.save_local_cluster_plot_png(bbox_inches='tight')

    SummaryDistPlot(plot_obj).save_png_horizontal()

    del cluster_obj,plot_obj
    gc.collect()

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

    # sys.stderr = original_stderr
    # sys.stdout = original_stdout

    # fh.close()
