import sys
import time

from qgis.core import QgsApplication

from gui.MainWindow import MainWindow
from SplashScreen import SplashScreen
import config


class App:

    def __init__(self):
        config.setup_env()
        self.qgs = QgsApplication([], True)
        self.qgs.setPrefixPath('qgis', True)
        self.qgs.initQgis()
        self.qgs.setQuitOnLastWindowClosed(True)
        # Processing.initialize()
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
