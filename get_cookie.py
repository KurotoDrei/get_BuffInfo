"""
Cookie获取脚本

使用方法：
1. 运行此脚本
2. 在弹出的浏览器中手动登录Buff
3. 登录成功后，按Enter键继续
4. 脚本会自动获取Cookie并保存到config.py
"""

import time
import re
from playwright.sync_api import sync_playwright


def get_cookie():
    """
    获取Buff Cookie
    
    Returns:
        str: cookie字符串，获取失败返回空字符串
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 访问Buff首页
        print("=" * 60)
        print("Buff Cookie获取工具")
        print("=" * 60)
        print()
        print("请在弹出的浏览器窗口中手动登录Buff...")
        print()
        
        page.goto('https://buff.163.com')
        
        # 等待用户手动登录
        print("请在浏览器中完成登录，然后回到此窗口...")
        print()
        input("登录完成后，请按Enter键继续...")
        
        # 获取cookies
        cookies = context.cookies()
        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        browser.close()
        return cookie_string


def save_cookie_to_config(cookie):
    """
    保存Cookie到config.py
    
    Args:
        cookie: cookie字符串
    """
    # 读取config.py
    with open('config.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换BUFF_COOKIE
    new_content = re.sub(
        r'BUFF_COOKIE = ".*?"',
        f'BUFF_COOKIE = "{cookie}"',
        content
    )
    
    # 保存config.py
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Cookie已保存到 config.py")


if __name__ == "__main__":
    cookie = get_cookie()
    if cookie:
        print(f"获取到Cookie: {cookie[:50]}...")
        save_cookie_to_config(cookie)
        print("\n现在可以运行 python main.py 来获取刀饰品数据了")
    else:
        print("获取Cookie失败")
