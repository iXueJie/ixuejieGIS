from qgis._gui import QgsSingleSymbolRendererWidget, QgsCategorizedSymbolRendererWidget, \
    QgsGraduatedSymbolRendererWidget
from qgis.core import QgsVectorLayer, QgsRasterLayer
import os


class LayerFactory:
    vector = ["*.shp"]
    raster = ["*.tif"]

    @classmethod
    def get_layer(cls, fullpath, filters: str):
        formats = set(filters.split(";"))
        if formats.issubset(cls.vector):
            return QgsVectorLayer(fullpath, os.path.splitext(os.path.basename(fullpath))[0], "ogr")
        elif formats.issubset(cls.raster):
            return QgsRasterLayer(fullpath, os.path.splitext(os.path.basename(fullpath))[0],)
        else:
            return None


class RendererFactory:
    renderers = {"single": QgsSingleSymbolRendererWidget,
                 "categorized": QgsCategorizedSymbolRendererWidget,
                 "graduated": QgsGraduatedSymbolRendererWidget}

    @classmethod
    def get_renderer(cls, symbol: str):
        if symbol not in cls.renderers:
            raise ValueError(f"Unknown type of symbol: {symbol}")
        return cls.renderers.get(symbol)
