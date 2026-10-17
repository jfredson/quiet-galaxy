# Review: life-and-mind packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 0 searches made. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 16472 in, 1465 out, 8613 thinking; 1068 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-life-and-mind.md` (the brief in `docs/reviews/brief.md` followed by the factor records, the claims to check, the publications logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

Here is the review of the packet for the two biological factors.

| Item | Factor | What it concerns | Your proposal in a few words | Confidence |
| :--- | :--- | :--- | :--- | :--- |
| 1 | fl | Spread | Increase from 50 to at least 1,000 | High |
| 2 | fl | Missing estimate | Add Koonin (2007) and Totani (2020) to the list | High |
| 3 | fl | Test | Require the second example to be an independent origin | High |
| 4 | fi | Low end | Lower from 0.0001 to $10^{-10}$ or below | High |
| 5 | fi | Missing estimate | Add Barrow & Tipler (1986) or Snyder-Beattie (2021) | Medium |
| 6 | fi | Test | Add the detection of biosignatures without technosignatures | High |

**1. The spread for the chance life starts (fl)**
The record currently uses a spread of 50 powers of ten. You should increase this to at least 1,000 powers of ten. The spread is designed to bridge the optimistic view (life is easy) and the pessimistic view (life is an impossible chemical fluke). As the record's own notes point out, the published pessimists place the chance of unguided replication vanishingly low: Totani (2020) requires vastly more stars than exist in the observable universe just to get one short RNA chain, and Koonin (2007) places the chance below one in $10^{1,018}$. A spread of 50 only stretches the lower end of the bell curve down to around $10^{-50}$, which completely fails to capture the true quantitative pessimism of these published models. Evidence to settle this would be a lab demonstration of the minimum sequence length needed for self-replication, bounding how large the prebiotic search space actually is.

**2. Missing estimate for the chance life starts (fl)**
The estimates list jumps straight from the 2018 paper's model down to 0.13, omitting the actual figures from the pessimists entirely. You should move Eugene Koonin (2007, *Biology Direct*, stating $< 10^{-1,018}$ for a coupled copying system) and Tomonori Totani (2020, *Scientific Reports*, showing $10^{22}$ stars falls short by more than 80 orders of magnitude for a 40-unit RNA) from the notes into the official list of estimates. Including them explicitly justifies the need to widen the spread. This moves the bottom tail of the range massively downward.

**3. The test for the chance life starts (fl)**
The record's test line accepts "Evidence of life, or of its chemical signatures, anywhere beyond Earth (Mars samples...)". This is biologically insufficient because it ignores the possibility that life travels between neighboring planets on meteorites. Finding microbes on Mars that use identical DNA and ribosomes to Earth life would not prove that life starts easily; it would only prove that rocks can cross the solar system. The test must specify evidence of a *second, independent origin* of life (e.g., a completely alien genetic chemistry) to definitively move the factor. 

**4. The low end for the chance intelligence follows (fi)**
The current floor of 0.0001 is far too optimistic. It is based entirely on Pascal Lee's simple fraction of Earth's lifetime. However, the dominant pessimistic argument in astrobiology—the "hard steps" model originating with Brandon Carter (1983) and updated by Snyder-Beattie and colleagues (2021)—argues that if intelligence requires multiple highly improbable evolutionary transitions, the expected wait time is orders of magnitude longer than a star's lifespan. If Earth is a statistical fluke that beat these odds, the chance of it happening per planet could easily be $10^{-10}$, $10^{-20}$, or worse. The floor should be lowered to at least $10^{-10}$ to properly include the standard hard steps conclusions. Evidence to settle it would be discovering a genetic or developmental mechanism proving that complex cognition requires no highly improbable mutations.

**5. Missing estimate for the chance intelligence follows (fi)**
The record omits the most pessimistic quantitative estimates ever published on the evolution of intelligence. John Barrow and Frank Tipler (1986, *The Anthropic Cosmological Principle*, Oxford University Press) analyzed the probability of the human genome evolving by chance and calculated combinatorially microscopic probabilities, effectively placing the chance near zero (e.g., $10^{-24,000,000}$). Alternatively, Andrew Snyder-Beattie and colleagues (2021, *Astrobiology*), who are already in the site's log, model transition rates that easily yield biological probabilities below $10^{-10}$. Adding one of these explicitly numerical constraints to the estimates list justifies the drastic drop required for the low end.

**6. The test for the chance intelligence follows (fi)**
The current test line relies heavily on fossils on Earth or finding intelligence directly. It completely misses the most likely large-scale astronomical data we will gather. If upcoming space telescopes survey tens of thousands of exoplanets and find widespread, robust biosignatures (like oxygen and methane atmospheres) but continue to find absolutely zero technosignatures (no radio signals, no megastructures), that statistical limit would directly force this factor downward. Discovering that simple life is common but the galaxy remains quiet is exactly the kind of result that would cap this range sooner.

***

**Factors and features left as they are:**
*   **The centre for fl:** Left at 1. Anchoring the distribution's peak at 1 perfectly represents the "easy" hypothesis that life starts reliably when conditions allow (as it seemed to on early Earth), leaving the widened spread to do the job of reaching the pessimists.
*   **The shape for fi:** Left as log-uniform. Because the uncertainty crosses many independent evolutionary steps and several powers of ten, treating every order of magnitude as equally likely is the correct statistical approach.

**A note on the method:**
The method calculates the chance we are alone in the galaxy by simply counting the "share of runs in which the result came out below one." This is statistically incorrect and overstates the probability of being alone. If a run outputs an expected value of 0.5 civilizations, it currently counts as 100% alone, whereas the actual Poisson chance of that galaxy being empty is $e^{-0.5}$, or about 60.6%. The site should calculate the mean of $e^{-N}$ across the runs, as the 2018 paper did.
