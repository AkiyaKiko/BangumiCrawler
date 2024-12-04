import asyncio
import logging
import aiohttp
from scraper.directory import get_anime_list, get_total_pages
from utils.sqldb import create_db, insert_anime_data
from config import USE_PROXY, START_YEAR, END_YEAR

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fetch_all_data():
    """抓取所有番剧的数据并插入到数据库"""
    create_db()  # 创建数据库（如果不存在）

    async with aiohttp.ClientSession() as session:
        for year in range(START_YEAR, END_YEAR + 1):
            total_pages = await get_total_pages(session, year)
            anime_list = await get_anime_list(session, year, total_pages)

            for anime_name, sub_url in anime_list:
                logger.info(f"Fetching data for {anime_name}")

                # 假设获取到番剧的详细信息（可以替换为实际的获取过程）
                anime_id = sub_url.split('/')[-1]  # 假设ID是URL的最后一部分
                category = "Example Category"  # 这里替换为实际分类
                score = 8.5  # 这里替换为实际评分
                score_count = 1000  # 这里替换为实际评分人数
                release_date = "2024-01-01"  # 这里替换为实际放送日期

                # 将数据插入到数据库
                insert_anime_data(anime_id, anime_name, score, score_count, category, release_date)

        logger.info("All data fetched and inserted into the database!")

if __name__ == "__main__":
    asyncio.run(fetch_all_data())
