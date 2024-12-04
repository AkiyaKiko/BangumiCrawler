import asyncio
import aiohttp
from aiohttp import ClientTimeout, ClientError
from bs4 import BeautifulSoup
import re
from config import MAIN_URL, HEADERS
from utils.proxy_manager import get_random_proxy
import logging

# 设置日志
logger = logging.getLogger(__name__)

async def fetch(session, url):
    """异步获取网页内容，带超时设置和重试机制"""
    timeout = ClientTimeout(total=60)  # 设置60秒超时时间
    retries = 3  # 最大重试次数
    attempt = 0
    proxy = get_random_proxy()  # 使用代理池中的代理

    while attempt < retries:
        try:
            async with session.get(url, headers=HEADERS, proxy=proxy, timeout=timeout) as response:
                return await response.text()
        except asyncio.TimeoutError:
            logger.error(f"TimeoutError: Failed to fetch {url} on attempt {attempt + 1}")
            attempt += 1
            await asyncio.sleep(2)  # 等待2秒再试
        except ClientError as e:
            logger.error(f"ClientError: {e} while fetching {url}")
            break  # 遇到客户端错误时退出
        except Exception as e:
            logger.error(f"Unknown error: {e} while fetching {url}")
            break  # 捕获其他未知异常

    return None  # 如果超过最大重试次数仍然失败，返回 None


async def get_anime_details(session, sub_url):
    """获取单个番剧的评分、评分人数、标签和制作公司"""
    url = f"{MAIN_URL}{sub_url}"
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'lxml')

    # 获取评分
    score_tag = soup.find('span', class_='number', property='v:average')
    score = score_tag.text.strip() if score_tag else 'N/A'
    
    # 获取评分人数
    votes_tag = soup.find('span', property='v:votes')
    votes = votes_tag.text.strip() if votes_tag else '0'
    
    # 获取所有标签
    tags = []
    tag_div = soup.find('div', class_='subject_tag_section')  # 通过正确的class获取标签部分
    if tag_div:
        tag_links = tag_div.find_all('a', class_='l')  # 查找所有带有class='l'的a标签
        for tag in tag_links:
            tag_name = tag.find('span').text.strip() if tag.find('span') else 'Unknown'
            tags.append(tag_name)
    
    # 获取制作公司
    production_companies = []
    infobox = soup.find('ul', id='infobox')
    if infobox:
        for li in infobox.find_all('li'):
            if '动画制作' in li.text:
                production_tags = li.find_all('a', class_='l')
                for tag in production_tags:
                    production_name = tag.text.strip()
                    production_companies.append(production_name)

    return {
        'score': score,
        'votes': votes,
        'tags': tags,  # 返回标签列表
        'production_companies': production_companies  # 返回制作公司列表
    }
