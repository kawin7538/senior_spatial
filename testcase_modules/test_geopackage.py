from libpysal.weights.contiguity import Queen
from data_loading.geopackage import GEOPackage

class TestGEOPackage(GEOPackage):
    def __init__(self, num_layer, selected_layer, selected_name, **kwargs) -> None:
        # super().__init__(**kwargs)
        self.map=self._read_file("gadm36_THA.gpkg",f"gadm36_THA_{num_layer}")
        self.map=self._filter(selected_layer,selected_name)
        self.w=self._read_weight(Queen)
        self.num_layer=num_layer
    
    def _filter(self,selected_layer,selected_name):
        return self.get_map()[self.get_map()[f"NAME_{selected_layer}"]==selected_name]