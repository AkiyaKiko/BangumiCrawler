# scraper/directory.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from config import MAIN_URL, HEADERS
from utils.proxy_manager import get_random_proxy

async def fetch(session, url):
    """异步获取网页内容"""
    proxy = get_random_proxy()  # 使用代理池中的代理
    async with session.get(url, headers=HEADERS, proxy=proxy) as response:
        return await response.text()

async def get_total_pages(session, year):
    """获取指定年份的番剧总页数"""
    page_num = 1
    while True:
        url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            return page_num - 1  # 总页数
        page_num += 1

async def get_anime_list(session, year, total_pages):
    """获取指定年份和页数的所有番剧信息"""
    tasks = []
    for page_num in range(1, total_pages + 1):
        url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
        tasks.append(fetch(session, url))

    pages_content = await asyncio.gather(*tasks)
    anime_list = []
    for html in pages_content:
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")
        for item in browser_item_list.find_all('li', class_='item'):
            title_tag = item.find('h3').find('a') if item.find('h3') else None
            anime_name = title_tag.text.strip() if title_tag else "Unknown"
            sub_url = title_tag['href'] if title_tag else "#"
            anime_list.append((anime_name, sub_url))
    
    return anime_list
