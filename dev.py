"""Local mode: serve the page on http://localhost:8107 and run the Telegram bot live.

  C:\\Python314\\python dev.py                 # page + bot + 9 PM reminder / nightly draft
  C:\\Python314\\python dev.py --no-schedule   # page + bot only
  C:\\Python314\\python dev.py --page-only     # just the page

Don't run this while the GitHub Actions workflow is active — both would answer the bot.
"""
import functools
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from shiplog import bot, env, github_sync, jobs, site, tg

PORT = 8107
SYNC_EVERY = 600  # seconds between GitHub commit checks


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def serve():
    handler = functools.partial(Handler, directory=str(env.DOCS_DIR))
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()


def safe(label, fn):
    try:
        return fn()
    except Exception as e:
        print(f"[{label}] {e}")


def main(args):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # emoji on Windows consoles
    site.build()
    threading.Thread(target=serve, daemon=True).start()
    print(f"Page:  http://localhost:{PORT}")

    bot_on = "--page-only" not in args and bool(tg.token())
    schedule_on = bot_on and "--no-schedule" not in args and bool(tg.owner_chat())
    if not bot_on:
        print("Bot:   off" + ("" if tg.token() else " (TELEGRAM_BOT_TOKEN missing in .env)"))
    else:
        print("Bot:   listening" + ("" if tg.owner_chat() else " — send it any message to learn your chat id"))
        print("Jobs:  " + ("9 PM reminder + nightly draft on" if schedule_on else "off"))
    print("Ctrl+C to stop.\n")

    last_sync = 0
    try:
        while True:
            if time.time() - last_sync > SYNC_EVERY:
                n = safe("github", github_sync.sync)
                if n:
                    print(f"[github] {n} new commit(s) logged")
                last_sync = time.time()
            if bot_on:
                n = safe("bot", lambda: bot.poll_once(wait=25))
                if n is None:
                    time.sleep(5)  # network hiccup — don't spin
                elif n:
                    print(f"[bot] handled {n} update(s)")
                if schedule_on:
                    ran = safe("jobs", jobs.run_due_jobs)
                    if ran:
                        print(f"[jobs] {ran}")
            else:
                time.sleep(5)
            safe("build", site.build)
    except KeyboardInterrupt:
        print("bye")


if __name__ == "__main__":
    main(sys.argv[1:])
