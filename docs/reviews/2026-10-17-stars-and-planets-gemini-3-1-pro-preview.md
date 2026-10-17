# Review: stars-and-planets packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 0 searches made. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 21744 in, 1267 out, 11434 thinking; 321 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-stars-and-planets.md` (the brief in `docs/reviews/brief.md` followed by the factor records, the claims to check, the publications logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

| Item | Factor | Concern | Proposal | Confidence |
|---|---|---|---|---|
| 1 | How many stars are born each year (R*) | Shape | Change to uniform | Medium |
| 2 | How many stars are born each year (R*) | High end | Raise to 20 | High |
| 3 | How many stars are born each year (R*) | Missing estimate | Add Ruiz-Lara et al. (2020) at ~4x normal rate | High |
| 4 | How many stars are born each year (R*) | Test | Update outside bounds to 1 to 20 | High |
| 5 | The share of stars that have planets (fp) | Shape | Change to uniform | Medium |
| 6 | The share of stars that have planets (fp) | Missing estimate | Add Zhu & Dong (2021) at ~100% | High |
| 7 | Planets per star that could support life (ne) | Low end | Lower to 0.00001 (1e-5) | High |
| 8 | Planets per star that could support life (ne) | Missing estimate | Add Hsu et al. (2019) at ~0.2 | High |

**Item 1.** For the rate at which stars are born (R*), the record currently uses a log-uniform shape. I would change this shape to uniform. The uncertainty for this factor spans roughly one order of magnitude (between 1 and 20 stars a year), and the debate hinges on straightforward linear numbers (such as 1.3 versus 3 versus 16) rather than which power of ten applies. A uniform shape spreads the likelihood evenly across these linear estimates. Consensus among statisticians on modeling narrow, linearly bounded rates would settle this.

**Item 2.** The record currently sets the high end for R* at 10 stars a year. Given your specific question about the Siegert (2023) measurement and the Quintana (2025) census, the top should rise past 10 to 20. Moving it to 20 fully envelopes Siegert's upper bound of 16 stars a year while leaving room for the higher historical bursts that produced the stars hosting civilisations today. The floor of 1 definitely holds, as Quintana's measurement of 1.3 stars a year is comfortably contained just above it. A final, universally agreed-upon history of the galaxy's star formation would settle the exact upper bound.

**Item 3.** The R* record is missing a major study by Tomás Ruiz-Lara and colleagues, published in *Nature Astronomy* in May 2020. By looking at the ages of millions of stars, they reconstructed the Milky Way's history and found past episodes where the star formation rate surged to roughly four times the normal background rate. Adding this paper would move the range's high end upward (justifying the rise to 20 in Item 2), as it shows the historical average over the galaxy's life was driven significantly higher by these bursts.

**Item 4.** The R* record's "what would move this" test currently looks for new measurements falling outside "one to ten stars a year." Because the range's top should expand to 20, I would update this test to look for measurements that fall outside "one to twenty stars a year" so it remains the correct trigger for opening a review. 

**Item 5.** For the share of stars with planets (fp), the record uses a log-uniform shape over a narrow span of 0.5 to 1. I would change this shape to uniform. When a linear fraction only varies by a factor of two, the uncertainty is not spanning broad powers of ten. A uniform distribution is the mathematically standard and intuitive choice for a simple percentage bounded between 50 and 100 percent. Statistical best practices for variables with a very narrow, rigid ceiling would settle this.

**Item 6.** The fp record is missing a comprehensive review paper by Wei Zhu and Subo Dong, published in the *Annual Review of Astronomy and Astrophysics* in 2021. They synthesized years of exoplanet demographics to conclude that the total fraction of stars with detectable planets is close to 100 percent. Adding this would not move the range, as the high end is already capped at 1, but it firmly cements the modern consensus that planets are the absolute rule.

**Item 7.** For the planets per star that could support life (ne), the record sets the low end at 0.01 based on Ward and Brownlee's Rare Earth requirements. However, as the record's own note from October 16 rightly points out, Ward and Brownlee's 1% to 0.001% (0.00001) span applies to their reading of the *ordinary* equation before they even introduce their long list of stringent extras. I would lower the floor to 0.00001 (1e-5) to accurately reflect their published baseline. A definitive future count of how many worlds actually keep their water and atmospheres for billions of years would settle this.

**Item 8.** The ne record is missing the estimate by Danley Hsu, Eric Ford, Darin Ragozzine, and colleagues, published in *The Astronomical Journal* in August 2019. Combining Kepler and Gaia data, they calculated an occurrence rate of roughly 0.2 Earth-size planets in the habitable zone per Sun-like star. Adding this would not move the range, because 0.2 is already safely tucked between the low and high ends, but it serves as a highly cited baseline in the scientific literature.

None of the three factors in this packet are left entirely as they are; every factor requires at least a shape adjustment, an expanded end, or the addition of a missing estimate.
