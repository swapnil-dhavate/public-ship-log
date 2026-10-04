"""Write docs/data.json, which the static page (docs/index.html) reads."""
import json
from collections import defaultdict

from . import env, store
from .streak import compute, now_ist


def build():
    cfg = env.config()
    entries = store.entries()

    days = defaultdict(lambda: {"n": 0, "h": 0.0, "c": 0})
    for e in entries:
        d = days[e["date"]]
        d["n"] += 1
        d["h"] = round(d["h"] + (e.get("hours") or 0), 2)
        d["c"] += e["source"] == "github"

    timeline = [
        {k: e[k] for k in ("date", "time", "source", "text", "hours", "repo", "url") if e.get(k)}
        for e in reversed(entries[-300:])
    ]
    posts = [{"date": p["date"], "text": p["text"], "url": p["url"]}
             for p in store.posts() if p["status"] == "posted" and p.get("url")][-60:]

    data = {
        "title": cfg["title"],
        "subtitle": cfg["subtitle"],
        "links": cfg.get("links") or [],
        "generated": now_ist().isoformat(timespec="seconds"),
        "stats": compute(entries),
        "days": dict(sorted(days.items())),
        "timeline": timeline,
        "posts": posts,
    }
    env.DOCS_DIR.mkdir(exist_ok=True)
    out = env.DOCS_DIR / "data.json"
    new = json.dumps(data, indent=1, ensure_ascii=False)
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    # Only rewrite when something other than the timestamp changed (keeps git history quiet).
    strip = lambda s: "\n".join(l for l in s.splitlines() if '"generated"' not in l)
    if strip(new) != strip(old):
        out.write_text(new + "\n", encoding="utf-8")
        return True
    return False
