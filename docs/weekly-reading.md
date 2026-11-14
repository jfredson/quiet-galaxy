# The weekly reading: how the records are read against the news

Written 2026-10-16, the evening the site went live, from John's instruction that day to build it now. Adapted from The Belt Equation's scan plan and scan procedure (`~/Code/belt-equation/docs/scan-plan.md` and `scan-procedure.md`, ruled by John 2026-09-19 and audited 2026-10-06), which is what the tracker pattern (`sentient-horizons/design/tracker-pattern.md`, sections 5 and 7) asks every tracker to have. The procedure in the second half is the standalone instruction the scheduled session follows, top to bottom. The design choices in the first half are **proposed, not ruled**, each with a confidence level and the strongest alternative, per the ground rule of 2026-09-08; the cap and the schedule in particular wait on John. The first reading ran by hand the same evening (`data/readings/2026-10-16.toml`), so the site has a real reading to show.

**Revised 2026-10-18** after the audit of the first scheduled reading (`docs/readings/audit-2026-10-17.md`), which found that run had searched only by news-style queries, opened no page, lent most records their searches from other records, left one search out of the record, and edited a test. The nine changes John ruled that day (proposals 1 to 8 and 10 of the audit; proposal 9 was skipped) are in the steps below and set out, with confidence and alternatives, in the section "Revised 2026-10-18". They apply from the reading of 2026-10-24.

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
- resolve anything about an explanation beyond logging what bears on it (an explanation has no number to move);
- edit a script, a test, the site, a document under `docs/` or the routine's own prompt. If a script or test fails for a reason the reading did not cause, step 7 says what to do instead of fixing it.

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

- **The strip on the home page**, under the headline: "Last checked 16 October 2026: 39 records read, nothing moved, one left for me", linking to the reading page. For a reading made before the 2026-10-18 changes (no `pages_opened` line) the strip says how it was checked: "by a news-style web search of the window (the preprint listing was not checked)". The words drop away once a reading carries the new lines.
- **The reading page** (`/reading/`, "This week's reading", out of the top bar since 2026-10-21 under tracker pattern rule 4.21 and linked from the home page, About, News and the footer; before that it was in the top bar; the tracker pattern's rule 4.6 puts it in the heavier tier, but John cut this site's spine to two links on 2026-10-16 for fit, so it sits in the lighter tier after the story so far until he says otherwise): the latest reading at the top with its counts and, from the reading of 2026-10-24, the lines saying how many pages it opened and what it could not see; a "waiting on me" list of flagged items nothing has picked up; every item grouped under the seven pieces and then the three families, in one column, each entry one row when closed (the name, the verdict as a badge, and the first sentence of what was found) that opens to the rest of the note, anything left for me and how it was ruled on, the publications it logged, the sources, the searches it ran and a link to the record; entries marked "Nothing new" start closed and every other verdict (Logged, no change; A range moved; Waiting on me, ruled on or not) starts open; the counts line under the page heading; the key to the four verdicts at the foot; earlier readings collapsed below, using the same rows. The one-column layout replaced the card grid on 2026-10-21, as John approved.
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

## Revised 2026-10-18

Ruled by John on 2026-10-18 (relayed by the master session), after `docs/readings/audit-2026-10-17.md`. The audit's proposal 9 (name any paper from a `verify` list that the item relied on) was skipped. Confidence and alternative for each, per the ground rule of 2026-09-08:

| # | Change | Confidence | Strongest alternative and its cost |
|---|---|---|---|
| 11 | **Each record has a search of its own and borrows at most one**, with a reason particular to its test; the validator refuses a search listed twice without a reused line, a second reused line, and the same reason twice (readings dated 2026-10-19 on). | High that the old floor was unclear (20 of 39 records had no search of their own on 2026-10-17); moderate on "at most one". | Keep the old floor and trust the wording. Costs the thing the audit found. |
| 12 | **One of each record's own searches is an arXiv listing query**, sorted by date, with the dates read. | High on the idea; untested from the cloud (the network setting). | Web search only, as before, which cannot filter by date. |
| 13 | **Pages are opened, and the first line of a run tests that they can be.** The record says how many it opened (`pages_opened`). | High. | Leave it to the run's judgment, as before: the first scheduled run opened none and said nothing. |
| 14 | **The record says what the run could not see (`limits`)**, and the reading page prints it under the window line. | Moderate that a new field is better than a longer `window` line. | A longer `window` line; no schema change. |
| 15 | **The `found` sentence names a thing seen with its date, or says nothing relevant came back**; a sentence repeated for two records is refused. | High. | Allow a stock sentence for quiet records; keeps the page shorter, hides that nothing was looked at. |
| 16 | **A run counts its own searches** and lists every one, including date checks, before it writes `searches`. | High. | None worth the name; the validator cannot see an unlisted search. |
| 17 | **The window is the last 14 days**, or since the last reading if longer. | Moderate; more to read per record and a little more noise. | The old window, which made the second reading a one-day window and left a paper missed once missed for good. |
| 18 | **When a test fails for a reason the reading did not cause, the run does not edit it**: it parks the reading on a branch and reports. The test that failed on 2026-10-17 (it assumed only one reading would ever exist) was fixed in the same commit by the run; it is now fixed in the repository. | Moderate on stopping rather than publishing. | Let the reading make a one-line fix and say so, which keeps the schedule running at the cost of the rule. |
| 19 | **The routine's prompt says web search finds and `WebFetch` opens**, and that a page that will not open is said so in the record. | Moderate. | Leave the prompt as it was. |

The reading of 2026-10-17 and the reading of 2026-10-16 are not edited; the stricter checks apply only to readings dated 2026-10-19 or later.

## Ruled 2026-11-13: journals as well as preprints

**Proposed by Claude on 2026-11-13 at John's request ("Yes, propose it"), and accepted by John the same day as written ("Accept as written"). All eight choices, 20 to 27, are ruled. They are in the procedure below (step 1a and step 5) and apply from the reading of 2026-11-14. Nature (ISSN 1476-4687), Science (1095-9203) and the Proceedings of the National Academy of Sciences (1091-6490) had their numbers checked in Crossref on 2026-11-13 and are on the list. The catch-up pass of choice 27 is a separate job, not yet run.**

**Why.** A review of the news on 2026-11-13 found three papers that bear on a record's test and were not in the publications log. Two of them had never appeared on arXiv, which is the only place the reading can search by date: Murphy and colleagues on organic carbon in the Jezero crater mudstones (Science Advances, June 2026) and Doughty and colleagues on carbon fixed on nearby planets (International Journal of Astrobiology, online 2026-09-22). Every reading since 2026-10-24 has said as much in its own `limits` line ("no journal tables of contents"). The Mars paper bears directly on the test for the chance life starts, the factor the whole answer most depends on, so this is the gap most worth closing.

**What was tested on 2026-11-13,** from John's Mac, with plain fetches and no key:

| Tried | Result |
|---|---|
| Crossref (the public catalogue that publishers register papers with), searched by words across all journals inside a date window | Too noisy to use. Neither paper came back in the first eight results; an Indonesian engineering journal named "Mars" did. |
| Europe PMC (the public catalogue of life-science papers), searched by words inside a date window | Found the Mars paper, four results in all. Did not find the astrobiology paper. |
| Crossref, one named journal at a time, by date (`https://api.crossref.org/journals/<ISSN>/works?filter=from-pub-date:...,until-pub-date:...`) | Found the Mars paper in Science Advances when a few words were added (four results). Found the astrobiology paper only when the filter was the online date (`from-online-pub-date`), because that journal registers the year alone as its publication date. |
| How much a 14-day window returns, per journal (2026-10-30 to 2026-11-13) | Astrobiology 4, Nature Astronomy 11, Icarus 49, Acta Astronautica 119, The Astrophysical Journal 212, Science Advances 243. |

**The change in one paragraph.** Once per reading, before the records are read, the run lists what a short fixed set of journals published in the window, using Crossref's per-journal listing. It reads every title from the small specialist journals, and from the large general ones only the titles a few words pick out. Any title that looks as if it bears on a record's test is opened and handed to that record, where it is judged like any arXiv candidate. The record says which journals were listed and how many titles were read.

| # | Choice | Confidence | Standard or judgment | Strongest alternative and its cost |
|---|---|---|---|---|
| 20 | **Crossref's per-journal listing by date is the tool.** | Moderate. It found both missed papers today and needs no key. It is untested from the cloud routine, though the arXiv listing is fetched the same way there and works. | Judgment. | NASA's Astrophysics Data System, which covers preprints and journals in one search and is what astronomers use. It needs a key stored on the routine, which is one more secret to keep, and it is thin on biology journals. Worth a second look if Crossref proves unreliable from the cloud. |
| 21 | **A fixed list of journals, in two groups.** Read whole: International Journal of Astrobiology (ISSN 1475-3006), Astrobiology (1531-1074), Nature Astronomy (2397-3366). Filtered by a few words (life, biosignature, habitable, extraterrestrial, technosignature, Mars, Enceladus, Europa, exoplanet): Science Advances (2375-2548), Icarus (0019-1035), Acta Astronautica (0094-5765), The Astrophysical Journal (1538-4357), and Nature, Science and the Proceedings of the National Academy of Sciences once their numbers are checked. | Moderate on having a list; low on this exact list, which is the part I expect to change after the first few runs. | Judgment. | A search by words across every journal. Tested today and it missed both papers. A longer list costs more titles to read for little gain, since most astronomy journals' papers are on arXiv already. |
| 22 | **Once per reading, not once per record.** The listing is one pass of about ten fetches; candidates are then assigned to records. | Moderate. Thirty-nine records times ten journals would be 390 fetches for the same titles. | Judgment. | Per record, as the arXiv query is. It keeps "a search counts only where it was aimed" intact, at many times the cost. Under this proposal a journal candidate is listed under the record it was handed to, with the listing address as the search. |
| 23 | **Each journal is listed twice, by publication date and by online date,** and the two lists are merged. | High. The astrobiology paper appears only under the online date. | Standard for this catalogue. | One filter only, which would have missed one of the two papers. |
| 24 | **The window for journals is the same 14 days.** | Moderate. A journal can register a paper some days after it appears, so a paper may be missed once and caught by the overlap the next week. | Judgment. | Twenty-eight days for journals. Doubles the titles read, and catches late registrations with more margin. |
| 25 | **When a publisher's page refuses the fetch, the abstract in Crossref or Europe PMC counts as the page opened,** and the record says "abstract only". Science's site refused on 2026-11-13; the abstract was readable in both catalogues. | Moderate. | Judgment. | Require the publisher's own page. That would have left the Mars paper unlogged. |
| 26 | **The reading record gains one header line, `journals_checked`,** saying which journals were listed, over which dates, and how many titles were read; the `limits` line stops saying journals were not checked. The validator and the reading page need a small change for it, made by an ordinary session and not by the reading. | Moderate that a new line is better than a longer `limits` line. | Judgment. | Put it in `limits` as prose. No change to the validator or the page, at the cost of a line the site cannot print on its own. |
| 27 | **One catch-up pass by hand, over 2026-01-01 to the day of the ruling,** with the same journals, so the log does not carry a gap from before the change. | Low to moderate; it is a few hours of a session for papers that are mostly old news. | Judgment. | No catch-up. The log simply starts covering journals from the ruling on, and says so. |

**What it costs.** About ten more fetches a run and a few hundred titles to scan, most of them plainly off the subject. No money, no key.

**What it still does not catch.** A paper in a journal that is not on the list. A press story about an older paper, such as the release of 2026-11-12 about the Mars paper of June: the web search still cannot filter by date. A result announced by a mission or an agency before any paper exists.

**Flagged for reconsideration:** choice 21, the list itself. John was offered a smaller start and chose the list as written; for the record, the three specialist journals plus Science Advances, Nature and Science would have caught both missed papers and cost about half as much.

## The procedure

The standalone instruction for the scheduled reading. A fresh Claude session with no memory of any earlier conversation follows this from top to bottom. When this file and anything else disagree, this file wins for the reading and the disagreement is a flag for John.

### 0. Orient

- Get the date in John's time zone before anything else: `TZ=America/Los_Angeles date +%F`. That is the reading's `date` and its id; every date you write is absolute (year-month-day), never "today" or "last week".
- The repository `jfredson/quiet-galaxy` is cloned in the cloud workspace; `cd` into it. Never work in the linked computer's copy at `~/Code/quiet-galaxy`; John's own sessions run there.
- Switch to main and bring it up to date with GitHub in one command: `git fetch origin && git checkout -B main origin/main`. The workspace clones onto a session branch named `claude/...` and its copy of main can be days old; the publish command refuses to push from any branch but main and refuses a main that is behind. Nothing in a fresh clone is worth keeping.
- Record `git rev-parse --short HEAD` as `commit_before`.
- Read this file, `docs/record-schema.md` (the reading record and the publication record), and `CLAUDE.md` at the root and in `~/Code` if present (plain language; absolute dates; every design choice with confidence and an alternative; a commit hook that refuses a relative date).
- The window is the **last 14 days** ending on the reading's date, or the time since the newest reading in `data/readings/` if that is longer (read that file's date). Windows overlap on purpose: a paper an earlier reading missed gets a second look, and the search tool's habit of returning the older papers first stops mattering. If there is no earlier reading, say so in `window` and search back over the past year. Say the window in `window` in one line, with its two dates.
- **Test that pages open, first.** Before any search, open one named page with `WebFetch`: `https://arxiv.org/abs/2607.09460` (a paper that exists, with a title you can check: "Project Hephaistos -- IV"). Note the result for the record's `pages_opened` line: if it opened, "opened"; if not, "none" and the error in plain words. If it did not open, continue, but every `found` sentence must then say it rests on search extracts only (see step 1) and the record's `limits` line must say that no page could be opened.
- Step 1a (the journal listing) runs once, after this step and before the first record is read.
- Load the records with Python's `tomllib` to get the list: every file under `data/factors/` and `data/explanations/`. Do not parse by hand. Every record is read every week.

### 1. Read each record against the world

For each record, factors first in equation order (`order` 1 to 7), then explanations by family (`never-there`, `gone`, `unseen`) and alphabetically by id:

1. Compose two to four searches from the record's test: a factor's `what_would_move_this`; an explanation's `would_strengthen` and `would_weaken`. Two is a floor, and this is what counts toward it (changed 2026-10-18):
   - **At least one search is the record's own**, composed for this record and listed under no other record in this reading. A search first run for another record may be listed again with a `reused` line, but **at most one per record**, quoting the search as written, naming the record it was first run for, and saying in one line **what is specific to this record's test** that the same results answer (not "the same kind of evidence"). The same reason for two records is refused. A search borrowed only to make up the number does not count; run another. The validator checks all of this for readings dated 2026-10-19 or later.
   - **At least one of the record's own searches is a preprint-listing query** (below), unless its test names only a source arXiv does not carry (a mission's own announcements, a news report); say that in `found` if so.
   - The others are web searches at wider reporting, worded differently from each other and from the listing query. Ask for the window in words.
   - **The preprint listing.** The web search tool cannot filter by date and returns older papers first, so a window cannot be searched with it alone. arXiv's own listing can: fetch `https://export.arxiv.org/api/query?search_query=all:%22Dyson+sphere%22&sortBy=submittedDate&sortOrder=descending&max_results=25` (change the words to the record's test; `all:`, `ti:` and `abs:` prefixes and `AND`/`OR` work; pause three seconds between calls) with `WebFetch`, and read the `<published>` date of each entry. A paper submitted inside the window, or in the three days before it (arXiv announces a day or two later), is a candidate; open its abstract page. List the query as written in `queries`, like any other search.
   Read the record's `verify` list first so that a paper a claim already names is not logged as new.
2. Read the results that bear on the test. Read the test literally: the standard is "two people reading it would agree whether this is the kind of result named". A press claim with no paper behind it, a plan, a proposal, a mission milestone and a funding announcement are not results. Check a paper's date, authors and venue on the paper's own page (arXiv, the journal) before logging it; the publication record's `verify` list is for what could not be checked. **Open the page behind anything you write down**: a title, a date, a number. A thing known only from a search extract is written as such ("from a search extract; page not opened") and is never logged as a publication.
3. Write the `found` sentence (one to three plain sentences) so that it **names at least one thing the searches returned, with its date and where it came from** (a title and an arXiv number, a news item), or says plainly that the searches returned nothing relevant and how far back the newest result was dated. Say, for anything that falls just outside the window or is already in the log, which it is: check the log by title and arXiv number, not by memory. A sentence that is word for word the same as another record's is refused. Then give one verdict (the table above). For `moved`, decide the new end of the range within the cap and write down which publication it moves on. For `flagged`, write `for_john`: the move you would have made and the evidence, and make no edit.

Search economy: no fewer than two searches for each record (one of them its own, at most one borrowed), no more than four. If a search tool fails twice, mark the record `quiet` with `found = "search unavailable"` and move on.

### 1a. List the journals (once per reading, before the records are read)

Added 2026-11-13 (choices 20 to 27 above, ruled by John that day). The arXiv listing shows preprints only, and some papers that bear on a test appear only in a journal. So once per reading, before step 1, list what these ten journals published in the window, using Crossref, the public catalogue that publishers register papers with. Fetch with `curl` or `WebFetch`; no key is needed; pause one second between calls.

| Group | Journal | ISSN |
|---|---|---|
| Read every title | International Journal of Astrobiology | 1475-3006 |
| Read every title | Astrobiology | 1531-1074 |
| Read every title | Nature Astronomy | 2397-3366 |
| Filtered by words | Science Advances | 2375-2548 |
| Filtered by words | Nature | 1476-4687 |
| Filtered by words | Science | 1095-9203 |
| Filtered by words | Proceedings of the National Academy of Sciences | 1091-6490 |
| Filtered by words | The Astrophysical Journal | 1538-4357 |
| Filtered by words | Icarus | 0019-1035 |
| Filtered by words | Acta Astronautica | 0094-5765 |

1. **Each journal is listed twice and the two lists merged**, because some journals register only the year as the publication date and a paper then shows up only under its online date. With `FROM` and `TO` the window's two dates:
   - `https://api.crossref.org/journals/<ISSN>/works?filter=from-pub-date:FROM,until-pub-date:TO&rows=100&select=DOI,title,published,published-online,type`
   - the same with `from-online-pub-date:FROM,until-online-pub-date:TO`.
2. **For a journal in the second group, add the words** `&query.bibliographic=life+biosignature+habitable+extraterrestrial+technosignature+Mars+Enceladus+Europa+exoplanet` to both addresses. On 2026-11-13 this left three to nine titles a journal for a 14-day window.
3. **Read every title that comes back.** A title that looks as if it bears on any record's test is a candidate. Open it: the publisher's page through the DOI first; if that refuses, the abstract in the Crossref record (`https://api.crossref.org/works/<DOI>`) or in Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<DOI>&resultType=core&format=json`) counts as the page opened, and everything written from it says "abstract only".
4. **Hand each candidate to the record whose test it bears on.** In step 1 it is judged there like any arXiv candidate. List the journal address that found it among that record's `queries`; it does not count as the record's own search or its preprint-listing query, which are still required. A journal listing that produced no candidate is not listed under any item and is not counted in `searches`; it is accounted for in `journals_checked` instead.
5. **Keep the tally for the record's `journals_checked` line** (step 5): the journals listed, the window's two dates, how many titles were read in all, how many were opened, and any journal whose listing failed. If Crossref cannot be reached at all, write `journals_checked = "none"` with the error in plain words, say so in `limits`, and carry on with the reading.

### 2. Log the publications

For every paper or discovery a `noted`, `moved` or `flagged` item rests on, add a publication record under `data/papers/` in the layout `docs/record-schema.md` gives: id from the first author's surname and year (add a word when two collide, as `hanson-2021-grabby` does), `date` the paper's own date as text, `added_on` the reading's date, authors as on the paper (the first twelve and a count when there are more), title, venue with volume and pages where they exist, link, a `finding` of two to four plain sentences with the numbers that matter, the factors and explanations it bears on, `moved_range = false` (true only when step 3 moves a range on it), a `verify` list for anything not checked on the paper's page, and a `notes` line naming the reading. Never edit a publication record that already exists; if one is wrong, say so in the report. Check each file with `python3 -c "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))" data/papers/X.toml` and then `python3 scripts/compute.py validate`.

### 3. Move a range (`moved` only)

Edit the factor's TOML by text, keeping its layout. In `[range]`, change `low` or `high` (never both in one reading, never the shape, never `median` or `spread_orders`), set `set_on` to the reading's date, and add one sentence to the end of `why` beginning with the date and naming the publication. Append a `[[revision]]` with `date` the reading's date, `field` (`range.low` or `range.high`), `old`, `new`, `why` beginning `[reading YYYY-MM-DD]` with one sentence and the source, and `publication` the id logged in step 2; set that publication's `moved_range = true`. Run `python3 scripts/compute.py validate`. If it fails, revert the factor file (`git checkout -- data/factors/X.toml`), set the publication back to false, mark the item `flagged` with the error in `for_john`, and continue. Never edit a factor you did not mark `moved`.

### 4. Rerun the headline (only if a range moved)

`python3 scripts/compute.py run`. It validates, plays the equation out and rewrites `data/headline.json`; the seed is fixed, so the file changes only because the range did. Note the headline before and after for the changelog line and the report. If nothing moved, do not run it.

### 5. Write the reading record

Write `data/readings/YYYY-MM-DD.toml` (create the folder if absent) exactly in the layout `docs/record-schema.md` gives: `id` and `date` the reading's date, `ran_at` from `date -u +%Y-%m-%dT%H:%M:%SZ`, `run_by = "scheduled"`, `window` in one line, **`pages_opened`** (how many pages you opened beyond the search tool, by `WebFetch`, and which kinds; "none" and why if none, including the result of the page test in step 0), **`journals_checked`** (from step 1a: which journals were listed, over which dates, how many titles read and how many opened, or "none" and why), **`limits`** (in plain words, what you could not see: for example that the web search tool cannot filter by date, which listings you did and did not check, anything that would not open), `records_read`, `searches` (the number of distinct searches across all items; the validator counts what the items list), `commit_before`, then one `[[item]]` per record in the order read, with `record`, `verdict`, `queries`, `reused` where step 1 asked for it, `found` (one to three plain sentences, absolute dates), `sources` for every verdict but quiet, `publications` for noted and moved (and for flagged when one was logged), `for_john` for flagged. If the folder already has a file dated today, suffix `-2`. **Count your own searches before you write `searches`**: every web search and every listing query you made, including any made only to check a date or a name. Each one is listed under the item it served; the number you counted must equal `searches`. The validator cannot see a search you left out, so this count is yours. Run `python3 scripts/compute.py validate`; fix what it names before going on.

### 6. Changelog

Add one line under a `## YYYY-MM-DD` heading at the top of `CHANGELOG.md` (create the heading if today's is absent): "Weekly reading (scheduled task, YYYY-MM-DD): N records read, M ranges moved, K logged, F flagged for John; record at data/readings/YYYY-MM-DD.toml." Name each moved range with its before and after and the publication, and the headline before and after, in the same line.

### 7. Publish: one command

    python3 scripts/publish.py --push \
      --message "YYYY-MM-DD: weekly reading, N read, M moved, K logged, F flagged" \
      --fallback-branch claude/reading-YYYY-MM-DD

It validates, runs the tests, writes the site's data, builds the site, shows what changed, and commits everything as one commit and pushes main; the deploy action on GitHub builds and publishes the site from that push. If it stops before building, the reading's edits broke a rule: read the message, fix or revert, and run it again. If it stops at the site build for a reason that is not the records (Node missing, packages not downloading), run `python3 scripts/export.py --check`, then `git add -A && git commit` with the same message and `git push origin main`, and put the build error in the report. If the push to main is refused, the command pushes the same commit once to the fallback branch and says so; report the branch name so John can merge it, and do not retry. If that push is refused too, put the reading record's contents in the report and stop. The commit message must carry no relative or month-name date (the repository's hook refuses one).

**If a test fails and the reading did not cause it** (the failing test is about code or a record the reading did not touch), do not edit the test, a script or anything outside the limits. Put the reading where it can be merged: `git switch -c claude/reading-YYYY-MM-DD`, `git add -A`, commit with the same message, `git push origin claude/reading-YYYY-MM-DD`, and report the branch, the name of the failing test and its message, first among John's action items. If the failure is in a file the reading wrote, fix that file (a record layout error), not the test.

### 8. Worklog entry

If the Time-Assembler connector is reachable, write one `progress` entry on the project "Quiet Galaxy" (id `c12ca524-a388-4aa7-8c5c-b5d2e40996aa`; `list_projects` if that fails), `repo = "quiet-galaxy"`, titled "Weekly reading YYYY-MM-DD: N read, M moved, K logged, F flagged", with the counts, each moved range, each flagged item's `for_john` line, and the branch if the push fell back. Plain language, no bare ids. If the connector is not reachable, say so in the report and skip this step; the nightly sweep backfills.

### 9. Report

Send John one short message, a numbered list and nothing else: first what he needs to do (each flagged item with its `for_john` line, and the merge if the push fell back to a branch), then one line per moved range with before and after and the headline before and after, then one line per publication logged (first author, year, what it bears on), then one line with the counts, then one line saying how many pages you opened and what you could not see (the record's `pages_opened` and `limits`). No prose, no summary of quiet records.

### Standing rules

- Plain language, absolute dates, no bare ids (a publication id carries the paper's first author and year in words beside it).
- Read, do not infer: a range moves on a published number about its test, not on mood about the field.
- One reading, one commit, made by the publish command. Never force-push, never rebase, never touch a branch other than main and the one fallback branch.
- Say what you rested on: a thing seen on a page you opened, or a thing seen only in a search extract. Never write as if you had read a page you did not open.
- If anything in this file cannot be followed as written, do the parts that can, flag the rest for John in the report, and never improvise an edit outside the limits above.
