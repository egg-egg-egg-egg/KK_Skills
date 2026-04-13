#!/usr/bin/env python3
"""Check prerequisites for douyin-publish skill: OpenCLI + Browser Bridge + Douyin login"""

import subprocess
import sys


def run(cmd: str) -> tuple:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)


def main():
    checks = []

    # 1. OpenCLI installed
    ok, out = run("opencli --version")
    checks.append(("OpenCLI installed", ok, out if ok else "opencli not found, install first"))

    # 2. OpenCLI doctor
    ok, out = run("opencli doctor")
    daemon_ok = "Daemon" in out and "OK" in out
    ext_ok = "Extension" in out and ("Connected" in out or "OK" in out)
    conn_ok = "Connectivity" in out and "OK" in out
    checks.append(("Daemon running", daemon_ok, out if not daemon_ok else "OK"))
    checks.append(("Browser Bridge connected", ext_ok, out if not ext_ok else "OK"))
    checks.append(("Connectivity OK", conn_ok, out if not conn_ok else "OK"))

    # 3. Browser can reach Douyin
    ok, out = run("opencli browser open https://www.douyin.com")
    checks.append(("Browser can reach Douyin", ok, out if not ok else "OK"))

    print("=" * 50)
    print("Douyin Publish Skill - Environment Check")
    print("=" * 50)
    all_ok = True
    for name, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            print(f"       -> {detail}")
            all_ok = False
    print("=" * 50)
    if all_ok:
        print("All checks passed! Ready to publish.")
    else:
        print("Some checks failed. Fix them before publishing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
