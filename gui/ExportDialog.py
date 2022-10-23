from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class ExportDialog(QDialog):
    """程序主窗口"""
    def __init__(self):
        super(ExportDialog, self).__init__()
        uic.loadUi("gui/exportDialog.ui")
