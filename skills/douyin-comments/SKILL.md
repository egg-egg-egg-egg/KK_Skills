---
name: douyin-comments
description: |
  抖音评论区抓取技能。双轨架构：视频评论用 OpenCLI 内置 douyin 命令，文章/图文评论用 agent-browser 浏览器自动化。
  当用户要求"抓抖音评论"、"获取评论"、"爬取评论区"、"导出评论数据"等意图时触发此 skill。
  依赖 OpenCLI（≥v1.7.8）+ agent-browser + Edge 浏览器登录态。
---

# 抖音评论抓取（双轨架构）

## 架构总览

| 内容类型 | 工具 | 原理 | 需要登录态 |
|----------|------|------|-----------|
| 视频评论 (`/video/`) | `opencli douyin comments` | Browser Bridge 扩展 + 适配器 | 推荐 |
| 视频批量+热门评论 | `opencli douyin user-videos` | Browser Bridge 扩展 + 适配器 | 推荐 |
| 文章/图文评论 (`/article/`) | agent-browser + Edge profile | CDP 驱动真实浏览器，直接 DOM 提取 | **必须** |

## 前置条件

### 1. OpenCLI 已安装并运行

```bash
opencli doctor
```

必须全部通过：Daemon OK + Extension Connected + Connectivity OK。

### 2. Agent-browser 可用

agent-browser 位于 `xbrowser` skill 的 node_modules 中：
```
C:\Users\Coder\.qclaw\tools\xbrowser\node_modules\agent-browser\bin\agent-browser-win32-x64.exe
```

### 3. Edge 浏览器登录态

Edge 可执行文件：`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
User Data 目录：`%LOCALAPPDATA%\Microsoft\Edge\User Data`
Profile：`Default`

---

## 轨一：视频评论（OpenCLI）

### 单条视频评论

```bash
opencli douyin comments --url "<视频URL>" --limit <数量> --format json
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 视频链接 (`video/<id>`) | 必填 |
| `--limit` | 最多抓取条数（0 = 不限） | 0 |
| `--maxExpand` | 展开子回复最大数量 | 10 |
| `--scrolls` | 滚动加载次数 | 30 |
| `--format json` | JSON 格式输出 | table |

**示例：**

```bash
opencli douyin comments --url "https://www.douyin.com/video/7633534116155149620" --limit 50 --format json
```

**输出结构：**

```json
{
  "url": "https://www.douyin.com/video/7633534116155149620",
  "video": { "title": "...", "author": "...", "url": "..." },
  "total_scraped": 50,
  "has_more": true,
  "comments": [{ "user": "...", "content": "...", "time": "3小时前", "likes": 123, "replies": 5 }],
  "scraped_at": "2026-05-02T00:20:00+08:00"
}
```

### 批量视频 + 热门评论

```bash
opencli douyin user-videos <sec_uid> --limit <数量> --with_comments true --comment_limit <每条评论数> --format json
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `sec_uid` | 用户 sec_uid（位置参数） | 必填 |
| `--limit` | 视频数量（最大 20） | 20 |
| `--with_comments` | 是否包含热门评论 | true |
| `--comment_limit` | 每条视频评论数（最大 10） | 10 |

获取当前用户的 sec_uid：
```bash
opencli douyin profile --format json  # → uid 字段即 sec_uid
```

---

## 轨二：文章评论（agent-browser）

### 场景

`opencli douyin comments` 对 `/article/` 路径**不支持**（适配器层面限制，选择器只匹配视频页 DOM）。文章/图文评论必须使用浏览器自动化。

### 步骤 1：启动 agent-browser + Edge

```powershell
$env:AGENT_BROWSER_EXECUTABLE_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$env:AGENT_BROWSER_PROFILE = "$env:LOCALAPPDATA\Microsoft\Edge\User Data"
$env:AGENT_BROWSER_JSON = "1"

# 启动浏览器并导航到文章
& "<agent-browser路径>" open "https://www.douyin.com/article/<article_id>" 2>&1
```

> **关键**：`AGENT_BROWSER_PROFILE` 指向用户真实的 Edge User Data，复用浏览器登录态。未登录只能看到约 13 条评论（103 条中的一小部分）。

### 步骤 2：滚动评论区到底

抖音文章评论区是**懒加载**的，需要反复滚动到外层滚动容器底部才能触发新评论加载。

```powershell
# 重复执行直到 scrollH 不再增长
& "<agent-browser路径>" eval "
  (function(){
    const outer = document.querySelector('.route-scroll-container') || document.querySelector('[class*=route-scroll]');
    outer.scrollTop = outer.scrollHeight;
    return JSON.stringify({scrollH: outer.scrollHeight, scrollTop: outer.scrollTop});
  })();
" 2>&1
```

**滚动容器注意事项：**
- ✅ 外层含 `route-scroll` class 的容器 → 滚动触发懒加载
- ❌ 内层评论区 div（如 `class="IHrj7RhK U9C7HmQ0"`）→ 滚动**不**触发懒加载
- 当 `scrollH` 连续两次执行不再增长时，评论已全部加载

**参考值**：文章 103 条评论，scrollH 从 ~2000 增长到 ~8784 后稳定。

### 步骤 3：一次性批量提取所有评论

```powershell
& "<agent-browser路径>" eval "
  (function(){
    const items = document.querySelectorAll('[data-e2e=comment-item]');
    const result = [];
    items.forEach((el, i) => {
      result.push({i, text: el.innerText});
    });
    return JSON.stringify({total: result.length, items: result});
  })();
" 2>&1
```

**选择器**：`[data-e2e=comment-item]` — 抖音评论区的稳定标识，每个评论项（含作者回复展开）都是独立元素。

`innerText` 会保留换行和层级关系，每次提取的内容格式：
```
用户名
...
评论正文（可能多行）
X天前·省份

点赞数

分享
回复
```

### 步骤 4：关闭浏览器

```powershell
& "<agent-browser路径>" close 2>&1
```

### 步骤 5：格式化输出（Python 后处理）

```python
# 解析 agent-browser 输出的 innerText，正则匹配字段
import re, json

# 推荐正则：
# 用户名: r'^(.+?)$(?=\n...\n.*?·)'
# 时间地点: r'(\d+.*?·..)'
# 点赞数: r'^(\d+)$(?=\n.*分享.*回复)'
```

---

## 最佳实践

### 数据持久化
- **每一步都写文件**，不要在内存中累积数据再用
- 步骤 2 (滚动) 完成后立即把 scrollH 状态记下来
- 步骤 3 (提取) 完成后立即写临时 JSON 文件
- 桌面 .md 文件用 `write_file.py` 写出（qclaw-text-file 规则）

### 采集策略
| 场景 | 推荐策略 | 原因 |
|------|---------|------|
| 少量视频评论 (<100) | `opencli douyin comments` | 零步数消耗，结构化输出 |
| 大量视频评论 (>100) | `opencli douyin comments --scrolls 50` | 调大 scrolls，一次跑完 |
| 文章/图文评论 | agent-browser 三步骤（滚动→提取→关闭） | opencli 不支持 article |
| 批量视频+热门 | `opencli douyin user-videos` | 适合做账号趋势分析 |

### 稳定性
- 视频抓取间隔 ≥ 5 秒避免触发验证码
- agent-browser eval 中避免重复声明变量 → 用 IIFE `(function(){...})()` 包裹
- scrollH 稳定后再提取，不要中途提取
- 关闭浏览器时确认无残留 agent-browser session

---

## 已知限制

| 限制 | 影响 | 缓解方案 |
|------|------|----------|
| `douyin comments` 不支持 `/article/` | 文章评论无法用 opencli | 使用轨二（agent-browser） |
| 部分 `/video/` 返回 `eval_returned_null` | 某些视频的评论页 DOM 结构变化 | 改用 agent-browser 或标记为"采集失败" |
| 未登录仅可见 ~13 条评论 | 数据不完整 | 必须用 Edge 登录态 |
| agent-browser eval 变量名冲突 | `Identifier already declared` | 每次 eval 用唯一变量名或 IIFE |
| 深层子回复未完全展开 | 总评论数 ≠ 采集数 | 标注采集数 vs 显示总数 |

---

## 依赖

| 工具 | 最低版本 | 用途 |
|------|---------|------|
| OpenCLI | ≥ v1.7.8 | 视频评论（轨一） |
| Browser Bridge 扩展 | — | OpenCLI 的 Chrome 连接器 |
| agent-browser | — | 文章评论 DOM 提取（轨二） |
| Edge 浏览器 | — | 复用用户登录态 |
| Python 3 | — | 后处理和格式化 |
