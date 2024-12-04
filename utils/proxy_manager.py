# utils/proxy_manager.py

import random
from config import PROXIES, USE_PROXY

def get_random_proxy():
    """从代理池中随机选择一个代理"""
    if USE_PROXY and PROXIES:  # 如果需要使用代理并且代理池非空
        return random.choice(PROXIES)
    return None  # 不使用代理
