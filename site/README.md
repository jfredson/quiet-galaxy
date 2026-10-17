# The website

The public face of the records: https://thequietgalaxy.com (domain registered by John and attached 2026-10-16), with a preview address at https://quietgalaxy.jfredson.workers.dev (first deployed 2026-10-16). Built the same way as The Belt Equation's site, on the Sentient Horizons design standard (`sentient-horizons/design/`).

## How it fits together

    data/**/*.toml  ──►  scripts/export.py  ──►  site/src/data/records.json  ──►  astro build  ──►  dist/  ──►  wrangler deploy

- **Python owns the data.** `scripts/export.py` reads the records with the same loader and validator as `scripts/compute.py`, so the site can never show a record that fails the schema. It writes `src/data/records.json`. That file is generated, not committed: every `npm run build` and `npm run dev` runs the export first (`prebuild`, `predev`), so the site always reflects the records in `data/`.
- **Astro owns the pages.** Astro 5, fully static, same generator and folder layout as the sister sites. `src/lib/records.ts` is the typed view of the JSON; every page reads from it.
- **The styles are the standard's.** `src/styles/global.css` is `deep-field.css` copied unchanged (version 1.3.0 of 2026-10-08) with this site's own styles below the marked line. `Base.astro` and `Nav.astro` express the standard's shell: the theme script, the top bar with the two tiers and the toggle, the footer with the four lines and the parent line.

## Pages

The page map, built 2026-10-16 (weekend step 6 of `docs/2026-10-16-kickoff.md`) on the tracker pattern of the design standard (`sentient-horizons/design/tracker-pattern.md`, ruled by John 2026-10-16). Every record in `data/` gets a page or an anchored entry, and the counts on every page come from the same export the validator passed.

| Path | What it shows | Source file |
|---|---|---|
| `/` | The home page, built like The Belt Equation's first screen (two columns on a desktop, stacked on a phone). Left: the eyebrow; the chance we are alone in the galaxy in the largest type, with the middle estimate and the chance we are alone in the observable universe beneath it; the question; one paragraph for a newcomer; the width of the argument in one line; the last-checked strip; two buttons. Right: the equation line with each term linked to its piece and the range under it. Below: the three families, what would move it, the story so far, disagree. Every number reads "not computed yet" in words until `compute.py run` has written the headline file. | `src/pages/index.astro` |
| `/equation/` | The equation in plain words, the calculator (seven sliders, plain JavaScript, N recomputed live, each with the project's range marked as a band), and a card per piece. | `src/pages/equation/index.astro` |
| `/factors/<id>/` | One page per piece of the equation, all seven (a piece whose record is not written yet says so): the range used and why, the published estimates with dates and sources, what would move it, how the range has moved, the explanations that lean on it, the papers and library entries that point at it. | `src/pages/factors/[id].astro` |
| `/explanations/` | Every explanation, in the three families with their plain names and blurbs. | `src/pages/explanations/index.astro` |
| `/explanations/<id>/` | One page per explanation at its permanent address: summary, body, which pieces it bears on and how, what would strengthen or weaken it, how seriously it is taken, the papers and library entries that point at it (gathered at build time by `scripts/export.py`), related explanations in both directions. | `src/pages/explanations/[id].astro` |
| `/library/` | The shelf, grouped by kind, each work at an anchor named for its id (`/library/#three-body-problem`). | `src/pages/library/index.astro` |
| `/story/` | The story so far: the publications log, newest first by the day each was logged, each entry at an anchor named for its id, saying which pieces or explanations it bears on and whether it moved a range, with the revisions it caused. | `src/pages/story/index.astro` |
| `/method/` | How the numbers are worked out, in plain words, with the working documents linked and prefaced at the end. | `src/pages/method/index.astro` |
| `/disagree/` | Disagree with something: the three forms (a missing explanation, a range that should move with a source, an error on a page), each a prefilled issue template under `.github/ISSUE_TEMPLATE/`, and the four steps that follow. | `src/pages/disagree/index.astro` |
| `/404.html` | Not found, with the retired ids and their replacements when there are any. | `src/pages/404.astro` |

Top bar (tracker pattern rule 4.6): the heavier tier is Home, The equation, Explanations, Library, The story so far; the lighter tier is How the numbers are worked out, Disagree with something, Source. The components copied from The Belt Equation (the big number, the last-checked strip, the equation line, the piece cards, the record layout with its rail, the "what would move this" list, the story entry card, the three disagree forms) and from the AGI Zeitgeist Tracker (the working-document preface) each carry a comment saying where they came from, per the pattern's rule 7.1.

**The headline.** `scripts/export.py` reads the numbers from `data/headline.json`, the file `compute.py run` writes (or `--headline FILE`): `median`, `alone_in_galaxy`, `alone_in_universe`, `runs`, `computed_on`, `mean`, `percentiles`, `any_range_first_pass`, `verify_open`, the `method` block (runs, seed, independent draws, galaxy count, status), and the width of the argument from `extremes.from_estimates` (optimist and pessimist) with the same from the ranges' ends beside it. A file without the median and the two chances is ignored with a note, and every page then says the numbers are not computed and why. The last-checked strip says in words that no weekly reading has run yet; the export's `reading` field is where the latest reading goes once the weekly scan exists.

## Commands

Run from `site/`. Needs Node (the Mac has 26) and Python 3.11 or later for the export.

    npm install          once
    npm run export       write the JSON from ../data without building
    npm run dev          local preview with live reload (runs the export first)
    npm run build        static build to dist/ (runs the export first)
    npm run preview      serve dist/ locally
    npm run deploy       build, then `wrangler deploy` to Cloudflare Workers static assets

The ordinary way to publish is not `npm run deploy` but `python3 scripts/publish.py --push` from the repository root: it validates, exports and builds everything, shows what changed, and pushes main, and the GitHub Action (`.github/workflows/deploy.yml`) builds and deploys from that push. That needs two repository secrets, `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` (a token with Workers Scripts: Edit and Workers Routes: Edit on the zones), both set on 2026-10-16; the first deploy from GitHub ran that evening. `npm run deploy` stays for a deploy from this Mac by hand, which needs a Cloudflare login here (`npx wrangler login`). The Worker is named `quietgalaxy`.

## The domain and the forwarding address

thequietgalaxy.com and www.thequietgalaxy.com are custom domains on the Worker (`routes` in `wrangler.jsonc`, attached by `wrangler deploy` from this Mac on 2026-10-16). `worker/redirect.js` runs in front of the static files (`run_worker_first`): a request that arrives at any address other than thequietgalaxy.com, apart from the workers.dev preview, is sent to the same page at thequietgalaxy.com with a permanent redirect, and everything else is served from `dist/`. That is how www forwards, and how whereareallthealiens.com and its www forward (registered by John and attached 2026-10-16, the same way: custom domains on the one Worker). A dashboard redirect rule would have done the same for the forwarding address; the worker was chosen so the forwarding lives in the repository and every deploy carries it.
