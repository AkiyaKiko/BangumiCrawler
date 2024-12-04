import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
import random

# 常量定义
MAIN_URL = "https://bangumi.tv"
START_YEAR = 2023
END_YEAR = 2024  # Adjust based on the range you want
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/78.0.3904.108 Safari/537.36'
}

# 代理池
PROXIES = ["http://127.0.0.1:10809"]

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fetch(session, url):
    """异步获取网页内容"""
    # 使用随机代理
    #proxy = '''random.choice(PROXIES)'''
    async with session.get(url) as response:
        return await response.text()

async def fetch_main_page(session, year, page_num):
    """获取某一年份的指定页的番剧信息"""
    url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
    logger.info(f"Fetching page {page_num} for year {year}: {url}")

    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")

        # 检查是否有番剧信息
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            return

        # 提取每个番剧的基本信息
        for item in browser_item_list.find_all('li', class_='item'):
            title_tag = item.find('h3').find('a') if item.find('h3') else None
            anime_name = title_tag.text.strip() if title_tag else "Unknown"
            sub_url = title_tag['href'] if title_tag else "#"
            
            # You can extract more data like ratings, release date, etc. here.
            logger.info(f"Found anime: {anime_name}, URL: {sub_url}")

    except Exception as e:
        logger.error(f"Error fetching page {page_num} for year {year}: {e}")

async def find_total_pages(session, year):
    """获取指定年份的总页数"""
    page_num = 1
    while True:
        url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
        logger.info(f"Checking page {page_num} for year {year}: {url}")
        
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")
        
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            logger.info(f"Found the last page for year {year}: {page_num - 1}")
            return page_num - 1  # Total pages found
        page_num += 1

async def fetch_all_years_data(session):
    """获取所有年份的番剧信息"""
    tasks = []
    for year in range(START_YEAR, END_YEAR + 1):
        total_pages = await find_total_pages(session, year)  # Pass session here
        tasks.extend([fetch_main_page(session, year, page_num) for page_num in range(1, total_pages + 1)])

    await asyncio.gather(*tasks)

async def main():
    """主函数"""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # 获取所有年份的番剧数据
        await fetch_all_years_data(session)

# 运行程序
asyncio.run(main())
