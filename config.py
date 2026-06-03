"""
Buff平台配置文件

Cookie获取方法:
1. 运行 get_cookie.py 脚本
2. 在弹出的浏览器中手动登录Buff
3. 登录成功后，脚本会自动获取Cookie并保存到此文件

环境变量加载顺序:
1. 优先读取项目根目录的 .env 文件（本地运行用）
2. 若 .env 不存在，回退到系统环境变量 BUFF_COOKIE（GitHub Actions用）
"""

import os
from pathlib import Path

# 尝试加载 .env 文件（本地运行用）
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"已加载 .env 配置文件")
    except ImportError:
        pass  # python-dotenv 未安装，回退到系统环境变量

# Buff平台Cookie
# 本地运行: .env 文件中的 BUFF_COOKIE（通过 local_setup.py 配置）
# GitHub Actions运行: 通过仓库 Secrets 中的 BUFF_COOKIE 环境变量传入
BUFF_COOKIE = os.environ.get("BUFF_COOKIE", "")

# API配置
BUFF_API_BASE = "https://buff.163.com/api/market/goods"
BUFF_API_DETAIL = "https://buff.163.com/api/market/goods/info"

# 游戏类型
GAME_CSGO = "csgo"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://buff.163.com/market/csgo",
}

# 请求间隔(秒)，避免被限制
REQUEST_DELAY = 2

# 默认获取页数
DEFAULT_PAGES = 3

# 输出目录
OUTPUT_DIR = "output"
