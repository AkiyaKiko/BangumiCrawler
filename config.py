# config.py

# 代理设置
USE_PROXY = False  # 是否使用代理
PROXIES = [
    "http://127.0.0.1:10809",  # 示例代理，实际使用时可以从配置文件或数据库加载
    # Add more proxies if needed
]

# 爬虫基本配置
MAIN_URL = "https://bangumi.tv"
START_YEAR = 2000
END_YEAR = 2024
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Cookie': 'chii_searchDateLine=1733345293; chii_cookietime=0; chii_auth=E5ErLFF6qYbAW8fsslGzXoClJXsbosMEBeRROExCfAc10j%2Bac0whK6qpzsNs3eBDgVZhNJq8ignmIj25r5x5Ci%2Fz6IP8tdl6jX2u'
}
