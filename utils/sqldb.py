import sqlite3
import logging

# 数据库文件路径
DB_FILE = 'anime_data.db'

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_db():
    """创建数据库并创建表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 创建番剧信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anime (
        anime_id INTEGER PRIMARY KEY,
        anime_title TEXT NOT NULL,
        score REAL,
        score_count INTEGER,
        category TEXT,
        release_date TEXT
    );
    ''')

    conn.commit()
    conn.close()
    logger.info("Database and table created successfully!")

def insert_anime_data(anime_id, anime_title, score, score_count, category, release_date):
    """将番剧数据插入到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 插入数据
    cursor.execute('''
    INSERT OR REPLACE INTO anime (anime_id, anime_title, score, score_count, category, release_date) 
    VALUES (?, ?, ?, ?, ?, ?);
    ''', (anime_id, anime_title, score, score_count, category, release_date))

    conn.commit()
    conn.close()
    logger.info(f"Inserted data for anime: {anime_title} (ID: {anime_id})")

def get_anime_data():
    """获取数据库中所有番剧数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM anime')
    rows = cursor.fetchall()
    conn.close()

    return rows

def clear_anime_data():
    """清空番剧表的数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM anime')
    conn.commit()
    conn.close()

    logger.info("All anime data has been cleared.")

