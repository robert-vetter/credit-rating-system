# Experiment 10, design stage: sizing an all-sector GPT-5.1 test

*Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter (decision 0). Computed by
`sizing.py` from Moody's 17g-7 archives dated 2026-08-11, SEC's name list, the confirmed Retail
mapping (used as an answer key, read only) and SEC submissions downloaded 2026-10-01 (532 companies,
Robert's approval). No model call, no spend. Outputs in `runs/sizing/` (gitignored).*

## Question

How many next-quarter rating changes in the GPT-5.1 window (outcome quarters 2025 Q1 and Q2, the
window of Experiment 09) could be tested across all corporate sectors, and what would it take?

## Result

| Step | Changes | Unchanged company-quarters |
|---|---|---|
| Corporate issuers in Moody's public file | 13,025 issuers | |
| Window company-quarters with a rating at t and at the next quarter end | 526 (276 down, 250 up) | 9,059 |
| A single SEC company matched by name | 200 | 3,114 |
| A 10-K filed within 450 days before t (the Experiment 09 rule) | **95** (44 down, 51 up; 94 companies; no duplicate company-quarters) | **about 1,365** (estimated from a seeded sample of 730, 44% eligible) |

Against Experiment 09's 11 changes, the automatic route alone gives about nine times as many.
The base rate among testable company-quarters stays near 6.5%.

| Testable changes by | |
|---|---|
| Rating at t | Aaa 1, Aa 1, A 6, Baa 29, Ba 28, B 27, Caa 3 |
| Sector (SEC SIC division) | Manufacturing 36, Transport, communications and utilities 24, Services 14, Mining and energy 8, Retail 5, Finance and real estate 4, Wholesale 3, Construction 1 |
| Prediction date | 2024-12-31: 48; 2025-03-31: 47 |
| Level switches (entity versus bond rating) | 8 |

## How good the automatic matching is

Scored on the 186 Retail entities Robert confirmed by hand:

| Outcome | Entities |
|---|---|
| A single SEC company proposed, the confirmed one | 138 |
| A single SEC company proposed, not the confirmed one | 11 |
| Several candidates | 24 |
| No candidate | 13 |

Most of the 11 "wrong" proposals are the rated subsidiary's own SEC record (Albertson's LLC, Sally
Holdings LLC, Torrid LLC) where the confirmed decision points to the parent that files the 10-Ks.
The filing check removes these as "no recent 10-K", so they cost cases rather than introduce wrong
labels.

Of the 14 Retail-frame changes in this window, the automatic route keeps 6 (Foot Locker, Qurate as
Liberty Interactive, V.F., Dollar General, Under Armour, Compass Group). Hand mapping in Experiment 09
kept 11 in-scope ones. Lost automatically: Gap and Carvana (several candidates), Kohl's and Leslie's
(no name match), RH, PetSmart and Covetrus (subsidiary or stale record). If the same ratio held across
sectors, a mapping pass that resolves parents and ambiguous names would roughly double the count, to
about 150 to 200 changes. That extrapolates from one sector and 14 cases; it is a planning figure,
not a result.

## What a test would cost

At Experiment 09's average of about $0.10 per forecast with filings (flex tier):

| Design | Forecasts | Cost |
|---|---|---|
| A. All 95 changes and all about 1,365 stable company-quarters | about 1,460 | about $145 |
| B. All 95 changes and a random third of the stable ones, weighted back to the natural rate | about 550 | about $55 |
| C. As B after a mapping pass (about 175 changes, about 600 stable) | about 775 | about $80 |

Design B keeps precision measurable: each sampled stable company-quarter counts three times in the
metrics. With about nine times the changes of Experiment 09, the interval on the difference to the
rating-level baseline would be roughly three times narrower.

## What else a test needs

| Item | Note |
|---|---|
| Baselines across sectors | the rating-level and history models of Experiment 08 were fitted on Retail only; refit on all corporate rating histories 2012 to 2024 (free; also gives a cross-sector version of the rating table sent to Xiaowei) |
| Numbers model across sectors | needs SEC XBRL for the testable companies (free download) |
| Prompt | describes a Retail and Apparel analyst; a sector-neutral wording is needed and must be fixed before the run |
| Mapping decisions | the project rules make Moody's-to-SEC mappings human decisions: Robert confirms the proposed matches for every company in the test (about 95 to 200 changes plus the stable sample), or a sample with an agreed error rate |
| A third outcome quarter | a fresh download of Moody's public file (Robert's account) should now reach about September 2025 and would add 2025 Q3 |

## Limitations

The counts are worldwide issuers filtered to SEC filers by name; how many US companies are missed by
the name matcher is not measured. A parent and its rated subsidiary are separate Moody's entities;
the 95 testable changes have distinct SEC companies and dates, but the stable estimate does not
remove such pairs. The stable eligibility rate comes from a sample of 730 company-quarters.

## Decisions for Robert

| # | Decision | Options | Proposed |
|---|---|---|---|
| 1 | Go on to an Experiment 10 specification | yes; stay in Retail | yes |
| 2 | Mapping | automatic only (95 changes); a mapping pass with Robert confirming (about 150 to 200) | the mapping pass, with Claude proposing candidates and Robert confirming |
| 3 | Design | A, B or C above | C, or B if the mapping pass is not wanted |
| 4 | Newer labels | download a fresh Moody's file now | yes, it adds a quarter at no cost |
