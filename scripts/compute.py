#!/usr/bin/env python3
"""The Quiet Galaxy: check the records in data/ and, once the factors are seeded, compute
the headline numbers.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/compute.py validate            check every record against docs/record-schema.md
    python3 scripts/compute.py run                 compute the headline numbers (a stub until the
                                                   seven factor records exist)
    python3 scripts/compute.py --data DIR ...      use a different data folder (for tests)

"validate" reads every TOML file under data/factors, data/explanations, data/library and
data/papers, plus data/retired.toml, and lists everything that breaks a rule in plain
language: a factor with no source, an explanation with no family or no factor, a link to a
record that does not exist, a file whose name and id disagree, an id that was committed
before and has disappeared without an entry in data/retired.toml. It exits non-zero on any
failure, and nothing downstream runs until it passes.

"run" will play the Drake Equation out many thousands of times with a random draw from each
factor's range (after Sandberg, Drexler and Ord 2018) and report the median number of
detectable civilisations in the galaxy, the chance we are alone in the galaxy, the chance we
are alone in the observable universe, and the optimist-to-pessimist width. Until all seven
factor records exist it says so and stops.

Written 2026-10-16 (weekend step 2 of docs/2026-10-16-kickoff.md).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import tomllib
from pathlib import Path

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
SHAPES = {"log-uniform", "uniform"}
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
RANGE_ALLOWED = {"low", "high", "shape", "status", "set_on", "why", "sources"}
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
            for key in ("low", "high", "shape", "status", "set_on", "why"):
                if key not in rng or _empty(rng[key]):
                    problems.append(f"{tag}, range: missing {key!r}")
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
        print("The headline needs all seven; Saturday session A writes them "
              "(docs/2026-10-16-kickoff.md, weekend step 3).")
        return 2
    print("All seven factors exist, but the headline computation is not written yet "
          "(Saturday session A, docs/2026-10-16-kickoff.md, weekend step 3).")
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The Quiet Galaxy: validate the records, compute the headline.")
    parser.add_argument("--data", default=str(ROOT / "data"), help="data folder (default: the repository's data/)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="check every record against docs/record-schema.md")
    sub.add_parser("run", help="compute the headline numbers (a stub until the factors are seeded)")
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
