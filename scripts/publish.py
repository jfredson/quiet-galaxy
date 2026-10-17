#!/usr/bin/env python3
"""The Quiet Galaxy: publish the site with one command.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/publish.py                 validate, export and build, then stop and show what changed
    python3 scripts/publish.py --push          the same, then commit everything and push main
    python3 scripts/publish.py --push --message "2026-10-18: ..."   with your own commit message

What it does, in order, stopping at the first thing that fails:

1. Checks every record against the schema (compute.py validate) and runs the validator's tests.
2. Writes the site's data (export.py).
3. Builds the site (astro build in site/), installing its packages first if they are missing.
4. Shows what changed (git status).
5. Only with --push: fetches GitHub and stops, with nothing committed, if main here is behind
   origin/main; otherwise stages everything, commits with a dated message (or --message), and
   pushes main. The GitHub Action (.github/workflows/deploy.yml) then builds and deploys the
   site from that push. This script never deploys by any other road; `npm run deploy` in site/
   stays for a deploy from this Mac by hand.

Adapted 2026-10-16 from The Belt Equation's publish script (its 2026-09-25 version, with the
behind-origin check of 2026-10-12), without the snapshot, picture and story steps that project
has and this one does not yet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TZ = "America/Los_Angeles"


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ, TZ=TZ)
    print(f"$ {' '.join(cmd)}  (in {cwd.relative_to(ROOT) if cwd != ROOT else '.'})")
    return subprocess.run(cmd, cwd=cwd, env=env, check=check)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate, export, build, and optionally commit and push.")
    parser.add_argument("--push", action="store_true", help="commit everything and push main after building")
    parser.add_argument("--message", help="the commit message (default: a dated 'site regenerated' line)")
    args = parser.parse_args(argv)

    try:
        run([sys.executable, str(ROOT / "scripts" / "compute.py"), "validate"])
        run([sys.executable, str(ROOT / "scripts" / "test_compute.py")])
        run([sys.executable, str(ROOT / "scripts" / "export.py")])
        if not (SITE / "node_modules").exists():
            run(["npm", "ci"], cwd=SITE)
        run(["npm", "run", "build"], cwd=SITE)
    except subprocess.CalledProcessError as e:
        print(f"Stopped: a step failed (exit {e.returncode}). Nothing committed.", file=sys.stderr)
        return e.returncode or 1

    run(["git", "status", "--short"], check=False)
    if not args.push:
        print("Built. Nothing committed; run again with --push to commit and push main.")
        return 0

    run(["git", "fetch", "origin", "main"])
    behind = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    if behind not in ("", "0"):
        print(f"Stopped: main here is {behind} commit(s) behind origin/main; pull first. Nothing committed.",
              file=sys.stderr)
        return 1
    if not subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print("Nothing to commit; main is already as built.")
        return 0
    today = dt.datetime.now(ZoneInfo(TZ)).date().isoformat()
    message = args.message or f"Publish {today}: site regenerated"
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", message])
    run(["git", "push", "origin", "main"])
    print("Pushed. The deploy workflow builds and publishes the site from this push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
