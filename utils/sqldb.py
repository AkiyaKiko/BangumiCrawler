import sqlite3
import logging
from sqlite3 import Error

# 数据库文件路径
DB_PATH = 'anime_data.db'

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建数据库连接
def create_connection():
    """创建与数据库的连接"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Connected to SQLite, DB path: {DB_PATH}")
    except Error as e:
        print(e)
    return conn

# 创建数据库表
def create_db():
    """创建数据库表"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # 创建 Anime 表
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS Anime (
                    anime_id INTEGER PRIMARY KEY,
                    anime_title TEXT NOT NULL,
                    score REAL,
                    score_count INTEGER,
                    release_date TEXT
                );
            ''')

            # 创建 Category 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Category (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT UNIQUE NOT NULL
                );
            ''')

            # 创建 Anime_Category 关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Anime_Category (
                    anime_id INTEGER,
                    category_id INTEGER,
                    FOREIGN KEY (anime_id) REFERENCES Anime(anime_id),
                    FOREIGN KEY (category_id) REFERENCES Category(category_id),
                    PRIMARY KEY (anime_id, category_id)
                );
            ''')

            # 创建 Production 表 (制作公司)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Production (
                    production_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    production_name TEXT UNIQUE NOT NULL
                );
            ''')

            # 创建 Anime_Production 关系表 (动漫与制作公司关系)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Anime_Production (
                    anime_id INTEGER,
                    production_id INTEGER,
                    FOREIGN KEY (anime_id) REFERENCES Anime(anime_id),
                    FOREIGN KEY (production_id) REFERENCES Production(production_id),
                    PRIMARY KEY (anime_id, production_id)
                );
            ''')

            # 创建 Comments 表 (评论数据)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anime_id INTEGER,
                    comment TEXT NOT NULL,
                    time_ago TEXT NOT NULL,
                    FOREIGN KEY (anime_id) REFERENCES Anime(anime_id)
                );
            ''')

            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info("Database and tables created successfully!")

# 插入番剧数据
def insert_anime_data(anime_id, anime_title, score, score_count, release_date):
    """插入番剧数据"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO Anime (anime_id, anime_title, score, score_count, release_date)
                VALUES (?, ?, ?, ?, ?);
            ''', (anime_id, anime_title, score, score_count, release_date))
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted data for anime: {anime_title} (ID: {anime_id})")

# 插入分类数据，返回分类 ID
def insert_category_data(category_name):
    """插入分类数据，返回分类 ID"""
    conn = create_connection()
    category_id = None
    if conn:
        try:
            cursor = conn.cursor()
            # 查询分类是否已经存在
            cursor.execute('SELECT category_id FROM Category WHERE category_name = ?', (category_name,))
            result = cursor.fetchone()
            if result:
                category_id = result[0]
            else:
                cursor.execute('INSERT INTO Category (category_name) VALUES (?)', (category_name,))
                conn.commit()
                category_id = cursor.lastrowid
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted category {category_name} (ID: {category_id}) successfully!")
    return category_id

# 插入动漫与分类关系
def insert_anime_category_relation(anime_id, category_id):
    """插入动漫与分类的关系"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO Anime_Category (anime_id, category_id)
                VALUES (?, ?);
            ''', (anime_id, category_id))
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted relation for anime ID: {anime_id} and category ID: {category_id}")

# 插入制作公司数据，返回制作公司 ID
def insert_production_data(production_name):
    """插入制作公司数据，返回制作公司 ID"""
    conn = create_connection()
    production_id = None
    if conn:
        try:
            cursor = conn.cursor()
            # 查询制作公司是否已经存在
            cursor.execute('SELECT production_id FROM Production WHERE production_name = ?', (production_name,))
            result = cursor.fetchone()
            if result:
                production_id = result[0]
            else:
                cursor.execute('INSERT INTO Production (production_name) VALUES (?)', (production_name,))
                conn.commit()
                production_id = cursor.lastrowid
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted production {production_name} (ID: {production_id}) successfully!")
    return production_id

# 插入动漫与制作公司关系
def insert_anime_production_relation(anime_id, production_id):
    """插入动漫与制作公司之间的关系"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO Anime_Production (anime_id, production_id)
                VALUES (?, ?);
            ''', (anime_id, production_id))
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted relation for anime ID: {anime_id} and production ID: {production_id}")

# 插入评论数据
def insert_comment_data(anime_id, comment, time_ago):
    """插入评论数据"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Comments (anime_id, comment, time_ago)
                VALUES (?, ?, ?);
            ''', (anime_id, comment, time_ago))
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()
            logger.info(f"Inserted comment for anime ID: {anime_id} by comment {comment}")
