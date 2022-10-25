class TOC:

    def __init__(self, window):
        self.toc_view = QgsLayerTreeView(window)
        self.toc_model = QgsLayerTreeModel(QgsProject.instance().layerTreeRoot(), window)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeRename)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.toc_model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.toc_model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)
        self.toc_model.setAutoCollapseLegendNodes(10)
        self.toc_view.setModel(self.toc_model)
        self.toc_bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), window.map_canvas)
