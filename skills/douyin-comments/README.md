# douyin-comments

抖音评论区抓取 Skill，基于 [OpenCLI](https://github.com/jackwener/OpenCLI) 浏览器自动化。

## 功能

- 抓取抖音笔记/视频的评论区内容
- 提取用户名、评论内容、点赞数、回复数、时间
- 自动保存为结构化 JSON 文件
- 支持滚动加载更多评论

## 依赖

- OpenCLI ≥ v1.7.3
- Browser Bridge Chrome 扩展
- Chrome 浏览器
- Python 3

## 使用

在 OpenClaw 中说：

> "帮我抓一下这个抖音笔记的评论：https://www.douyin.com/note/7620109115684354021"

AI 会自动打开页面、抓取评论、保存 JSON 文件。

## 输出示例

```json
{
  "url": "https://www.douyin.com/note/7620109115684354021",
  "title": "我觉得AI不会替代人工...",
  "author": "刚上课就",
  "comments": [
    {
      "user": "用户名",
      "content": "评论内容",
      "likes": 123,
      "replies": 5,
      "time": "3小时前"
    }
  ],
  "total_comments": 30,
  "scraped_at": "2026-04-14T03:30:00+08:00"
}
```
