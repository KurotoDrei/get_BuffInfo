# ADR-0001: 使用 iframe + 侧边栏的多页面仪表盘架构

## 状态

已采纳

## 背景

需要为多个独立页面（两张折线图、数据表格、Cookie 设置指南）提供统一的导航体验。这些页面由不同的生成器生成：
- 折线图页面由 Plotly 的 `fig.write_html()` 生成（自动包含完整 HTML 结构）
- 数据表格页面由 `dashboard_generator.py` 生成
- Cookie 设置指南页面同样由 `dashboard_generator.py` 生成

## 决策

采用 **iframe 嵌入 + 侧边栏** 架构：
- `index.html` 作为唯一入口，包含左侧固定侧边栏导航
- 右侧内容区域使用 `<iframe>` 嵌入其他页面
- 侧边栏点击切换 iframe 的 `src` 属性

## 备选方案

### A. 每个页面独立包含侧边栏
每个 HTML 文件都包含完整的侧边栏 HTML 代码。

- **优点**: URL 独立，可单独访问/分享任意页面
- **缺点**: 侧边栏修改需要重新生成所有页面

### B. iframe 主框架（选中的方案）
一个 index.html 包含侧边栏，内容区用 iframe 嵌入。

- **优点**:
  - 侧边栏只需维护一份代码
  - 切换页面无需重新加载侧边栏
  - 与其他生成器的输出（Plotly HTML）天然兼容
- **缺点**:
  - 子页面 URL 无法被直接分享
  - iframe 高度需要手动管理（当前使用 `flex: 1` + `100vh` 解决）

### C. 纯前端单页应用（SPA）
使用前端框架或原生 JS 实现客户端路由。

- **优点**: 最灵活，无 iframe 限制
- **缺点**: 需要修改所有页面的生成方式，与 Plotly HTML 兼容性差

## 影响

- 子页面（折线图、数据表格）必须是完整 HTML 文档，不需要适配侧边栏
- 所有页面可以通过 `https://kurotodrei.github.io/get_BuffInfo/index.html` 访问
- 侧边栏导航和 iframe 页面之间的通信有限（当前不需要）
- 日后如需支持独立页面，可以回退到方案 A

## （非）适用范围

决定适用于所有由 `dashboard_generator.py` 和 `chart_generator.py` 生成的页面。
