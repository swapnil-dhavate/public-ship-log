"""Time-based jobs. They are idempotent, so they can run every few minutes and only
act once they are due: the 9 PM IST reminder and the nightly draft."""
from . import bot, env, store, tg
from .streak import compute, now_ist


def _minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def run_due_jobs():
    cfg = env.config()
    now = now_ist()
    today = now.date().isoformat()
    minute = now.hour * 60 + now.minute
    entries = store.entries()
    stats = compute(entries)
    done = []

    if minute >= _minutes(cfg["reminder_time_ist"]) and not stats["logged_today"] \
            and store.state().get("reminded_on") != today:
        if stats["current"]:
            text = (f"⚠️ <b>Streak at risk!</b> You're on a {stats['current']}-day streak and haven't "
                    "logged anything today.\nEven 20 minutes counts → <code>/log what you did</code>")
        else:
            text = "Nothing logged today. Do one small thing and start a streak → <code>/log what you did</code>"
        tg.send(text)
        store.update_state(reminded_on=today)
        done.append("reminder")

    has_post_today = any(p["date"] == today for p in store.posts())
    if minute >= _minutes(cfg["draft_time_ist"]) and stats["logged_today"] and not has_post_today:
        bot.create_draft(today)
        done.append("draft")

    return done
