# Record schema and data format

Drafted 2026-10-16 (weekend step 2 of `docs/2026-10-16-kickoff.md`) and **DECIDED the same day**: Claude proposed the layout below with a confidence level and the strongest alternative for each choice, recorded at the end under "Decisions", and John accepted all twelve as proposed on 2026-10-16. This document is the source of truth for the record layout, and `scripts/compute.py validate` refuses any file that does not follow it. A change to the layout is a new proposal, made the same way.

## What a record is

The data is the project. There are four kinds of record, one TOML file per record, under four folders in `data/`:

| Kind | Folder | What one record is | Its id is also |
|---|---|---|---|
| factor | `data/factors/` | One of the seven quantities in the Drake Equation, with its published estimates and the range the project uses now | the factor page address (`/factors/planets/`) |
| explanation | `data/explanations/` | One explanation for the silence | the explanation page address (`/explanations/dark-forest/`), **never renamed** |
| library | `data/library/` | One book, film, show, game or video that dramatises a factor or an explanation | the library entry's address |
| publication | `data/papers/` | One scientific paper or discovery that bears on the calculation, in an append-only log | the citation key other records link with |

A fifth file, `data/retired.toml`, lists ids that once existed and were retired or replaced. It is how an id is taken out of service without ever being renamed.

The links between the four kinds point one way. A library entry says which explanations and factors it illustrates; a publication says which factors and explanations it bears on; a factor's estimates may name the publication they come from; an explanation names the factors it bears on and the explanations related to it. A page for a factor or an explanation gathers the papers and library entries that point at it. Nothing is stored in two places.

## File format and layout

TOML, one file per record, read by Python's standard library (`tomllib`, present since Python 3.11; this Mac has 3.14). TOML is plain text, allows comments, keeps each field on its own line so a change to one number shows as a one-line diff, and supports multi-line text for the paragraphs. The alternative was JSON, which the standard library also reads but which has no comments and diffs badly for prose. The same choice The Belt Equation made on 2026-09-08.

    data/
      retired.toml                    ids that once existed and were retired or replaced
      factors/
        star-formation.toml           R*, how many stars are born in the galaxy each year
        planets.toml                  fp, the share of stars with planets
        habitable-planets.toml        ne, planets per star that could support life
        life.toml                     fl, the share of those on which life starts
        intelligence.toml             fi, the share of those on which it becomes intelligent
        detectable.toml               fc, the share of intelligent species that are detectable
        lifetime.toml                 L, how long they stay detectable, in years
      explanations/
        dark-forest.toml              one file per explanation, named for its id
        ...
      library/
        three-body-problem.toml       one file per book, film, show, game or video
        ...
      papers/
        sandberg-2018.toml            one file per paper, named first author and year
        ...

**Ids.** Every record has an `id`: lowercase letters, digits and single dashes, like `dark-forest` or `sandberg-2018`. The file is named `<id>.toml`, and the validator refuses a file whose name and id disagree: that is the first guard against renaming. Ids are unique across all four kinds, so a link is never ambiguous. Factor ids are the seven plain-word names above and nothing else. Publication ids are the first author's surname and the year (`sandberg-2018`), with a word added when two collide (`hanson-2021-grabby`).

**Dates.** A date the project writes (when a range was set, when a paper was logged, when a revision was made) is a TOML date, `2026-10-16`. A date the world supplies (when an estimate was published, when a paper appeared) is text, because old papers often have only a year or a year and month: `"1961"`, `"2012-01"` or `"2012-01-12"`, nothing else.

**Top-level fields come before the first table.** In TOML, anything written after a `[range]` or `[[estimate]]` header belongs to that table, so `verify` and `notes` written at the bottom of a file silently become fields of the last table and fail as unknown. Write them before the first `[[estimate]]`, `[range]` or `[[bears_on]]` header; the worked examples below do.

**Unknown fields are refused.** A field not listed below fails validation, so a misspelt field name is caught instead of silently ignored.

## The factor record

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | One of the seven factor ids. |
| `symbol` | yes | The symbol in the equation as written: `R*`, `fp`, `ne`, `fl`, `fi`, `fc` or `L`. Must match the id (the script holds the table). |
| `order` | yes | 1 to 7, the factor's place in the equation. Must match the id. |
| `name` | yes | Plain-language name, one line, readable by someone outside the project. |
| `unit` | yes | `"stars per year"`, `"fraction"`, `"planets per star"` or `"years"`. Must match the id. A fraction's estimates and range must lie between 0 and 1. |
| `description` | yes | Two or three sentences on what the factor means and how well it is known. |
| `what_would_move_this` | yes | One line saying what kind of discovery would change the range. The weekly scan writes its searches from this. |
| `[[estimate]]` | at least one | A published estimate. Fields: `who` (yes), `when` (yes; year, year-month or full date as text), either `value` or both `low` and `high` (yes; numbers, `low <= high`), `source` (yes; the citation in words, enough to find it; "common knowledge" is not a source), `method` (yes; one line on how the number was reached), `link` (no), `publication` (no; the id of the publication record it comes from, which must exist). |
| `[range]` | yes | The range the project uses now. Fields: `shape` (yes; `"log-uniform"`, which spreads the draws evenly across orders of magnitude; `"uniform"`; or `"log-normal-rate"`, below), `status` (yes; `"first-pass"` until the outside review has run, then `"reviewed"`), `set_on` (yes; date), `why` (yes; the reason in plain words, naming the estimates it rests on), `sources` (no; publication ids). A log-uniform or uniform range carries `low` and `high` (yes; `low <= high`, and `low > 0` when log-uniform). A `log-normal-rate` range carries `median` and `spread_orders` instead (yes; both above 0) and no `low` or `high`: it is the 2018 paper's model for the chance life starts, and fits only a factor measured as a fraction. The number of times life starts on a habitable planet over its life is drawn from a bell curve in its powers of ten, centred on `median` starts per planet and `spread_orders` powers of ten wide, and the chance is one minus e to the minus that number. **Added 2026-10-16, ruled by John the same day** ("Use the 2018 paper's log-normal rate shape for the chance life starts, adding the third shape to the record layout"); decision 4 below anticipated it. |
| `[[revision]]` | no | One per change to the range or any other field after the file's first commit, newest last. Fields: `date`, `field`, `old`, `new`, `why` (all yes), `publication` (no; the publication id that caused it, which must exist). A range change always gets one. |
| `verify` | no | List of plain-language claims in this record that were written from memory and not checked against a source at the time. A later session clears each by checking it and either deleting the entry or correcting the record. The weekly scan reads the list but may not edit it (the Belt Equation rule of 2026-10-06). |
| `notes` | no | Anything else worth keeping with the factor. |

### Worked example: `data/factors/planets.toml`

    id = "planets"
    symbol = "fp"
    order = 2
    name = "The share of stars that have planets"
    unit = "fraction"
    description = """
    Of all the stars in the galaxy, what fraction have at least one planet. In 1961 this was
    a guess; since the first exoplanet discoveries in the 1990s and the Kepler mission of 2009
    to 2018 it has become one of the two best-measured factors in the equation. The current
    reading is that planets are the rule, not the exception."""
    what_would_move_this = "A survey that counts planets around a large, well-understood sample of stars, including the dim red dwarfs that make up most of the galaxy, and reports the share of stars with none."

    verify = [
      "Drake's 1961 range of 0.2 to 0.5 for fp is quoted from secondary accounts of the Green Bank meeting; check it against the 2015 Drake, Vakoch and Dowd book.",
    ]

    [[estimate]]
    who = "Frank Drake and the Green Bank meeting"
    when = "1961"
    low = 0.2
    high = 0.5
    source = "Green Bank meeting of November 1961, as recorded in Drake, Vakoch and Dowd, The Drake Equation (Cambridge University Press, 2015)"
    method = "Educated guess before any planet outside the solar system had been found."

    [[estimate]]
    who = "Arnaud Cassan and colleagues"
    when = "2012-01-12"
    low = 0.62
    high = 1.0
    source = "Cassan et al., 'One or more bound planets per Milky Way star from microlensing observations', Nature 481, 167–169 (2012)"
    link = "https://arxiv.org/abs/1202.0903"
    method = "Gravitational microlensing over six years of survey data; 62% of stars found to host a planet of a few Earth masses at 0.5 to 10 times the Earth-Sun distance, and the planets per star add to more than one."

    [range]
    low = 0.1
    high = 1.0
    shape = "log-uniform"
    status = "first-pass"
    set_on = 2026-10-16
    sources = ["sandberg-2018"]
    why = """
    Starts from the range Sandberg, Drexler and Ord used in 2018 ("log-uniform from 0.1 to 1").
    The lower bound of 0.1 is almost certainly too low given the 2012 microlensing result and the
    Kepler record; it is kept as a first pass until the full record is read on 2026-10-18."""

The file in `data/` is the complete version. When a range moves, the file gains a revision such as:

    [[revision]]
    date = 2026-11-02
    field = "range.low"
    old = 0.1
    new = 0.5
    why = "The Kepler occurrence-rate record read in full; no survey since 2012 finds fewer than half of stars with a planet."
    publication = "cassan-2012"

## The explanation record

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The page address, never renamed once committed. Retire it in `data/retired.toml` instead. |
| `name` | yes | Plain-language name, one line, that says what the explanation claims: not just "Dark forest" but what the dark forest is. |
| `family` | yes | `"never-there"` (the factors before L are small), `"gone"` (L is short) or `"unseen"` (the equation is fine and the silence is about us). The three families are the catalogue's top-level sections; their plain names live in the script. |
| `proposed_by` | yes | Who first put it forward, as far as the record shows. |
| `proposed_in` | yes | The year, as a number. |
| `proposed_source` | no | Where: the paper, book or talk. |
| `summary` | yes | The one-paragraph version, for the index and for a reader who stops there. |
| `body` | yes | The longer version: the argument, its history, how it bears on the equation, the main objections. |
| `[[bears_on]]` | at least one | Which factor it bears on and in which direction. Fields: `factor` (one of the seven factor ids) and `direction` (`"lowers"`, `"raises"` or `"unchanged"`, the last for an explanation that leaves the factor where it is and says the silence is about our search). An explanation may bear on more than one factor. |
| `standing` | no | How seriously it is taken and by whom, in a sentence or two. |
| `would_strengthen` | yes | What evidence or result would make it more likely. The weekly scan searches on this. |
| `would_weaken` | yes | What would make it less likely. |
| `related` | no | List of explanation ids that a reader of this one should see next. Each must exist, and an explanation may not list itself. |
| `verify` | no | As for factors. |
| `notes` | no | Anything else. |

### What is not in the record

- **Its library entries and its papers.** A library entry names the explanations it illustrates, and a publication names the explanations it bears on; the explanation page gathers them. Storing the list on the explanation too is how the two drift apart (the lesson The Belt Equation drew about tier membership on 2026-09-08). The kickoff document and the step-2 brief both listed library entries as a field on the explanation; this is the one place the proposal departs from them, for that reason.

### Worked example: `data/explanations/dark-forest.toml`

Abridged; the file in `data/` has the full text.

    id = "dark-forest"
    name = "The dark forest: everyone is hiding, because announcing yourself gets you killed"
    family = "unseen"
    proposed_by = "Liu Cixin"
    proposed_in = 2008
    proposed_source = "The Dark Forest, the second novel of the Remembrance of Earth's Past trilogy, 2008"
    summary = """
    The galaxy may be full of civilisations that all keep quiet, because the safest thing to
    do when you cannot know a stranger's intentions, and cannot talk to them fast enough to find
    out, is to say nothing and destroy anyone who speaks. ..."""
    body = """
    The argument runs in three steps. ..."""
    standing = "Widely known from the novels; among researchers it is one of several 'they choose silence' explanations, and most consider the hiding it requires too hard to sustain."
    would_strengthen = "Evidence of a civilisation deliberately suppressing its emissions; ..."
    would_weaken = "Any detected civilisation that broadcasts freely; ..."
    related = []

    verify = [
      "That Greg Bear's The Forge of God (1987) is a fair example of the 'punish the loud' idea and the year is right.",
    ]

    [[bears_on]]
    factor = "detectable"
    direction = "lowers"

    [[bears_on]]
    factor = "lifetime"
    direction = "lowers"

## The library record

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Slug, usually the title. |
| `title` | yes | The work's title. |
| `maker` | yes | Author, director, studio or channel. |
| `year` | yes | Year of release, as a number. For a series, the year the relevant part appeared, said in `how`. |
| `kind` | yes | `"book"`, `"story"`, `"film"`, `"television"`, `"game"`, `"video"` or `"essay"`. |
| `explanations` | one of these two | List of explanation ids the work illustrates. |
| `factors` | one of these two | List of factor ids the work illustrates. At least one id across the two lists. |
| `how` | yes | One paragraph on how the work treats the idea. |
| `worth_the_time` | yes | One line: is it worth the time, and for whom. |
| `link` | no | A reference page or the work's own page. |
| `verify`, `notes` | no | As above. |

### Worked example: `data/library/three-body-problem.toml`

    id = "three-body-problem"
    title = "Remembrance of Earth's Past (The Three-Body Problem, The Dark Forest, Death's End)"
    maker = "Liu Cixin"
    year = 2008
    kind = "book"
    explanations = ["dark-forest"]
    factors = ["detectable"]
    link = "https://en.wikipedia.org/wiki/Remembrance_of_Earth%27s_Past"
    how = """
    The trilogy is the source of the dark forest idea rather than an illustration of it. ..."""
    worth_the_time = "Yes, and start with the first book: it is the most complete dramatisation of the silence as a survival strategy, and the second book is where the idea everyone quotes is actually laid out."

## The publication record

The publications log is append-only: a record is added when a paper is read and never edited afterwards except to fix an error, with a changelog line.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | First author's surname and year, like `sandberg-2018`. |
| `date` | yes | When it appeared, as text: year, year-month or full date. |
| `added_on` | yes | The date it was logged here (a TOML date). The log is read in this order. |
| `authors` | yes | List of names, as they appear on the paper. |
| `title` | yes | The paper's title. |
| `venue` | yes | Journal, preprint server, book or announcement, with volume and pages where they exist. |
| `link` | yes | Where to read it. |
| `finding` | yes | One or two plain sentences on what it found or claimed, with the numbers that matter. |
| `factors` | one of these two | List of factor ids it bears on. |
| `explanations` | one of these two | List of explanation ids it bears on. At least one id across the two lists. |
| `moved_range` | yes | `true` or `false`: did reading it move a factor's range? If `true`, some factor's revision log must carry a revision naming this publication. |
| `verify`, `notes` | no | As above. |

### Worked example: `data/papers/sandberg-2018.toml`

    id = "sandberg-2018"
    date = "2018-06-06"
    added_on = 2026-10-16
    authors = ["Anders Sandberg", "Eric Drexler", "Toby Ord"]
    title = "Dissolving the Fermi Paradox"
    venue = "arXiv:1806.02404 (physics.pop-ph), Future of Humanity Institute, Oxford; submitted to Proceedings of the Royal Society A"
    link = "https://arxiv.org/abs/1806.02404"
    finding = """
    Run with a range for each factor instead of a single value, the Drake Equation gives a
    median of 0.32 detectable civilisations in the galaxy, a 52% chance that we are alone in
    the galaxy and a 38% chance that we are alone in the observable universe. ..."""
    factors = ["star-formation", "planets", "habitable-planets", "life", "intelligence", "detectable", "lifetime"]
    explanations = []
    moved_range = false

## The retired list

`data/retired.toml` holds a list `retired`, each entry with `id`, `kind` (`factor`, `explanation`, `library` or `publication`), `date`, `why`, and optionally `replaced_by` (an id that must exist). To retire a record: delete its file, add the entry, and update every record that linked to it. The validator refuses a new record that reuses a retired id.

## Rules the validator enforces

`python3 scripts/compute.py validate` reads every record and refuses to continue on any failure, listing everything wrong in plain language.

1. Every file under the four folders is valid TOML, and every record has every required field with a non-empty value; every enumerated field has an allowed value; no record carries a field not listed above.
2. Ids are lowercase slugs, unique across all four kinds, and each file is named for its id.
3. Factor ids are the seven known ones, and `symbol`, `order` and `unit` match the id.
4. Every estimate has `who`, `when`, `source` and `method`, and either `value` or both `low` and `high` with `low <= high`. A fraction's estimates lie between 0 and 1.
5. Every factor has a range with an allowed `shape` and `status`, a `set_on` date and a `why`. A log-uniform or uniform range has `low <= high`; a log-uniform range has `low > 0`; a fraction's range lies between 0 and 1. A log-normal-rate range has `median` and `spread_orders` above 0, no `low` or `high`, and belongs to a factor measured as a fraction; a range of any other shape may not carry `median` or `spread_orders`.
6. Every link between records resolves: an estimate's or revision's `publication`, a range's `sources`, an explanation's `bears_on` factors and `related` ids, a library entry's `explanations` and `factors`, a publication's `factors` and `explanations`, a retired entry's `replaced_by`. A `bears_on` or `factors` id must be one of the seven factor ids; its record file need not exist yet until `run`.
7. Every explanation has a family and bears on at least one factor, each with a direction; it does not list itself as related.
8. Every library entry and every publication names at least one factor or explanation.
9. A publication with `moved_range = true` is named by a revision on some factor.
10. No id is renamed. The file name must equal the id; and a data file that was committed to the repository before and is now gone must have an entry in `data/retired.toml` (the script reads the repository's history for this, and skips the check with a note when the data folder is not in a git repository). A current record may not reuse a retired id.

`python3 scripts/compute.py run` validates first, refuses with a plain message until all seven factor records exist, and otherwise plays the equation out and writes `data/headline.json`. How it does that, and the parameters proposed for it on 2026-10-16, are in `docs/method.md`.

## Decisions (2026-10-16)

Proposed by Claude with a confidence level and the strongest alternative for each, per the ground rule of 2026-09-08, and accepted by John as proposed on 2026-10-16. Recorded here so the reasoning is checkable later. Items 2 and 6 depart from the kickoff document and say why.

1. **One TOML file per record, in four folders, named for the id.** High confidence: it is the Belt Equation's format, the standard-library reader exists, a one-line diff per change, and parallel sessions on Saturday can each write a folder without touching the others. Standard practice for a data-as-text project. Alternative: one file per kind (`explanations.toml` holding thirty records), which is fewer files but makes every Saturday session edit the same file and makes a page's source harder to find. The kickoff proposed one file per record for factors and explanations and left the library and papers open; this settles them the same way.
2. **The explanations folder is `data/explanations/`, not `data/theories/` as the kickoff wrote.** Moderate confidence; a judgment call about words. The kickoff itself calls the records "explanations" everywhere else, including the page address `/explanations/dark-forest/`, and "theory" claims more than most of these ideas have earned. Alternative: keep `theories/` as written, which costs a mismatch between the folder, the record kind and the address.
3. **Factor ids are plain words (`planets`, `lifetime`), with the symbol as a field.** Moderate confidence; a judgment call. The id is a page address, and `/factors/planets/` reads where `/factors/f-p/` does not; the workspace rule is plain language everywhere. Alternative: the symbols as slugs (`r-star`, `f-p`, `l`), which match the equation as written at the cost of addresses that read as code and one (`l`) that is a single letter. The script holds the table from id to symbol, order and unit, and the file repeats the three for readability; the validator refuses a mismatch, so the repetition cannot drift.
4. **A range carries a `shape` and a `status`.** Moderate confidence. The 2018 paper used log-uniform ranges for six factors and a log-normal for one, so the shape is part of the method and should be arguable per factor rather than fixed in the script; `status` lets the site label every number "first pass" until the outside review of the seven ranges (kickoff, after-the-weekend item 2) has run, as The Belt Equation does. Alternative: fix log-uniform in the script and drop both fields, which is simpler and would need a field added later anyway. On reflection I would keep `shape` to two values and add `log-normal` only when a factor needs it; that is what is proposed. **Note added 2026-10-16:** the factor that needs it is the chance life starts, and John ruled the same day that the third shape, `log-normal-rate`, is added and used there (`docs/method.md`, item 7).
5. **An explanation can bear on more than one factor, each with a direction.** Moderate confidence; a judgment call. Rare Earth bears on `habitable-planets` and `life`; the dark forest on `detectable` and `lifetime`. Alternative: one `factor` field, which is simpler for the index page but forces a false choice on perhaps a third of the thirty explanations. The direction `unchanged` exists for explanations that attack the observation rather than the equation ("we have not looked long enough").
6. **Library entries and papers link to explanations and factors; nothing links back.** High confidence; standard practice (one source of truth). The kickoff and the step-2 brief listed "library entries" as an explanation field; storing the list on both ends is how they drift apart, and the site can gather the back-links at build time. Alternative: store both and have the validator check they agree, which doubles the writing for no gain.
7. **The three families are keys (`never-there`, `gone`, `unseen`) whose plain names live in the script, not a fifth record type.** Moderate confidence. Three fixed sections do not need a data file; a `families.toml` would be a record type with three rows that never change. Alternative: the file, which lets the site read the family's blurb from data. Revisit if the families get long introductions.
8. **World dates are text (year, year-month or full date); project dates are TOML dates.** Moderate confidence; a judgment call. Drake's 1961 meeting has a month and no day worth recording, and forcing a full date would mean inventing one. Alternative: TOML dates everywhere, which sorts and compares for free at the cost of made-up days.
9. **Renamed ids are caught two ways: file name must equal id, and an id that was ever committed and is now gone must be in `data/retired.toml`.** High confidence on the rule; moderate on reading git history from the validator, which is unusual but cheap (one `git log` call) and skipped outside a repository. Alternative: a hand-kept registry of every id ever used, which is one more file to forget to update.
10. **A publication that says it moved a range must be named by a revision on a factor.** High confidence; it is the cross-check that keeps the log honest, and the weekly scan's "moved a range" verdict is only true when the factor file changed.
11. **Unknown fields are refused.** High confidence; standard practice for a strict validator. Alternative: ignore them, which lets a misspelt `source` become a factor with no source that passes.
12. **The `verify` list is carried over from The Belt Equation.** High confidence; it is the mechanism behind the ground rule that facts from memory are marked for checking.

## Known simplifications

- **The headline's parameters are in `docs/method.md`**, proposed with confidence and alternatives and ruled by John on 2026-10-16: 200,000 runs, a fixed seed, independent draws, ten to the eleven galaxies for the observable universe, the result committed as `data/headline.json`, the width from the published estimates, and the third range shape for the chance life starts. The kickoff's method itself (a random draw from each range, many thousands of times; the median, the chance of N below 1, the chance of N below one per observable universe, and the optimist-to-pessimist width) was settled before.
- **A log-normal-rate range has no ends.** Where the site or the width computation needs a low and a high for one (the band on the calculator, the width from the ranges), `scripts/compute.py range_ends` takes the chance one spread below the centre (about one in ten to the fifty for the paper's shape) and 1; where it needs a starting value, `range_middle` takes the chance at the centre (0.63). Both are conveniences for display, not part of the record.
- **Estimates are not weighted.** The range is set by hand from the estimates with a written reason, not computed from them. That is deliberate: the reason is the arguable part.
- **A library entry has one `how` paragraph** even when it illustrates several explanations. If an entry needs a paragraph per explanation, split it or revisit.
