---
name: douyin-publish
description: |
  抖音文章/图文发布技能。通过 OpenCLI 控制浏览器，自动化完成抖音创作者中心的文章发布流程。
  当用户要求发抖音、发布文章到抖音、抖音发文、写抖音文章等意图时触发此 skill。
  依赖 OpenCLI（Browser Bridge 扩展 + Daemon）实现浏览器自动化。
---

# 抖音文章发布

## 概述

通过 OpenCLI 的浏览器控制能力，自动化操作抖音创作者中心，完成文章发布全流程。
支持：发布文章（长文）、发布图文（图片+文字）。

## 前置条件

### 1. OpenCLI 已安装并运行

`ash
# 检查 OpenCLI 状态
opencli doctor
`

必须全部通过：
- ✅ Daemon: OK
- ✅ Extension: Connected (Browser Bridge Chrome 扩展已加载)
- ✅ Connectivity: OK

如果 Extension 未连接，需要先在 Chrome 加载 Browser Bridge 扩展（通常在 ~/.opencli/extension/ 目录下）。

### 2. 抖音已登录

浏览器中抖音账号必须已登录。可通过以下方式确认：

`ash
opencli browser open https://www.douyin.com
opencli state
`

页面右上角应显示用户头像而非登录按钮。

## 发布文章流程

### Step 1: 导航到创作者中心

`ash
opencli browser open https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new
`

等待 3-5 秒页面加载。

### Step 2: 获取页面状态

`ash
opencli state
`

确认页面包含以下元素：
- 标题输入框（contenteditable，placeholder 提示请输入文章标题）
- 摘要输入框
- 正文编辑区（contenteditable）
- 文章头图区域
- 封面设置区域
- 话题添加
- 发布按钮

### Step 3: 填写标题

**约束：标题最多 30 字。**

1. 从 state 输出中找到标题输入框的元素编号
2. 点击聚焦：

`ash
opencli click <标题元素编号>
`

3. 清空已有内容（如有）并输入：

`ash
opencli type <标题元素编号> 你的标题文字
`

### Step 4: 填写摘要

**约束：摘要最多 30 字。**

同理，找到摘要输入框元素编号，点击聚焦后输入。

### Step 5: 填写正文

**约束：正文最多 8000 字。**

1. 找到正文编辑区的 contenteditable 元素编号
2. 点击聚焦：

`ash
opencli click <正文元素编号>
`

3. 等待 1 秒确保焦点到位
4. 输入正文内容：

`ash
opencli type <正文元素编号> 正文内容...
`

**注意：** 正文内容较长时，分多次输入可能更稳定。

### Step 6: 设置头图（可选）

1. 找到AI配图按钮元素编号
2. 点击后等待 AI 生成头图（约 3-5 秒）
3. 如需换图，点击AI换图

也可以上传本地图片：
1. 找到头图上传区域
2. 使用文件上传操作

### Step 7: 设置封面（可选但有推荐）

1. 可点击同步头图为封面将头图同步为封面
2. 或上传自定义封面图

**注意：** 实测文章类型即使不设置封面也能发布成功。

### Step 8: 添加话题（可选）

**约束：最多 5 个话题。**

1. 找到话题添加区域
2. 输入话题关键词
3. 从下拉建议中选择匹配话题

### Step 9: 发布设置

默认为公开 + 立即发布，如需修改：
- 谁可以看：公开 / 好友可见 / 仅自己可见
- 发布时间：立即发布 / 定时发布

### Step 10: 点击发布

1. 找到发布按钮元素编号
2. 点击发布：

`ash
opencli click <发布按钮编号>
`

3. 等待 3 秒确认发布结果
4. 成功后页面会跳转到作品管理页，弹出审核通知

### Step 11: 关闭审核弹窗（可选）

如需继续操作，找到弹窗关闭按钮并点击。

## 发布图文流程

图文走不同的入口：

`ash
opencli browser open https://creator.douyin.com/creator-micro/content/upload?enter_from=dou_web
`

图文约束：
- 格式：jpg/jpeg/png/webp（不支持 gif）
- 单张 ≤ 50MB
- 最多 35 张
- 宽高比推荐 3:4 或 4:3

## ⚠️ 关键注意事项

### 元素编号会变

每次执行 opencli state 后，所有元素的编号会重新分配。**必须先 state 获取最新编号，再执行操作。** 不要复用旧的元素编号。

### 页面可能跳转到 about:blank

如果页面变为 about:blank，重新导航即可：

`ash
opencli browser open https://creator.douyin.com/creator-micro/content/post/article?enter_from=publish_page&media_type=article&type=new
`

### contenteditable 输入

标题、摘要、正文都是 contenteditable 元素，操作模式：
1. 先 click 聚焦
2. 等待 1 秒
3. 再 type 输入内容

如果 type 失败，重新 click 聚焦再试。

### Windows PowerShell 兼容

Windows PowerShell 不支持 && 链式命令，需分开执行或使用 ;：

`powershell
# ❌ 错误
opencli click 123 && opencli type 123 text

# ✅ 正确
opencli click 123; opencli type 123 text
`

### 网络代理

如果 GitHub 等海外网站访问不畅，需配置代理：

`powershell
=http://127.0.0.1:7890
`

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| opencli doctor 显示 Extension 未连接 | 检查 Chrome 是否加载了 Browser Bridge 扩展 |
| 页面未登录 | 先在浏览器手动登录抖音 |
| 元素编号找不到 | 重新执行 opencli state |
| type 输入失败 | 先 click 聚焦，等 1 秒再 type |
| 页面变成 about:blank | 重新 opencli browser open 导航 |
| 发布按钮点击无反应 | 检查必填项是否完成（标题、正文） |

## 依赖

- **OpenCLI** ≥ v1.7.3 — 核心浏览器控制工具
- **Browser Bridge Chrome 扩展** — OpenCLI 的浏览器桥接
- **Chrome 浏览器** — 已安装并保持打开
- **抖音账号** — 已登录状态