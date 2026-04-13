# KK_Skills 🛠️

精选 OpenClaw Skills 合集。

## Skills

| Skill | 说明 | 依赖 |
|-------|------|------|
| [douyin-publish](./skills/douyin-publish/) | 抖音文章/图文自动发布 | OpenCLI + Browser Bridge |

## 安装

将需要的 skill 目录复制或链接到 OpenClaw workspace 的 skills 目录：

```bash
# 复制单个 skill
cp -r skills/douyin-publish ~/.openclaw/workspace/skills/

# 或链接（方便后续 git pull 更新）
ln -s $(pwd)/skills/douyin-publish ~/.openclaw/workspace/skills/douyin-publish
```

重启 Gateway 使 skill 生效。

## 贡献

欢迎提交 PR 添加新的 skill。
