---
name: douyin-comments
description: |
  抖音评论区抓取技能。通过 OpenCLI 内置的 douyin 工具，一键抓取抖音视频/笔记的评论区数据，结构化输出为 JSON 文件。
  当用户要求"抓抖音评论"、"获取评论"、"爬取评论区"、"导出评论数据"等意图时触发此 skill。
  依赖 OpenCLI（≥v1.7.7，含 Browser Bridge 扩展 + Daemon）实现浏览器自动化。
---

# 抖音评论抓取

## 概述

通过 OpenCLI 内置的 `douyin` 工具集，自动化抓取抖音视频/笔记的评论区数据，提取评论内容、用户名、点赞数等信息，结构化保存为 JSON 文件。

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

## 抓取方式

### 方式一：单条视频/笔记评论（推荐）

直接通过 URL 抓取指定视频/笔记的评论：

```bash
opencli douyin comments --url "<视频/笔记URL>" --limit <数量> --format json
```

**参数说明：**
- `--url`: 视频或笔记链接，支持 `https://www.douyin.com/video/<id>` 或 `https://www.douyin.com/note/<id>`
- `--limit`: 最多抓取多少条评论（默认 0 = 不限）
- `--maxExpand`: 展开子回复的最大数量（默认 10）
- `--scrolls`: 滚动加载次数（默认 30）
- `--format json`: 输出 JSON 格式

**示例：**

```bash
opencli douyin comments --url "https://www.douyin.com/video/7620109115684354021" --limit 50 --format json
```

**输出示例：**

```json
{
  "url": "https://www.douyin.com/video/7620109115684354021",
  "video": {
    "title": "视频标题",
    "author": "作者昵称",
    "url": "https://www.douyin.com/video/7620109115684354021"
  },
  "total_scraped": 50,
  "has_more": true,
  "comments": [
    {
      "user": "用户名",
      "content": "评论内容",
      "time": "3小时前",
      "likes": 123,
      "replies": 5
    }
  ],
  "scraped_at": "2026-04-26T09:20:00+08:00"
}
```

### 方式二：批量获取用户视频 + 热门评论

获取指定用户的视频列表，同时附带每条视频的热门评论：

```bash
opencli douyin user-videos <sec_uid> --limit <数量> --with_comments true --comment_limit <每条视频评论数> --format json
```

**参数说明：**
- `sec_uid`: 用户 sec_uid（可从 `opencli douyin profile` 获取）
- `--limit`: 获取视频数量（最大 20）
- `--with_comments`: 是否包含热门评论（默认 true）
- `--comment_limit`: 每条视频获取多少条评论（最大 10）

**获取当前登录用户的 sec_uid：**

```bash
opencli douyin profile --format json
```

**示例输出：**

```json
[
  {
    "uid": "59332272778",
    "nickname": "刚上课就",
    "follower_count": 75,
    "following_count": 245,
    "aweme_count": 18
  }
]
```

**批量获取视频 + 评论示例：**

```bash
opencli douyin user-videos "59332272778" --limit 10 --with_comments true --comment_limit 5 --format json
```

**输出示例：**

```json
[
  {
    "index": 1,
    "aweme_id": "7632538845397093617",
    "title": "视频标题",
    "duration": 0,
    "digg_count": 11,
    "play_url": "https://...",
    "top_comments": [
      {
        "text": "评论内容",
        "digg_count": 0,
        "nickname": "用户名"
      }
    ]
  }
]
```

## 保存为 JSON 文件

抓取完成后，使用内置脚本保存为 JSON 文件：

```bash
# 方式一：单条视频评论
opencli douyin comments --url "<URL>" --limit 50 --format json > comments_raw.json
python scripts/save_comments.py --input comments_raw.json --output "./douyin_comments_<id>.json"

# 方式二：批量视频+评论
opencli douyin user-videos "<sec_uid>" --limit 10 --with_comments true --format json > videos_raw.json
python scripts/save_comments.py --input videos_raw.json --output "./douyin_videos_<sec_uid>.json"
```

**默认保存路径：** 当前工作目录下，文件名格式 `douyin_comments_<id>_<时间戳>.json`

## 完整工作流示例

### 场景：抓取单条视频的全部评论

```bash
# 1. 确认 OpenCLI 状态
opencli doctor

# 2. 抓取评论
opencli douyin comments --url "https://www.douyin.com/video/7620109115684354021" --limit 100 --format json > /tmp/comments.json

# 3. 保存为结构化文件
python scripts/save_comments.py --input /tmp/comments.json

# 4. 汇报结果
cat douyin_comments_7620109115684354021_*.json | python -m json.tool
```

### 场景：批量抓取用户近期视频的热门评论

```bash
# 1. 获取用户 sec_uid
opencli douyin profile --format json

# 2. 批量抓取视频+评论
opencli douyin user-videos "59332272778" --limit 20 --with_comments true --comment_limit 10 --format json > /tmp/videos.json

# 3. 保存
python scripts/save_comments.py --input /tmp/videos.json --output "./user_videos_comments.json"
```

## 输出字段说明

### 单条评论（comments 模式）

| 字段 | 类型 | 说明 |
|------|------|------|
| user | string | 评论用户昵称 |
| content | string | 评论正文 |
| time | string | 发布时间（相对时间，如"3小时前"） |
| likes | number | 点赞数 |
| replies | number | 回复数 |

### 视频信息（user-videos 模式）

| 字段 | 类型 | 说明 |
|------|------|------|
| aweme_id | string | 视频/笔记 ID |
| title | string | 标题/正文摘要 |
| digg_count | number | 点赞数 |
| play_url | string | 播放地址 |
| top_comments | array | 热门评论列表 |

## 技巧与最佳实践

### 提高评论覆盖率

- `--scrolls` 默认 30 次，约可加载 200-300 条评论
- 如需更多，增加 `--scrolls` 值（如 `--scrolls 100`）
- 评论数过多时建议设置 `--limit` 上限避免耗时过长

### 处理笔记（note）类型

部分笔记页面的评论区 DOM 结构与视频不同，如果 `comments` 命令返回空或报错，可尝试：
1. 先用 `opencli browser open` 打开笔记页面
2. 手动滚动评论区加载内容
3. 再执行 `opencli douyin comments --url <url>`

### 评论排序

默认按热度排序。如需按时间排序，先手动在页面切换排序方式，再执行抓取命令。

## ⚠️ 关键注意事项

### 元素编号会变（仅手动操作时）

如果使用 `opencli browser open` + `opencli state` 手动操作，每次 state 后元素编号会重新分配。**使用内置 `douyin` 命令时无需关心此问题。**

### 网络代理

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

### 抖音反爬

- 频繁抓取可能触发验证码或限流
- 建议抓取间隔 ≥ 5 秒
- 单次抓取评论数建议不超过 500 条

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `total_scraped: 0` | 检查是否已登录；笔记类型可能不支持，尝试视频 URL |
| 评论内容不完整 | 增加 `--scrolls` 值；检查页面是否加载完成 |
| `Extension not connected` | 确认 Browser Bridge 扩展已启用并刷新页面 |
| 返回空数组 | 该视频可能没有评论，或评论区未加载 |

## 依赖

- **OpenCLI** ≥ v1.7.7 — 核心工具（内置 `douyin` 命令）
- **Browser Bridge Chrome 扩展** — OpenCLI 的浏览器桥接
- **Chrome 浏览器** — 已安装并保持打开
- **抖音账号** — 已登录状态
- **Python 3** — 用于保存 JSON 文件
