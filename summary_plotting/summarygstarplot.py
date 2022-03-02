import numpy as np
from clustering_ploting.base import BasePlot
from summary_plotting.summarydistplot import SummaryDistPlot
import matplotlib.pyplot as plt

class SummaryGStarPlot(SummaryDistPlot):
    def __init__(self, plot_obj: BasePlot):
        super(SummaryGStarPlot,self).__init__(plot_obj)
        self.summary_keyword='gstar'

    def _create_custom_legend(self, data_keyword):
        colors = ['red','blue','white',(1,0.3,0.3),(0.3,0.3,1),'lightgrey',(1,0.6,0.6),(0.6,0.6,1),'white']
        f = lambda m,c: plt.plot([],[],marker=m, color=c,markersize=11, ls="none")[0]
        handles = [f("o", colors[i]) for i in range(9)]
        labels = ['Hot Spot - 99% Confidence','Cold Spot - 99% Confidence',' ','Hot Spot - 95% Confidence','Cold Spot - 95% Confidence','not-significant','Hot Spot - 90% Confidence','Cold Spot - 90% Confidence',' ']
        plt.axis('off')
        legend = plt.legend(handles, labels, loc=3, framealpha=1, frameon=True ,ncol=3)

        fig=legend.figure
        fig.canvas.draw()
        bbox  = legend.get_window_extent()
        bbox = bbox.from_extents(*(bbox.extents + np.array([-0,-0,0,0])))
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
        # bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig('{}/label.png'.format(f"{self.plot_obj.data.base_output_path}/{self.summary_keyword}/{data_keyword}"), dpi=1200, bbox_inches=bbox)