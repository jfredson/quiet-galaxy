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

## Four kinds of record

The data is the project. Four record types, each one plain-text TOML file per entry under `data/`, laid out so a change shows as a one-line diff:

1. **Factors** (`data/factors/`). One file per Drake factor: what it means, the published estimates (value or range, who, when, source, method in one line), the range the project uses now and why, and a revision log. Seven files when complete.
2. **Explanations** (`data/explanations/`). One file per explanation for the silence, sorted into three families: *they were never there* (the factors before L are small), *they are gone* (L is short), and *they are there and we cannot see them* (the equation is fine and the silence is about us). Each says which factor it bears on and in which direction, who proposed it and when, what would strengthen or weaken it, and which explanations it is related to. About thirty in the first version.
3. **The library** (`data/library/`). Books, films, television, games and videos that treat a factor or an explanation in an interesting way: who made it, when, which explanation or factor it illustrates, one paragraph on how, and whether it is worth the time.
4. **The publications log** (`data/papers/`). An append-only, dated list of the scientific papers and discoveries that bear on the calculation, from the founding papers of the 1960s to the latest exoplanet results. Each entry says which factor or explanation it bears on and whether it moved a range.

The links between the four are what make the site useful: a factor page lists the papers behind its range and the explanations that lean on it; an explanation page lists the papers for and against it and the books and films that dramatise it; a library entry points back at the explanation it illustrates. The record layout and the rules the validator enforces are in `docs/record-schema.md`.

## Layout

- `docs/` holds the plans and definitions. `docs/2026-10-16-kickoff.md` is the original outline, kept as the record of where the project started. `docs/record-schema.md` is the source of truth for the four record types.
- `data/` holds the records, in the four folders above, plus `data/retired.toml`, the list of ids that once existed and were retired or replaced (an explanation id is a public address and is never renamed). Seeded with one worked example of each type; the full set lands over the weekend of 2026-10-18.
- `scripts/` holds the code: `compute.py validate` checks every record against the schema and refuses to continue on any failure; `compute.py run` will compute the headline numbers once the seven factors are seeded; `export.py` writes the site's data; `publish.py` validates, builds and pushes in one command. `scripts/test_compute.py` checks the validator. Python standard library only.
- `site/` holds the website: an Astro static site on the Sentient Horizons design standard, reading the exported records at build time. Live at thequietgalaxy.com, with a preview address at quietgalaxy.jfredson.workers.dev. See `site/README.md`.
- `CHANGELOG.md` records every change to a range, a record or the method, with absolute dates.

## Status

Created 2026-10-16; the name was ruled by John the same day. The repository is public on GitHub, the record schema is ruled, the validator exists, and the factors, explanations, library and publications log are each seeded with one worked example. A holding version of the site is live at thequietgalaxy.com. The first public version is targeted for the weekend of 2026-10-18 and 2026-10-19.

## Licences

The records and every other data file are under Creative Commons Attribution 4.0 (`LICENSE-DATA`): reuse them freely, with credit. The scripts and the site are under the MIT licence (`LICENSE`). Both from the first commit, as the Sentient Horizons design standard asks.

To cite the data: John Fredrickson, *The Quiet Galaxy*, Sentient Horizons, 2026, with the date you read it and the address of the record.

## Author

John Fredrickson, with Claude as a working partner. Published under the Sentient Horizons project.
