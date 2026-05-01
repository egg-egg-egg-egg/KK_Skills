---
name: douyin-publish
description: |
  抖音内容管理全生命周期技能。覆盖视频发布/定时发布/草稿/删除/更新/作品列表/账号信息/数据分析，
  以及话题搜索、地理位置、官方活动、合集管理等辅助策略工具。
  当用户要求发抖音、发布视频、定时发布、管理抖音作品、抖音发文、写抖音文章等意图时触发。
  依赖 OpenCLI（≥v1.7.8，含 Browser Bridge 扩展 + Daemon）。
---

# 抖音内容管理

## 概述

覆盖抖音创作者内容全生命周期：

| 阶段 | 命令 | 说明 |
|------|------|------|
| **发布** | `publish` | 定时发布视频（2h~14天后） |
| **草稿** | `draft` / `drafts` | 保存草稿 / 查看草稿列表 |
| **管理** | `videos` / `update` / `delete` | 作品列表 / 修改信息 / 删除 |
| **分析** | `stats` / `profile` | 作品数据 / 账号信息 |
| **策略** | `hashtag` / `location` / `activities` / `collections` | 话题 / POI / 活动 / 合集 |
| **文章** | 浏览器自动化 | 长文/图文发布（见 [文章发布详情](#文章图文发布浏览器自动化)） |

> 💡 每个命令的完整参数可通过 `opencli douyin <命令> -h` 查询。

## 前置条件

```bash
opencli doctor
```

必须全部通过：Daemon OK + Extension Connected + Connectivity OK。

---

## 一、视频发布

```bash
opencli douyin publish "<视频路径>" --title "标题" --schedule "<时间>"
```

**必填参数：**
- `video` — 本地视频文件路径
- `--title` — 标题，≤30字
- `--schedule` — 定时发布时间，ISO8601（如 `2026-05-03T15:00:00+08:00`）或 Unix 秒，范围 2h~14天后

**常用可选参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--caption` | 正文，≤1000字，支持 `#话题` | `""` |
| `--cover` | 封面图片路径（不提供则自动截帧） | `""` |
| `--visibility` | `public` / `friends` / `private` | `public` |
| `--allow_download` | 允许下载 | `false` |
| `--sync_toutiao` | 同步发布到头条 | `false` |
| `--collection` | 合集 ID | `""` |
| `--activity` | 活动 ID | `""` |
| `--poi_id` | 地理位置 ID | `""` |
| `--poi_name` | 地理位置名称 | `""` |
| `--hotspot` | 关联热点词 | `""` |
| `--no_safety_check` | 跳过内容安全检测 | `false` |

### 快速示例

```bash
# 立即发布（设为2小时后）
$time = (Get-Date).AddHours(2).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
opencli douyin publish "C:\Videos\my_video.mp4" `
  --title "AI不会替代人工" `
  --schedule $time `
  --caption "你觉得呢？评论区聊聊 #AI #职场"

# 明天下午3点发布
opencli douyin publish "C:\Videos\idea.mp4" `
  --title "一个有趣的想法" `
  --schedule "2026-05-03T15:00:00+08:00" `
  --visibility public

# 全参数优化发布（带话题+POI+活动+热点）
opencli douyin publish "C:\Videos\travel.mp4" `
  --title "五一故宫游记" `
  --schedule "2026-05-03T15:00:00+08:00" `
  --caption "假期第一站 #故宫 #五一旅行" `
  --cover "C:\Images\cover.png" `
  --poi_id "12345" `
  --poi_name "故宫博物院" `
  --activity "7634441995797959690" `
  --hotspot "都来这里过五一" `
  --sync_toutiao true
```

### 输出

```
status    aweme_id              url                                    publish_time
────────  ────────────────────  ─────────────────────────────────────  ────────────
success   7633534116155149620   https://www.douyin.com/video/76335...  2026-05-03T15:00:00+08:00
```

---

## 二、草稿管理

### 保存草稿

```bash
opencli douyin draft "<视频路径>" --title "标题"
```

参数与 `publish` 相同（但不含 schedule）。返回 `draft_id`。

**示例：**

```bash
opencli douyin draft "C:\Videos\draft_video.mp4" `
  --title "草稿测试" `
  --caption "这是一条待发布的草稿 #测试" `
  --format json
```

### 查看草稿列表

```bash
opencli douyin drafts --limit 20 --format json
```

返回字段：`aweme_id`、`title`、`create_time`。

---

## 三、作品管理

### 作品列表

```bash
opencli douyin videos --limit 20 --page 1 --status all --format json
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--limit` | 每页数量 | 20 |
| `--page` | 页码 | 1 |
| `--status` | `all` / `published` / `reviewing` / `scheduled` | all |

返回字段：`aweme_id`、`title`、`status`、`play_count`、`digg_count`、`create_time`。

### 更新作品信息

```bash
opencli douyin update <aweme_id> --reschedule "<新时间>" --caption "新正文"
```

⚠️ 需同时传 `--reschedule` 和 `--caption` 至少一个。单独传 `--caption` 可能报"参数不合法"。

### 删除作品

```bash
opencli douyin delete <aweme_id>
```

⚠️ **不可逆操作。** 执行前必须向用户确认 aweme_id 和作品标题。返回 `status: "success"`。

---

## 四、账号与数据

### 账号信息

```bash
opencli douyin profile --format json
```

返回：`uid`（即 sec_uid）、`nickname`、`follower_count`、`following_count`、`aweme_count`。

### 作品数据

```bash
opencli douyin stats <aweme_id> --format json
```

> ⚠️ 实测偶发 `Douyin API error 4`，重试有效。

---

## 五、发布策略工具

优化视频发布效果时使用的辅助命令。

### 话题管理

```bash
# 热点词（高流量话题）
opencli douyin hashtag hot --limit 10 --format json
# 返回：name, id, view_count

# 关键词搜索
opencli douyin hashtag search --keyword "<关键词>" --limit 10 --format json

# AI 推荐话题（传入封面图）
opencli douyin hashtag suggest --cover "<封面URI>" --limit 10 --format json
```

### 地理位置

```bash
opencli douyin location "<地名>" --limit 20 --format json
# 返回：poi_id, name, address, city
```

### 官方活动

```bash
opencli douyin activities --format json
# 返回：activity_id, title, end_time
```

筛选即将到期的活动（可用于抢占流量窗口）。

### 合集管理

```bash
opencli douyin collections --limit 20 --format json
# 返回：mix_id, name, item_count
```

---

## 六、最优发布流程

将策略工具与发布命令串联，最大化曝光：

```bash
# 1. 找热门话题
opencli douyin hashtag hot --limit 5 --format json

# 2. 找相关活动
opencli douyin activities --format json
# 筛选与视频内容匹配的活动

# 3. 搜索 POI（如涉及地点）
opencli douyin location "故宫" --limit 3 --format json

# 4. 获取合集 ID（如需归类）
opencli douyin collections --format json

# 5. 组装参数发布
opencli douyin publish "C:\Videos\final.mp4" `
  --title "最佳标题" `
  --schedule "2026-05-03T20:00:00+08:00" `
  --caption "正文 #话题1 #话题2" `
  --hotspot "热点词" `
  --activity "<activity_id>" `
  --collection "<mix_id>" `
  --poi_id "<poi_id>" `
  --poi_name "地点名称" `
  --sync_toutiao true
```

---

## 七、文章/图文发布（浏览器自动化）

`opencli douyin publish` 不支持文章/图文类型，此场景用浏览器自动化。

### 发布策略

**默认模式（半自动）：** AI 完成所有内容填写，最后"点击发布"交给用户。

**全自动模式：** 用户明确说"帮我发出去"、"直接发布"时，AI 代为点击发布按钮。

### 文章发布流程

```bash
# 1. 导航
opencli browser open "https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new"

# 2. 等待加载
opencli wait 3s

# 3. 获取元素编号
opencli state

# 4. 填写标题（≤30字）：click → type
opencli click <标题元素编号>
opencli type <标题元素编号> "标题文字"

# 5. 填写摘要（≤30字）
opencli click <摘要元素编号>
opencli type <摘要元素编号> "摘要文字"

# 6. 填写正文（≤8000字）
opencli click <正文元素编号>
opencli wait 1s
opencli type <正文元素编号> "正文内容..."

# 7. 可选：设置头图（点击"AI配图"）、同步封面、添加话题

# 8. 发布
# 半自动：告知用户检查并点击发布
# 全自动：opencli click <发布按钮编号>
```

### 图文发布

```bash
opencli browser open "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web"
# 约束：jpg/jpeg/png/webp，单张≤50MB，最多35张，宽高比推荐 3:4/4:3
```

### ⚠️ 浏览器自动化注意事项

| 事项 | 说明 |
|------|------|
| 元素编号会变 | 每次 `opencli state` 后重新编号，操作前必须重新获取 |
| contenteditable 输入 | 先 `click` 聚焦 → `wait 1s` → `type` |
| 页面跳 about:blank | 重新 `opencli browser open` 导航即可 |
| PowerShell | 用 `;` 代替 `&&` 链式命令 |

### 网络代理

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

---

## 八、故障排除

| 现象 | 原因 | 解决 |
|------|------|------|
| publish 报 schedule 错误 | 时间不在 2h~14d 范围 | 调整 schedule 时间 |
| update "参数不合法" | 仅传 caption 未传 reschedule | 同时传 `--reschedule` 和 `--caption` |
| stats API error 4 | API 偶发错误 | 重试 |
| comments total_scraped:0 | 笔记类型不支持 | 用 `douyin-comments` skill |
| Extension Detached | 浏览器扩展断开 | 刷新页面，确认 Chrome 运行 |
| 视频格式不支持 | 格式不符 | 确保 mp4/webm，≤16G |
| 文章发布按钮无反应 | 必填项未完成 | 确认标题、正文已填写 |

## 已知限制

- **stats / update**：偶发 API 错误，不稳定
- **hashtag search**：偶发 JSON 解析失败，建议优先使用 `hashtag hot`
- **location**：偶发 Extension Detached，重试可恢复
- **文章/图文**：无内置命令，需浏览器自动化

## 相关 Skill

- [douyin-comments](../douyin-comments/SKILL.md) — 评论抓取

## 依赖

- **OpenCLI** ≥ v1.7.8 — 内置 `douyin` 命令集
- **Browser Bridge Chrome 扩展** + **Daemon**
- **Chrome 浏览器** — 已安装并打开
- **抖音账号** — 已登录
