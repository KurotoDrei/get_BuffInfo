"""
图表生成模块测试（全历史数据格式）
"""

import pytest
import pandas as pd
import os
import tempfile
from datetime import datetime
from chart_generator import (
    plot_historical_trend,
    plot_normal_knives_trend,
    plot_stattrak_knives_trend,
)


@pytest.fixture
def sample_historical_data():
    """模拟全历史价格数据"""
    data = {
        "date": [
            datetime(2026, 6, 2, 8, 0), datetime(2026, 6, 2, 9, 0), datetime(2026, 6, 2, 10, 0),
            datetime(2026, 6, 2, 8, 0), datetime(2026, 6, 2, 9, 0), datetime(2026, 6, 2, 10, 0),
            datetime(2026, 6, 2, 8, 0), datetime(2026, 6, 2, 9, 0), datetime(2026, 6, 2, 10, 0),
        ],
        "knife_name": [
            "★ Karambit", "★ Karambit", "★ Karambit",
            "★ Butterfly Knife", "★ Butterfly Knife", "★ Butterfly Knife",
            "★ StatTrak™ Karambit", "★ StatTrak™ Karambit", "★ StatTrak™ Karambit",
        ],
        "price": [1500.0, 1510.0, 1505.0, 1200.0, 1210.0, 1205.0, 1800.0, 1810.0, 1805.0],
    }
    return pd.DataFrame(data)


class TestPlotHistoricalTrend:
    """测试全历史价格趋势折线图"""

    def test_plot_with_data(self, sample_historical_data):
        """测试有数据时绘制图表"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            import chart_generator
            original_dir = chart_generator.OUTPUT_DIR
            chart_generator.OUTPUT_DIR = tmpdir

            try:
                plot_historical_trend(sample_historical_data, "测试图表", "test.html")

                filepath = os.path.join(tmpdir, "test.html")
                assert os.path.exists(filepath)
                assert os.path.getsize(filepath) > 0
            finally:
                chart_generator.OUTPUT_DIR = original_dir

    def test_plot_with_empty_data(self):
        """测试空数据时绘制图表"""
        empty_df = pd.DataFrame(columns=["date", "knife_name", "price"])
        plot_historical_trend(empty_df, "测试图表", "test.html")


class TestPlotNormalKnivesTrend:
    """测试不带计数器的刀饰品价格趋势"""

    def test_plot_normal_knives(self, sample_historical_data):
        """测试绘制不带计数器的刀饰品图表"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            import chart_generator
            original_dir = chart_generator.OUTPUT_DIR
            chart_generator.OUTPUT_DIR = tmpdir

            try:
                plot_normal_knives_trend(sample_historical_data)

                filepath = os.path.join(tmpdir, "normal_knives_trend.html")
                assert os.path.exists(filepath)
                assert os.path.getsize(filepath) > 0
            finally:
                chart_generator.OUTPUT_DIR = original_dir

    def test_plot_with_empty_data(self):
        """测试空数据时绘制图表"""
        empty_df = pd.DataFrame(columns=["date", "knife_name", "price"])
        plot_normal_knives_trend(empty_df)


class TestPlotStattrakKnivesTrend:
    """测试带计数器的刀饰品价格趋势"""

    def test_plot_stattrak_knives(self, sample_historical_data):
        """测试绘制带计数器的刀饰品图表"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            import chart_generator
            original_dir = chart_generator.OUTPUT_DIR
            chart_generator.OUTPUT_DIR = tmpdir

            try:
                plot_stattrak_knives_trend(sample_historical_data)

                filepath = os.path.join(tmpdir, "stattrak_knives_trend.html")
                assert os.path.exists(filepath)
                assert os.path.getsize(filepath) > 0
            finally:
                chart_generator.OUTPUT_DIR = original_dir

    def test_plot_with_empty_data(self):
        """测试空数据时绘制图表"""
        empty_df = pd.DataFrame(columns=["date", "knife_name", "price"])
        plot_stattrak_knives_trend(empty_df)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
