import asyncio
import logging
import aiohttp
from scraper.directory import get_anime_list, get_total_pages
from scraper.fetcher import get_anime_details  # 获取番剧详细信息
from scraper.comments import fetch_user_comments  # 获取番剧评论
from utils.sqldb import create_db, insert_anime_data, insert_category_data, insert_anime_category_relation, insert_production_data, insert_anime_production_relation, insert_comment_data
from config import USE_PROXY, START_YEAR, END_YEAR

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fetch_anime_details_and_insert(session, anime_name, sub_url, release_date):
    """异步获取番剧详细信息并插入数据库"""
    logger.info(f"Fetching details for {anime_name}")
    
    try:
        # 获取番剧的详细信息
        anime_details = await get_anime_details(session, sub_url)

        # 从详细信息中提取数据
        anime_id = sub_url.split('/')[-1]  # 假设ID是URL的最后一部分
        score = anime_details.get('score', 0.0)  # 获取评分
        score_count = anime_details.get('votes', 0)  # 获取评分人数
        release_date = release_date or anime_details.get('release_date', "Unknown")  # 获取放送日期，优先使用抓取到的日期
        tags = anime_details.get('tags', [])  # 获取分类标签
        production_companies = anime_details.get('production_companies', [])  # 获取制作公司
        # 将动漫基本信息插入到数据库
        insert_anime_data(anime_id, anime_name, score, score_count, release_date)
        # 插入分类标签并建立动漫与分类的关系
        for tag in tags:
            category_id = insert_category_data(tag)  # 插入分类并返回分类ID
            insert_anime_category_relation(anime_id, category_id)  # 插入动漫与分类的关系
        # 插入制作公司并建立动漫与制作公司关系
        for company in production_companies:
            production_id = insert_production_data(company)  # 插入制作公司并返回制作公司ID
            insert_anime_production_relation(anime_id, production_id)  # 插入动漫与制作公司关系
        # 获取评论数据并插入数据库
        comments = await fetch_user_comments(session, sub_url)
        for comment in comments:
            insert_comment_data(anime_id, comment['comment'], comment['time_ago'])
        print(comments)

    except Exception as e:
        logger.error(f"Error fetching details for {anime_name} (URL: {sub_url}): {e}")
        # 如果出错，记录该番剧并跳过
        with open('failed_animes.txt', 'a', encoding='utf-8') as f:
            f.write(f"{anime_name} (URL: {sub_url}) failed: {str(e)}\n")

async def fetch_all_data():
    """抓取所有番剧的数据并插入到数据库"""
    create_db()  # 创建数据库（如果不存在）

    async with aiohttp.ClientSession() as session:
        for year in range(START_YEAR, END_YEAR + 1):
            total_pages = await get_total_pages(session, year)
            anime_list = await get_anime_list(session, year, total_pages)

            tasks = []  # 用于存储所有异步任务

            for anime_name, sub_url, release_date in anime_list:  # 获取的列表包含 release_date
                # 创建并添加任务到任务列表
                tasks.append(fetch_anime_details_and_insert(session, anime_name, sub_url, release_date))

            # 等待所有任务并发执行
            await asyncio.gather(*tasks)

        logger.info("All data fetched and inserted into the database!")

if __name__ == "__main__":
    asyncio.run(fetch_all_data())
