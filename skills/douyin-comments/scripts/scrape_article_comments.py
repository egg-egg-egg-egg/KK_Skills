#!/usr/bin/env python3
"""
scrape_article_comments.py — 抖音文章/图文评论采集脚本

封装 agent-browser 三步骤（启动→滚动→提取→关闭），
自动检测滚动稳定，输出 JSON 或 Markdown。

依赖：agent-browser (xbrowser skill 内置) + Edge 浏览器登录态

用法：
  python scrape_article_comments.py --url "https://www.douyin.com/article/763...920"
  python scrape_article_comments.py --url "<url>" --format markdown --output ./comments.md
  python scrape_article_comments.py --url "<url>" --scroll-timeout 60
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── 环境检测 ──────────────────────────────────────────────

def _detect_platform():
    """检测当前运行平台和默认路径"""
    system = sys.platform

    if system == "win32":
        # Windows: Edge 路径
        edge_exe = os.environ.get(
            "EDGE_PATH",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        )
        user_data = os.environ.get(
            "EDGE_USER_DATA",
            os.path.join(os.environ["LOCALAPPDATA"], r"Microsoft\Edge\User Data")
        )
        # agent-browser 默认路径（xbrowser skill node_modules）
        ab_default = os.path.join(
            os.path.expanduser("~"), r".qclaw\tools\xbrowser\node_modules\agent-browser\bin\agent-browser-win32-x64.exe"
        )
    elif system == "darwin":
        edge_exe = os.environ.get(
            "CHROME_PATH",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        user_data = os.environ.get(
            "CHROME_USER_DATA",
            os.path.join(os.path.expanduser("~"), "Library/Application Support/Google/Chrome")
        )
        ab_default = os.path.join(
            os.path.expanduser("~"), ".qclaw/tools/xbrowser/node_modules/agent-browser/bin/agent-browser-darwin-x64"
        )
    else:
        # Linux
        edge_exe = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")
        user_data = os.environ.get(
            "CHROME_USER_DATA",
            os.path.join(os.path.expanduser("~"), ".config/google-chrome")
        )
        ab_default = os.path.join(
            os.path.expanduser("~"), ".qclaw/tools/xbrowser/node_modules/agent-browser/bin/agent-browser-linux-x64"
        )

    return system, edge_exe, user_data, ab_default


# ── agent-browser 调用封装 ─────────────────────────────────

class AgentBrowser:
    """agent-browser CLI 的 Python 封装"""

    def __init__(self, browser_path: str, executable_path: str, user_data: str):
        self.browser_path = browser_path
        self.executable_path = executable_path
        self.user_data = user_data
        self._env = os.environ.copy()
        self._env["AGENT_BROWSER_JSON"] = "1"
        self._env["AGENT_BROWSER_EXECUTABLE_PATH"] = self.executable_path
        self._env["AGENT_BROWSER_PROFILE"] = self.user_data

    def _run(self, *args, timeout: int = 30) -> dict:
        """调用 agent-browser 并解析 JSON 输出。
        
        返回 {"ok": True, "data": ...} 或 {"ok": False, "error": ...}
        """
        cmd = [self.browser_path] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._env
            )
            raw = result.stdout.strip() or result.stderr.strip()
            if not raw:
                return {"ok": False, "error": "empty output"}
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return {"ok": False, "error": f"json parse error: {raw[:200]}"}

            if parsed.get("success"):
                return {"ok": True, "data": parsed}
            else:
                return {"ok": False, "error": parsed.get("error", str(parsed))}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"timeout ({timeout}s)"}
        except FileNotFoundError:
            return {"ok": False, "error": f"agent-browser not found at {self.browser_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open(self, url: str, timeout: int = 30) -> dict:
        """打开 URL"""
        return self._run("open", url, timeout=timeout)

    def close(self, timeout: int = 10) -> dict:
        """关闭浏览器"""
        return self._run("close", timeout=timeout)

    def eval_js(self, js: str, timeout: int = 30) -> dict:
        """在页面中执行 JavaScript（IIFE 包裹防冲突）"""
        # 自动清理 JS 中的注释和空白
        clean = re.sub(r'//.*$', '', js, flags=re.MULTILINE)
        clean = ' '.join(clean.split())
        escaped = clean.replace('"', '\\"')
        return self._run("eval", f'"(function(){{ {escaped} }})()"', timeout=timeout)

    def scroll_and_wait(self, container_selector: str, wait_s: float = 2.0) -> int:
        """滚动容器到底并返回 scrollHeight"""
        js = f"""
            var el = document.querySelector('{container_selector}') || document.querySelector('[class*={container_selector.replace("[class*=", "").replace("]", "").strip()}]');
            if (el) {{ el.scrollTop = el.scrollHeight; return el.scrollHeight; }}
            return -1;
        """
        result = self.eval_js(js, timeout=15)
        if not result["ok"]:
            return -1
        try:
            inner = result["data"]["data"]["result"]
            return int(json.loads(inner))
        except (KeyError, json.JSONDecodeError, ValueError, TypeError):
            return -1


# ── 滚动加载逻辑 ───────────────────────────────────────────

def scroll_until_stable(
    ab: AgentBrowser,
    container_selector: str = '[class*=route-scroll]',
    max_rounds: int = 50,
    stable_count: int = 3,
    wait_s: float = 2.0,
    timeout_s: float = 120.0
) -> tuple:
    """
    反复滚动直到 scrollHeight 不再变化，返回 (总条数, 最终scrollH, 轮次)
    
    当 scrollH 连续 stable_count 轮不变时，认为已加载全部评论。
    """
    t0 = time.time()
    last_h = 0
    stable_rounds = 0

    for round_idx in range(1, max_rounds + 1):
        elapsed = time.time() - t0
        if elapsed > timeout_s:
            return -1, last_h, round_idx, "scroll_timeout"

        h = ab.scroll_and_wait(container_selector, wait_s)
        time.sleep(wait_s)

        if h < 0:
            return -1, last_h, round_idx, "scroll_error"

        if h == last_h:
            stable_rounds += 1
        else:
            stable_rounds = 0

        last_h = h

        if stable_rounds >= stable_count:
            # 再确认一次：提取评论数
            count_result = ab.eval_js(
                "return document.querySelectorAll('[data-e2e=comment-item]').length;"
            )
            count = 0
            if count_result["ok"]:
                try:
                    count = int(json.loads(count_result["data"]["data"]["result"]))
                except (KeyError, json.JSONDecodeError, ValueError, TypeError):
                    pass
            return count, h, round_idx, "stable"

    return -1, last_h, max_rounds, "max_rounds"


# ── 评论提取 ───────────────────────────────────────────────

def extract_comments(ab: AgentBrowser) -> list:
    """
    从页面提取所有评论项的 innerText。
    每个评论项是一个 dict: {text, index}
    """
    js = """
        var items = document.querySelectorAll('[data-e2e=comment-item]');
        var result = [];
        items.forEach(function(el, i) {
            result.push({index: i, text: el.innerText});
        });
        return JSON.stringify({total: items.length, items: result});
    """
    result = ab.eval_js(js, timeout=30)
    if not result["ok"]:
        return []
    try:
        inner = result["data"]["data"]["result"]
        data = json.loads(inner)
    except (KeyError, json.JSONDecodeError, TypeError):
        return []
    return data.get("items", [])


# ── 格式化输出 ─────────────────────────────────────────────

def format_markdown(url: str, items: list, headers: dict) -> str:
    """将评论列表格式化为 Markdown"""
    lines = [
        f"# 抖音文章评论",
        f"",
        f"- **URL**: {url}",
        f"- **文章标题**: {headers.get('title', '未知')}",
        f"- **作者**: {headers.get('author', '未知')}",
        f"- **采集评论数**: {len(items)} 条",
        f"- **采集时间**: {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
    ]

    for item in items:
        lines.append(f"### {item['index'] + 1}")
        lines.append(f"")
        lines.append(f"```")
        lines.append(item["text"])
        lines.append(f"```")
        lines.append(f"")

    return "\n".join(lines)


def format_json(url: str, items: list, headers: dict) -> str:
    """将评论列表格式化为 JSON"""
    data = {
        "url": url,
        "title": headers.get("title", ""),
        "author": headers.get("author", ""),
        "count": len(items),
        "scraped_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "comments": items
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── 主流程 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="抖音文章/图文评论采集 — 基于 agent-browser + Edge 登录态"
    )
    parser.add_argument(
        "--url", "-u", required=True,
        help="抖音文章 URL (例: https://www.douyin.com/article/7633534116155149620)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="输出文件路径（默认自动生成到桌面）"
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "markdown", "md"], default="markdown",
        help="输出格式 (default: markdown)"
    )
    parser.add_argument(
        "--browser-path", default=None,
        help="agent-browser 可执行文件路径（默认自动检测）"
    )
    parser.add_argument(
        "--edge-path", default=None,
        help="Edge/Chrome 可执行文件路径（默认自动检测）"
    )
    parser.add_argument(
        "--user-data", default=None,
        help="浏览器 User Data 目录（默认 Edge Default profile）"
    )
    parser.add_argument(
        "--profile", default="Default",
        help="浏览器 Profile 名 (default: Default)"
    )
    parser.add_argument(
        "--scroll-timeout", type=float, default=120,
        help="滚动加载超时秒数 (default: 120)"
    )
    parser.add_argument(
        "--scroll-wait", type=float, default=2.0,
        help="每次滚动后等待秒数 (default: 2.0)"
    )
    parser.add_argument(
        "--container-selector", default="[class*=route-scroll]",
        help="滚动容器 CSS 选择器 (default: [class*=route-scroll])"
    )
    parser.add_argument(
        "--no-close", action="store_true",
        help="采集完成后不关闭浏览器（用于调试）"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅检测环境，不实际采集"
    )

    args = parser.parse_args()

    # ── 环境检测 ──
    platform, default_edge, default_user_data, default_ab = _detect_platform()

    edge_path = args.edge_path or default_edge
    user_data = args.user_data or default_user_data
    ab_path = args.browser_path or default_ab

    # 验证路径
    errors = []
    if not os.path.isfile(ab_path):
        errors.append(f"agent-browser 不存在: {ab_path}")
    if not os.path.isfile(edge_path):
        errors.append(f"浏览器不存在: {edge_path}")
    if not os.path.isdir(user_data):
        errors.append(f"User Data 目录不存在: {user_data}")

    if args.dry_run:
        print("=== 环境检测 ===")
        print(f"  平台: {platform}")
        print(f"  agent-browser: {ab_path} {'✅' if os.path.isfile(ab_path) else '❌'}")
        print(f"  浏览器: {edge_path} {'✅' if os.path.isfile(edge_path) else '❌'}")
        print(f"  User Data: {user_data} {'✅' if os.path.isdir(user_data) else '❌'}")
        print(f"  URL: {args.url}")
        if errors:
            print(f"\n  ⚠️ {len(errors)} 个环境问题:")
            for e in errors:
                print(f"    - {e}")
        sys.exit(1 if errors else 0)

    if errors:
        print(f"❌ 环境错误:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    # ── 提取文章 ID ──
    url = args.url
    m = re.search(r'/article/(\d+)', url)
    article_id = m.group(1) if m else "unknown"

    # ── 输出路径 ──
    if args.output is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if args.format in ("markdown", "md") else "json"
        out_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        args.output = os.path.join(out_dir, f"抖音评论_{article_id}_{ts}.{ext}")

    # ── 启动 agent-browser ──
    print(f"🚀 启动 agent-browser...")
    ab = AgentBrowser(ab_path, edge_path, user_data)
    print(f"   浏览器: {edge_path}")
    print(f"   Profile: {user_data}\\{args.profile}")
    print(f"   URL: {url}")

    open_result = ab.open(url, timeout=30)
    if not open_result["ok"]:
        print(f"❌ 浏览器启动失败: {open_result['error']}", file=sys.stderr)
        print(f"   提示: 确保浏览器已关闭所有窗口再重试，或使用 --edge-path / --user-data 指定路径")
        sys.exit(1)

    print(f"✅ 浏览器已启动，等待页面加载...")
    time.sleep(5)

    # ── 提取文章标题和作者 ──
    headers = {"title": "", "author": ""}
    title_result = ab.eval_js("return document.title || '';", timeout=10)
    if title_result["ok"]:
        try:
            headers["title"] = json.loads(title_result["data"]["data"]["result"])
            # 清理标题后缀
            headers["title"] = re.sub(r'\s*[-–—].*$', '', headers["title"]).strip()
        except (KeyError, json.JSONDecodeError, TypeError):
            pass

    author_result = ab.eval_js(
        "var el = document.querySelector('[data-e2e=user-info-name]'); return el ? el.textContent.trim() : '';",
        timeout=10
    )
    if author_result["ok"]:
        try:
            headers["author"] = json.loads(author_result["data"]["data"]["result"])
        except (KeyError, json.JSONDecodeError, TypeError):
            pass

    print(f"📄 文章: {headers['title'] or '未知'}")
    print(f"👤 作者: {headers['author'] or '未知'}")

    # ── 滚动加载 ──
    print(f"📜 滚动加载评论（超时 {args.scroll_timeout}s）...")
    count, final_h, rounds, reason = scroll_until_stable(
        ab,
        container_selector=args.container_selector,
        max_rounds=50,
        stable_count=3,
        wait_s=args.scroll_wait,
        timeout_s=args.scroll_timeout
    )

    print(f"   scrollH: {final_h}, 轮次: {rounds}, 原因: {reason}")

    # 点击展开回复按钮
    print(f"🔽 展开子回复...")
    expand_count = 0
    for _ in range(3):
        expand_result = ab.eval_js("""
            var btns = document.querySelectorAll('.comment-reply-expand-btn');
            var clicked = 0;
            btns.forEach(function(b) {
                if (b.textContent.includes('展开') && b.offsetParent) { b.click(); clicked++; }
            });
            return clicked;
        """, timeout=10)
        if expand_result["ok"]:
            try:
                expand_count = int(json.loads(expand_result["data"]["data"]["result"]))
            except (KeyError, json.JSONDecodeError, ValueError, TypeError):
                pass
        time.sleep(2)

    print(f"   已点击 {expand_count} 个展开按钮")

    # ── 最终提取 ──
    print(f"📥 提取评论...")
    items = extract_comments(ab)
    print(f"   提取到 {len(items)} 条评论项")

    # ── 关闭浏览器 ──
    if not args.no_close:
        print(f"🔒 关闭浏览器...")
        close_result = ab.close(timeout=10)
        if not close_result["ok"]:
            print(f"   ⚠️ 关闭失败: {close_result['error']}（不影响数据）")

    # ── 格式化输出 ──
    if args.format in ("markdown", "md"):
        content = format_markdown(url, items, headers)
    else:
        content = format_json(url, items, headers)

    # ── 写入文件 ──
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 完成！{len(items)} 条评论 → {args.output}")

    # ── 统计 ──
    if count > 0 and count != len(items):
        print(f"   ⚠️ 注意: 滚动检测到 {count} 个元素，但最终提取了 {len(items)} 条（可能因为展开子回复）")


if __name__ == "__main__":
    main()
