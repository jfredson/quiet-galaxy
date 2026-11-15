#!/usr/bin/env python3
"""Checks for the year-in-review rules in scripts/check_news.py (ruled by John 2026-11-15, the same on
all five trackers): the kind is accepted; every record it names must show a dated change in the post's
own calendar year, in place of the fourteen-day window; and there is at most one such post a year.

    python3 scripts/test_news.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_news  # noqa: E402

REVIEW = ("---\ntitle: The year\ndate: 2026-12-29\nkind: year-in-review\nsummary: The year.\n"
          "records: [a-range]\nsources:\n  - label: A source\n    url: https://example.org/\n---\n\n"
          "One paragraph with a figure, 58 percent ([a source](https://example.org/)).\n")
# The range changed in October, far more than fourteen days before the post, but in the same year.
RECORDS = {"factors": [{"id": "a-range", "revisions": [{"date": "2026-10-17"}]}], "explanations": [], "readings": []}


class YearInReview(unittest.TestCase):
    def run_check(self, posts: dict[str, str], records=RECORDS) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name, text in posts.items():
                (d / name).write_text(text, encoding="utf-8")
            return check_news.check(d, records)[0]

    def test_the_kind_is_accepted_with_a_change_earlier_in_the_year(self):
        self.assertEqual(self.run_check({"2026-12-29-the-year.md": REVIEW}), [])

    def test_the_fourteen_day_rule_still_holds_for_other_kinds(self):
        other = REVIEW.replace("kind: year-in-review", "kind: estimate-revised")
        self.assertTrue(any("within 14 days" in p for p in self.run_check({"2026-12-29-the-year.md": other})))

    def test_a_record_with_no_change_that_year_is_refused(self):
        old = {"factors": [{"id": "a-range", "revisions": [{"date": "2025-12-31"}], "range": {"set_on": "2027-01-01"}}], "explanations": [], "readings": []}
        problems = self.run_check({"2026-12-29-the-year.md": REVIEW}, old)
        self.assertTrue(any("no dated change in 2026" in p for p in problems))

    def test_a_second_review_in_the_same_year_is_refused(self):
        second = REVIEW.replace("date: 2026-12-29", "date: 2026-12-30")
        problems = self.run_check({"2026-12-29-the-year.md": REVIEW, "2026-12-30-the-year-again.md": second})
        self.assertTrue(any("one per year" in p for p in problems))

    def test_one_review_in_each_of_two_years_passes(self):
        later = REVIEW.replace("date: 2026-12-29", "date: 2027-12-29")
        records = {"factors": [{"id": "a-range", "revisions": [{"date": "2026-10-17"}, {"date": "2027-03-01"}]}], "explanations": [], "readings": []}
        self.assertEqual(self.run_check({"2026-12-29-the-year.md": REVIEW, "2027-12-29-the-year.md": later}, records), [])


if __name__ == "__main__":
    unittest.main()
