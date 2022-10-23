from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """程序主窗口"""
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("mainWindow.ui")
