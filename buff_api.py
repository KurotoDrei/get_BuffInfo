"""
Buff API请求模块
"""

import requests
import time
import random
from config import (
    BUFF_API_BASE,
    BUFF_API_DETAIL,
    GAME_CSGO,
    HEADERS,
    BUFF_COOKIE,
    REQUEST_DELAY,
    DEFAULT_PAGES,
)


def get_headers(cookie=None):
    """获取带Cookie的请求头"""
    headers = HEADERS.copy()
    if cookie:
        headers["Cookie"] = cookie
    elif BUFF_COOKIE:
        headers["Cookie"] = BUFF_COOKIE
    return headers


def ensure_login():
    """
    确保已登录
    
    Returns:
        str: cookie字符串
    """
    if BUFF_COOKIE:
        return BUFF_COOKIE
    
    print("请先运行 python get_cookie.py 来获取Cookie")
    return ""


def fetch_goods_list(page_num=1, game=GAME_CSGO, category_group=None, cookie=None, sort_by="name"):
    """
    获取饰品列表

    Args:
        page_num: 页码
        game: 游戏类型
        category_group: 分类(如 knife, pistol, rifle等)
        cookie: cookie字符串
        sort_by: 排序方式（默认"name"保持稳定排序，避免分页时物品位置变动）

    Returns:
        dict: API响应数据
    """
    params = {
        "game": game,
        "page_num": page_num,
        "page_size": 80,  # 使用更大的page_size减少请求次数
        "use_suggestion": 0,
        "trigger": "undefined_trigger",
        "sort_by": sort_by,  # 稳定排序，防止物品在分页之间移动
        "_": int(time.time() * 1000),
    }

    if category_group:
        params["category_group"] = category_group

    # 重试机制
    max_retries = 2
    for retry in range(max_retries):
        try:
            response = requests.get(
                BUFF_API_BASE, headers=get_headers(cookie), params=params, timeout=(10, 15)
            )
            
            # 如果遇到429错误，等待后重试
            if response.status_code == 429:
                wait_time = (retry + 1) * 10  # 10秒、20秒
                print(f"  遇到429错误，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if retry < max_retries - 1:
                wait_time = (retry + 1) * 5
                print(f"  请求失败，等待 {wait_time} 秒后重试: {e}")
                time.sleep(wait_time)
            else:
                print(f"  请求失败，已重试 {max_retries} 次: {e}")
                return None
    
    return None


def fetch_goods_detail(goods_id, game=GAME_CSGO, cookie=None):
    """
    获取饰品详情

    Args:
        goods_id: 饰品ID
        game: 游戏类型
        cookie: cookie字符串

    Returns:
        dict: API响应数据
    """
    params = {"game": game, "goods_id": goods_id}

    try:
        response = requests.get(
            BUFF_API_DETAIL, headers=get_headers(cookie), params=params, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"获取详情失败: {e}")
        return None


def fetch_hot_goods(pages=DEFAULT_PAGES, game=GAME_CSGO):
    """
    获取热门饰品数据

    Args:
        pages: 获取页数
        game: 游戏类型

    Returns:
        list: 饰品数据列表
    """
    all_items = []

    for page in range(1, pages + 1):
        print(f"正在获取第 {page}/{pages} 页数据...")

        # 增加随机延迟，避免被限制
        if page > 1:
            delay = REQUEST_DELAY + random.uniform(1, 3)
            time.sleep(delay)

        data = fetch_goods_list(page_num=page, game=game)

        if data and "data" in data and data.get("code") == "OK":
            items = data["data"].get("items", [])
            all_items.extend(items)
            print(f"  获取到 {len(items)} 个饰品")
        else:
            print(f"  第 {page} 页数据获取失败")
            break

    return all_items


# 已知的所有无涂装刀名称（用于完整性验证）
# 共 40 把：20 普通 + 20 StatTrak
KNOWN_VANILLA_KNIFE_NAMES = frozenset([
    "★ Bayonet",
    "★ Bowie Knife",
    "★ Butterfly Knife",
    "★ Classic Knife",
    "★ Falchion Knife",
    "★ Flip Knife",
    "★ Gut Knife",
    "★ Huntsman Knife",
    "★ Karambit",
    "★ Kukri Knife",
    "★ M9 Bayonet",
    "★ Navaja Knife",
    "★ Nomad Knife",
    "★ Paracord Knife",
    "★ Skeleton Knife",
    "★ Shadow Daggers",
    "★ Stiletto Knife",
    "★ Survival Knife",
    "★ Talon Knife",
    "★ Ursus Knife",
    "★ StatTrak™ Bayonet",
    "★ StatTrak™ Bowie Knife",
    "★ StatTrak™ Butterfly Knife",
    "★ StatTrak™ Classic Knife",
    "★ StatTrak™ Falchion Knife",
    "★ StatTrak™ Flip Knife",
    "★ StatTrak™ Gut Knife",
    "★ StatTrak™ Huntsman Knife",
    "★ StatTrak™ Karambit",
    "★ StatTrak™ Kukri Knife",
    "★ StatTrak™ M9 Bayonet",
    "★ StatTrak™ Navaja Knife",
    "★ StatTrak™ Nomad Knife",
    "★ StatTrak™ Paracord Knife",
    "★ StatTrak™ Skeleton Knife",
    "★ StatTrak™ Shadow Daggers",
    "★ StatTrak™ Stiletto Knife",
    "★ StatTrak™ Survival Knife",
    "★ StatTrak™ Talon Knife",
    "★ StatTrak™ Ursus Knife",
])


def fetch_knife_items(max_pages=None, game=GAME_CSGO):
    """
    获取所有刀饰品数据

    Args:
        max_pages: 最大页数（默认None，自动检测总页数）
        game: 游戏类型

    Returns:
        list: 刀饰品数据列表
    """
    # 确保已登录
    cookie = ensure_login()
    if not cookie:
        return []
    
    all_items = []
    seen_ids = set()  # 用于去重
    start_time = time.time()
    
    # 先获取第1页，确定总页数
    first_data = fetch_goods_list(page_num=1, game=game, category_group="knife", cookie=cookie)
    if not first_data or first_data.get("code") != "OK":
        print("获取第一页数据失败")
        return []
    
    total_page = first_data["data"].get("total_page", 0)
    total_count = first_data["data"].get("total_count", 0)
    total_pages = max_pages if max_pages else total_page
    print(f"总物品数: {total_count}, 总页数: {total_page}, 计划获取: {total_pages} 页")
    
    # 处理第1页数据
    if first_data and "data" in first_data:
        items = first_data["data"].get("items", [])
        new_items = []
        for item in items:
            item_id = item.get("id")
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                new_items.append(item)
        all_items.extend(new_items)
        print(f"  第 1 页: 获取到 {len(items)} 个（新增 {len(new_items)} 个），累计 {len(all_items)} 个")
        
        if len(items) == 0:
            print("  没有数据，停止获取")
            return all_items

    for page in range(2, total_pages + 1):
        elapsed = time.time() - start_time
        # 总超时控制：超过180秒就停止
        if elapsed > 180:
            print(f"  [{elapsed:.0f}s] 总耗时超过180秒，停止获取")
            break

        # 单页重试机制：最多重试3次
        page_ok = False
        for page_retry in range(3):
            try:
                print(f"[{elapsed:.0f}s] 正在获取第 {page}/{total_pages} 页（尝试 {page_retry + 1}/3）...")

                # 减少延迟，避免总耗时过长
                delay = 1 + random.uniform(0.5, 1.5)
                if page_retry > 0:
                    delay += page_retry * 3  # 重试时增加等待时间
                time.sleep(delay)

                data = fetch_goods_list(page_num=page, game=game, category_group="knife", cookie=cookie)

                if data and "data" in data and data.get("code") == "OK":
                    items = data["data"].get("items", [])
                    
                    # 去重：只添加未见过的刀饰品
                    new_items = []
                    for item in items:
                        item_id = item.get("id")
                        if item_id and item_id not in seen_ids:
                            seen_ids.add(item_id)
                            new_items.append(item)
                    
                    all_items.extend(new_items)
                    print(f"  第 {page} 页: 获取到 {len(items)} 个（新增 {len(new_items)} 个），累计 {len(all_items)} 个")
                    
                    # 如果没有更多数据，停止翻页
                    if len(items) == 0:
                        print("  没有更多数据，停止获取")
                        page_ok = True
                        break

                    page_ok = True
                    break
                else:
                    code = data.get('code') if data else '请求失败'
                    print(f"  第 {page} 页获取失败: {code}（尝试 {page_retry + 1}/3）")
            except Exception as e:
                print(f"  第 {page} 页异常: {e}（尝试 {page_retry + 1}/3）")

        if not page_ok:
            print(f"  第 {page} 页在 3 次尝试后仍失败，跳过此页继续下一页")

    elapsed = time.time() - start_time
    print(f"\n总共获取 {len(all_items)} 个刀饰品，耗时 {elapsed:.0f} 秒")
    return all_items


def filter_vanilla_knives(items):
    """
    筛选无涂装刀饰品（包括计数器版本）

    Args:
        items: 刀饰品列表

    Returns:
        tuple: (不带计数器的无涂装刀, 带计数器的无涂装刀)
    """
    vanilla_knives = []
    stattrak_vanilla_knives = []
    seen_names = set()  # 用于去重

    for item in items:
        name = item.get("market_hash_name", "")
        
        # 检查是否是无涂装刀（Vanilla）
        # 无涂装刀的特征：名称中不包含 '|' （没有皮肤名称）
        # 例如：★ Karambit, ★ Butterfly Knife
        # 计数器版本：★ StatTrak™ Karambit
        if '|' not in name:
            # 去重：如果已经见过这个名称，跳过
            if name in seen_names:
                continue
            seen_names.add(name)
            
            # 检查是否带计数器
            if 'StatTrak' in name or 'StatTrak™' in name:
                stattrak_vanilla_knives.append(item)
            else:
                vanilla_knives.append(item)

    return vanilla_knives, stattrak_vanilla_knives


def search_knife_by_name(name, game=GAME_CSGO):
    """
    按名称在 Buff 搜索指定饰品（目标搜索）。

    使用 Buff API 的 search 参数，分页遍历结果，找到完全匹配的饰品。
    相比全量翻页抓取（38页~2分钟），此方法只需遍历搜索结果的几页。

    Args:
        name: 饰品 market_hash_name（如 "★ Karambit"）
        game: 游戏类型

    Returns:
        dict or None: 匹配的饰品数据，未找到时返回 None
    """
    cookie = ensure_login()
    if not cookie:
        return None

    try:
        for page in range(1, 6):  # 最多翻5页
            params = {
                "game": game,
                "page_num": page,
                "page_size": 80,
                "search": name,
                "category_group": "knife",
                "use_suggestion": 0,
                "sort_by": "name",
                "_": int(time.time() * 1000),
            }
            response = requests.get(
                BUFF_API_BASE, headers=get_headers(cookie), params=params, timeout=(10, 15)
            )
            if response.status_code != 200:
                break

            data = response.json()
            if data.get("code") != "OK":
                break

            items = data["data"].get("items", [])
            for item in items:
                if item.get("market_hash_name") == name:
                    return item

            if len(items) < 80:  # 已翻完所有页
                break

    except requests.RequestException as e:
        print(f"  搜索 '{name}' 失败: {e}")

    return None


def verify_vanilla_completeness(items):
    """
    验证无涂装刀是否获取完整，返回缺失的刀名列表。

    Args:
        items: filter_vanilla_knives 返回的 (normal, stattrak) 元组

    Returns:
        list: 缺失的刀名列表（空列表 = 完整）
    """
    normal, stattrak = items
    found = {item["market_hash_name"] for item in normal + stattrak}
    missing = sorted(KNOWN_VANILLA_KNIFE_NAMES - found)

    if missing:
        print(f"  数据不完整: 已有 {len(found)}/40 把，缺失 {len(missing)} 把:")
        for name in missing:
            print(f"    - {name}")
    else:
        print(f"  数据完整: 40/40 把无涂装刀均已获取")

    return missing


def retry_missing_knives(missing_names, game=GAME_CSGO):
    """
    针对缺失的刀名，逐一把目标搜索补全。

    使用 Buff API 的 search 参数按名称搜索，每次请求约 2 秒。
    相比全量翻页（38 页~2 分钟），缺失数量不多时快得多。

    Args:
        missing_names: 缺失的刀名列表
        game: 游戏类型

    Returns:
        list: 补全后的原始刀饰品数据列表（包含初始已找到的 + 新搜到的）
    """
    if not missing_names:
        return list(KNOWN_VANILLA_KNIFE_NAMES)

    import time

    found_items = []
    still_missing = []

    print(f"\n  按名称逐一搜索 {len(missing_names)} 把缺失的刀...")
    for i, name in enumerate(missing_names, 1):
        print(f"    [{i}/{len(missing_names)}] 搜索: {name}")
        time.sleep(0.5)  # 短延迟，避免触发限制
        item = search_knife_by_name(name, game=game)
        if item:
            found_items.append(item)
            print(f"      [OK] 找到（价格: {item.get('sell_min_price', 'N/A')}）")
        else:
            still_missing.append(name)
            print(f"      [FAIL] 未找到")

    if found_items:
        print(f"  搜索补全成功: {len(found_items)} 把")
    if still_missing:
        print(f"  搜索后仍缺失 {len(still_missing)} 把: {', '.join(still_missing)}")
        # 最后尝试一次全量重抓（兜底）
        print(f"\n  尝试全量重抓兜底...")
        retry_raw = fetch_knife_items(game=game)
        retry_names = {
            item["market_hash_name"]
            for item in retry_raw
            if '|' not in item.get("market_hash_name", "")
        }
        for name in list(still_missing):
            if name in retry_names:
                for item in retry_raw:
                    if item.get("market_hash_name") == name:
                        found_items.append(item)
                        still_missing.remove(name)
                        print(f"      [OK] 全量重抓找到: {name}")
                        break

    return found_items, still_missing


def get_knife_name_in_chinese(english_name):
    """
    获取刀饰品的名称（直接使用英文名称）
    
    Args:
        english_name: 英文名称
        
    Returns:
        str: 名称（直接返回英文名称）
    """
    return english_name
