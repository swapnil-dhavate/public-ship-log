"""Command line: python -m shiplog <command>

  tick     everything GitHub Actions runs every 15 min: Telegram + commits + due jobs + page data
  poll     process waiting Telegram messages/button presses once
  sync     pull new GitHub commits
  draft    write today's post draft and send it to Telegram  (--date YYYY-MM-DD)
  remind   run the reminder/draft checks now (they only fire when due)
  build    regenerate docs/data.json
  status   print streak stats
  chatid   print chat ids that have messaged the bot (to fill TELEGRAM_CHAT_ID)
"""
import json
import sys

from . import bot, github_sync, jobs, site, store, tg
from .streak import compute


def _safe(label, fn):
    try:
        return fn()
    except Exception as e:  # keep the rest of the tick going
        print(f"[{label}] failed: {e}")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # emoji on Windows consoles
    cmd = argv[0] if argv else "help"
    if cmd == "tick":
        if tg.token():
            print("telegram updates:", _safe("poll", bot.poll_once))
        print("new commits:", _safe("sync", github_sync.sync))
        if tg.token() and tg.owner_chat():
            print("due jobs:", _safe("jobs", jobs.run_due_jobs))
        print("page data changed:", site.build())
    elif cmd == "poll":
        print("handled", bot.poll_once())
    elif cmd == "sync":
        print("new commits:", github_sync.sync(verbose=True))
    elif cmd == "draft":
        day = argv[argv.index("--date") + 1] if "--date" in argv else None
        post = bot.create_draft(day)
        print(json.dumps(post, indent=2, ensure_ascii=False) if post else "nothing logged")
    elif cmd == "remind":
        print("ran:", jobs.run_due_jobs())
    elif cmd == "build":
        print("page data changed:", site.build())
    elif cmd == "status":
        print(json.dumps(compute(store.entries()), indent=2))
    elif cmd == "chatid":
        for u in tg.get_updates():
            chat = (u.get("message") or {}).get("chat")
            if chat:
                print(chat["id"], chat.get("username") or chat.get("first_name"))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
