# coding:utf-8
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import ScrollArea, SubtitleLabel, IndeterminateProgressRing, BodyLabel, Pivot, PushButton, FluentIcon

from ..common.style_sheet import StyleSheet
from ..api import KhinsiderAPI
from ..components import AlbumCard


class FetchAlbumsThread(QThread):
    """ Thread for fetching albums """
    
    finished = pyqtSignal(list)
    
    def __init__(self, category='latest', limit=20, parent=None):
        super().__init__(parent)
        self.category = category
        self.limit = limit
        
    def run(self):
        albums = KhinsiderAPI.fetchAlbumsByCategory(self.category, self.limit)
        self.finished.emit(albums)


class AlbumListWidget(ScrollArea):
    """ Album list widget for each category """
    
    def __init__(self, category='latest', parent=None):
        super().__init__(parent=parent)
        self.category = category
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        
        # create widgets
        self.loadingRing = IndeterminateProgressRing(self.view)
        self.loadingLabel = BodyLabel(self.tr('Loading soundtracks...'), self.view)
        self.errorLabel = None
        self.retryButton = None
        
        self.fetchThread = None
        self.isLoaded = False
        
        self.__initWidget()
        self.__initLayout()
    
    def __initWidget(self):
        """ Initialize widget """
        self.setObjectName(f'{self.category}AlbumList')
        self.setWidgetResizable(True)
        self.setWidget(self.view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # set object name for styling
        self.view.setObjectName('view')
        StyleSheet.HOME_INTERFACE.apply(self)
        
        # setup loading widgets
        self.loadingRing.setFixedSize(60, 60)
        self.loadingRing.setStrokeWidth(5)
        self.loadingLabel.setAlignment(Qt.AlignCenter)
    
    def __initLayout(self):
        """ Initialize layout """
        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.addSpacing(40)
        self.vBoxLayout.addWidget(self.loadingRing, 0, Qt.AlignCenter)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.loadingLabel, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
    
    def loadAlbums(self):
        """ Load albums from KHInsider """
        if self.isLoaded:
            return
        
        # show loading widgets if retrying
        if self.errorLabel:
            self.loadingRing.show()
            self.loadingLabel.show()
            if self.errorLabel:
                self.errorLabel.hide()
            if self.retryButton:
                self.retryButton.hide()
        
        self.fetchThread = FetchAlbumsThread(self.category, 20, self)
        self.fetchThread.finished.connect(self.__onAlbumsFetched)
        self.fetchThread.start()
    
    def __onAlbumsFetched(self, albums):
        """ Handle fetched albums """
        # remove loading widgets
        self.loadingRing.hide()
        self.loadingLabel.hide()
        
        if not albums:
            self.__showErrorState()
            return
        
        self.isLoaded = True
        
        # remove the initial spacing before adding cards
        # layout order: spacing(40), loadingRing, spacing(16), loadingLabel, stretch
        item = self.vBoxLayout.itemAt(0)
        if item and item.spacerItem():
            self.vBoxLayout.removeItem(item)
        
        # add album cards
        for album in albums:
            card = AlbumCard(
                title=album['title'],
                platform=album['platform'],
                albumType=album['type'],
                year=album['year'],
                url=album['url'],
                coverUrl=album.get('cover'),
                parent=self.view
            )
            self.vBoxLayout.insertWidget(self.vBoxLayout.count() - 1, card)
    
    def __showErrorState(self):
        """ Show error state with retry button """
        if not self.errorLabel:
            self.errorLabel = BodyLabel(
                self.tr('Failed to load soundtracks. Please check your internet connection.'), 
                self.view
            )
            self.errorLabel.setAlignment(Qt.AlignCenter)
            self.errorLabel.setWordWrap(True)
            self.vBoxLayout.insertWidget(1, self.errorLabel)
        else:
            self.errorLabel.show()
        
        if not self.retryButton:
            self.retryButton = PushButton(FluentIcon.SYNC, self.tr('Retry'), self.view)
            self.retryButton.clicked.connect(self.__onRetryClicked)
            self.vBoxLayout.insertWidget(2, self.retryButton, 0, Qt.AlignCenter)
        else:
            self.retryButton.show()
    
    def __onRetryClicked(self):
        """ Handle retry button clicked """
        self.loadAlbums()


class LatestInterface(QWidget):
    """ Latest soundtracks interface with category tabs """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout(self)
        
        # create widgets
        self.titleLabel = SubtitleLabel(self.tr('Soundtracks from KHInsider'), self)
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        
        # create category widgets
        self.latestWidget = AlbumListWidget('latest', self)
        self.top40Widget = AlbumListWidget('top40', self)
        self.newlyAddedWidget = AlbumListWidget('newly_added', self)
        self.mostFavoritesWidget = AlbumListWidget('most_favorites', self)

        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ Initialize widget """
        self.setObjectName('latestInterface')
        
        # add sub interfaces to pivot
        self.addSubInterface(self.latestWidget, 'latest', self.tr('Latest'))
        self.addSubInterface(self.top40Widget, 'top40', self.tr('Top 40'))
        self.addSubInterface(self.newlyAddedWidget, 'newly_added', self.tr('Newly Added'))
        self.addSubInterface(self.mostFavoritesWidget, 'most_favorites', self.tr('Most Favorites'))
        
        # set current widget
        self.stackedWidget.setCurrentWidget(self.latestWidget)
        self.pivot.setCurrentItem(self.latestWidget.objectName())
        
        # connect signals
        self.pivot.currentItemChanged.connect(self.__onCurrentIndexChanged)
        
        # load first category
        self.latestWidget.loadAlbums()

    def __initLayout(self):
        """ Initialize layout """
        self.vBoxLayout.setContentsMargins(36, 36, 36, 0)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
    
    def addSubInterface(self, widget: AlbumListWidget, objectName: str, text: str):
        """ Add sub interface """
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)
    
    def __onCurrentIndexChanged(self, routeKey: str):
        """ Handle current index changed """
        widget = self.findChild(AlbumListWidget, routeKey)
        if widget:
            self.stackedWidget.setCurrentWidget(widget)
            widget.loadAlbums()

