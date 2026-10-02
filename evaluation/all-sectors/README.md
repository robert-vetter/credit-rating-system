# evaluation/all-sectors/: the all-sector universe

*Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter. This folder holds the
committed records of the all-sector universe. The Retail and Apparel universe is separate and
unchanged (see the table below).*

## Two universes

| | Retail and Apparel | All sectors |
|---|---|---|
| Used by | Experiments 01 to 09 | Experiment 10 onwards |
| Moody's issuers | 186 entities in 161 groups, one Moody's methodology | 13,025 corporate issuers, every sector and country; 4,894 rated in the 2025 window |
| Moody's-to-SEC mapping | by hand, every pair decided by Robert (August 2026) | proposed by rules, accepted by Robert through a spot check of a random sample |
| Mapping records (committed) | `evaluation/mapping.json`, `evaluation/decisions.jsonl` | this folder: `proposed-mapping.json`, `spot-check-*.md`, `decisions.jsonl` |
| Rating labels (gitignored) | `evaluation/companies/<slug>/` | `data/all-sectors/moodys-quarterly-labels.json` |
| SEC data (gitignored) | `data/edgar/companyfacts/`, `data/edgar/companyfacts-withdrawn/`, `evaluation/companies/<slug>/filings/` | `data/all-sectors/sec-submissions/` |
| Built by | `build_frame.py`, `compile_folders.py`, `build_observations.py` and the rest of `evaluation/pipeline/` | `evaluation/pipeline/map_all_sectors.py` |

Both universes read the same raw Moody's archives (`data/moodys/`) and SEC name lists
(`data/edgar/cik-lookup-data.txt`, `company_tickers.json`) and apply the same label rule.

## Files here

| File | What it is | Decision or proposal |
|---|---|---|
| `proposed-mapping.json` | one entry per issuer rated in the 2025 window: the rule applied, the proposed SEC company with its evidence (SEC name, earlier names, industry, state, LEI check, 10-K filings at the test dates) and a status | proposal |
| `spot-check-<date>.md` | a seeded random sample of proposed matches for Robert to mark right or wrong | Robert's verdicts, once filled in |
| `decisions.jsonl` | append-only log of Robert's decisions on this mapping | decisions |

## Mapping rules

| Rule | When | Status |
|---|---|---|
| A, unique name | the cleaned Moody's name matches exactly one SEC registrant | proposed |
| B, 10-K tie-break | several registrants share the cleaned name and exactly one filed a 10-K within 450 days before 2024-12-31 or 2025-03-31 | proposed |
| Conflict | several of them filed such a 10-K | dropped (Robert, 2026-10-01) |
| Unmapped | no registrant, or none of several files 10-Ks | not mapped |
| LEI | where SEC lists an LEI: equal to Moody's confirms; different rejects | dropped if different |

Measured on the 186 Retail decisions: every rule-A match that also files a recent 10-K (56 of 56)
was the company Robert had chosen by hand. Matches that fail the 10-K check never enter a test.
