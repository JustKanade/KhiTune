# coding:utf-8
from PyQt5.QtCore import Qt, QUrl, QRectF
from PyQt5.QtGui import QDesktopServices, QPixmap, QFont, QPainter, QPainterPath, QBrush
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from qfluentwidgets import CardWidget, IconWidget, FluentIcon, BodyLabel, CaptionLabel

from ..utils import ImageLoader


class AlbumCard(CardWidget):
    """ Album card with cover image following WinUI design """

    def __init__(self, title: str, platform: str, albumType: str, year: str, 
                 url: str, coverUrl: str = None, parent=None):
        super().__init__(parent=parent)
        self.url = QUrl(url)
        self.coverUrl = coverUrl
        
        # create widgets
        self.coverLabel = QLabel(self)
        self.titleLabel = BodyLabel(title, self)
        self.platformLabel = CaptionLabel(platform, self)
        self.metaLabel = CaptionLabel(f"{albumType} • {year}", self)
        self.iconWidget = IconWidget(FluentIcon.MUSIC, self)
        
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        
        self.imageLoader = None
        
        self.__initWidget()
        self.__loadCover()
    
    def __initWidget(self):
        """ Initialize widget """
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(96)
        
        # setup cover label
        self.coverLabel.setFixedSize(64, 64)
        self.coverLabel.setScaledContents(False)
        self.coverLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)
        
        # setup icon (fallback)
        self.iconWidget.setFixedSize(64, 64)
        self.iconWidget.setIcon(FluentIcon.MUSIC)
        self.iconWidget.hide()  # hide initially, show if cover fails to load
        
        # setup title with bold font
        self.titleLabel.setWordWrap(False)
        font = self.titleLabel.font()
        font.setPointSize(13)
        font.setBold(True)
        self.titleLabel.setFont(font)
        
        # setup platform and meta labels with secondary color
        self.platformLabel.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        self.metaLabel.setStyleSheet("color: rgba(255, 255, 255, 0.45);")
        
        # setup layouts
        self.hBoxLayout.setSpacing(12)
        self.hBoxLayout.setContentsMargins(12, 16, 16, 16)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        # add widgets
        self.hBoxLayout.addWidget(self.coverLabel, 0, Qt.AlignTop)
        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignTop)
        self.hBoxLayout.addLayout(self.vBoxLayout, 1)
        
        self.vBoxLayout.addSpacing(2)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.platformLabel)
        self.vBoxLayout.addWidget(self.metaLabel)
        self.vBoxLayout.addStretch(1)
        
        # set object names for styling
        self.titleLabel.setObjectName('albumTitleLabel')
        self.platformLabel.setObjectName('albumPlatformLabel')
        self.metaLabel.setObjectName('albumMetaLabel')
    
    def __loadCover(self):
        """ Load cover image """
        if self.coverUrl:
            self.imageLoader = ImageLoader(self.coverUrl, self)
            self.imageLoader.finished.connect(self.__onCoverLoaded)
            self.imageLoader.failed.connect(self.__onCoverFailed)
            self.imageLoader.start()
        else:
            self.__onCoverFailed()
    
    def __onCoverLoaded(self, pixmap: QPixmap):
        """ Handle cover loaded """
        if not pixmap.isNull():
            # scale pixmap to fit
            scaled = pixmap.scaled(
                64, 64, 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            # crop to center
            if scaled.width() > 64 or scaled.height() > 64:
                x = (scaled.width() - 64) // 2
                y = (scaled.height() - 64) // 2
                scaled = scaled.copy(x, y, 64, 64)
            
            # apply rounded corners
            rounded = self.__createRoundedPixmap(scaled, 4)
            self.coverLabel.setPixmap(rounded)
        else:
            self.__onCoverFailed()
    
    def __createRoundedPixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """ Create pixmap with rounded corners """
        # create a new pixmap with transparency
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)
        
        # create painter
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # create rounded rectangle path
        path = QPainterPath()
        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        path.addRoundedRect(rect, radius, radius)
        
        # clip to rounded rectangle and draw pixmap
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return rounded
    
    def __onCoverFailed(self):
        """ Handle cover load failed """
        self.coverLabel.hide()
        self.iconWidget.show()
    
    def mouseReleaseEvent(self, e):
        """ Handle mouse release """
        super().mouseReleaseEvent(e)
        QDesktopServices.openUrl(self.url)

