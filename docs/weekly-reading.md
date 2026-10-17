# The weekly reading: how the records are read against the news

Written 2026-10-16, the evening the site went live, from John's instruction that day to build it now. Adapted from The Belt Equation's scan plan and scan procedure (`~/Code/belt-equation/docs/scan-plan.md` and `scan-procedure.md`, ruled by John 2026-09-19 and audited 2026-10-06), which is what the tracker pattern (`sentient-horizons/design/tracker-pattern.md`, sections 5 and 7) asks every tracker to have. The procedure in the second half is the standalone instruction the scheduled session follows, top to bottom. The design choices in the first half are **proposed, not ruled**, each with a confidence level and the strongest alternative, per the ground rule of 2026-09-08; the cap and the schedule in particular wait on John. The first reading ran by hand the same evening (`data/readings/2026-10-16.toml`), so the site has a real reading to show.

## The idea in one paragraph

Every factor record says in one line what kind of discovery would move its range, and every explanation record says what would strengthen it and what would weaken it. Those lines are tests. Once a week a fresh session searches the web for what was published against each test, writes down for every record what it searched, what it found and one of four verdicts, logs every paper that bears on a test in the publications log, moves a range only when the evidence meets a factor's test and the move is small, reruns the headline, and commits. The site rebuilds from the commit. The point of recording the weeks when nothing happened is the same as the Belt Equation's: a reader can see the records being watched instead of taking it on faith, and the publications log grows into the dated record of the science that the kickoff promised.

## What the reading does and does not do

**It may:**

- log a publication (a new record under `data/papers/`, `added_on` the reading's date, `moved_range` false unless the same reading moved a range on it);
- move one end of a factor's range by at most the cap below, toward a number a logged publication gives, with a revision entry naming that publication, and set that publication's `moved_range` to true;
- rerun the headline (`scripts/compute.py run`) and commit `data/headline.json`;
- write the reading record and the changelog line, and commit and push.

**It may not:**

- edit a `verify` list (the claims-to-check lists belong to the sessions that clear them; the reading only reads them, so that it does not log as new a paper a claim already names);
- change a test: a factor's `what_would_move_this`, an explanation's `would_strengthen` or `would_weaken`;
- change any other text in a factor or explanation record (names, descriptions, bodies, standing, related, notes), add or retire a record, or add an estimate to a factor's estimate list;
- move a range past the cap, change a range's shape, or touch the centre or spread of the range for the chance life starts (its shape was ruled by John on 2026-10-16, and its centre and spread are the outside review's to argue);
- promote a range from `first-pass` to `reviewed`;
- edit a publication record that already exists, or a reading record;
- resolve anything about an explanation beyond logging what bears on it (an explanation has no number to move).

Anything it would have done outside these limits it writes up as a `flagged` item with a `for_john` line saying the move it would have made and why, and makes no edit.

## The four verdicts

| Verdict | Meaning | What the record carries |
|---|---|---|
| `quiet` | Nothing in the window bears on the test. `found` may still say what was seen and why it falls short. | the searches and `found` |
| `noted` | Something bears on the test, and it is logged as a publication, but no range moves. For an explanation, this is as far as a reading can go. | `sources`, `publications` (at least one, with `moved_range` false) |
| `moved` | A factor only. The evidence meets the factor's test closely enough to move an end of its range, within the cap. | `sources`, `publications` (the one the range moved on, with `moved_range` true), a revision on the factor dated the reading's day naming it, and a rerun headline |
| `flagged` | Something the reading may not do on its own: a move past the cap, a test that no longer fits what was found, a publication whose number sits outside the range, anything about the shape of a range. | `sources`, `for_john`, and the publication logged if there is one |

The Belt Equation has a fifth verdict, `resolved`, for a step that came true. Nothing here resolves: a factor's range moves, and an explanation is strengthened or weakened by what the log accumulates, so four is enough.

## The cap (proposed, not ruled)

A reading may move one end of a log-uniform or uniform range by at most **one tenfold step** per reading (from 10 to 100, or 0.01 to 0.001), in one direction, toward a number that a publication it logs gives for that factor. It may not move an end past the most extreme published estimate in that direction. The range for the chance life starts (the log-normal-rate shape) is off limits entirely.

## The reading record

One file per reading under `data/readings/`, named for the Pacific date it ran (`2026-10-16.toml`; `2026-10-16-2.toml` for a second run the same day), written once and never edited. It is the fifth kind of record, laid out in `docs/record-schema.md` and checked by `scripts/compute.py validate` with the other four, so the site refuses to build on a reading that does not add up. Its header says when it ran, who ran it (`scheduled` or `hand`), what window the searches covered, how many records were read, how many distinct searches were run, and the commit the records were read at. Then one `[[item]]` per record, in the order read, with the searches, what was found in one to three plain sentences, the verdict, the sources, the publications logged, and the `for_john` line on a flagged item. A search first run for another record may be listed again with a `reused` line saying why it bears on this one (the Belt Equation's rule of 2026-10-06: a search counts only where it was aimed).

## What the reader sees

- **The strip on the home page**, under the headline: "Last checked 16 October 2026: 39 records read, nothing moved, one left for me", linking to the reading page.
- **The reading page** (`/reading/`, "This week's reading" in the top bar's heavier tier, as the tracker pattern's rule 4.6 asks): the latest reading at the top with its counts; a "waiting on me" list of flagged items nothing has picked up; every item grouped under the seven pieces and then the three families, each a card with the verdict as a badge, the found sentence, the publications it logged and the searches it ran; the key to the four verdicts at the foot; earlier readings collapsed below.
- **On each factor and explanation page**, its last three readings, each a line that opens to the found sentence and the sources.

The page, the strip, the badges and the last-three-readings list are copied from The Belt Equation's radar page, scan strip and node page, with a comment in each file saying so.

## Design choices, with confidence and alternatives

Proposed by Claude on 2026-10-16. Nothing here is settled until John says so.

| # | Choice | Confidence | Standard or judgment | Strongest alternative and its cost |
|---|---|---|---|---|
| 1 | **Every record, every week**: all seven factors and every explanation (39 records on 2026-10-16), two to four searches each, with a search allowed to serve several records when their tests name the same evidence, listed under each with a `reused` reason. | Moderate. The explanations' tests overlap heavily (a detected civilisation, a second origin of life, a waste-heat survey), so 39 records cost about 80 distinct searches, which is what the first reading took and inside what the Belt Equation's whole-tree scan does monthly. | Judgment. | The Belt Equation's split: factors every week, explanations on the first reading of the month. Cheaper by two thirds most weeks, at the cost of an explanation page whose last reading can be five weeks old, and of a split the reader has to be told about. If the weekly run proves too slow or thin, switch to the split. |
| 2 | **Four verdicts, and `noted` means logged.** A reading never says "something relevant happened" without putting it in the publications log, so the log is the one place the science accumulates. | Moderate. It keeps the kickoff's promise that the log holds every paper that bears on the calculation from launch onward, and the validator can check it (a noted item names a publication that exists). | Judgment. | The Belt Equation's `noted` without a ledger entry unless widely reported. Fewer records to write, at the cost of findings that live only in the reading file and never reach a factor or explanation page. |
| 3 | **The cap: one tenfold step per end per reading, toward a logged publication's number, never past the most extreme published estimate, never the shape, never the chance life starts.** | Moderate; John ruled for autonomy with after-the-fact review on The Belt Equation, and this is the same bargain with a cap that fits ranges spanning powers of ten. The first reading found one case where it would have applied (the star-formation rate) and flagged it instead, so the cap is untested. | Judgment. | Half a step (a factor of about three), which would have let the star-formation top rise from 10 to 30 and no further; or propose-only, every move a flagged item. John rejected propose-only for the Belt Equation on 2026-09-19 as a gate that does not earn its place, and the same reasoning applies: the log is append-only and every move is a revision with a date, so a mistake costs one correcting revision. |
| 4 | **A fifth kind of record in `data/readings/`, validated by `compute.py` with the other four.** | High. The validator already refuses any folder of TOML it does not know, and "every record passes the validator" is the project's rule; the reading has an id, a file named for it, cross-references (records, publications) that must resolve, and a history check (a reading that disappears must be retired), all of which the existing machinery gives for free. | Standard: one validator for all the data. | A file outside the four kinds, checked by the export script as the Belt Equation does. Keeps `compute.py` smaller, at the cost of two validators and a reading that `compute.py validate` would not see. |
| 5 | **Schedule: Saturdays at 19:00 Pacific**, a day before the Belt Equation's Sunday scan, so the two never compete and both are on the record by Monday. | Low; any slot works, and the cost of changing it is one field on the routine. | Judgment. | Sunday 18:00 Pacific, the Belt Equation's slot, which keeps the family on one rhythm at the cost of two cloud sessions pushing at once and two reports landing together. |
| 6 | **The reading does not work the `verify` lists.** It reads them so that it does not log as new a paper a claim already names, and it may not edit them. The Belt Equation's rule (ruled 2026-10-06) gives every claim its own search each week; here there were 152 claims on 2026-10-16 against the Belt's handful, and the sessions clearing them are separate. | Moderate. A departure from the Belt rule, for load. | Judgment. | The Belt rule as it stands: a search per claim per week. About 150 more searches a week until the lists are cleared, for claims that are citations rather than facts about the world. Revisit once the lists are short. |
| 7 | **A publication logged by a reading carries `added_on` the reading's date and the reading's own words in `finding`, and names the reading in `notes`.** | High; it is what the schema already says a publication is. | Standard. | None worth the name. |
| 8 | **A flagged item stays on the "waiting on me" list until a later reading reads that record again, or the record carries a revision, dated on or after the reading, whose reason names the reading's date.** Copied from the Belt Equation (its rule of 2026-10-12). | High. | Standard, for this family. | A hand-kept list of rulings, which is one more file to forget. |
| 9 | **The scheduled session is a cloud routine with the repository attached, pushing to main, falling back to a `claude/reading-YYYY-MM-DD` branch when the push is refused.** The Belt Equation's arrangement, ruled 2026-09-19. The routine's prompt only says to follow this file, so the procedure can change without touching the routine. | High. | Standard, for this family. | A GitHub Action with a search key and a model key: two secrets and a script to maintain, for the same result. |
| 10 | **The reading ends with a worklog entry on the TimeAssembler project Quiet Galaxy**, through the connector attached to the routine, as the workspace rules ask of every working session. | Moderate; the Belt Equation's scan does not do this (its Monday digest does), and the connector may not be reachable from the routine, in which case the reading says so in its report and the nightly sweep backfills. | Judgment. | A separate Monday digest routine, as the Belt Equation has. Worth adding once the readings have found something worth a digest. |

Flagged for reconsideration: choice 1 is the one I would most expect to change. If the weekly run takes more than about an hour of cloud time, or the explanation items come back `quiet` for a month running, the Belt Equation's split is the better bargain.

## The procedure

The standalone instruction for the scheduled reading. A fresh Claude session with no memory of any earlier conversation follows this from top to bottom. When this file and anything else disagree, this file wins for the reading and the disagreement is a flag for John.

### 0. Orient

- Get the date in John's time zone before anything else: `TZ=America/Los_Angeles date +%F`. That is the reading's `date` and its id; every date you write is absolute (year-month-day), never "today" or "last week".
- The repository `jfredson/quiet-galaxy` is cloned in the cloud workspace; `cd` into it. Never work in the linked computer's copy at `~/Code/quiet-galaxy`; John's own sessions run there.
- Switch to main and bring it up to date with GitHub in one command: `git fetch origin && git checkout -B main origin/main`. The workspace clones onto a session branch named `claude/...` and its copy of main can be days old; the publish command refuses to push from any branch but main and refuses a main that is behind. Nothing in a fresh clone is worth keeping.
- Record `git rev-parse --short HEAD` as `commit_before`.
- Read this file, `docs/record-schema.md` (the reading record and the publication record), and `CLAUDE.md` at the root and in `~/Code` if present (plain language; absolute dates; every design choice with confidence and an alternative; a commit hook that refuses a relative date).
- The window is the time since the last reading: read the newest file in `data/readings/` and search from its date. If there is none, say so in `window` and search back over the past year.
- Load the records with Python's `tomllib` to get the list: every file under `data/factors/` and `data/explanations/`. Do not parse by hand. Every record is read every week.

### 1. Read each record against the world

For each record, factors first in equation order (`order` 1 to 7), then explanations by family (`never-there`, `gone`, `unseen`) and alphabetically by id:

1. Compose two to four web searches from the record's test: a factor's `what_would_move_this`; an explanation's `would_strengthen` and `would_weaken`. Two is a floor: at least one aimed at the kind of source the test names (a survey, a mission, a journal, a preprint server) and at least one at wider reporting, worded differently, both listed in the item's `queries`. Ask for the window. A search counts toward a record only if it was aimed at that record; a search first run for another record may be listed again with a `reused` line quoting the search as written, naming the record it was first run for, and saying in one line why it bears on this record's test. A search borrowed only to make up the number does not count; run another. Read the record's `verify` list first so that a paper a claim already names is not logged as new.
2. Read the results that bear on the test. Read the test literally: the standard is "two people reading it would agree whether this is the kind of result named". A press claim with no paper behind it, a plan, a proposal, a mission milestone and a funding announcement are not results. Check a paper's date, authors and venue on the paper's own page (arXiv, the journal) before logging it; the publication record's `verify` list is for what could not be checked.
3. Give one verdict (the table above). For `moved`, decide the new end of the range within the cap and write down which publication it moves on. For `flagged`, write `for_john`: the move you would have made and the evidence, and make no edit.

Search economy: no fewer than two searches aimed at each record, no more than four. If a search tool fails twice, mark the record `quiet` with `found = "search unavailable"` and move on.

### 2. Log the publications

For every paper or discovery a `noted`, `moved` or `flagged` item rests on, add a publication record under `data/papers/` in the layout `docs/record-schema.md` gives: id from the first author's surname and year (add a word when two collide, as `hanson-2021-grabby` does), `date` the paper's own date as text, `added_on` the reading's date, authors as on the paper (the first twelve and a count when there are more), title, venue with volume and pages where they exist, link, a `finding` of two to four plain sentences with the numbers that matter, the factors and explanations it bears on, `moved_range = false` (true only when step 3 moves a range on it), a `verify` list for anything not checked on the paper's page, and a `notes` line naming the reading. Never edit a publication record that already exists; if one is wrong, say so in the report. Check each file with `python3 -c "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))" data/papers/X.toml` and then `python3 scripts/compute.py validate`.

### 3. Move a range (`moved` only)

Edit the factor's TOML by text, keeping its layout. In `[range]`, change `low` or `high` (never both in one reading, never the shape, never `median` or `spread_orders`), set `set_on` to the reading's date, and add one sentence to the end of `why` beginning with the date and naming the publication. Append a `[[revision]]` with `date` the reading's date, `field` (`range.low` or `range.high`), `old`, `new`, `why` beginning `[reading YYYY-MM-DD]` with one sentence and the source, and `publication` the id logged in step 2; set that publication's `moved_range = true`. Run `python3 scripts/compute.py validate`. If it fails, revert the factor file (`git checkout -- data/factors/X.toml`), set the publication back to false, mark the item `flagged` with the error in `for_john`, and continue. Never edit a factor you did not mark `moved`.

### 4. Rerun the headline (only if a range moved)

`python3 scripts/compute.py run`. It validates, plays the equation out and rewrites `data/headline.json`; the seed is fixed, so the file changes only because the range did. Note the headline before and after for the changelog line and the report. If nothing moved, do not run it.

### 5. Write the reading record

Write `data/readings/YYYY-MM-DD.toml` (create the folder if absent) exactly in the layout `docs/record-schema.md` gives: `id` and `date` the reading's date, `ran_at` from `date -u +%Y-%m-%dT%H:%M:%SZ`, `run_by = "scheduled"`, `window` in one line, `records_read`, `searches` (the number of distinct searches across all items; the validator counts them), `commit_before`, then one `[[item]]` per record in the order read, with `record`, `verdict`, `queries`, `reused` where step 1 asked for it, `found` (one to three plain sentences, absolute dates), `sources` for every verdict but quiet, `publications` for noted and moved (and for flagged when one was logged), `for_john` for flagged. If the folder already has a file dated today, suffix `-2`. Run `python3 scripts/compute.py validate`; fix what it names before going on.

### 6. Changelog

Add one line under a `## YYYY-MM-DD` heading at the top of `CHANGELOG.md` (create the heading if today's is absent): "Weekly reading (scheduled task, YYYY-MM-DD): N records read, M ranges moved, K logged, F flagged for John; record at data/readings/YYYY-MM-DD.toml." Name each moved range with its before and after and the publication, and the headline before and after, in the same line.

### 7. Publish: one command

    python3 scripts/publish.py --push \
      --message "YYYY-MM-DD: weekly reading, N read, M moved, K logged, F flagged" \
      --fallback-branch claude/reading-YYYY-MM-DD

It validates, runs the tests, writes the site's data, builds the site, shows what changed, and commits everything as one commit and pushes main; the deploy action on GitHub builds and publishes the site from that push. If it stops before building, the reading's edits broke a rule: read the message, fix or revert, and run it again. If it stops at the site build for a reason that is not the records (Node missing, packages not downloading), run `python3 scripts/export.py --check`, then `git add -A && git commit` with the same message and `git push origin main`, and put the build error in the report. If the push to main is refused, the command pushes the same commit once to the fallback branch and says so; report the branch name so John can merge it, and do not retry. If that push is refused too, put the reading record's contents in the report and stop. The commit message must carry no relative or month-name date (the repository's hook refuses one).

### 8. Worklog entry

If the Time-Assembler connector is reachable, write one `progress` entry on the project "Quiet Galaxy" (id `c12ca524-a388-4aa7-8c5c-b5d2e40996aa`; `list_projects` if that fails), `repo = "quiet-galaxy"`, titled "Weekly reading YYYY-MM-DD: N read, M moved, K logged, F flagged", with the counts, each moved range, each flagged item's `for_john` line, and the branch if the push fell back. Plain language, no bare ids. If the connector is not reachable, say so in the report and skip this step; the nightly sweep backfills.

### 9. Report

Send John one short message, a numbered list and nothing else: first what he needs to do (each flagged item with its `for_john` line, and the merge if the push fell back to a branch), then one line per moved range with before and after and the headline before and after, then one line per publication logged (first author, year, what it bears on), then one line with the counts. No prose, no summary of quiet records.

### Standing rules

- Plain language, absolute dates, no bare ids (a publication id carries the paper's first author and year in words beside it).
- Read, do not infer: a range moves on a published number about its test, not on mood about the field.
- One reading, one commit, made by the publish command. Never force-push, never rebase, never touch a branch other than main and the one fallback branch.
- If anything in this file cannot be followed as written, do the parts that can, flag the rest for John in the report, and never improvise an edit outside the limits above.
