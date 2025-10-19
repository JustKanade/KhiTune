# coding:utf-8
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    def fetchAlbumTracks(cls, album_url: str) -> List[Dict]:
        """
        Fetch tracks from album page

        Parameters
        ----------
        album_url: str
            album page URL

        Returns
        -------
        tracks: List[Dict]
            list of track dictionaries with keys: name, duration
        """
        try:
            response = requests.get(album_url, headers=cls.HEADERS, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tracks = []
            
            # find track table
            table = soup.find('table', {'id': 'songlist'})
            if not table:
                return []
            
            rows = table.find_all('tr')[1:]  # skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                
                # extract track name from third column (index 2)
                track_link = cols[2].find('a')
                if not track_link:
                    continue
                
                track_name = track_link.text.strip()
                
                # extract duration from fourth column (index 3)
                duration = ''
                if len(cols) > 3:
                    duration = cols[3].text.strip()
                
                tracks.append({
                    'name': track_name,
                    'duration': duration
                })
            
            return tracks
            
        except Exception as e:
            print(f"Error fetching tracks from {album_url}: {e}")
            return []
    
    @classmethod
    def fetchAlbumCovers(cls, album_url: str) -> List[str]:
        """
        Fetch all album cover image URLs from album page

        Parameters
        ----------
        album_url: str
            album page URL

        Returns
        -------
        covers: List[str]
            list of cover image URLs
        """
        try:
            response = requests.get(album_url, headers=cls.HEADERS, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            covers = []
            
            # find all album image divs (class="albumImage")
            album_image_divs = soup.find_all('div', class_='albumImage')
            
            for div in album_image_divs:
                # find <a> tag within div, href points to full-size image
                link = div.find('a')
                if link:
                    cover_href = link.get('href', '')
                    if cover_href:
                        if cover_href.startswith('/'):
                            covers.append(cls.BASE_URL + cover_href)
                        elif cover_href.startswith('http'):
                            covers.append(cover_href)
            
            return covers
            
        except Exception as e:
            print(f"Error fetching album covers from {album_url}: {e}")
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

