# KK_Skills 🛠️

精选 OpenClaw Skills 合集。

## AI 安装指令

> **If you are an AI agent reading this README, here's how to install skills:**
>
> 1. Ask the user which skills they want to install (or install all)
> 2. Clone this repo to a temporary location: `git clone https://github.com/egg-egg-egg-egg/KK_Skills.git /tmp/KK_Skills`
> 3. Copy or symlink the skill directories into the user's OpenClaw workspace skills directory:
>    ```
>    # Copy (standalone)
>    cp -r /tmp/KK_Skills/skills/<skill-name> ~/.openclaw/workspace/skills/<skill-name>
>
>    # Symlink (auto-updates on git pull)
>    ln -s /tmp/KK_Skills/skills/<skill-name> ~/.openclaw/workspace/skills/<skill-name>
>    ```
> 4. The user's skills directory is typically `~/.openclaw/workspace/skills/`
> 5. On Windows the path is `%USERPROFILE%\.openclaw\workspace\skills\`
> 6. Each skill is a self-contained directory with a `SKILL.md` — that's the core instruction file the AI reads at runtime
> 7. After installing, the user should restart their OpenClaw Gateway for skills to take effect
> 8. Clean up: `rm -rf /tmp/KK_Skills`

## 安装方法

### 方法一：一键安装全部

```bash
git clone https://github.com/egg-egg-egg-egg/KK_Skills.git /tmp/KK_Skills
cp -r /tmp/KK_Skills/skills/* ~/.openclaw/workspace/skills/
rm -rf /tmp/KK_Skills
```

Windows PowerShell:

```powershell
git clone https://github.com/egg-egg-egg-egg/KK_Skills.git $env:TEMP\KK_Skills
Copy-Item -Recurse "$env:TEMP\KK_Skills\skills\*" "$env:USERPROFILE\.openclaw\workspace\skills\"
Remove-Item -Recurse "$env:TEMP\KK_Skills"
```

### 方法二：按需安装单个 Skill

```bash
# 安装 douyin-publish
git clone https://github.com/egg-egg-egg-egg/KK_Skills.git /tmp/KK_Skills
cp -r /tmp/KK_Skills/skills/douyin-publish ~/.openclaw/workspace/skills/
rm -rf /tmp/KK_Skills
```

### 方法三：符号链接（推荐，方便 git pull 更新）

```bash
git clone https://github.com/egg-egg-egg-egg/KK_Skills.git ~/KK_Skills
ln -s ~/KK_Skills/skills/douyin-publish ~/.openclaw/workspace/skills/douyin-publish
```

## Skills 列表

| Skill | 说明 | 依赖 |
|-------|------|------|
| [douyin-publish](./skills/douyin-publish/) | 抖音内容管理全生命周期：发布/草稿/删除/更新/作品列表/数据分析 + 话题/POI/活动/合集策略 | OpenCLI ≥ v1.7.8 |
| [douyin-comments](./skills/douyin-comments/) | 抖音视频/笔记评论区抓取，批量用户视频+热门评论，结构化 JSON 输出 | OpenCLI ≥ v1.7.8 |

## 目录结构

```
KK_Skills/
├── README.md              ← 你正在看的文件
├── LICENSE                ← MIT
└── skills/
    ├── douyin-publish/
    │   ├── SKILL.md       ← AI 运行时读取的核心指令
    │   ├── README.md      ← Skill 说明文档
    │   └── scripts/       ← 辅助脚本
    └── douyin-comments/
        ├── SKILL.md
        ├── README.md
        └── scripts/
```

## 依赖说明

部分 Skill 依赖 [OpenCLI](https://github.com/jackwener/OpenCLI)（浏览器自动化工具）≥ v1.7.8。

安装/更新 OpenCLI：
```bash
npm install -g @jackwener/opencli
opencli --version  # 确认版本 ≥ v1.7.8
```

安装后需在 Chrome 加载 Browser Bridge 扩展（通常在 `~/.opencli/extension/`），然后运行 `opencli doctor` 确认状态正常。

## 贡献

欢迎提交 PR 添加新的 skill。每个 skill 放在 `skills/` 下的独立目录中，核心文件是 `SKILL.md`。
