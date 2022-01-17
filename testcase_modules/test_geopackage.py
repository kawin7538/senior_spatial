from libpysal.weights.contiguity import Queen
from libpysal.weights.weights import W
import numpy as np
from data_loading.geopackage import GEOPackage

class TestGEOPackage(GEOPackage):
    def __init__(self, num_layer, selected_layer, selected_name, **kwargs) -> None:
        # super().__init__(**kwargs)
        self.map=self._read_file("gadm36_THA.gpkg",f"gadm36_THA_{num_layer}")
        if num_layer>1:
            self.map=self._filter(selected_layer,selected_name)
        self.map['centroid']=np.array(self.map.geometry.centroid)
        self.w=self._read_weight(Queen)
        if num_layer==1:
            self.w=self._custom_weight(38,47,1)
        self.num_layer=num_layer
    
    def _filter(self,selected_layer,selected_name):
        return self.get_map()[self.get_map()[f"NAME_{selected_layer}"]==selected_name]
