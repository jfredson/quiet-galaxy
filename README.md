# The Quiet Galaxy

Where is everybody? The galaxy is old enough and big enough that, on most ways of counting, someone else should have shown up by now. Nobody has. The puzzle has a name, the Fermi Paradox, after the physicist Enrico Fermi, who asked the question over lunch in 1950.

The Quiet Galaxy (thequietgalaxy.com; whereareallthealiens.com forwards to it) is a public explainer and tracker for that question. It does for the empty sky what The Belt Equation does for a settled solar system: it takes a question people file under science fiction and breaks it into factors anyone can argue about, with a number at the top that is computed from the pieces and never chosen by hand. It also keeps a catalogue of every serious explanation for the silence, each on its own page at a stable address, so that any of them can be linked to from a conversation online.

## The equation

The pieces already have a famous form, the Drake Equation, written by the astronomer Frank Drake in 1961 to organise the first meeting on searching for other civilisations. It multiplies seven quantities to get N, the number of civilisations in our galaxy that could be detected right now:

    N = R* × fp × ne × fl × fi × fc × L

In plain words:

- **R\*** — how many stars are born in the galaxy each year.
- **fp** — what share of those stars have planets.
- **ne** — how many planets, per star with planets, could support life.
- **fl** — on what share of those planets life actually starts.
- **fi** — on what share of those it becomes intelligent.
- **fc** — what share of intelligent species make themselves detectable.
- **L** — how long they stay detectable, in years.

The honest answer to most of these is "somewhere between this and that, across many orders of magnitude", so a single multiplied-out number misleads. The project follows the method of a 2018 paper by Anders Sandberg, Eric Drexler and Toby Ord, "Dissolving the Fermi Paradox": each factor carries a range drawn from the published estimates, the equation is run many thousands of times with a random draw from each range, and the result is a spread, not a point.

## The headline numbers

Three numbers come out of that spread and go on the home page:

1. The middle estimate of how many detectable civilisations are in the galaxy right now.
2. The chance we are the only one in the galaxy.
3. The chance we are the only one in the observable universe.

A fourth figure is kept beside them: what the number would be if you take the most optimistic published estimate of every factor, and the most pessimistic. That is the width of the argument, and it is the thing most people have never seen.

Every factor page shows the published estimates it rests on, each with a date and a source, and the range the project currently uses. When a new discovery changes the record for a factor, the range moves, the headline recomputes, and the change is logged with its reason.

The numbers live in one small file, `data/headline.json`, written by the computation and never by hand, and the site serves the same file at thequietgalaxy.com/data/headline.json (since 2026-10-17), so another site or a script can read the headline and the date it was computed without scraping a page.

## Five kinds of record

The data is the project. Five record types (four at the kickoff, the fifth added 2026-10-16), each one plain-text TOML file per entry under `data/`, laid out so a change shows as a one-line diff:

1. **Factors** (`data/factors/`). One file per Drake factor: what it means, the published estimates (value or range, who, when, source, method in one line), the range the project uses now and why, and a revision log. All seven written on 2026-10-16; every range reviewed on 2026-10-17.
2. **Explanations** (`data/explanations/`). One file per explanation for the silence, sorted into three families: *they were never there* (the factors before L are small), *they are gone* (L is short), and *they are there and we cannot see them* (the equation is fine and the silence is about us). Each says which factor it bears on and in which direction, who proposed it and when, what would strengthen or weaken it, and which explanations it is related to. Thirty-two on 2026-10-17.
3. **The library** (`data/library/`). Books, films, television, games and videos that treat a factor or an explanation in an interesting way: who made it, when, which explanation or factor it illustrates, one paragraph on how, and whether it is worth the time. Thirty-six entries.
4. **The publications log** (`data/papers/`). An append-only, dated list of the scientific papers and discoveries that bear on the calculation, from the founding papers of the 1960s to the latest exoplanet results. Each entry says which factor or explanation it bears on and whether it moved a range. Seventy-six entries on 2026-10-17.
5. **The weekly readings** (`data/readings/`, added 2026-10-16). Once a week a scheduled session reads every factor and explanation against what was published, logs what bears on them, and writes one record per run: what it searched, what it found, and a verdict for each record. The procedure, the four verdicts and the limits on what a reading may do are in `docs/weekly-reading.md`.

The links between the records are what make the site useful: a factor page lists the papers behind its range and the explanations that lean on it; an explanation page lists the papers for and against it and the books and films that dramatise it; a library entry points back at the explanation it illustrates; a reading names the records it read. The record layout and the rules the validator enforces are in `docs/record-schema.md`.

## Layout

- `docs/` holds the plans and definitions. `docs/2026-10-16-kickoff.md` is the original outline, kept as the record of where the project started. `docs/record-schema.md` is the source of truth for the five record types. `docs/weekly-reading.md` is the weekly reading's plan and procedure, and `docs/weekly-reading-prompt.md` the prompt its scheduled task runs.
- `data/` holds the records, in the five folders above, plus `data/retired.toml`, the list of ids that once existed and were retired or replaced (an explanation id is a public address and is never renamed), and `data/headline.json`, the computed headline.
- `scripts/` holds the code: `compute.py validate` checks every record against the schema and refuses to continue on any failure; `compute.py run` plays the equation out and writes `data/headline.json`; `export.py` is the only reader of the records and writes the site's data (nothing in the browser touches the TOML files); `publish.py` validates, builds and pushes in one command. `scripts/test_compute.py` checks the validator, the computation and the export. Python standard library only.
- `site/` holds the website: an Astro static site on the Sentient Horizons design standard's shared skeleton, wearing this site's own skin, Hush, and reading the exported records at build time. Live at thequietgalaxy.com, with a preview address at quietgalaxy.jfredson.workers.dev. See `site/README.md`.
- `CHANGELOG.md` records every change to a range, a record or the method, with absolute dates.

## Status

As of 2026-10-17. Created 2026-10-16, when John ruled the name; the record schema, the validator and the full first set of records were written the same day, and the full site went live at thequietgalaxy.com that evening, two days ahead of the weekend the kickoff planned for.

- **The headline**, computed 2026-10-17 (200,000 runs, seed 1961): a middle estimate of **0.021** detectable civilisations in the galaxy, a **58.0%** chance we are alone in the galaxy, and a **39.5%** chance we are alone in the observable universe. Every one of the seven ranges is marked **reviewed**: the outside-model review of the ranges ran on 2026-10-17 and John ruled on its twenty items the same day, moving one range (the top of how many stars are born each year, from 10 to 20). The rulings and what they changed are in `docs/reviews/2026-10-17-rulings.md` and the changelog.
- **The records**: seven factors with 42 published estimates, 32 explanations, 36 library entries, 76 publications in the log, and one weekly reading (2026-10-16, run by hand).
- **The site** wears its own skin, Hush (a cold, near-empty sky: blue-black, cold white, a pale ice-blue, a dozen still stars and no glow; dark by default), ruled by John 2026-10-16, with the Ripples backdrop (hairline rings from the top corner behind the stars) added 2026-10-17. It serves the headline file at `/data/headline.json` and a sitemap at `/sitemap.xml`.
- **The weekly reading** is a scheduled cloud session on Saturdays at 19:00 Pacific, first due 2026-10-17; it reads every factor and explanation against what was published that week, logs what bears on them, moves a range only within a cap, reruns the headline and commits to main. Its cap and schedule are proposed, not yet ruled (`docs/weekly-reading.md`).
- **Open**: two claims written from memory are marked `verify` (updated 2026-10-17, after a pass that checked the other 25 against their sources): Grinspoon's "potentially billions of years" for the lifetime factor, and Shklovskii and Sagan's 1966 treatment of the overlap-in-time problem. Both wait on books John ordered on 2026-10-17 (Grinspoon 2004, Shklovskii and Sagan 1966). Nothing is promoted while an entry stays open.

Every change since, with its date and reason, is in `CHANGELOG.md`.

## Licences

The records and every other data file are under Creative Commons Attribution 4.0 (`LICENSE-DATA`): reuse them freely, with credit. The scripts and the site's code are under the MIT licence (`LICENSE`); its text and data are under CC BY 4.0 (`LICENSE-DATA`). Both from the first commit, as the Sentient Horizons design standard asks.

When you reuse the data or the text, please credit it as: *The Quiet Galaxy*, by John Andrew Fredrickson, a Sentient Horizons project, https://thequietgalaxy.com/

To cite the data: John Andrew Fredrickson, *The Quiet Galaxy*, Sentient Horizons, 2026, with the date you read it and the address of the record.

## Author

John Andrew Fredrickson, with Claude as a working partner. Published under the Sentient Horizons project.
