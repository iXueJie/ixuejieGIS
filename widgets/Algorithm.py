import csv
import typing

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant, QSortFilterProxyModel, QRegExp
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeView, QTreeWidget, QTreeWidgetItem
from qgis._core import QgsApplication

from processing import AlgorithmDialog, Processing


def _load_algs_from_file(file):
    algorithms = {}
    with open(file, mode='r') as f:
        # 只加载文件中记录的算法
        reader = csv.reader(f)
        for _id, name in reader:
            algorithms[name] = _id
    return algorithms


Processing.initialize()
_algorithms = {"gdal": _load_algs_from_file('res/algs/gdal.csv'),
               "qgis": _load_algs_from_file('res/algs/qgis.csv')}


class ProcessingTreeWidget(QTreeWidget):

    def __init__(self, parent=None):
        super(ProcessingTreeWidget, self).__init__(parent=parent)
        self.setHeaderHidden(True)

        for provider, algs in _algorithms.items():
            Processing.initialize()
            child = QTreeWidgetItem()
            child.setText(0, provider)
            for alg in algs.keys():
                item = QTreeWidgetItem(child)
                item.setText(0, alg)
                child.addChild(item)
            self.addTopLevelItem(child)

        self.doubleClicked.connect(self.onDoubleClick)
        self.filtered_model = QSortFilterProxyModel()

    def onDoubleClick(self, index: QModelIndex):
        _id = _algorithms[index.parent().data()][index.data()]
        alg = QgsApplication.processingRegistry().createAlgorithmById(_id)
        dlg = AlgorithmDialog(alg, parent=self)
        dlg.show()

    def actionSearchBoxValueChanged(self, value: str):
        regexp = QRegExp(value, Qt.CaseInsensitive, QRegExp.RegExp)
        self.filtered_model.setFilterRegExp(regexp)
        super(ProcessingTreeWidget, self).setModel(self.filtered_model)


class ProcessingTreeItem:

    def __init__(self, _id, name, parent=None):
        self._id = _id
        self.name = name
        self.parent = parent
        if parent is not None:
            self.parent.children.append(self)
        self.children = []

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)


tree_root = ProcessingTreeItem('', 'processing')
for provider, alg in _algorithms.items():
    child = ProcessingTreeItem('', provider, tree_root)
    for name, _id in alg.items():
        ProcessingTreeItem(_id, name, child)


class ProcessingTreeModel(QAbstractItemModel):

    def __init__(self):
        super(ProcessingTreeModel, self).__init__()
        self.root = tree_root
        self.icon_provider = QIcon('res/icon/cc/259806.png')
        self.icon_algorithm = QIcon("res/icon/cc/259796.png")

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DecorationRole:
            if item.childCount() != 0:
                return self.icon_provider
            return self.icon_algorithm

        if role == Qt.DisplayRole:
            return item.name

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return self.root.childCount()
        return parent.internalPointer().childCount()

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item = self.root
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.children[row]

        if child_item:
            return self.createIndex(row, 0, child_item)
        else:
            return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()
        child_item = child.internalPointer()
        parent_item = child_item.parent
        if parent_item is self.root:
            return QModelIndex()
        row = parent_item.children.index(child_item)
        return self.createIndex(row, 0, parent_item)


class ProcessingTreeView(QTreeView):

    def __init__(self, parent=None):
        super(ProcessingTreeView, self).__init__(parent=parent)
        self.setHeaderHidden(True)
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(ProcessingTreeModel())
        self.proxy.setRecursiveFilteringEnabled(True)
        self.setModel(self.proxy)
        self.doubleClicked.connect(self.onDoubleClick)

    def setFilterString(self, value: str):
        if value == '':
            self.collapseAll()
            return
        regexp = QRegExp(value, Qt.CaseInsensitive, QRegExp.RegExp)
        self.proxy.setFilterRegExp(regexp)
        self.expandAll()

    def onDoubleClick(self, index: QModelIndex):
        _id = _algorithms[index.parent().data()][index.data()]
        alg = QgsApplication.processingRegistry().createAlgorithmById(_id)
        dlg = AlgorithmDialog(alg, parent=self)
        dlg.show()


if __name__ == '__main__':
    app = QgsApplication([], True)
    app.setPrefixPath('qgis', True)
    app.initQgis()
    app.setQuitOnLastWindowClosed(True)

    Processing.initialize()
    win = ProcessingTreeView()

    win.expandAll()
    win.show()
    app.exec_()
