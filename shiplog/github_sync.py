"""Pull new commits from the tracked repos and log them as entries.

Repos come from two places:
  * config.json "github_repos": public, so only list repos that are public anyway.
  * the SHIPLOG_REPOS env var / Actions secret (comma separated): for private repos.
    Their names are never printed or saved, because the logs and data/ are public.
"""
import re
from datetime import datetime, timedelta, timezone

from . import env, net, store
from .streak import to_ist

API = "https://api.github.com"


def _headers():
    hdrs = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    return hdrs


def repos(cfg):
    """[(repo, label)] where label is what may be printed in public logs."""
    public = [r.strip() for r in cfg.get("github_repos") or [] if r.strip()]
    hidden = [r for r in re.split(r"[\s,]+", env.get("SHIPLOG_REPOS")) if r]
    out = [(r, r) for r in public]
    seen = {r.lower() for r in public}
    for i, r in enumerate(hidden, 1):
        if r.lower() not in seen:
            out.append((r, f"private repo #{i}"))
            seen.add(r.lower())
    return out


def _commits(repo, since):
    # No server-side "author" filter: GitHub's author=<login> misses commits made with the
    # <id>+<login>@users.noreply.github.com address, so authorship is checked in _is_mine().
    params = {"since": since, "per_page": 100}
    out = []
    for page in range(1, 6):
        batch = net.get(f"{API}/repos/{repo}/commits", headers=_headers(), params={**params, "page": page})
        out.extend(batch)
        if len(batch) < 100:
            break
    return out


def _is_mine(c, author):
    """Commit belongs to the GitHub account `author` (by linked login or its noreply email)."""
    if not author:
        return True
    author = author.lower()
    login = ((c.get("author") or {}).get("login") or "").lower()
    email = ((c.get("commit") or {}).get("author") or {}).get("email", "").lower()
    noreply = f"{author}@users.noreply.github.com"
    return login == author or email == noreply or email.endswith("+" + noreply)


BOT_LOGINS = {"actions-user", "github-actions", "dependabot"}


def _is_automated(c, ignore_patterns):
    """Bot/CI commits shouldn't keep a streak alive."""
    login = ((c.get("author") or {}).get("login") or "").lower()
    email = c["commit"]["author"].get("email", "").lower()
    message = c["commit"]["message"]
    return (login.endswith("[bot]") or login in BOT_LOGINS or email == "actions@github.com"
            or "github-actions" in email or any(p in message for p in ignore_patterns))


def sync(verbose=False):
    """Fetch each repo's commits since its own last good sync (with 2 days of overlap).

    The cursor is kept per repo (keyed by GitHub's numeric repo id, not its name) and only
    moves when that repo was read successfully, so a repo the token can't read yet gets a
    full backfill once access is granted instead of silently losing that history.
    """
    cfg = env.config()
    tracked = repos(cfg)
    if not tracked:
        return 0

    now = datetime.now(timezone.utc)
    backfill = now - timedelta(days=int(cfg.get("github_backfill_days", 14)))
    cursors = dict(store.state().get("github_cursors") or {})
    author = cfg.get("github_author")
    redact = cfg.get("redact_private_repos", True)
    ignore = cfg.get("ignore_commits_matching") or []
    seen = store.known_shas()
    new = []
    for repo, label in tracked:
        try:
            info = net.get(f"{API}/repos/{repo}", headers=_headers())
            key = str(info["id"])
            last = cursors.get(key)
            since_dt = datetime.fromisoformat(last) - timedelta(days=2) if last else backfill
            since = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            commits = _commits(repo, since)
        except Exception as e:  # one broken repo shouldn't block the rest
            print(f"[github] {label}: {str(e).replace(repo, label)[:200]}")
            continue
        # Fail closed: anything not explicitly public is treated as private.
        hide = redact and info.get("private") is not False
        counted = 0
        for c in commits:
            sha = c["sha"]
            if (sha in seen or len(c.get("parents", [])) > 1 or not _is_mine(c, author)
                    or _is_automated(c, ignore)):
                continue
            at = to_ist(c["commit"]["author"]["date"])
            if hide:
                entry = store.make_entry("Pushed a commit to a private project", source="github",
                                         at=at, repo="private", sha=sha)
            else:
                message = c["commit"]["message"].strip().splitlines()[0][:200]
                entry = store.make_entry(message, source="github", at=at, repo=repo, sha=sha,
                                         url=c.get("html_url"))
            new.append(entry)
            seen.add(sha)
            counted += 1
        cursors[key] = now.isoformat(timespec="seconds")
        if verbose:
            print(f"[github] {label}: {counted} new of {len(commits)} commits since {since}")

    store.add_entries(new)
    store.update_state(github_synced_at=now.isoformat(timespec="seconds"), github_cursors=cursors)
    return len(new)
