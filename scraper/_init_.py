# scraper/__init__.py

from .directory import get_anime_list, get_total_pages
from .fetcher import get_anime_details
from .comments import get_comments

__all__ = ['get_anime_list', 'get_total_pages', 'get_anime_details', 'get_comments']
