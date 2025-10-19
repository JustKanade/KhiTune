# coding:utf-8
from PyQt5.QtCore import QSize, QTimer, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QPainter
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme,
                            NavigationAvatarWidget)
from qfluentwidgets import FluentIcon as FIF

from .home_interface import HomeInterface
from .latest_interface import LatestInterface
from .setting_interface import SettingInterface
from ..common.config import cfg, APP_NAME
from ..common.signal_bus import signalBus
from ..background import BackgroundManager


class MainWindow(FluentWindow):
    """ Main window """

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create background manager
        self.backgroundManager = BackgroundManager()

        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.latestInterface = LatestInterface(self)
        self.settingInterface = SettingInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        # start theme listener
        self.themeListener.start()

    def connectSignalToSlot(self):
        """ Connect signal to slot """
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.backgroundChanged.connect(self.update)

    def openGitHub(self):
        QDesktopServices.openUrl(QUrl("https://github.com/JustKanade"))

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.latestInterface, FIF.MUSIC, self.tr('Latest'))
        
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('Vieleck', 'app/resource/Vieleck.png'),
            onClick=self.openGitHub,
            position=NavigationItemPosition.BOTTOM,
        )
        
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)
        
        self.navigationInterface.setExpandWidth(190)
        self.navigationInterface.setCollapsible(False)

    def initWindow(self):
        """ Initialize window """
        self.resize(960, 600)
        self.setMinimumWidth(800)
        self.setWindowIcon(QIcon('app/resource/logo/logo.png'))
        self.setWindowTitle(APP_NAME)

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        """ Resize event """
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        """ Close event """
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        """ Theme changed finished """
        super()._onThemeChangedFinished()

        # retry mica effect
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))
    
    def paintEvent(self, event):
        """ Paint event for background rendering """
        super().paintEvent(event)
        
        # check if background manager is initialized
        if not hasattr(self, 'backgroundManager'):
            return
        
        if self.backgroundManager.is_background_enabled():
            painter = QPainter(self)
            background_pixmap = self.backgroundManager.get_background_pixmap(self.size())
            
            if background_pixmap:
                # set opacity
                opacity = self.backgroundManager.get_background_opacity() / 100.0
                painter.setOpacity(opacity)
                
                # draw background
                painter.drawPixmap(0, 0, background_pixmap)
                painter.end()

