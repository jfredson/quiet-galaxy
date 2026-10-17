#!/usr/bin/env python3
"""The Quiet Galaxy: turn the records in data/ into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/records.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)

The records are read with the same loader and validator as scripts/compute.py, so the site can
never show a record that fails the schema: if validation fails, nothing is written and the
build stops. The site (site/) reads the JSON at build time. Nothing in the browser touches TOML.

What the JSON holds for the holding version of the site (2026-10-16): the date and source
version it was built from, the counts of each kind of record, each factor's summary and range,
the three families with their counts, and a plain reason that the headline is not computed yet.
Saturday session D widens it to the full records as the pages that need them are built.

Written 2026-10-16.
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


def short_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def build_export(loaded: dict) -> dict:
    records = loaded["records"]
    by_kind: dict[str, list[dict]] = {k: [] for k in compute.RECORD_KINDS}
    for r in records:
        by_kind[r["_kind"]].append(r)

    factors = []
    for f in sorted(by_kind["factor"], key=lambda r: r["order"]):
        rng = f.get("range")
        factors.append({
            "id": f["id"], "order": f["order"], "symbol": f["symbol"], "name": f["name"],
            "unit": f["unit"], "description": f["description"].strip(),
            "range": {"low": rng["low"], "high": rng["high"], "shape": rng["shape"],
                      "status": rng["status"], "set_on": rng["set_on"].isoformat()} if rng else None,
            "estimates": len(f.get("estimate") or []),
        })

    families = [{"key": k, "name": name,
                 "count": sum(1 for e in by_kind["explanation"] if e.get("family") == k)}
                for k, name in compute.FAMILIES.items()]

    have = {f["id"] for f in factors}
    missing = [compute.FACTORS[k][1] for k in compute.FACTOR_ORDER if k not in have]
    if missing:
        n = len(have)
        reason = (f"The numbers are not computed yet: {n} of the seven pieces {'has' if n == 1 else 'have'} "
                  f"the published estimates written up so far, and the calculation needs all seven.")
    else:
        reason = "The numbers are not computed yet: the calculation is being written."

    return {
        "exported_on": dt.datetime.now(TZ).date().isoformat(),
        "commit": short_commit(),
        "counts": {
            "factors": len(factors), "factors_expected": len(compute.FACTORS),
            "explanations": len(by_kind["explanation"]), "library": len(by_kind["library"]),
            "publications": len(by_kind["publication"]),
            "verify": sum(len(r.get("verify") or []) for r in records),
        },
        "headline": {"available": False, "reason": reason},
        "factors": factors,
        "families": families,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the site's JSON from the records in data/.")
    parser.add_argument("--data", default=str(ROOT / "data"))
    parser.add_argument("--out", default=str(ROOT / "site" / "src" / "data"))
    parser.add_argument("--check", action="store_true", help="validate and print counts, write nothing")
    args = parser.parse_args(argv)

    try:
        loaded = compute.load_and_validate(Path(args.data).resolve())
    except compute.RecordError as e:
        print("The records do not pass validation; nothing written:", file=sys.stderr)
        for line in str(e).splitlines():
            print(f"  - {line}", file=sys.stderr)
        return 1

    export = build_export(loaded)
    c = export["counts"]
    print(f"{c['factors']} of {c['factors_expected']} factors, {c['explanations']} explanations, "
          f"{c['library']} library entries, {c['publications']} publications; "
          f"{c['verify']} claim(s) to verify; version {export['commit'] or 'unknown'}")
    if args.check:
        return 0
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out / 'records.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
