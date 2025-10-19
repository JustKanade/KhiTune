# coding:utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):
    """ Translator for common text """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.home = self.tr('Home')
        self.settings = self.tr('Settings')

