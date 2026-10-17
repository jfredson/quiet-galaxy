# The Quiet Galaxy — instructions for Claude

These two rules come from The Belt Equation (`~/Code/belt-equation/CLAUDE.md`, where they
moved on 2026-10-12 from memory notes that had loaded for every project). They apply here
because this repository is built the same way: a public data-and-documentation project with
one author. The workspace `CLAUDE.md` in `~/Code` still applies on top, including plain
language everywhere and absolute year-month-day dates. A commit hook (`.githooks/commit-msg`,
turned on with `git config core.hooksPath .githooks`) refuses a commit message with a
month-name, slash or relative date.

## Commit on main and push

In an interactive session, commit on `main` and push at the end of each working session,
without asking. Ruled by John 2026-09-08 for The Belt Equation, after a background-job
session left a review commit on a side branch and asked him to merge it. The repository is
a public documentation-and-data project with one author, so a branch-and-merge step is a
chore with no review benefit.

Background-job sessions cannot push to `main`. If a task here runs as a background job,
say up front that the result will land on a branch, and open a pull request so the merge
is one click.

Until the repository has a GitHub remote, say so in the closing message and leave the
commits on `main`. Creating a public repository is John's call.

## Every design choice comes with confidence and an alternative

Ruled by John 2026-09-08. Before asking John to accept any design choice (a record field, a
method, a file layout, a name), give him, as a short table or list:

1. The choice.
2. How confident you are (high, moderate or low), with a sentence on why.
3. Whether it is standard practice or a judgment call.
4. The strongest alternative and what it would cost.

Flag any proposal you would change yourself on reflection. Nothing is settled until John
says so; a proposal that has not been ruled is written up as proposed, with the date, in the
document it belongs to (`docs/record-schema.md` for the record layout). Do not reopen what
the kickoff document (`docs/2026-10-16-kickoff.md`) already proposes without saying why.

## Two things specific to this repository

- **Explanation ids are public addresses.** An explanation's `id` is the last part of its
  page address (`/explanations/dark-forest/`) and is never renamed once committed. Retire it
  in `data/retired.toml` and point at the replacement instead. The validator checks this.
- **Facts from memory are marked.** A claim written without checking it against a source
  goes in the record's `verify` list, and a later session clears it. The ranges and the
  publications log are only as good as their sources.
