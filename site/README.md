# The website

The public face of the records: https://thequietgalaxy.com (domain registered by John and attached 2026-10-16), with a preview address at https://quietgalaxy.jfredson.workers.dev (first deployed 2026-10-16). Built the same way as The Belt Equation's site, on the Sentient Horizons design standard (`sentient-horizons/design/`).

## How it fits together

    data/**/*.toml  ──►  scripts/export.py  ──►  site/src/data/records.json  ──►  astro build  ──►  dist/  ──►  wrangler deploy

- **Python owns the data.** `scripts/export.py` reads the records with the same loader and validator as `scripts/compute.py`, so the site can never show a record that fails the schema. It writes `src/data/records.json`. That file is generated, not committed: every `npm run build` and `npm run dev` runs the export first (`prebuild`, `predev`), so the site always reflects the records in `data/`.
- **Astro owns the pages.** Astro 5, fully static, same generator and folder layout as the sister sites. `src/lib/records.ts` is the typed view of the JSON; every page reads from it.
- **The styles are the standard's.** `src/styles/global.css` is `deep-field.css` copied unchanged (version 1.3.0 of 2026-10-08) with this site's own styles below the marked line. `Base.astro` and `Nav.astro` express the standard's shell: the theme script, the top bar with the two tiers and the toggle, the footer with the four lines and the parent line.

## Pages

| Path | What it shows |
|---|---|
| `/` | Holding version (2026-10-16): the question, the equation in plain words, the three numbers that will go at the top once the seven factors are seeded, and the four kinds of record with live counts. The first full version (the equation page with its calculator, one page per factor, the explanations by family, the library, the publications log, the method and feedback pages) is Saturday session D's work (`docs/2026-10-16-kickoff.md`, weekend step 6). |
| `/404.html` | Not found. Explanation ids are the page addresses and are never renamed, so a link that fails probably never pointed at one. |

## Commands

Run from `site/`. Needs Node (the Mac has 26) and Python 3.11 or later for the export.

    npm install          once
    npm run export       write the JSON from ../data without building
    npm run dev          local preview with live reload (runs the export first)
    npm run build        static build to dist/ (runs the export first)
    npm run preview      serve dist/ locally
    npm run deploy       build, then `wrangler deploy` to Cloudflare Workers static assets

The ordinary way to publish is not `npm run deploy` but `python3 scripts/publish.py --push` from the repository root: it validates, exports and builds everything, shows what changed, and pushes main, and the GitHub Action (`.github/workflows/deploy.yml`) builds and deploys from that push. That needs two repository secrets, `CLOUDFLARE_ACCOUNT_ID` (set 2026-10-16) and `CLOUDFLARE_API_TOKEN` (a token with Workers Scripts: Edit and, once the zone exists, Workers Routes: Edit; John creates it in the Cloudflare dashboard, as for The Belt Equation on 2026-09-25). `npm run deploy` stays for a deploy from this Mac by hand, which needs a Cloudflare login here (`npx wrangler login`). The Worker is named `quietgalaxy`.

## The domain and the forwarding address

thequietgalaxy.com and www.thequietgalaxy.com are custom domains on the Worker (`routes` in `wrangler.jsonc`, attached by `wrangler deploy` from this Mac on 2026-10-16). `worker/redirect.js` runs in front of the static files (`run_worker_first`): a request that arrives at any address other than thequietgalaxy.com, apart from the workers.dev preview, is sent to the same page at thequietgalaxy.com with a permanent redirect, and everything else is served from `dist/`. That is how www forwards, and how whereareallthealiens.com and its www forward (registered by John and attached 2026-10-16, the same way: custom domains on the one Worker). A dashboard redirect rule would have done the same for the forwarding address; the worker was chosen so the forwarding lives in the repository and every deploy carries it.
