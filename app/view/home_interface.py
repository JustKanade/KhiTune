# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, TitleLabel, BodyLabel

from ..common.style_sheet import StyleSheet


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        
        # create widgets
        self.titleLabel = TitleLabel(self.tr('Welcome to KhiTune'), self.view)
        self.descLabel = BodyLabel(
            self.tr('A modern tool for browsing and downloading video game soundtracks from KHInsider.'),
            self.view
        )
        self.descLabel.setWordWrap(True)

        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ Initialize widget """
        self.setObjectName('homeInterface')
        self.setWidgetResizable(True)
        self.setWidget(self.view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # set object name for styling
        self.view.setObjectName('view')
        StyleSheet.HOME_INTERFACE.apply(self)

    def __initLayout(self):
        """ Initialize layout """
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.descLabel)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

