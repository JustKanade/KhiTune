# coding:utf-8
from PyQt5.QtCore import Qt, QUrl, QEvent, QRectF, QSize
from PyQt5.QtGui import QDesktopServices, QPixmap, QPainter, QPainterPath
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel

from qfluentwidgets import (MessageBoxBase, SubtitleLabel, BodyLabel, CaptionLabel, 
                            ScrollArea, SingleDirectionScrollArea, PrimaryPushButton, 
                            TransparentPushButton, IndeterminateProgressRing, FluentIcon, isDarkTheme)
from qfluentwidgets.common.color import FluentSystemColor


class AlbumDetailDialog(MessageBoxBase):
    """ Album detail dialog """
    
    def __init__(self, albumData: dict, parent=None):
        super().__init__(parent)
        self.albumData = albumData
        self.tracks = []
        self.coverLabels = []
        self.imageLoaders = []
        
        self.titleLabel = SubtitleLabel(albumData.get('title', 'Unknown Album'))
        self.metaLabel = CaptionLabel()
        
        # cover scroll area
        self.coverScrollArea = SingleDirectionScrollArea(orient=Qt.Horizontal)
        self.coverWidget = QWidget()
        self.coverLayout = QHBoxLayout(self.coverWidget)
        
        # loading widget - centered container for loading animation
        self.loadingWidget = QWidget()
        self.loadingWidgetLayout = QVBoxLayout(self.loadingWidget)
        self.loadingRing = IndeterminateProgressRing()
        self.loadingLabel = BodyLabel(self.tr('Loading tracks...'))
        
        # track scroll area
        self.scrollArea = ScrollArea()
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.trackLabel = BodyLabel()
        
        self.__initWidget()
    
    def __initWidget(self):
        """ Initialize widget """
        # set window properties
        self.widget.setMinimumWidth(500)
        self.widget.setMaximumWidth(600)
        self.widget.setMaximumHeight(700)  # limit dialog height to prevent button occlusion
        
        # setup title
        self.titleLabel.setWordWrap(True)
        
        # setup meta info
        platform = self.albumData.get('platform', 'Unknown')
        albumType = self.albumData.get('type', 'Unknown')
        year = self.albumData.get('year', 'Unknown')
        self.metaLabel.setText(f"{platform} • {albumType} • {year}")
        self.metaLabel.setTextColor("#606060", "#d2d2d2")
        
        # setup cover scroll area
        self.coverScrollArea.setWidget(self.coverWidget)
        self.coverScrollArea.setWidgetResizable(True)
        self.coverScrollArea.setFixedHeight(170)
        self.coverScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.coverScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.coverScrollArea.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        # ensure viewport is transparent
        if self.coverScrollArea.viewport():
            self.coverScrollArea.viewport().setStyleSheet("background-color: transparent;")
        
        # setup cover widget
        self.coverWidget.setStyleSheet("background-color: transparent;")
        self.coverLayout.setContentsMargins(0, 0, 0, 0)
        self.coverLayout.setSpacing(12)
        self.coverLayout.setAlignment(Qt.AlignLeft)
        
        # setup scroll area
        self.scrollArea.setWidget(self.contentWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumHeight(100)
        self.scrollArea.setMaximumHeight(100)  # allow dynamic height up to 350px
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setObjectName('albumScrollArea')
        
        # setup content widget with transparent background
        self.contentWidget.setObjectName('contentWidget')
        
        # apply styles for both light and dark themes
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            #contentWidget {
                background-color: transparent;
            }
        """)
        
        # ensure viewport is also transparent
        if self.scrollArea.viewport():
            self.scrollArea.viewport().setStyleSheet("background-color: transparent;")
        
        # setup content layout
        self.contentLayout.setContentsMargins(12, 12, 12, 12)
        self.contentLayout.setAlignment(Qt.AlignTop)
        
        # setup track label
        self.trackLabel.setWordWrap(True)
        self.trackLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.trackLabel.setText(self.tr('Loading album information...'))
        self.contentLayout.addWidget(self.trackLabel)
        
        # setup loading widget
        self.loadingRing.setFixedSize(40, 40)
        self.loadingRing.setStrokeWidth(4)
        self.loadingWidget.setMinimumHeight(100)
        
        self.loadingWidgetLayout.addStretch(1)
        self.loadingWidgetLayout.addWidget(self.loadingRing, 0, Qt.AlignCenter)
        self.loadingWidgetLayout.addSpacing(12)
        self.loadingWidgetLayout.addWidget(self.loadingLabel, 0, Qt.AlignCenter)
        self.loadingWidgetLayout.addStretch(1)
        self.loadingWidgetLayout.setContentsMargins(0, 0, 0, 0)
        
        # add to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(4)
        self.viewLayout.addWidget(self.metaLabel)
        self.viewLayout.addSpacing(16)
        self.viewLayout.addWidget(self.coverScrollArea)
        self.viewLayout.addSpacing(12)
        self.viewLayout.addWidget(self.loadingWidget)
        self.viewLayout.addWidget(self.scrollArea)
        self.scrollArea.hide()  # hide until loaded
        
        # customize buttons
        self.yesButton.setText(self.tr('Open in Browser'))
        self.yesButton.setIcon(FluentIcon.LINK)
        self.cancelButton.setText(self.tr('Close'))
        
        self.yesButton.clicked.connect(self.__onOpenInBrowser)
    
    def setCovers(self, coverUrls: list):
        """ Set album cover images """
        if not coverUrls:
            # show placeholder if no covers
            self.__createPlaceholderCover()
            return
        
        # create a label for each cover
        for coverUrl in coverUrls:
            coverLabel = QLabel()
            coverLabel.setFixedSize(150, 150)
            coverLabel.setAlignment(Qt.AlignCenter)
            coverLabel.setScaledContents(False)
            coverLabel.setStyleSheet("QLabel { background-color: transparent; }")
            
            self.coverLabels.append(coverLabel)
            self.coverLayout.addWidget(coverLabel, 0, Qt.AlignLeft)
            
            # load cover image
            self.__loadCoverImage(coverUrl, coverLabel)
    
    def setTracks(self, tracks: list):
        """ Set album tracks """
        self.tracks = tracks
        self.loadingWidget.hide()  # hide loading widget
        self.scrollArea.show()
        
        # re-apply transparent background after showing
        if self.scrollArea.viewport():
            self.scrollArea.viewport().setStyleSheet("background-color: transparent;")
        
        if not tracks:
            self.trackLabel.setText(self.tr('No tracks found or failed to load.'))
            return
        
        # build track list text
        trackText = ""
        for i, track in enumerate(tracks, 1):
            trackName = track.get('name', 'Unknown')
            duration = track.get('duration', '')
            if duration:
                trackText += f"{i}. {trackName} - {duration}\n"
            else:
                trackText += f"{i}. {trackName}\n"
        
        self.trackLabel.setText(trackText.strip())
    
    def setError(self, errorMsg: str):
        """ Set error message """
        self.loadingRing.hide()
        self.loadingLabel.setText(errorMsg)
        # use system critical color for both light and dark themes
        criticalColor = FluentSystemColor.CRITICAL_FOREGROUND.color()
        self.loadingLabel.setStyleSheet(f"color: {criticalColor.name()};")
        # keep loadingWidget visible to show error message
    
    def __onOpenInBrowser(self):
        """ Open album in browser """
        url = self.albumData.get('url')
        if url:
            QDesktopServices.openUrl(QUrl(url))
        self.accept()
    
    def __loadCoverImage(self, coverUrl: str, targetLabel: QLabel):
        """ Load single cover image """
        from ..utils import ImageLoader
        
        if coverUrl:
            imageLoader = ImageLoader(coverUrl, self)
            imageLoader.finished.connect(lambda pixmap: self.__onCoverLoaded(pixmap, targetLabel))
            imageLoader.failed.connect(lambda: self.__onCoverFailed(targetLabel))
            imageLoader.start()
            self.imageLoaders.append(imageLoader)
        else:
            self.__onCoverFailed(targetLabel)
    
    def __onCoverLoaded(self, pixmap: QPixmap, targetLabel: QLabel):
        """ Handle cover loaded """
        if not pixmap.isNull():
            # scale and create rounded pixmap
            scaled = pixmap.scaled(
                150, 150,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            # crop to center
            if scaled.width() > 150 or scaled.height() > 150:
                x = (scaled.width() - 150) // 2
                y = (scaled.height() - 150) // 2
                scaled = scaled.copy(x, y, 150, 150)
            
            # apply rounded corners
            rounded = self.__createRoundedPixmap(scaled, 8)
            targetLabel.setPixmap(rounded)
            targetLabel.setStyleSheet("background-color: transparent;")
        else:
            self.__onCoverFailed(targetLabel)
    
    def __onCoverFailed(self, targetLabel: QLabel):
        """ Handle cover load failed """
        targetLabel.setText("🎵")
        font = targetLabel.font()
        font.setPointSize(48)
        targetLabel.setFont(font)
        # adaptive placeholder style for both themes
        if isDarkTheme():
            targetLabel.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    background-color: rgba(255, 255, 255, 0.05);
                    color: rgba(255, 255, 255, 0.3);
                }
            """)
        else:
            targetLabel.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    background-color: rgba(0, 0, 0, 0.05);
                    color: rgba(0, 0, 0, 0.3);
                }
            """)
    
    def __createPlaceholderCover(self):
        """ Create placeholder cover when no covers available """
        coverLabel = QLabel()
        coverLabel.setFixedSize(150, 150)
        coverLabel.setAlignment(Qt.AlignCenter)
        coverLabel.setText("🎵")
        font = coverLabel.font()
        font.setPointSize(48)
        coverLabel.setFont(font)
        # adaptive placeholder style for both themes
        if isDarkTheme():
            coverLabel.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    background-color: rgba(255, 255, 255, 0.05);
                    color: rgba(255, 255, 255, 0.3);
                }
            """)
        else:
            coverLabel.setStyleSheet("""
                QLabel {
                    border-radius: 8px;
                    background-color: rgba(0, 0, 0, 0.05);
                    color: rgba(0, 0, 0, 0.3);
                }
            """)
        self.coverLabels.append(coverLabel)
        self.coverLayout.addWidget(coverLabel, 0, Qt.AlignLeft)
    
    def __createRoundedPixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """ Create pixmap with rounded corners """
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        path = QPainterPath()
        rect = QRectF(0, 0, pixmap.width(), pixmap.height())
        path.addRoundedRect(rect, radius, radius)
        
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return rounded

