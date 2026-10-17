#!/usr/bin/env python3
"""The Quiet Galaxy: check the records in data/ and, once the factors are seeded, compute
the headline numbers.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/compute.py validate            check every record against docs/record-schema.md
    python3 scripts/compute.py run                 compute the headline numbers and write data/headline.json
    python3 scripts/compute.py run --runs N --seed S --out FILE
                                                   change the number of runs, the seed, or where the
                                                   JSON goes (--out - prints it instead)
    python3 scripts/compute.py --data DIR ...      use a different data folder (for tests)

"validate" reads every TOML file under data/factors, data/explanations, data/library and
data/papers, plus data/retired.toml, and lists everything that breaks a rule in plain
language: a factor with no source, an explanation with no family or no factor, a link to a
record that does not exist, a file whose name and id disagree, an id that was committed
before and has disappeared without an entry in data/retired.toml. It exits non-zero on any
failure, and nothing downstream runs until it passes.

"run" plays the Drake Equation out many thousands of times with a random draw from each
factor's range (after Sandberg, Drexler and Ord 2018) and reports the median number of
detectable civilisations in the galaxy, the chance we are alone in the galaxy, the chance we
are alone in the observable universe, and the optimist-to-pessimist width. It writes the
result to data/headline.json for scripts/export.py and the site. Until all seven factor
records exist it says so and stops. The parameters (number of runs, seed, galaxy count) and
the three range shapes are in docs/method.md; John ruled them on 2026-10-16.

Written 2026-10-16 (weekend step 2 of docs/2026-10-16-kickoff.md); the headline computation
added the same day (weekend step 3, Saturday session A).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent

# The seven factors of the Drake Equation: id -> (order, symbol, unit). The factor file
# repeats symbol, order and unit for readability; the validator refuses a mismatch.
FACTORS: dict[str, tuple[int, str, str]] = {
    "star-formation": (1, "R*", "stars per year"),
    "planets": (2, "fp", "fraction"),
    "habitable-planets": (3, "ne", "planets per star"),
    "life": (4, "fl", "fraction"),
    "intelligence": (5, "fi", "fraction"),
    "detectable": (6, "fc", "fraction"),
    "lifetime": (7, "L", "years"),
}
FACTOR_ORDER = sorted(FACTORS, key=lambda k: FACTORS[k][0])

# The three families of explanation: key -> plain name (the catalogue's top-level sections).
FAMILIES: dict[str, str] = {
    "never-there": "They were never there",
    "gone": "They are gone",
    "unseen": "They are there and we cannot see them",
}
DIRECTIONS = {"lowers", "raises", "unchanged"}
# The shapes a range may have. "log-normal-rate" (ruled by John 2026-10-16; decision 4 of the record
# layout anticipated it) is the 2018 paper's model for the chance life starts: the number of times
# life starts per habitable planet is log-normal with a median and a spread in powers of ten, and
# the chance is 1 - exp(-rate). It carries "median" and "spread_orders" instead of "low" and "high".
SHAPES = {"log-uniform", "uniform", "log-normal-rate"}
RANGE_STATUSES = {"first-pass", "reviewed"}
LIBRARY_KINDS = {"book", "story", "film", "television", "game", "video", "essay"}
RECORD_KINDS = {"factor", "explanation", "library", "publication"}

# Folder under data/ -> record kind.
FOLDERS: dict[str, str] = {
    "factors": "factor",
    "explanations": "explanation",
    "library": "library",
    "papers": "publication",
}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WORLD_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# Fields each kind may carry (docs/record-schema.md). Required ones are listed separately.
ALLOWED: dict[str, set[str]] = {
    "factor": {"id", "symbol", "order", "name", "unit", "description", "what_would_move_this",
               "estimate", "range", "revision", "verify", "notes"},
    "explanation": {"id", "name", "family", "proposed_by", "proposed_in", "proposed_source",
                    "summary", "body", "bears_on", "standing", "would_strengthen",
                    "would_weaken", "related", "verify", "notes"},
    "library": {"id", "title", "maker", "year", "kind", "explanations", "factors", "how",
                "worth_the_time", "link", "verify", "notes"},
    "publication": {"id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "factors", "explanations", "moved_range", "verify", "notes"},
}
REQUIRED: dict[str, list[str]] = {
    "factor": ["id", "symbol", "order", "name", "unit", "description", "what_would_move_this",
               "estimate", "range"],
    "explanation": ["id", "name", "family", "proposed_by", "proposed_in", "summary", "body",
                    "bears_on", "would_strengthen", "would_weaken"],
    "library": ["id", "title", "maker", "year", "kind", "how", "worth_the_time"],
    "publication": ["id", "date", "added_on", "authors", "title", "venue", "link", "finding",
                    "moved_range"],
}
ESTIMATE_ALLOWED = {"who", "when", "value", "low", "high", "source", "method", "link", "publication"}
RANGE_ALLOWED = {"low", "high", "median", "spread_orders", "shape", "status", "set_on", "why", "sources"}
REVISION_ALLOWED = {"date", "field", "old", "new", "why", "publication"}
RETIRED_ALLOWED = {"id", "kind", "date", "replaced_by", "why"}


class RecordError(Exception):
    """Raised with a plain-language list of everything wrong with the records."""


# ---------------------------------------------------------------- loading


def load_records(data_dir: Path) -> dict:
    """Read every record file and the retired list. Returns {"records": [...], "retired": [...]}.

    Each record is the TOML table with two extra keys: "_kind" (factor, explanation, library or
    publication) and "_path" (the file it came from). Files that cannot be read as TOML are
    reported through RecordError; nothing else is checked here.
    """
    problems: list[str] = []
    records: list[dict] = []

    def read(path: Path) -> dict | None:
        try:
            return tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            problems.append(f"{rel(path, data_dir)}: cannot be read as TOML: {e}")
            return None
        except OSError as e:
            problems.append(f"{rel(path, data_dir)}: cannot be read: {e}")
            return None

    if not data_dir.is_dir():
        raise RecordError(f"{data_dir} is not a folder")

    for folder, kind in FOLDERS.items():
        sub = data_dir / folder
        if not sub.is_dir():
            problems.append(f"{folder}/ is missing from {data_dir}")
            continue
        for path in sorted(sub.glob("*.toml")):
            table = read(path)
            if table is None:
                continue
            table["_kind"] = kind
            table["_path"] = path
            records.append(table)

    # Any other folder holding TOML is a mistake: a record in the wrong place is never read.
    for sub in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        if sub.name not in FOLDERS and any(sub.rglob("*.toml")):
            problems.append(f"{sub.name}/ is not one of the four record folders "
                            f"({', '.join(FOLDERS)}) but holds TOML files")

    retired: list[dict] = []
    retired_path = data_dir / "retired.toml"
    if retired_path.exists():
        table = read(retired_path)
        if table is not None:
            retired = table.get("retired", [])
            if not isinstance(retired, list):
                problems.append("retired.toml: 'retired' must be a list")
                retired = []
    else:
        problems.append("retired.toml is missing (it may be empty, but it must exist)")

    if problems:
        raise RecordError("\n".join(problems))
    return {"records": records, "retired": retired}


def rel(path: Path, data_dir: Path) -> str:
    try:
        return str(path.relative_to(data_dir))
    except ValueError:
        return str(path)


def ids_in_history(data_dir: Path) -> set[tuple[str, str]] | None:
    """Every (kind, id) whose file was ever committed under data_dir, read from git history.

    Returns None when the folder is not in a git repository or git is not available, in which
    case the renamed-id check is skipped with a note.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--no-renames", "--name-only",
             "--pretty=format:", "--relative", "--", "."],
            cwd=data_dir, capture_output=True, text=True, check=True, timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    seen: set[tuple[str, str]] = set()
    for line in out.splitlines():
        parts = line.strip().split("/")
        if len(parts) == 2 and parts[0] in FOLDERS and parts[1].endswith(".toml"):
            seen.add((FOLDERS[parts[0]], parts[1][: -len(".toml")]))
    return seen


# ---------------------------------------------------------------- validation


def validate(loaded: dict, previously_seen: set[tuple[str, str]] | None = None) -> list[str]:
    """Check every record against docs/record-schema.md. Returns a list of problems; empty means OK.

    previously_seen is the set of (kind, id) ever committed (ids_in_history); pass None to skip
    the renamed-id history check.
    """
    records: list[dict] = loaded["records"]
    retired: list[dict] = loaded["retired"]
    problems: list[str] = []

    def where(r: dict) -> str:
        return f"{r['_kind']} {r['_path'].name}"

    # ---- ids: shape, uniqueness, file name
    by_kind: dict[str, dict[str, dict]] = {k: {} for k in RECORD_KINDS}
    all_ids: dict[str, dict] = {}
    for r in records:
        rid = r.get("id")
        if not isinstance(rid, str) or not rid:
            problems.append(f"{where(r)}: has no id")
            continue
        if not ID_RE.match(rid):
            problems.append(f"{where(r)}: id {rid!r} is not a lowercase slug (letters, digits, single dashes)")
        if r["_path"].stem != rid:
            problems.append(f"{where(r)}: file is named {r['_path'].stem!r} but its id is {rid!r}; "
                            "ids are never renamed, and the file is named for the id")
        if rid in all_ids:
            problems.append(f"{where(r)}: id {rid!r} is also used by {where(all_ids[rid])}; ids are unique across all records")
        else:
            all_ids[rid] = r
            by_kind[r["_kind"]][rid] = r

    factor_ids = set(by_kind["factor"])
    explanation_ids = set(by_kind["explanation"])
    publication_ids = set(by_kind["publication"])

    # ---- retired list
    retired_ids: set[str] = set()
    for i, entry in enumerate(retired, 1):
        tag = f"retired.toml entry {i}"
        if not isinstance(entry, dict):
            problems.append(f"{tag}: must be a table")
            continue
        for key in entry:
            if key not in RETIRED_ALLOWED:
                problems.append(f"{tag}: unknown field {key!r}")
        for key in ("id", "kind", "date", "why"):
            if key not in entry or entry[key] in ("", None):
                problems.append(f"{tag}: missing {key!r}")
        rid = entry.get("id")
        if isinstance(rid, str):
            retired_ids.add(rid)
            if rid in all_ids:
                problems.append(f"{tag}: id {rid!r} is retired but {where(all_ids[rid])} still uses it; a retired id is never reused")
        if entry.get("kind") not in RECORD_KINDS:
            problems.append(f"{tag}: kind must be one of {sorted(RECORD_KINDS)}")
        if "date" in entry and not isinstance(entry["date"], dt.date):
            problems.append(f"{tag}: date must be a TOML date like 2026-10-16")
        rep = entry.get("replaced_by")
        if rep is not None and rep not in all_ids:
            problems.append(f"{tag}: replaced_by {rep!r} is not a record that exists")

    # ---- the renamed-id history check
    if previously_seen is not None:
        current = {(r["_kind"], r["id"]) for r in records if isinstance(r.get("id"), str)}
        for kind, rid in sorted(previously_seen - current):
            if rid not in retired_ids:
                problems.append(f"{kind} {rid!r} was committed before and is now gone, with no entry in "
                                "data/retired.toml; ids are never renamed or silently deleted")

    # ---- per-record checks
    for r in records:
        kind = r["_kind"]
        tag = where(r)
        fields = {k for k in r if not k.startswith("_")}
        for key in sorted(fields - ALLOWED[kind]):
            problems.append(f"{tag}: unknown field {key!r} (see docs/record-schema.md)")
        for key in REQUIRED[kind]:
            if key not in r or _empty(r[key]):
                problems.append(f"{tag}: required field {key!r} is missing or empty")
        _check_text_fields(r, tag, problems)
        _check_verify(r, tag, problems)

        if kind == "factor":
            _check_factor(r, tag, publication_ids, problems)
        elif kind == "explanation":
            _check_explanation(r, tag, explanation_ids, problems)
        elif kind == "library":
            _check_library(r, tag, explanation_ids, problems)
        elif kind == "publication":
            _check_publication(r, tag, explanation_ids, by_kind["factor"], problems)

    return problems


def _empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _check_text_fields(r: dict, tag: str, problems: list[str]) -> None:
    """Fields that must be text when present."""
    text_fields = {"id", "symbol", "name", "unit", "description", "what_would_move_this", "family",
                   "proposed_by", "proposed_source", "summary", "body", "standing",
                   "would_strengthen", "would_weaken", "title", "maker", "kind", "how",
                   "worth_the_time", "link", "date", "venue", "finding", "notes"}
    for key in text_fields & set(r):
        if not isinstance(r[key], str):
            problems.append(f"{tag}: {key!r} must be text")
    for key in ("order", "proposed_in", "year"):
        if key in r and (not isinstance(r[key], int) or isinstance(r[key], bool)):
            problems.append(f"{tag}: {key!r} must be a whole number")


def _check_verify(r: dict, tag: str, problems: list[str]) -> None:
    v = r.get("verify")
    if v is None:
        return
    if not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v):
        problems.append(f"{tag}: 'verify' must be a list of plain-language claims (non-empty text)")


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _check_id_list(r: dict, key: str, allowed: set[str], what: str, tag: str, problems: list[str]) -> list[str]:
    """A list field of ids that must all exist. Returns the list (empty if absent or malformed)."""
    v = r.get(key)
    if v is None:
        return []
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        problems.append(f"{tag}: {key!r} must be a list of ids")
        return []
    for x in v:
        if x not in allowed:
            problems.append(f"{tag}: {key!r} names {x!r}, which is not {what}")
    return v


def _check_factor(r: dict, tag: str, publication_ids: set[str], problems: list[str]) -> None:
    rid = r.get("id")
    if rid not in FACTORS:
        problems.append(f"{tag}: id {rid!r} is not one of the seven factors ({', '.join(FACTOR_ORDER)})")
        fraction = False
    else:
        order, symbol, unit = FACTORS[rid]
        if r.get("symbol") != symbol:
            problems.append(f"{tag}: symbol must be {symbol!r} for {rid}")
        if r.get("order") != order:
            problems.append(f"{tag}: order must be {order} for {rid}")
        if r.get("unit") != unit:
            problems.append(f"{tag}: unit must be {unit!r} for {rid}")
        fraction = unit == "fraction"

    estimates = r.get("estimate", [])
    if not isinstance(estimates, list):
        problems.append(f"{tag}: 'estimate' must be a list of [[estimate]] tables")
        estimates = []
    for i, e in enumerate(estimates, 1):
        etag = f"{tag}, estimate {i}"
        if not isinstance(e, dict):
            problems.append(f"{etag}: must be a table")
            continue
        for key in sorted(set(e) - ESTIMATE_ALLOWED):
            problems.append(f"{etag}: unknown field {key!r}")
        for key in ("who", "when", "source", "method"):
            if not isinstance(e.get(key), str) or not e[key].strip():
                problems.append(f"{etag}: has no {key} (a published estimate needs who, when, source and method)")
        if isinstance(e.get("when"), str) and not WORLD_DATE_RE.match(e["when"]):
            problems.append(f"{etag}: 'when' must be a year, year-month or full date as text, like \"1961\" or \"2012-01-12\"")
        has_value = "value" in e
        has_range = "low" in e or "high" in e
        if has_value and has_range:
            problems.append(f"{etag}: give either 'value' or 'low' and 'high', not both")
        elif has_value:
            if not _is_number(e["value"]):
                problems.append(f"{etag}: 'value' must be a number")
            elif fraction and not 0 <= e["value"] <= 1:
                problems.append(f"{etag}: a fraction's value must lie between 0 and 1")
        elif has_range:
            lo, hi = e.get("low"), e.get("high")
            if not (_is_number(lo) and _is_number(hi)):
                problems.append(f"{etag}: 'low' and 'high' must both be numbers")
            else:
                if lo > hi:
                    problems.append(f"{etag}: low ({lo}) is above high ({hi})")
                if fraction and not (0 <= lo and hi <= 1):
                    problems.append(f"{etag}: a fraction's range must lie between 0 and 1")
        else:
            problems.append(f"{etag}: has no number: give 'value' or 'low' and 'high'")
        if "link" in e and not isinstance(e["link"], str):
            problems.append(f"{etag}: 'link' must be text")
        pub = e.get("publication")
        if pub is not None and pub not in publication_ids:
            problems.append(f"{etag}: publication {pub!r} is not a publication record that exists")

    rng = r.get("range")
    if rng is not None:
        if not isinstance(rng, dict):
            problems.append(f"{tag}: 'range' must be a [range] table")
        else:
            for key in sorted(set(rng) - RANGE_ALLOWED):
                problems.append(f"{tag}, range: unknown field {key!r}")
            rate_shape = rng.get("shape") == "log-normal-rate"
            needed = ("shape", "status", "set_on", "why") + (("median", "spread_orders") if rate_shape else ("low", "high"))
            for key in needed:
                if key not in rng or _empty(rng[key]):
                    problems.append(f"{tag}, range: missing {key!r}")
            if rate_shape:
                # The 2018 paper's shape for the chance life starts: set by the median number of
                # starts per planet and the spread in powers of ten, never by low and high.
                for key in ("low", "high"):
                    if key in rng:
                        problems.append(f"{tag}, range: a log-normal-rate range has no {key!r}; "
                                        "it is set by 'median' and 'spread_orders'")
                med, spread = rng.get("median"), rng.get("spread_orders")
                if "median" in rng and (not _is_number(med) or med <= 0):
                    problems.append(f"{tag}, range: 'median' must be a number above 0 (starts of life per planet over its life)")
                if "spread_orders" in rng and (not _is_number(spread) or spread <= 0):
                    problems.append(f"{tag}, range: 'spread_orders' must be a number above 0 (powers of ten)")
                if not fraction:
                    problems.append(f"{tag}, range: the log-normal-rate shape gives a chance between 0 and 1, "
                                    "so it fits only a factor measured as a fraction")
            else:
                for key in ("median", "spread_orders"):
                    if key in rng:
                        problems.append(f"{tag}, range: {key!r} belongs only to the log-normal-rate shape")
                lo, hi = rng.get("low"), rng.get("high")
                if _is_number(lo) and _is_number(hi):
                    if lo > hi:
                        problems.append(f"{tag}, range: low ({lo}) is above high ({hi})")
                    if rng.get("shape") == "log-uniform" and lo <= 0:
                        problems.append(f"{tag}, range: a log-uniform range needs low > 0")
                    if fraction and not (0 <= lo and hi <= 1):
                        problems.append(f"{tag}, range: a fraction's range must lie between 0 and 1")
                elif "low" in rng or "high" in rng:
                    problems.append(f"{tag}, range: 'low' and 'high' must be numbers")
            if "shape" in rng and rng["shape"] not in SHAPES:
                problems.append(f"{tag}, range: shape must be one of {sorted(SHAPES)}")
            if "status" in rng and rng["status"] not in RANGE_STATUSES:
                problems.append(f"{tag}, range: status must be one of {sorted(RANGE_STATUSES)}")
            if "set_on" in rng and not isinstance(rng["set_on"], dt.date):
                problems.append(f"{tag}, range: set_on must be a TOML date like 2026-10-16")
            if "why" in rng and not isinstance(rng["why"], str):
                problems.append(f"{tag}, range: 'why' must be text")
            _check_id_list(rng, "sources", publication_ids, "a publication record that exists", f"{tag}, range", problems)

    revisions = r.get("revision", [])
    if not isinstance(revisions, list):
        problems.append(f"{tag}: 'revision' must be a list of [[revision]] tables")
        revisions = []
    for i, rev in enumerate(revisions, 1):
        rtag = f"{tag}, revision {i}"
        if not isinstance(rev, dict):
            problems.append(f"{rtag}: must be a table")
            continue
        for key in sorted(set(rev) - REVISION_ALLOWED):
            problems.append(f"{rtag}: unknown field {key!r}")
        for key in ("date", "field", "old", "new", "why"):
            if key not in rev or _empty(rev[key]):
                problems.append(f"{rtag}: missing {key!r}")
        if "date" in rev and not isinstance(rev["date"], dt.date):
            problems.append(f"{rtag}: date must be a TOML date like 2026-10-16")
        pub = rev.get("publication")
        if pub is not None and pub not in publication_ids:
            problems.append(f"{rtag}: publication {pub!r} is not a publication record that exists")


def _check_explanation(r: dict, tag: str, explanation_ids: set[str], problems: list[str]) -> None:
    fam = r.get("family")
    if fam is not None and fam not in FAMILIES:
        problems.append(f"{tag}: family must be one of {sorted(FAMILIES)}")
    bears = r.get("bears_on", [])
    if not isinstance(bears, list):
        problems.append(f"{tag}: 'bears_on' must be a list of [[bears_on]] tables")
        bears = []
    seen: set[str] = set()
    for i, b in enumerate(bears, 1):
        btag = f"{tag}, bears_on {i}"
        if not isinstance(b, dict):
            problems.append(f"{btag}: must be a table with 'factor' and 'direction'")
            continue
        for key in sorted(set(b) - {"factor", "direction"}):
            problems.append(f"{btag}: unknown field {key!r}")
        f = b.get("factor")
        if f not in FACTORS:
            problems.append(f"{btag}: factor {f!r} is not one of the seven factors ({', '.join(FACTOR_ORDER)})")
        elif f in seen:
            problems.append(f"{btag}: factor {f!r} is listed twice")
        else:
            seen.add(f)
        if b.get("direction") not in DIRECTIONS:
            problems.append(f"{btag}: direction must be one of {sorted(DIRECTIONS)}")
    related = _check_id_list(r, "related", explanation_ids, "an explanation that exists", tag, problems)
    if r.get("id") in related:
        problems.append(f"{tag}: lists itself under 'related'")


def _check_library(r: dict, tag: str, explanation_ids: set[str], problems: list[str]) -> None:
    if "kind" in r and r["kind"] not in LIBRARY_KINDS:
        problems.append(f"{tag}: kind must be one of {sorted(LIBRARY_KINDS)}")
    ex = _check_id_list(r, "explanations", explanation_ids, "an explanation that exists", tag, problems)
    fa = _check_id_list(r, "factors", set(FACTORS), "one of the seven factors", tag, problems)
    if not ex and not fa:
        problems.append(f"{tag}: names no explanation and no factor; a library entry illustrates at least one")


def _check_publication(r: dict, tag: str, explanation_ids: set[str], factors: dict[str, dict],
                       problems: list[str]) -> None:
    if isinstance(r.get("date"), str) and not WORLD_DATE_RE.match(r["date"]):
        problems.append(f"{tag}: 'date' must be a year, year-month or full date as text, like \"2018-06-06\"")
    if "added_on" in r and not isinstance(r["added_on"], dt.date):
        problems.append(f"{tag}: added_on must be a TOML date like 2026-10-16")
    authors = r.get("authors")
    if authors is not None and (not isinstance(authors, list)
                                or not all(isinstance(a, str) and a.strip() for a in authors)):
        problems.append(f"{tag}: 'authors' must be a list of names")
    ex = _check_id_list(r, "explanations", explanation_ids, "an explanation that exists", tag, problems)
    fa = _check_id_list(r, "factors", set(FACTORS), "one of the seven factors", tag, problems)
    if not ex and not fa:
        problems.append(f"{tag}: names no factor and no explanation; a publication bears on at least one")
    moved = r.get("moved_range")
    if moved is not None and not isinstance(moved, bool):
        problems.append(f"{tag}: 'moved_range' must be true or false")
    if moved is True:
        rid = r.get("id")
        named = any(rev.get("publication") == rid
                    for f in factors.values()
                    for rev in (f.get("revision") or []) if isinstance(rev, dict))
        if not named:
            problems.append(f"{tag}: says it moved a range, but no factor has a revision naming {rid!r}")


# ---------------------------------------------------------------- commands


def summary(loaded: dict) -> str:
    counts = {k: 0 for k in ("factor", "explanation", "library", "publication")}
    verify = 0
    for r in loaded["records"]:
        counts[r["_kind"]] += 1
        verify += len(r.get("verify") or [])
    seeded = sorted(r["id"] for r in loaded["records"] if r["_kind"] == "factor" and r.get("id") in FACTORS)
    lines = [
        f"{counts['factor']} of {len(FACTORS)} factors ({', '.join(seeded) or 'none'}), "
        f"{counts['explanation']} explanations, {counts['library']} library entries, "
        f"{counts['publication']} publications, {len(loaded['retired'])} retired ids",
        f"{verify} claim(s) marked to verify",
    ]
    return "\n".join(lines)


def load_and_validate(data_dir: Path, history: bool = True) -> dict:
    """Load, validate, and raise RecordError on any problem. Returns the loaded records."""
    loaded = load_records(data_dir)
    seen = ids_in_history(data_dir) if history else None
    problems = validate(loaded, seen)
    if problems:
        raise RecordError("\n".join(problems))
    loaded["_history_checked"] = seen is not None
    return loaded


def cmd_validate(args: argparse.Namespace) -> int:
    data_dir = Path(args.data).resolve()
    try:
        loaded = load_and_validate(data_dir)
    except RecordError as e:
        print(f"The records in {data_dir} do not pass (docs/record-schema.md):", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(summary(loaded))
    if not loaded["_history_checked"]:
        print("note: not in a git repository, so the renamed-id history check was skipped")
    print("OK: every record follows docs/record-schema.md")
    return 0


# ---------------------------------------------------------------- the headline
#
# The equation is N = R* x fp x ne x fl x fi x fc x L. Instead of multiplying seven single
# values, each run draws one value from every factor's range and multiplies those; many
# thousands of runs give a spread of N, and the headline numbers are read off the spread.
# Method after Sandberg, Drexler and Ord 2018 ("Dissolving the Fermi Paradox"). The
# parameters below were proposed in docs/method.md and ruled by John on 2026-10-16.

RUNS = 200_000          # how many times the equation is played out
SEED = 1961             # the year of the equation; fixed so the published numbers reproduce exactly
GALAXIES = 100_000_000_000   # Milky-Way-sized galaxies' worth of stars in the observable universe
TZ = ZoneInfo("America/Los_Angeles")

# Shapes the engine can draw from: the same three the record layout allows. "log-normal-rate"
# is the 2018 paper's model for the chance life starts (fl): the number of times life starts per
# habitable planet over its lifetime is drawn from a log-normal (the paper: median 1, spread 50
# orders of magnitude), and fl = 1 - exp(-rate). Ruled by John 2026-10-16 (docs/method.md, 7).
ENGINE_SHAPES = SHAPES


def draw(spec: dict, rng: random.Random) -> float:
    """One random value from a range spec: {"shape": ..., "low": ..., "high": ...} or, for
    log-normal-rate, {"shape": "log-normal-rate", "median": 1.0, "spread_orders": 50}."""
    shape = spec["shape"]
    if shape == "log-uniform":
        return 10 ** rng.uniform(math.log10(spec["low"]), math.log10(spec["high"]))
    if shape == "uniform":
        return rng.uniform(spec["low"], spec["high"])
    if shape == "log-normal-rate":
        rate = 10 ** rng.gauss(math.log10(spec["median"]), spec["spread_orders"])
        return -math.expm1(-rate)   # 1 - exp(-rate), exact for very small rates
    raise ValueError(f"unknown shape {shape!r}; the engine knows {sorted(ENGINE_SHAPES)}")


def simulate(specs: list[dict], runs: int = RUNS, seed: int = SEED) -> list[float]:
    """Play the equation out `runs` times: one independent draw per factor per run, multiplied.
    Returns the list of N values, one per run, in the order they were drawn."""
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(runs):
        n = 1.0
        for spec in specs:
            n *= draw(spec, rng)
        out.append(n)
    return out


def quantile(sorted_values: list[float], q: float) -> float:
    """The q-th quantile (0 to 1) of an already sorted list, by nearest rank."""
    if not sorted_values:
        raise ValueError("no values")
    i = min(len(sorted_values) - 1, max(0, math.ceil(q * len(sorted_values)) - 1))
    return sorted_values[i]


def share_below(sorted_values: list[float], threshold: float) -> float:
    """What fraction of the sorted values lie below the threshold."""
    lo, hi = 0, len(sorted_values)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] < threshold:
            lo = mid + 1
        else:
            hi = mid
    return lo / len(sorted_values)


def summarise(samples: list[float], galaxies: float = GALAXIES) -> dict:
    """The headline numbers from a list of N values.

    median: the middle estimate of detectable civilisations in the galaxy now.
    alone_in_galaxy: the share of runs with N below 1.
    alone_in_universe: the share of runs with N below 1 / galaxies, i.e. fewer than one
      civilisation across all the Milky-Way-sized galaxies' worth of stars we can see.
    Also the mean (dominated by the rare very optimistic runs, as the paper notes), a few
    percentiles, and a histogram of N by power of ten for the site to draw.
    """
    s = sorted(samples)
    runs = len(s)
    hist: dict[int, int] = {}
    for n in s:
        if n <= 0:
            key = -999
        else:
            key = math.floor(math.log10(n))
        hist[key] = hist.get(key, 0) + 1
    histogram = [{"log10_from": k if k != -999 else None, "share": c / runs}
                 for k, c in sorted(hist.items())]
    return {
        "runs": runs,
        "median": quantile(s, 0.5),
        "mean": sum(s) / runs,
        "alone_in_galaxy": share_below(s, 1.0),
        "alone_in_universe": share_below(s, 1.0 / galaxies),
        "alone_in_universe_by_galaxy_count": {
            f"{g:.0e}": share_below(s, 1.0 / g) for g in (1e10, 1e11, 1e12)
        },
        "percentiles": {str(p): quantile(s, p / 100) for p in (5, 25, 50, 75, 95)},
        "histogram": histogram,
    }


def range_spec(factor: dict) -> dict:
    """The engine spec for a factor record's [range]."""
    rng = factor["range"]
    if rng["shape"] == "log-normal-rate":
        return {"shape": "log-normal-rate", "median": float(rng["median"]), "spread_orders": float(rng["spread_orders"])}
    return {"shape": rng["shape"], "low": float(rng["low"]), "high": float(rng["high"])}


def range_ends(rng: dict) -> tuple[float, float]:
    """(pessimistic end, optimistic end) of a range, for the width from the ranges and for the
    band on the calculator. A log-uniform or uniform range has its low and high. A log-normal-rate
    range has no ends: the pessimistic end is taken as the chance when the rate is one spread
    below its median (for the paper's shape, about one in ten to the fifty), and the optimistic
    end is 1, which the chance approaches as the rate grows."""
    if rng["shape"] == "log-normal-rate":
        low_rate = float(rng["median"]) * 10 ** (-float(rng["spread_orders"]))
        return -math.expm1(-low_rate), 1.0
    return float(rng["low"]), float(rng["high"])


def range_middle(rng: dict) -> float:
    """Where a slider for this range should start: the chance at the median rate for a
    log-normal-rate range (0.63 for the paper's), the geometric middle of a log-uniform range,
    the arithmetic middle of a uniform one."""
    if rng["shape"] == "log-normal-rate":
        return -math.expm1(-float(rng["median"]))
    if rng["shape"] == "uniform":
        return (float(rng["low"]) + float(rng["high"])) / 2
    return math.sqrt(float(rng["low"]) * float(rng["high"]))


# The alternatives shown on the page for the chance life starts, so a reader can see how much
# that one factor's shape moves the headline (docs/method.md). Each is run with the other six
# factors as they are. Labels are plain words for the site; the factor's own range is marked.
LIFE_ALTERNATIVES: list[tuple[str, dict]] = [
    ("every power of ten from 0.001 up to 1 equally likely", {"shape": "log-uniform", "low": 1e-3, "high": 1.0}),
    ("every power of ten from 1 in 100,000 up to 1 equally likely", {"shape": "log-uniform", "low": 1e-5, "high": 1.0}),
    ("every power of ten from 1 in 10 to the 10 up to 1 equally likely", {"shape": "log-uniform", "low": 1e-10, "high": 1.0}),
    ("every power of ten from 1 in 10 to the 22 (one start per observable universe) up to 1 equally likely",
     {"shape": "log-uniform", "low": 1e-22, "high": 1.0}),
    ("every power of ten from 1 in 10 to the 30 up to 1 equally likely", {"shape": "log-uniform", "low": 1e-30, "high": 1.0}),
    ("every power of ten from 1 in 10 to the 50 up to 1 equally likely", {"shape": "log-uniform", "low": 1e-50, "high": 1.0}),
    ("the 2018 paper's shape: a rate centred on one start per planet, spread over fifty orders of magnitude",
     {"shape": "log-normal-rate", "median": 1.0, "spread_orders": 50.0}),
]


def life_sensitivity(specs: list[dict], runs: int, seed: int, galaxies: float) -> list[dict]:
    """The headline under each alternative for the chance life starts (factor 4), the other six
    factors unchanged. Returns one row per alternative with the three headline numbers."""
    i = FACTOR_ORDER.index("life")
    rows = []
    for label, alt in LIFE_ALTERNATIVES:
        trial = list(specs)
        trial[i] = alt
        r = summarise(simulate(trial, runs, seed), galaxies)
        rows.append({
            "label": label,
            "in_use": alt == specs[i],
            "median": r["median"],
            "alone_in_galaxy": r["alone_in_galaxy"],
            "alone_in_universe": r["alone_in_universe"],
        })
    return rows


def estimate_extremes(factor: dict) -> tuple[float, float]:
    """(most pessimistic, most optimistic) value among a factor's published estimates:
    the smallest low or value, and the largest high or value."""
    lows, highs = [], []
    for e in factor.get("estimate") or []:
        if "value" in e:
            lows.append(float(e["value"]))
            highs.append(float(e["value"]))
        else:
            lows.append(float(e["low"]))
            highs.append(float(e["high"]))
    return min(lows), max(highs)


def headline(loaded: dict, runs: int = RUNS, seed: int = SEED, galaxies: float = GALAXIES) -> dict:
    """Compute the headline from validated records (all seven factors must exist).

    The result is what data/headline.json holds and what scripts/export.py hands the site.
    """
    factors = {r["id"]: r for r in loaded["records"] if r["_kind"] == "factor"}
    missing = [f for f in FACTOR_ORDER if f not in factors]
    if missing:
        raise RecordError(f"the headline needs all seven factors; missing: {', '.join(missing)}")
    ordered = [factors[f] for f in FACTOR_ORDER]

    specs = [range_spec(f) for f in ordered]
    samples = simulate(specs, runs, seed)
    result = summarise(samples, galaxies)

    pess_est, opt_est = 1.0, 1.0
    pess_rng, opt_rng = 1.0, 1.0
    per_factor_est: dict[str, dict] = {}
    for f in ordered:
        lo, hi = estimate_extremes(f)
        per_factor_est[f["id"]] = {"pessimist": lo, "optimist": hi}
        pess_est *= lo
        opt_est *= hi
        lo_end, hi_end = range_ends(f["range"])
        pess_rng *= lo_end
        opt_rng *= hi_end

    return {
        "computed_on": dt.datetime.now(TZ).date().isoformat(),
        "method": {
            "after": "sandberg-2018",
            "runs": runs,
            "seed": seed,
            "independent_draws": True,
            "galaxies": galaxies,
            "status": "ruled by John 2026-10-16 (docs/method.md)",
        },
        "ranges": [{
            "id": f["id"], "symbol": f["symbol"], "name": f["name"], "unit": f["unit"],
            "shape": f["range"]["shape"],
            "low": range_ends(f["range"])[0], "high": range_ends(f["range"])[1],
            "median": f["range"].get("median"), "spread_orders": f["range"].get("spread_orders"),
            "middle": range_middle(f["range"]),
            "status": f["range"]["status"], "set_on": f["range"]["set_on"].isoformat(),
            "estimates": len(f.get("estimate") or []),
        } for f in ordered],
        "life_sensitivity": life_sensitivity(specs, runs, seed, galaxies),
        "any_range_first_pass": any(f["range"]["status"] == "first-pass" for f in ordered),
        **result,
        "extremes": {
            "from_estimates": {"pessimist": pess_est, "optimist": opt_est, "factors": per_factor_est},
            "from_ranges": {"pessimist": pess_rng, "optimist": opt_rng},
        },
        "verify_open": sum(len(r.get("verify") or []) for r in loaded["records"] if r["_kind"] == "factor"),
    }


def plain_number(x: float) -> str:
    """A number for the terminal: ordinary when it is between 0.001 and a million, else a power of ten."""
    if x == 0:
        return "0"
    if 0.001 <= abs(x) < 1e6:
        return f"{x:,.3g}" if abs(x) < 100 else f"{x:,.0f}"
    return f"{x:.2g}"


def describe(h: dict) -> str:
    lines = [
        f"Played out {h['runs']:,} times (seed {h['method']['seed']}), one independent draw per factor per run.",
        f"  Middle estimate of detectable civilisations in the galaxy now: {plain_number(h['median'])}",
        f"  Chance we are alone in the galaxy: {h['alone_in_galaxy']:.0%}",
        f"  Chance we are alone in the observable universe: {h['alone_in_universe']:.0%}"
        f" (taking {h['method']['galaxies']:.0e} Milky-Way-sized galaxies' worth of stars)",
        f"  Mean (pulled up by the rare optimistic runs): {plain_number(h['mean'])}",
        f"  Spread from the 5th to the 95th percentile: {plain_number(h['percentiles']['5'])} to "
        f"{plain_number(h['percentiles']['95'])}",
        f"  Most pessimistic published estimate of every factor at once: {plain_number(h['extremes']['from_estimates']['pessimist'])}",
        f"  Most optimistic published estimate of every factor at once: {plain_number(h['extremes']['from_estimates']['optimist'])}",
    ]
    if h["any_range_first_pass"]:
        lines.append("  Every range is a first pass; the outside review has not run.")
    if h["verify_open"]:
        lines.append(f"  {h['verify_open']} claim(s) in the factor records are still marked to verify.")
    return "\n".join(lines)


def cmd_run(args: argparse.Namespace) -> int:
    data_dir = Path(args.data).resolve()
    try:
        loaded = load_and_validate(data_dir)
    except RecordError as e:
        print("Refusing to run: the records do not pass validation.", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1
    have = {r["id"] for r in loaded["records"] if r["_kind"] == "factor"}
    missing = [f for f in FACTOR_ORDER if f not in have]
    if missing:
        print(f"The factors are not seeded yet: {len(have)} of {len(FACTORS)} factor records exist"
              f" ({', '.join(sorted(have)) or 'none'}).")
        print(f"Missing: {', '.join(missing)}.")
        print("The headline needs all seven.")
        return 2
    h = headline(loaded, runs=args.runs, seed=args.seed, galaxies=args.galaxies)
    print(describe(h))
    text = json.dumps(h, indent=2, ensure_ascii=False) + "\n"
    if args.out == "-":
        print(text, end="")
    else:
        out = Path(args.out) if args.out else data_dir / "headline.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The Quiet Galaxy: validate the records, compute the headline.")
    parser.add_argument("--data", default=str(ROOT / "data"), help="data folder (default: the repository's data/)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check every record against docs/record-schema.md")
    run = sub.add_parser("run", help="compute the headline numbers and write data/headline.json")
    run.add_argument("--runs", type=int, default=RUNS, help=f"how many times to play the equation out (default {RUNS:,})")
    run.add_argument("--seed", type=int, default=SEED, help=f"random seed (default {SEED})")
    run.add_argument("--galaxies", type=float, default=GALAXIES,
                     help="Milky-Way-sized galaxies' worth of stars in the observable universe (default 1e11)")
    run.add_argument("--out", default=None, help="where to write the JSON (default DATA/headline.json; '-' prints it)")
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
