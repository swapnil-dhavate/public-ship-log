"""Tiny JSON-over-HTTP helper on top of urllib (no third-party packages)."""
import json
import urllib.error
import urllib.parse
import urllib.request


class HttpError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


def request(method, url, payload=None, headers=None, params=None, timeout=30):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    hdrs = {"User-Agent": "public-ship-log/1.0", "Accept": "application/json"}
    hdrs.update(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.read().decode("utf-8", "replace")) from None
    return json.loads(body) if body else {}


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, payload, **kw):
    return request("POST", url, payload=payload, **kw)
