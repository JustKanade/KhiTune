# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel
from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup, SwitchSettingCard,
                            OptionsSettingCard, CustomColorSettingCard, LineEdit, setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF

from ..common.config import cfg, Language
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from .proxy_host_card import ProxyHostCard


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # personalization group
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr('Change the appearance of your application'),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self.personalGroup
        )
        self.languageCard = OptionsSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )
        self.dpiCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        
        # network group
        self.networkGroup = SettingCardGroup(
            self.tr('Network'), self.scrollWidget)
        self.proxyEnableCard = SwitchSettingCard(
            FIF.GLOBE,
            self.tr('Proxy server'),
            self.tr('Enable proxy for network requests'),
            cfg.proxyEnabled,
            self.networkGroup
        )
        self.proxyHostCard = ProxyHostCard(
            FIF.CONNECT,
            self.tr('Proxy address'),
            self.tr('Set proxy host and port'),
            self.networkGroup
        )

        self.__initWidget()

    def __initWidget(self):
        """ Initialize widget """
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ Initialize layout """
        self.settingLabel.move(36, 30)

        # add cards to group
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.languageCard)
        self.personalGroup.addSettingCard(self.dpiCard)
        
        self.networkGroup.addSettingCard(self.proxyEnableCard)
        self.networkGroup.addSettingCard(self.proxyHostCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.networkGroup)
        
        # load proxy settings
        self.__loadProxySettings()

    def __connectSignalToSlot(self):
        """ Connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)
        
        # proxy settings
        self.proxyEnableCard.checkedChanged.connect(self.__onProxyEnabledChanged)
        self.proxyHostCard.hostLineEdit.textChanged.connect(self.__onProxyHostChanged)
        self.proxyHostCard.portLineEdit.textChanged.connect(self.__onProxyPortChanged)
    
    def __loadProxySettings(self):
        """ Load proxy settings from config """
        self.proxyHostCard.setHost(cfg.get(cfg.proxyHost))
        self.proxyHostCard.setPort(cfg.get(cfg.proxyPort))
        self.__updateProxyHostCardState()
    
    def __onProxyEnabledChanged(self, checked: bool):
        """ Handle proxy enabled changed """
        self.__updateProxyHostCardState()
    
    def __updateProxyHostCardState(self):
        """ Update proxy host card enabled state """
        enabled = self.proxyEnableCard.isChecked()
        self.proxyHostCard.setEnabled(enabled)
    
    def __onProxyHostChanged(self, text: str):
        """ Handle proxy host changed """
        cfg.set(cfg.proxyHost, text)
    
    def __onProxyPortChanged(self, text: str):
        """ Handle proxy port changed """
        cfg.set(cfg.proxyPort, text)

    def __showRestartTooltip(self):
        """ Show restart tooltip """
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

