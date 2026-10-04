// Builds the two user manuals (Overview + Complete) as HTML, in the same visual
// format as the other project manuals. Sections tagged "both" appear in both
// editions; "full" only in the Complete edition.
// Run: node docs/manual/build-docs.mjs   (then print to PDF: powershell -File docs\manual\print-pdfs.ps1)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const css = fs.readFileSync(path.join(here, "manual-style.css"), "utf8");

const PAGE = "https://swapnil-dhavate.github.io/public-ship-log/";
const REPO = "https://github.com/swapnil-dhavate/public-ship-log";
const FOLDER = String.raw`D:\Swapnil\Personel Project\Weekend AI Projects\09-public-ship-log`;
const PY = String.raw`C:\Python314\python`;
const PUBLISH = `cd "${FOLDER}"; git pull --rebase; git add -A; git commit -m "describe the change"; git push`;

const diagram = `
<figure>
<svg viewBox="0 0 900 400" role="img" aria-label="You send /log messages and button presses in Telegram, and push commits to your GitHub repos. Every 15 minutes GitHub Actions runs the tick: it reads Telegram, pulls new commits, sends the reminder or draft when due, and rebuilds the page data. Entries, drafts and state are saved as JSON in the data folder and committed back to the repo. Drafts are written by Gemini, then Groq, then a template. Approved posts go to Bluesky. The page is deployed to GitHub Pages." style="width:100%;max-width:900px;height:auto;">
  <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><polygon points="0,0 7,3 0,6" fill="#0a3d7a"/></marker></defs>
  <style>
    .n{fill:#eaf3ff;stroke:#0a66c2;stroke-width:1.4}.n2{fill:#0a3d7a;stroke:#0a3d7a}
    .t{font-size:12.5px;fill:#0a2647;font-weight:700}.t2{font-size:12.5px;fill:#fff;font-weight:700}
    .s{font-size:9.5px;fill:#33465e}.s2{font-size:9.5px;fill:#cfe3fa}
    .e{stroke:#0a3d7a;stroke-width:1.3;fill:none;marker-end:url(#ah)}
  </style>
  <rect class="n" x="20" y="10" width="400" height="58" rx="8"/>
  <text class="t" x="220" y="34" text-anchor="middle">You, in Telegram</text>
  <text class="s" x="220" y="50" text-anchor="middle">/log fixed the login bug 1.5h · Approve / Skip / Rewrite</text>
  <rect class="n" x="480" y="10" width="400" height="58" rx="8"/>
  <text class="t" x="680" y="34" text-anchor="middle">Your GitHub repos</text>
  <text class="s" x="680" y="50" text-anchor="middle">listed in config.json → your own commits count</text>
  <line class="e" x1="220" y1="68" x2="220" y2="96"/>
  <line class="e" x1="680" y1="68" x2="680" y2="96"/>
  <rect class="n2" x="20" y="100" width="860" height="150" rx="10"/>
  <text class="t2" x="450" y="122" text-anchor="middle">The "tick" (python -m shiplog tick) — GitHub Actions every 15 min, or dev.py on your PC</text>
  <rect x="34" y="136" width="196" height="100" rx="7" fill="#123f73" stroke="#7fc4ff"/>
  <text class="t2" x="132" y="160" text-anchor="middle">1. Telegram bot</text>
  <text class="s2" x="132" y="178" text-anchor="middle">reads new messages</text>
  <text class="s2" x="132" y="192" text-anchor="middle">and button presses</text>
  <text class="s2" x="132" y="206" text-anchor="middle">answers only you</text>
  <rect x="244" y="136" width="196" height="100" rx="7" fill="#123f73" stroke="#7fc4ff"/>
  <text class="t2" x="342" y="160" text-anchor="middle">2. Commit sync</text>
  <text class="s2" x="342" y="178" text-anchor="middle">new commits since last sync</text>
  <text class="s2" x="342" y="192" text-anchor="middle">skips bot / CI / merge commits</text>
  <text class="s2" x="342" y="206" text-anchor="middle">private repos shown blank</text>
  <rect x="454" y="136" width="196" height="100" rx="7" fill="#123f73" stroke="#7fc4ff"/>
  <text class="t2" x="552" y="160" text-anchor="middle">3. Due jobs (IST)</text>
  <text class="s2" x="552" y="178" text-anchor="middle">21:00 streak reminder</text>
  <text class="s2" x="552" y="192" text-anchor="middle">22:30 draft for approval</text>
  <text class="s2" x="552" y="206" text-anchor="middle">each fires once a day</text>
  <rect x="664" y="136" width="202" height="100" rx="7" fill="#123f73" stroke="#7fc4ff"/>
  <text class="t2" x="765" y="160" text-anchor="middle">4. Page build</text>
  <text class="s2" x="765" y="178" text-anchor="middle">streak numbers</text>
  <text class="s2" x="765" y="192" text-anchor="middle">heatmap + timeline</text>
  <text class="s2" x="765" y="206" text-anchor="middle">→ docs/data.json</text>
  <path class="e" d="M230,186 L242,186"/><path class="e" d="M440,186 L452,186"/><path class="e" d="M650,186 L662,186"/>
  <line class="e" x1="132" y1="250" x2="132" y2="280"/>
  <line class="e" x1="342" y1="250" x2="342" y2="280"/>
  <line class="e" x1="552" y1="250" x2="552" y2="280"/>
  <line class="e" x1="765" y1="250" x2="765" y2="280"/>
  <rect class="n" x="20" y="284" width="205" height="62" rx="8"/>
  <text class="t" x="122" y="308" text-anchor="middle">data\\*.json</text>
  <text class="s" x="122" y="324" text-anchor="middle">entries · posts · state</text>
  <rect class="n" x="240" y="284" width="205" height="62" rx="8"/>
  <text class="t" x="342" y="308" text-anchor="middle">AI writer</text>
  <text class="s" x="342" y="324" text-anchor="middle">Gemini → Groq → template</text>
  <rect class="n" x="455" y="284" width="205" height="62" rx="8"/>
  <text class="t" x="557" y="308" text-anchor="middle">Bluesky</text>
  <text class="s" x="557" y="324" text-anchor="middle">only after you press Approve</text>
  <rect class="n" x="675" y="284" width="205" height="62" rx="8"/>
  <text class="t" x="777" y="308" text-anchor="middle">GitHub Pages</text>
  <text class="s" x="777" y="324" text-anchor="middle">docs/index.html + data.json</text>
  <rect class="n2" x="20" y="362" width="860" height="32" rx="8"/>
  <text class="t2" x="450" y="383" text-anchor="middle">GitHub (swapnil-dhavate/public-ship-log): the workflow commits data back, then deploys the page</text>
</svg>
<figcaption>How a note or a commit becomes a streak, a heatmap square and (after approval) a post.</figcaption>
</figure>`;

const S = []; // { ed: "both" | "full", title, toc, body }
const add = (ed, title, toc, body) => S.push({ ed, title, toc, body });

add("both", "What Is This System?", "Plain-English introduction", `
<p class="lead">In one sentence: <strong>you tell a Telegram bot what you worked on, it also counts your GitHub commits, keeps a daily streak on a public web page, and every night writes a short post that goes to Bluesky only if you approve it.</strong></p>
<h2>What it does</h2>
<ul>
  <li><strong>Logs your work:</strong> send <code>/log fixed the login bug 1.5h</code>. Hours are optional.</li>
  <li><strong>Counts commits too:</strong> commits you push to the repos listed in <code>config.json</code> are added on their own. Bot and CI commits don't count.</li>
  <li><strong>Keeps a streak in India time (IST):</strong> any day with at least one entry counts. The streak stays alive until midnight IST.</li>
  <li><strong>Reminds you at 9 PM IST</strong> if nothing is logged yet and your streak is at risk.</li>
  <li><strong>Drafts a post at 10:30 PM IST:</strong> AI turns the day's notes and commits into a short update, e.g. <em>"Day 12 of shipping daily 🚢 …"</em>. You get <span class="click">Approve &amp; post</span>, <span class="click">Skip</span> and <span class="click">Rewrite</span> buttons.</li>
  <li><strong>Shows it publicly:</strong> a page with your streak, a 12-month heatmap and a timeline of every day.</li>
</ul>
<h2>Where it runs</h2>
<table>
<tr><th></th><th>Online (normal)</th><th>On your PC (testing)</th></tr>
<tr><td><strong>Runs on</strong></td><td>GitHub Actions, every 15 minutes</td><td><code>${PY} dev.py</code></td></tr>
<tr><td><strong>Page</strong></td><td><code>swapnil-dhavate.github.io/public-ship-log</code></td><td><code>http://localhost:8107</code></td></tr>
<tr><td><strong>Bot replies</strong></td><td>Within about 15 minutes</td><td>Straight away</td></tr>
</table>
<div class="box warn"><span class="box-title">Current status (4 October 2026)</span>
Built and tested offline (10 tests pass). Not live yet: it still needs its own Telegram bot token, Gemini and Groq keys, the list of repos to track, Bluesky details, and GitHub Pages switched on. The checklist is in Section 7.1.</div>
<h2>What it costs</h2>
<p><strong>Nothing: ₹0.</strong> Every service used has a free tier, and GitHub Actions and Pages are free for public repos.</p>`);

add("both", "How the Streak Is Counted", "The core idea explained simply", `
<p class="lead">The rule is simple: <strong>a day counts if it has at least one entry, and the streak is the number of days in a row, counted in India Standard Time.</strong></p>
<h2>The rules</h2>
<ol class="steps">
  <li><strong>One entry is enough.</strong> A <code>/log</code> message or one commit makes the day count. Five entries in one day still count as one day.</li>
  <li><strong>Days are IST days.</strong> GitHub stores commit times in UTC. The app moves them to IST first, so a commit at 19:00 UTC on 3 Oct counts for <strong>4 Oct</strong> (00:30 IST).</li>
  <li><strong>Today is a grace day.</strong> If you haven't logged yet today, yesterday's streak is still shown, marked "at risk", until midnight IST.</li>
  <li><strong>A missed day resets it.</strong> The current streak goes back to 0. Your longest streak is kept.</li>
  <li><strong>Only real work counts.</strong> Commits from bots (names ending in <code>[bot]</code>, GitHub Actions, Dependabot), merge commits and messages with <code>[skip ci]</code> are ignored.</li>
</ol>
<h2>A worked example (today is 4 October)</h2>
<table>
<tr><th>Date</th><th>Entries</th><th>Counts?</th></tr>
<tr><td>1 Oct</td><td>none</td><td>✘ gap</td></tr>
<tr><td>2 Oct</td><td><code>/log wrote the streak tests 2h</code></td><td>✔</td></tr>
<tr><td>3 Oct</td><td>2 commits to a tracked repo</td><td>✔ (one day)</td></tr>
<tr><td>4 Oct, 8 PM</td><td>nothing yet</td><td>grace day</td></tr>
</table>
<p>At 8 PM the page shows a <strong>2-day streak, at risk</strong>. At 9 PM IST the bot sends <em>"Streak at risk!"</em>. If you send <code>/log fixed the heatmap colours 1h</code> before midnight, the reply is <em>"✅ Logged (1h) … 🔥 Day 3 — streak kept alive!"</em>.</p>
<div class="box info"><span class="box-title">Hours are optional</span>
<code>2h</code>, <code>1.5 hours</code> and <code>45m</code> are read as hours (0.75 for 45m). Numbers that aren't hours, like "read 3 chapters", stay in the text.</div>`);

add("both", "System Architecture", "The full picture, with a diagram", `
<p class="lead">Every piece involved and how they connect. Each tool is explained in Section 6, and every technical word is in the Glossary.</p>
${diagram}
<h2>In words</h2>
<ol>
  <li>You send messages to the bot and push code to your repos as usual.</li>
  <li>Every 15 minutes GitHub Actions starts a small Python job, the <strong>tick</strong>. It reads new Telegram messages, pulls new commits, sends the reminder or draft if it's time, and rebuilds the page data.</li>
  <li>Everything is saved as JSON files in <code>data\\</code>. The job commits them back to the repo, so the repo itself is the database.</li>
  <li>Drafts are written by <strong>Gemini</strong>; if that fails, <strong>Groq</strong>; if both fail, a plain template.</li>
  <li>When you press Approve, the post goes to <strong>Bluesky</strong>. The page is redeployed to <strong>GitHub Pages</strong> whenever the data changed.</li>
</ol>`);

add("both", "How It Works, Step by Step", "From a note to a public post", `
<h2>4.1 — One tick (every 15 minutes)</h2>
<ol class="steps">
  <li><strong>Telegram:</strong> fetch messages and button presses since the last one handled (the position is saved in <code>data\\state.json</code>).</li>
  <li><strong>Commits:</strong> ask GitHub for commits since the last sync, minus 2 days of overlap to catch late pushes. Already-known commits are skipped.</li>
  <li><strong>Jobs:</strong> after 21:00 IST with nothing logged → reminder (once a day). After 22:30 IST with something logged and no draft yet → draft.</li>
  <li><strong>Page:</strong> rebuild <code>docs\\data.json</code>. If anything changed, commit and deploy the page.</li>
</ol>
<h2>4.2 — Writing the draft</h2>
<ol class="steps">
  <li>The day's notes and commits are listed for the AI, with the total hours.</li>
  <li>The AI is told: one update, at most 200 characters, first person, concrete, no hashtags, no hype words.</li>
  <li>The app adds <em>"Day N of shipping daily 🚢"</em> in front, then <code>#buildinpublic</code> and the page link if they fit in Bluesky's 300-character limit.</li>
</ol>
<h2>4.3 — Approving it</h2>
<table>
<tr><th>Button</th><th>What happens</th></tr>
<tr><td>✅ Approve &amp; post</td><td>Posts to Bluesky and shows the link. In dry-run it is only marked "approved".</td></tr>
<tr><td>⏭ Skip</td><td>Marked skipped. Nothing is posted. The day still counts in the streak.</td></tr>
<tr><td>🔄 Rewrite</td><td>Asks the AI again and replaces the text in the same message.</td></tr>
</table>
<p>If posting fails, the bot says why and the draft stays pending, so you can press Approve again.</p>`);

add("both", "Layers & Who Does What", "Every building block explained", `
<table>
<tr><th>Layer</th><th>File</th><th>Its job</th></tr>
<tr><td><strong>1. Commands</strong></td><td><code>shiplog\\__main__.py</code></td><td><code>tick</code>, <code>sync</code>, <code>draft</code>, <code>status</code> and other commands.</td></tr>
<tr><td><strong>2. Bot</strong></td><td><code>shiplog\\bot.py</code></td><td>Telegram commands, hours parsing, draft buttons, publishing.</td></tr>
<tr><td><strong>3. Telegram client</strong></td><td><code>shiplog\\tg.py</code></td><td>Send, edit and fetch Telegram messages.</td></tr>
<tr><td><strong>4. Streak</strong></td><td><code>shiplog\\streak.py</code></td><td>IST clock and the streak numbers.</td></tr>
<tr><td><strong>5. Commits</strong></td><td><code>shiplog\\github_sync.py</code></td><td>Pulls commits, skips bots, hides private repo details.</td></tr>
<tr><td><strong>6. Writer</strong></td><td><code>shiplog\\writer.py</code></td><td>Gemini → Groq → template; adds day number, tags, link.</td></tr>
<tr><td><strong>7. Publisher</strong></td><td><code>shiplog\\bluesky.py</code></td><td>Logs in with the app password, posts, makes links and tags clickable.</td></tr>
<tr><td><strong>8. Timed jobs</strong></td><td><code>shiplog\\jobs.py</code></td><td>The 9 PM reminder and the 10:30 PM draft.</td></tr>
<tr><td><strong>9. Storage</strong></td><td><code>shiplog\\store.py</code></td><td>Reads and safely writes the JSON files in <code>data\\</code>.</td></tr>
<tr><td><strong>10. Page data</strong></td><td><code>shiplog\\site.py</code></td><td>Builds <code>docs\\data.json</code>; rewrites it only when something real changed.</td></tr>
<tr><td><strong>11. Settings</strong></td><td><code>shiplog\\env.py</code>, <code>config.json</code>, <code>.env</code></td><td>Where every setting and secret comes from.</td></tr>
<tr><td><strong>12. Public page</strong></td><td><code>docs\\index.html</code></td><td>Streak, heatmap and timeline; reads <code>data.json</code>.</td></tr>
<tr><td><strong>13. Local mode</strong></td><td><code>dev.py</code></td><td>Page on port 8107 + live bot + jobs on your PC.</td></tr>
<tr><td><strong>14. Schedule</strong></td><td><code>.github\\workflows\\shiplog.yml</code></td><td>Runs the tick every 15 min, commits data, deploys the page.</td></tr>
<tr><td><strong>15. Checks</strong></td><td><code>tests\\test_core.py</code></td><td>10 automatic tests.</td></tr>
</table>`);

add("both", "Tools Used & Their Cost", "Full list, all free", `
<table>
<tr><th>Tool</th><th>Used for</th><th>Cost</th></tr>
<tr><td><strong>Python 3</strong> <span class="tag free">FREE</span></td><td>All the code, standard library only (3.14 on the PC, 3.12 on Actions)</td><td>Open-source</td></tr>
<tr><td><strong>Telegram Bot API</strong> <span class="tag free">FREE</span></td><td>Logging, reminders, approval buttons</td><td>Free</td></tr>
<tr><td><strong>GitHub REST API</strong> <span class="tag free">FREE</span></td><td>Reading your commits</td><td>Free</td></tr>
<tr><td><strong>GitHub Actions</strong> <span class="tag free">FREE</span></td><td>Running the tick every 15 minutes</td><td>Free for public repos</td></tr>
<tr><td><strong>GitHub Pages</strong> <span class="tag free">FREE</span></td><td>Hosting the public page</td><td>Free for public repos</td></tr>
<tr><td><strong>Gemini (gemini-2.5-flash)</strong> <span class="tag free">FREE</span></td><td>Writing drafts</td><td>Free tier</td></tr>
<tr><td><strong>Groq (llama-3.3-70b-versatile)</strong> <span class="tag free">FREE</span></td><td>Backup draft writer</td><td>Free tier</td></tr>
<tr><td><strong>Bluesky</strong> <span class="tag free">FREE</span></td><td>Publishing approved posts</td><td>Free</td></tr>
</table>
<div class="box cost"><span class="box-title">Total: ₹0 a month</span>
One draft a day uses a tiny part of the free AI limits. No card is attached to any of these services.</div>
<h2>Why these choices?</h2>
<ul>
  <li><strong>No packages:</strong> nothing to install or update, and nothing breaks when a library changes.</li>
  <li><strong>GitHub Actions instead of a server:</strong> free and always on. The cost is a slower bot (up to 15 minutes).</li>
  <li><strong>JSON in the repo instead of a database:</strong> the log is public anyway, and git keeps the full history.</li>
  <li><strong>Bluesky:</strong> its API is free and allows posting with an app password. X and LinkedIn don't offer that for free.</li>
</ul>`);

add("both", "Daily Usage Guide (SOP)", "Setup checklist and daily routine", `
<h2>7.1 — First-time setup checklist (still pending)</h2>
<table>
<tr><th>#</th><th>Item</th><th>Where it goes</th></tr>
<tr><td>1</td><td>New Telegram bot: <strong>@BotFather</strong> → <code>/newbot</code> → copy the token</td><td><code>TELEGRAM_BOT_TOKEN</code></td></tr>
<tr><td>2</td><td>Your chat id: run <code>dev.py</code>, message the bot, it replies with the id</td><td><code>TELEGRAM_CHAT_ID</code></td></tr>
<tr><td>3</td><td>Gemini key (aistudio.google.com/apikey) and Groq key (console.groq.com/keys)</td><td><code>GEMINI_API_KEY</code>, <code>GROQ_API_KEY</code></td></tr>
<tr><td>4</td><td>Repos to track and your GitHub username</td><td><code>config.json</code>: <code>github_repos</code>, <code>github_author</code></td></tr>
<tr><td>5</td><td>Bluesky handle + app password (Settings → Privacy and security → App passwords)</td><td><code>BLUESKY_HANDLE</code>, <code>BLUESKY_APP_PASSWORD</code></td></tr>
<tr><td>6</td><td>Optional: read-only fine-grained token, only for private repos</td><td><code>GH_TOKEN</code></td></tr>
<tr><td>7</td><td>Copy items 1–6 into repo <strong>Settings → Secrets and variables → Actions</strong></td><td>Secrets</td></tr>
<tr><td>8</td><td>Repo <strong>Settings → Pages</strong> → Source: <strong>GitHub Actions</strong></td><td>GitHub</td></tr>
<tr><td>9</td><td><strong>Actions → ship-log → Run workflow</strong> once; then stop running <code>dev.py</code></td><td>GitHub</td></tr>
<tr><td>10</td><td>When happy: variable <code>BLUESKY_DRY_RUN</code> = <code>0</code>; set <code>site_url</code></td><td>Variables, <code>config.json</code></td></tr>
</table>
<p>For testing on the PC, items 1–6 go in a <code>.env</code> file (copy <code>.env.example</code>).</p>
<h2>7.2 — Every day</h2>
<ol class="steps">
  <li>Work on something. Push commits as usual; they count on their own.</li>
  <li>For work without commits (design, reading, writing), send <code>/log what you did 1h</code>.</li>
  <li>At 9 PM IST, a reminder comes only if nothing is logged.</li>
  <li>At 10:30 PM IST, read the draft. Press <span class="click">Approve &amp; post</span>, <span class="click">Rewrite</span> or <span class="click">Skip</span>.</li>
</ol>
<div class="box tip"><span class="box-title">Handy commands in Telegram</span>
<code>/streak</code> numbers · <code>/today</code> what's logged · <code>/undo</code> remove your last /log · <code>/draft</code> write today's post now.</div>`);

add("full", "How to Make Changes", "Every change, explained", `
<p class="lead">Most changes are settings in <code>config.json</code>. Every change follows the same steps: <strong>edit, test, then push to GitHub.</strong> The next tick uses the new version. You can also just ask Claude to do the edit.</p>
<h2>8.1 — Common changes</h2>
<table>
<tr><th>To change…</th><th>Edit this</th></tr>
<tr><td>Page heading and text</td><td><code>title</code>, <code>subtitle</code> in <code>config.json</code></td></tr>
<tr><td>Repos that count</td><td><code>github_repos</code>, e.g. <code>["swapnil-dhavate/some-repo"]</code></td></tr>
<tr><td>Reminder and draft times</td><td><code>reminder_time_ist</code> (21:00), <code>draft_time_ist</code> (22:30)</td></tr>
<tr><td>Hashtags and page link in posts</td><td><code>hashtags</code>, <code>site_url</code></td></tr>
<tr><td>Profile links on the page</td><td><code>links</code>: <code>[{"label": "Bluesky", "url": "..."}]</code></td></tr>
<tr><td>Show private repo commit messages</td><td><code>redact_private_repos</code>: <code>false</code></td></tr>
<tr><td>Commit messages to ignore</td><td><code>ignore_commits_matching</code></td></tr>
<tr><td>Tone of the posts</td><td><code>SYSTEM</code> text in <code>shiplog\\writer.py</code></td></tr>
<tr><td>Page look</td><td><code>docs\\index.html</code></td></tr>
</table>
<h2>8.2 — Check before publishing</h2>
<p>In a terminal, in the project folder:</p>
<p><code>${PY} -m unittest discover -s tests -t .</code></p>
<p>It should end with <strong>"Ran 10 tests … OK"</strong>. To see the page: <code>${PY} dev.py --page-only</code> → <code>http://localhost:8107</code>.</p>
<h2>8.3 — Publish</h2>
<p>Open VS Code → <span class="click">Terminal → New Terminal</span>, paste this line and press Enter:</p>
<p><code style="font-size:10px;word-break:break-all;">${PUBLISH}</code></p>
<div class="box warn"><span class="box-title">Always pull first</span>
The workflow commits data to the repo every time something changes. <code>git pull --rebase</code> brings those commits down first, so your push isn't rejected. Never edit <code>data\\*.json</code> while Actions is running unless you pull right before and push right after.</div>`);

add("full", "Adding Features & Growing", "Extending the system", `
<h2>9.1 — Track another repo</h2>
<p>Add <code>"owner/repo"</code> to <code>github_repos</code> in <code>config.json</code> and push. The very first sync looks back <code>github_backfill_days</code> (14) days. After that, each sync looks back only 2 days before the previous one, so a repo added later doesn't get its older history.</p>
<h2>9.2 — Go live on Bluesky</h2>
<ol class="steps">
  <li>Test with <code>BLUESKY_DRY_RUN=1</code> (the default): Approve only marks the draft "approved".</li>
  <li>When the drafts look right, add the Actions variable <code>BLUESKY_DRY_RUN</code> = <code>0</code>.</li>
  <li>Set <code>site_url</code> to the Pages address so posts link to your heatmap.</li>
</ol>
<h2>9.3 — Post without asking (optional)</h2>
<p>Set <code>approval_required</code> to <code>false</code>. The nightly draft is then posted straight away and you only get a copy. Keep it <code>true</code> until you trust the drafts.</p>
<h2>9.4 — Backfill a missed draft</h2>
<p><code>${PY} -m shiplog draft --date 2026-10-03</code> writes and sends a draft for that IST date.</p>
<h2>9.5 — Ideas for later</h2>
<ul>
  <li>Post to Mastodon or LinkedIn as well as Bluesky.</li>
  <li>A weekly recap post every Sunday.</li>
  <li>A webhook (for example a free Cloudflare Worker) so the bot replies instantly instead of every 15 minutes.</li>
  <li>Tag entries by project and filter the heatmap.</li>
  <li>An <code>/edit</code> command to fix a logged entry.</li>
</ul>`);

add("full", "Renewing & Maintaining", "What needs periodic attention", `
<p class="lead">Short answer: <strong>very little.</strong> Nothing is paid. These are the things that can expire or change.</p>
<table>
<tr><th>Item</th><th>Lifetime</th><th>What to do</th></tr>
<tr><td>Telegram bot token</td><td>Doesn't expire</td><td>If it leaks: @BotFather → <code>/revoke</code>, then update the secret.</td></tr>
<tr><td>Gemini / Groq keys</td><td>Until revoked</td><td>Replace the secret if drafts start saying <code>template</code>.</td></tr>
<tr><td>AI model names</td><td>Providers retire models</td><td>Set <code>GEMINI_MODEL</code> / <code>GROQ_MODEL</code> to a current model.</td></tr>
<tr><td>Bluesky app password</td><td>Until revoked</td><td>Make a new one in Bluesky settings, update the secret.</td></tr>
<tr><td><code>GH_TOKEN</code> (if used)</td><td>Fine-grained tokens expire (you pick, max 1 year)</td><td>Make a new one before it expires and update the secret.</td></tr>
<tr><td>Scheduled workflow</td><td>GitHub pauses schedules after 60 days with no repo activity</td><td>Data commits usually keep it active. If paused: Actions → ship-log → <span class="click">Enable workflow</span>.</td></tr>
<tr><td>Data files</td><td>Grow slowly</td><td>A year of daily use is still small. The page shows the latest 300 entries.</td></tr>
</table>
<h2>Weekly check (2 minutes)</h2>
<ol class="steps">
  <li>Repo → <strong>Actions</strong>: recent runs are green.</li>
  <li>Open the page: today's square and the streak look right.</li>
  <li>In Telegram, <code>/streak</code> answers within 15 minutes.</li>
</ol>
<div class="box info"><span class="box-title">Where secrets live</span>
Online: repo Settings → Secrets and variables → Actions. On the PC: the <code>.env</code> file, which git ignores. Nowhere else.</div>`);

add("full", "Security & Privacy", "Who can see what", `
<h2>What is public on purpose</h2>
<ul>
  <li><strong>The page and the whole repo,</strong> including <code>data\\entries.json</code> (every note and commit message) and <code>data\\posts.json</code> (every draft, including skipped ones).</li>
  <li><strong>Actions run logs</strong> are visible to anyone on a public repo. The code never prints keys, but error messages from services can appear there.</li>
</ul>
<div class="box warn"><span class="box-title">Don't log secrets or employer details</span>
Anything you send with <code>/log</code> becomes public. Keep notes about side projects only.</div>
<h2>What stays private</h2>
<ul>
  <li><strong>Keys and tokens</strong> are in GitHub Secrets or the git-ignored <code>.env</code>, never in the code.</li>
  <li><strong>Private repos:</strong> their commits appear as "Pushed a commit to a private project", with no name or message (<code>redact_private_repos</code> = <code>true</code>).</li>
  <li><strong>Bluesky</strong> uses an app password, which can be revoked without touching your real password.</li>
</ul>
<h2>Who can control the bot</h2>
<ul>
  <li>Only the chat in <code>TELEGRAM_CHAT_ID</code>. Messages and button presses from anyone else are ignored silently.</li>
  <li>Until <code>TELEGRAM_CHAT_ID</code> is set, the bot replies to anyone with their own chat id and does nothing else. Set it straight away.</li>
</ul>
<h2>Nothing is posted by surprise</h2>
<table>
<tr><th>Guard</th><th>Effect</th></tr>
<tr><td><code>approval_required</code> = <code>true</code></td><td>Every post waits for your Approve press</td></tr>
<tr><td><code>BLUESKY_DRY_RUN</code> = <code>1</code> (default)</td><td>Even Approve doesn't really post</td></tr>
<tr><td>Bluesky not configured</td><td>Approve only marks the draft "approved"</td></tr>
</table>`);

add("full", "Technical Reference", "For whoever maintains it", `
<h2>Addresses</h2>
<table>
<tr><td>Public page (after Pages is on)</td><td><code>${PAGE}</code></td></tr>
<tr><td>Code</td><td><code>${REPO}</code></td></tr>
<tr><td>Local page</td><td><code>http://localhost:8107</code> (<code>dev.py</code>)</td></tr>
<tr><td>Project folder</td><td><code style="font-size:10px;">${FOLDER}</code></td></tr>
</table>
<h2>Commands (<code>${PY} -m shiplog …</code>)</h2>
<table>
<tr><td><code>tick</code></td><td>Telegram + commits + due jobs + page data (what Actions runs)</td></tr>
<tr><td><code>poll</code> / <code>sync</code></td><td>Only Telegram / only commits</td></tr>
<tr><td><code>draft [--date YYYY-MM-DD]</code></td><td>Write a draft and send it for approval</td></tr>
<tr><td><code>remind</code></td><td>Run the reminder/draft checks (fire only when due)</td></tr>
<tr><td><code>build</code> / <code>status</code></td><td>Rebuild <code>docs\\data.json</code> / print streak numbers</td></tr>
<tr><td><code>chatid</code></td><td>List chat ids that messaged the bot</td></tr>
</table>
<p><code>dev.py</code> options: <code>--no-schedule</code> (no reminder or draft), <code>--page-only</code> (no bot). It checks commits every 10 minutes.</p>
<h2>Settings in .env / Actions</h2>
<table>
<tr><td>Secrets</td><td><code>TELEGRAM_BOT_TOKEN</code>, <code>TELEGRAM_CHAT_ID</code>, <code>GEMINI_API_KEY</code>, <code>GROQ_API_KEY</code>, <code>GH_TOKEN</code>, <code>BLUESKY_HANDLE</code>, <code>BLUESKY_APP_PASSWORD</code></td></tr>
<tr><td>Optional</td><td><code>GEMINI_MODEL</code>, <code>GROQ_MODEL</code>, <code>BLUESKY_PDS</code> (default <code>https://bsky.social</code>)</td></tr>
<tr><td>Variable</td><td><code>BLUESKY_DRY_RUN</code> (defaults to 1 if unset)</td></tr>
</table>
<h2>Workflow facts</h2>
<ul>
  <li>Cron <code>*/15 * * * *</code> plus a manual <span class="click">Run workflow</span>. Runs never overlap.</li>
  <li>Commits <code>data</code> and <code>docs/data.json</code> as <em>ship-log-bot</em>, then deploys the whole <code>docs\\</code> folder to Pages. This manual (<code>docs\\manual\\</code>) is published with it.</li>
</ul>`);

add("both", "Troubleshooting & FAQ", "Common issues, explained simply", `
<h3>The bot doesn't answer</h3>
<p>Online it answers within about 15 minutes, and GitHub's timer can run late. Check Actions for a red run. On the PC, <code>dev.py</code> must be running and show <em>"Bot: listening"</em>.</p>
<h3>Some messages get answered, others vanish</h3>
<p><code>dev.py</code> and Actions are both reading the same bot. Stop <code>dev.py</code>, or use <code>dev.py --page-only</code>.</p>
<h3>Bot says "Your chat id is …" to every message</h3>
<p><code>TELEGRAM_CHAT_ID</code> isn't set. Put that number in <code>.env</code> (and the Actions secret) and restart.</p>
<h3>My commits don't show up</h3>
<p>Check the repo is in <code>github_repos</code> as <code>owner/repo</code> and <code>github_author</code> is your GitHub username. Private repos need <code>GH_TOKEN</code>. Merge commits and <code>[skip ci]</code> commits never count. Run <code>${PY} -m shiplog sync</code> to see what it finds.</p>
<h3>A commit counted for the wrong day</h3>
<p>Days are IST. A commit after midnight IST counts for the next day, even if it was still evening in UTC.</p>
<h3>The draft says "template" instead of gemini or groq</h3>
<p>Both AI services failed (wrong key, limit reached, or retired model). The template draft still works. Check the keys and model names.</p>
<h3>Approve says "Approved (not posted…)"</h3>
<p>Dry-run is on or Bluesky isn't set up. Set <code>BLUESKY_DRY_RUN</code> = <code>0</code> and both Bluesky secrets.</p>
<h3>"Bluesky post failed"</h3>
<p>Usually a wrong handle or app password. The draft stays pending; fix the secret and press Approve again.</p>
<h3>The page shows "Couldn't load data.json"</h3>
<p>Open it through <code>http://localhost:8107</code> or the Pages address, not by double-clicking the file.</p>`);

add("full", "Known Limits", "What it can't do (yet)", `
<table>
<tr><th>Limit</th><th>Why</th><th>Workaround</th></tr>
<tr><td>Not live yet</td><td>Keys, bot, repos and Pages still pending</td><td>Setup checklist, Section 7.1</td></tr>
<tr><td>Only tested offline</td><td>No real Telegram, AI or Bluesky call made yet</td><td>Start with dry-run on; watch the first few days</td></tr>
<tr><td>Bot replies are slow online</td><td>Actions polls every 15 min, sometimes later</td><td>Use <code>dev.py</code> for instant replies (not at the same time)</td></tr>
<tr><td>Late runs can skip a draft</td><td>If no tick runs between 22:30 and midnight IST, the job never sees that day</td><td><code>shiplog draft --date …</code>, or <code>/draft</code> before midnight</td></tr>
<tr><td>Can't run bot in two places</td><td>Telegram hands each message to whoever asks first</td><td>One place at a time</td></tr>
<tr><td>No way to edit entries in chat</td><td>Only <code>/undo</code> (last /log) exists</td><td>Edit <code>data\\entries.json</code>, then push</td></tr>
<tr><td>Everything logged is public</td><td>The repo and page are public by design</td><td>Log side-project work only</td></tr>
<tr><td>One user only</td><td>One chat id, one author</td><td>Fork the repo for another person</td></tr>
<tr><td>Posts to Bluesky only</td><td>Other networks not built</td><td>Copy the draft by hand</td></tr>
<tr><td>Up to 500 commits per repo per sync</td><td>5 pages of 100</td><td>Fine for normal use</td></tr>
<tr><td>Times are IST only</td><td>Built for India</td><td>Change <code>IST</code> in <code>streak.py</code></td></tr>
</table>`);

add("both", "Glossary", "Every technical term, in plain English", `
<table>
<tr><th>Term</th><th>Plain-English meaning</th></tr>
<tr><td><strong>Streak</strong></td><td>How many days in a row you've logged something.</td></tr>
<tr><td><strong>IST</strong></td><td>India Standard Time (UTC + 5:30). The app's clock.</td></tr>
<tr><td><strong>Entry</strong></td><td>One logged item: a <code>/log</code> message or one commit.</td></tr>
<tr><td><strong>Commit</strong></td><td>A saved change in a GitHub repo.</td></tr>
<tr><td><strong>Repo</strong></td><td>A project's folder on GitHub, with its full history.</td></tr>
<tr><td><strong>Tick</strong></td><td>One run of the job: read Telegram, get commits, do due jobs, rebuild the page.</td></tr>
<tr><td><strong>GitHub Actions</strong></td><td>GitHub's free robot that runs the tick every 15 minutes.</td></tr>
<tr><td><strong>GitHub Pages</strong></td><td>GitHub's free website hosting, used for the public page.</td></tr>
<tr><td><strong>Heatmap</strong></td><td>The calendar grid. Darker squares mean more activity that day.</td></tr>
<tr><td><strong>Draft</strong></td><td>A post written by AI that waits for your decision.</td></tr>
<tr><td><strong>Dry-run</strong></td><td>Practice mode: Approve works, but nothing is really posted.</td></tr>
<tr><td><strong>Bluesky / app password</strong></td><td>A free social network, and a spare password just for this app that you can cancel any time.</td></tr>
<tr><td><strong>Gemini / Groq</strong></td><td>Free AI services that write the drafts. Groq is the backup.</td></tr>
<tr><td><strong>Secret</strong></td><td>A key or password stored safely in GitHub settings, never in the code.</td></tr>
<tr><td><strong>Chat id</strong></td><td>The number Telegram uses for your chat. The bot only obeys this one.</td></tr>
<tr><td><strong>JSON</strong></td><td>A plain text format for data. All the log data is kept in JSON files.</td></tr>
<tr><td><strong>localhost</strong></td><td>"This computer". <code>localhost:8107</code> only opens on your PC.</td></tr>
</table>`);

add("both", "Quick Reference Card", "One page, everything at a glance", `
<h2>Addresses</h2>
<table>
<tr><td>Public page (once Pages is on)</td><td><code>${PAGE}</code></td></tr>
<tr><td>Code</td><td><code>${REPO}</code></td></tr>
<tr><td>Local page + bot</td><td><code>${PY} dev.py</code> → <code>http://localhost:8107</code></td></tr>
<tr><td>Project folder</td><td><code style="font-size:10px;">${FOLDER}</code></td></tr>
</table>
<h2>Telegram</h2>
<table>
<tr><td><code>/log what you did 2h</code></td><td>Log today's work (hours optional: 2h, 1.5 hours, 45m)</td></tr>
<tr><td><code>/streak</code> · <code>/today</code></td><td>Numbers · today's entries</td></tr>
<tr><td><code>/undo</code> · <code>/draft</code></td><td>Remove last /log · write today's post now</td></tr>
<tr><td>9 PM · 10:30 PM IST</td><td>Reminder (if nothing logged) · draft with Approve / Skip / Rewrite</td></tr>
</table>
<h2>Terminal</h2>
<table>
<tr><td>Tests</td><td><code>${PY} -m unittest discover -s tests -t .</code></td></tr>
<tr><td>Streak numbers</td><td><code>${PY} -m shiplog status</code></td></tr>
<tr><td>Pull commits now</td><td><code>${PY} -m shiplog sync</code></td></tr>
<tr><td>Rebuild this manual</td><td><code>node docs\\manual\\build-docs.mjs</code>, then <code>docs\\manual\\print-pdfs.ps1</code></td></tr>
</table>
<h2>Publish a change</h2>
<p><code style="font-size:10px;word-break:break-all;">${PUBLISH}</code></p>
<div class="box tip" style="margin-top:18px;"><span class="box-title">Remember</span>
Cost is ₹0. Everything you log is public. Nothing is posted until you press Approve and <code>BLUESKY_DRY_RUN</code> is 0. Run the bot in one place only.</div>`);

function build(edition) {
  const full = edition === "full";
  const sections = S.filter((s) => s.ed === "both" || full);
  const kicker = full ? "Complete System Guide" : "System Overview Guide";
  const version = full ? "Version 1.0" : "Version 1.0 — Overview Edition";
  const badges = full
    ? ["System Architecture", "Daily Usage Guide", "Making Changes", "Maintenance &amp; Security"]
    : ["System Architecture", "Daily Usage Guide", "Troubleshooting"];
  const title = full ? "Public Ship Log — User Manual" : "Public Ship Log — User Manual (Overview Edition)";
  const toc = sections
    .map((s, i) => `<li><span><span class="n">${i + 1}.</span>${s.title}</span><span>${s.toc}</span></li>`)
    .join("\n");
  const pages = sections
    .map(
      (s, i) => `
<div class="page">
  <div class="section-kicker">Section ${i + 1}</div>
  <h1 class="section-title"><span class="section-num">${i + 1}</span>${s.title}</h1>
  ${s.body}
</div>`,
    )
    .join("\n");
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>${title}</title><style>${css}</style></head>
<body>
<div class="page cover">
  <div class="kicker">${kicker}</div>
  <h1>Public Ship Log</h1>
  <div class="sub">User Manual, Architecture Guide &amp; Standard Operating Procedure — a public daily build streak from Telegram notes and GitHub commits, with AI-drafted posts you approve, written in plain English for anyone to follow.</div>
  <div class="badge-row">${badges.map((b) => `<div class="badge">${b}</div>`).join("")}</div>
  <div class="meta">Prepared for Swapnil Dhavate · MES Business Analyst<br>${version} · October 2026</div>
</div>
<div class="page">
  <div class="section-kicker">Contents</div>
  <h1 class="section-title"><span class="section-num">·</span>Table of Contents</h1>
  <ul class="toc-list">${toc}</ul>
</div>
${pages}
</body></html>`;
}

fs.writeFileSync(path.join(here, "user-manual-overview.html"), build("short"));
fs.writeFileSync(path.join(here, "user-manual.html"), build("full"));
console.log("sections:", S.filter((s) => s.ed === "both").length, "overview /", S.length, "complete");
