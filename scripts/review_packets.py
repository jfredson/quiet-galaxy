#!/usr/bin/env python3
"""Build the packets for the outside-model review of the seven ranges (docs/reviews/protocol.md).

A packet is one file under docs/reviews/packets/ that a reviewer model reads in one call: the
brief (docs/reviews/brief.md) followed by the factor records in the packet rendered as plain text,
the claims still to be checked that touch those factors, the publications logged against them,
and the part of docs/method.md that explains the shapes. Packets are generated from the records,
never hand-written, so a packet is always the record as of its date.

    python3 scripts/review_packets.py                  write the three packets dated today
    python3 scripts/review_packets.py --date 2026-10-17  date them otherwise
    python3 scripts/review_packets.py --list           print the packets and their factors

Standard library only. Written 2026-10-17 for the first review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REVIEWS = ROOT / "docs" / "reviews"

# The three packets, by the kind of evidence each factor rests on: what telescopes measure, what
# biology argues, and what civilisations do. Protocol decision 3.
PACKETS: dict[str, tuple[str, list[str]]] = {
    "stars-and-planets": ("The three measured factors: stars born each year, the share of stars with planets, "
                          "and habitable planets per star",
                          ["star-formation", "planets", "habitable-planets"]),
    "life-and-mind": ("The two biological factors: the chance life starts and the chance it becomes intelligent",
                      ["life", "intelligence"]),
    "signals-and-lifetimes": ("The two civilisation factors: the share that become detectable and how long they stay so",
                              ["detectable", "lifetime"]),
}


def load(folder: str) -> list[dict]:
    out = []
    for path in sorted((DATA / folder).glob("*.toml")):
        with path.open("rb") as f:
            out.append(tomllib.load(f))
    return out


def fmt(x) -> str:
    """A number as a reviewer would write it: 1e-50 stays, 10000000000 becomes 10,000,000,000."""
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return f"{x:,}"
    if isinstance(x, float):
        if x == int(x) and abs(x) < 1e15:
            return f"{int(x):,}"
        if abs(x) < 1e-3:
            return f"{x:.0e}".replace("e-0", "e-").replace("e+0", "e+")
        return f"{x:g}"
    return str(x)


def render_estimate(i: int, e: dict) -> str:
    figure = fmt(e["value"]) if "value" in e else f"{fmt(e['low'])} to {fmt(e['high'])}"
    lines = [f"{i}. **{e['who']}, {e['when']}: {figure}.** {e['method'].strip()}",
             f"   Source: {e['source'].strip()}"]
    if e.get("link"):
        lines.append(f"   Link: {e['link']}")
    return "\n".join(lines)


def render_range(r: dict) -> str:
    if r["shape"] == "log-normal-rate":
        head = (f"Shape: log-normal-rate. Centre: {fmt(r['median'])} start per habitable planet over its life. "
                f"Spread: {fmt(r['spread_orders'])} powers of ten.")
    else:
        head = f"Shape: {r['shape']}. Low: {fmt(r['low'])}. High: {fmt(r['high'])}."
    return (f"{head} Status: {r['status']}. Set on {r['set_on'].isoformat()}.\n\n"
            f"The reason the record gives:\n\n{r['why'].strip()}")


def render_factor(f: dict, papers: list[dict]) -> str:
    parts = [f"## Factor {f['order']} of 7: {f['name']} ({f['symbol']})",
             f"Unit: {f['unit']}.",
             "", "### What it is", f["description"].strip(),
             "", "### What would move this", f["what_would_move_this"].strip(),
             "", "### The published estimates the record lists"]
    for i, e in enumerate(f.get("estimate") or [], 1):
        parts.append(render_estimate(i, e))
        parts.append("")
    parts += ["### The range the site uses now", render_range(f["range"]), ""]
    if f.get("notes"):
        parts += ["### The record's notes", f["notes"].strip(), ""]
    revs = f.get("revision") or []
    if revs:
        parts.append("### Revisions since the record was written")
        for r in revs:
            parts.append(f"- {r['date'].isoformat()}, {r['field']}: from {fmt(r['old'])} to {fmt(r['new'])}. {r['why'].strip()}")
        parts.append("")
    verify = list(f.get("verify") or [])
    for p in papers:
        for v in p.get("verify") or []:
            verify.append(f"(on the publication {p['id']}, {p['title']}) {v}")
    if verify:
        parts.append("### Claims still to be checked against a source")
        parts.append("Written from memory or from a secondary source and not yet confirmed; weigh them accordingly.")
        for v in verify:
            parts.append(f"- {v.strip()}")
        parts.append("")
    if papers:
        parts.append("### Publications the site has logged against this factor")
        parts.append("The site's publications log, filtered to this factor, newest first. None has moved a range.")
        for p in papers:
            authors = p["authors"]
            who = ", ".join(authors[:3]) + (" and others" if len(authors) > 3 else "")
            parts.append(f"- **{who} ({p['date']}), \"{p['title']}\", {p['venue']}.** {p['finding'].strip()}")
        parts.append("")
    return "\n".join(parts)


def method_extract() -> str:
    """The part of docs/method.md that explains what a draw is and what the shapes mean."""
    text = (ROOT / "docs" / "method.md").read_text()
    start = text.index("## What the computation does")
    end = text.index("## Reproducing the 2018 paper")
    return text[start:end].strip()


def build(name: str, date: str, factors: dict[str, dict], papers: list[dict]) -> str:
    title, ids = PACKETS[name]
    brief = (REVIEWS / "brief.md").read_text()
    brief_body = brief.split("---", 1)[1].strip()
    out = [f"# Review packet: {name} ({date})", "",
           f"{title}. Generated by `scripts/review_packets.py` from the records as committed on {date}; "
           "the brief (`docs/reviews/brief.md`) comes first, then the records, then the method extract.", "",
           brief_body, "", "---", "", f"# The records in this packet: {', '.join(factors[i]['name'] for i in ids)}", ""]
    for i in ids:
        mine = sorted((p for p in papers if i in (p.get("factors") or [])), key=lambda p: p["date"], reverse=True)
        out.append(render_factor(factors[i], mine))
        out.append("---")
        out.append("")
    out += ["# From the method document: what the computation does", "", method_extract(), ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat())
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for name, (title, ids) in PACKETS.items():
            print(f"{name}: {', '.join(ids)}")
        return 0
    factors = {f["id"]: f for f in load("factors")}
    papers = load("papers")
    (REVIEWS / "packets").mkdir(parents=True, exist_ok=True)
    for name in PACKETS:
        path = REVIEWS / "packets" / f"{args.date}-{name}.md"
        text = build(name, args.date, factors, papers)
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)} ({len(text.split()):,} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
