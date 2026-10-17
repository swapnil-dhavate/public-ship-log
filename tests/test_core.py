import contextlib
import io
import json
import os
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from shiplog import bluesky, github_sync, store, writer
from shiplog.bot import parse_log
from shiplog.streak import compute, to_ist


def days(*isos):
    return [{"date": d, "source": "telegram", "text": "x"} for d in isos]


class StreakTests(unittest.TestCase):
    T = date(2026, 10, 4)

    def test_logged_today_counts_today(self):
        s = compute(days("2026-10-02", "2026-10-03", "2026-10-04"), today=self.T)
        self.assertEqual((s["current"], s["logged_today"], s["at_risk"]), (3, True, False))

    def test_not_logged_today_is_at_risk_but_alive(self):
        s = compute(days("2026-10-02", "2026-10-03"), today=self.T)
        self.assertEqual((s["current"], s["at_risk"]), (2, True))

    def test_gap_breaks_streak(self):
        s = compute(days("2026-09-30", "2026-10-01", "2026-10-02"), today=self.T)
        self.assertEqual((s["current"], s["longest"], s["at_risk"]), (0, 3, False))

    def test_multiple_entries_same_day_count_once(self):
        s = compute(days("2026-10-04", "2026-10-04", "2026-10-03"), today=self.T)
        self.assertEqual((s["current"], s["total_days"], s["total_entries"]), (2, 2, 3))

    def test_ist_day_boundary(self):
        # 19:00 UTC on 3 Oct is 00:30 IST on 4 Oct
        self.assertEqual(to_ist("2026-10-03T19:00:00Z").date(), date(2026, 10, 4))
        self.assertEqual(to_ist(datetime(2026, 10, 3, 18, 0, tzinfo=timezone.utc)).date(), date(2026, 10, 3))


class ParseLogTests(unittest.TestCase):
    def test_hours_variants(self):
        self.assertEqual(parse_log("fixed login bug 2h"), ("fixed login bug", 2.0))
        self.assertEqual(parse_log("wrote tests 1.5 hours"), ("wrote tests", 1.5))
        self.assertEqual(parse_log("refactor for 45m"), ("refactor", 0.75))
        self.assertEqual(parse_log("shipped v2 of the page"), ("shipped v2 of the page", None))

    def test_numbers_that_are_not_hours_stay(self):
        self.assertEqual(parse_log("read 3 chapters of the h264 spec"), ("read 3 chapters of the h264 spec", None))


class PostTests(unittest.TestCase):
    def test_compose_fits_limit(self):
        cfg = {"hashtags": ["buildinpublic"], "site_url": "https://example.github.io/ship-log"}
        text = writer.compose("x" * 280, 5, cfg)
        self.assertLessEqual(len(text), writer.MAX_POST)
        self.assertTrue(text.startswith("Day 5"))

    def test_compose_adds_tags_and_link_when_room(self):
        cfg = {"hashtags": ["buildinpublic"], "site_url": "https://example.github.io/ship-log"}
        text = writer.compose("Fixed the heatmap.", 3, cfg)
        self.assertIn("#buildinpublic", text)
        self.assertIn("https://example.github.io/ship-log", text)

    def test_facets_use_byte_offsets(self):
        text = "Day 3 🚢 done #buildinpublic https://a.io/x."
        f = bluesky.facets(text)
        raw = text.encode("utf-8")
        got = {raw[x["index"]["byteStart"]:x["index"]["byteEnd"]].decode() for x in f}
        self.assertEqual(got, {"#buildinpublic", "https://a.io/x"})


def commit(sha, login, email, message="secret work", date_="2026-10-10T10:00:00Z"):
    return {"sha": sha, "parents": [{}], "html_url": f"https://github.com/x/commit/{sha}",
            "author": {"login": login} if login else None,
            "commit": {"message": message, "author": {"email": email, "date": date_}}}


class GithubSyncTests(unittest.TestCase):
    ME = "swapnil-dhavate"

    def test_is_mine_matches_login_and_noreply_only(self):
        mine = github_sync._is_mine
        self.assertTrue(mine(commit("a", "Swapnil-Dhavate", "x@example.com"), self.ME))
        self.assertTrue(mine(commit("b", None, "256497006+swapnil-dhavate@users.noreply.github.com"), self.ME))
        self.assertTrue(mine(commit("c", None, "swapnil-dhavate@users.noreply.github.com"), self.ME))
        self.assertFalse(mine(commit("d", None, "someone@work.example"), self.ME))
        self.assertFalse(mine(commit("e", "rushi6298", "someone@work.example"), self.ME))
        self.assertFalse(mine(commit("f", None, "1+not-swapnil-dhavate@users.noreply.github.com"), self.ME))

    def test_private_repo_names_only_come_from_env_and_get_labels(self):
        cfg = {"github_repos": ["me/public-one"]}
        with mock.patch.dict(os.environ, {"SHIPLOG_REPOS": "me/secret-a, me/secret-b,me/public-one"}):
            got = github_sync.repos(cfg)
        self.assertEqual(got, [("me/public-one", "me/public-one"), ("me/secret-a", "private repo #1"),
                               ("me/secret-b", "private repo #2")])

    def _run_sync(self, repo_info, commits, state=None, fail=()):
        """Run sync() against fake GitHub data in a temp data dir; return (entries, state, log)."""
        cfg = {"github_repos": [], "github_author": self.ME, "github_backfill_days": 14,
               "redact_private_repos": True, "ignore_commits_matching": ["[skip ci]"]}

        def fake_get(url, **kw):
            repo = url.split("/repos/", 1)[1].split("/commits")[0]
            if repo in fail:
                raise RuntimeError(f"HTTP 404 for {url}")
            return commits[repo] if url.endswith("/commits") else repo_info[repo]

        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            if state:
                (data / "state.json").write_text(json.dumps(state), encoding="utf-8")
            out = io.StringIO()
            with mock.patch.object(store, "DATA_DIR", data), \
                    mock.patch.object(github_sync.env, "config", return_value=cfg), \
                    mock.patch.object(github_sync.net, "get", side_effect=fake_get), \
                    mock.patch.dict(os.environ, {"SHIPLOG_REPOS": ",".join(repo_info)}), \
                    contextlib.redirect_stdout(out):
                github_sync.sync(verbose=True)
            return store_load(data, "entries"), store_load(data, "state"), out.getvalue()

    def test_private_commits_are_redacted_and_names_never_logged_or_saved(self):
        info = {"me/hidden-proj": {"id": 11, "private": True}, "me/no-flag": {"id": 12}}
        commits = {
            "me/hidden-proj": [commit("s1", self.ME, "x@y.z", "add payroll export"),
                               commit("s2", None, "someone@work.example", "colleague commit")],
            "me/no-flag": [commit("s3", self.ME, "x@y.z", "top secret thing")],
        }
        entries, state, log = self._run_sync(info, commits)
        self.assertEqual([e["sha"] for e in entries], ["s1", "s3"])
        blob = json.dumps([entries, state]) + log
        for leak in ("hidden-proj", "no-flag", "payroll", "top secret", "colleague", "x@y.z"):
            self.assertNotIn(leak, blob)
        self.assertTrue(all(e["repo"] == "private" and "url" not in e for e in entries))

    def test_public_repo_keeps_message_and_link(self):
        info = {"me/open": {"id": 5, "private": False}}
        entries, _, _ = self._run_sync(info, {"me/open": [commit("p1", self.ME, "x@y.z", "fix heatmap\n\nbody")]})
        self.assertEqual((entries[0]["text"], entries[0]["repo"]), ("fix heatmap", "me/open"))
        self.assertIn("url", entries[0])

    def test_unreadable_repo_keeps_its_backfill_for_later(self):
        info = {"me/later": {"id": 7, "private": True}}
        entries, state, log = self._run_sync(info, {"me/later": []}, fail=("me/later",))
        self.assertEqual(entries, [])
        self.assertNotIn("7", state.get("github_cursors", {}))
        self.assertNotIn("me/later", log)


def store_load(data_dir, name):
    path = data_dir / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else ([] if name == "entries" else {})


if __name__ == "__main__":
    unittest.main()
