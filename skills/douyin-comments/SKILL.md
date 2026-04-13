---
name: douyin-comments
description: |
  抖音笔记评论区抓取技能。通过 OpenCLI 控制浏览器，抓取抖音笔记/视频的评论区内容，结构化输出并自动保存为 JSON 文件。
  当用户要求"抓抖音评论"、"获取评论"、"爬取评论区"、"导出评论数据"等意图时触发此 skill。
  依赖 OpenCLI（Browser Bridge 扩展 + Daemon）实现浏览器自动化。
---

# 抖音评论抓取

## 概述

通过 OpenCLI 的浏览器控制能力，自动化抓取抖音笔记/视频页面的评论区数据，提取评论内容、用户名、点赞数、时间等信息，结构化保存为 JSON 文件。

## 前置条件

### 1. OpenCLI 已安装并运行

```bash
opencli doctor
```

必须全部通过：
- ✅ Daemon: OK
- ✅ Extension: Connected
- ✅ Connectivity: OK

### 2. 抖音已登录

浏览器中抖音账号必须已登录。未登录状态下评论内容可能受限。

## 抓取流程

### Step 1: 打开目标页面

支持两种 URL 格式：

```bash
# 笔记（图文）
opencli browser open "https://www.douyin.com/note/<笔记ID>"

# 视频
opencli browser open "https://www.douyin.com/video/<视频ID>"
```

等待 3-5 秒页面加载完成。

### Step 2: 获取页面状态

```bash
opencli state
```

从 state 输出中提取以下信息：

**作品基本信息：**
- 标题/正文内容
- 作者昵称
- 点赞数、评论数、分享数

**评论区数据：**
- 评论区通常在页面右侧面板或弹窗中
- 每条评论包含：用户名、评论内容、点赞数、回复数、发布时间

### Step 3: 滚动加载更多评论

评论区是懒加载的，需要滚动来加载更多评论。

1. 找到评论区容器的元素编号
2. 向下滚动评论区：

```bash
opencli scroll <评论区元素编号> down
```

3. 等待 2-3 秒让新评论加载
4. 再次 `opencli state` 获取新加载的评论
5. 重复直到评论不再新增（或达到目标数量）

**注意：** 抖音网页版通常一次显示约 20-30 条评论，需要多次滚动才能获取更多。

### Step 4: 解析评论数据

从 state 输出中，按以下结构解析每条评论：

```
- 用户名
- 评论内容
- 点赞数
- 回复数
- 发布时间
```

评论区 DOM 中，评论通常包含以下模式：
- 用户名通常在评论块的顶部
- 评论正文紧随用户名
- 点赞数通常有"赞"相关标识
- 回复数如有会标注"N条回复"

### Step 5: 构建结构化数据

将解析出的评论整理为以下 JSON 结构：

```json
{
  "url": "https://www.douyin.com/note/7620109115684354021",
  "title": "文章标题或正文摘要",
  "author": "作者昵称",
  "stats": {
    "likes": 11000,
    "comments": 110,
    "shares": 6
  },
  "comments": [
    {
      "user": "用户名",
      "content": "评论正文内容",
      "likes": 123,
      "replies": 5,
      "time": "3小时前"
    },
    {
      "user": "另一个用户",
      "content": "另一条评论",
      "likes": 45,
      "replies": 0,
      "time": "昨天"
    }
  ],
  "total_comments": 30,
  "scraped_at": "2026-04-14T03:30:00+08:00"
}
```

### Step 6: 保存为 JSON 文件

使用 Python 将结构化数据保存为 JSON 文件：

```bash
python scripts/save_comments.py --data '<JSON字符串>' --output '<保存路径>'
```

**默认保存路径：** 当前工作目录下，文件名格式 `douyin_comments_<笔记ID>_<时间戳>.json`

例如：`douyin_comments_7620109115684354021_20260414_033000.json`

### Step 7: 汇报结果

抓取完成后，向用户汇报：

1. 作品基本信息（标题、作者、互动数据）
2. 抓取到的评论总数
3. 保存的 JSON 文件路径
4. 如有评论趋势或亮点，简要总结

## 技巧与最佳实践

### 提高评论覆盖率

- 抖音网页版评论区一次约加载 20-30 条
- 建议至少滚动 3-5 次获取代表性样本
- 如果评论数超过 100，可询问用户是否需要全部抓取（会比较耗时）

### 处理评论区的子回复

部分评论有子回复（楼中楼），默认只抓取一级评论。如需抓取子回复：
1. 找到"N条回复"元素
2. 点击展开
3. 重新获取 state 解析子评论

### 评论排序

抖音评论区默认按热度排序。如需按时间排序：
1. 找到评论区排序切换按钮
2. 点击切换到"按时间排序"

### 去重

多次 state 获取的评论可能有重叠，需按评论内容或用户名+时间进行去重。

## ⚠️ 关键注意事项

### 元素编号会变

每次执行 `opencli state` 后，所有元素的编号会重新分配。**必须先 state 获取最新编号，再执行操作。**

### 页面可能跳转到 about:blank

如果页面变为 about:blank，重新导航即可。

### Windows PowerShell 兼容

```powershell
# ❌ 错误
opencli scroll 123 && opencli state

# ✅ 正确
opencli scroll 123; opencli state
```

### 网络代理

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 评论区不加载 | 检查是否已登录，尝试刷新页面 |
| 滚动后没有新评论 | 可能已到底部，或页面加载超时 |
| 评论内容不完整 | 等待更长时间让懒加载完成 |
| 保存 JSON 失败 | 检查文件路径权限，JSON 格式是否正确 |

## 依赖

- **OpenCLI** ≥ v1.7.3 — 核心浏览器控制工具
- **Browser Bridge Chrome 扩展** — OpenCLI 的浏览器桥接
- **Chrome 浏览器** — 已安装并保持打开
- **抖音账号** — 已登录状态
- **Python 3** — 用于保存 JSON 文件
