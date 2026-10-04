"""IST clock helpers and the streak calculation.

A "day" is a calendar day in India Standard Time (UTC+05:30, no daylight saving,
so a fixed offset is exact and needs no tz database on Windows).
"""
from datetime import date, datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")
ONE_DAY = timedelta(days=1)


def now_ist():
    return datetime.now(IST)


def today_ist():
    return now_ist().date()


def to_ist(dt):
    """Accept a datetime or ISO string (incl. trailing 'Z') and return it in IST."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def compute(entries, today=None):
    """Streak stats from a list of entries (each has an IST 'date' string)."""
    today = today or today_ist()
    days = {date.fromisoformat(e["date"]) for e in entries}
    days = {d for d in days if d <= today}  # ignore anything dated in the future

    logged_today = today in days
    current = 0
    day = today if logged_today else today - ONE_DAY
    while day in days:
        current += 1
        day -= ONE_DAY

    longest = run = 0
    prev = None
    for d in sorted(days):
        run = run + 1 if prev and d - prev == ONE_DAY else 1
        longest = max(longest, run)
        prev = d

    return {
        "current": current,
        "longest": longest,
        "total_days": len(days),
        "logged_today": logged_today,
        "at_risk": not logged_today and current > 0,
        "last_logged": max(days).isoformat() if days else None,
        "total_entries": len(entries),
        "total_hours": round(sum(e.get("hours") or 0 for e in entries), 1),
        "total_commits": sum(1 for e in entries if e.get("source") == "github"),
        "today": today.isoformat(),
    }
