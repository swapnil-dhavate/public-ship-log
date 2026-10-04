"""Post to Bluesky via the AT Protocol (free; needs a handle + app password)."""
import re
from datetime import datetime, timezone

from . import env, net

URL_RE = re.compile(r"https?://[^\s]+")
TAG_RE = re.compile(r"(?<![\w#])#([A-Za-z][A-Za-z0-9_]*)")


def configured():
    return bool(env.get("BLUESKY_HANDLE") and env.get("BLUESKY_APP_PASSWORD"))


def dry_run():
    return env.flag("BLUESKY_DRY_RUN", default=True)


def _byte_range(text, start, end):
    return {"byteStart": len(text[:start].encode("utf-8")), "byteEnd": len(text[:end].encode("utf-8"))}


def facets(text):
    """Make links and #tags clickable (Bluesky needs UTF-8 byte offsets)."""
    out = []
    for m in URL_RE.finditer(text):
        uri = m.group(0).rstrip(".,;:!?)")
        out.append({"index": _byte_range(text, m.start(), m.start() + len(uri)),
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": uri}]})
    for m in TAG_RE.finditer(text):
        out.append({"index": _byte_range(text, m.start(), m.end()),
                    "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]})
    return out


def post(text):
    """Publish and return the public post URL."""
    pds = env.get("BLUESKY_PDS") or "https://bsky.social"
    session = net.post(f"{pds}/xrpc/com.atproto.server.createSession",
                       {"identifier": env.get("BLUESKY_HANDLE"), "password": env.get("BLUESKY_APP_PASSWORD")})
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "langs": ["en"],
    }
    if f := facets(text):
        record["facets"] = f
    resp = net.post(f"{pds}/xrpc/com.atproto.repo.createRecord",
                    {"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
                    headers={"Authorization": f"Bearer {session['accessJwt']}"})
    rkey = resp["uri"].rsplit("/", 1)[-1]
    return f"https://bsky.app/profile/{session['handle']}/post/{rkey}"
