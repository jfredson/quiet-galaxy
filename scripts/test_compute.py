#!/usr/bin/env python3
"""Checks that the validator accepts the records and refuses what the schema forbids, and that the
headline computation reproduces the 2018 paper given its ranges.

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
import json
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


def forget(data: Path, id_: str) -> None:
    """Remove every link to an id from every record, so a test can delete that record cleanly.
    Added 2026-10-16 when the real explanations arrived and the dark forest gained neighbours."""
    pat = re.escape(id_)
    for path in sorted((data / "readings").glob("*.toml")) if (data / "readings").is_dir() else []:
        # A weekly reading that read this record would be left naming it; the test is about the
        # record, not the reading, so the reading goes too (added 2026-10-16 with the readings).
        if f'record = "{id_}"' in path.read_text(encoding="utf-8"):
            path.unlink()
    for path in sorted(data.rglob("*.toml")):
        text = path.read_text(encoding="utf-8")
        new = re.sub(rf'"{pat}",\s*', "", text)
        new = re.sub(rf',\s*"{pat}"', "", new)
        new = re.sub(rf'"{pat}"', "", new)
        if new != text:
            path.write_text(new, encoding="utf-8")


class TheRecords(unittest.TestCase):
    def test_examples_pass(self):
        self.assertEqual(problems_for(DATA), [])

    def test_examples_pass_with_history(self):
        seen = compute.ids_in_history(DATA)
        if seen is None:
            self.skipTest("data/ is not in a git repository here")
        self.assertEqual(problems_for(DATA, seen), [])

    def test_at_least_one_of_each_kind_and_all_seven_factors(self):
        loaded = compute.load_records(DATA)
        kinds = {r["_kind"] for r in loaded["records"]}
        self.assertEqual(kinds, {"explanation", "factor", "library", "publication", "reading"})
        factors = sorted(r["id"] for r in loaded["records"] if r["_kind"] == "factor")
        self.assertEqual(factors, sorted(compute.FACTORS))

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


class TheThirdShape(unittest.TestCase):
    """The log-normal-rate shape, ruled by John 2026-10-16: median and spread_orders in place of
    low and high, for a fraction only (docs/record-schema.md, docs/method.md item 7)."""

    def test_the_life_record_uses_it_and_passes(self):
        loaded = compute.load_records(DATA)
        life = next(r for r in loaded["records"] if r.get("id") == "life")
        self.assertEqual(life["range"]["shape"], "log-normal-rate")
        self.assertEqual(life["range"]["median"], 1.0)
        self.assertEqual(life["range"]["spread_orders"], 50)
        self.assertNotIn("low", life["range"])
        self.assertEqual(problems_for(DATA), [])

    def test_low_and_high_are_refused_with_it(self):
        with TempData() as data:
            edit(data / "factors" / "life.toml", r'^median = 1\.0\n', "median = 1.0\nlow = 0.001\n")
            problems = problems_for(data)
        self.assertTrue(any("has no 'low'" in p for p in problems), problems)

    def test_median_and_spread_are_required_with_it(self):
        with TempData() as data:
            edit(data / "factors" / "life.toml", r'^spread_orders = 50\n', "")
            problems = problems_for(data)
        self.assertTrue(any("missing 'spread_orders'" in p for p in problems), problems)

    def test_median_must_be_above_zero(self):
        with TempData() as data:
            edit(data / "factors" / "life.toml", r'^median = 1\.0', "median = 0")
            problems = problems_for(data)
        self.assertTrue(any("'median' must be a number above 0" in p for p in problems), problems)

    def test_median_and_spread_belong_only_to_it(self):
        with TempData() as data:
            edit(data / "factors" / "planets.toml", r'^shape = "log-uniform"\n', 'shape = "log-uniform"\nmedian = 1.0\n')
            problems = problems_for(data)
        self.assertTrue(any("'median' belongs only to the log-normal-rate shape" in p for p in problems), problems)

    def test_it_fits_only_a_fraction(self):
        with TempData() as data:
            path = data / "factors" / "lifetime.toml"
            text = path.read_text(encoding="utf-8")
            start = text.index("[range]")
            text = text[:start] + ('[range]\nshape = "log-normal-rate"\nmedian = 1.0\nspread_orders = 50\n'
                                   'status = "first-pass"\nset_on = 2026-10-16\nwhy = "Test."\n')
            path.write_text(text, encoding="utf-8")
            problems = problems_for(data)
        self.assertTrue(any("fits only a factor measured as a fraction" in p for p in problems), problems)

    def test_ends_and_middle_for_display(self):
        rng = {"shape": "log-normal-rate", "median": 1.0, "spread_orders": 50}
        lo, hi = compute.range_ends(rng)
        self.assertAlmostEqual(lo, 1e-50, delta=1e-52)
        self.assertEqual(hi, 1.0)
        self.assertAlmostEqual(compute.range_middle(rng), 1 - compute.math.exp(-1), places=9)
        self.assertEqual(compute.range_ends({"shape": "log-uniform", "low": 0.1, "high": 1}), (0.1, 1.0))
        self.assertAlmostEqual(compute.range_middle({"shape": "log-uniform", "low": 0.01, "high": 1}), 0.1)
        self.assertEqual(compute.range_middle({"shape": "uniform", "low": 2, "high": 4}), 3.0)


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
            edit(data / "explanations" / "dark-forest.toml", r"^related = \[.*\]$", 'related = ["dark-woods"]')
            problems = problems_for(data)
        self.assertTrue(any("'dark-woods'" in p and "not an explanation that exists" in p for p in problems), problems)

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
            edit(data / "papers" / "drake-1961.toml", r"^moved_range = false", "moved_range = true")
            problems = problems_for(data)
        self.assertTrue(any("no factor has a revision naming 'drake-1961'" in p for p in problems), problems)

    def test_moved_range_backed_by_a_revision_passes(self):
        with TempData() as data:
            edit(data / "papers" / "drake-1961.toml", r"^moved_range = false", "moved_range = true")
            with (data / "factors" / "planets.toml").open("a", encoding="utf-8") as f:
                f.write('\n[[revision]]\ndate = 2026-10-16\nfield = "range.low"\nold = 0.05\nnew = 0.1\n'
                        'why = "Test revision."\npublication = "drake-1961"\n')
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
            forget(data, "dark-forest")
            seen = {("explanation", "dark-forest"), ("factor", "planets")}
            problems = problems_for(data, seen)
        self.assertTrue(any("'dark-forest' was committed before and is now gone" in p for p in problems), problems)

    def test_retired_id_satisfies_the_history_check(self):
        with TempData() as data:
            (data / "explanations" / "dark-forest.toml").unlink()
            forget(data, "dark-forest")
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


class TheReading(unittest.TestCase):
    """The fifth kind of record: a weekly reading of the records against the news
    (docs/weekly-reading.md; added 2026-10-16). Each test breaks the first reading's file."""

    FILE = Path("readings") / "2026-10-16.toml"

    def test_the_first_reading_passes(self):
        loaded = compute.load_records(DATA)
        readings = [r for r in loaded["records"] if r["_kind"] == "reading"]
        self.assertEqual([r["id"] for r in readings], ["2026-10-16"])
        self.assertEqual(readings[0]["records_read"], len(readings[0]["item"]))
        self.assertEqual(problems_for(DATA), [])

    def test_unknown_verdict_is_refused(self):
        with TempData() as data:
            edit(data / self.FILE, r'verdict = "quiet"', 'verdict = "maybe"')
            problems = problems_for(data)
        self.assertTrue(any("verdict must be one of quiet, noted, moved, flagged" in p for p in problems), problems)

    def test_noted_needs_a_publication(self):
        with TempData() as data:
            edit(data / self.FILE, r'^publications = \["glidden-2025"\]\n', "")
            problems = problems_for(data)
        self.assertTrue(any("habitable-planets" in p and "name it in 'publications'" in p for p in problems), problems)

    def test_publication_must_exist(self):
        with TempData() as data:
            edit(data / self.FILE, r'"glidden-2025"', '"nobody-2099"')
            problems = problems_for(data)
        self.assertTrue(any("'nobody-2099' is not a publication record that exists" in p for p in problems), problems)

    def test_one_search_is_not_enough(self):
        with TempData() as data:
            edit(data / self.FILE, r'  "Gaia DR4 exoplanet census planets per star 2026",\n', "")
            problems = problems_for(data)
        self.assertTrue(any("(planets)" in p and "one search is not enough" in p for p in problems), problems)

    def test_header_counts_must_match(self):
        with TempData() as data:
            edit(data / self.FILE, r'^records_read = 39', "records_read = 38")
            edit(data / self.FILE, r'^searches = (\d+)', "searches = 3")
            problems = problems_for(data)
        self.assertTrue(any("says 38 records were read" in p for p in problems), problems)
        self.assertTrue(any("says 3 searches" in p for p in problems), problems)

    def test_moved_needs_a_factor_with_a_revision(self):
        with TempData() as data:
            # An explanation cannot move; a factor can, but only with a revision naming the publication.
            edit(data / self.FILE, r'(record = "zoo-hypothesis"\nverdict = )"quiet"', r'\1"moved"')
            edit(data / self.FILE, r'(record = "lifetime"\nverdict = )"noted"', r'\1"moved"')
            problems = problems_for(data)
        self.assertTrue(any("zoo-hypothesis" in p and "only a factor can be 'moved'" in p for p in problems), problems)
        self.assertTrue(any("lifetime" in p and "no revision dated 2026-10-16" in p for p in problems), problems)
        self.assertTrue(any("lifetime" in p and "moved_range = false" in p for p in problems), problems)

    def test_flagged_needs_for_john_and_nothing_else_may_carry_it(self):
        with TempData() as data:
            edit(data / self.FILE, r'^for_john = ', "found_extra = ")
            problems = problems_for(data)
        self.assertTrue(any("star-formation" in p and "needs 'for_john'" in p for p in problems), problems)
        self.assertTrue(any("unknown field 'found_extra'" in p for p in problems), problems)

    def test_reused_line_must_quote_a_search_and_give_a_reason(self):
        with TempData() as data:
            edit(data / self.FILE, r'was first run for we-are-early: how often[^"]*', "was first run for we-are-early")
            problems = problems_for(data)
        self.assertTrue(any("habitable-planets" in p and "carries no reason" in p for p in problems), problems)
        with TempData() as data:
            edit(data / self.FILE, r'"\\"hard steps model evolution intelligence reanalysis 2026\\" was first run',
                 '"the hard-steps search was first run')
            problems = problems_for(data)
        self.assertTrue(any("(intelligence)" in p and "does not quote any search" in p for p in problems), problems)

    def test_file_name_is_the_date(self):
        with TempData() as data:
            (data / self.FILE).rename(data / "readings" / "first.toml")
            problems = problems_for(data)
        self.assertTrue(any("named 'first' but its id is '2026-10-16'" in p for p in problems), problems)

    def test_date_must_match_the_id(self):
        with TempData() as data:
            edit(data / self.FILE, r'^date = 2026-10-16', "date = 2026-10-17")
            problems = problems_for(data)
        self.assertTrue(any("is not the date in the id" in p for p in problems), problems)


class TheHeadline(unittest.TestCase):
    """The run command and the engine behind it (docs/method.md)."""

    # Table 1 of Sandberg, Drexler and Ord 2018, as read from the arXiv text on 2026-10-16.
    PAPER = [
        {"shape": "log-uniform", "low": 1, "high": 100},          # stars per year
        {"shape": "log-uniform", "low": 0.1, "high": 1},          # share with planets
        {"shape": "log-uniform", "low": 0.1, "high": 1},          # habitable planets per star
        {"shape": "log-normal-rate", "median": 1.0, "spread_orders": 50},  # chance life starts
        {"shape": "log-uniform", "low": 0.001, "high": 1},        # intelligence
        {"shape": "log-uniform", "low": 0.01, "high": 1},         # detectable
        {"shape": "log-uniform", "low": 100, "high": 1e10},       # lifetime in years
    ]

    def test_reproduces_the_2018_paper(self):
        """Their Table 2 'no update' row: median 0.32, 52% alone in the galaxy, 38% alone in the
        observable universe (N below one in ten to the ten), mean 27 million."""
        samples = compute.simulate(self.PAPER, runs=100_000, seed=1961)
        r = compute.summarise(samples, galaxies=1e10)
        self.assertGreater(r["median"], 0.2)
        self.assertLess(r["median"], 0.5)
        self.assertAlmostEqual(r["alone_in_galaxy"], 0.52, delta=0.02)
        self.assertAlmostEqual(r["alone_in_universe"], 0.38, delta=0.02)
        self.assertGreater(r["mean"], 1e6)
        self.assertLess(r["mean"], 1e9)

    def test_same_seed_same_numbers(self):
        a = compute.simulate(self.PAPER, runs=2_000, seed=7)
        b = compute.simulate(self.PAPER, runs=2_000, seed=7)
        c = compute.simulate(self.PAPER, runs=2_000, seed=8)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_draws_stay_inside_their_range(self):
        rng = compute.random.Random(1)
        for _ in range(2_000):
            x = compute.draw({"shape": "log-uniform", "low": 0.01, "high": 1}, rng)
            self.assertTrue(0.01 <= x <= 1, x)
            y = compute.draw({"shape": "uniform", "low": 2, "high": 5}, rng)
            self.assertTrue(2 <= y <= 5, y)
            z = compute.draw({"shape": "log-normal-rate", "median": 1.0, "spread_orders": 50}, rng)
            self.assertTrue(0 <= z <= 1, z)

    def test_log_uniform_spreads_evenly_across_powers_of_ten(self):
        rng = compute.random.Random(3)
        xs = [compute.draw({"shape": "log-uniform", "low": 1, "high": 1000}, rng) for _ in range(30_000)]
        below_ten = sum(1 for x in xs if x < 10) / len(xs)
        self.assertAlmostEqual(below_ten, 1 / 3, delta=0.02)

    def test_unknown_shape_is_refused(self):
        with self.assertRaises(ValueError):
            compute.draw({"shape": "triangular", "low": 1, "high": 2}, compute.random.Random(0))

    def test_quantile_and_share_below(self):
        s = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(compute.quantile(s, 0.5), 2.0)
        self.assertEqual(compute.quantile(s, 1.0), 4.0)
        self.assertEqual(compute.share_below(s, 2.5), 0.5)
        self.assertEqual(compute.share_below(s, 0.5), 0.0)
        self.assertEqual(compute.share_below(s, 10), 1.0)

    def test_estimate_extremes(self):
        factor = {"estimate": [{"value": 1}, {"low": 0.2, "high": 0.5}, {"value": 0.3}]}
        self.assertEqual(compute.estimate_extremes(factor), (0.2, 1.0))

    def test_headline_from_the_records(self):
        loaded = compute.load_and_validate(DATA, history=False)
        h = compute.headline(loaded, runs=20_000, seed=1)
        self.assertEqual(len(h["ranges"]), 7)
        self.assertEqual([r["id"] for r in h["ranges"]], compute.FACTOR_ORDER)
        for key in ("median", "mean", "alone_in_galaxy", "alone_in_universe", "percentiles",
                    "histogram", "extremes", "method", "computed_on"):
            self.assertIn(key, h)
        self.assertTrue(0 <= h["alone_in_galaxy"] <= 1)
        self.assertTrue(0 <= h["alone_in_universe"] <= h["alone_in_galaxy"])
        self.assertLess(h["extremes"]["from_estimates"]["pessimist"], h["extremes"]["from_estimates"]["optimist"])
        self.assertLess(h["extremes"]["from_ranges"]["pessimist"], h["extremes"]["from_ranges"]["optimist"])
        self.assertAlmostEqual(sum(b["share"] for b in h["histogram"]), 1.0, places=6)
        rows = h["life_sensitivity"]
        self.assertEqual(len(rows), len(compute.LIFE_ALTERNATIVES))
        self.assertEqual(sum(1 for r in rows if r["in_use"]), 1)
        in_use = next(r for r in rows if r["in_use"])
        self.assertAlmostEqual(in_use["alone_in_galaxy"], h["alone_in_galaxy"])
        life = next(r for r in h["ranges"] if r["id"] == "life")
        self.assertEqual(life["shape"], "log-normal-rate")
        self.assertAlmostEqual(life["middle"], 1 - compute.math.exp(-1), places=9)

    def test_run_command_writes_the_json(self):
        with TempData() as data:
            out = data.parent / "headline.json"
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run", "--runs", "5000", "--out", str(out)])
            self.assertEqual(code, 0, e.getvalue())
            self.assertIn("Chance we are alone in the galaxy", o.getvalue())
            written = compute.json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(written["runs"], 5000)
        self.assertEqual(written["method"]["seed"], compute.SEED)

    def test_run_writes_data_headline_json_by_default(self):
        with TempData() as data:
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run", "--runs", "2000"])
            self.assertEqual(code, 0, e.getvalue())
            self.assertTrue((data / "headline.json").exists())

    def test_run_says_factors_not_seeded_when_one_is_missing(self):
        with TempData() as data:
            (data / "factors" / "lifetime.toml").unlink()
            for reading in (data / "readings").glob("*.toml"):
                reading.unlink()   # the first reading read the lifetime; without the record it cannot pass
            o, e = io.StringIO(), io.StringIO()
            with redirect_stdout(o), redirect_stderr(e):
                code = compute.main(["--data", str(data), "run"])
        self.assertEqual(code, 2)
        self.assertIn("not seeded yet", o.getvalue())
        self.assertIn("6 of 7", o.getvalue())
        self.assertIn("lifetime", o.getvalue())

    def test_run_refuses_invalid_data(self):
        with TempData() as data:
            edit(data / "explanations" / "dark-forest.toml", r'^family = "unseen"\n', "")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = compute.main(["--data", str(data), "run"])
        self.assertEqual(code, 1)
        self.assertIn("Refusing to run", err.getvalue())


class TheServedHeadline(unittest.TestCase):
    """The export copies the headline file into the site's public folder, byte for byte, so the
    built site serves it at /data/headline.json (added 2026-10-17 at John's ruling on the family's
    lessons review); and removes a stale copy when there is no headline to serve."""

    def test_export_copies_the_headline_file_unchanged(self):
        import export
        source = DATA / "headline.json"
        self.assertTrue(source.exists(), "data/headline.json is what compute.py run writes")
        with tempfile.TemporaryDirectory() as tmp:
            out, public = Path(tmp) / "out", Path(tmp) / "public"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = export.main(["--out", str(out), "--public", str(public)])
            self.assertEqual(code, 0)
            self.assertTrue((out / "records.json").exists())
            self.assertEqual((public / "headline.json").read_bytes(), source.read_bytes())
            # The source path is for the copy only and never reaches the JSON the site reads.
            written = json.loads((out / "records.json").read_text(encoding="utf-8"))
            self.assertTrue(written["headline"]["available"])
            self.assertNotIn("_source", written["headline"])

    def test_export_removes_a_stale_copy_when_there_is_no_headline(self):
        import export
        with TempData() as data, tempfile.TemporaryDirectory() as tmp:
            (data / "headline.json").unlink()
            out, public = Path(tmp) / "out", Path(tmp) / "public"
            public.mkdir()
            (public / "headline.json").write_text("{}", encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = export.main(["--data", str(data), "--out", str(out), "--public", str(public),
                                    "--headline", str(data / "headline.json")])
            self.assertEqual(code, 0)
            self.assertFalse((public / "headline.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=1)
