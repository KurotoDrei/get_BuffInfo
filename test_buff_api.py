"""
Buff API模块深度测试
"""

import pytest
import os
import tempfile
from buff_api import (
    get_headers,
    ensure_login,
    filter_vanilla_knives,
    get_knife_name_in_chinese,
)


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
        {
            "id": 1005,
            "market_hash_name": "★ StatTrak™ Butterfly Knife",
            "sell_min_price": "1600.00",
            "sell_num": 40,
            "buy_num": 15,
        },
        {
            "id": 1006,
            "market_hash_name": "★ M9 Bayonet | Tiger Tooth (Factory New)",
            "sell_min_price": "2500.00",
            "sell_num": 20,
            "buy_num": 5,
        },
    ]


class TestGetHeaders:
    """测试获取请求头"""

    def test_get_headers_with_cookie(self):
        """测试使用指定cookie获取请求头"""
        cookie = "test_cookie=123"
        headers = get_headers(cookie)
        
        assert headers["Cookie"] == cookie
        assert "User-Agent" in headers
        assert "Accept" in headers

    def test_get_headers_without_cookie(self):
        """测试不使用cookie获取请求头"""
        import buff_api
        original_cookie = buff_api.BUFF_COOKIE
        buff_api.BUFF_COOKIE = "test_cookie=123"

        try:
            headers = get_headers()
            assert "Cookie" in headers
            assert headers["Cookie"] == "test_cookie=123"
            assert "User-Agent" in headers
        finally:
            buff_api.BUFF_COOKIE = original_cookie


class TestEnsureLogin:
    """测试确保已登录"""

    def test_ensure_login_with_cookie(self):
        """测试有cookie时确保已登录"""
        # 临时设置BUFF_COOKIE
        import buff_api
        original_cookie = buff_api.BUFF_COOKIE
        buff_api.BUFF_COOKIE = "test_cookie=123"
        
        try:
            cookie = ensure_login()
            assert cookie == "test_cookie=123"
        finally:
            # 恢复原始值
            buff_api.BUFF_COOKIE = original_cookie

    def test_ensure_login_without_cookie(self):
        """测试没有cookie时确保已登录"""
        # 临时清空BUFF_COOKIE
        import buff_api
        original_cookie = buff_api.BUFF_COOKIE
        buff_api.BUFF_COOKIE = ""
        
        try:
            cookie = ensure_login()
            assert cookie == ""
        finally:
            # 恢复原始值
            buff_api.BUFF_COOKIE = original_cookie


class TestFilterVanillaKnives:
    """测试无涂装刀饰品筛选"""

    def test_filter_vanilla_knives(self, sample_raw_items):
        """测试筛选无涂装刀饰品"""
        vanilla, stattrak = filter_vanilla_knives(sample_raw_items)

        # 应该有2个普通无涂装刀：★ Karambit, ★ Butterfly Knife
        assert len(vanilla) == 2
        # 应该有2个带计数器的无涂装刀：★ StatTrak™ Karambit, ★ StatTrak™ Butterfly Knife
        assert len(stattrak) == 2

    def test_filter_with_doppler(self, sample_raw_items):
        """测试筛选不包含有涂装的刀"""
        vanilla, stattrak = filter_vanilla_knives(sample_raw_items)

        # ★ Karambit | Doppler (Factory New) 不应该被选中
        vanilla_names = [item["market_hash_name"] for item in vanilla]
        assert "★ Karambit | Doppler (Factory New)" not in vanilla_names

    def test_filter_with_tiger_tooth(self, sample_raw_items):
        """测试筛选不包含Tiger Tooth涂装的刀"""
        vanilla, stattrak = filter_vanilla_knives(sample_raw_items)

        # ★ M9 Bayonet | Tiger Tooth (Factory New) 不应该被选中
        vanilla_names = [item["market_hash_name"] for item in vanilla]
        assert "★ M9 Bayonet | Tiger Tooth (Factory New)" not in vanilla_names

    def test_filter_empty_list(self):
        """测试空列表"""
        vanilla, stattrak = filter_vanilla_knives([])
        assert vanilla == []
        assert stattrak == []

    def test_filter_only_vanilla(self):
        """测试只包含无涂装刀的列表"""
        items = [
            {"id": 1, "market_hash_name": "★ Karambit"},
            {"id": 2, "market_hash_name": "★ Butterfly Knife"},
        ]
        vanilla, stattrak = filter_vanilla_knives(items)
        
        assert len(vanilla) == 2
        assert len(stattrak) == 0

    def test_filter_only_stattrak(self):
        """测试只包含带计数器无涂装刀的列表"""
        items = [
            {"id": 1, "market_hash_name": "★ StatTrak™ Karambit"},
            {"id": 2, "market_hash_name": "★ StatTrak™ Butterfly Knife"},
        ]
        vanilla, stattrak = filter_vanilla_knives(items)
        
        assert len(vanilla) == 0
        assert len(stattrak) == 2

    def test_filter_only_coated(self):
        """测试只包含有涂装刀的列表"""
        items = [
            {"id": 1, "market_hash_name": "★ Karambit | Doppler (Factory New)"},
            {"id": 2, "market_hash_name": "★ M9 Bayonet | Tiger Tooth (Factory New)"},
        ]
        vanilla, stattrak = filter_vanilla_knives(items)
        
        assert len(vanilla) == 0
        assert len(stattrak) == 0


class TestGetKnifeNameInChinese:
    """测试名称映射（直接使用英文名称）"""

    def test_normal_knife(self):
        """测试普通刀饰品名称映射"""
        assert get_knife_name_in_chinese("★ Karambit") == "★ Karambit"
        assert get_knife_name_in_chinese("★ Butterfly Knife") == "★ Butterfly Knife"
        assert get_knife_name_in_chinese("★ M9 Bayonet") == "★ M9 Bayonet"

    def test_stattrak_knife(self):
        """测试带计数器的刀饰品名称映射"""
        assert get_knife_name_in_chinese("★ StatTrak™ Karambit") == "★ StatTrak™ Karambit"
        assert get_knife_name_in_chinese("★ StatTrak™ Butterfly Knife") == "★ StatTrak™ Butterfly Knife"

    def test_unknown_knife(self):
        """测试未知刀饰品名称映射"""
        assert get_knife_name_in_chinese("★ Unknown Knife") == "★ Unknown Knife"

    def test_coated_knife(self):
        """测试有涂装刀饰品名称映射"""
        assert get_knife_name_in_chinese("★ Karambit | Doppler (Factory New)") == "★ Karambit | Doppler (Factory New)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
