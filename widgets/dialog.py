import os.path

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QDialog, QHBoxLayout
from qgis._core import QgsVectorLayerCache, QgsVectorLayer, QgsProject, QgsLayout, QgsLayoutExporter, QgsLayoutItemMap, \
    QgsMapSettings, QgsRectangle, QgsLayoutPoint, QgsUnitTypes, QgsLayoutItemLabel, QgsLayoutItemLegend, \
    QgsLayoutItemScaleBar, QgsLayoutItemMapGrid
from qgis._gui import QgsAttributeTableModel, QgsAttributeTableFilterModel, QgsAttributeTableView, QgsMapCanvas


class AttributeTableDialog(QDialog):

    def __init__(self,
                 layer: QgsVectorLayer,
                 canvas: QgsMapCanvas,
                 parent=None):
        super(AttributeTableDialog, self).__init__(parent)
        self.setWindowTitle("属性表")
        self.resize(800, 600)

        layout = QHBoxLayout(self)
        layer_cache = QgsVectorLayerCache(layer, 10240)
        table_model = QgsAttributeTableModel(layer_cache)
        table_model.loadLayer()
        table_model_filtered = QgsAttributeTableFilterModel(canvas, table_model)
        table_view = QgsAttributeTableView(self)

        layout.addWidget(table_view)
        table_view.setModel(table_model_filtered)
        self.setWindowModality(Qt.WindowModal)


class ExportDialog(QDialog):
    """制图导出对话框"""
    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent)
        uic.loadUi("ui/exportDialog.ui", self)

        self.layer = None
        self.layout = None
        self.tile = None
        self.title_font = None
        self.title_loc = None
        self.legend_title = None
        self.legend_loc = None
        self.scalebar_loc = None
        self.map_loc = None
        self.map_size = None
        self.map_scale = None

        self.previewButton.clicked.connect(self.preview)

    def preview(self) -> None:
        self.updateData()
        # filepath = self.exportFileWidget.filePath()
        # if filepath == "":
        #     return
        filepath = r"temp\preview.png"
        if not os.path.exists('./temp'):
            os.mkdir('./temp')

        QgsProject.instance().addMapLayer(self.layer)
        self.updateLayout()
        self.export(filepath)
        img = QImage(filepath)
        self.previewView.setPixmap(QPixmap.fromImage(img.scaled(QSize(800, 600), Qt.IgnoreAspectRatio)))
        os.remove(filepath)

    def export(self, filepath) -> None:
        exporter = QgsLayoutExporter(self.layout)
        exporter.exportToImage(filepath, QgsLayoutExporter.ImageExportSettings())

    def setLayer(self, layer) -> None:
        self.layer = layer

    def updateData(self) -> None:
        self.map_scale = float(self.mapScale.text())
        self.map_size = list(map(int, [self.sizeLength.text(), self.sizeWidth.text()]))
        self.map_loc = list(map(int, [self.sizeX.text(), self.sizeY.text()]))
        self.tile = self.title.text()
        self.title_font = self.titleFont.currentFont()
        self.title_loc = list(map(int, [self.titleX.text(), self.titleY.text()]))
        self.scalebar_loc = list(map(int, [self.scaleX.text(), self.scaleY.text()]))
        self.legend_title = self.legendTitle.text()
        self.legend_loc = list(map(int, [self.legendX.text(), self.legendY.text()]))

    def updateLayout(self) -> None:
        self.layout = QgsLayout(QgsProject.instance())
        self.layout.initializeDefaults()
        map_preview = QgsLayoutItemMap(self.layout)
        map_preview.setRect(*self.map_loc, *self.map_size)

        map_settings = QgsMapSettings()
        map_settings.setLayers([self.layer])

        rect = QgsRectangle(map_settings.fullExtent())
        rect.scale(self.map_scale)

        map_settings.setExtent(rect)
        map_preview.setExtent(rect)

        map_preview.setBackgroundColor(QColor(255, 255, 255, 0))
        self.layout.addLayoutItem(map_preview)
        map_preview.attemptMove(QgsLayoutPoint(*self.map_loc, units=QgsUnitTypes.LayoutUnit.LayoutMillimeters))

        # Title
        title = QgsLayoutItemLabel(self.layout)
        title.setText(self.tile)
        title.setFont(self.title_font)
        title.adjustSizeToText()
        self.layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(*self.title_loc, units=QgsUnitTypes.LayoutUnit.LayoutMillimeters))

        # Legend
        legend = QgsLayoutItemLegend(self.layout)
        legend.setTitle(self.legend_title)
        self.layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(*self.legend_loc, units=QgsUnitTypes.LayoutUnit.LayoutMillimeters))

        # Scale
        scalebar = QgsLayoutItemScaleBar(self.layout)
        scalebar.setStyle("Single Box")
        scalebar.setLinkedMap(map_preview)
        scalebar.applyDefaultSize()
        self.layout.addLayoutItem(scalebar)
        scalebar.attemptMove(QgsLayoutPoint(*self.scalebar_loc, units=QgsUnitTypes.LayoutUnit.LayoutMillimeters))

        # Grid
        map_grid = map_preview.grid()
        map_grid.setEnabled(True)
        map_grid.setIntervalX(1)
        map_grid.setIntervalY(1)
        map_grid.setAnnotationEnabled(True)
        map_grid.setGridLineColor(QColor(0, 0, 0))
        map_grid.setGridLineWidth(0.1)
        map_grid.setAnnotationPrecision(3)
        map_grid.setAnnotationFrameDistance(1)
        map_grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Right)
        map_grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll, QgsLayoutItemMapGrid.Top)

        map_grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
        map_grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)

        map_grid.setAnnotationPosition(QgsLayoutItemMapGrid.OutsideMapFrame, QgsLayoutItemMapGrid.Bottom)
        map_grid.setAnnotationDirection(QgsLayoutItemMapGrid.Horizontal, QgsLayoutItemMapGrid.Bottom)

        map_preview.updateBoundingRect()
