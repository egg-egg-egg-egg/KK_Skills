---
name: douyin-publish
description: |
  抖音内容发布技能。支持视频定时发布（OpenCLI 内置命令）和文章/图文发布（浏览器自动化）。
  当用户要求发抖音、发布视频到抖音、抖音发文、写抖音文章、定时发布等意图时触发此 skill。
  依赖 OpenCLI（≥v1.7.7，含 Browser Bridge 扩展 + Daemon）。
---

# 抖音内容发布

## 概述

根据内容类型选择最优发布方式：

| 内容类型 | 推荐方式 | 说明 |
|----------|----------|------|
| **视频** | `opencli douyin publish` 命令 | 参数化配置，稳定可靠，支持定时发布 |
| **文章/图文** | 浏览器自动化（OpenCLI state/click/type） | 需操作创作者中心页面，详见 [文章发布详情](#文章发布详情) |

## 前置条件

```bash
opencli doctor
```

必须全部通过：
- ✅ Daemon: OK
- ✅ Extension: Connected
- ✅ Connectivity: OK

## 一、视频发布（推荐方式）

### 快速发布

```bash
opencli douyin publish "<视频文件路径>" --title "标题" --caption "正文内容 #话题"
```

**必填参数：**
- `video` — 视频文件路径（本地文件）
- `--title` — 标题，≤30字

**常用可选参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--caption` | 正文内容，≤1000字，支持 `#话题` | `""` |
| `--cover` | 封面图片路径（不提供则自动截帧） | `""` |
| `--visibility` | 可见性：`public`/`friends`/`private` | `public` |
| `--schedule` | 定时发布时间（ISO8601 或 Unix 秒，2h~14天后） | 立即发布 |
| `--allow_download` | 允许下载：`true`/`false` | `false` |
| `--sync_toutiao` | 同步发布到头条：`true`/`false` | `false` |

### 完整参数查询

如需查看全部参数和高级用法：

```bash
opencli douyin publish -h
```

### 发布示例

**立即发布：**

```bash
opencli douyin publish "C:\Videos\my_video.mp4" \
  --title "AI不会替代人工，反而让普通人快速掌握技能" \
  --caption "你觉得AI会抢走你的工作吗？评论区聊聊 #AI #职场 #技能提升" \
  --visibility public
```

**定时发布（明天下午3点）：**

```bash
opencli douyin publish "C:\Videos\my_video.mp4" \
  --title "定时发布测试" \
  --schedule "2026-04-27T15:00:00+08:00" \
  --visibility public
```

**带封面+话题+禁止下载：**

```bash
opencli douyin publish "C:\Videos\my_video.mp4" \
  --title "白银涨价了，套利机会分析" \
  --caption "最近白银涨了不少，分享一个套利思路 #白银 #投资 #套利" \
  --cover "C:\Images\cover.png" \
  --allow_download false \
  --visibility public
```

### 输出结果

成功发布后返回：

```
status    aweme_id              url                                    publish_time
────────  ────────────────────  ─────────────────────────────────────  ────────────
success   7620109115684354021   https://www.douyin.com/video/7620...   2026-04-26T09:30:00+08:00
```

JSON 格式：`--format json`

## 二、文章/图文发布（浏览器自动化）

当用户要求发布文章（长文）或图文（图片+文字）时，使用浏览器自动化方案。

### 快速流程

```bash
# 1. 导航到创作者中心文章发布页
opencli browser open "https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new"

# 2. 等待页面加载
opencli wait 3s

# 3. 获取页面元素编号
opencli state

# 4. 依次填写标题、摘要、正文（先 click 聚焦，再 type 输入）
#    标题≤30字，摘要≤30字，正文≤8000字

# 5. 可选：设置头图、封面、话题

# 6. 发布（默认交给用户点击，全自动需用户明确授权）
```

### 详细操作说明

如需完整的元素操作细节、故障排除、注意事项：

**→ 查看 [文章发布详情](#文章发布详情)**

---

## 文章发布详情

### 发布策略

**默认模式：半自动（推荐）**

AI 完成所有内容填写，**最后一步"点击发布"交给用户**。

流程：
1. AI 完成标题、摘要、正文、配图等所有填写
2. AI 告知用户："内容已全部填好，请在浏览器上检查并点击发布按钮"
3. 用户自行检查并点击发布

**全自动模式**

用户明确说"帮我发出去"、"直接发布"、"全自动"时，AI 代为点击发布按钮。

### Step-by-Step 操作

#### Step 1: 导航

```bash
opencli browser open "https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new"
```

#### Step 2: 获取页面状态

```bash
opencli state
```

确认包含：标题输入框、摘要输入框、正文编辑区、发布按钮。

#### Step 3: 填写标题（≤30字）

```bash
opencli click <标题元素编号>
opencli type <标题元素编号> "标题文字"
```

#### Step 4: 填写摘要（≤30字）

```bash
opencli click <摘要元素编号>
opencli type <摘要元素编号> "摘要文字"
```

#### Step 5: 填写正文（≤8000字）

```bash
opencli click <正文元素编号>
opencli type <正文元素编号> "正文内容..."
```

**注意：** contenteditable 元素需先 click 聚焦，等待 1 秒后再 type。

#### Step 6: 设置头图（可选）

找到"AI配图"按钮点击，等待 3-5 秒生成。

#### Step 7: 设置封面（可选）

点击"同步头图为封面"或上传自定义封面。实测文章类型不设置封面也能发布。

#### Step 8: 添加话题（可选，最多5个）

在话题区域输入关键词，从下拉建议中选择。

#### Step 9: 发布

**半自动（默认）：**

内容填好后告知用户检查并手动点击发布。

**全自动（用户明确要求）：**

```bash
opencli click <发布按钮编号>
```

### 发布图文入口

```bash
opencli browser open "https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web"
```

图文约束：jpg/jpeg/png/webp，单张≤50MB，最多35张，宽高比推荐 3:4 或 4:3。

### ⚠️ 关键注意事项

| 问题 | 解决方案 |
|------|----------|
| 元素编号会变 | 每次操作前重新 `opencli state` |
| 页面变成 about:blank | 重新 `opencli browser open` 导航 |
| type 输入失败 | 先 click 聚焦，等 1 秒再 type |
| PowerShell 链式命令 | 用 `;` 代替 `&&` |
| 未登录 | 先在浏览器手动登录抖音 |

### 网络代理

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

## 三、故障排除

| 现象 | 原因 | 解决 |
|------|------|------|
| `opencli douyin publish` 报错 | 视频格式/大小不符，或未到定时发布时间 | 检查视频格式（mp4/webm，≤16G），确认 schedule 在 2h~14d 范围内 |
| Extension 未连接 | Browser Bridge 扩展未加载 | 检查 Chrome 扩展状态 |
| 文章发布按钮无反应 | 必填项未完成 | 确认标题、正文已填写 |
| 定时发布未生效 | 时间不在 2h~14d 范围内 | 调整 schedule 时间 |

## 依赖

- **OpenCLI** ≥ v1.7.7 — 核心工具（内置 `douyin publish`）
- **Browser Bridge Chrome 扩展** — 浏览器自动化所需
- **Chrome 浏览器** — 已安装并保持打开
- **抖音账号** — 已登录状态
- **视频文件** — 发布视频时需提供本地文件
