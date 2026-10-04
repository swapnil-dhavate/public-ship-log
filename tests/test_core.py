import unittest
from datetime import date, datetime, timezone

from shiplog import bluesky, writer
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


if __name__ == "__main__":
    unittest.main()
