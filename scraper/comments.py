import asyncio
import aiohttp
from aiohttp import ClientTimeout, ClientError
from bs4 import BeautifulSoup
import logging
from config import HEADERS
from utils.proxy_manager import get_random_proxy

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

async def fetch_user_comments(session, sub_url, page_limit=10):
    """爬取某个番剧的所有用户评论"""
    base_url = f'https://bangumi.tv{sub_url}/comments'
    comments_data = []

    for page in range(1, page_limit + 1):
        url = f"{base_url}?page={page}"
        logger.info(f"Fetching comments from: {url}")
        html = await fetch(session, url)
        if not html:
            logger.warning(f"No data fetched from page {page}, stopping further pagination.")
            break

        soup = BeautifulSoup(html, 'html.parser')

        # 查找所有包含评论的item
        items = soup.find_all('div', class_='item clearit')
        if not items:  # 如果没有找到更多评论项，说明到最后一页了
            logger.info(f"No more comments found on page {page}. Stopping.")
            break

        for item in items:
            try:
                # 提取评论内容
                comment = item.find('p', class_='comment').get_text(strip=True)

                # 提取看过时间
                time_ago = item.find('small', class_='grey').get_text(strip=True)

                # 将数据添加到列表中
                comments_data.append({
                    'comment': comment,
                    'time_ago': time_ago
                })
            except AttributeError as e:
                logger.error(f"Error extracting data for an item on page {page}: {e}")
                continue  # 跳过出错的项

    return comments_data
