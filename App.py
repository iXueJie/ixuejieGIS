import sys
sys.path.append("E:\\Program Files\\QGIS 3.22.10\\apps\\qgis-ltr\\python\\plugins")

import time
from plugins.processing.core.Processing import Processing
from qgis.core import QgsApplication
from widgets.mainWindow import MainWindow
from widgets.SplashScreen import SplashScreen


class App:

    def __init__(self):
        import qdarkstyle
        self.qgs = QgsApplication([], True)
        self.qgs.setPrefixPath('qgis', True)
        self.qgs.initQgis()
        self.qgs.setQuitOnLastWindowClosed(True)
        # self.qgs.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=qdarkstyle.LightPalette))
        # self.qgs.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        Processing.initialize()
        self.win = MainWindow()
        self.splash = SplashScreen()

    def run(self):
        self.splash.show()
        time.sleep(2)
        self.win.show()
        self.splash.finish(self.win)
        sys.exit(self.qgs.exec_())


if __name__ == "__main__":
    app = App()
    app.run()
