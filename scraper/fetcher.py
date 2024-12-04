# scraper/fetcher.py

import aiohttp
from bs4 import BeautifulSoup
from config import MAIN_URL, HEADERS
from utils.proxy_manager import get_random_proxy

async def fetch(session, url):
    """异步获取网页内容"""
    proxy = get_random_proxy()
    async with session.get(url, headers=HEADERS, proxy=proxy) as response:
        return await response.text()

async def get_anime_details(session, sub_url):
    """获取单个番剧的详细信息（评分、分类、制作等）"""
    url = f"{MAIN_URL}{sub_url}"
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'lxml')
    
    # 获取详细信息（评分、分类、制作等）
    score = soup.find('div', class_='score')
    category = soup.find('span', class_='category')
    studio = soup.find('span', class_='studio')

    return {
        'score': score.text.strip() if score else 'N/A',
        'category': category.text.strip() if category else 'N/A',
        'studio': studio.text.strip() if studio else 'N/A'
    }
