#!/usr/bin/env python3
"""Checks that the validator accepts the four worked examples and refuses what the schema forbids.

Written 2026-10-16 with the validator (weekend step 2 of docs/2026-10-16-kickoff.md). Plain
Python, standard library only, no dependencies:

    python3 scripts/test_compute.py

Each refusal test copies data/ to a temporary folder, breaks one thing in one file by editing
its text (so the test exercises the same TOML the validator reads), and checks that the
validator names the problem. The history check (ids that were committed before and are now
gone) is exercised by passing the set of previously seen ids directly, since a temporary copy
has no git history.
"""

from __future__ import annotations

import io
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def problems_for(data_dir: Path, previously_seen=None) -> list[str]:
    loaded = compute.load_records(data_dir)
    return compute.validate(loaded, previously_seen)


class TempData:
    """A throwaway copy of data/ that a test can break."""

    def __enter__(self) -> Path:
        self.tmp = Path(tempfile.mkdtemp(prefix="quiet-galaxy-test-"))
        self.data = self.tmp / "data"
        shutil.copytree(DATA, self.data)
        return self.data

    def __exit__(self, *exc) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


def edit(path: Path, pattern: str, replacement: str, count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, replacement, text, count=count, flags=re.M)
    assert n >= 1, f"pattern {pattern!r} not found in {path.name}"
    path.write_text(new, encoding="utf-8")


class TheFourExamples(unittest.TestCase):
    def test_examples_pass(self):
        self.assertEqual(problems_for(DATA), [])

    def test_examples_pass_with_history(self):
        seen = compute.ids_in_history(DATA)
        if seen is None:
            self.skipTest("data/ is not in a git repository here")
        self.assertEqual(problems_for(DATA, seen), [])

    def test_one_of_each_kind(self):
        loaded = compute.load_records(DATA)
        kinds = sorted(r["_kind"] for r in loaded["records"])
        self.assertEqual(kinds, ["explanation", "factor", "library", "publication"])

    def test_validate_command_exits_zero(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = compute.main(["--data", str(DATA), "validate"])
        self.assertEqual(code, 0)
        self.assertIn("OK", out.getvalue())


class FactorRules(unittest.TestCase):
    def test_factor_with_no_source_is_refused(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r'^source = "Cassan.*\n', "")
            problems = problems_for(data)
        self.assertTrue(problems, "a factor estimate with no source must fail")
        self.assertTrue(any("estimate 2" in p and "source" in p for p in problems), problems)

    def test_factor_with_no_estimates_is_refused(self):
        with TempData() as data:
            path = data / "factors" / "planets.toml"
            text = path.read_text(encoding="utf-8")
            text = text[: text.index("[[estimate]]")] + text[text.index("[range]"):]
            path.write_text(text, encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any("'estimate'" in p for p in problems), problems)

    def test_fraction_outside_zero_to_one_is_refused(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r"^high = 1\.0\n(shape)", "high = 3.0\n\\1")
            problems = problems_for(data)
        self.assertTrue(any("between 0 and 1" in p for p in problems), problems)

    def test_symbol_must_match_id(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r'^symbol = "fp"', 'symbol = "ne"')
            problems = problems_for(data)
        self.assertTrue(any("symbol must be 'fp'" in p for p in problems), problems)

    def test_unknown_field_is_refused(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r'^source = "Green', 'sourse = "Green')
            problems = problems_for(data)
        self.assertTrue(any("unknown field 'sourse'" in p for p in problems), problems)
        self.assertTrue(any("estimate 1" in p and "no source" in p for p in problems), problems)


class ExplanationRules(unittest.TestCase):
    def test_explanation_with_no_family_is_refused(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r'^family = "unseen"\n', "")
            problems = problems_for(data)
        self.assertTrue(any("'family'" in p for p in problems), problems)

    def test_explanation_with_no_factor_is_refused(self):
        with TempData() as data:
            path = data / "explanations" / "dark-forest.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text[: text.index("[[bears_on]]")], encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any("'bears_on'" in p for p in problems), problems)

    def test_unknown_family_is_refused(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r'^family = "unseen"', 'family = "hiding"')
            problems = problems_for(data)
        self.assertTrue(any("family must be one of" in p for p in problems), problems)

    def test_bad_direction_is_refused(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r'^direction = "lowers"', 'direction = "shrinks"')
            problems = problems_for(data)
        self.assertTrue(any("direction must be one of" in p for p in problems), problems)


class Links(unittest.TestCase):
    def test_dangling_related_explanation_is_refused(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r"^related = \[\]", 'related = ["zoo-hypothesis"]')
            problems = problems_for(data)
        self.assertTrue(any("'zoo-hypothesis'" in p and "not an explanation that exists" in p for p in problems), problems)

    def test_dangling_library_link_is_refused(self):
        with TempData() as data:
            edit(data / "library" / "three-body-problem.toml", r'^explanations = \["dark-forest"\]', 'explanations = ["dark-woods"]')
            problems = problems_for(data)
        self.assertTrue(any("'dark-woods'" in p for p in problems), problems)

    def test_dangling_range_source_is_refused(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r'^sources = \["sandberg-2018"\]', 'sources = ["nobody-1999"]')
            problems = problems_for(data)
        self.assertTrue(any("'nobody-1999'" in p for p in problems), problems)

    def test_library_entry_needs_a_target(self):
        with TempData() as data:
            edit(data / "library" / "three-body-problem.toml", r'^explanations = \["dark-forest"\]\n', "")
            edit(data / "library" / "three-body-problem.toml", r'^factors = \["detectable"\]\n', "")
            problems = problems_for(data)
        self.assertTrue(any("names no explanation and no factor" in p for p in problems), problems)

    def test_moved_range_needs_a_revision(self):
        with TempData() as data:
            edit(data / "papers" / "sandberg-2018.toml", r"^moved_range = false", "moved_range = true")
            problems = problems_for(data)
        self.assertTrue(any("no factor has a revision naming 'sandberg-2018'" in p for p in problems), problems)

    def test_moved_range_backed_by_a_revision_passes(self):
        with TempData() as data:
            edit(data / "papers" / "sandberg-2018.toml", r"^moved_range = false", "moved_range = true")
            with (data / "factors" / "planets.toml").open("a", encoding="utf-8") as f:
                f.write('\n[[revision]]\ndate = 2026-10-16\nfield = "range.low"\nold = 0.05\nnew = 0.1\n'
                        'why = "Test revision."\npublication = "sandberg-2018"\n')
            problems = problems_for(data)
        self.assertEqual(problems, [])


class RenamedIds(unittest.TestCase):
    def test_file_name_must_equal_id(self):
        with TempData() as data:
            (data / "explanations" / "dark-forest.toml").rename(data / "explanations" / "dark-woods.toml")
            problems = problems_for(data)
        self.assertTrue(any("named 'dark-woods' but its id is 'dark-forest'" in p for p in problems), problems)

    def test_id_gone_from_history_without_retirement_is_refused(self):
        with TempData() as data:
            (data / "explanations" / "dark-forest.toml").unlink()
            edit(data / "library" / "three-body-problem.toml", r'^explanations = \["dark-forest"\]\n', "")
            seen = {("explanation", "dark-forest"), ("factor", "planets")}
            problems = problems_for(data, seen)
        self.assertTrue(any("'dark-forest' was committed before and is now gone" in p for p in problems), problems)

    def test_retired_id_satisfies_the_history_check(self):
        with TempData() as data:
            (data / "explanations" / "dark-forest.toml").unlink()
            edit(data / "library" / "three-body-problem.toml", r'^explanations = \["dark-forest"\]\n', "")
            (data / "retired.toml").write_text(
                '[[retired]]\nid = "dark-forest"\nkind = "explanation"\ndate = 2026-10-16\n'
                'why = "Test retirement."\n', encoding="utf-8")
            seen = {("explanation", "dark-forest")}
            problems = problems_for(data, seen)
        self.assertEqual(problems, [])

    def test_retired_id_cannot_be_reused(self):
        with TempData() as data:
            (data / "retired.toml").write_text(
                '[[retired]]\nid = "dark-forest"\nkind = "explanation"\ndate = 2026-10-16\n'
                'why = "Test retirement."\n', encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any("retired but" in p and "never reused" in p for p in problems), problems)


class RunStub(unittest.TestCase):
    def test_run_says_factors_not_seeded(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = compute.main(["--data", str(DATA), "run"])
        self.assertEqual(code, 2)
        self.assertIn("not seeded yet", out.getvalue())
        self.assertIn("1 of 7", out.getvalue())

    def test_run_refuses_invalid_data(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r'^family = "unseen"\n', "")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = compute.main(["--data", str(data), "run"])
        self.assertEqual(code, 1)
        self.assertIn("Refusing to run", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
