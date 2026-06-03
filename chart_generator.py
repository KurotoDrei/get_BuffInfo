"""
图表生成模块 - 使用Plotly生成交互式HTML价格趋势图表（全历史数据）
"""

import plotly.graph_objects as go
import pandas as pd
import os
from config import OUTPUT_DIR


def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def plot_historical_trend(df, title, filename):
    """
    绘制全历史价格趋势折线图（交互式HTML）

    Args:
        df: 包含date, knife_name, price列的DataFrame
        title: 图表标题
        filename: 输出HTML文件名
    """
    ensure_output_dir()

    if df.empty:
        print(f"没有数据用于生成 {filename}")
        return

    latest_date = df['date'].max()
    # 初始显示最近24小时，刷新自动跳到最新
    default_range = [latest_date - pd.Timedelta(hours=24), latest_date]

    fig = go.Figure()

    for knife_name, group in df.groupby('knife_name'):
        group = group.sort_values('date')
        display_name = str(knife_name).replace('\u2122', '')

        fig.add_trace(go.Scatter(
            x=group['date'],
            y=group['price'],
            mode='lines+markers',
            name=display_name,
            line=dict(width=2),
            marker=dict(size=5),
            hovertemplate=(
                f'<b>{display_name}</b><br>'
                '%{x|%m-%d %H:00}<br>'
                '价格: ¥%{y:.2f}'
                '<extra></extra>'
            ),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title='时间',
        yaxis_title='价格 (元)',
        hovermode='closest',
        hoverlabel=dict(
            namelength=-1,
        ),
        xaxis=dict(
            tickformat='%m-%d %H:00',
            tickangle=-60,              # 纵向显示，避免标签重叠
            nticks=15,                   # 控制刻度密度
            rangeslider=dict(visible=True),  # 底部全景滚动条
            range=default_range,            # 初始化定位到最新数据
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
        ),
        template='plotly_white',
        height=700,
        margin=dict(r=250, t=60, b=60, l=80),
    )

    fig.update_yaxes(exponentformat='none')

    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.write_html(filepath)
    print(f"图表已保存: {filepath}")


def plot_normal_knives_trend(df):
    """
    绘制不带计数器的刀饰品全历史价格趋势

    Args:
        df: 包含date, knife_name, price列的DataFrame
    """
    if df.empty:
        print("没有数据用于生成不带计数器的刀饰品图表")
        return

    normal_df = df[~df['knife_name'].str.contains('StatTrak', na=False)]

    if normal_df.empty:
        print("没有不带计数器的刀饰品数据")
        return

    plot_historical_trend(normal_df, "无涂装刀饰品历史价格走势（不带计数器）", "normal_knives_trend.html")


def plot_stattrak_knives_trend(df):
    """
    绘制带计数器的刀饰品全历史价格趋势

    Args:
        df: 包含date, knife_name, price列的DataFrame
    """
    if df.empty:
        print("没有数据用于生成带计数器的刀饰品图表")
        return

    stattrak_df = df[df['knife_name'].str.contains('StatTrak', na=False)]

    if stattrak_df.empty:
        print("没有带计数器的刀饰品数据")
        return

    plot_historical_trend(stattrak_df, "无涂装刀饰品历史价格走势（带计数器）", "stattrak_knives_trend.html")


def generate_knife_report():
    """
    生成刀饰品价格报告（基于全历史数据）
    """
    from data_parser import load_price_history

    df = load_price_history()

    if df.empty:
        print("没有历史价格数据，请先运行数据采集")
        return

    print("正在生成价格趋势图表...")

    # 生成不带计数器的刀饰品图表
    plot_normal_knives_trend(df)

    # 生成带计数器的刀饰品图表
    plot_stattrak_knives_trend(df)

    print("图表生成完成！")


def generate_report(top_gainers, top_losers, all_df):
    """
    生成完整报告（兼容旧版本）
    """
    generate_knife_report()
