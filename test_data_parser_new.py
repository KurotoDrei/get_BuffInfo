"""
数据解析模块测试
"""

import pytest
import pandas as pd
import os
import tempfile
from datetime import datetime
from data_parser import (
    parse_knife_items,
    save_hourly_price_data,
    load_price_history,
    load_today_hourly_data,
    separate_knife_types,
    sort_knife_items,
)
from buff_api import filter_vanilla_knives, get_knife_name_in_chinese


@pytest.fixture
def sample_raw_items():
    """模拟Buff API返回的原始刀饰品数据"""
    return [
        {
            "id": 1001,
            "market_hash_name": "★ Karambit",
            "sell_min_price": "1500.00",
            "sell_num": 100,
            "buy_num": 50,
        },
        {
            "id": 1002,
            "market_hash_name": "★ StatTrak™ Karambit",
            "sell_min_price": "1800.00",
            "sell_num": 50,
            "buy_num": 20,
        },
        {
            "id": 1003,
            "market_hash_name": "★ Butterfly Knife",
            "sell_min_price": "1200.00",
            "sell_num": 80,
            "buy_num": 30,
        },
        {
            "id": 1004,
            "market_hash_name": "★ Karambit | Doppler (Factory New)",
            "sell_min_price": "2000.00",
            "sell_num": 30,
            "buy_num": 10,
        },
    ]


@pytest.fixture
def sample_parsed_items():
    """解析后的刀饰品数据"""
    return [
        {
            "id": 1001,
            "name": "★ Karambit",
            "chinese_name": "★ Karambit",
            "price": 1500.0,
            "sell_num": 100,
            "buy_num": 50,
        },
        {
            "id": 1002,
            "name": "★ StatTrak™ Karambit",
            "chinese_name": "★ StatTrak™ Karambit",
            "price": 1800.0,
            "sell_num": 50,
            "buy_num": 20,
        },
        {
            "id": 1003,
            "name": "★ Butterfly Knife",
            "chinese_name": "★ Butterfly Knife",
            "price": 1200.0,
            "sell_num": 80,
            "buy_num": 30,
        },
    ]


class TestGetKnifeNameInChinese:
    """测试名称映射（直接使用英文名称）"""

    def test_normal_knife(self):
        assert get_knife_name_in_chinese("★ Karambit") == "★ Karambit"
        assert get_knife_name_in_chinese("★ Butterfly Knife") == "★ Butterfly Knife"
        assert get_knife_name_in_chinese("★ M9 Bayonet") == "★ M9 Bayonet"

    def test_stattrak_knife(self):
        assert get_knife_name_in_chinese("★ StatTrak™ Karambit") == "★ StatTrak™ Karambit"
        assert get_knife_name_in_chinese("★ StatTrak™ Butterfly Knife") == "★ StatTrak™ Butterfly Knife"

    def test_unknown_knife(self):
        assert get_knife_name_in_chinese("★ Unknown Knife") == "★ Unknown Knife"


class TestParseKnifeItems:
    """测试刀饰品数据解析"""

    def test_parse_normal_items(self, sample_raw_items):
        result = parse_knife_items(sample_raw_items)
        assert len(result) == 4
        assert result[0]["id"] == 1001
        assert result[0]["name"] == "★ Karambit"
        assert result[0]["chinese_name"] == "★ Karambit"
        assert result[0]["price"] == 1500.0

    def test_parse_empty_list(self):
        result = parse_knife_items([])
        assert result == []

    def test_parse_missing_fields(self):
        items = [{"id": 2001}]
        result = parse_knife_items(items)
        assert len(result) == 1
        assert result[0]["name"] == ""
        assert result[0]["price"] == 0.0


class TestSortKnifeItems:
    """测试按基础名称排序"""

    def test_sort_basic(self, sample_parsed_items):
        sorted_items = sort_knife_items(sample_parsed_items)
        assert len(sorted_items) == 3
        assert sorted_items[0]["name"] == "★ Butterfly Knife"
        assert sorted_items[1]["name"] == "★ Karambit"
        assert sorted_items[2]["name"] == "★ StatTrak™ Karambit"

    def test_sort_empty(self):
        assert sort_knife_items([]) == []


class TestFilterVanillaKnives:
    """测试无涂装刀饰品筛选"""

    def test_filter_vanilla_knives(self, sample_raw_items):
        vanilla, stattrak = filter_vanilla_knives(sample_raw_items)
        assert len(vanilla) == 2
        assert len(stattrak) == 1

    def test_filter_with_doppler(self, sample_raw_items):
        vanilla, stattrak = filter_vanilla_knives(sample_raw_items)
        vanilla_names = [item["market_hash_name"] for item in vanilla]
        assert "★ Karambit | Doppler (Factory New)" not in vanilla_names

    def test_filter_empty_list(self):
        vanilla, stattrak = filter_vanilla_knives([])
        assert vanilla == []
        assert stattrak == []


class TestSeparateKnifeTypes:
    """测试刀饰品分类"""

    def test_separate_knife_types(self, sample_parsed_items):
        normal, stattrak = separate_knife_types(sample_parsed_items)
        assert len(normal) == 2
        assert len(stattrak) == 1

    def test_separate_empty_list(self):
        normal, stattrak = separate_knife_types([])
        assert normal == []
        assert stattrak == []


class TestSaveAndLoadPriceData:
    """测试每小时价格数据保存和加载（宽格式）"""

    def test_save_and_load(self, sample_parsed_items):
        """测试保存和加载：宽格式包含所有price_N列"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            filename = os.path.join(tmpdir, "test_prices.xlsx")
            save_hourly_price_data(sample_parsed_items, filename)

            assert os.path.exists(filename)

            # 验证宽格式存在
            today = datetime.now().strftime("%Y-%m-%d")
            xls = pd.ExcelFile(filename)
            assert today in xls.sheet_names

            sheet_df = pd.read_excel(filename, sheet_name=today)
            # 验证有 price_N 列
            assert "knife_name" in sheet_df.columns
            price_cols = [c for c in sheet_df.columns if str(c).startswith("price_")]
            assert len(price_cols) == 24
            assert len(sheet_df) == 3

    def test_hourly_append(self, sample_parsed_items):
        """测试同一天不同小时：追加价格到对应列，不覆盖其他小时"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            filename = os.path.join(tmpdir, "test_prices.xlsx")

            # 第一次保存（当前小时）
            save_hourly_price_data(sample_parsed_items, filename)

            # 第二次保存（同一天，应更新price_N列但不重复添加行）
            save_hourly_price_data(sample_parsed_items, filename)

            today = datetime.now().strftime("%Y-%m-%d")
            sheet_df = pd.read_excel(filename, sheet_name=today)

            # 行数应仍然是3（不是6）
            assert len(sheet_df) == 3

            # 验证有价格数据
            hour = datetime.now().hour
            assert f"price_{hour}" in sheet_df.columns

    def test_load_price_history_compat(self, sample_parsed_items):
        """测试 load_price_history 能正确读取宽格式并转为长格式"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            filename = os.path.join(tmpdir, "test_prices.xlsx")
            save_hourly_price_data(sample_parsed_items, filename)

            df = load_price_history(filename)
            assert not df.empty
            assert "date" in df.columns
            assert "knife_name" in df.columns
            assert "price" in df.columns

            # 每小时一条记录，3个饰品
            # 当前小时有数据，其他小时为None被dropna过滤
            # 至少有1小时 × 3 = 3条
            assert len(df) >= 3

    def test_load_today_hourly(self, sample_parsed_items):
        """测试 load_today_hourly_data"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            filename = os.path.join(tmpdir, "test_prices.xlsx")
            save_hourly_price_data(sample_parsed_items, filename)

            hourly_df = load_today_hourly_data(filename)
            assert not hourly_df.empty
            assert "hour" in hourly_df.columns
            assert "knife_name" in hourly_df.columns
            assert "price" in hourly_df.columns

            # 当前小时有3个刀的价格
            assert len(hourly_df) == 3

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        df = load_price_history("nonexistent.xlsx")
        assert df.empty

        hourly_df = load_today_hourly_data("nonexistent.xlsx")
        assert hourly_df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
