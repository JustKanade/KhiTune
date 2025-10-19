# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from qfluentwidgets import SettingCard, LineEdit, FluentIconBase


class ProxyHostCard(SettingCard):
    """ Proxy host and port setting card """

    def __init__(self, icon: FluentIconBase, title: str, content: str = None, parent=None):
        super().__init__(icon, title, content, parent)
        
        # create widgets
        self.hostLabel = QLabel(self.tr('Host:'), self)
        self.hostLineEdit = LineEdit(self)
        self.portLabel = QLabel(self.tr('Port:'), self)
        self.portLineEdit = LineEdit(self)
        
        # setup widgets
        self.hostLineEdit.setPlaceholderText(self.tr('e.g., 127.0.0.1'))
        self.hostLineEdit.setFixedWidth(140)
        self.portLineEdit.setPlaceholderText(self.tr('e.g., 7890'))
        self.portLineEdit.setFixedWidth(100)
        
        # add widgets to layout
        self.inputLayout = QHBoxLayout()
        self.inputLayout.setSpacing(10)
        self.inputLayout.addWidget(self.hostLabel)
        self.inputLayout.addWidget(self.hostLineEdit)
        self.inputLayout.addSpacing(10)
        self.inputLayout.addWidget(self.portLabel)
        self.inputLayout.addWidget(self.portLineEdit)
        
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.inputLayout)
        self.hBoxLayout.addSpacing(16)
    
    def setHost(self, host: str):
        """ Set proxy host """
        self.hostLineEdit.setText(host)
    
    def getHost(self) -> str:
        """ Get proxy host """
        return self.hostLineEdit.text()
    
    def setPort(self, port: str):
        """ Set proxy port """
        self.portLineEdit.setText(port)
    
    def getPort(self) -> str:
        """ Get proxy port """
        return self.portLineEdit.text()
    
    def setEnabled(self, enabled: bool):
        """ Set card enabled state """
        super().setEnabled(enabled)
        self.hostLineEdit.setEnabled(enabled)
        self.portLineEdit.setEnabled(enabled)
        self.hostLabel.setEnabled(enabled)
        self.portLabel.setEnabled(enabled)

