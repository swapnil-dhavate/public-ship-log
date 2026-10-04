# Public Ship Log

A public tracker for the days you work on your projects. You tell a Telegram bot what you did,
and it also counts your GitHub commits. It keeps a streak, shows everything on a public web page,
and every night writes a short update post. You approve it in Telegram before it goes to Bluesky.
If you haven't logged anything by 9 PM (India time), it reminds you.

Everything runs on free tools: Python, Telegram, GitHub Actions, GitHub Pages, Gemini/Groq and Bluesky.

**What the project covers**
- **No dependencies:** plain Python standard library only. The HTTP clients for Telegram, GitHub, Gemini, Groq and
  Bluesky (AT Protocol) are written by hand.
- **Serverless, $0 to run:** GitHub Actions runs the bot on a schedule, the data lives as JSON in the repo, and
  GitHub Pages hosts the page.
- **Human approval before publishing:** AI writes the post, but nothing goes public until you press Approve in Telegram.
- **AI fallback:** Gemini first, then Groq, then a plain template, so a draft always gets written.
- **Scheduled jobs that are safe to re-run:** the reminder and the draft check the time on every run, so a late or
  repeated GitHub run never sends twice.
- **Honest streak:** bot and CI commits don't count. Commits to private repos are shown without details.

---

## How it works

1. **You log work.** Send the bot `/log fixed the login bug 1.5h`. The hours are optional.
2. **Commits count too.** Commits you push to the repos listed in `config.json` are added on their own.
   Bot and CI commits are ignored.
3. **The streak is counted in India time (IST).** Any day with at least one entry counts.
   Your streak stays alive until midnight IST.
4. **Reminder at 9 PM IST.** If nothing is logged by then, the bot warns you that your streak is at risk.
5. **Draft post at 10:30 PM IST.** If you logged something that day, AI turns your notes and commits into a short
   post, for example *"Day 12 of shipping daily 🚢 …"*. It comes to Telegram with three buttons:
   **Approve & post**, **Skip** and **Rewrite**. Nothing is posted until you press Approve.
   You can also ask for a draft at any time with `/draft`.
6. **Public page.** The page shows your streak, a 12-month calendar heatmap and a timeline of every day.

## Bot commands

| Command | What it does |
|---|---|
| `/log what you did [2h]` | Log work for today. Hours can be written as `2h`, `1.5 hours` or `45m`. |
| `/streak` | Current streak, longest streak, total days and hours |
| `/today` | Everything logged today |
| `/undo` | Remove your last `/log` entry |
| `/draft` | Write today's post now and send it for approval |

The bot only answers you. It ignores messages from everyone else.

---

## Setup, step by step

### 1. Make a new Telegram bot (just for this project)
In Telegram, open **@BotFather** → `/newbot` → pick a name → copy the token.

### 2. Create your `.env` file
Copy `.env.example` to `.env` and fill it in:

- `TELEGRAM_BOT_TOKEN`: the token from step 1.
- `TELEGRAM_CHAT_ID`: leave it empty at first. Run the bot (step 3), send it any message, and it replies with
  your chat id. Paste that in and restart.
- `GEMINI_API_KEY`: free key from https://aistudio.google.com/apikey
- `GROQ_API_KEY`: free key from https://console.groq.com/keys. This is the backup writer. If both AI services
  fail, a simple template is used, so you always get a draft.
- `GH_TOKEN`: only needed for private repos. Use a fine-grained GitHub token with read-only "Contents" access.
- `BLUESKY_HANDLE` / `BLUESKY_APP_PASSWORD`: use an **app password** (Bluesky → Settings → Privacy and security →
  App passwords), not your real password.
- `BLUESKY_DRY_RUN=1`: while this is 1, pressing Approve does **not** really post. Change it to `0` when you're
  ready to go public.

`.env` is listed in `.gitignore`, so it is never committed.

### 3. Run it on your PC
```powershell
cd "D:\Swapnil\Personel Project\Weekend AI Projects\09-public-ship-log"
C:\Python314\python dev.py
```
Open **http://localhost:8107** to see the page. The bot replies straight away while this window is open.
Nothing needs installing because the project uses only built-in Python.

Options: `--no-schedule` turns off the 9 PM reminder and nightly draft on your PC. `--page-only` shows just the page.

### 4. Choose which repos count (`config.json`)
```json
"github_repos": ["swapnil-dhavate/some-repo", "swapnil-dhavate/another-repo"],
"github_author": "swapnil-dhavate"
```
`github_author` makes sure only *your* commits count. The first sync looks back `github_backfill_days` days.
Commits to **private** repos show as "Pushed a commit to a private project" with no name or message, because the
log is public. Set `redact_private_repos` to `false` if you don't mind showing them.

Other settings in `config.json`:

- `title` and `subtitle`: the page heading.
- `reminder_time_ist` and `draft_time_ist`: when the reminder and the nightly draft are sent.
- `hashtags`: hashtags added to each post.
- `site_url`: your page link, added to posts when there's room.
- `links`: your profile links, as `[{"label": "Bluesky", "url": "..."}]`.
- `approval_required`: set this to `false` later if you want posts to go out without asking you first.

### 5. Put it online (GitHub Actions + GitHub Pages)
1. Create a **public** GitHub repo and push this folder. GitHub Pages is free for public repos.
   Remember that everything in `data/` is public, because that's the point of the project.
2. Repo → **Settings → Secrets and variables → Actions**:
   - **Secrets:** add `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`, `GROQ_API_KEY`,
     `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD`. Add `GH_TOKEN` too if you track private repos.
   - **Variables:** add `BLUESKY_DRY_RUN` = `0` when you want real posts. The default is dry-run.
3. Repo → **Settings → Pages** → Source: **GitHub Actions**.
4. Repo → **Actions** → *ship-log* → **Run workflow** once to start it.

After that the workflow runs **every 15 minutes**. Each run does the following:

- answers your Telegram messages and button presses
- picks up new commits
- sends the reminder or draft when it's due
- updates the page

On Actions, the bot answers within about 15 minutes instead of instantly. GitHub's timer can also run a few
minutes late.

> ⚠️ Once Actions is running, **stop running `dev.py` with the bot on.** Otherwise your PC and GitHub both read
> the same Telegram messages and split them between them. To just look at the page locally, run
> `git pull` and then `C:\Python314\python dev.py --page-only`.

---

## Handy commands
```powershell
C:\Python314\python -m shiplog status   # streak numbers
C:\Python314\python -m shiplog sync     # pull commits now
C:\Python314\python -m shiplog draft    # write today's draft and send it to Telegram
C:\Python314\python -m shiplog tick     # what GitHub Actions runs every 15 min
C:\Python314\python -m unittest discover -s tests -t .   # run the tests
```

## Where things live
| Path | What's in it |
|---|---|
| `data/entries.json` | Every log entry, from Telegram and GitHub |
| `data/posts.json` | Drafts and their status: pending, posted, approved or skipped |
| `data/state.json` | Bookkeeping: last Telegram message read, last reminder, last commit sync |
| `docs/index.html` | The public page |
| `docs/data.json` | Page data, rebuilt from `data/` |
| `shiplog/` | The code: `bot.py` (Telegram), `streak.py`, `github_sync.py`, `writer.py` (AI), `bluesky.py`, `jobs.py` (reminder and draft timing), `site.py` |
| `.github/workflows/shiplog.yml` | The 15-minute GitHub Actions job |
