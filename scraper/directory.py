import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from config import MAIN_URL, HEADERS
from utils.proxy_manager import get_random_proxy

async def fetch(session, url):
    """异步获取网页内容"""
    proxy = get_random_proxy()  # 使用代理池中的代理
    async with session.get(url, headers=HEADERS, proxy=proxy) as response:
        return await response.text()

def extract_release_date(text):
    """从文本中提取上映日期，处理两种日期格式"""
    # 优化的正则表达式，匹配 1979-01-05 或 1979年01月05日 格式
    match1 = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)  # yyyy-mm-dd 格式
    if match1:
        # 如果匹配到 yyyy-mm-dd 格式，直接返回
        return f"{match1.group(1)}-{match1.group(2).zfill(2)}-{match1.group(3).zfill(2)}"
    
    # 如果没有匹配到 yyyy-mm-dd 格式，尝试匹配 yyyy年mm月dd日 格式
    match2 = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)  # yyyy年mm月dd日 格式
    if match2:
        # 如果匹配到 yyyy年mm月dd日 格式，返回格式化后的日期
        return f"{match2.group(1)}-{match2.group(2).zfill(2)}-{match2.group(3).zfill(2)}"
    
    # 如果没有匹配到任何日期格式，返回 None
    return None

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
            
            # 获取上映时间
            info_tag = item.find('p', class_='info tip')
            release_date = None
            if info_tag:
                release_text = info_tag.text.strip()
                release_date = extract_release_date(release_text)
                
            anime_list.append((anime_name, sub_url, release_date))
    
    return anime_list
