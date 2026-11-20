"""MythLab Reader — đọc & nghe truyện theo định dạng repo Done_*.

Định dạng nguồn (giống repo Done_*):
    <root>/<Tên truyện>/info.json              (tùy chọn: name, synopsis, poster, genres, tags...)
    <root>/<Tên truyện>/chapters_manifest.json (tùy chọn)
    <root>/<Tên truyện>/Chương <N> <tiêu đề>.txt

Nguồn hỗ trợ (cấu hình trong config.json):
    - local : thư mục trên máy (quét <root>/<truyện> và <root>/<repo>/<truyện>)
    - github: đọc trực tiếp các repo có tiền tố (mặc định Done_) qua GitHub API,
              xác thực bằng GITHUB_TOKEN hoặc `gh auth token`; cache ra đĩa.

Chạy:  python server.py  [--port 8765] [--host 127.0.0.1] [--lan]
       --lan: mở cho mạng LAN (0.0.0.0); mọi /api/* cần khoá truy cập (X-MythLab-Key hoặc ?k=).
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))
BUNDLE = Path(getattr(sys, "_MEIPASS", HERE))
STATIC = BUNDLE / "static"
if FROZEN:  # bản đóng gói (PyInstaller): dữ liệu người dùng nằm ngoài thư mục cài
    _exe_dir = Path(sys.executable).resolve().parent
    _appdata = Path(os.environ.get("APPDATA") or Path.home()) / "MythLab"
    CACHE = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "MythLab" / "cache"
    CONFIG_PATH = _exe_dir / "config.json" if (_exe_dir / "config.json").exists() else _appdata / "config.json"
    BASE = CONFIG_PATH.parent
else:
    CACHE = HERE / ".cache"
    CONFIG_PATH = HERE / "config.json"
    BASE = HERE

CHAPTER_RE = re.compile(r"^Chương\s+(\d+)\s*[-:.–]?\s*(.*?)\.txt$", re.IGNORECASE)
HEADER_RULE = re.compile(r"^\s*[=\-_*]{5,}\s*$")

DEFAULT_CONFIG = {
    "local": [
        {"name": "MythLab", "path": ".."},
        {"name": "Thư viện (library/)", "path": "library"},
    ],
    "github": [{"owner": "", "prefix": "Done_"}],
    "tts": {"default_voice": "vi-VN-HoaiMyNeural"},
}


def load_config() -> dict:
    if FROZEN and not CONFIG_PATH.exists():  # lần đầu: github/tts từ config đóng kèm, thư viện ở %APPDATA%
        cfg = dict(DEFAULT_CONFIG)
        try:
            cfg.update(json.loads((BUNDLE / "config.json").read_text(encoding="utf-8-sig")))
        except Exception:  # noqa: BLE001
            pass
        cfg["local"] = [{"name": "Thư viện (library/)", "path": "library"}]
        return cfg
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
            return {**DEFAULT_CONFIG, **cfg}
        except Exception as e:  # noqa: BLE001
            print(f"[config] lỗi đọc config.json: {e} — dùng mặc định", file=sys.stderr)
    return dict(DEFAULT_CONFIG)


def natural_title(raw: str) -> str:
    return raw.strip().strip("-:. ").strip()


def parse_chapter_name(filename: str):
    m = CHAPTER_RE.match(filename)
    if not m:
        return None
    return int(m.group(1)), natural_title(m.group(2))


def clean_chapter_text(text: str) -> tuple[str | None, list[str]]:
    """Tách header kiểu
        =====
        Chương 1: Tên
        =====
    và trả về (title, danh sách đoạn)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
    lines = text.split("\n")
    title = None
    # header block: rule / title / rule trong vài dòng đầu
    head = [i for i, ln in enumerate(lines[:8]) if HEADER_RULE.match(ln)]
    if len(head) >= 2 and head[1] - head[0] <= 4:
        inner = [ln.strip() for ln in lines[head[0] + 1 : head[1]] if ln.strip()]
        if inner:
            title = " ".join(inner)
        lines = lines[head[1] + 1 :]
    paras = [re.sub(r"[ \t]+", " ", ln).strip() for ln in lines]
    paras = [p for p in paras if p and not HEADER_RULE.match(p)]
    if title is None and paras and re.match(r"^Chương\s+\d+", paras[0], re.I) and len(paras[0]) < 160:
        title = paras.pop(0)
    return title, paras


def info_summary(info: dict | None, fallback_name: str) -> dict:
    info = info or {}
    poster = info.get("poster")
    if isinstance(poster, dict):
        poster = poster.get("600") or poster.get("default") or next(iter(poster.values()), None)
    genres = [g.get("name") for g in info.get("genres") or [] if isinstance(g, dict) and g.get("name")]
    tags = [t.get("name") for t in info.get("tags") or [] if isinstance(t, dict) and t.get("name")]
    author = info.get("author")
    if isinstance(author, dict):
        author = author.get("name")
    return {
        "name": info.get("name") or fallback_name,
        "author": author,
        "synopsis": info.get("synopsis") or info.get("description") or "",
        "poster": poster if isinstance(poster, str) else None,
        "genres": genres,
        "tags": tags,
        "status": info.get("status_name") or info.get("state"),
        "declared_chapters": info.get("chapter_count"),
        "link": info.get("link"),
    }


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------
class LocalProvider:
    kind = "local"

    def __init__(self, sid: str, name: str, root: Path):
        self.id, self.name, self.root = sid, name, root

    def describe(self):
        return {"id": self.id, "name": self.name, "kind": self.kind, "detail": str(self.root), "available": self.root.is_dir()}

    def _story_dirs(self):
        if not self.root.is_dir():
            return []
        out = []

        def has_chapters(d: Path) -> bool:
            try:
                return any(parse_chapter_name(f.name) for f in d.iterdir() if f.is_file())
            except OSError:
                return False

        for d in sorted(self.root.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")) or d.name in {"reader", "apk", "node_modules"}:
                continue
            if has_chapters(d) or (d / "info.json").exists():
                out.append((d.name, d))
            else:  # có thể là 1 repo Done_* đã clone → quét thêm 1 tầng
                try:
                    for s in sorted(d.iterdir()):
                        if s.is_dir() and not s.name.startswith((".", "_")) and (has_chapters(s) or (s / "info.json").exists()):
                            out.append((f"{d.name}/{s.name}", s))
                except OSError:
                    pass
        return out

    def list_stories(self):
        res = []
        for key, d in self._story_dirs():
            info = None
            if (d / "info.json").exists():
                try:
                    info = json.loads((d / "info.json").read_text(encoding="utf-8-sig"))
                except Exception:  # noqa: BLE001
                    info = None
            n = sum(1 for f in d.iterdir() if f.is_file() and parse_chapter_name(f.name))
            res.append({"key": key, "folder": d.name, "group": key.split("/")[0] if "/" in key else None,
                        "chapter_files": n, **info_summary(info, d.name)})
        return res

    def _dir(self, key: str) -> Path:
        d = (self.root / key).resolve()
        if self.root.resolve() not in d.parents:
            raise PermissionError("path escape")
        return d

    def chapters(self, key: str):
        d = self._dir(key)
        items = []
        for f in d.iterdir():
            p = parse_chapter_name(f.name) if f.is_file() else None
            if p:
                items.append({"n": p[0], "title": p[1], "file": f.name})
        items.sort(key=lambda x: (x["n"], x["file"]))
        return items

    def read_chapter(self, key: str, file: str) -> str:
        f = (self._dir(key) / file)
        if f.parent != self._dir(key) or not parse_chapter_name(f.name):
            raise PermissionError("bad chapter file")
        return f.read_text(encoding="utf-8-sig", errors="replace")

    def info(self, key: str):
        p = self._dir(key) / "info.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:  # noqa: BLE001
                return None
        return None


class GitHub:
    API = "https://api.github.com"

    def __init__(self):
        self._token = None
        self._token_lock = threading.Lock()

    def token(self):
        with self._token_lock:
            if self._token is None:
                tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
                if not tok:
                    try:
                        tok = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=15,
                                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.strip()
                    except Exception:  # noqa: BLE001
                        tok = ""
                self._token = tok or ""
            return self._token

    def get(self, path: str, raw: bool = False, timeout: int = 60):
        url = path if path.startswith("http") else self.API + path
        headers = {"User-Agent": "mythlab-reader", "X-GitHub-Api-Version": "2022-11-28",
                   "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json"}
        if self.token():
            headers["Authorization"] = f"Bearer {self.token()}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            link = r.headers.get("Link", "")
        return (body if raw else json.loads(body)), link


GH = GitHub()


def qpath(p: str) -> str:
    return urllib.parse.quote(p, safe="/")


class GitHubProvider:
    """Mỗi repo khớp tiền tố là 1 'nguồn con'; truyện = thư mục cấp 1 trong repo."""

    kind = "github"

    def __init__(self, sid: str, owner: str, prefix: str):
        self.id, self.owner, self.prefix = sid, owner, prefix
        self.name = f"GitHub {owner or '(tôi)'}/{prefix}*"
        self._repos = None
        self._repos_at = 0.0
        self._trees: dict[str, tuple[float, dict]] = {}
        self._lock = threading.Lock()
        self.cache = CACHE / "github"
        self.cache.mkdir(parents=True, exist_ok=True)

    def describe(self):
        return {"id": self.id, "name": self.name, "kind": self.kind, "detail": f"{self.owner}/{self.prefix}*", "available": True}

    def repos(self):
        with self._lock:
            if self._repos is not None and time.time() - self._repos_at < 600:
                return self._repos
        owner = self.owner
        if not owner:
            me, _ = GH.get("/user")
            owner = self.owner = me["login"]
            self.name = f"GitHub {owner}/{self.prefix}*"
        url = f"/user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=full_name"
        out = []
        while url:
            data, link = GH.get(url)
            for r in data:
                if r["owner"]["login"].lower() == owner.lower() and r["name"].startswith(self.prefix):
                    out.append({"repo": r["name"], "branch": r.get("default_branch") or "main",
                                "pushed_at": r.get("pushed_at"), "private": r.get("private")})
            m = re.search(r'<([^>]+)>;\s*rel="next"', link or "")
            url = m.group(1) if m else None
        out.sort(key=lambda x: x["repo"].lower())
        with self._lock:
            self._repos, self._repos_at = out, time.time()
        return out

    def _tree(self, repo: str) -> dict:
        """{story: {"info": sha|None, "chapters": [(n,title,file,sha)]}}"""
        with self._lock:
            hit = self._trees.get(repo)
            if hit and time.time() - hit[0] < 600:
                return hit[1]
        branch = next((r["branch"] for r in self.repos() if r["repo"] == repo), "main")
        cfile = self.cache / f"tree_{repo}.json"
        try:
            commit, _ = GH.get(f"/repos/{self.owner}/{repo}/commits/{branch}")
            sha = commit["commit"]["tree"]["sha"]
        except Exception:  # noqa: BLE001 — offline: dùng cache cũ
            if cfile.exists():
                stories = json.loads(cfile.read_text(encoding="utf-8"))["stories"]
                with self._lock:
                    self._trees[repo] = (time.time(), stories)
                return stories
            raise
        if cfile.exists():
            cached = json.loads(cfile.read_text(encoding="utf-8"))
            if cached.get("sha") == sha:
                with self._lock:
                    self._trees[repo] = (time.time(), cached["stories"])
                return cached["stories"]
        data, _ = GH.get(f"/repos/{self.owner}/{repo}/git/trees/{sha}?recursive=1", timeout=120)
        entries = data.get("tree", [])
        if data.get("truncated"):
            entries = self._tree_slow(repo, sha)
        stories: dict[str, dict] = {}
        for e in entries:
            if e.get("type") != "blob":
                continue
            parts = e["path"].split("/")
            if len(parts) != 2:
                continue
            story, fname = parts
            s = stories.setdefault(story, {"info": None, "chapters": []})
            if fname == "info.json":
                s["info"] = e["sha"]
            else:
                p = parse_chapter_name(fname)
                if p:
                    s["chapters"].append([p[0], p[1], fname, e["sha"]])
        for s in stories.values():
            s["chapters"].sort(key=lambda c: (c[0], c[2]))
        stories = {k: v for k, v in stories.items() if v["chapters"] or v["info"]}
        cfile.write_text(json.dumps({"sha": sha, "stories": stories}, ensure_ascii=False), encoding="utf-8")
        with self._lock:
            self._trees[repo] = (time.time(), stories)
        return stories

    def _tree_slow(self, repo: str, sha: str):
        top, _ = GH.get(f"/repos/{self.owner}/{repo}/git/trees/{sha}")
        out = []
        for t in top["tree"]:
            if t["type"] != "tree":
                continue
            sub, _ = GH.get(f"/repos/{self.owner}/{repo}/git/trees/{t['sha']}")
            for e in sub["tree"]:
                out.append({**e, "path": f"{t['path']}/{e['path']}"})
        return out

    def blob(self, repo: str, sha: str) -> bytes:
        f = self.cache / "blobs" / sha[:2] / sha
        if f.exists():
            return f.read_bytes()
        data, _ = GH.get(f"/repos/{self.owner}/{repo}/git/blobs/{sha}", raw=True)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
        return data

    def info_for(self, repo: str, story: str):
        s = self._tree(repo).get(story)
        if not s or not s["info"]:
            return None
        try:
            return json.loads(self.blob(repo, s["info"]).decode("utf-8-sig", errors="replace"))
        except Exception:  # noqa: BLE001
            return None

    def list_stories(self, repo: str | None = None):
        repos = [repo] if repo else [r["repo"] for r in self.repos()]
        res = []

        def one(rp):
            tree = self._tree(rp)
            out = []
            for story, s in sorted(tree.items()):
                out.append({"key": f"{rp}/{story}", "folder": story, "group": rp,
                            "chapter_files": len(s["chapters"]), **info_summary(self.info_for(rp, story), story)})
            return out

        with ThreadPoolExecutor(max_workers=8) as ex:
            for part in ex.map(one, repos):
                res.extend(part)
        return res

    @staticmethod
    def _split(key: str):
        repo, _, story = key.partition("/")
        return repo, story

    def chapters(self, key: str):
        repo, story = self._split(key)
        s = self._tree(repo).get(story) or {"chapters": []}
        return [{"n": c[0], "title": c[1], "file": c[2]} for c in s["chapters"]]

    def read_chapter(self, key: str, file: str) -> str:
        repo, story = self._split(key)
        s = self._tree(repo).get(story) or {"chapters": []}
        for c in s["chapters"]:
            if c[2] == file:
                return self.blob(repo, c[3]).decode("utf-8-sig", errors="replace")
        raise FileNotFoundError(file)

    def info(self, key: str):
        return self.info_for(*self._split(key))


class Library:
    def __init__(self, cfg: dict):
        self.providers: dict[str, object] = {}
        for i, loc in enumerate(cfg.get("local") or []):
            p = Path(loc["path"])
            if not p.is_absolute():
                p = (BASE / p).resolve()
            self.providers[f"local{i}"] = LocalProvider(f"local{i}", loc.get("name") or p.name, p)
        gh = cfg.get("github") or []
        if isinstance(gh, dict):
            gh = [gh]
        for i, g in enumerate(gh):
            if g.get("enabled", True):
                self.providers[f"gh{i}"] = GitHubProvider(f"gh{i}", g.get("owner", ""), g.get("prefix", "Done_"))
        self._list_cache: dict[str, tuple[float, list]] = {}

    def get(self, sid: str):
        if sid not in self.providers:
            raise KeyError(sid)
        return self.providers[sid]


# ---------------------------------------------------------------------------
# TTS (edge-tts)
# ---------------------------------------------------------------------------
try:
    import edge_tts  # type: ignore
except Exception:  # noqa: BLE001
    edge_tts = None

TTS_DIR = CACHE / "tts"
_tts_locks: dict[str, threading.Lock] = {}
_tts_locks_guard = threading.Lock()
_tts_sem = threading.Semaphore(2)  # dịch vụ Edge hay chặn khi gọi dồn dập
VOICES_FALLBACK = [
    {"id": "vi-VN-HoaiMyNeural", "name": "Hoài My (nữ)", "gender": "Female"},
    {"id": "vi-VN-NamMinhNeural", "name": "Nam Minh (nam)", "gender": "Male"},
]


def tts_mp3(text: str, voice: str, rate: int, pitch: int) -> Path:
    if edge_tts is None:
        raise RuntimeError("edge-tts chưa được cài (pip install edge-tts)")
    if not re.fullmatch(r"[A-Za-z]{2,3}-[A-Za-z]{2,4}-[A-Za-z]+Neural", voice):
        raise ValueError("voice không hợp lệ")
    rate = max(-50, min(100, int(rate)))
    pitch = max(-50, min(50, int(pitch)))
    key = hashlib.sha1(f"{voice}|{rate}|{pitch}|{text}".encode()).hexdigest()
    out = TTS_DIR / key[:2] / f"{key}.mp3"
    if out.exists() and out.stat().st_size > 0:
        return out
    with _tts_locks_guard:
        lock = _tts_locks.setdefault(key, threading.Lock())
    with lock, _tts_sem:
        if out.exists() and out.stat().st_size > 0:
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(f".{threading.get_ident()}.tmp")
        last = None
        for attempt in range(3):
            try:
                try:
                    comm = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz",
                                                connect_timeout=10, receive_timeout=25)
                except TypeError:  # bản edge-tts cũ không có tham số timeout
                    comm = edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz")
                asyncio.run(comm.save(str(tmp)))
                if tmp.exists() and tmp.stat().st_size > 0:
                    os.replace(tmp, out)
                    return out
                last = RuntimeError("edge-tts trả về rỗng")
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(1.2 * (attempt + 1))
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"TTS lỗi: {last}")


_voices_cache = None


def list_voices():
    global _voices_cache
    if _voices_cache is not None:
        return _voices_cache
    if edge_tts is None:
        return []
    try:
        vs = asyncio.run(edge_tts.list_voices())
        vi = [{"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"]), "gender": v.get("Gender")}
              for v in vs if v.get("Locale", "").startswith("vi-")]
        multi = [{"id": v["ShortName"], "name": v.get("FriendlyName", v["ShortName"]), "gender": v.get("Gender")}
                 for v in vs if "Multilingual" in v["ShortName"]]
        _voices_cache = vi + multi or VOICES_FALLBACK
    except Exception:  # noqa: BLE001
        _voices_cache = VOICES_FALLBACK
    return _voices_cache


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
CFG = load_config()
LIB = Library(CFG)


CORS_ORIGINS = {"https://localhost", "http://localhost", "capacitor://localhost", "tauri://localhost"}
CORS_ORIGIN_RE = re.compile(r"^http://(localhost|127\.0\.0\.1)(:\d{1,5})?$")
KEY_COOKIE = "mythlab_key"
LOOPBACK = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}


def cors_ok(origin: str | None) -> bool:
    return bool(origin) and (origin in CORS_ORIGINS or bool(CORS_ORIGIN_RE.match(origin)))


class Handler(SimpleHTTPRequestHandler):
    server_version = "MythLabReader/1.0"
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
                      ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon",
                      ".webmanifest": "application/manifest+json", ".woff2": "font/woff2", ".woff": "font/woff",
                      ".ttf": "font/ttf", ".otf": "font/otf"}
    _set_cookie = None

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def log_message(self, fmt, *args):  # gọn log
        if "/api/tts" in (self.path or "") and " 200 " in (fmt % args if args else fmt):
            return
        msg = re.sub(r"([?&]k=)[^&\s]+", r"\1***", fmt % args)
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), msg))

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        elif cors_ok(self.headers.get("Origin")):
            self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
            self.send_header("Vary", "Origin")
        if self._set_cookie:
            self.send_header("Set-Cookie", self._set_cookie)
        super().end_headers()

    # --- chế độ LAN: khoá truy cập (header X-MythLab-Key, ?k= hoặc cookie) ---
    def _key_ok(self, q: dict) -> bool:
        key = getattr(self.server, "access_key", None)
        if not getattr(self.server, "lan", False) or not key or self.client_address[0] in LOOPBACK:
            return True
        given = self.headers.get("X-MythLab-Key") or q.get("k") or ""
        if not given:
            for part in (self.headers.get("Cookie") or "").split(";"):
                name, _, val = part.strip().partition("=")
                if name == KEY_COOKIE:
                    given = val
        return hmac.compare_digest(given.encode(), key.encode())

    def do_OPTIONS(self):  # noqa: N802 — CORS preflight
        ok = self.path.startswith("/api/") and cors_ok(self.headers.get("Origin"))
        self.send_response(204 if ok else 403)
        if ok:
            self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "X-MythLab-Key, Content-Type, Range")
            self.send_header("Access-Control-Max-Age", "600")
            if self.headers.get("Access-Control-Request-Private-Network"):
                self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _err(self, status, msg):
        self._json({"error": msg}, status)

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlsplit(self.path)
        q = {k: v[-1] for k, v in urllib.parse.parse_qs(u.query).items()}
        if not u.path.startswith("/api/"):
            # LAN: mở http://ip:port/?k=<khoá> một lần → cookie cho các /api/* cùng gốc
            key = getattr(self.server, "access_key", None)
            if getattr(self.server, "lan", False) and key and hmac.compare_digest(q.get("k", "").encode(), key.encode()):
                self._set_cookie = f"{KEY_COOKIE}={q['k']}; Path=/; Max-Age=31536000; SameSite=Strict; HttpOnly"
            return super().do_GET()
        if not self._key_ok(q):
            return self._err(401, "cần khoá truy cập (X-MythLab-Key)")
        try:
            route = u.path[5:]
            if route == "ping":
                return self._json({"ok": True, "app": "mythlab"})
            if route == "sources":
                out = []
                for p in LIB.providers.values():
                    d = p.describe()
                    if isinstance(p, GitHubProvider):
                        try:
                            d["repos"] = p.repos()
                            d["name"] = p.name
                        except Exception as e:  # noqa: BLE001
                            d["available"], d["error"] = False, str(e)
                    out.append(d)
                return self._json({"sources": out, "tts": {"edge": edge_tts is not None,
                                                           "default_voice": CFG.get("tts", {}).get("default_voice")}})
            if route == "stories":
                p = LIB.get(q["source"])
                if isinstance(p, GitHubProvider):
                    return self._json({"stories": p.list_stories(q.get("repo") or None)})
                return self._json({"stories": p.list_stories()})
            if route == "story":
                p = LIB.get(q["source"])
                key = q["key"]
                info = p.info(key)
                folder = key.split("/")[-1]
                return self._json({"key": key, "source": q["source"], **info_summary(info, folder),
                                   "chapters": p.chapters(key)})
            if route == "chapter":
                p = LIB.get(q["source"])
                raw = p.read_chapter(q["key"], q["file"])
                title, paras = clean_chapter_text(raw)
                pn = parse_chapter_name(q["file"])
                if not title and pn:
                    title = f"Chương {pn[0]}" + (f": {pn[1]}" if pn[1] else "")
                return self._json({"title": title, "paragraphs": paras,
                                   "words": sum(len(x.split()) for x in paras)})
            if route == "voices":
                return self._json({"voices": list_voices(), "edge": edge_tts is not None})
            if route == "tts":
                text = (q.get("text") or "").strip()
                if not text:
                    return self._err(400, "text rỗng")
                if len(text) > 3000:
                    return self._err(413, "text quá dài")
                path = tts_mp3(text, q.get("voice") or "vi-VN-HoaiMyNeural",
                               int(q.get("rate") or 0), int(q.get("pitch") or 0))
                data = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "public, max-age=31536000, immutable")
                self.end_headers()
                self.wfile.write(data)
                return
            return self._err(404, "không có API này")
        except KeyError as e:
            return self._err(400, f"thiếu/không đúng tham số: {e}")
        except FileNotFoundError as e:
            return self._err(404, f"không tìm thấy: {e}")
        except PermissionError as e:
            return self._err(403, str(e))
        except urllib.error.HTTPError as e:
            return self._err(502, f"GitHub {e.code}: {e.reason}")
        except (BrokenPipeError, ConnectionResetError):
            return None
        except Exception as e:  # noqa: BLE001
            return self._err(503 if u.path == "/api/tts" else 500, f"{type(e).__name__}: {e}")


KEY_PATH = CACHE / "server.json"


def access_key() -> str:
    """Khoá LAN: config.json → server.access_key; chưa có thì sinh 1 lần, lưu ở <cache>/server.json
    (không ghi vào config.json vì file đó nằm trong repo công khai)."""
    key = (CFG.get("server") or {}).get("access_key")
    if key:
        return str(key)
    try:
        key = json.loads(KEY_PATH.read_text(encoding="utf-8"))["access_key"]
    except Exception:  # noqa: BLE001
        key = secrets.token_urlsafe(18)
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEY_PATH.write_text(json.dumps({"access_key": key}), encoding="utf-8")
    return key


def lan_ips() -> list[str]:
    ips = set()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            ips.add(s.getsockname()[0])
    except OSError:
        pass
    try:
        ips.update(i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET))
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith(("127.", "169.254.")))


def make_server(host: str = "127.0.0.1", port: int = 8765, lan: bool = False) -> ThreadingHTTPServer:
    """Tạo server (chưa chạy serve_forever). port=0 → OS chọn cổng trống: srv.server_address[1]."""
    if lan and host in ("127.0.0.1", "localhost"):
        host = "0.0.0.0"
    CACHE.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    srv.lan = lan
    srv.access_key = access_key() if lan else None
    return srv


def main():
    ap = argparse.ArgumentParser(description="MythLab Reader")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--lan", action="store_true", help="mở cho mạng LAN (0.0.0.0); /api/* cần khoá truy cập")
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    srv = make_server(args.host, args.port, args.lan)
    host, port = srv.server_address[:2]
    if args.lan:
        print(f"MythLab Reader (LAN): http://127.0.0.1:{port}  (edge-tts: {'có' if edge_tts else 'không'})")
        print(f"  khoá truy cập: {srv.access_key}")
        for ip in lan_ips():
            print(f"  LAN: http://{ip}:{port}/?k={srv.access_key}")
    else:
        print(f"MythLab Reader: http://{args.host}:{args.port}  (edge-tts: {'có' if edge_tts else 'không'})")
    for p in LIB.providers.values():
        print("  nguồn:", p.describe()["name"], "-", p.describe()["detail"])
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
