# douyin-publish

抖音内容发布技能。支持视频定时发布（OpenCLI 内置命令）和文章/图文发布（浏览器自动化）。

## 功能

- **视频发布**：通过 `opencli douyin publish` 命令一键发布，支持定时发布、封面设置、话题标签、可见性控制
- **文章发布**：通过浏览器自动化操作创作者中心，完成长文发布
- **图文发布**：通过浏览器自动化操作创作者中心，完成图片+文字发布

## 快速开始

### 前置条件

1. OpenCLI 已安装并运行（`opencli doctor` 全部通过）
2. Chrome 浏览器已安装，Browser Bridge 扩展已启用
3. 抖音账号已登录

### 安装

```bash
# Windows
xcopy /E /I "douyin-publish" "%USERPROFILE%\.qclaw\skills\douyin-publish"

# macOS/Linux
cp -r douyin-publish ~/.qclaw/skills/
```

### 发布视频（推荐）

```bash
# 立即发布
opencli douyin publish "C:\Videos\my_video.mp4" \
  --title "AI不会替代人工" \
  --caption "你觉得AI会抢走你的工作吗？ #AI #职场"

# 定时发布（明天下午3点）
opencli douyin publish "C:\Videos\my_video.mp4" \
  --title "定时发布测试" \
  --schedule "2026-04-27T15:00:00+08:00"
```

### 发布文章

```bash
# 导航到创作者中心
opencli browser open "https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new"

# 然后按照 SKILL.md 中的步骤填写内容
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能主文档，包含完整使用说明和详细参数 |
| `scripts/check_env.py` | 环境检查脚本 |
| `README.md` | 本文件 |

## 发布方式对比

| 内容类型 | 方式 | 稳定性 | 复杂度 |
|----------|------|--------|--------|
| 视频 | `opencli douyin publish` | ⭐⭐⭐ 高 | 低，参数化配置 |
| 文章 | 浏览器自动化 | ⭐⭐ 中 | 中，需操作 DOM |
| 图文 | 浏览器自动化 | ⭐⭐ 中 | 中，需操作 DOM |

## 依赖

- [OpenCLI](https://github.com/jackwener/OpenCLI) ≥ v1.7.7
- Python 3.7+
- Chrome 浏览器 + Browser Bridge 扩展
- 抖音账号（已登录）

## License

MIT
