---
title: "Start here: is anyone out there, and how this site keeps count"
date: 2026-10-18
kind: start-here
summary: Is anyone out there? Enrico Fermi asked in 1950, and the sky has stayed silent. This is how the site keeps count of what we know about that silence, where the count stood on 17 October 2026, and what could change it.
sources:
  - label: The numbers as they stand
    url: https://thequietgalaxy.com/data/headline.json
  - label: How the numbers are worked out
    url: https://thequietgalaxy.com/method/
---

Over lunch in 1950, the physicist [Enrico Fermi](https://en.wikipedia.org/wiki/Enrico_Fermi) asked a question that has never gone away: [where is everybody?](/) Our galaxy is old enough and big enough that someone should have shown up by now, and nobody has. This site is my attempt to keep an honest count of what we actually know about that silence, and to change the count only when the evidence does.

In 1961 the astronomer [Frank Drake](https://en.wikipedia.org/wiki/Frank_Drake) wrote Fermi's question as a multiplication of seven quantities, so that a room of scientists could argue about one at a time, from how many stars the galaxy makes each year to how long a civilisation stays detectable. The site takes the question apart the same way.

The trouble is how far apart the guesses are. Take every hopeful estimate that has been published and multiply them together, and you get 5 trillion civilisations in our galaxy. Take every gloomy one, and you get about 1 in 10 to the 67, where 10 to the 67 is a 1 followed by sixty-seven zeros ([the home page](/)). Neither end is a serious answer on its own. So instead of picking one number, I give each of the seven pieces the range the published estimates support, multiply the seven together two hundred thousand times with a random pick from each range, and report how the answers spread out. This follows [a 2018 paper](https://arxiv.org/abs/1806.02404) by [Anders Sandberg](https://en.wikipedia.org/wiki/Anders_Sandberg), [Eric Drexler](https://en.wikipedia.org/wiki/K._Eric_Drexler) and [Toby Ord](https://en.wikipedia.org/wiki/Toby_Ord), and done this way the silence looks like roughly what you should expect, given how little we know.

This post opens the site's news section. When something is found that changes one of the ranges, or a famous claim turns out not to, I write it up here in plain words, with a link to the page it changes. A quiet week gets no post. An essay about the project is coming.

## Where the Numbers Stand

As of the last calculation, on 17 October 2026, the site puts a 42 percent chance on there being other civilisations we could detect in our galaxy right now, and a 61 percent chance on there being others somewhere in the observable universe, the part of it whose light has had time to reach us. Put the other way round, the chance that we are alone in our galaxy is 58 percent. Line up all two hundred thousand answers from smallest to largest, and the one in the middle is 0.021 civilisations in our galaxy: about one for every 47 galaxies like ours. That middle answer is below one even though the chance of company is 42 percent, because the answers spread so widely: a quarter of the runs find more than 400 civilisations, and a quarter find fewer than 1 in 10 to the 31 ([the numbers as they stand](/data/headline.json)).

These are the seven ranges behind those numbers. An outside review argued with every one of them on 17 October 2026 ([the rulings](https://github.com/jfredson/quiet-galaxy/blob/main/docs/reviews/2026-10-17-rulings.md)), and each name below links to its own page:

- [how many stars are born in the galaxy each year](/factors/star-formation/): 1 to 20 stars;
- [the share of stars that have planets](/factors/planets/): a half to all of them;
- [planets per star that could support life](/factors/habitable-planets/): 0.01 to 1;
- [the share of those planets on which life actually starts](/factors/life/): centred on one start per planet, but spread across fifty powers of ten, from almost everywhere to almost nowhere;
- [the share of planets with life on which it becomes intelligent](/factors/intelligence/): 1 in 10,000 to all of them;
- [the share of intelligent species that make themselves detectable](/factors/detectable/): 1 in 100 to all of them;
- [how long a civilisation stays detectable](/factors/lifetime/): 100 years to 10 billion years.

One of the seven matters more than all the others put together: whether life starts at all on a planet where it could. Nobody knows whether that happens on nearly every such planet or on almost none, which is why that range is so wide. Changing nothing but how the site spreads its guesses across that range moves the chance that we are alone in the galaxy anywhere from 38 to 94 percent ([how the numbers are worked out](/method/)).

## How to Follow It

Every Saturday evening, Pacific time, the site runs an automatic reading of new published work. Each of the seven pieces, and each of the thirty-two explanations for the silence, says what kind of finding would change it, and the reading searches for exactly that and reports what it found. In a single week it may stretch or shrink either end of a range tenfold at most, and it may never touch the range for whether life starts. Anything bigger comes to me ([this week's reading](https://thequietgalaxy.com/reading/)).

To try your own numbers, use the sliders on [the equation page](https://thequietgalaxy.com/equation/). To see what has been read and what it changed, there is [the story so far](https://thequietgalaxy.com/story/). [The feed](/news/feed.xml) carries every post in this section, and if you think a number here is wrong, [Feedback](/disagree/) says how to tell me and what happens next.

## What Has Happened So Far

The biggest change so far had nothing to do with the sky. On 16 October 2026, before the site went public, [the first calculation](/story/#logged-2026-10-16) came out at 88 percent alone in the galaxy. It used a simple stand-in for the range for whether life starts, one that put most of its weight on life being very rare. The 2018 paper, the only published treatment of that uncertainty, splits the weight evenly between life being easy and life being hard. The same day I switched to the paper's version, and the answer fell to 59 percent ([how the numbers are worked out](/method/)). Nothing out there had changed; what changed was how the site described what we do not know. That is worth keeping in mind before reading any other number here: the answer leans hardest on the piece nobody has measured.

The first weekly reading, run by hand the same day before the Saturday schedule began, found [a 2023 study by Siegert and colleagues](https://arxiv.org/abs/2301.10192). From the faint gamma-ray glow of radioactive aluminium, which massive stars scatter through the galaxy, it works out to 8 to 16 stars born each year: above the top of the range, which was then 10. An outside review weighed it on 17 October 2026, and [the top went up to 20](/news/2026-10-18-the-star-formation-range-widens/). The answer in the middle moved from 0.016 to 0.021, and the chance we are alone in the galaxy from 58.8 to 58.0 percent. It was the only range the review moved, and doubling the top of the best-measured of the seven pieces shifted the answer by less than one point.

The same day, I went through every statement on the site that did not yet have a source a reader could check. Of 27, 11 were confirmed, 8 corrected and 6 removed, and 2 are waiting on books I have ordered ([the list of changes](https://github.com/jfredson/quiet-galaxy/blob/main/CHANGELOG.md)). A fact that cannot be traced to something a reader can open does not stay on the site.

The site also keeps a famous claim and what became of it. In [2023](https://doi.org/10.3847/2041-8213/acf577) and [2025](https://doi.org/10.3847/2041-8213/adc1c8) one team reported a possible sign of life, a gas called dimethyl sulfide, in the air of the planet [K2-18 b](https://en.wikipedia.org/wiki/K2-18b) ([the library](/library/)). Three papers in 2025 went back over the data and found no significant evidence for it. No range moved: a reported sign of life would change the range for whether life starts, and a report that does not hold up does not.

On 18 October 2026 I had the first automatic reading checked, and [the check](/reading/) found it had been too thin: it took three minutes, opened no web page, and gave 20 of the 39 things it was meant to look at (the seven pieces and the thirty-two explanations) no search of their own. The check found two papers it had missed. In [one](https://arxiv.org/abs/2607.09460), the [Webb telescope](https://science.nasa.gov/mission/webb/) showed that the extra infrared light from two stars flagged as possible homes of giant alien structures, called [Dyson spheres](https://en.wikipedia.org/wiki/Dyson_sphere), comes from galaxies far behind them. In [the other](https://arxiv.org/abs/2608.12458), none of 129 nearby galaxies showed the waste heat such structures would give off. Neither moved a range, and the reading's rules were tightened after the check, starting with the reading of 24 October 2026.

## What to Watch For

The finding that would move the number most is a second, independent origin of life, one that does not share Earth life's chemistry: in a sample from Mars, in the plumes of Enceladus or Europa, or in the air of a planet around another star. Short of that, a planet with signs of life in its air, or a survey that finds none on hundreds of them, would move [the range for whether life starts](/factors/life/).

On the calendar, the European Space Agency's [Gaia mission](https://www.esa.int/Science_Exploration/Space_Science/Gaia) makes its [fourth data release on 2 December 2026](https://www.cosmos.esa.int/web/gaia/release), and the site has marked it as the next thing to read for the share of stars with planets. NASA's [Europa Clipper reaches Jupiter in April 2030](https://science.nasa.gov/mission/europa-clipper/) to study whether Europa's ocean could hold life; its arrival is a milestone, and only what it finds can move a range. On Mars, the [Perseverance rover](https://science.nasa.gov/mission/mars-2020-perseverance/) found features in a rock called Cheyava Falls that its team, [in a paper published in September 2025](https://doi.org/10.1038/s41586-025-09413-0), called potential signs of life. Settling it means examining the rock on Earth, and [the mission to bring it back](https://science.nasa.gov/mission/mars-sample-return/) is unfunded.

---

*Every fact in this post links to its source in the sentence that states it, checked on 19 October 2026; the full list, with the page or file each figure comes from, is [in the site's repository](https://github.com/jfredson/quiet-galaxy/blob/main/docs/news/2026-10-19-rewrites.md#sources-for-the-start-here-post).*

*Rewritten on 19 October 2026 so that a reader new to the site can follow it; no figure changed ([the earlier version](https://github.com/jfredson/quiet-galaxy/blob/db3ede5/site/src/content/news/2026-10-18-start-here.md)).*
