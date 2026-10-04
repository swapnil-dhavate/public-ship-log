"""Telegram commands, draft approval buttons and publishing."""
import html
import re

from . import bluesky, env, store, tg, writer
from .streak import compute, now_ist, today_ist

HOURS_RE = re.compile(
    r"(?<!\S)(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)(?![\w])", re.I)

HELP = (
    "<b>Ship Log bot</b>\n\n"
    "/log <i>what you did</i> [2h] — log today's work (hours optional: 2h, 1.5h, 45m)\n"
    "/streak — current streak and stats\n"
    "/today — what's logged today\n"
    "/undo — remove your last /log entry\n"
    "/draft — write today's update post now (you approve before it's posted)\n"
)


def parse_log(text):
    """'fixed login bug 1.5h' -> ('fixed login bug', 1.5). Hours are optional."""
    hours = None
    matches = list(HOURS_RE.finditer(text))
    if matches:
        m = matches[-1]
        value = float(m.group(1))
        value = value if m.group(2).lower().startswith("h") else value / 60
        if 0 < value <= 24:
            hours = round(value, 2)
            text = text[: m.start()] + text[m.end():]
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+(for|in|-|–)$", "", text).strip(" ,;-–")
    return text, hours


def _stats():
    return compute(store.entries())


def streak_line(stats):
    n = stats["current"]
    if stats["logged_today"]:
        return f"🔥 {n}-day streak. Today is done."
    if n:
        return f"⚠️ {n}-day streak — not logged today yet."
    return "No active streak. Log something today to start one."


# ---- drafts ---------------------------------------------------------------

def _draft_message(post):
    status = {"pending": "", "posted": f"\n\n✅ Posted: {post.get('url', '')}",
              "approved": "\n\n✅ Approved (not posted — Bluesky dry-run or not configured)",
              "skipped": "\n\n⏭ Skipped"}[post["status"]]
    return (f"📝 <b>Draft for {post['date']}</b> <i>({post['provider']}, {len(post['text'])}/300)</i>\n\n"
            f"{html.escape(post['text'])}{status}")


DRAFT_BUTTONS = [[("✅ Approve & post", "ap"), ("⏭ Skip", "sk")], [("🔄 Rewrite", "rg")]]


def _buttons(post_id):
    return [[(label, f"{action}:{post_id}") for label, action in row] for row in DRAFT_BUTTONS]


def create_draft(day=None, notify=True):
    """Write a draft for an IST date, replace any pending one, and send it for approval."""
    day = day or today_ist().isoformat()
    text, provider = writer.draft_for(day)
    if text is None:
        if notify:
            tg.send(f"Nothing logged on {day}, so there's nothing to post.")
        return None
    for old in store.posts():
        if old["date"] == day and old["status"] == "pending":
            old["status"] = "skipped"
            store.save_post(old)
    post = {"id": store.new_post_id(), "date": day, "created": now_ist().isoformat(timespec="seconds"),
            "text": text, "provider": provider, "status": "pending"}
    store.save_post(post)

    if not env.config().get("approval_required", True):
        publish(post)
        if notify:
            tg.send(_draft_message(post))
        return post
    if notify:
        msg = tg.send(_draft_message(post), buttons=_buttons(post["id"]))
        post["message_id"] = msg["message_id"]
        store.save_post(post)
    return post


def publish(post):
    if bluesky.configured() and not bluesky.dry_run():
        post["url"] = bluesky.post(post["text"])
        post["status"] = "posted"
    else:
        post["status"] = "approved"
    post["decided"] = now_ist().isoformat(timespec="seconds")
    store.save_post(post)
    return post


def _on_callback(cq):
    chat_id = str(cq["message"]["chat"]["id"])
    if chat_id != tg.owner_chat():
        return tg.answer_callback(cq["id"])
    action, _, post_id = (cq.get("data") or "").partition(":")
    post = store.get_post(post_id)
    msg_id = cq["message"]["message_id"]
    if not post:
        return tg.answer_callback(cq["id"], "That draft no longer exists.")
    if post["status"] != "pending":
        tg.answer_callback(cq["id"], f"Already {post['status']}.")
        return tg.edit(chat_id, msg_id, _draft_message(post))

    if action == "ap":
        try:
            publish(post)
        except Exception as e:
            tg.answer_callback(cq["id"], "Posting failed")
            return tg.send(f"❌ Bluesky post failed: {html.escape(str(e))[:300]}\nThe draft is still pending.")
        tg.answer_callback(cq["id"], "Posted!" if post["status"] == "posted" else "Approved")
        tg.edit(chat_id, msg_id, _draft_message(post))
    elif action == "sk":
        post["status"] = "skipped"
        post["decided"] = now_ist().isoformat(timespec="seconds")
        store.save_post(post)
        tg.answer_callback(cq["id"], "Skipped")
        tg.edit(chat_id, msg_id, _draft_message(post))
    elif action == "rg":
        tg.answer_callback(cq["id"], "Rewriting…")
        text, provider = writer.draft_for(post["date"])
        if text:
            post.update(text=text, provider=provider)
            store.save_post(post)
        tg.edit(chat_id, msg_id, _draft_message(post), buttons=_buttons(post["id"]))


# ---- messages -------------------------------------------------------------

def _on_message(msg):
    chat_id = str(msg["chat"]["id"])
    owner = tg.owner_chat()
    if not owner:
        tg.send(f"Hi! Your chat id is <code>{chat_id}</code>.\nPut <code>TELEGRAM_CHAT_ID={chat_id}</code> "
                "in the .env file, then restart the bot.", chat_id=chat_id)
        return
    if chat_id != owner:
        return  # strangers are ignored silently

    text = (msg.get("text") or "").strip()
    cmd, _, arg = text.partition(" ")
    cmd = cmd.split("@")[0].lower()
    arg = arg.strip()

    if cmd == "/log":
        what, hours = parse_log(arg)
        if not what:
            tg.send("Tell me what you did, e.g.\n<code>/log wired up the Bluesky poster 1.5h</code>")
            return
        was_logged = _stats()["logged_today"]
        store.add_entry(what, source="telegram", hours=hours)
        stats = _stats()
        hrs = f" ({hours:g}h)" if hours else ""
        extra = "" if was_logged else f"\n🔥 Day {stats['current']} — streak {'started' if stats['current'] == 1 else 'kept alive'}!"
        tg.send(f"✅ Logged{hrs}: {html.escape(what)}{extra}")
    elif cmd == "/streak":
        s = _stats()
        tg.send(f"{streak_line(s)}\n\nLongest: {s['longest']} days\nDays shipped: {s['total_days']}\n"
                f"Hours logged: {s['total_hours']:g}\nCommits counted: {s['total_commits']}")
    elif cmd == "/today":
        today = today_ist().isoformat()
        items = [e for e in store.entries() if e["date"] == today]
        if not items:
            tg.send("Nothing logged today yet.")
        else:
            lines = [f"{'💻' if e['source'] == 'github' else '✍️'} {html.escape(e['text'])}"
                     + (f" ({e['hours']:g}h)" if e.get("hours") else "") for e in items]
            tg.send(f"<b>Today ({today})</b>\n" + "\n".join(lines))
    elif cmd == "/undo":
        mine = [e for e in store.entries() if e["source"] == "telegram"]
        if not mine:
            tg.send("Nothing to undo.")
        else:
            store.remove_entry(mine[-1]["id"])
            tg.send(f"🗑 Removed: {html.escape(mine[-1]['text'])}\n{streak_line(_stats())}")
    elif cmd == "/draft":
        tg.send("✍️ Writing today's update…")
        create_draft()
    elif cmd in ("/start", "/help"):
        tg.send(HELP + "\n" + streak_line(_stats()))
    else:
        tg.send("To log work, start with /log — e.g. <code>/log fixed the heatmap colours 1h</code>\n/help for more.")


def handle_update(update):
    if "callback_query" in update:
        _on_callback(update["callback_query"])
    elif "message" in update:
        _on_message(update["message"])


def poll_once(wait=0):
    """Process pending Telegram updates; returns how many were handled."""
    updates = tg.get_updates(store.state().get("tg_offset"), wait=wait)
    for upd in updates:
        try:
            handle_update(upd)
        except Exception as e:
            print(f"[bot] update {upd.get('update_id')} failed: {e}")
        store.update_state(tg_offset=upd["update_id"] + 1)
    return len(updates)
