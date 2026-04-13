# douyin-publish 🎵

抖音文章/图文自动发布 Skill，基于 [OpenCLI](https://github.com/jackwener/OpenCLI) 浏览器自动化。

## 功能

- ✅ 发布抖音文章（长文，最多 8000 字）
- ✅ 发布抖音图文（图片+文字，最多 35 张）
- ✅ AI 自动配图 / 自定义头图
- ✅ 封面设置
- ✅ 话题标签（最多 5 个）
- ✅ 发布权限与定时发布

## 前置条件

1. [OpenCLI](https://github.com/jackwener/OpenCLI) ≥ v1.7.3 已安装
2. Browser Bridge Chrome 扩展已加载
3. Chrome 浏览器中抖音已登录

## 安装

将此 skill 目录放入 OpenClaw skills 目录：

\\\ash
# 方式 1: 复制到 skills 目录
cp -r douyin-publish ~/.openclaw/workspace/skills/

# 方式 2: 符号链接
ln -s C:\Users\Coder\.qclaw\workspace-agent-ca7a63c8/douyin-publish ~/.openclaw/workspace/skills/douyin-publish
\\\

重启 Gateway 使 skill 生效。

## 使用

在 OpenClaw 中说：

> 帮我发一篇抖音文章，标题是XXX，内容是XXX

AI 会自动读取此 skill 的指引，通过 OpenCLI 控制浏览器完成发布全流程。

## 流程概览

1. 检查 OpenCLI 连通性（opencli doctor）
2. 导航到抖音创作者中心
3. 填写标题（≤30字）、摘要（≤30字）、正文（≤8000字）
4. 可选：设置头图/AI配图、封面、话题、配乐
5. 点击发布

详细流程见 [SKILL.md](./SKILL.md)。

## 注意事项

- 元素编号每次 state 后会变，操作前必须重新获取
- Windows PowerShell 不支持 \&&\，用 \;\ 代替
- contenteditable 元素需先 click 聚焦再 type 输入

## License

MIT