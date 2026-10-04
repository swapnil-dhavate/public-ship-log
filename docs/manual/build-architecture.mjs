// Builds the landscape architecture deck in the same format as the other project
// architecture documents. Run: node docs/manual/build-architecture.mjs
// (then print to PDF: powershell -File docs\manual\print-pdfs.ps1)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const css = fs.readFileSync(path.join(here, "deck-style.css"), "utf8");

const card = (t, d) => `<div class="badge-card"><div class="t">${t}</div><div class="d">${d}</div></div>`;
const step = (n, t, d) => `<div class="step"><div class="num">${n}</div><div class="t">${t}</div><div class="d">${d}</div></div>`;

const diagram = `
<svg viewBox="0 0 900 360" role="img" aria-label="You log work in Telegram and push commits to your GitHub repos. Every 15 minutes GitHub Actions runs python -m shiplog tick, which reads Telegram, syncs commits, runs the 9 PM reminder and 10:30 PM draft jobs, and rebuilds the page data. Data is stored as JSON in the repo, drafts are written by Gemini with Groq and a template as fallbacks, approved posts go to Bluesky, and the heatmap page is deployed to GitHub Pages." style="width:100%;max-width:900px;height:auto;">
  <defs><marker id="a1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><polygon points="0,0 7,3 0,6" fill="#ffffff"/></marker></defs>
  <style>
    .n{fill:rgba(255,255,255,0.10);stroke:rgba(255,255,255,0.55);stroke-width:1.3;}
    .n2{fill:#ffffff;stroke:#ffffff;}
    .t{font-size:13px;fill:#ffffff;font-weight:700;}
    .t2{font-size:13px;fill:#0a2647;font-weight:700;}
    .s{font-size:9.5px;fill:#cfe3fa;}
    .s2{font-size:9.5px;fill:#45536b;}
    .e{stroke:#ffffff;stroke-width:1.2;fill:none;marker-end:url(#a1);}
  </style>
  <rect class="n" x="10" y="15" width="400" height="60" rx="8"/>
  <text class="t" x="210" y="42" text-anchor="middle">You, in Telegram</text>
  <text class="s" x="210" y="58" text-anchor="middle">/log · /streak · /today · /undo · /draft · Approve / Skip / Rewrite</text>
  <rect class="n" x="490" y="15" width="400" height="60" rx="8"/>
  <text class="t" x="690" y="42" text-anchor="middle">Your GitHub repos</text>
  <text class="s" x="690" y="58" text-anchor="middle">commits by github_author · bot, CI and merge commits ignored</text>
  <path class="e" d="M210,75 L210,110"/>
  <path class="e" d="M690,75 L690,110"/>

  <rect class="n2" x="10" y="115" width="880" height="100" rx="8"/>
  <text class="t2" x="450" y="138" text-anchor="middle">GitHub Actions, every 15 min: python -m shiplog tick (or dev.py on localhost:8107)</text>
  <text class="s2" x="120" y="166" text-anchor="middle">Telegram bot</text>
  <text class="s2" x="120" y="180" text-anchor="middle">owner-only commands + buttons</text>
  <text class="s2" x="340" y="166" text-anchor="middle">Commit sync</text>
  <text class="s2" x="340" y="180" text-anchor="middle">GitHub REST API · 2-day overlap</text>
  <text class="s2" x="560" y="166" text-anchor="middle">Due jobs (IST)</text>
  <text class="s2" x="560" y="180" text-anchor="middle">21:00 reminder · 22:30 draft</text>
  <text class="s2" x="780" y="166" text-anchor="middle">Page build</text>
  <text class="s2" x="780" y="180" text-anchor="middle">streak stats → docs/data.json</text>
  <text class="s2" x="450" y="203" text-anchor="middle">→ → →</text>

  <path class="e" d="M112,215 L112,250"/>
  <path class="e" d="M337,215 L337,250"/>
  <path class="e" d="M562,215 L562,250"/>
  <path class="e" d="M787,215 L787,250"/>
  <rect class="n" x="10" y="255" width="205" height="60" rx="8"/>
  <text class="t" x="112" y="280" text-anchor="middle">data/*.json</text>
  <text class="s" x="112" y="296" text-anchor="middle">committed back to the repo</text>
  <rect class="n" x="235" y="255" width="205" height="60" rx="8"/>
  <text class="t" x="337" y="280" text-anchor="middle">AI writer</text>
  <text class="s" x="337" y="296" text-anchor="middle">Gemini → Groq → template</text>
  <rect class="n" x="460" y="255" width="205" height="60" rx="8"/>
  <text class="t" x="562" y="280" text-anchor="middle">Bluesky</text>
  <text class="s" x="562" y="296" text-anchor="middle">only after Approve · dry-run default</text>
  <rect class="n" x="685" y="255" width="205" height="60" rx="8"/>
  <text class="t" x="787" y="280" text-anchor="middle">GitHub Pages</text>
  <text class="s" x="787" y="296" text-anchor="middle">streak + 12-month heatmap</text>
  <text class="s" x="450" y="345" text-anchor="middle">Python standard library only · no server · nothing goes public until you press Approve</text>
</svg>`;

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Public Ship Log — Deck</title><style>${css}</style></head>
<body>

<div class="slide center">
  <div class="kicker">Architecture Overview</div>
  <h1 style="font-size:64px;">Public Ship Log</h1>
  <div class="sub" style="font-size:19px; text-align:center;">A public build-streak tracker: log work in Telegram, count GitHub commits, publish a heatmap, and post AI-drafted updates only after approval</div>
  <div style="margin-top:40px; font-size:14px; color:#eaf4ff;"><strong>Swapnil Dhavate</strong><br><span style="color:#9fc9ee; font-size:12px;">Business Analyst · MES &amp; Agentic AI</span></div>
</div>

<div class="slide left">
  <div class="kicker">What It Does</div>
  <h2>From a one-line note to a public streak</h2>
  <div class="steps">
    ${step(1, "Log", "/log in Telegram, or just push a commit")}
    ${step(2, "Count", "Streak counted per day in India time (IST)")}
    ${step(3, "Draft", "10:30 PM IST: AI writes a short update post")}
    ${step(4, "Approve", "Your tap in Telegram sends it to Bluesky")}
  </div>
</div>

<div class="slide left">
  <div class="kicker">System Architecture</div>
  <h2>Serverless: one scheduled job does everything</h2>
  <figure>${diagram}</figure>
</div>

<div class="slide left">
  <div class="kicker">Reliability &amp; Safety</div>
  <h2>Safe to re-run, nothing posted by surprise</h2>
  <div class="badge-grid" style="justify-content:flex-start;">
    ${card("Re-runnable jobs", "Reminder and draft check the time and fire once per day")}
    ${card("AI fallback chain", "Gemini, then Groq, then a plain template")}
    ${card("Human approval gate", "Approve button + BLUESKY_DRY_RUN=1 by default")}
    ${card("Honest streak", "Bot, CI and merge commits never count")}
    ${card("Owner-only bot", "Messages from anyone else are ignored")}
    ${card("Test-backed", "10 unit tests: streak, IST midnight, hours, 300-char limit")}
  </div>
</div>

<div class="slide left">
  <div class="kicker">Technology Stack</div>
  <h2>Plain Python, all free services</h2>
  <div class="badge-grid" style="justify-content:flex-start;">
    ${card("Python 3 stdlib", "No packages to install")}
    ${card("Telegram Bot API", "Logging and approval buttons")}
    ${card("GitHub REST API", "Commit sync")}
    ${card("GitHub Actions", "15-minute schedule")}
    ${card("GitHub Pages", "Public heatmap page")}
    ${card("Gemini 2.5 Flash", "Main post writer")}
    ${card("Groq · Llama 3.3 70B", "Backup writer")}
    ${card("Bluesky AT Protocol", "Publishing approved posts")}
  </div>
</div>

<div class="slide center">
  <div class="kicker">Cost Structure</div>
  <div class="big-stat">₹0<span style="font-size:28px;">/month</span></div>
  <div class="big-stat-label">Free GitHub Actions and Pages for a public repo, free AI tiers, free Telegram and Bluesky</div>
</div>

<div class="slide left">
  <div class="kicker">Growth Potential</div>
  <h2>From streak counter to build-in-public assistant</h2>
  <div class="badge-grid" style="justify-content:flex-start;">
    ${card("More platforms", "Mastodon or LinkedIn next to Bluesky")}
    ${card("Weekly recap", "One summary post every Sunday")}
    ${card("Instant replies", "Webhook instead of the 15-minute poll")}
    ${card("Per-project view", "Tag entries and filter the heatmap")}
  </div>
</div>

<div class="slide center">
  <h1>Public Ship Log</h1>
  <div class="sub" style="text-align:center;">Designed &amp; Engineered by Swapnil Dhavate</div>
</div>

</body></html>`;

fs.writeFileSync(path.join(here, "architecture-deck.html"), html);
console.log("written architecture-deck.html");
