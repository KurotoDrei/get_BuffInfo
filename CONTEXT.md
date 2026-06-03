# 项目术语表

## 领域概念

### Buff 平台
中国最大的 CS2/CSGO 饰品的第三方交易平台（buff.163.com）。提供市场行情、买卖挂单等功能。需要通过 Steam OAuth 登录才能访问 API。

### 无涂装刀 (Vanilla Knife)
没有任何图案涂层的刀饰品。与 Doppler、Tiger Tooth 等涂装版本相对。每种刀都有普通版和 StatTrak 版两种变体。

### StatTrak™
计数器版本，饰品上带有击杀计数显示。同一把刀有普通版和 StatTrak™ 版，后者在名称中包含 "StatTrak™"。

### Goods (商品)
Buff API 中对挂牌物品的称呼。每个 goods 包含 `market_hash_name`、`sell_min_price`、`sell_listing` 等字段。

### sell_min_price
Buff 平台上某饰品当前最低挂牌出售价格（单位：元）。

### 已知清单 (Known Vanilla Knife List)
硬编码在 `buff_api.py` 中的 40 把无涂装刀名称（20 普通 + 20 StatTrak），用于验证 API 返回数据是否完整。当某次运行时检测到缺失某些刀，将通过重新抓取自动补全。

## 数据格式

### 宽表 (Wide Format)
Excel 存储格式：`knife_name | price_0 | price_1 | ... | price_23`。每行代表一把刀，每小时一个价格列。同一天多次运行只更新当前小时列。

### 长表 (Long Format)
图表展示格式：`date | knife_name | price`。每行一个数据点，通过 melt（逆透视）将宽表转换得到。

## 技术概念

### sort_by
Buff API 分页参数。使用 `sort_by=name` 确保物品按名字排序，避免分页过程中物品在页面间漂移导致重复或遗漏。

### BUFF_COOKIE
环境变量 / GitHub Actions Secret，存储 Buff 登录 Cookie，用于 API 认证。

### GitHub Pages
静态网站托管，从 main 分支根目录提供 HTML 文件。URL: `https://kurotodrei.github.io/get_BuffInfo/`

### msg 桌面通知
Windows `msg *` 命令，从 SYSTEM 环境（Task Scheduler）向当前登录用户发送桌面弹窗。用于定时任务运行完成后的本地通知。
