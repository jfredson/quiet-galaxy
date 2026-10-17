# How the headline is computed

Written 2026-10-16 (weekend step 3 of `docs/2026-10-16-kickoff.md`, Saturday session A, run early at John's ruling). The method itself, a random draw from each factor's range played out many thousands of times after Sandberg, Drexler and Ord 2018, was settled in the kickoff. The **parameters** below were proposed by Claude with a confidence level and the strongest alternative for each, per the ground rule of 2026-09-08, and **John ruled on all seven on 2026-10-16**, in his words: "Use the 2018 paper's log-normal rate shape for the chance life starts, adding the third shape to the record layout; accept the other six parameters as proposed." The rows are kept as proposed so the reasoning stays checkable; the ruling is marked on each. The code is `scripts/compute.py run`; the result it writes is `data/headline.json`.

## What the computation does

The Drake Equation multiplies seven quantities: how many stars are born each year, the share with planets, the planets per star that could support life, the share of those where life starts, the share of those where it becomes intelligent, the share of intelligent species that are detectable, and how long they stay detectable. Each factor's record in `data/factors/` carries a range and a shape. One run draws one value from every range and multiplies the seven. The equation is played out two hundred thousand times, and the headline numbers are read off the spread of results:

1. **The middle estimate** of detectable civilisations in the galaxy: the median of the runs. Not the mean, which the rare very optimistic runs pull up to millions (the 2018 paper's mean was 27 million against a median of 0.32).
2. **The chance we are alone in the galaxy**: the share of runs in which the result came out below one. (The exact chance that a galaxy with an expected N civilisations has none is e to the minus N; the 2018 paper's footnote 3 shows the difference from the share below one is about one percentage point, and we follow them in using the share.)
3. **The chance we are alone in the observable universe**: the share of runs in which the result came out below one per the number of Milky-Way-sized galaxies' worth of stars we can see.
4. **The width of the argument**: the result when every factor takes its most optimistic published estimate at once, and when every factor takes its most pessimistic. Computed from the estimates in the records, as the kickoff defines it; the same figure from the ranges' ends is reported beside it.

Three shapes are allowed by the record layout: `log-uniform` (every power of ten between the ends is equally likely, right for a quantity whose uncertainty is "which power of ten"), `uniform` (every value equally likely), and `log-normal-rate`, the 2018 paper's model for the chance life starts (item 7 below), which has no ends: the number of times life starts on a habitable planet over its life is drawn from a bell curve in its powers of ten, and the chance is one minus e to the minus that number. Six ranges are log-uniform; the chance life starts uses the third shape since John's ruling of 2026-10-16.

Where a low and a high are needed for a range with no ends (the band on the calculator, the width from the ranges' ends), the pessimistic end is taken as the chance one spread below the centre (about one in ten to the fifty for the paper's shape) and the optimistic end as 1; where a starting value is needed (the calculator's slider), the chance at the centre, 0.63. These are display conveniences, written in `scripts/compute.py` as `range_ends` and `range_middle`.

## Reproducing the 2018 paper

The kickoff set one test for this step: given the paper's own ranges, the numbers must reproduce its result to within noise. The paper's Table 1 (read from the arXiv text on 2026-10-16): stars per year log-uniform 1 to 100; share with planets 0.1 to 1; habitable planets per star 0.1 to 1; intelligence 0.001 to 1; detectable 0.01 to 1; lifetime 100 to 10,000,000,000 years; and for the chance life starts, a rate model: the number of times life starts per habitable planet over its life is log-normal with median 1 and a spread of fifty orders of magnitude, and the chance is 1 minus e to the minus that rate. Alone in the observable universe is N below one in ten to the ten in their text.

| | The paper | This engine, four seeds, 200,000 runs each |
|---|---|---|
| Median N | 0.32 | 0.305 to 0.326 |
| Chance alone in the galaxy | 52% | 52.1% to 52.2% |
| Chance alone in the observable universe | "nearly 38%" (Table 2: 0.38) | 39.3% to 39.5% |
| Mean N | 27 million | 25 to 29 million |

The median, the galaxy figure and the mean match. The observable-universe figure is 1.4 points above theirs, more than our run-to-run noise (0.2 points); the paper does not state how many runs it used, so the gap is most likely their noise, and the test in `scripts/test_compute.py` allows two points. Reading the fifty orders of magnitude as natural-log units instead of powers of ten gives 1.8, 49% and 27%, which does not match, so powers of ten is the right reading.

## What the first-pass ranges give

With the seven first-pass ranges as ruled on 2026-10-16 (seed 1961, 200,000 runs, ten to the eleven galaxies; the chance life starts in the paper's shape):

| | First-pass ranges | The 2018 paper |
|---|---|---|
| Median N | 0.016 | 0.32 |
| Chance alone in the galaxy | 59% | 52% |
| Chance alone in the observable universe | 40% | 38% |

The site is a little more pessimistic than the paper because two of its six log-uniform ranges are narrower on the optimistic side (stars per year 1 to 10 against their 1 to 100) or wider on the pessimistic side (habitable planets 0.01 to 1 against their 0.1 to 1; intelligence 0.0001 to 1 against their 0.001 to 1), and a little more optimistic in one (share with planets 0.5 to 1 against 0.1 to 1). Before the ruling, with a plain low-to-high stand-in for the chance life starts (every power of ten from one in ten to the 22 up to 1), the figures were a median of about 2 in a billion, 88% and 39%; the sensitivity table under item 7 shows why.

## The parameters (proposed and ruled 2026-10-16)

| # | Choice | Confidence | Standard or judgment | Strongest alternative and its cost |
|---|---|---|---|---|
| 1 | **200,000 runs.** | High. The percentages then wobble by about a tenth of a point from seed to seed, far below any rounding the site shows, and the run takes a third of a second. | Standard: it is "many thousands" with margin. | One million runs: noise of a twentieth of a point, a second and a half per run. Or 20,000: the least that "many thousands" can mean, with noise of a third of a point that would show in a diff of the JSON. |
| 2 | **A fixed seed, 1961** (the year of the equation). | High that the seed should be fixed: the published numbers then reproduce exactly on any machine, and `data/headline.json` changes only when a range changes, so every change to the headline is a visible diff with a changelog line. Low on the particular value, which is a joke and can be any number. | Standard practice for a published computation. | No seed: the numbers wobble by a tenth of a point on every run and every site build produces a diff. |
| 3 | **Independent draws**: the seven factors are drawn without any link between them. | High. It is what the 2018 paper's main text does; their Supplement II tries two kinds of link (life spreading between planets, gamma-ray bursts sterilising regions) and finds the effect modest. | Standard. | Linked draws, which would need a rule for each link and a record field to carry it; nothing published gives one. |
| 4 | **Ten to the eleven Milky-Way-sized galaxies** for "alone in the observable universe", so the threshold is N below one in ten to the eleven. | Moderate; a judgment call. The observable universe holds roughly ten to the 22 to ten to the 24 stars against the Milky Way's one to four times ten to the eleven, so the ratio is ten to the eleven to ten to the thirteen; the low end is taken because the counts of distant stars are least certain. | Judgment. | The 2018 paper's implicit ten to the ten (their threshold is N below one in ten to the ten), for direct comparability; or two trillion, the count of all galaxies (Conselice and others 2016), most of them far smaller than ours. The JSON reports all three: with the first-pass ranges, 44%, 39% and 35%. |
| 5 | **The result is written to `data/headline.json` and committed**, and `scripts/export.py` reads it (or calls `compute.headline()` directly; Saturday session D's call). | Moderate. It is data the site reads, it belongs with the data it is computed from, and committing it means a headline change is a reviewable diff. | Judgment. | Compute at site build time inside the export script with no file: nothing to commit, but the headline could change without a changelog line, and the build would depend on the computation's determinism across machines. |
| 6 | **The width is computed from the published estimates** (the smallest low or value and the largest high or value among each factor's estimates), with the width from the ranges' ends beside it. | High on following the kickoff's definition. | Standard: it is what the kickoff says. | Ranges only. Reported alongside anyway, so the alternative costs nothing to keep. |
| 7 | **Add a third shape, `log-normal-rate`, and use it for the chance life starts.** The record carries `median` (starts per habitable planet over its life; the paper uses 1) and `spread_orders` (the paper uses 50) instead of `low` and `high`. **Ruled by John 2026-10-16 and done the same day**: the shape is in the record layout and the validator, and `data/factors/life.toml` uses it, with a revision naming the paper. | Moderate that it should be added; a judgment call. Decision 4 of the record layout anticipated it: "add log-normal only when a factor needs it", and this is the factor. On reflection Claude recommended it over the committed first pass: the log-uniform stand-in put most of the weight on "life is very rare" (half of it below one in ten to the eleven), where the only published treatment of the uncertainty splits the weight evenly between "life is easy" and "life is hard", and the headline swings between 88% and 59% on that choice alone. | Judgment. | Keep log-uniform with the floor at one start per observable universe (the first pass before the ruling), which is simpler and needs no layout change, at the cost of a headline that leans pessimistic for a reason that is a modelling convenience rather than evidence. |

### How much the chance life starts moves the headline

Same six other ranges, seed and runs; only the shape or floor of the chance life starts changes.

| Chance life starts | Median N | Alone in the galaxy | Alone in the observable universe |
|---|---|---|---|
| Log-uniform 0.001 to 1 | 6.8 | 40% | 0% |
| Log-uniform 0.00001 to 1 | 0.69 | 52% | 0% |
| Log-uniform 1 in 10^10 to 1 | 0.002 | 74% | 1% |
| Log-uniform 1 in 10^22 to 1 (the first pass before the ruling) | 2 in 10^9 | 88% | 39% |
| Log-uniform 1 in 10^30 to 1 | 2 in 10^13 | 91% | 56% |
| Log-uniform 1 in 10^50 to 1 | 2 in 10^23 | 95% | 73% |
| **The 2018 paper's shape (item 7, ruled; in use)** | **0.016** | **59%** | **40%** |

The lesson for the factor page is the one the 2018 paper drew: the paradox is an artefact of treating this factor as known. `compute.py run` recomputes this table on every run and writes it to `data/headline.json` as `life_sensitivity`, and the page for the chance life starts shows it.

## Noise

Four seeds at 200,000 runs with the paper's ranges spread the galaxy figure over 0.1 points and the observable-universe figure over 0.2 points; the median moved between 0.305 and 0.326. The mean is a poor statistic here (it is set by a handful of runs in the far optimistic tail) and is reported but not shown as a headline.

## What is not done

- The ranges are a first pass. The outside-model review of the seven ranges (kickoff, after-the-weekend item 2) has not run, and every range carries `status = "first-pass"`. The ruling of 2026-10-16 settled the shape of the chance life starts, not its centre or spread, which the review may argue.
- Twenty-nine claims in the factor records are marked `verify`: mostly numbers quoted through the Wikipedia article on the Drake equation (read 2026-10-16) rather than from the paper or book itself, and Carl Sagan's Cosmos values from memory.
- The publication records for most of the estimates' sources are Saturday session C's; the estimates name them in their `source` text and will get `publication` links once the records exist.
