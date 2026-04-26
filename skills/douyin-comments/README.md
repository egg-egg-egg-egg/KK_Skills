# douyin-comments

抖音评论区抓取技能。通过 OpenCLI 内置的 `douyin` 工具集，一键抓取抖音视频/笔记的评论区数据。

## 功能

- **单条视频/笔记评论抓取**：通过 URL 直接抓取指定作品的全部评论
- **批量用户视频+评论**：获取用户近期视频列表及每条视频的热门评论
- **结构化输出**：自动保存为 JSON 文件，包含评论内容、用户名、点赞数、时间等

## 快速开始

### 前置条件

1. OpenCLI 已安装并运行（`opencli doctor` 全部通过）
2. Chrome 浏览器已安装，Browser Bridge 扩展已启用
3. 抖音账号已登录

### 安装

将此 skill 目录复制到 OpenClaw skills 目录：

```bash
# Windows
xcopy /E /I "douyin-comments" "%USERPROFILE%\.qclaw\skills\douyin-comments"

# macOS/Linux
cp -r douyin-comments ~/.qclaw/skills/
```

### 使用示例

**抓取单条视频评论：**

```bash
opencli douyin comments --url "https://www.douyin.com/video/7620109115684354021" --limit 50 --format json > /tmp/comments.json
python scripts/save_comments.py --input /tmp/comments.json
```

**批量抓取用户视频+评论：**

```bash
# 获取 sec_uid
opencli douyin profile --format json

# 批量抓取
opencli douyin user-videos "59332272778" --limit 10 --with_comments true --comment_limit 5 --format json > /tmp/videos.json
python scripts/save_comments.py --input /tmp/videos.json
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能主文档，包含完整使用说明 |
| `scripts/save_comments.py` | JSON 保存脚本，将 opencli 输出保存为结构化文件 |
| `README.md` | 本文件 |

## 输出格式

### 单条评论模式

```json
{
  "url": "https://www.douyin.com/video/7620109115684354021",
  "video": {
    "title": "视频标题",
    "author": "作者昵称"
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

### 批量视频模式

```json
{
  "videos": [
    {
      "aweme_id": "7632538845397093617",
      "title": "视频标题",
      "digg_count": 11,
      "top_comments": [
        {
          "text": "评论内容",
          "digg_count": 0,
          "nickname": "用户名"
        }
      ]
    }
  ],
  "scraped_at": "2026-04-26T09:20:00+08:00"
}
```

## 依赖

- [OpenCLI](https://github.com/jackwener/OpenCLI) ≥ v1.7.7
- Python 3.7+
- Chrome 浏览器 + Browser Bridge 扩展
- 抖音账号（已登录）

## License

MIT
