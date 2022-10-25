import os
import random

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__()

        self.imgs = [os.path.join('res/bg', file) for file in os.listdir('./res/bg')]
        if not self.imgs:
            raise ValueError("Splash screen img is missing.")
        self.setPixmap(QPixmap(random.choice(self.imgs)).scaledToHeight(600))
        self.showMessage("热烈欢迎领导莅临检查工作", Qt.AlignCenter | Qt.AlignBottom, Qt.white)
