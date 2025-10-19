# coding:utf-8
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class KhinsiderAPI:
    """ KHInsider API wrapper """

    BASE_URL = "https://downloads.khinsider.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    CATEGORY_URLS = {
        'latest': '',
        'top40': '/game-soundtracks/browse/top-40',
        'newly_added': '/game-soundtracks/browse/newly-added',
        'most_favorites': '/game-soundtracks/browse/most-favorites'
    }

    @classmethod
    def fetchAlbumsByCategory(cls, category='latest', limit=10) -> List[Dict]:
        """
        Fetch albums by category

        Parameters
        ----------
        category: str
            category name: 'latest', 'top40', 'newly_added', 'most_favorites'
        limit: int
            number of albums to fetch

        Returns
        -------
        albums: List[Dict]
            list of album dictionaries with keys: title, platform, type, year, url, cover
        """
        url_path = cls.CATEGORY_URLS.get(category, '')
        return cls._fetchAlbumsFromUrl(cls.BASE_URL + url_path, limit)

    @classmethod
    def fetchLatestAlbums(cls, limit=10) -> List[Dict]:
        """
        Fetch latest albums from KHInsider (alias for fetchAlbumsByCategory)

        Parameters
        ----------
        limit: int
            number of albums to fetch

        Returns
        -------
        albums: List[Dict]
            list of album dictionaries with keys: title, platform, type, year, url, cover
        """
        return cls.fetchAlbumsByCategory('latest', limit)
    
    @classmethod
    def _fetchAlbumsFromUrl(cls, url: str, limit=10) -> List[Dict]:
        """
        Internal method to fetch albums from a specific URL

        Parameters
        ----------
        url: str
            URL to fetch albums from
        limit: int
            number of albums to fetch

        Returns
        -------
        albums: List[Dict]
            list of album dictionaries
        """
        try:
            response = requests.get(url, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            albums = []
            
            # find album table
            table = soup.find('table')
            if not table:
                return []
            
            rows = table.find_all('tr')[1:]  # skip header
            
            for row in rows[:limit]:
                cols = row.find_all('td')
                if len(cols) < 5:
                    continue
                
                # extract cover image from column 0
                cover_img = cols[0].find('img')
                cover_url = None
                if cover_img:
                    cover_src = cover_img.get('src', '')
                    if cover_src.startswith('/'):
                        cover_url = cls.BASE_URL + cover_src
                    elif cover_src.startswith('http'):
                        cover_url = cover_src
                
                # extract title from column 1
                album_link = cols[1].find('a')
                if not album_link:
                    continue
                
                title = album_link.text.strip()
                album_url = cls.BASE_URL + album_link.get('href', '')
                
                # extract platform from column 2
                platform_cell = cols[2]
                platforms = [a.text.strip() for a in platform_cell.find_all('a')]
                platform = ', '.join(platforms) if platforms else 'Unknown'
                
                # extract type from column 3
                album_type = cols[3].text.strip() if len(cols) > 3 else 'Unknown'
                
                # extract year from column 4
                year = cols[4].text.strip() if len(cols) > 4 else 'Unknown'
                
                albums.append({
                    'title': title,
                    'platform': platform,
                    'type': album_type,
                    'year': year,
                    'url': album_url,
                    'cover': cover_url
                })
            
            return albums
            
        except Exception as e:
            print(f"Error fetching albums from {url}: {e}")
            return []
    
    @classmethod
    def fetchAlbumCover(cls, album_url: str) -> Optional[str]:
        """
        Fetch album cover image URL from album page

        Parameters
        ----------
        album_url: str
            album page URL

        Returns
        -------
        cover_url: Optional[str]
            cover image URL or None
        """
        try:
            response = requests.get(album_url, headers=cls.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # find cover image in album page
            cover_div = soup.find('div', {'id': 'coverImage'})
            if cover_div:
                img = cover_div.find('img')
                if img:
                    cover_src = img.get('src', '')
                    if cover_src.startswith('/'):
                        return cls.BASE_URL + cover_src
                    elif cover_src.startswith('http'):
                        return cover_src
            
            return None
            
        except Exception as e:
            print(f"Error fetching album cover: {e}")
            return None

