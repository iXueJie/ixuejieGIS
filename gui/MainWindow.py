from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMenuBar
from qgis.gui import QgsMapCanvas


class MainWindow(QMainWindow):
    """程序主窗口"""
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("gui/mainWindow.ui")

        self.setWindowIcon(QIcon("res/icon/title.png"))
        self.map_canvas = QgsMapCanvas()
        self.setCentralWidget(self.map_canvas)

