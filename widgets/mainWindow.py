from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QFileDialog
from plugins.processing.gui.AlgorithmDialog import AlgorithmDialog
from qgis._core import QgsApplication, QgsStyle, QgsLayerTreeModel, QgsProject, QgsVectorLayer
from qgis._gui import QgsMapToolZoom, QgsMapToolPan, QgsMapCanvas, QgsLayerTreeView, QgsLayerTreeMapCanvasBridge

from .dialog import ExportDialog, AttributeTableDialog
from .factory import RendererFactory, LayerFactory

alg_cache = {}


class MainWindow(QMainWindow):
    """程序主窗口"""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.loaded_layers = []
        uic.loadUi("ui/mainWindow.ui", self)

        self.map_tool = None
        self.view_tool_lock = ""
        self.setWindowIcon(QIcon("res/icon/title.png"))
        self.canvas = QgsMapCanvas()
        self.setCentralWidget(self.canvas)

        # 内容列表
        self.toc_view = QgsLayerTreeView(self.tocDock)
        self.toc_model = QgsLayerTreeModel(QgsProject.instance().layerTreeRoot(), self.tocDock)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeRename)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.toc_model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)
        self.toc_model.setAutoCollapseLegendNodes(10)
        self.toc_view.setModel(self.toc_model)
        self.toc_bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), self.canvas)
        self.tocDock.setWidget(self.toc_view)

        # 菜单栏
        self.actionImportVectorLayer.triggered.connect(lambda: self.load_layer("*.shp"))
        self.actionImportRasterLayer.triggered.connect(lambda: self.load_layer("*.tif"))

        # 工具栏
        self.view_tools = {
            "放大": ["./res/icon/ZoomIn.png", lambda: self.actionViewToolsToggled("放大", QgsMapToolZoom, False)],
            "缩小": ["./res/icon/ZoomOut.png", lambda: self.actionViewToolsToggled("缩小", QgsMapToolZoom, True)],
            "平移": ["./res/icon/pan.png", lambda: self.actionViewToolsToggled("平移", QgsMapToolPan)]}
        self.focus_tool = {
            "缩放至图层大小": ["./res/icon/FullExtent.png", self.actionZoomToLayerTriggered]}
        self.proc_tools = {
            "裁剪": ["./res/icon/clip.png", lambda: self.actionProcToolsTriggered("gdal:cliprasterbymasklayer")],
            "波段计算器": ["./res/icon/calculate.png", lambda: self.actionProcToolsTriggered("qgis:rastercalculator")],
            "属性表": ["./res/icon/attribute.png", self.actionAttributeTableTriggered]}
        self.symbol_renderers = {
            "简单符号样式渲染": ["./res/icon/single.png", lambda: self.actionLayerSymbolTriggered('single')],
            "分类符号渲染": ["./res/icon/Categorized.png", lambda: self.actionLayerSymbolTriggered('categorized')],
            "渐变符号渲染": ["./res/icon/graduated.png", lambda: self.actionLayerSymbolTriggered('graduated')]}
        self.export_map = {
            "冲冲冲！": ["./res/icon/export.png", lambda: self.actionExportMapTiggered()]}

        self.add_action_group(self.view_tools, checkable=True)
        self.add_action_group(self.focus_tool)
        self.toolbar.addSeparator()
        self.add_action_group(self.proc_tools)
        self.toolbar.addSeparator()
        self.add_action_group(self.symbol_renderers)
        self.toolbar.addSeparator()
        self.add_action_group(self.export_map)

    def add_action_group(self, group: dict, checkable=False):
        for name, params in group.items():
            action = QAction(name, self.toolbar)
            action.setIcon(QIcon(params[0]))
            action.setStatusTip(name)
            action.setToolTip(name)
            if checkable:
                action.setCheckable(checkable)
                action.toggled.connect(params[1])
            else:
                action.triggered.connect(params[1])
            self.toolbar.addAction(action)
            group[name].append(action)

    def open_file(self, filters=""):
        return QFileDialog.getOpenFileNames(self, "导入数据", "./data/", filters)

    def load_layer(self, filters=""):
        fullpath, formats = self.open_file(filters)
        if fullpath is None:
            return

        canvas = self.canvas
        for path in fullpath:
            layer = LayerFactory.get_layer(path, formats)  # 对于ALL Files 没有解决
            if layer is not None and layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                self.loaded_layers.append(layer)
                canvas.setLayers(self.loaded_layers)
                canvas.setExtent(layer.extent())
                canvas.refresh()
            else:
                print("图层加载错误:", layer.error())
                # QMessageBox.critical(self, "Error", "图层加载错误")
        self.toc_view.setCurrentLayer(self.loaded_layers[0])

    "----------------------slots--------------------------"

    def actionViewToolsToggled(self, tool, cls, *args):
        if self.view_tools[tool][-1].isChecked():
            if self.view_tool_lock != "":
                self.view_tools[self.view_tool_lock][-1].setChecked(False)
            self.view_tool_lock = tool
            self.map_tool = cls(self.canvas, *args)
            self.canvas.setMapTool(self.map_tool)
        else:
            if self.view_tool_lock == tool:
                self.map_tool = None
                self.canvas.setMapTool(None)

    def actionZoomToLayerTriggered(self):
        layer = self.toc_view.currentLayer()
        if layer is not None and layer.isValid():
            self.canvas.setExtent(layer.extent())
            self.canvas.refresh()

    def currentLayerChanged(self):
        if isinstance(self.toc_view.currentLayer(), QgsVectorLayer):
            self.proc_tools["属性表"][-1].setEnabled(True)
        else:
            self.proc_tools["属性表"][-1].setEnabled(False)

    def actionProcToolsTriggered(self, _id: str):
        global alg_cache
        if _id.lower() not in alg_cache:
            alg_cache[_id] = QgsApplication.processingRegistry().algorithmById(_id).create()
        alg = alg_cache[_id].create()
        dlg = AlgorithmDialog(alg, parent=self)
        # dlg.show()
        dlg.exec_()

    def actionAttributeTableTriggered(self):
        layer = self.toc_view.currentLayer()
        if layer is not None and layer.isValid():
            dlg = AttributeTableDialog(layer, self.canvas, self)
            dlg.exec_()

    def actionLayerSymbolTriggered(self, symbol):
        def repaint_layer(_layer, _renderer):
            if _layer is not None and _layer.isValid():
                _layer.setRenderer(_renderer)
                _layer.triggerRepaint()

        layer = self.toc_view.currentLayer()
        if layer is not None and layer.isValid():
            renderer_widget = RendererFactory.get_renderer(symbol).create(layer, QgsStyle.defaultStyle(),
                                                                          layer.renderer())
            renderer_widget.widgetChanged.connect(lambda: repaint_layer(layer, renderer_widget.renderer()))
            renderer_widget.show()

    def actionExportMapTiggered(self):
        dlg = ExportDialog(self)
        dlg.setLayer(self.toc_view.currentLayer())
        dlg.show()
