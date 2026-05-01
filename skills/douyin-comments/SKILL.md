---
name: douyin-comments
description: |
  抖音评论区抓取技能。通过 OpenCLI 内置的 douyin 工具，一键抓取抖音视频/笔记的评论区数据，结构化输出为 JSON 文件。
  当用户要求"抓抖音评论"、"获取评论"、"爬取评论区"、"导出评论数据"等意图时触发此 skill。
  依赖 OpenCLI（≥v1.7.8，含 Browser Bridge 扩展 + Daemon）。
---

# 抖音评论抓取

## 概述

通过 OpenCLI 内置的 `douyin` 工具集，自动化抓取抖音视频/笔记的评论区数据，输出结构化 JSON。

## 前置条件

### 1. OpenCLI 已安装并运行

```bash
opencli doctor
```

必须全部通过：Daemon OK + Extension Connected + Connectivity OK。

### 2. 抖音已登录

浏览器中抖音账号必须已登录。未登录状态下评论内容可能受限。

## 抓取方式

### 方式一：单条视频/笔记评论（推荐）

```bash
opencli douyin comments --url "<视频/笔记URL>" --limit <数量> --format json
```

**参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 视频/笔记链接 (`video/<id>` 或 `note/<id>`) | 必填 |
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
  "video": {
    "title": "视频标题",
    "author": "作者昵称",
    "url": "https://www.douyin.com/video/7633534116155149620"
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
  "scraped_at": "2026-05-02T00:20:00+08:00"
}
```

### 方式二：批量获取用户视频 + 热门评论

```bash
opencli douyin user-videos <sec_uid> --limit <数量> --with_comments true --comment_limit <每条评论数> --format json
```

**参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `sec_uid` | 用户 sec_uid（位置参数） | 必填 |
| `--limit` | 视频数量（最大 20） | 20 |
| `--with_comments` | 是否包含热门评论 | true |
| `--comment_limit` | 每条视频评论数（最大 10） | 10 |

**获取当前登录用户的 sec_uid：**

```bash
opencli douyin profile --format json
# → uid 字段即 sec_uid
```

**示例：**

```bash
opencli douyin user-videos "59332272778" --limit 10 --with_comments true --comment_limit 5 --format json
```

**输出结构：**

```json
[
  {
    "index": 1,
    "aweme_id": "7633534116155149620",
    "title": "AI会让共产主义自动到来？别天真了",
    "duration": 0,
    "digg_count": 89,
    "play_url": "https://...",
    "top_comments": [
      {
        "text": "评论内容",
        "digg_count": 5,
        "nickname": "用户名"
      }
    ]
  }
]
```

## 保存为 JSON 文件

```bash
# 方式一：单条视频评论
opencli douyin comments --url "<URL>" --limit 50 --format json > comments_raw.json
python scripts/save_comments.py --input comments_raw.json --output "./douyin_comments_<id>.json"

# 方式二：批量视频+评论
opencli douyin user-videos "<sec_uid>" --limit 10 --with_comments true --format json > videos_raw.json
python scripts/save_comments.py --input videos_raw.json --output "./douyin_videos_<sec_uid>.json"
```

## 完整工作流

### 场景：抓取单条视频全部评论

```bash
opencli doctor
opencli douyin comments --url "https://www.douyin.com/video/7633534116155149620" --limit 100 --format json > /tmp/comments.json
python scripts/save_comments.py --input /tmp/comments.json
```

### 场景：批量抓取用户近期视频热门评论

```bash
opencli douyin profile --format json
opencli douyin user-videos "59332272778" --limit 20 --with_comments true --comment_limit 10 --format json > /tmp/videos.json
python scripts/save_comments.py --input /tmp/videos.json --output "./user_videos_comments.json"
```

## 最佳实践

- `--scrolls` 默认 30 次 ≈ 200-300 条评论，需要更多时调大
- 建议设置 `--limit` 上限避免耗时过长
- 频繁抓取可能触发验证码，建议间隔 ≥ 5 秒
- 单次抓取不超过 500 条评论

## 已知限制

- **笔记 (note) 类型**：`comments` 命令对部分笔记页面返回 `total_scraped: 0`。可尝试先用 `opencli browser open` 打开笔记页面，手动滚动评论区加载后，再执行抓取命令
- **登录态**：抓取前确保抖音已登录

## 依赖

- **OpenCLI** ≥ v1.7.8 — 内置 `douyin comments` / `douyin user-videos` / `douyin profile`
- **Browser Bridge Chrome 扩展** + **Daemon**
- **Chrome 浏览器** — 已安装并打开
- **抖音账号** — 已登录
- **Python 3** — 用于 save_comments.py
