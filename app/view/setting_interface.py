# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QHBoxLayout
from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup, SwitchSettingCard,
                            OptionsSettingCard, CustomColorSettingCard, LineEdit, setTheme, 
                            setThemeColor, isDarkTheme, RangeSettingCard, PushSettingCard,
                            InfoBar, ExpandSettingCard, SettingCard, PushButton)
from qfluentwidgets import FluentIcon as FIF

from ..common.config import cfg, Language
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from .proxy_host_card import ProxyHostCard
from ..background import BackgroundManager


class BackgroundImageCard(SettingCard):
    """ Custom setting card with select and clear buttons for background image """
    
    def __init__(self, title, content, icon, parent=None):
        super().__init__(icon, title, content, parent)
        
        # create buttons
        self.selectButton = PushButton(self.tr('Select image'), self)
        self.clearButton = PushButton(self.tr('Clear'), self)
        
        # create button layout
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        self.buttonLayout.addWidget(self.selectButton)
        self.buttonLayout.addWidget(self.clearButton)
        
        # add button layout to the card
        self.hBoxLayout.addLayout(self.buttonLayout)
        self.hBoxLayout.addSpacing(16)
        
        # initialize display
        self._updateDisplay()
    
    def _updateDisplay(self):
        """ Update the card display based on current background image path """
        bg_path = cfg.get(cfg.backgroundImagePath)
        if bg_path:
            import os
            file_name = os.path.basename(bg_path)
            self.setContent(f"{self.tr('Selected')}: {file_name}")
            self.clearButton.setEnabled(True)
        else:
            self.setContent(self.tr('Choose a custom background image file'))
            self.clearButton.setEnabled(False)


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
        
        # background group - use ExpandSettingCard for collapsible section
        self.backgroundGroup = ExpandSettingCard(
            FIF.PHOTO,
            self.tr('Background'),
            self.tr('Customize application background settings'),
            self.scrollWidget)
        self.backgroundEnableCard = SwitchSettingCard(
            FIF.PHOTO,
            self.tr('Background image'),
            self.tr('Enable custom background image for main window'),
            cfg.backgroundImageEnabled,
            self.backgroundGroup
        )
        self.backgroundFileCard = BackgroundImageCard(
            self.tr('Background file'),
            self.tr('Choose a custom background image file'),
            FIF.FOLDER,
            self.backgroundGroup
        )
        self.backgroundOpacityCard = RangeSettingCard(
            cfg.backgroundOpacity,
            FIF.TRANSPARENT,
            self.tr('Background opacity'),
            self.tr('Adjust the opacity of background image (0-100)'),
            self.backgroundGroup
        )
        self.backgroundBlurCard = RangeSettingCard(
            cfg.backgroundBlurRadius,
            FIF.BRUSH,
            self.tr('Background blur'),
            self.tr('Adjust the blur radius of background image (0-50)'),
            self.backgroundGroup
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
        
        # add widgets to expand card view instead of as setting cards
        self.backgroundGroup.viewLayout.addWidget(self.backgroundEnableCard)
        self.backgroundGroup.viewLayout.addWidget(self.backgroundFileCard)
        self.backgroundGroup.viewLayout.addWidget(self.backgroundOpacityCard)
        self.backgroundGroup.viewLayout.addWidget(self.backgroundBlurCard)
        self.backgroundGroup._adjustViewSize()
        
        self.networkGroup.addSettingCard(self.proxyEnableCard)
        self.networkGroup.addSettingCard(self.proxyHostCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.backgroundGroup)
        self.expandLayout.addWidget(self.networkGroup)
        
        # load proxy settings
        self.__loadProxySettings()
        
        # update background card states
        self.__updateBackgroundCardStates()

    def __connectSignalToSlot(self):
        """ Connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)
        
        # background settings
        self.backgroundEnableCard.checkedChanged.connect(self.__onBackgroundEnabledChanged)
        self.backgroundFileCard.selectButton.clicked.connect(self.__onChooseBackgroundFile)
        self.backgroundFileCard.clearButton.clicked.connect(self.__onClearBackgroundImage)
        self.backgroundOpacityCard.valueChanged.connect(self.__onBackgroundSettingChanged)
        self.backgroundBlurCard.valueChanged.connect(self.__onBackgroundSettingChanged)
        
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

    def __onBackgroundEnabledChanged(self, checked: bool):
        """ Handle background enabled changed """
        self.__updateBackgroundCardStates()
        self.__onBackgroundSettingChanged()
    
    def __updateBackgroundCardStates(self):
        """ Update background card enabled states """
        enabled = self.backgroundEnableCard.isChecked()
        self.backgroundFileCard.setEnabled(enabled)
        self.backgroundOpacityCard.setEnabled(enabled)
        self.backgroundBlurCard.setEnabled(enabled)
    
    def __onChooseBackgroundFile(self):
        """ Handle choose background file """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Choose background image"),
            "",
            self.tr("Image files") + " (*.jpg *.jpeg *.png *.bmp *.gif *.webp)"
        )
        
        if file_path:
            # validate image
            if BackgroundManager.validate_image_path(file_path):
                cfg.set(cfg.backgroundImagePath, file_path)
                self.backgroundFileCard._updateDisplay()
                self.__onBackgroundSettingChanged()
            else:
                InfoBar.error(
                    self.tr('Invalid image'),
                    self.tr('Please select a valid image file'),
                    duration=2000,
                    parent=self
                )
    
    def __onClearBackgroundImage(self):
        """ Handle clear background image """
        cfg.set(cfg.backgroundImagePath, "")
        self.backgroundFileCard._updateDisplay()
        self.__onBackgroundSettingChanged()
    
    def __onBackgroundSettingChanged(self):
        """ Handle background setting changed """
        # trigger main window repaint
        signalBus.backgroundChanged.emit()

    def __showRestartTooltip(self):
        """ Show restart tooltip """
        from qfluentwidgets import InfoBar, InfoBarPosition
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

