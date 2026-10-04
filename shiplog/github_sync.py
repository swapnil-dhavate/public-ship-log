"""Pull new commits from the repos listed in config.json and log them as entries."""
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


def _commits(repo, since, author):
    params = {"since": since, "per_page": 100}
    if author:
        params["author"] = author
    out = []
    for page in range(1, 6):
        batch = net.get(f"{API}/repos/{repo}/commits", headers=_headers(), params={**params, "page": page})
        out.extend(batch)
        if len(batch) < 100:
            break
    return out


BOT_LOGINS = {"actions-user", "github-actions", "dependabot"}


def _is_automated(c, ignore_patterns):
    """Bot/CI commits shouldn't keep a streak alive."""
    login = ((c.get("author") or {}).get("login") or "").lower()
    email = c["commit"]["author"].get("email", "").lower()
    message = c["commit"]["message"]
    return (login.endswith("[bot]") or login in BOT_LOGINS or email == "actions@github.com"
            or "github-actions" in email or any(p in message for p in ignore_patterns))


def sync(verbose=False):
    """Fetch commits since the last sync (with 2 days of overlap) and add unseen ones."""
    cfg = env.config()
    repos = cfg.get("github_repos") or []
    if not repos:
        return 0

    now = datetime.now(timezone.utc)
    last = store.state().get("github_synced_at")
    if last:
        since_dt = datetime.fromisoformat(last) - timedelta(days=2)  # catch late/rebased pushes
    else:
        since_dt = now - timedelta(days=int(cfg.get("github_backfill_days", 14)))
    since = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    ignore = cfg.get("ignore_commits_matching") or []
    seen = store.known_shas()
    new = []
    for repo in repos:
        try:
            private = net.get(f"{API}/repos/{repo}", headers=_headers()).get("private", False)
            commits = _commits(repo, since, cfg.get("github_author"))
        except Exception as e:  # one broken repo shouldn't block the rest
            print(f"[github] {repo}: {e}")
            continue
        for c in commits:
            sha = c["sha"]
            if sha in seen or len(c.get("parents", [])) > 1 or _is_automated(c, ignore):
                continue
            message = c["commit"]["message"].strip().splitlines()[0][:200]
            at = to_ist(c["commit"]["author"]["date"])
            if private and cfg.get("redact_private_repos", True):
                entry = store.make_entry("Pushed a commit to a private project", source="github",
                                         at=at, repo="private", sha=sha)
            else:
                entry = store.make_entry(message, source="github", at=at, repo=repo, sha=sha,
                                         url=c.get("html_url"))
            new.append(entry)
            seen.add(sha)
        if verbose:
            print(f"[github] {repo}: {len(commits)} commits since {since}")

    store.add_entries(new)
    store.update_state(github_synced_at=now.isoformat(timespec="seconds"))
    return len(new)
