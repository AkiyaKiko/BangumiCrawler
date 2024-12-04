import aiohttp
import asyncio
import logging
import time
from bs4 import BeautifulSoup
import requests
import csv
from collections import Counter, defaultdict
import random

# 常量定义
MAIN_URL = "https://bangumi.tv"
START_YEAR = 2010
END_YEAR = 2024  # 如果你是测试可以将差值缩小
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/78.0.3904.108 Safari/537.36'
}

# 代理池
PROXIES = [
    "http://127.0.0.1:10809",
    # "http://proxy2_url:port",
    # "http://proxy3_url:port",
    # Add more proxies if needed
]

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量
tags_counter = Counter()
yearly_tags_counter = defaultdict(Counter)
anime_data = []

def get_random_proxy():
    """从代理池中随机选择一个代理"""
    return random.choice(PROXIES)

def find_total_pages(year):
    """同步方式找到指定年份的总页数"""
    page_num = 1
    while True:
        url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
        logger.info(f"Checking page {page_num} for year {year}: {url}")
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        # 检测 id 为 browserItemList 的标签是否为空
        browser_item_list = soup.find(id="browserItemList")
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            logger.info(f"Empty page found for year {year} at page {page_num}. Total pages: {page_num - 1}")
            return page_num - 1  # 返回总页数
        page_num += 1


async def fetch(session, url):
    """异步获取网页内容"""
    # 使用随机代理
    proxy = get_random_proxy()  
    async with session.get(url, proxy=proxy) as response:
        return await response.text()


async def fetch_main_page(session, year, page_num):
    """获取主页面并提取动画信息"""
    url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
    logger.info(f"Fetching page {page_num} for year {year}: {url}")

    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            return

        for item in browser_item_list.find_all('li', class_='item'):
            # 提取标题
            title_tag = item.find('h3').find('a') if item.find('h3') else None
            anime_name = title_tag.text.strip() if title_tag else "Unknown"
            sub_url = title_tag['href'] if title_tag else "#"

            # 提取排名
            rank_tag = item.find('span', class_='rank')
            rank_value = rank_tag.text.strip().replace('Rank ', '') if rank_tag else "N/A"

            # 提取评分
            rate_info = item.find('p', class_='rateInfo')
            score = "N/A"
            if rate_info:
                score_tag = rate_info.find('small', class_='fade')
                if score_tag and score_tag.text.strip():
                    score = score_tag.text.strip()

            # 添加到全局数据
            anime_data.append([year, anime_name, rank_value, score])

            # 添加任务以抓取标签
            if sub_url != "#":
                await fetch_anime_tags(session, year, sub_url)

    except Exception as e:
        logger.error(f"Error fetching page {page_num} for year {year}: {e}")


async def fetch_anime_tags(session, year, sub_url):
    """异步获取二级页面的标签信息"""
    sub_page_url = f"{MAIN_URL}{sub_url}"
    try:
        html = await fetch(session, sub_page_url)
        sub_soup = BeautifulSoup(html, 'lxml')

        tag_section = sub_soup.find('div', class_='subject_tag_section')
        if tag_section:
            for span in tag_section.find_all('span'):
                if span.get('id') == 'user_tags':  # 跳过用户标签
                    continue
                tag_text = span.text.strip()
                if tag_text:
                    tags_counter[tag_text] += 1
                    yearly_tags_counter[year][tag_text] += 1
    except Exception as e:
        logger.error(f"Error fetching tags from {sub_page_url}: {e}")


async def fetch_all_years_pages():
    """异步并发检测每年总页数"""
    tasks = []

    for year in range(START_YEAR, END_YEAR + 1):
        tasks.append(asyncio.to_thread(find_total_pages, year))  # 使用 asyncio.to_thread 进行并发调用同步函数

    total_pages_per_year = await asyncio.gather(*tasks)  # 等待所有任务完成
    return dict(zip(range(START_YEAR, END_YEAR + 1), total_pages_per_year))  # 返回每年的总页数


async def fetch_all_years_data(session):
    """异步并发获取每年所有页面"""
    total_pages_per_year = await fetch_all_years_pages()

    tasks = []
    for year, total_pages in total_pages_per_year.items():
        tasks.extend([fetch_main_page(session, year, page_num) for page_num in range(1, total_pages + 1)])

    # 并发执行所有页面的抓取任务
    await asyncio.gather(*tasks)


def save_anime_data(file_path):
    """保存动画信息到 CSV"""
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Anime_Name', 'Rank', 'Score'])
        writer.writerows(anime_data)


def save_yearly_tags_to_csv(file_path):
    """保存按年统计的标签数据到 CSV 文件"""
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Tag', 'Count'])
        for year, tags in yearly_tags_counter.items():
            for tag, count in tags.items():
                writer.writerow([year, tag, count])


async def main():
    """主函数"""
    start_time = time.time()

    # 创建一个全局的 ClientSession，添加代理配置
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # 异步爬取所有年份的数据
        await fetch_all_years_data(session)

    # 保存数据
    save_anime_data('data/anime_data.csv')
    save_yearly_tags_to_csv('data/yearly_tags_stats.csv')

    logger.info(f"Data saved. Execution time: {time.time() - start_time:.2f} seconds")


# 运行程序
asyncio.run(main())
