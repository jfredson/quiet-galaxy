# Review: signals-and-lifetimes packet, gemini-3.1-pro-preview, 2026-10-17

Model: `gemini-3.1-pro-preview`, version string reported by the API `gemini-3.1-pro-preview`, thinking at the highest level the API allows. Date: 2026-10-17. Mode: the packet shown in full; Google Search lookup on, 0 searches made. Called through the Gemini API by `scripts/review_gemini.py` and filed verbatim the same day. Finish reason: STOP. Tokens: 21153 in, 1336 out, 13687 thinking; 1267 seconds. Never edited after filing.

Packet sent: `docs/reviews/packets/2026-10-17-signals-and-lifetimes.md` (the brief in `docs/reviews/brief.md` followed by the factor records, the claims to check, the publications logged against them, and the method extract).

Rulings: `docs/reviews/2026-10-17-rulings.md`.

---

| Item | Factor | Concerns | Proposal | Confidence |
|---|---|---|---|---|
| 1 | Factor 6 (fc) | low end | Lower from 0.01 to 0.0001 | Medium |
| 2 | Factor 6 (fc) | missing estimate | Add De Visscher (2020) and Shostak (2015) | High |
| 3 | Factor 6 (fc) | test | Remove the survey bounds test | High |
| 4 | Factor 7 (L) | low end | Lower from 100 to 10 years | High |
| 5 | Factor 7 (L) | missing estimate | Add Garrett (2025) | High |
| 6 | Factor 7 (L) | missing estimate | Add Rahvar & Rouhani (2026) | Medium |

**Item 1: Factor 6, low end**
The record currently sets the low end at 0.01, keeping the 2018 paper's span. I would lower this to 0.0001. The reason is that an intelligent species making itself detectable likely has to pass through multiple consecutive bottlenecks—such as surviving the discovery of dangerous technology, choosing to build loud beacons rather than staying quiet, and navigating a transition to artificial intelligence. When multiple uncertain choices or filters compound, the resulting fraction can drop rapidly. Lowering the floor to 0.0001 better accommodates models where the vast majority of intelligent species either destroy themselves before broadcasting or intentionally hide. This would be settled by the discovery of numerous silent or dead civilisations.

**Item 2: Factor 6, missing estimate**
The record misses Alex De Visscher (2020-01), "Artificial versus Biological Intelligence in the Cosmos: Clues from a Stochastic Analysis of the Drake Equation" (arXiv:2001.11822). De Visscher estimates that the fraction ranges from 0.0001 to 1, arguing that the development of artificial intelligence represents an additional filter with a similar selectivity to a biological species developing interstellar communication. Adding this estimate would move the range's low end downwards by a factor of 100. The record also misses Seth Shostak (2015-07), "Fraction of civilizations that develop a technology that releases detectable signs of their existence into space" (Chapter 12 in *The Drake Equation*, Cambridge University Press), who estimates the value is 1 based on our own technological trajectory; this would not move the range, as the high end is already 1.

**Item 3: Factor 6, test**
The record states that a survey result bounding how many transmitters could be nearby (like the Breakthrough Listen limits) would move the range. This is the wrong test for this specific factor. A radio search of the sky bounds the overall expected number of civilisations—the product of all seven Drake factors multiplied together—not the fraction of intelligent species that choose to communicate in isolation. Without knowing the exact values of the preceding biological factors and the lifetime factor, the silence of the sky cannot constrain this fraction alone. The right test would be sociological or technological models (arguments with numbers) on the duty cycles of communication, or the direct discovery of a hidden intelligent species.

**Item 4: Factor 7, low end**
The record currently sets the low end at 100 years, adopting Westby and Conselice's assumption based on humanity's detectable history so far. I would lower this to 10 years (or a few decades). The reason is that rapid technological acceleration could mean a civilisation's inefficient "loud" phase—leaking radio waves or shedding vast amounts of waste heat—might be extremely brief before the species either destroys itself or transitions to highly efficient, closed, and undetectable technologies. A floor of 10 years better captures this tight bottleneck. This would be settled by finding the dead ruins or brief historical technological signature of an extinct civilisation.

**Item 5: Factor 7, missing estimate**
The record misses a paper already in the site's own publications log: Michael Garrett (2025-09), "Blink and you'll miss it: How Technological Acceleration Shrinks SETI's Narrow Detection Window" (Acta Astronautica; arXiv:2509.23632). Garrett explicitly argues that civilisations may advance so fast that the phase in which their technology is detectable to us lasts "mere decades." This estimate directly addresses the detectable lifetime of a civilisation and would move the range's low end downwards from 100 years to the tens of years.

**Item 6: Factor 7, missing estimate**
The record misses another paper in its own publications log: Sohrab Rahvar and Shahin Rouhani (2026-02), "Constraining the Lifespan of Intelligent Technological Civilization in the Galaxy" (Monthly Notices of the Royal Astronomical Society Letters; arXiv:2602.22252). They derive an upper bound on the lifetime of about 5,000 years by assuming optimistic values for the biological factors and applying the silence of the galaxy. This published bound would not move the range, because it is a posterior constraint calculated backward from the silence itself; putting it into the starting range before playing out the equation would double-count the Fermi paradox.

Factor 6 (fc): The shape (log-uniform) and the high end (1) are left as they are, because the uncertainty is about which power of ten applies, and a 100% communication rate remains a mathematically defensible upper bound.

Factor 7 (L): The shape (log-uniform), high end (10,000,000,000 years), and test are left as they are, because the uncertainty spans orders of magnitude, civilisations could theoretically persist for the physical age of the galaxy, and measuring a dead civilisation's age is a valid test.

The method's rule for the chance we are alone is mathematically flawed: it should be calculated as the average of *e* to the minus *N* across all runs, rather than the share of runs where the result is simply below one.
