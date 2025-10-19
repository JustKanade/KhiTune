# coding:utf-8
import os
from typing import Optional
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter
from ..common.config import cfg


class BackgroundManager:
    """ Background image manager with blur effects and caching """
    
    def __init__(self):
        self._cache = {}
        self._cache_key = None
    
    def is_background_enabled(self) -> bool:
        """ Check if background image is enabled """
        return cfg.get(cfg.backgroundImageEnabled)
    
    def get_background_path(self) -> str:
        """ Get background image path """
        return cfg.get(cfg.backgroundImagePath)
    
    def get_background_opacity(self) -> int:
        """ Get background opacity (0-100) """
        return cfg.get(cfg.backgroundOpacity)
    
    def get_background_blur_radius(self) -> int:
        """ Get background blur radius (0-50) """
        return cfg.get(cfg.backgroundBlurRadius)
    
    def get_background_pixmap(self, window_size: QSize) -> Optional[QPixmap]:
        """
        Get processed background pixmap

        Parameters
        ----------
        window_size: QSize
            target window size for scaling

        Returns
        -------
        pixmap: Optional[QPixmap]
            processed background pixmap or None
        """
        if not self.is_background_enabled():
            return None
        
        image_path = self.get_background_path()
        if not image_path or not os.path.exists(image_path):
            return None
        
        # generate cache key
        blur_radius = self.get_background_blur_radius()
        cache_key = (image_path, window_size.width(), window_size.height(), blur_radius)
        
        # return from cache if available
        if cache_key == self._cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        
        # load and process image
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return None
        
        # scale to window size maintaining aspect ratio
        pixmap = pixmap.scaled(
            window_size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        
        # crop to exact size
        if pixmap.width() > window_size.width() or pixmap.height() > window_size.height():
            x = (pixmap.width() - window_size.width()) // 2
            y = (pixmap.height() - window_size.height()) // 2
            pixmap = pixmap.copy(x, y, window_size.width(), window_size.height())
        
        # apply blur effect
        if blur_radius > 0:
            pixmap = self._apply_efficient_blur(pixmap, blur_radius)
        
        # update cache
        self._clear_cache()
        self._cache[cache_key] = pixmap
        self._cache_key = cache_key
        
        return pixmap
    
    def _apply_efficient_blur(self, pixmap: QPixmap, radius: int) -> QPixmap:
        """
        Apply efficient blur using scale-down/scale-up technique

        Parameters
        ----------
        pixmap: QPixmap
            source pixmap
        radius: int
            blur radius (0-50)

        Returns
        -------
        blurred: QPixmap
            blurred pixmap
        """
        if radius <= 0:
            return pixmap
        
        # calculate scale factor for optimization
        scale_factor = max(0.25, 1.0 - (radius / 100.0))
        
        # scale down
        small_size = QSize(
            int(pixmap.width() * scale_factor),
            int(pixmap.height() * scale_factor)
        )
        
        # prevent too small size
        if small_size.width() < 10 or small_size.height() < 10:
            return pixmap
        
        small_pixmap = pixmap.scaled(
            small_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # scale back up
        blurred = small_pixmap.scaled(
            pixmap.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        return blurred
    
    def _clear_cache(self):
        """ Clear cache """
        self._cache.clear()
        self._cache_key = None
    
    @staticmethod
    def validate_image_path(path: str) -> bool:
        """
        Validate image file path

        Parameters
        ----------
        path: str
            image file path

        Returns
        -------
        valid: bool
            whether path is valid
        """
        if not path or not os.path.exists(path):
            return False
        
        # check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        _, ext = os.path.splitext(path.lower())
        
        return ext in valid_extensions

