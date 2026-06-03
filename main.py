"""
Buff刀饰品价格追踪工具 - 主程序

功能：
1. 使用Cookie登录Buff平台
2. 获取所有无涂装刀饰品（包括带计数器和不带计数器的版本）
3. 记录每小时价格数据到Excel文件（宽格式：knife_name, price_0...price_23）
4. 生成交互式HTML价格趋势折线图（X轴为0-23小时）
5. 支持 GitHub Actions 定时运行（每小时一次）
6. 本地运行结束时发送Windows通知

使用方法：
1. 运行 python get_cookie.py 获取Cookie
2. 运行: python main.py
"""

import sys
import os
from datetime import datetime

# 设置环境变量，确保UTF-8输出
os.environ['PYTHONIOENCODING'] = 'utf-8'

from buff_api import fetch_knife_items, filter_vanilla_knives, verify_vanilla_completeness, retry_missing_knives
from data_parser import (
    parse_knife_items,
    save_hourly_price_data,
    load_price_history,
    separate_knife_types,
    migrate_csv_to_xlsx,
)
from chart_generator import generate_knife_report
from dashboard_generator import generate_dashboard
from config import BUFF_COOKIE, OUTPUT_DIR

# 判断是否在云端运行（GitHub Actions 没有 winsound 和 Windows 通知）
IS_CLOUD = os.environ.get("GITHUB_ACTIONS") == "true"

if not IS_CLOUD:
    try:
        from notification import send_notification
    except ImportError:
        send_notification = None
else:
    send_notification = None


def main():
    print("=" * 60, flush=True)
    print("Buff刀饰品价格追踪工具", flush=True)
    print("=" * 60, flush=True)
    now = datetime.now()
    print(f"运行时间: {now.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    # 检查Cookie配置
    if not BUFF_COOKIE:
        print("错误: 请先获取Cookie", flush=True)
        print("运行 python get_cookie.py 来获取Cookie", flush=True)
        print("或者在 GitHub Actions 中设置 BUFF_COOKIE secret", flush=True)
        return

    cookie_preview = BUFF_COOKIE[:20] + "..." if len(BUFF_COOKIE) > 20 else BUFF_COOKIE
    print(f"Cookie已配置: {cookie_preview}", flush=True)

    # 迁移旧CSV数据到新的Excel格式（如有）
    migrate_csv_to_xlsx()
    xlsx_filename = os.path.join(OUTPUT_DIR, "knife_prices.xlsx")

    # 步骤1：获取所有刀饰品数据
    print("\n[1/4] 正在获取所有刀饰品数据...", flush=True)
    raw_items = fetch_knife_items()

    if not raw_items:
        print("获取数据失败，请检查登录信息是否正确")
        if send_notification:
            send_notification("Buff刀饰品价格追踪", "数据获取失败，请检查登录信息")
        return

    print(f"\n共获取 {len(raw_items)} 个刀饰品")

    # 步骤2：筛选无涂装刀饰品
    print("\n[2/4] 正在筛选无涂装刀饰品...")
    vanilla_knives, stattrak_vanilla_knives = filter_vanilla_knives(raw_items)

    print(f"不带计数器的无涂装刀: {len(vanilla_knives)} 个")
    print(f"带计数器的无涂装刀: {len(stattrak_vanilla_knives)} 个")

    # 合并所有无涂装刀饰品
    all_vanilla_knives = vanilla_knives + stattrak_vanilla_knives

    if not all_vanilla_knives:
        print("没有找到无涂装刀饰品")
        if send_notification:
            send_notification("Buff刀饰品价格追踪", "没有找到无涂装刀饰品")
        return

    # 验证数据完整性，缺失时自动重试
    print("\n  验证数据完整性...")
    missing = verify_vanilla_completeness((vanilla_knives, stattrak_vanilla_knives))
    if missing:
        print(f"  → 发现 {len(missing)} 把刀缺失，启动补全重试...")
        # 重新获取完整列表（会得到所有刀的汇总，不仅仅是缺失的）
        retry_raw = fetch_knife_items()
        retry_vanilla, retry_stattrak = filter_vanilla_knives(retry_raw)
        # 合并原始结果和重试结果（去重）
        all_raw_names = {
            item["market_hash_name"]
            for item in raw_items + retry_raw
            if '|' not in item.get("market_hash_name", "")
        }
        still_missing = sorted(set(missing) - all_raw_names)
        if still_missing:
            print(f"  ⚠️ 重试后仍缺失 {len(still_missing)} 把: {', '.join(still_missing)}")
        else:
            print(f"  ✅ 重试后全部补齐")

        # 使用补全后的数据
        all_vanilla_knives = [
            item for item in raw_items + retry_raw
            if '|' not in item.get("market_hash_name", "")
        ]
        # 去重（按 id）
        seen = set()
        deduped = []
        for item in all_vanilla_knives:
            item_id = item.get("id")
            if item_id and item_id not in seen:
                seen.add(item_id)
                deduped.append(item)
        all_vanilla_knives = deduped
        vanilla_knives, stattrak_vanilla_knives = filter_vanilla_knives(all_vanilla_knives)
        print(f"  补全后: 普通 {len(vanilla_knives)} + StatTrak {len(stattrak_vanilla_knives)} = {len(vanilla_knives) + len(stattrak_vanilla_knives)}")

    # 步骤3：解析数据并保存到Excel（宽格式，更新当前小时列）
    print("\n[3/4] 正在解析数据并保存价格记录...")
    parsed_items = parse_knife_items(all_vanilla_knives)

    # 保存到Excel（追加当前小时的价格到当天的sheet中）
    save_hourly_price_data(parsed_items, xlsx_filename)

    # 步骤4：生成图表（基于今天的小时数据）
    print("\n[4/4] 正在生成价格趋势图表...")
    generate_knife_report()

    # 步骤5：生成仪表盘页面（首页+数据表格）
    print("\n[5/5] 正在生成仪表盘页面...")
    generate_dashboard()

    # 完成提示
    print("\n" + "=" * 60)
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"数据保存: {xlsx_filename}")
    print(f"图表输出: {OUTPUT_DIR}/")
    print("=" * 60)

    # 本地运行时发送Windows通知
    if send_notification:
        send_notification(
            "Buff刀饰品价格追踪",
            f"数据采集完成！\n"
            f"不带计数器的刀: {len(vanilla_knives)} 个\n"
            f"带计数器的刀: {len(stattrak_vanilla_knives)} 个\n"
            f"数据已保存到 {xlsx_filename}"
        )


if __name__ == "__main__":
    main()
