import matplotlib.pyplot as plt
import numpy as np
from data_loading import DataLoading
from matplotlib import colors
from libpysal.weights import W, full

from .base import BaseCluster, BasePlot

# The `NoCluster` class inherits from the `BaseCluster` class. 
# 
# The `__init__` method takes the data and the multiplier as arguments. 
# 
# The `global_keyword` and `local_keyword` are set to "No_Cluster". 
# 
# The `_set_output_folder` method is called to set the output folder to "distribution".
class NoCluster(BaseCluster):
    def __init__(self, data: DataLoading, multiplier) -> None:
        '''
        The function is the constructor of the class
        
        :param data: the DataLoading object that contains the data to be analyzed
        :type data: DataLoading
        :param multiplier: The multiplier is used to scale the data. This is useful for
        '''
        super().__init__(data, multiplier=multiplier)
        self.global_keyword="No_Cluster"
        self.local_keyword="No_Cluster"

        self._set_output_folder('distribution')

# The class NoPlot is a subclass of BasePlot. It is used to plot the distribution of the data.
class NoPlot(BasePlot):
    def __init__(self, cluster: BaseCluster,gamma) -> None:
        '''
        The __init__ function is the constructor for the class. 
        
        The super function is used to call the constructor of the parent class. 
        
        The keyword argument is used to pass a string that will be used as a key word for the function. 
        
        The path argument is used to pass a string that will be used as a path to store the plot.
        
        :param cluster: the cluster object that is being used to run the experiment
        :type cluster: BaseCluster
        :param gamma: the gamma value for the distribution plot
        '''
        super(NoPlot,self).__init__(cluster)
        self.gamma=gamma
        self.keyword="Distribution Plot"
        self.path="{}/distribution/{}/{}/{}.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        '''
        It creates a map of the data for a given year, and then plots it
        
        :param year: the year you want to plot
        :param data_keyword: 'case' or 'death'
        :param type_keyword: the type of data to be plotted
        :param idx: the index of the cluster to be plotted
        '''
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        if data_keyword=='case':
            y.plot(column='total',legend=False,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=2,norm=colors.PowerNorm(self.gamma[0],vmin=0,vmax=self.data.case_max_value))
        if data_keyword=='death':
            y.plot(column='total',legend=False,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=2,norm=colors.PowerNorm(self.gamma[1],vmin=0,vmax=self.data.death_max_value))
        ax.set_axis_off()

# The class NoPlotNoScale inherits from BasePlot. 
# 
# The class NoPlotNoScale has a constructor that takes a cluster as an argument. 
# 
# The class NoPlotNoScale has a method _make_local_cluster_plot that takes a year, a data_keyword, a
# type_keyword, and an idx as arguments. 
# 
# The class NoPlotNoScale has a method _make_local_cluster_plot that creates a plot of the data for
# the given year, data_keyword, and type
class NoPlotNoScale(BasePlot):
    def __init__(self, cluster: BaseCluster) -> None:
        '''
        The __init__ function is called when the class is instantiated. 
        
        The super function is used to initialize the parent class. 
        
        The keyword and path variables are used to set the name of the plot and the path to save the
        plot.
        
        :param cluster: the cluster object that this plotter is associated with
        :type cluster: BaseCluster
        '''
        super(NoPlotNoScale,self).__init__(cluster)
        self.keyword="Distribution Plot (No Scale)"
        self.path="{}/distribution/{}/{}/{}.noscale.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        '''
        It creates a map of the data for a given year.
        
        :param year: the year you want to plot
        :param data_keyword: the name of the dataframe in the data object that contains the data to be
        plotted
        :param type_keyword: the type of data to be plotted
        :param idx: the index of the map to be plotted
        '''
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        y.plot(column='total',legend=True,ax=ax,cmap='Oranges',edgecolor=(0,0,0,1),linewidth=1)
        ax.set_axis_off()

# The NoVPlot class is a subclass of BasePlot. It inherits all the attributes and methods from
# BasePlot.
# It has a constructor that takes a cluster object as an argument. It also has a gamma attribute that
# is used in the make_local_cluster_plot method.
# The make_local_cluster_plot method is a method that takes a year, data_keyword, type_keyword, and
# idx as arguments.
# It creates a figure and axes object. It also creates a map_with_data dataframe that contains the
class NoVPlot(BasePlot):
    def __init__(self, cluster: BaseCluster,gamma) -> None:
        '''
        The __init__ function is called when an instance of the class is created. 
        
        The __init__ function is where you define all the attributes of the class. 
        
        The __init__ function must at least accept one argument, even if it is just self. 
        
        The __init__ function must always have a self argument. 
        
        The __init__ function must always return None.
        
        :param cluster: the cluster object that we created in the previous step
        :type cluster: BaseCluster
        :param gamma: the gamma value used in the simulation
        '''
        super(NoVPlot,self).__init__(cluster)
        self.gamma=gamma
        self.keyword="Distribution Variance Plot"
        self.path="{}/distribution/{}/{}/{}.V.png"

    def _make_local_cluster_plot(self,year,data_keyword,type_keyword,idx):
        '''
        It makes a plot of the variance of the data in each cluster
        
        :param year: the year you want to plot
        :param data_keyword: 'case' or 'death'
        :param type_keyword: 'state' or 'nation'
        :param idx: the index of the cluster to be plotted
        '''
        fig,ax=plt.subplots(1,figsize=(9,12))
        map_with_data=self.data.get_map_with_data(data_keyword=data_keyword,type_keyword=type_keyword)
        y=map_with_data[map_with_data['year']==year]
        a=np.array(y['total'].values)
        b,_=full(self.cluster.data.get_weight())
        y['var']=np.var(a*b,axis=1)
        if data_keyword=='case':
            y.plot(column='var',legend=True,ax=ax,cmap='RdYlGn_r',edgecolor=(0,0,0,1),linewidth=1)
        if data_keyword=='death':
            y.plot(column='var',legend=True,ax=ax,cmap='RdYlGn_r',edgecolor=(0,0,0,1),linewidth=1)
        ax.set_axis_off()