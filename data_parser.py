"""
数据解析模块 - 解析和处理Buff饰品数据
"""

import gc
import time
import pandas as pd
import os
from datetime import datetime
from buff_api import get_knife_name_in_chinese


def parse_knife_items(items):
    """
    解析刀饰品数据

    Args:
        items: API返回的原始刀饰品列表

    Returns:
        list: 解析后的刀饰品数据
    """
    parsed_items = []

    for item in items:
        try:
            market_hash_name = item.get("market_hash_name", "")
            chinese_name = get_knife_name_in_chinese(market_hash_name)

            price_info = {
                "id": item.get("id"),
                "name": market_hash_name,
                "chinese_name": chinese_name,
                "price": float(item.get("sell_min_price", 0)),
                "sell_num": item.get("sell_num", 0),
                "buy_num": item.get("buy_num", 0),
            }
            parsed_items.append(price_info)
        except (ValueError, TypeError) as e:
            print(f"解析刀饰品数据出错: {e}")
            continue

    return parsed_items


def sort_knife_items(items):
    """
    按基础名称排序，确保同一刀种的StatTrak和非StatTrak版本相邻。

    排序规则：
    1. 去掉"StatTrak™"后得到基础名称
    2. 按基础名称字母排序
    3. 同一基础名称内，非StatTrak在前，StatTrak在后

    Args:
        items: 解析后的刀饰品数据列表

    Returns:
        list: 排序后的刀饰品数据列表
    """
    def sort_key(item):
        name = item.get("name", item.get("chinese_name", ""))
        base = name.replace("StatTrak™", "").replace("StatTrak", "").replace("★", "").strip()
        has_stattrak = 1 if "StatTrak" in name else 0
        return (base, has_stattrak)

    return sorted(items, key=sort_key)


def _base_name(name):
    """获取基础名称（去除 StatTrak 和 ★ 前缀）"""
    return str(name).replace("StatTrak™", "").replace("StatTrak", "").replace("★", "").strip()


def _has_stattrak(name):
    """检查名称是否包含 StatTrak"""
    return "StatTrak" in str(name)


def save_hourly_price_data(items, filename="output/knife_prices.xlsx"):
    """
    保存每小时价格数据到Excel文件（宽格式）。

    Excel格式：
    - 每天一个sheet，sheet名=日期
    - 列：knife_name, price_0, price_1, ..., price_23
    - 每行代表一个饰品，每列代表该小时的sell_min_price
    - 同一天多次运行只会更新当前小时的价格列，不会覆盖其他小时

    Args:
        items: 解析后的刀饰品数据列表
        filename: Excel文件名
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().hour
    col_name = f"price_{hour}"

    # 读取已有Excel数据
    all_sheets = {}
    if os.path.exists(filename):
        try:
            xls = pd.ExcelFile(filename)
            for sheet in xls.sheet_names:
                all_sheets[sheet] = pd.read_excel(filename, sheet_name=sheet, dtype={"knife_name": str})
            del xls
            gc.collect()
            time.sleep(0.2)  # 等待文件锁释放
        except Exception as e:
            print(f"读取已有Excel文件失败: {e}")

    # 准备所有price列名
    all_price_cols = [f"price_{h}" for h in range(24)]
    valid_cols = ["knife_name"] + all_price_cols

    # 清理所有现有 sheet 中的旧格式遗留列（如旧的 "price" 列）
    # 这些列与新宽表格式冲突，会导致 melt(value_name="price") 报错
    for sheet_name in list(all_sheets.keys()):
        extra_cols = [c for c in all_sheets[sheet_name].columns if c not in valid_cols]
        if extra_cols:
            all_sheets[sheet_name] = all_sheets[sheet_name].drop(columns=extra_cols)
            print(f"清理 {sheet_name} 旧格式遗留列: {extra_cols}")

    # 获取或创建今天的sheet
    if today in all_sheets:
        today_df = all_sheets[today]
        for c in all_price_cols:
            if c not in today_df.columns:
                today_df[c] = None
    else:
        today_df = pd.DataFrame(columns=["knife_name"] + all_price_cols)
        today_df["knife_name"] = today_df["knife_name"].astype(str)

    # 按基础名称排序
    sorted_items = sort_knife_items(items)

    # 更新当前小时的价格
    for item in sorted_items:
        name = str(item["name"])
        price = item["price"]

        if name in today_df["knife_name"].values:
            idx = today_df[today_df["knife_name"] == name].index[0]
            today_df.at[idx, col_name] = price
        else:
            new_row = {c: None for c in today_df.columns}
            new_row["knife_name"] = name
            new_row[col_name] = price
            today_df = pd.concat([today_df, pd.DataFrame([new_row])], ignore_index=True)

    # 按基础名称排序（StatTrak与对应普通版相邻）
    today_df["_base"] = today_df["knife_name"].apply(_base_name)
    today_df["_st"] = today_df["knife_name"].apply(_has_stattrak).astype(int)
    today_df = today_df.sort_values(["_base", "_st"]).drop(columns=["_base", "_st"]).reset_index(drop=True)

    # 写入所有sheet（释放文件锁后写）
    gc.collect()
    time.sleep(0.1)
    all_sheets[today] = today_df
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, sheet_df in all_sheets.items():
            sheet_df.to_excel(writer, sheet_name=str(sheet_name), index=False)

    gc.collect()
    print(f"价格数据已保存到 {filename} (sheet: {today}, hour: {hour})")


def load_price_history(filename="output/knife_prices.xlsx"):
    """
    加载所有历史价格数据（兼容新旧格式）。

    新格式（宽表）会被melt为长表，每行包含：
    date (精确到小时), knife_name, price

    Args:
        filename: Excel文件名

    Returns:
        pd.DataFrame: 包含date, knife_name, price列的历史数据
    """
    if not os.path.exists(filename):
        return pd.DataFrame(columns=["date", "knife_name", "price"])

    try:
        xls = pd.ExcelFile(filename)
        dfs = []

        for sheet in xls.sheet_names:
            df = pd.read_excel(filename, sheet_name=sheet)

            # 判断是否为宽格式（包含 price_0 ... 等列）
            price_cols = [c for c in df.columns if str(c).startswith("price_")]

            if price_cols:
                # 清除可能冲突的旧 price 列（与 value_name="price" 冲突）
                if "price" in df.columns:
                    df = df.drop(columns=["price"])
                # 宽格式 → melt成(基表): knife_name, hour, price
                id_vars = [c for c in df.columns if not str(c).startswith("price_")]
                melted = pd.melt(df, id_vars=id_vars, value_vars=price_cols,
                                 var_name="hour_str", value_name="price")
                melted["hour"] = melted["hour_str"].str.replace("price_", "", regex=False).astype(int)
                melted = melted.dropna(subset=["price"]).copy()
                # 构造带小时的日期时间
                base_date = pd.to_datetime(sheet)
                melted["date"] = base_date + pd.to_timedelta(melted["hour"], unit="h")
                melted = melted[["date", "knife_name", "price"]]
            else:
                # 旧格式（直接有 date/price 列 或 只有 knife_name/price）
                if "date" not in df.columns:
                    df["date"] = pd.to_datetime(sheet)
                else:
                    df["date"] = pd.to_datetime(df["date"])

                # 提取所需列
                if "knife_name" in df.columns and "price" in df.columns:
                    melted = df[["date", "knife_name", "price"]]
                else:
                    continue

            dfs.append(melted)

        if not dfs:
            return pd.DataFrame(columns=["date", "knife_name", "price"])

        result = pd.concat(dfs, ignore_index=True)
        result["price"] = pd.to_numeric(result["price"], errors="coerce")
        return result

    except Exception as e:
        print(f"加载价格数据出错: {e}")
        return pd.DataFrame(columns=["date", "knife_name", "price"])


def load_today_hourly_data(filename="output/knife_prices.xlsx"):
    """
    加载今天的每小时价格数据（用于图表展示）。

    将宽表 melt 为长表，返回：
    hour (0-23), knife_name, price

    Args:
        filename: Excel文件名

    Returns:
        pd.DataFrame: 包含 hour, knife_name, price 列
    """
    if not os.path.exists(filename):
        return pd.DataFrame(columns=["hour", "knife_name", "price"])

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        xls = pd.ExcelFile(filename)
        if today not in xls.sheet_names:
            return pd.DataFrame(columns=["hour", "knife_name", "price"])

        df = pd.read_excel(filename, sheet_name=today)

        # 找出所有 price_N 列
        price_cols = sorted(
            [c for c in df.columns if str(c).startswith("price_")],
            key=lambda x: int(x.replace("price_", "")),
        )

        if not price_cols:
            return pd.DataFrame(columns=["hour", "knife_name", "price"])

        # Melt宽表为长表
        melted = pd.melt(df, id_vars=["knife_name"], value_vars=price_cols,
                         var_name="hour_str", value_name="price")
        melted["hour"] = melted["hour_str"].str.replace("price_", "", regex=False).astype(int)
        melted = melted.dropna(subset=["price"]).drop(columns=["hour_str"])
        melted = melted.sort_values(["knife_name", "hour"]).reset_index(drop=True)

        return melted

    except Exception as e:
        print(f"加载今天小时数据出错: {e}")
        return pd.DataFrame(columns=["hour", "knife_name", "price"])


def migrate_csv_to_xlsx(csv_filename="output/knife_prices.csv", xlsx_filename="output/knife_prices.xlsx"):
    """
    将旧的CSV格式数据迁移到新的Excel多sheet格式（宽表）。

    迁移时会将旧数据放入对应日期的sheet，放到 price_0 列中（因为旧数据没有小时信息）。

    Args:
        csv_filename: 原有CSV文件名
        xlsx_filename: 目标Excel文件名
    """
    if not os.path.exists(csv_filename):
        return

    print(f"检测到旧的CSV文件，正在迁移到新的Excel格式...")
    df = pd.read_csv(csv_filename, encoding='utf-8-sig')

    if "date" not in df.columns or "knife_name" not in df.columns or "price" not in df.columns:
        print("CSV格式不正确，跳过迁移")
        return

    dates = sorted(df['date'].unique())

    # 读取已有Excel数据
    all_sheets = {}
    if os.path.exists(xlsx_filename):
        try:
            xls = pd.ExcelFile(xlsx_filename)
            for sheet in xls.sheet_names:
                all_sheets[sheet] = pd.read_excel(xlsx_filename, sheet_name=sheet, dtype={"knife_name": str})
            del xls
            gc.collect()
            time.sleep(0.2)
        except Exception as e:
            print(f"读取已有Excel文件失败: {e}")

    all_price_cols = [f"price_{h}" for h in range(24)]

    # 添加CSV中的数据（不覆盖Excel已有的sheet）
    migrated_count = 0
    for date in dates:
        if date not in all_sheets:
            day_data = df[df['date'] == date][['knife_name', 'price']]
            # 放入宽表
            wide_df = pd.DataFrame(columns=["knife_name"] + all_price_cols)
            wide_df["knife_name"] = day_data["knife_name"].values
            wide_df["price_0"] = day_data["price"].values  # 旧数据默认为第0小时
            all_sheets[date] = wide_df
            migrated_count += 1

    if migrated_count == 0:
        print("CSV数据已存在于Excel中，无需迁移")
    else:
        gc.collect()
        time.sleep(0.1)
        with pd.ExcelWriter(xlsx_filename, engine='openpyxl') as writer:
            for sheet_name, sheet_df in all_sheets.items():
                sheet_df.to_excel(writer, sheet_name=str(sheet_name), index=False)
        gc.collect()
        print(f"已迁移 {migrated_count} 天的数据到 {xlsx_filename}")

    # 迁移后重命名CSV
    csv_backup = csv_filename.replace(".csv", "_backup.csv")
    os.rename(csv_filename, csv_backup)
    print(f"原CSV文件已重命名为: {csv_backup}")


def get_price_changes(filename="output/knife_prices.xlsx"):
    """
    计算价格变动

    Args:
        filename: Excel文件名

    Returns:
        pd.DataFrame: 价格变动数据
    """
    df = load_price_history(filename)

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(['knife_name', 'date'])

    df['price_change'] = df.groupby('knife_name')['price'].diff()
    df['price_change_pct'] = df.groupby('knife_name')['price'].pct_change() * 100

    return df


def separate_knife_types(items):
    """
    将刀饰品按是否带计数器分类

    Args:
        items: 解析后的刀饰品数据列表

    Returns:
        tuple: (不带计数器的刀饰品, 带计数器的刀饰品)
    """
    normal_knives = []
    stattrak_knives = []

    for item in items:
        if "StatTrak" in item["name"] or "StatTrak™" in item["name"]:
            stattrak_knives.append(item)
        else:
            normal_knives.append(item)

    return normal_knives, stattrak_knives
