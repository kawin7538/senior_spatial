import geopandas
from libpysal.weights import Queen, W

class GEOPackage:
    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)
        self.map=self._read_file("gadm36_THA.gpkg","gadm36_THA_1")
        self.w=self._read_weight(Queen)
        self.w=self._custom_weight(38,47,1)

    def _read_file(self,file_path,file_layer):
        return geopandas.read_file(file_path,layer=file_layer)

    def _read_weight(self,func):
        return func.from_dataframe(self.map)

    def _custom_weight(self,node1_idx,node2_idx,replace_value):
        w=dict(self.w)
        w=self._replace_weight(w,node1_idx,node2_idx,replace_value)
        return W(w)

    def _replace_weight(self,w,node1_idx,node2_idx,replace_value):
        w[node1_idx][node2_idx]=replace_value
        w[node2_idx][node1_idx]=replace_value
        return w

    def set_inner_loop(self,cnt_node,replace_value):
        w=self.w
        for i in range(len(self.map)):
            w=self._replace_weight(w,i,i,replace_value)
        self.w=w

    def get_weight(self):
        return self.w

    def get_map(self):
        return self.map

    def __repr__(self) -> str:
        return "GEOPackage(**kwargs)"