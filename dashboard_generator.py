"""
仪表盘生成模块 - 生成导航首页和交互式数据表格页面

生成的HTML文件：
- index.html: 侧边栏导航 + iframe内容区
- data_table.html: 全历史数据交互表格（搜索、排序、分页、日期筛选）
"""

import json
import os
import pandas as pd
from config import OUTPUT_DIR
from data_parser import load_price_history


def generate_dashboard():
    """生成所有仪表盘页面"""
    _generate_index_html()
    _generate_data_table_html()
    print("仪表盘页面生成完成！")


"""
仪表盘生成模块 - 生成导航首页和交互式数据表格页面

生成的HTML文件：
- index.html: 侧边栏导航 + iframe内容区
- data_table.html: 全历史数据交互表格（搜索、排序、分页、日期筛选）
- cookie_guide.html: Cookie 设置指南页
"""

import json
import os
import pandas as pd
from config import OUTPUT_DIR
from data_parser import load_price_history


def generate_dashboard():
    """生成所有仪表盘页面"""
    _generate_index_html()
    _generate_data_table_html()
    _generate_cookie_guide_html()
    print("仪表盘页面生成完成！")


def _generate_index_html():
    """生成带侧边栏的首页 (iframe嵌入其他页面)"""
    html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Buff刀饰品价格追踪</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f6fa; }
  .layout { display: flex; height: 100vh; }
  .sidebar {
    width: 220px; background: #1e1e2f; color: #cdd6f4;
    display: flex; flex-direction: column; flex-shrink: 0;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }
  .sidebar-header {
    padding: 20px 16px; border-bottom: 1px solid #313244;
    font-size: 16px; font-weight: 600; color: #f5f5f5;
    display: flex; align-items: center; gap: 10px;
  }
  .sidebar-header .icon { font-size: 22px; }
  .sidebar-nav { flex: 1; padding: 12px 0; }
  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 20px; cursor: pointer; transition: all 0.2s;
    border-left: 3px solid transparent; text-decoration: none; color: #cdd6f4; font-size: 14px;
  }
  .nav-item:hover { background: #313244; color: #fff; }
  .nav-item.active { background: #313244; border-left-color: #89b4fa; color: #89b4fa; font-weight: 500; }
  .nav-item .nav-icon { font-size: 18px; width: 24px; text-align: center; }
  .nav-separator { border: none; border-top: 1px solid #313244; margin: 8px 16px; }
  .content { flex: 1; display: flex; flex-direction: column; }
  .content iframe {
    flex: 1; width: 100%; border: none; background: #fff;
  }
  .content-header {
    padding: 10px 20px; background: #fff; border-bottom: 1px solid #e0e0e0;
    font-size: 13px; color: #666; display: flex; align-items: center; gap: 8px;
  }
  .content-header .dot { width: 8px; height: 8px; border-radius: 50%; background: #4caf50; display: inline-block; }
  @media (max-width: 600px) {
    .sidebar { width: 56px; }
    .sidebar-header span.label, .nav-item span.label { display: none; }
    .sidebar-header { justify-content: center; padding: 16px 8px; }
    .nav-item { justify-content: center; padding: 14px 8px; }
  }
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-header">
      <span class="icon">🔪</span>
      <span class="label">Buff 价格追踪</span>
    </div>
    <div class="sidebar-nav">
      <a class="nav-item active" href="#" onclick="switchPage('normal_knives_trend.html', this)" data-page="chart-normal">
        <span class="nav-icon">📈</span>
        <span class="label">普通刀折线图</span>
      </a>
      <a class="nav-item" href="#" onclick="switchPage('stattrak_knives_trend.html', this)" data-page="chart-st">
        <span class="nav-icon">📊</span>
        <span class="label">StatTrak折线图</span>
      </a>
      <a class="nav-item" href="#" onclick="switchPage('data_table.html', this)" data-page="table">
        <span class="nav-icon">📋</span>
        <span class="label">数据表格</span>
      </a>
      <hr class="nav-separator">
      <a class="nav-item" href="#" onclick="switchPage('cookie_guide.html', this)" data-page="cookie">
        <span class="nav-icon">🍪</span>
        <span class="label">Cookie 设置</span>
      </a>
    </div>
  </nav>
  <main class="content">
    <div class="content-header">
      <span class="dot"></span>
      <span id="pageTitle">普通刀折线图</span>
    </div>
    <iframe id="mainFrame" src="normal_knives_trend.html"></iframe>
  </main>
</div>
<script>
function switchPage(url, el) {
  document.getElementById('mainFrame').src = url;
  document.querySelectorAll('.nav-item').forEach(function(item) { item.classList.remove('active'); });
  if (el) el.classList.add('active');
  var titles = {
    'chart-normal': '普通刀折线图',
    'chart-st': 'StatTrak折线图',
    'table': '数据表格',
    'cookie': 'Cookie 设置指南'
  };
  var page = el ? el.getAttribute('data-page') : 'chart-normal';
  document.getElementById('pageTitle').textContent = titles[page] || '普通刀折线图';
}
</script>
</body>
</html>'''
    filepath = os.path.join(OUTPUT_DIR, 'index.html')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"首页已生成: {filepath}")


def _generate_data_table_html():
    """生成全历史数据交互表格页面（JS搜索+排序+分页+日期筛选）"""
    df = load_price_history()
    records = []
    if not df.empty:
        # 处理TM字符，确保JSON可序列化
        df['knife_name'] = df['knife_name'].astype(str).str.replace('\u2122', '')
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d %H:%M')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        # 过滤无效价格
        df = df.dropna(subset=['price'])
        records = df[['date_str', 'knife_name', 'price']].to_dict(orient='records')

    data_json = json.dumps(records, ensure_ascii=False)

    html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全历史数据表格 - Buff刀饰品价格追踪</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #fff; color: #333; padding: 20px; font-size: 14px;
  }
  h1 { font-size: 20px; margin-bottom: 16px; color: #1e1e2f; }
  .toolbar {
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
    margin-bottom: 16px; padding: 12px 16px; background: #f8f9fa;
    border-radius: 8px; border: 1px solid #e0e0e0;
  }
  .toolbar label { font-size: 13px; color: #555; display: flex; align-items: center; gap: 6px; }
  .toolbar input, .toolbar select {
    padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
  }
  .toolbar input[type="text"] { width: 180px; }
  .toolbar input[type="date"] { width: 140px; }
  .toolbar .info { margin-left: auto; font-size: 13px; color: #888; }
  table {
    width: 100%; border-collapse: collapse; background: #fff;
    border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden;
  }
  thead { background: #f0f1f5; }
  th {
    padding: 10px 12px; text-align: left; font-weight: 600; font-size: 13px;
    color: #555; cursor: pointer; user-select: none; white-space: nowrap; border-bottom: 2px solid #ddd;
  }
  th:hover { background: #e4e6ed; }
  th .sort-arrow { margin-left: 4px; color: #999; font-size: 11px; }
  th.sorted-asc .sort-arrow::after { content: " ▲"; color: #89b4fa; }
  th.sorted-desc .sort-arrow::after { content: " ▼"; color: #89b4fa; }
  td { padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
  tr:hover { background: #f8f9ff; }
  .price-cell { text-align: right; font-variant-numeric: tabular-nums; }
  .pagination {
    display: flex; justify-content: center; align-items: center;
    gap: 4px; margin-top: 16px; flex-wrap: wrap;
  }
  .pagination button {
    padding: 6px 12px; border: 1px solid #ddd; background: #fff;
    border-radius: 4px; cursor: pointer; font-size: 13px; color: #333;
  }
  .pagination button:hover:not(:disabled) { background: #e4e6ed; }
  .pagination button.active { background: #89b4fa; color: #fff; border-color: #89b4fa; }
  .pagination button:disabled { opacity: 0.4; cursor: default; }
  .no-data { text-align: center; padding: 40px; color: #999; font-size: 15px; }
  @media (max-width: 600px) {
    body { padding: 10px; }
    .toolbar { flex-direction: column; align-items: stretch; }
    .toolbar input[type="text"] { width: 100%; }
    .toolbar .info { margin-left: 0; }
  }
</style>
</head>
<body>
<h1>📋 全历史价格数据</h1>
<div class="toolbar">
  <label>🔍 搜索: <input type="text" id="searchInput" placeholder="刀名搜索..." oninput="renderTable()"></label>
  <label>📅 开始: <input type="date" id="dateFrom" onchange="renderTable()"></label>
  <label>📅 结束: <input type="date" id="dateTo" onchange="renderTable()"></label>
  <label>
    每页:
    <select id="pageSize" onchange="renderTable()">
      <option value="25">25</option>
      <option value="50" selected>50</option>
      <option value="100">100</option>
      <option value="0">全部</option>
    </select>
  </label>
  <span class="info" id="dataInfo"></span>
</div>
<table>
  <thead>
    <tr>
      <th onclick="sortBy('date_str')">日期时间 <span class="sort-arrow"></span></th>
      <th onclick="sortBy('knife_name')">刀名 <span class="sort-arrow"></span></th>
      <th onclick="sortBy('price')" style="text-align:right">价格 (元) <span class="sort-arrow"></span></th>
    </tr>
  </thead>
  <tbody id="tableBody"></tbody>
</table>
<div class="pagination" id="pagination"></div>

<script>
var allData = ''' + data_json + r''';
var currentSort = { key: 'date_str', asc: false };
var currentPage = 1;

function renderTable() {
  var search = document.getElementById('searchInput').value.trim().toLowerCase();
  var dateFrom = document.getElementById('dateFrom').value;
  var dateTo = document.getElementById('dateTo').value;
  var pageSize = parseInt(document.getElementById('pageSize').value) || 0;

  // Filter
  var filtered = allData.filter(function(r) {
    if (search && !r.knife_name.toLowerCase().includes(search)) return false;
    if (dateFrom && r.date_str.slice(0, 10) < dateFrom) return false;
    if (dateTo && r.date_str.slice(0, 10) > dateTo) return false;
    return true;
  });

  // Sort
  var key = currentSort.key;
  filtered.sort(function(a, b) {
    var va = a[key], vb = b[key];
    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();
    if (va < vb) return currentSort.asc ? -1 : 1;
    if (va > vb) return currentSort.asc ? 1 : -1;
    return 0;
  });

  // Update info
  document.getElementById('dataInfo').textContent = '共 ' + filtered.length + ' 条记录';

  // Pagination
  var totalPages = pageSize > 0 ? Math.ceil(filtered.length / pageSize) : 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;
  var start = pageSize > 0 ? (currentPage - 1) * pageSize : 0;
  var end = pageSize > 0 ? start + pageSize : filtered.length;
  var pageData = filtered.slice(start, end);

  // Render rows
  var tbody = document.getElementById('tableBody');
  if (pageData.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" class="no-data">暂无数据</td></tr>';
  } else {
    tbody.innerHTML = pageData.map(function(r) {
      return '<tr><td>' + r.date_str + '</td><td>' + r.knife_name + '</td><td class="price-cell">¥' + Number(r.price).toFixed(2) + '</td></tr>';
    }).join('');
  }

  // Render pagination
  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  var el = document.getElementById('pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }

  var html = '';
  html += '<button onclick="goPage(1)"' + (currentPage <= 1 ? ' disabled' : '') + '>«</button>';
  html += '<button onclick="goPage(' + (currentPage - 1) + ')"' + (currentPage <= 1 ? ' disabled' : '') + '>‹</button>';

  var start = Math.max(1, currentPage - 2);
  var end = Math.min(totalPages, currentPage + 2);
  if (start > 1) html += '<button onclick="goPage(1)">1</button>' + (start > 2 ? '<button disabled>…</button>' : '');
  for (var i = start; i <= end; i++) {
    html += '<button class="' + (i === currentPage ? 'active' : '') + '" onclick="goPage(' + i + ')">' + i + '</button>';
  }
  if (end < totalPages) html += (end < totalPages - 1 ? '<button disabled>…</button>' : '') + '<button onclick="goPage(' + totalPages + ')">' + totalPages + '</button>';

  html += '<button onclick="goPage(' + (currentPage + 1) + ')"' + (currentPage >= totalPages ? ' disabled' : '') + '>›</button>';
  html += '<button onclick="goPage(' + totalPages + ')"' + (currentPage >= totalPages ? ' disabled' : '') + '>»</button>';
  el.innerHTML = html;
}

function goPage(p) {
  currentPage = p;
  renderTable();
}

function sortBy(key) {
  if (currentSort.key === key) {
    currentSort.asc = !currentSort.asc;
  } else {
    currentSort.key = key;
    currentSort.asc = key === 'date_str' ? false : true;
  }
  // Update header arrows
  document.querySelectorAll('th').forEach(function(th) {
    th.classList.remove('sorted-asc', 'sorted-desc');
  });
  var ths = document.querySelectorAll('th');
  var idx = {'date_str': 0, 'knife_name': 1, 'price': 2};
  ths[idx[key]].classList.add(currentSort.asc ? 'sorted-asc' : 'sorted-desc');
  currentPage = 1;
  renderTable();
}

// Initial render
renderTable();
</script>
</body>
</html>'''
    filepath = os.path.join(OUTPUT_DIR, 'data_table.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"数据表格页已生成: {filepath}")


def _generate_cookie_guide_html():
    """生成 Cookie 设置指南页"""
    html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cookie 设置指南 - Buff刀饰品价格追踪</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: #fff; color: #333; padding: 30px; font-size: 14px; line-height: 1.7;
  }
  h1 { font-size: 22px; margin-bottom: 20px; color: #1e1e2f; }
  h2 { font-size: 17px; margin: 24px 0 12px; color: #2d2d44; border-bottom: 1px solid #eee; padding-bottom: 6px; }
  h3 { font-size: 15px; margin: 18px 0 8px; color: #444; }
  .step-card {
    background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px 20px; margin: 12px 0;
  }
  .step-card .step-num {
    display: inline-block; background: #89b4fa; color: #fff; border-radius: 50%;
    width: 28px; height: 28px; text-align: center; line-height: 28px; font-weight: 600; font-size: 14px; margin-right: 8px;
  }
  code {
    background: #eef1f5; padding: 2px 6px; border-radius: 3px; font-family: "Cascadia Code", "Consolas", monospace; font-size: 13px; color: #d63384;
  }
  pre {
    background: #1e1e2f; color: #cdd6f4; padding: 14px 18px; border-radius: 6px; overflow-x: auto; font-size: 13px; line-height: 1.5; margin: 10px 0;
  }
  .tip { background: #e8f4fd; border-left: 4px solid #4a9eff; padding: 12px 16px; margin: 10px 0; border-radius: 4px; font-size: 13px; }
  .warn { background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 16px; margin: 10px 0; border-radius: 4px; font-size: 13px; }
  ul, ol { padding-left: 24px; margin: 8px 0; }
  li { margin: 4px 0; }
  a { color: #4a9eff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .btn {
    display: inline-block; padding: 10px 20px; border-radius: 6px; font-size: 14px;
    text-decoration: none; color: #fff; background: #89b4fa; margin: 6px 4px; font-weight: 500;
  }
  .btn:hover { opacity: 0.9; text-decoration: none; }
  .btn-secondary { background: #585b70; }
  @media (max-width: 600px) { body { padding: 16px; } }
</style>
</head>
<body>
<h1>🍪 Cookie 设置指南</h1>
<p>要让系统自动追踪价格，需要将你的 Buff 登录 Cookie 设为 GitHub 仓库的密钥（Secret）。</p>

<h2>方法一：使用本地工具（推荐）</h2>
<div class="step-card">
  <span class="step-num">1</span>
  <strong>安装依赖</strong>
  <p>在项目目录运行：</p>
  <pre>pip install pynacl requests</pre>
</div>

<div class="step-card">
  <span class="step-num">2</span>
  <strong>运行 Cookie 设置工具</strong>
  <pre>python cookie_setup.py</pre>
  <p>按提示操作，工具会自动：</p>
  <ul>
    <li>指导你从浏览器获取 Cookie</li>
    <li>通过 GitHub API 设置为仓库 Secret</li>
    <li>可选触发首次价格追踪运行</li>
  </ul>
</div>

<h2>方法二：手动设置</h2>

<div class="step-card">
  <span class="step-num">1</span>
  <strong>获取 Buff Cookie</strong>
  <ol>
    <li>浏览器打开 <a href="https://buff.163.com/" target="_blank">buff.163.com</a> 并登录 Steam</li>
    <li>按 <code>F12</code> 打开开发者工具</li>
    <li>切换到 <strong>Network（网络）</strong> 选项卡</li>
    <li>刷新页面（<code>F5</code>）</li>
    <li>在请求列表中点击任意 <code>buff.163.com</code> 的请求</li>
    <li>在 <strong>Request Headers</strong> 中找到 <code>Cookie:</code> 字段</li>
    <li>复制 <strong>完整</strong> 的 Cookie 值（以 <code>session=...</code> 开头的一长串）</li>
  </ol>
  <div class="tip">
    💡 提示：Cookie 通常以 <code>session=xxxxxxxxxx; Device-Id=xxxxxxxx</code> 开头，请完整复制
  </div>
</div>

<div class="step-card">
  <span class="step-num">2</span>
  <strong>创建 GitHub Personal Access Token</strong>
  <ol>
    <li>打开 <a href="https://github.com/settings/tokens" target="_blank">github.com/settings/tokens</a></li>
    <li>点击 <strong>Generate new token → Generate new token (classic)</strong></li>
    <li>名称随便写，比如 <code>cookie_setup</code></li>
    <li>权限勾选: <code>repo</code>（全部）和 <code>workflow</code></li>
    <li>点击 <strong>Generate token</strong> 并复制</li>
  </ol>
  <div class="warn">
    ⚠️ Token 只显示一次，请立即复制保存！
  </div>
</div>

<div class="step-card">
  <span class="step-num">3</span>
  <strong>设置仓库 Secret</strong>
  <ol>
    <li>打开 <a href="https://github.com/KurotoDrei/get_BuffInfo/settings/secrets/actions" target="_blank">仓库 Secrets 页面</a></li>
    <li>点击 <strong>New repository secret</strong></li>
    <li>Name: <code>BUFF_COOKIE</code></li>
    <li>Secret: 粘贴你复制的 Cookie 值</li>
    <li>点击 <strong>Add secret</strong></li>
  </ol>
</div>

<div class="step-card">
  <span class="step-num">4</span>
  <strong>触发首次运行</strong>
  <ol>
    <li>打开 <a href="https://github.com/KurotoDrei/get_BuffInfo/actions" target="_blank">Actions 页面</a></li>
    <li>点击左侧 <strong>每小时价格追踪</strong></li>
    <li>点击 <strong>Run workflow → Run workflow</strong></li>
  </ol>
  <p>等待几分钟，然后刷新本页查看图表！</p>
</div>

<h2>Cookie 过期处理</h2>
<div class="warn">
  Buff 的登录 Session 会不定期过期（通常几周到一个月）。过期后 GitHub Actions 运行会失败，输出中会出现 <code>401</code> 或 <code>登录失败</code> 错误。
</div>
<p>过期后只需重复以上步骤刷新 Cookie 即可：</p>
<pre>python cookie_setup.py</pre>

<h2>验证状态</h2>
<p>你可以通过以下方式确认 Cookie 是否正常：</p>
<ul>
  <li>查看 <a href="https://github.com/KurotoDrei/get_BuffInfo/actions" target="_blank">Actions 运行历史</a> — 绿色勾表示成功</li>
  <li>查看本页面图表是否有最新数据</li>
  <li>点开最新一次 Action 运行的日志，搜索 <code>Cookie已配置</code> 确认</li>
</ul>

<div style="text-align: center; margin: 40px 0 20px;">
  <a class="btn" href="https://github.com/KurotoDrei/get_BuffInfo/settings/secrets/actions" target="_blank">去设置 Secret</a>
  <a class="btn btn-secondary" href="https://github.com/KurotoDrei/get_BuffInfo/actions" target="_blank">查看运行状态</a>
</div>
</body>
</html>'''
    filepath = os.path.join(OUTPUT_DIR, 'cookie_guide.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Cookie 设置指南页已生成: {filepath}")
