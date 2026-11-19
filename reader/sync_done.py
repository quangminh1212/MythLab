"""Tải (clone nông) các repo Done_* về reader/library/ để đọc offline.

    python sync_done.py                 # liệt kê repo khớp tiền tố
    python sync_done.py --all           # clone/pull tất cả
    python sync_done.py Done_LichSu Done_QuanSu   # chỉ các repo chỉ định
    python sync_done.py --owner quangminh1212 --prefix Done_ --all

Không bắt buộc: server đọc được trực tiếp từ GitHub (nguồn "github" trong config.json).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE / "library"


def gh_json(args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        sys.exit(out.stderr.strip())
    return json.loads(out.stdout)


def main():
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8-sig")) if (HERE / "config.json").exists() else {}
    g = (cfg.get("github") or [{}])
    g = g[0] if isinstance(g, list) and g else (g if isinstance(g, dict) else {})
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="*")
    ap.add_argument("--owner", default=g.get("owner") or "")
    ap.add_argument("--prefix", default=g.get("prefix") or "Done_")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    owner = a.owner or gh_json(["api", "user"])["login"]
    repos = [r["name"] for r in gh_json(["repo", "list", owner, "--limit", "2000", "--json", "name"])
             if r["name"].startswith(a.prefix)]
    repos.sort()
    targets = a.repos or (repos if a.all else [])
    if not targets:
        print(f"{len(repos)} repo khớp {owner}/{a.prefix}*:")
        for r in repos:
            print(("  [đã có] " if (LIB / r).exists() else "  ") + r)
        print("\nDùng --all hoặc truyền tên repo để tải.")
        return
    LIB.mkdir(exist_ok=True)
    for i, r in enumerate(targets, 1):
        dst = LIB / r
        print(f"[{i}/{len(targets)}] {r}", flush=True)
        if (dst / ".git").exists():
            subprocess.run(["git", "-C", str(dst), "pull", "--ff-only", "--depth", "1", "-q"])
        else:
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{owner}/{r}.git", str(dst)])


if __name__ == "__main__":
    main()
