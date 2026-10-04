"""Turn a day's raw notes + commits into a short public update.

Tries Gemini first, then Groq, then a plain template, so a draft is always produced.
"""
import re
from datetime import date

from . import env, net, store
from .streak import compute

MAX_POST = 300  # Bluesky's limit (graphemes); len() over-counts emoji, so this is safe

SYSTEM = (
    "You write short build-in-public updates for a solo developer who works on side "
    "projects after their day job. Write ONE update of at most 200 characters, first person, "
    "past tense, about what got done. Be concrete: name the actual things from the notes. "
    "Sound like a real person texting a friend, not a press release. No hashtags, no links, "
    "no emojis, no 'Day N' prefix, no quotation marks. Never use the words excited, thrilled, "
    "journey, game-changer, delve, leverage, or crushing it. Output only the update."
)


def _gemini(prompt):
    key = env.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("no GEMINI_API_KEY")
    model = env.get("GEMINI_MODEL") or "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 400,
                             "thinkingConfig": {"thinkingBudget": 0}},
    }
    try:
        resp = net.post(url, payload, headers={"x-goog-api-key": key})
    except net.HttpError as e:
        if e.status != 400:
            raise
        payload["generationConfig"].pop("thinkingConfig")  # model without thinking support
        resp = net.post(url, payload, headers={"x-goog-api-key": key})
    parts = resp["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def _groq(prompt):
    key = env.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("no GROQ_API_KEY")
    resp = net.post(
        "https://api.groq.com/openai/v1/chat/completions",
        {
            "model": env.get("GROQ_MODEL") or "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 200,
        },
        headers={"Authorization": f"Bearer {key}"},
    )
    return resp["choices"][0]["message"]["content"]


def _clean(text, limit=220):
    text = re.sub(r"\s+", " ", text).strip().strip('"“”').strip()
    text = re.sub(r"#\w+", "", text).strip()
    if len(text) > limit:
        cut = text[:limit]
        stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
        text = cut[: stop + 1] if stop > 80 else cut.rsplit(" ", 1)[0] + "…"
    return text


def _template(day_entries):
    notes = [e["text"] for e in day_entries if e["source"] != "github"]
    commits = [e for e in day_entries if e["source"] == "github"]
    bits = notes[:3]
    if commits:
        repos = sorted({e.get("repo", "") for e in commits if e.get("repo") != "private"})
        where = f" to {', '.join(r.split('/')[-1] for r in repos)}" if repos else ""
        bits.append(f"pushed {len(commits)} commit{'s' if len(commits) != 1 else ''}{where}")
    return "Today: " + "; ".join(bits) + "."


def compose(body, day_number, cfg):
    """Prefix the streak day, then add hashtags and the page link if they fit."""
    text = f"Day {day_number} of shipping daily 🚢\n\n{body}"
    tags = " ".join(f"#{t.lstrip('#')}" for t in cfg.get("hashtags") or [])
    for extra in (f"\n\n{tags}" if tags else "", f"\n{cfg['site_url']}" if cfg.get("site_url") else ""):
        if extra and len(text + extra) <= MAX_POST:
            text += extra
    if len(text) > MAX_POST:
        text = text[: MAX_POST - 1].rsplit(" ", 1)[0] + "…"
    return text


def draft_for(day):
    """Return (post_text, provider) for an IST date string, or (None, reason)."""
    all_entries = store.entries()
    day_entries = [e for e in all_entries if e["date"] == day]
    if not day_entries:
        return None, "nothing logged that day"

    lines = []
    for e in day_entries:
        if e["source"] == "github":
            lines.append(f"- commit to {e.get('repo', 'a repo')}: {e['text']}")
        else:
            hrs = f" ({e['hours']}h)" if e.get("hours") else ""
            lines.append(f"- note: {e['text']}{hrs}")
    hours = sum(e.get("hours") or 0 for e in day_entries)
    prompt = "What I did today:\n" + "\n".join(lines[:40])
    if hours:
        prompt += f"\nTime spent: about {hours:g} hours."

    body, provider = None, "template"
    for name, fn in (("gemini", _gemini), ("groq", _groq)):
        try:
            body = _clean(fn(prompt))
            if body:
                provider = name
                break
        except Exception as e:
            print(f"[writer] {name} failed: {e}")
    if not body:
        body = _clean(_template(day_entries))

    stats = compute(all_entries, today=date.fromisoformat(day))
    return compose(body, stats["current"], env.config()), provider
