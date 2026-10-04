"""JSON file storage in data/ — entries, draft posts and small bits of state."""
import json
import os
import uuid

from .env import DATA_DIR
from .streak import IST, now_ist


def _load(name, default):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save(name, obj):
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{name}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


# ---- entries -------------------------------------------------------------

def entries():
    return _load("entries", [])


def make_entry(text, *, source, at=None, hours=None, repo=None, sha=None, url=None):
    at = (at or now_ist()).astimezone(IST)
    entry = {
        "id": uuid.uuid4().hex[:10],
        "date": at.date().isoformat(),
        "time": at.isoformat(timespec="seconds"),
        "source": source,
        "text": text,
    }
    for key, value in (("hours", hours), ("repo", repo), ("sha", sha), ("url", url)):
        if value:
            entry[key] = value
    return entry


def add_entries(new):
    if not new:
        return
    all_entries = entries() + list(new)
    all_entries.sort(key=lambda e: e["time"])
    _save("entries", all_entries)


def add_entry(text, **kw):
    entry = make_entry(text, **kw)
    add_entries([entry])
    return entry


def remove_entry(entry_id):
    all_entries = entries()
    kept = [e for e in all_entries if e["id"] != entry_id]
    _save("entries", kept)
    return len(kept) != len(all_entries)


def known_shas():
    return {e["sha"] for e in entries() if e.get("sha")}


# ---- posts (drafts awaiting approval, and published ones) -----------------

def posts():
    return _load("posts", [])


def get_post(post_id):
    return next((p for p in posts() if p["id"] == post_id), None)


def save_post(post):
    all_posts = [p for p in posts() if p["id"] != post["id"]]
    all_posts.append(post)
    all_posts.sort(key=lambda p: p["created"])
    _save("posts", all_posts)


def new_post_id():
    return uuid.uuid4().hex[:8]


# ---- misc state (Telegram offset, last reminder, last GitHub sync) --------

def state():
    return _load("state", {})


def update_state(**changes):
    st = state()
    st.update(changes)
    _save("state", st)
    return st
