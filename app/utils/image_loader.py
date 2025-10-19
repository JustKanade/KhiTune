# coding:utf-8
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from typing import Optional


class ImageLoader(QThread):
    """ Thread for loading images from URL """
    
    finished = pyqtSignal(QPixmap)
    failed = pyqtSignal()
    
    def __init__(self, url: Optional[str], parent=None):
        super().__init__(parent)
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def run(self):
        """ Load image from URL """
        if not self.url:
            self.failed.emit()
            return
        
        try:
            # create session with retry strategy
            session = requests.Session()
            retry = Retry(
                total=2,
                read=2,
                connect=2,
                backoff_factor=0.3,
                status_forcelist=(500, 502, 504)
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            # try to load image
            response = session.get(
                self.url, 
                headers=self.headers, 
                timeout=15,
                verify=True
            )
            response.raise_for_status()
            
            pixmap = QPixmap()
            if pixmap.loadFromData(response.content):
                self.finished.emit(pixmap)
            else:
                self.failed.emit()
                
        except requests.exceptions.SSLError:
            # retry without SSL verification if SSL error occurs
            try:
                response = requests.get(
                    self.url, 
                    headers=self.headers, 
                    timeout=15,
                    verify=False
                )
                response.raise_for_status()
                
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.finished.emit(pixmap)
                else:
                    self.failed.emit()
            except Exception:
                self.failed.emit()
                
        except Exception:
            self.failed.emit()

