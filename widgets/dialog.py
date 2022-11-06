import os.path
import random
import threading
import time

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QColor, QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget, QDialogButtonBox, QFrame
from qgis._core import QgsVectorLayerCache, QgsVectorLayer, QgsProject, QgsLayout, QgsLayoutExporter, QgsLayoutItemMap, \
    QgsMapSettings, QgsRectangle, QgsLayoutPoint, QgsUnitTypes, QgsLayoutItemLabel, QgsLayoutItemLegend, \
    QgsLayoutItemScaleBar, QgsLayoutItemMapGrid, QgsApplication
from qgis._gui import QgsAttributeTableModel, QgsAttributeTableFilterModel, QgsAttributeTableView, QgsMapCanvas

from utils import Accumulator
from puzzle import PuzzleSet


class AttributeTableDialog(QDialog):

    def __init__(self,
                 layer: QgsVectorLayer,
                 canvas: QgsMapCanvas,
                 parent=None):
        super(AttributeTableDialog, self).__init__(parent)
        self.setWindowTitle("属性表")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(800, 600)

        self.layout = QHBoxLayout(self)
        self.layer_cache = QgsVectorLayerCache(layer, 10240)
        self.table_model = QgsAttributeTableModel(self.layer_cache)
        self.table_model.loadLayer()
        self.table_model_filtered = QgsAttributeTableFilterModel(canvas, self.table_model)
        self.table_view = QgsAttributeTableView(self)
        self.table_view.setModel(self.table_model_filtered)
        self.layout.addWidget(self.table_view)


class ExportDialog(QDialog):
    """制图导出对话框"""

    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent)
        uic.loadUi("ui/ExportDialog.ui", self)

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
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.export)
        self.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.close)

    def preview(self) -> None:
        self.updateData()
        if not os.path.exists('./temp'):
            os.mkdir('./temp')

        filepath = "temp/preview.png"
        QgsProject.instance().addMapLayer(self.layer)
        self.updateLayout()
        self.export(filepath)
        img = QImage(filepath)
        self.previewView.setPixmap(QPixmap.fromImage(img.scaled(QSize(800, 600), Qt.IgnoreAspectRatio)))
        os.remove(filepath)

    def export(self) -> None:
        filepath = self.exportFileWidget.filePath()
        if filepath == "":
            return
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


class PuzzleWidget(QWidget):
    # Signal
    submitted = pyqtSignal(int, name='submitted')
    allSettled = pyqtSignal(int, name="allSettled")

    def __init__(self, puzzle_set=None, parent=None):
        super(PuzzleWidget, self).__init__(parent)
        uic.loadUi("ui/PuzzleWidget.ui", self)

        self.nextPuzzle.clicked.connect(self.submit)
        self.submitted.connect(self.updateScore)

        self.options = [self.optionA, self.optionB, self.optionC, self.optionD]
        if isinstance(puzzle_set, PuzzleSet):
            raise TypeError("``puzzle_set`` should be type of PuzzleSet.")
        self.puzzle_set = puzzle_set
        self.current_puzzle = None  # 当前的问题
        # self.updatePuzzle()
        self.score = Accumulator()  # 记录分数

    def setPuzzleSet(self, puzzle_set: PuzzleSet):
        self.puzzle_set = puzzle_set
        self.updatePuzzle()
        self.score.reset()

    def updateScore(self, key_idx: int):
        if key_idx == self.current_puzzle.key_idx:
            self.score.tick()

    def updatePuzzle(self):
        try:
            self.current_puzzle = self.puzzle_set.pop()
            self.problemText.setText(f'**问题**：{self.current_puzzle.problem}')
            self.problemProgress.setText(f"[ {self.puzzle_set.settled} / {self.puzzle_set.size} ]")

            for blank, option in zip(self.options, self.current_puzzle.options):
                blank.setText(option)
        except KeyError:
            # 问题集已经pop完了
            print(f'你的分数是{self.score}')
            self.allSettled.emit(self.score.value)

    def submit(self):
        for idx, option in enumerate(self.options):
            if option.isChecked():
                # 取消选中
                option.setAutoExclusive(False)
                option.setChecked(False)
                option.setAutoExclusive(True)
                # 发射信号
                self.submitted.emit(idx)
                self.updatePuzzle()


class SystemWidget(QWidget):
    # Signal
    backdoor = pyqtSignal(name='backdoor')

    def __init__(self, parent=None):
        """

        :param parent:
        :param backdoor:
        """
        super(SystemWidget, self).__init__(parent)
        uic.loadUi("ui/SystemWidget.ui", self)

        self.systemIcon.setIcon(QIcon('res/icon/cc/system.png'))
        self.systemIcon.clicked.connect(self.actionBackdoorTriggerd)

    def setPrompt(self, prompt: str):
        self.prompt.setText(f"虚空：{prompt}")

    def actionBackdoorTriggerd(self):
        self.prompt.setStyleSheet('QLabel {font: 30pt "段宁毛笔行书(修订版）";}')
        self.prompt.setText("三年之期已到,恭迎龙王")
        threading.Timer(2, function=self.backdoor.emit).start()


class ForgeDialog(QDialog):
    """``Nahida的试炼``对话框"""
    trialBeginWith = pyqtSignal(PuzzleSet, name='systemSignal')
    trialDone = pyqtSignal(name='trialDone')

    puzzle_sets = [
        PuzzleSet("res/puzzle/计算机.json", shuffle=True).subset(2),
        PuzzleSet("res/puzzle/动画.json", shuffle=True).subset(5),
        PuzzleSet("res/puzzle/数学-物理.json", shuffle=True).subset(2),
        PuzzleSet("res/puzzle/专业.json", shuffle=True).subset(5),
        PuzzleSet("res/puzzle/生活.json", shuffle=True).subset(3),
    ]

    def __init__(self, parent=None):
        super(ForgeDialog, self).__init__(parent)
        uic.loadUi("ui/ForgeDialog.ui", self)
        # self.setWindowFlags(Qt.WindowTitleHint)

        self.nahidaIcon.setPixmap(QPixmap("res/icon/cc/forge-title.jpg"))
        self.system_widget = SystemWidget()
        self.puzzle_widget = PuzzleWidget()
        self.puzzle_widget.allSettled.connect(self._levelSettled)
        self.current_widget = self.nullWidget

        self.trialEnd = threading.Event()

        self.system_widget.backdoor.connect(self.trialDone.emit)
        self.trialBeginWith.connect(self._toTrial)
        self.trialDone.connect(self.close)

        threading.Thread(target=self.trial, daemon=True).start()

    def trial(self):
        # with self._on_trial:
        self._toSystem("亲爱的花之骑士，快快上前来，让我考考你。")
        _non_blocking_sleep(2.5)

        for puzzle_set in self.puzzle_sets:
            self.trialEnd.clear()
            self.trialBeginWith.emit(puzzle_set)
            self.trialEnd.wait()

        self._toSystem("")
        _non_blocking_sleep(1.5)

        self._toSystem("恭喜你，完成了纳西妲的试炼，领取你的奖励吧！")
        _non_blocking_sleep(1.5)
        self.trialDone.emit()

    def _toTrial(self, puzzle_set: PuzzleSet):
        # 切换至trial，开始游戏。主线程中执行
        self.puzzle_widget.setPuzzleSet(puzzle_set)
        self.layout().replaceWidget(self.current_widget, self.puzzle_widget)
        self.puzzle_widget.show()
        self.current_widget = self.puzzle_widget

    def _levelSettled(self, score):
        """当前问题集全部结束"""
        tl = ['可以的，', '强啊，', '不错，']
        tr = [
            '再奖励自己一个',
            '真厉害，不会是猜的吧，再来一个',
            '送自己一个',
        ]
        fl = ['可惜，', '差一点，', ]
        fr = [
            '再来一个练练手',
            '最后再来一个',
            '真的最后一个',
            '你是认真的吗╭(╯^╰)╮...',
        ]
        # 处理分数，提示信息
        if score / self.puzzle_widget.puzzle_set.size >= 0.6:
            # 60分及格
            prompt = random.choice(tl) + random.choice(tr)
        else:
            prompt = random.choice(fl) + random.choice(fr)
        self._toSystem(prompt)
        t = threading.Timer(_delay_time(prompt), self.trialEnd.set)
        t.setDaemon(True)
        t.start()

    def _toSystem(self, prompt):
        self.system_widget.setPrompt(prompt)
        if self.current_widget is not self.system_widget:
            last_item = self.layout().replaceWidget(self.current_widget, self.system_widget)
            last_item.widget().close()
            self.current_widget = self.system_widget

    def skipTrail(self):
        print("skip")


class ForgeTipWidget(QFrame):

    def __init__(self, parent=None):
        super(ForgeTipWidget, self).__init__(parent=parent)
        uic.loadUi("ui/ForgeTipWidget.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.img.setPixmap(QPixmap('res/img/entry.jpg'))


def _delay_time(s: str):
    return len(s) / 5 + 0.5


def _non_blocking_sleep(secs):
    t = threading.Thread(target=time.sleep, args=(secs,))
    t.start()
    t.join()


if __name__ == "__main__":
    app = QgsApplication([], True)
    app.setPrefixPath('qgis', True)
    app.initQgis()
    app.setQuitOnLastWindowClosed(True)
    win = ForgeDialog()
    win.show()
    exit(app.exec_())
