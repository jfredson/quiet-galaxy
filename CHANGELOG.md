# Changelog

Every change to a range, a record, the method or the site, with absolute dates. Newest first. A range change always says which publication moved it and by how much.

## 2026-10-16

- Repository started (weekend step 2 of `docs/2026-10-16-kickoff.md`). README, CLAUDE.md (the two Belt Equation rules, adapted: commit on main and push; every design choice with confidence and an alternative), MIT licence for scripts and site, Creative Commons Attribution 4.0 for data, a commit-message date hook.
- Record schema proposed in `docs/record-schema.md`: four record types (factor, explanation, library entry, publication), one TOML file per record named for its id, a retired-ids list, and the rules the validator enforces. Twelve design choices listed with confidence and alternatives, **awaiting John's ruling**; two depart from the kickoff and say why (the folder is `data/explanations/`, not `data/theories/`; library entries link to explanations, not the other way round).
- One worked example of each record type under `data/`: the planets factor (fp) with a first-pass range of 0.1 to 1, log-uniform, from Sandberg, Drexler and Ord 2018; the dark forest explanation; Liu Cixin's trilogy as a library entry; the 2018 paper as the founding publication. **No headline yet**: one of seven factors exists.
- `scripts/compute.py validate` and a stubbed `run`, with 25 tests in `scripts/test_compute.py`.
- The name ruled by John: The Quiet Galaxy, at thequietgalaxy.com, with whereareallthealiens.com forwarding to it.
