import aiohttp
import asyncio
import logging
import time
from bs4 import BeautifulSoup
import requests
import csv
from collections import Counter

# 常量定义
MAIN_URL = "https://bangumi.tv"  # 主网址
START_YEAR = 2010  # 开始年份
END_YEAR = 2024  # 结束年份
HEADERS = {  # 请求头
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/78.0.3904.108 Safari/537.36'
}

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量
tags_counter = Counter()  # 用于统计 tag 出现次数
anime_data = []  # 用于存储动画信息


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
    async with session.get(url) as response:
        return await response.text()


async def fetch_anime_page(session, year, anime_name, sub_url, rank):
    """获取二级页面内容并提取 tags"""
    sub_page_url = f"{MAIN_URL}{sub_url}"
    logger.info(f"Fetching details for {anime_name}, URL: {sub_page_url}")
    tags = []

    try:
        html = await fetch(session, sub_page_url)
        sub_soup = BeautifulSoup(html, 'lxml')

        # 查找 tag 信息
        tag_section = sub_soup.find('div', class_='subject_tag_section')
        if tag_section:
            for span in tag_section.find_all('span'):
                if span.get('id') == 'user_tags':  # 跳过带有 user_tags 的 span
                    continue
                tag_text = span.text.strip()
                if tag_text:
                    tags_counter[tag_text] += 1  # 更新 tag 计数
                    tags.append(tag_text)
    except Exception as e:
        logger.error(f"Error fetching details for {anime_name}: {e}")
    return tags


async def fetch_main_page(session, year, page_num):
    """获取主页面并提取动画信息"""
    url = f"{MAIN_URL}/anime/browser/airtime/{year}?sort=rank&page={page_num}"
    logger.info(f"Fetching page {page_num} for year {year}: {url}")

    try:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'lxml')
        browser_item_list = soup.find(id="browserItemList")

        # 检测是否有内容
        if not browser_item_list or not browser_item_list.get_text(strip=True):
            logger.warning(f"No content on page {page_num} for year {year}.")
            return []

        tasks = []
        for item in browser_item_list.find_all('li', class_='item'):
            # 提取标题、链接和 Rank
            title_tag = item.find('h3').find('a') if item.find('h3') else None
            anime_name = title_tag.text.strip() if title_tag else "Unknown"
            sub_url = title_tag['href'] if title_tag else "#"
            rank_tag = item.find('span', class_='rank')
            rank_value = rank_tag.text.strip().replace('Rank ', '') if rank_tag else "N/A"

            if sub_url != "#":
                tasks.append(fetch_anime_page(session, year, anime_name, sub_url, rank_value))

            anime_data.append([year, anime_name, rank_value])

        # 执行所有二级页面的任务
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error fetching page {page_num} for year {year}: {e}")


async def fetch_all_years_pages():
    """异步并发检测2010-2024每年总页数"""
    tasks = []

    for year in range(START_YEAR, END_YEAR + 1):
        tasks.append(asyncio.to_thread(find_total_pages, year))  # 使用 asyncio.to_thread 进行并发调用同步函数

    total_pages_per_year = await asyncio.gather(*tasks)  # 等待所有任务完成
    return dict(zip(range(START_YEAR, END_YEAR + 1), total_pages_per_year))  # 返回每年的总页数


async def main():
    """主函数，处理所有页面和数据保存"""
    start_time = time.time()  # 记录开始时间

    # 获取2010到2024年的所有页数
    total_pages_per_year = await fetch_all_years_pages()
    for year, total_pages in total_pages_per_year.items():
        logger.info(f"Total pages to process for year {year}: {total_pages}")

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = [fetch_main_page(session, year, page_num) for page_num in range(1, total_pages + 1)]
            await asyncio.gather(*tasks)

    # 保存动画信息到 CSV
    with open('data/anime_data.csv', 'w', encoding='utf-8', newline='') as anime_file:
        anime_writer = csv.writer(anime_file)
        anime_writer.writerow(['Year', 'Anime_Name', 'Rank'])  # 添加新的列 Rank
        anime_writer.writerows(anime_data)

    # 保存 tag 统计数据到文件
    with open('data/tags_stats.csv', 'w', encoding='utf-8', newline='') as tags_file:
        tags_writer = csv.writer(tags_file)
        tags_writer.writerow(['Tag', 'Count'])  # 写入表头
        for tag, count in tags_counter.most_common():
            tags_writer.writerow([tag, count])

    end_time = time.time()  # 记录结束时间
    logger.info(f"Data has been saved to 'anime_data.csv' and 'tags_stats.csv'.")
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds.")


# 启动异步任务
asyncio.run(main())
