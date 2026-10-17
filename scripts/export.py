#!/usr/bin/env python3
"""The Quiet Galaxy: turn the records in data/ into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/records.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)
    python3 scripts/export.py --headline FILE  read the headline numbers from another file

The records are read with the same loader and validator as scripts/compute.py, so the site can
never show a record that fails the schema: if validation fails, nothing is written and the
build stops. The site (site/) reads the JSON at build time. Nothing in the browser touches TOML.

What the JSON holds (widened 2026-10-16 for the first full version of the site, weekend step 6
of docs/2026-10-16-kickoff.md):

- the date and source version it was built from, and the counts of each kind of record, from
  the same loaded records the validator passed, so the site and the validator always agree;
- every factor in full (its estimates, range, revisions, claims to verify), with the
  explanations, publications and library entries that point at it gathered here, so a page
  never has to search the other records; the seven factors are listed in equation order with a
  placeholder for any whose record does not exist yet, so the equation page can show all seven;
- every explanation in full, grouped by family, with its library entries and publications and
  the explanations that list it as related gathered the same way;
- every library entry and every publication, the publications newest first by the date they
  were logged, which is the order the "story so far" page reads them in;
- the calculator's slider travel for each factor (how far the slider can go, not an estimate);
- the headline numbers, read from the output of `compute.py run` when it exists (see
  load_headline below), otherwise a plain reason that they are not computed yet.

The one-way links between records (docs/record-schema.md: a library entry names its
explanations, a publication names its factors, nothing links back) are turned into both-way
lists here, at build time, which is the arrangement the schema's decision 6 assumes.

Written 2026-10-16; widened the same day.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Los_Angeles")

# Plain names for the seven factors, used on the equation page for a factor whose record does
# not exist yet. A record's own name replaces these as soon as it is written.
PLAIN_NAMES: dict[str, str] = {
    "star-formation": "How many stars are born in the galaxy each year",
    "planets": "The share of stars that have planets",
    "habitable-planets": "Planets per star that could support life",
    "life": "The share of those planets on which life starts",
    "intelligence": "The share of those on which life becomes intelligent",
    "detectable": "The share of intelligent species that make themselves detectable",
    "lifetime": "How long they stay detectable, in years",
}

# How far each slider on the calculator can travel, low to high, on a scale where every tenfold
# step is the same width. This is the slider's travel and nothing more: not an estimate, not a
# range the project uses. The ranges the project uses come from the factor records and are
# marked on the slider. The travel is wide enough to hold every published estimate the kickoff
# document lists, with room on each side.
SLIDERS: dict[str, tuple[float, float]] = {
    "star-formation": (0.1, 1000.0),
    "planets": (0.001, 1.0),
    "habitable-planets": (0.001, 100.0),
    "life": (1e-9, 1.0),
    "intelligence": (1e-9, 1.0),
    "detectable": (1e-4, 1.0),
    "lifetime": (10.0, 1e10),
}

# The three families in the order the explanations index shows them: the equation's own order,
# from "the factors before L are small" to "the silence is about us".
FAMILY_ORDER = ["never-there", "gone", "unseen"]
FAMILY_BLURBS: dict[str, str] = {
    "never-there": "Explanations that say the early pieces of the equation are small: planets like ours, "
                   "life, or intelligence are rarer than they look, so nobody else ever arose nearby.",
    "gone": "Explanations that say others arose but did not last: the last piece of the equation, how "
            "long a civilisation stays detectable, is short.",
    "unseen": "Explanations that leave the equation alone and say the silence is about us: they are out "
              "there, and we cannot see them, have not looked properly, or are being kept from looking.",
}

LIBRARY_KIND_NAMES: dict[str, str] = {
    "book": "Book", "story": "Short story", "film": "Film", "television": "Television",
    "game": "Game", "video": "Video", "essay": "Essay",
}


def short_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def clean(value):
    """Make a record JSON-safe: dates become year-month-day text, private keys are dropped."""
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return value


def text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


# ---------------------------------------------------------------- the headline


def load_headline(data_dir: Path, path: Path | None) -> dict | None:
    """Read the headline numbers written by `compute.py run`, if they exist.

    `compute.py run` is Saturday session A's work. This reads its output from
    data/headline.json (or --headline FILE) and accepts these keys, every one optional except the
    first three: median (detectable civilisations in the galaxy, the middle of the spread),
    alone_galaxy (chance we are the only one in the galaxy, 0 to 1), alone_universe (the same for
    the observable universe), optimist and pessimist (N with every factor at its most hopeful and
    its most pessimistic published estimate), runs (how many draws), computed_on (year-month-day),
    seed, note. A file that lacks the first three is reported and ignored, so a half-written run
    never puts a number on the home page.
    """
    candidates = [path] if path else [data_dir / "headline.json", ROOT / "data" / "headline.json"]
    for cand in candidates:
        if cand is None or not cand.exists():
            continue
        try:
            raw = json.loads(cand.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"note: {cand} could not be read as the headline file ({e}); the headline is left uncomputed",
                  file=sys.stderr)
            return None
        # The run may nest its results; look one level down for the keys.
        src = raw.get("headline", raw) if isinstance(raw, dict) else {}
        aliases = {
            "median": ("median", "median_n", "n_median"),
            "alone_galaxy": ("alone_galaxy", "p_alone_galaxy", "chance_alone_galaxy"),
            "alone_universe": ("alone_universe", "p_alone_universe", "chance_alone_universe"),
            "optimist": ("optimist", "optimistic", "n_optimist", "high"),
            "pessimist": ("pessimist", "pessimistic", "n_pessimist", "low"),
            "runs": ("runs", "draws", "samples"),
            "computed_on": ("computed_on", "date", "run_on"),
            "seed": ("seed",),
            "note": ("note", "notes"),
        }
        out: dict = {}
        for key, names in aliases.items():
            for n in names:
                if n in src and src[n] is not None:
                    out[key] = src[n]
                    break
        if not all(k in out for k in ("median", "alone_galaxy", "alone_universe")):
            print(f"note: {cand} has no median, alone_galaxy and alone_universe; the headline is left uncomputed",
                  file=sys.stderr)
            return None
        out["available"] = True
        out["file"] = str(cand.relative_to(ROOT)) if cand.is_relative_to(ROOT) else str(cand)
        if isinstance(out.get("computed_on"), str) is False and "computed_on" in out:
            out["computed_on"] = str(out["computed_on"])
        return out
    return None


# ---------------------------------------------------------------- the export


def build_export(loaded: dict, headline: dict | None = None) -> dict:
    records = loaded["records"]
    by_kind: dict[str, list[dict]] = {k: [] for k in compute.RECORD_KINDS}
    for r in records:
        by_kind[r["_kind"]].append(r)
    factors_by_id = {f["id"]: f for f in by_kind["factor"]}
    explanations_by_id = {e["id"]: e for e in by_kind["explanation"]}
    publications_by_id = {p["id"]: p for p in by_kind["publication"]}

    # ---- back-links, gathered once
    pubs_for_factor: dict[str, set[str]] = {k: set() for k in compute.FACTORS}
    pubs_for_explanation: dict[str, set[str]] = {k: set() for k in explanations_by_id}
    for p in by_kind["publication"]:
        for f in p.get("factors") or []:
            pubs_for_factor.setdefault(f, set()).add(p["id"])
        for e in p.get("explanations") or []:
            pubs_for_explanation.setdefault(e, set()).add(p["id"])
    for f in by_kind["factor"]:
        for e in f.get("estimate") or []:
            if e.get("publication"):
                pubs_for_factor[f["id"]].add(e["publication"])
        for s in (f.get("range") or {}).get("sources") or []:
            pubs_for_factor[f["id"]].add(s)
        for rev in f.get("revision") or []:
            if rev.get("publication"):
                pubs_for_factor[f["id"]].add(rev["publication"])

    library_for_factor: dict[str, set[str]] = {k: set() for k in compute.FACTORS}
    library_for_explanation: dict[str, set[str]] = {k: set() for k in explanations_by_id}
    for item in by_kind["library"]:
        for f in item.get("factors") or []:
            library_for_factor.setdefault(f, set()).add(item["id"])
        for e in item.get("explanations") or []:
            library_for_explanation.setdefault(e, set()).add(item["id"])

    explanations_for_factor: dict[str, list[dict]] = {k: [] for k in compute.FACTORS}
    related_in: dict[str, set[str]] = {k: set() for k in explanations_by_id}
    for e in by_kind["explanation"]:
        for b in e.get("bears_on") or []:
            explanations_for_factor.setdefault(b["factor"], []).append(
                {"id": e["id"], "name": e["name"], "family": e["family"], "direction": b["direction"]})
        for r in e.get("related") or []:
            related_in.setdefault(r, set()).add(e["id"])

    # Which revisions name each publication (the "moved a range" cross-check, schema rule 9).
    revisions_for_pub: dict[str, list[dict]] = {k: [] for k in publications_by_id}
    for f in by_kind["factor"]:
        for rev in f.get("revision") or []:
            if rev.get("publication") in revisions_for_pub:
                revisions_for_pub[rev["publication"]].append({
                    "factor": f["id"], "factor_name": f["name"], "date": rev["date"].isoformat(),
                    "field": rev["field"], "old": rev["old"], "new": rev["new"], "why": text(rev["why"]),
                })

    def pub_brief(pid: str) -> dict:
        p = publications_by_id.get(pid)
        if not p:
            return {"id": pid, "title": pid, "date": "", "added_on": "", "authors": [], "moved_range": False,
                    "path": f"/story/#{pid}"}
        return {"id": p["id"], "title": p["title"], "date": p["date"], "added_on": p["added_on"].isoformat(),
                "authors": list(p.get("authors") or []), "moved_range": bool(p.get("moved_range")),
                "link": p.get("link", ""), "path": f"/story/#{p['id']}"}

    def pub_sort_key(pid: str):
        p = publications_by_id.get(pid)
        return (p["added_on"].isoformat() if p else "", p["date"] if p else "")

    def library_brief(lid: str) -> dict:
        item = next((x for x in by_kind["library"] if x["id"] == lid), None)
        if not item:
            return {"id": lid, "title": lid, "maker": "", "year": 0, "kind": "", "kind_name": "", "path": f"/library/#{lid}"}
        return {"id": item["id"], "title": item["title"], "maker": item["maker"], "year": item["year"],
                "kind": item["kind"], "kind_name": LIBRARY_KIND_NAMES.get(item["kind"], item["kind"]),
                "path": f"/library/#{item['id']}"}

    def explanation_brief(eid: str) -> dict:
        e = explanations_by_id.get(eid)
        if not e:
            return {"id": eid, "name": eid, "family": "", "path": f"/explanations/{eid}/"}
        return {"id": e["id"], "name": e["name"], "family": e["family"], "family_name": compute.FAMILIES[e["family"]],
                "summary": text(e["summary"]), "path": f"/explanations/{e['id']}/"}

    def factor_brief(fid: str) -> dict:
        order, symbol, unit = compute.FACTORS[fid]
        f = factors_by_id.get(fid)
        return {"id": fid, "order": order, "symbol": symbol, "unit": unit,
                "name": f["name"] if f else PLAIN_NAMES[fid], "exists": f is not None,
                "path": f"/factors/{fid}/"}

    # ---- the seven factors, in equation order, with a placeholder for any not yet written
    factors = []
    for fid in compute.FACTOR_ORDER:
        order, symbol, unit = compute.FACTORS[fid]
        f = factors_by_id.get(fid)
        base = {
            "id": fid, "order": order, "symbol": symbol, "unit": unit, "exists": f is not None,
            "name": f["name"] if f else PLAIN_NAMES[fid], "path": f"/factors/{fid}/",
            "file": f"data/factors/{fid}.toml" if f else None,
            "slider": {"low": SLIDERS[fid][0], "high": SLIDERS[fid][1]},
            "explanations": sorted(explanations_for_factor.get(fid, []), key=lambda x: x["name"]),
            "publications": [pub_brief(p) for p in sorted(pubs_for_factor.get(fid, set()), key=pub_sort_key, reverse=True)],
            "library": [library_brief(l) for l in sorted(library_for_factor.get(fid, set()))],
        }
        if f is None:
            base.update({"description": "", "what_would_move_this": "", "estimates": [], "range": None,
                         "revisions": [], "verify": [], "notes": ""})
            factors.append(base)
            continue
        rng = f["range"]
        estimates = []
        for e in f.get("estimate") or []:
            est = clean(dict(e))
            est["source"] = text(est.get("source"))
            est["method"] = text(est.get("method"))
            if est.get("publication"):
                est["publication_brief"] = pub_brief(est["publication"])
            estimates.append(est)
        base.update({
            "description": text(f["description"]),
            "what_would_move_this": text(f["what_would_move_this"]),
            "estimates": estimates,
            "range": {
                "low": rng["low"], "high": rng["high"], "shape": rng["shape"], "status": rng["status"],
                "set_on": rng["set_on"].isoformat(), "why": text(rng["why"]),
                "sources": [pub_brief(s) for s in rng.get("sources") or []],
            },
            "revisions": [dict(clean(rev), why=text(rev.get("why")),
                               publication_brief=pub_brief(rev["publication"]) if rev.get("publication") else None)
                          for rev in (f.get("revision") or [])],
            "verify": list(f.get("verify") or []),
            "notes": text(f.get("notes")),
        })
        factors.append(base)

    # ---- the explanations, in full, and the three families
    explanations = []
    for e in sorted(by_kind["explanation"], key=lambda r: r["name"].lower()):
        explanations.append({
            "id": e["id"], "name": e["name"], "family": e["family"],
            "family_name": compute.FAMILIES[e["family"]], "path": f"/explanations/{e['id']}/",
            "file": f"data/explanations/{e['id']}.toml",
            "proposed_by": e["proposed_by"], "proposed_in": e["proposed_in"],
            "proposed_source": text(e.get("proposed_source")),
            "summary": text(e["summary"]), "body": text(e["body"]),
            "standing": text(e.get("standing")),
            "would_strengthen": text(e["would_strengthen"]), "would_weaken": text(e["would_weaken"]),
            "bears_on": [dict(b, **factor_brief(b["factor"])) for b in e["bears_on"]],
            "related": [explanation_brief(r) for r in e.get("related") or []],
            "related_in": [explanation_brief(r) for r in sorted(related_in.get(e["id"], set()))
                           if r not in (e.get("related") or [])],
            "library": [library_brief(l) for l in sorted(library_for_explanation.get(e["id"], set()))],
            "publications": [pub_brief(p) for p in sorted(pubs_for_explanation.get(e["id"], set()),
                                                          key=pub_sort_key, reverse=True)],
            "verify": list(e.get("verify") or []),
            "notes": text(e.get("notes")),
        })
    families = [{
        "key": k, "name": compute.FAMILIES[k], "blurb": FAMILY_BLURBS[k],
        "count": sum(1 for e in explanations if e["family"] == k),
        "explanations": [x["id"] for x in explanations if x["family"] == k],
    } for k in FAMILY_ORDER]

    # ---- the library, by title
    library = []
    for item in sorted(by_kind["library"], key=lambda r: r["title"].lower()):
        library.append({
            "id": item["id"], "title": item["title"], "maker": item["maker"], "year": item["year"],
            "kind": item["kind"], "kind_name": LIBRARY_KIND_NAMES.get(item["kind"], item["kind"]),
            "path": f"/library/#{item['id']}", "file": f"data/library/{item['id']}.toml",
            "explanations": [explanation_brief(x) for x in item.get("explanations") or []],
            "factors": [factor_brief(x) for x in item.get("factors") or []],
            "how": text(item["how"]), "worth_the_time": text(item["worth_the_time"]),
            "link": item.get("link", ""),
            "verify": list(item.get("verify") or []), "notes": text(item.get("notes")),
        })
    library_kinds = [{"key": k, "name": LIBRARY_KIND_NAMES[k], "count": sum(1 for x in library if x["kind"] == k)}
                     for k in LIBRARY_KIND_NAMES if any(x["kind"] == k for x in library)]

    # ---- the publications log, newest logged first, then newest published first
    publications = []
    for p in sorted(by_kind["publication"], key=lambda r: (r["added_on"].isoformat(), r["date"]), reverse=True):
        publications.append({
            "id": p["id"], "date": p["date"], "added_on": p["added_on"].isoformat(),
            "authors": list(p["authors"]), "title": p["title"], "venue": p["venue"], "link": p["link"],
            "finding": text(p["finding"]), "path": f"/story/#{p['id']}", "file": f"data/papers/{p['id']}.toml",
            "factors": [factor_brief(x) for x in p.get("factors") or []],
            "explanations": [explanation_brief(x) for x in p.get("explanations") or []],
            "moved_range": bool(p["moved_range"]),
            "revisions": revisions_for_pub.get(p["id"], []),
            "verify": list(p.get("verify") or []), "notes": text(p.get("notes")),
        })
    story_totals = {
        "entries": len(publications),
        "moved": sum(1 for p in publications if p["moved_range"]),
        "held": sum(1 for p in publications if not p["moved_range"]),
        "days": len({p["added_on"] for p in publications}),
    }

    # ---- the headline
    have = {f["id"] for f in factors if f["exists"]}
    if headline:
        head = dict(headline)
    else:
        n = len(have)
        if n < len(compute.FACTORS):
            reason = (f"The numbers are not computed yet: {n} of the seven pieces {'has' if n == 1 else 'have'} "
                      f"the published estimates written up so far, and the calculation needs all seven.")
        else:
            reason = ("The numbers are not computed yet: all seven pieces are written up, and the calculation "
                      "has not been run against them.")
        head = {"available": False, "reason": reason}

    return {
        "exported_on": dt.datetime.now(TZ).date().isoformat(),
        "commit": short_commit(),
        "counts": {
            "factors": len(have), "factors_expected": len(compute.FACTORS),
            "explanations": len(explanations), "library": len(library),
            "publications": len(publications), "retired": len(loaded.get("retired") or []),
            "verify": sum(len(r.get("verify") or []) for r in records),
            "estimates": sum(len(f["estimates"]) for f in factors),
        },
        "headline": head,
        # No weekly reading of the records against the news has run yet; the strip on the home
        # page says so in words (tracker pattern, rule 5.2). When the weekly scan exists, its
        # latest reading goes here.
        "reading": None,
        "factors": factors,
        "families": families,
        "explanations": explanations,
        "library": library,
        "library_kinds": library_kinds,
        "publications": publications,
        "story_totals": story_totals,
        "retired": clean(list(loaded.get("retired") or [])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the site's JSON from the records in data/.")
    parser.add_argument("--data", default=str(ROOT / "data"))
    parser.add_argument("--out", default=str(ROOT / "site" / "src" / "data"))
    parser.add_argument("--headline", default=None,
                        help="the JSON written by `compute.py run` (default: data/headline.json if it exists)")
    parser.add_argument("--check", action="store_true", help="validate and print counts, write nothing")
    args = parser.parse_args(argv)

    data_dir = Path(args.data).resolve()
    try:
        loaded = compute.load_and_validate(data_dir)
    except compute.RecordError as e:
        print("The records do not pass validation; nothing written:", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1

    headline = load_headline(data_dir, Path(args.headline).resolve() if args.headline else None)
    export = build_export(loaded, headline)
    c = export["counts"]
    print(f"{c['factors']} of {c['factors_expected']} factors ({c['estimates']} published estimates), "
          f"{c['explanations']} explanations, {c['library']} library entries, {c['publications']} publications; "
          f"{c['verify']} claim(s) to verify; headline {'computed' if export['headline']['available'] else 'not computed'}; "
          f"version {export['commit'] or 'unknown'}")
    if args.check:
        return 0
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out / 'records.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
