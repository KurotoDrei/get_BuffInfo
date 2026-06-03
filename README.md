# Buff 刀饰品价格追踪

每小时自动采集 Buff 平台 40 把无涂装刀（Vanilla Knife）的价格，生成交互式趋势图表和历史数据表格，通过 GitHub Pages 在线展示。

## 在线仪表盘

👉 **https://kurotodrei.github.io/get_BuffInfo/**

| 页面 | 功能 |
|------|------|
| 普通刀折线图 | 20 把普通无涂装刀 24 小时价格走势 |
| StatTrak 折线图 | 20 把 StatTrak 版刀 24 小时价格走势 |
| 数据表格 | 全历史数据交互表格（搜索/排序/分页/日期筛选） |
| Cookie 设置 | Cookie 获取与更新指南 |

## 功能

- 每小时第 5 分钟自动运行（GitHub Actions）
- 记录 24 小时价格数据到 Excel 宽表（`knife_name | price_0 ... price_23`）
- 生成 Plotly 交互式 HTML 折线图（X 轴 = 0-23 小时）
- 全历史数据表格（客户端搜索 / 排序 / 分页 / 日期筛选）
- 侧边栏导航，多页面统一入口
- 支持 GitHub Actions 云端运行 + GitHub Pages 展示
- 支持本地运行（Windows 通知）

## 前置条件

- Python 3.11+
- Buff 平台账号（需 Steam 登录）
- GitHub 账号（用于部署）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/KurotoDrei/get_BuffInfo.git
cd get_BuffInfo
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 设置 Cookie

**方式一：本地工具（推荐）**

```bash
python cookie_setup.py
```
按提示操作——打开浏览器获取 Cookie、输入 GitHub Token，工具自动更新仓库 Secret。

**方式二：手动设置 GitHub Secret**

1. 从浏览器获取 Cookie（F12 → Network → 复制 Request Headers 中的 Cookie 字段）
2. 打开仓库 [Settings → Secrets and variables → Actions](https://github.com/KurotoDrei/get_BuffInfo/settings/secrets/actions)
3. 点击 **New repository secret**，Name: `BUFF_COOKIE`，Value: 粘贴 Cookie
4. 点击 **Add secret**

### 4. 本地测试

```bash
python main.py
```

### 5. 触发 GitHub Actions

在 [Actions 页面](https://github.com/KurotoDrei/get_BuffInfo/actions) 点击 **Run workflow**。

之后系统会在每小时第 5 分钟自动运行，更新 `output/` 目录下的 HTML 文件和 Excel 数据，GitHub Pages 会自动展示最新内容。

## 输出文件

```
output/
├── index.html                  # 仪表盘首页（侧边栏导航）
├── normal_knives_trend.html    # 普通刀 24h 折线图
├── stattrak_knives_trend.html  # StatTrak 刀 24h 折线图
├── data_table.html             # 全历史数据交互表格
├── cookie_guide.html           # Cookie 设置指南
└── knife_prices.xlsx           # 原始价格数据（宽表格式）
    └── Sheet: YYYY-MM-DD
        ├── knife_name
        ├── price_0  (00:00)
        ├── price_1  (01:00)
        ├── ...
        └── price_23 (23:00)
```

## 本地运行

在本地同样可运行，结果输出到 `output/` 目录：

```bash
python main.py
```

本地运行时需先设置 `BUFF_COOKIE` 环境变量：

```powershell
$env:BUFF_COOKIE="session=xxx"; python main.py
```

## 项目结构

```
├── .github/workflows/hourly.yml   # GitHub Actions 工作流（每小时运行）
├── buff_api.py                     # Buff API 封装（fetch/筛选/命名）
├── chart_generator.py              # Plotly 交互式图表生成
├── config.py                       # 配置（API URL、输出目录）
├── cookie_setup.py                 # Cookie 获取与 GitHub Secret 更新工具
├── dashboard_generator.py          # 仪表盘页面生成（index/data_table/cookie_guide）
├── data_parser.py                  # 数据解析/Excel读写/CSV迁移
├── main.py                         # 主入口
├── get_cookie.py                   # （旧）本地 Cookie 获取脚本
├── requirements.txt                # Python 依赖
├── CONTEXT.md                      # 项目术语表
└── docs/adr/                       # 架构决策记录
```

## 测试

```bash
pytest -v
```

包含 39 个测试用例，覆盖 API、数据解析、图表生成。

## 常见问题

### Cookie 过期了怎么办？

Buff Session 会不定期过期。重新运行：

```bash
python cookie_setup.py
```

### 数据没更新？

1. 检查 [Actions 运行状态](https://github.com/KurotoDrei/get_BuffInfo/actions)
2. 确认 `BUFF_COOKIE` Secret 是否有效
3. 手动触发一次 **Run workflow**

### 为什么是 40 把刀？

Buff 平台上有 20 种无涂装刀，每种有普通版和 StatTrak 版，共 40 个独立商品。

## 技术栈

- **数据采集**: Python + Buff API
- **数据存储**: Excel (openpyxl)
- **图表**: Plotly (交互式 HTML)
- **自动化**: GitHub Actions (cron 每小时)
- **展示**: GitHub Pages
- **测试**: pytest (39 tests)
