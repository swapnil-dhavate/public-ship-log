"""Paths, .env loading and config.json — the only place settings come from."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

DEFAULT_CONFIG = {
    "title": "Ship Log",
    "subtitle": "Every day I work on my projects shows up here.",
    "github_repos": [],
    "github_author": "",
    "github_backfill_days": 14,
    "redact_private_repos": True,
    "ignore_commits_matching": ["[skip ci]", "[ci skip]"],
    "reminder_time_ist": "21:00",
    "draft_time_ist": "22:30",
    "approval_required": True,
    "hashtags": ["buildinpublic"],
    "site_url": "",
    "links": [],
}


def load_env():
    """Read KEY=VALUE lines from .env into os.environ (real env vars win)."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get(name, default=""):
    return os.environ.get(name, default).strip()


def flag(name, default=False):
    value = get(name)
    if not value:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def config():
    cfg = dict(DEFAULT_CONFIG)
    path = ROOT / "config.json"
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    return cfg


load_env()
