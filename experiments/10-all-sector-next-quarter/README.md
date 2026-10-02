# Experiment 10: GPT-5.1 predicting next quarter's rating change across all sectors, specification

*Written 2026-10-01 by Claude (Opus 5.5), directed by Robert Vetter. Version 0.1, for review and
consensus. Follows [EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Built on the sizing note
([sizing.md](sizing.md)), the all-sector mapping accepted by Robert on 2026-10-01
(`evaluation/all-sectors/`), the groundwork run (`groundwork.py`, `runs/groundwork/`) and
Experiment 09, whose runner, prompts and scoring are reused. No request has been sent.*

State: design. Awaiting the decisions in section 13 and a cap.

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | Experiment 09's question with enough rating changes to answer it: can GPT-5.1, reading a company's filings and rating history at a quarter end, rank which ratings Moody's changes in the next quarter better than rating-based baselines, on actions after its training cutoff, across all corporate sectors? |
| Why | Experiment 09 found GPT-5.1 ahead of the rating-level baseline (0.237 against 0.173) but could not prove it with 11 changes. This cohort has 118 |
| Hypotheses, fixed before the run | H1 (primary): GPT-5.1's weighted PR area for any change exceeds M1's, 95% bootstrap interval above zero. H2: its direction accuracy on real changes exceeds M1's and M2's. H3: its PR area for downgrades ranked on their own exceeds M1's. All three were suggested by Experiment 09; none is chosen after seeing this cohort |
| Target | P(down), P(unchanged), P(up) for the next calendar quarter |
| Unit | company-quarter, one row per SEC company and date |
| What it is not | a test of the outstanding rating level; a test of the Retail methodology (the cross-sector prompt names no sector scorecard); a trading strategy |
| Place in the programme | decipher: whether filings carry signal for rating changes beyond the rating history, across sectors |

## 2. Dates

As Experiment 09: model `gpt-5.1-2025-11-13`, knowledge cutoff 2024-09-30 (vendor page saved in
`experiments/09-gpt51-next-quarter/evidence/`), boundary 2024-10-31, prediction dates 2024-12-31 and
2025-03-31, outcome quarters 2025 Q1 and Q2, labels from Moody's 17g-7 files dated 2026-08-11, filings
filed on or before t.

## 3. Sample and data characteristics

### 3.1 How the cohort is built

| Step | Count | Where |
|---|---|---|
| Corporate issuers in Moody's public file | 13,025 | `data/all-sectors/moodys-quarterly-labels.json` |
| Rated in the 2025 window | 4,894 | `evaluation/all-sectors/proposed-mapping.json` |
| Accepted SEC match (rules A and B, /OLD, GLEIF; two spot checks) | 1,896 | same |
| Filing a 10-K within 450 days before t, with a label at t and at the next quarter end | 1,890 company-quarters before deduplication | `groundwork.py` |
| One row per SEC company and date (entity-level label preferred, then the lowest Moody's id; 28 duplicates removed) | **1,862 company-quarters, 949 companies, 118 changes (52 down, 66 up)** | `runs/groundwork/cohort.json` |
| Design B (proposed): every change plus a seeded random third of the stable rows (seed 20261002), stable rows weighted 3 | **729 rows: 118 changes, 611 stable; 586 companies** | `runs/groundwork/design_b_rows.json`, sha256 5a7349da… |

Of the 1,862 rows, 108 are Retail companies already in Experiment 09 (9 changes); they stay in the
cohort and are also reported separately (DECISION 2).

### 3.2 Label characteristics

| Characteristic | Value |
|---|---|
| Changes by rating at t | Aaa 1, Aa 1, A 6, Baa 33, Ba 37, B 33, Caa 7 |
| Changes by prediction date | 2024-12-31: 62; 2025-03-31: 56 |
| Changes by sector (SEC SIC division) | Manufacturing 44, Transport, communications and utilities 30, Services 15, Mining and energy 11, Retail 8, Finance and real estate 5, Wholesale 3, Construction 2 |
| Level switches among changes | 8 |
| Change rate in the cohort | 6.3% |

### 3.3 Cross-sector base rates (groundwork, all corporate issuers 2012 to 2025)

| Rating at the start of the quarter | Next-quarter change | Downgrade | Upgrade | Retail (Experiment 07) |
|---|---|---|---|---|
| Aa | 3.3% | 2.6% | 0.7% | 0.0% |
| A | 3.1% | 1.9% | 1.1% | 2.5% |
| Baa | 4.0% | 1.9% | 2.0% | 4.4% |
| Ba | 6.8% | 3.5% | 3.0% | 7.1% |
| B | 7.8% | 4.8% | 2.8% | 12.9% |
| Caa | 14.3% | 8.2% | 5.9% | 18.5% |
| All | 6.1% (248,054 company-quarters, 10,092 issuers) | | | 7.8% |

82% of changes are one notch, as in Retail.

### 3.4 Imbalance plan

Case-control design B: all changes, a known third of the stable rows. Every metric is computed with
weights (changes 1, sampled stable rows 3), so precision, PR area and calibration refer to the natural
6.3% rate. The unweighted design is reported as a check.

## 4. Per-observation table

Produced by the run, as in Experiment 09, with M1 and M2's frozen probabilities next to GPT-5.1's.

## 5. Models and settings

| Setting | Value |
|---|---|
| Model and tier | `gpt-5.1-2025-11-13`, direct OpenAI Chat Completions, `service_tier: flex`, `store: false`, reasoning effort medium, JSON schema strict (as Experiment 09) |
| Runs | one per row (DECISION 4) |
| Key | the key of Experiment 09 decision 9, unless Robert names another (DECISION 6) |
| Runner | `experiments/09-gpt51-next-quarter/run.py`, unchanged, with its tests; new run folder here |
| Baselines | M0 persistence; M1 rating level and M2 rating history refitted on all corporate issuers, outcome quarters to 2024-12-31, gold excluded; predictions frozen in `runs/groundwork/baseline_predictions_window.json` (sha256 41540200…) before any request |
| Not included | Experiment 08's numbers model (M3): its scorecard features are Retail-specific and it needs XBRL for about 950 companies (DECISION 5) |

Quality of the refitted baselines on 2021 to mid-2025 (90,035 company-quarters, 4,775 changes,
random 0.053): M1 PR area 0.083, M2 0.096; direction M1 50%, M2 59%; downgrades M1 0.044, M2 0.066.
They are weaker across sectors than in Retail (M1 0.148 there).

## 6. Inputs to the model

As Experiment 09: the as-of line, the rating to assess with its type and level, the Moody's rating
history up to t, and the latest 10-K plus later 10-Qs filed on or before t, redacted with
`redact_v2`, the fragment scan and the final fragment pass; the oldest 10-Q dropped until the request
fits OpenAI's 272,000-token input limit. The filings are downloaded from EDGAR for the 729 rows (or
1,862) before the pre-flight.

## 7. Prompt and output

`prompts/`: task, probe and both schemas byte-identical to Experiment 09; the system prompt differs in
one phrase ("Retail and Apparel companies" becomes "corporate issuers"). Memory probe per company.

## 8. The calculation

None; metrics computed in code from saved answers by Experiment 09's `score.py`, extended with weights.

## 9. Metrics and baselines

| Item | Rule |
|---|---|
| Primary (H1) | weighted PR area for any change, GPT-5.1 against M1, company-block bootstrap (2,000) of the difference |
| H2 | direction on the 118 changes, against M1 and M2, bootstrap interval |
| H3 | weighted PR area for downgrades ranked on their own, against M1 |
| Also reported | M2 comparisons; ROC area; precision and recall in the top 5% and 10% (weighted); Brier and log loss; calibration by fifth; each prediction date; without the Retail rows; the Retail rows against Experiment 09; quotes verified (strict and piece check); memory flags |
| Missing answers | stay missing; metrics on answered rows with baselines on the same rows |

## 10. Controls and pre-checks

As Experiment 09 (P1 to P14), plus: the cohort and design files and the frozen baselines are hashed in
the manifest; the mapping is the accepted all-sector mapping, unchanged. P1 and P2 per DECISION 7.

## 11. Budget

| Design | Rows | Estimate at Experiment 09's averages |
|---|---|---|
| B (proposed) | 729 | about $77 (input 103 million tokens $64, output $10, probes $3) |
| Full cohort | 1,862 | about $195 |

The exact figure comes from the pre-flight token count after the filings are downloaded. Filings in
other sectors (utilities, banks' holding companies, conglomerates) may be longer than Retail's.

## 12. Known limitations before the run

| Limitation | Effect |
|---|---|
| Rule-based mapping, checked by two random samples of 30 (one error found and fixed) | a residual error rate of a few percent is possible, mostly among the 292 matches without an LEI to confirm |
| Only companies filing 10-Ks; foreign issuers excluded | the result is about US SEC filers |
| A rated subsidiary is mapped to its filing parent, as in Retail | the filings describe the parent; the label is the subsidiary's rating |
| One run per row | stability not measured |
| The numbers model is not in the comparison | GPT-5.1 is compared with rating-based baselines only |
| Two outcome quarters | a fresh Moody's file would add 2025 Q3 (DECISION 3) |

## 13. Decisions that need consensus before the run

| # | Decision | Options | Proposed | Agreed (who, date) |
|---|---|---|---|---|
| 1 | Design | B (729 rows, about $77); full cohort (1,862, about $195) | B | |
| 2 | Retail rows already in Experiment 09 | keep and report separately; exclude | keep: they also show whether the sector-neutral prompt changes the answers | |
| 3 | A third outcome quarter | download a fresh Moody's file (Robert's account) and add 2025 Q3; stay with two quarters | stay with two for this run; the fresh file is the next window | |
| 4 | Runs per row | 1; 2 | 1 | |
| 5 | Numbers model across sectors | skip; build (XBRL download for about 950 companies) | skip for this run | |
| 6 | Key and cap | key of Experiment 09 decision 9; cap after the pre-flight | cap about $100, final after the pre-flight | |
| 7 | Review and consensus | Codex review; chair; Robert's go | Robert's go, as for Experiment 09 | |
| 8 | Hypotheses | H1 to H3 as in section 1 | as stated | |

## 14. Definitions

| Term | Meaning |
|---|---|
| Case-control design | all events plus a random fraction of non-events, weighted back to the natural rate |
| Weighted PR area | the PR area with each sampled stable row counted three times |
| Frozen baseline | probabilities saved and hashed before any GPT request, so the comparison cannot be adjusted afterwards |
