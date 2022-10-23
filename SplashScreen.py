from PyQt5.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.welcome_msg = "热烈欢迎领导莅临检查工作"
