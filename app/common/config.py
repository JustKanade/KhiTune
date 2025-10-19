# coding:utf-8
import sys
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, ConfigSerializer, __version__)


class ProxyValidator:
    """ Proxy address validator """
    
    def validate(self, value):
        return isinstance(value, str)
    
    def correct(self, value):
        """ Correct proxy value """
        return str(value) if value is not None else ""


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    """ Check if system is Windows 11 """
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.ENGLISH, OptionsValidator(Language), LanguageSerializer(), restart=True)
    
    # proxy
    proxyEnabled = ConfigItem("Proxy", "Enabled", False, BoolValidator())
    proxyHost = ConfigItem("Proxy", "Host", "", ProxyValidator())
    proxyPort = ConfigItem("Proxy", "Port", "", ProxyValidator())


YEAR = 2024
AUTHOR = "Developer"
VERSION = __version__
APP_NAME = "KhiTune"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)

