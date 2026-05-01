# douyin-publish

抖音内容管理全生命周期技能。

## 功能

### 内容生命周期管理
- **视频发布** — `opencli douyin publish` 定时发布，支持封面、话题、POI、活动、热点词
- **草稿管理** — `opencli douyin draft` 保存草稿，`drafts` 查看列表
- **作品管理** — `videos` 列表、`update` 修改、`delete` 删除
- **数据分析** — `stats` 作品数据、`profile` 账号信息

### 发布策略增强
- **话题** — `hashtag hot` 热点词、`hashtag search` 关键词搜索、`hashtag suggest` AI推荐
- **POI** — `location` 地理位置搜索
- **活动** — `activities` 官方活动列表
- **合集** — `collections` 合集管理

### 文章/图文发布
- 通过浏览器自动化（OpenCLI state/click/type）操作创作者中心

## 快速开始

```bash
# 前置检查
opencli doctor

# 发布视频（2小时后）
opencli douyin publish "C:\Videos\demo.mp4" `
  --title "测试视频" `
  --schedule "2026-05-03T02:00:00+08:00" `
  --caption "第一条测试 #测试"
```

## 安装

```bash
# Windows
xcopy /E /I "douyin-publish" "%USERPROFILE%\.qclaw\skills\douyin-publish"

# macOS/Linux
cp -r douyin-publish ~/.qclaw/skills/
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能主文档，含完整命令参考和工作流 |
| `scripts/check_env.py` | 环境检查脚本 |
| `README.md` | 本文件 |

## 依赖

- [OpenCLI](https://github.com/jackwener/OpenCLI) ≥ v1.7.8
- Chrome + Browser Bridge 扩展 + Daemon
- 抖音已登录
- Python 3.7+

## License

MIT
