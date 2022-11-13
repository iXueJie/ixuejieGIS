import sys
import time
import config
from PyQt5.QtGui import QIcon, QFontDatabase
from qgis.core import QgsApplication
from widgets.mainWindow import MainWindow
from widgets.SplashScreen import SplashScreen


class App:

    def __init__(self):
        import qdarkstyle
        self.qgs = QgsApplication([], True)
        self.splash = SplashScreen()
        self.splash.show()
        QFontDatabase.addApplicationFont('res/font/FZJunLTJW_Zhun.TTF')
        QFontDatabase.addApplicationFont('res/font/HarmonyOS_Sans_SC_Medium.ttf')
        QFontDatabase.addApplicationFont('res/font/段宁毛笔行书修订版.ttf')
        self.qgs.setWindowIcon(QIcon('res/icon/cc/257625.jpg'))
        self.qgs.setQuitOnLastWindowClosed(True)
        self.qgs.setPrefixPath('qgis', True)
        self.qgs.initQgis()
        self.qgs.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=qdarkstyle.LightPalette))
        # self.qgs.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        self.win = MainWindow()
        config.setup_env()

    def run(self):
        time.sleep(2.5)
        self.win.show()
        self.splash.finish(self.win)
        sys.exit(self.qgs.exec_())


if __name__ == "__main__":
    app = App()
    app.run()
