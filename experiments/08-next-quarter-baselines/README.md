# Experiment 08: predicting next quarter's rating change without an LLM, specification

*Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Version 0.1, for review and
consensus. Follows [EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Built on Robert's notes of
2026-09-27 and the flight notes of 2026-09-26. Checked against: Experiment 07 run R2 (cohort,
labels, counts), the cached SEC companyfacts files under `data/edgar/companyfacts/`, the compact
`evaluation/companies/*/xbrl.json`, `evaluation/pipeline/calibrate_scorecard.py` and
`history_pack.py`, and `evaluation/goldset.json`. No result has been computed.*

State: design. Awaiting the decisions in section 13.

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | Which observable facts at the end of a quarter predict whether a company's Moody's rating goes down, stays or goes up in the next quarter, and can a fitted function turn them into useful probabilities? |
| Null hypothesis | No model beats the rating-level baseline (the Experiment 07 table) on the ranking measures of section 9 in the test years |
| Target | down / unchanged / up in the next quarter, as three probabilities (flight notes, file 02, option B) |
| Unit of observation | company-quarter, as in Experiment 07 |
| What it is | the first predictor, fitted on the past and tested on later years; the bar every LLM must clear; a search for which numbers precede Moody's actions |
| What it is not | an LLM test; a test of the qualitative factors; a trading strategy |
| Place in the programme | decipher (which facts precede Moody's actions) and encode (the fitted function is the first encoded piece of logic learned from data). Sets the baselines for Experiment 09 |

What is observable at prediction time, and what is not (Robert's note of 2026-09-27):

| Input | Observable at the end of a quarter? | Used |
|---|---|---|
| The current rating and its history | yes, public | yes |
| The quantitative scorecard inputs (revenue, EBITDA, debt, interest, capex, cash flow) | yes, from the latest 10-Q or 10-K filed by then (XBRL) | yes |
| Moody's four qualitative factor grades | no; Moody's does not publish them per quarter | no |
| What the numbers alone imply against the actual rating | yes, computed | yes, as a partial stand-in for the qualitative side: the rating already contains Moody's full judgement |

How it differs from the change test inside the 2026-09-12 calibration study, which found no
signal:

| | Calibration study, 2026-09-12 | Experiment 08 |
|---|---|---|
| Numbers | annual, from the latest 10-K | quarterly, trailing twelve months, from the latest 10-Q or 10-K |
| Rating history | persistence only | rating level, momentum, time since last change, the sector cycle |
| Output | a yes/no alarm | three probabilities |
| Judged by | mean notch error, which at a 6% change rate rewards never alarming | ranking measures (section 9) |
| Companies | survivors only | all in-scope companies, including withdrawn ratings |
| Split | companies held out, all years mixed | by time: fit on the past, test on the future |

## 2. Dates

| Date concept | Value | Source |
|---|---|---|
| Rating labels | Moody's 17g-7 files dated 2026-08-11, actions through August 2025 | Experiment 07 |
| Quarterly grid | prediction dates 2012-09-30 to 2025-03-31; outcome quarters to 2025-06-30 | Experiment 07 |
| Training years | outcome quarters up to 2020-12-31 (DECISION 1) | |
| Test years | outcome quarters 2021-03-31 to 2025-06-30 | |
| Experiment 09 window | outcome quarters 2025-03-31 and 2025-06-30 (147 company-quarters); the model is refitted on outcomes up to 2024-12-31 | flight notes, file 03 |
| XBRL | companyfacts cached 2026-09-11 for the 86 still-rated companies; not cached for the 74 withdrawn-rating groups (DECISION 3) | `data/edgar/companyfacts/` |
| Model cutoff | not applicable, no model | |

## 3. Sample and data characteristics

### 3.1 Cohort

The Experiment 07 run R2 cohort, frozen by hash: 125 in-scope companies with quarterly records
(72 still rated, 53 withdrawn-rating), 4,002 company-quarters, 314 changes.

### 3.2 Label characteristics, known before fitting

| Period | Company-quarters | Changes | Downgrades | Upgrades | Of which from withdrawn-rating companies |
|---|---|---|---|---|---|
| Training, to 2020 | 2,646 | 211 | 108 | 103 | 108 changes |
| Test, 2021 to mid-2025 | 1,356 | 103 | 61 | 42 | 18 changes |
| Experiment 09 window | 147 | 12 | 10 | 2 | |

Half the training changes come from companies whose rating was later withdrawn. A model that
uses reported numbers learns from them only if their XBRL is available (DECISION 3).

### 3.3 Imbalance plan

The natural rate (7.8%) is kept in training and test; no resampling, because the output is a
probability and resampling would distort it. The ranking measures of section 9 do not depend on
a threshold. A cost of a missed change against a false alarm is not needed for this experiment,
because nothing is flagged; it is needed before any flagging rule is built.

### 3.4 Data coverage, known before fitting

| Item | Value |
|---|---|
| Still-rated companies with quarterly revenue in the compact `xbrl.json` | 50 of 86 |
| Why 36 lack it | about 26 because of a defect in `fetch_xbrl.py` (section 12): the raw files hold their quarterly figures. About 10 file no 10-Q with XBRL: foreign filers (JD.com, Vipshop, Cencosud), filers that stopped before XBRL (7-Eleven, Ahold), companies without SEC financials (Gildan, Canada Goose, Amer Sports, Samsonite) |
| Withdrawn-rating companies with any XBRL | not known until downloaded (DECISION 3). XBRL starts around 2009 to 2011; private companies with public bonds may or may not file |

## 4. Per-observation table

Not applicable; aggregate results and per-feature tables only.

## 5. Models

No LLM. Five models, fixed before fitting:

| # | Model | Inputs | What it answers |
|---|---|---|---|
| M0 | persistence | none | the floor: probability of a change 0 for everyone |
| M1 | rating level | rating category at t | the Experiment 07 table, estimated on training years only |
| M2 | rating history | M1 plus momentum, time since last change, sector cycle (features R1 to R6) | does the rating history add to the level? |
| M3 | rating history and numbers | M2 plus the reported numbers (features F1 to F13) | do the filings' numbers add to the rating history? |
| M4 | flexible pattern search | the same inputs as M3 | are there non-linear patterns a regression misses? |

M1 to M3 are multinomial logistic regressions (three outcomes), with L2 regularisation whose
strength is chosen by time-ordered cross-validation inside the training years. They are the
"function you input parameters into": the fitted coefficients are published with a worked
example. M4 is a gradient-boosted tree model (scikit-learn `HistGradientBoostingClassifier`,
fixed settings: 200 iterations, learning rate 0.05, maximum depth 3, minimum 20 samples per
leaf), with the same inputs. scikit-learn 1.8.0, seed 20260927.

## 6. Inputs (features), fixed before fitting

Every feature at prediction date t uses only facts filed on or before t, and only labels of
actions on or before t.

| # | Feature | Definition |
|---|---|---|
| R1 | rating category | Aa and above, A, Baa, Ba, B, Caa and below; one indicator each |
| R2 | notch | position on the 21-notch scale |
| R3 | recent downgrade | a downgrade in the four quarters up to t |
| R4 | recent upgrade | an upgrade in the four quarters up to t |
| R5 | quarters since last change | capped at 20; counted from the history start if none |
| R6 | sector cycle | share of cohort companies downgraded, and share upgraded, in the four quarters up to t |
| F1 | revenue growth | trailing-twelve-month revenue against the same measure four fiscal quarters earlier |
| F2 | EBITDA margin | trailing-twelve-month (operating income plus D&A) over revenue |
| F3 | change in EBITDA margin | F2 against four fiscal quarters earlier, in percentage points |
| F4 | leverage | debt over trailing-twelve-month EBITDA, debt as in `history_pack.metrics_for` (including leases where tagged) |
| F5 | change in leverage | F4 against four fiscal quarters earlier |
| F6 | coverage | (EBITDA minus capex) over interest, trailing twelve months |
| F7 | change in coverage | F6 against four fiscal quarters earlier |
| F8 | liquidity | cash over debt |
| F9 | negative EBITDA | trailing-twelve-month EBITDA below zero |
| F10 | numbers-only scorecard score | the quantitative-only aggregate of `history_pack.quant_contribution`, on trailing-twelve-month values |
| F11 | change in F10 | against four fiscal quarters earlier |
| F12 | gap | the rating's notch minus the notch the numbers alone imply (F10 mapped through the scorecard outcome table): positive means the rating is worse than the numbers |
| F13 | staleness | days between t and the filing date of the latest figures used |
| F0 | financials available | 1 if F1 to F12 could be computed at t, else 0; missing values are filled with the training median and flagged |

Trailing-twelve-month flows are the sum of the latest four fiscal quarters filed by t. A fourth
fiscal quarter is derived as the annual value minus the first three quarters of that fiscal year,
when the 10-K is filed by t. Balance-sheet values are the latest filed by t. Quarterly values are
extracted from the raw companyfacts files by this experiment with true calendar-day durations (80
to 100 days for a quarter), not taken from the compact `xbrl.json` (section 12). The earliest
filing of a value wins; restatements are not applied backwards.

Exploratory pattern search (Robert's "hidden patterns"): on the training years only, the change
rate by fifth of each feature, and the pairs of features with the largest joint effect. Reported
as exploratory. It does not change the feature list or any model; a pattern found here becomes a
candidate for the next experiment, tested on data it was not found on.

## 7. Prompt and output

Not applicable.

## 8. The calculation

All code in this folder: `build_features.py` (features, point-in-time), `fit_models.py` (M0 to
M4, evaluation), tests in `test_*.py`. Scorecard arithmetic from `system/scorecard.py` through
`history_pack.py`; no new scoring rule.

## 9. Metrics and baselines

| Item | Rule |
|---|---|
| Change detection | rank company-quarters by P(down) + P(up). Area under the precision-recall curve (headline); area under the ROC curve; precision and recall among the top 5% and top 10% |
| Direction | on real changes only: share where P(down) > P(up) matched the direction |
| Probabilities | Brier score and log loss over the three outcomes; a calibration table by tenth of predicted probability |
| Baselines | M0 and M1 next to every number; M1 must be beaten for any claim |
| Uncertainty | company-block bootstrap on the test years, 2,000 resamples, 95% intervals; the difference M3 minus M1 with its interval |
| Coverage | every metric on all test company-quarters and on those with financials (F0 = 1), each with its n |
| Experiment 09 window | the same metrics on the 147 company-quarters, models refitted on outcomes up to 2024-12-31; these numbers are the baselines Experiment 09 must beat |
| Split rule | no training row has an outcome quarter in the test years; the sector-cycle feature uses only labels up to t |

## 10. Controls and pre-checks

| # | Check | Applies? | Evidence |
|---|---|---|---|
| P1 | Specification reviewed by the other model family | yes, unless Robert waives it as for Experiment 07 (DECISION 6) | |
| P2 | Chair consensus or Robert's decision to proceed | yes (DECISION 6) | `decisions.md` |
| P3 | Authorization and cap | no spend; a download needs Robert's approval (DECISION 3) | |
| P4 | Cohort frozen | Experiment 07 R2 cohort by hash | run folder |
| P5 | Inputs frozen | hashes of every rating, observation and companyfacts file | run folder |
| P6 | Point-in-time audit | every feature value's filing date asserted on or before t; every label date on or before t for R3 to R6 | `audit.json` |
| P7 to P12, P14 | redaction, tools, tokens, price, cutoff, probe, pilot | no model | |
| P13 | Tests | fixtures: a quarter with a first-of-month start (the Walmart case); a derived fourth quarter; a value filed after t is excluded; a restated value keeps the earliest filing; no training row in the test years; the sector-cycle feature ignores later labels; gold rows handled per DECISION 2 | `test_*.py` |

## 11. Budget

$0. No model call. The SEC download (DECISION 3) is free.

## 12. Known defects and limitations before the run

| Defect or limitation | Effect | Handling |
|---|---|---|
| `fetch_xbrl.py` approximates a period as months × 30 days, so quarters running from the 1st to the last day of a month (about 26 companies, among them Walmart, Nike and O'Reilly) measure 60 days and are dropped | the compact `xbrl.json` lacks their quarterly flows | this experiment re-extracts from the raw files with true days; the shared code is not changed here. Its effect on earlier experiments is a separate task |
| Withdrawn-rating companies have no cached XBRL | half the training changes lack financial features | DECISION 3 |
| XBRL starts around 2009 to 2011 | the earliest prediction dates have shorter histories | F0 flag; coverage reported |
| Tagging differs between companies and over time | some ratios are missing or mis-measured | the `fetch_xbrl.py` fallback chains, reused; coverage reported per feature |
| No qualitative grades | the model cannot see business-profile changes | the rating and the gap (F12) stand in partly; the rest is for LLMs to add |
| 211 training changes | limited room for many features; M4 can overfit | regularisation; fixed feature list; test only on later years |
| Regime change over time (COVID in training, the 2023 downgrade wave in test) | a model fitted on the past may not transfer | this is exactly what a time split measures; reported by year |
| One sector | results may not transfer | stated |
| Labels end August 2025 | no test after that | Experiment 09 window is the last usable one |

## 13. Decisions that need consensus before the run

| # | Decision | Options | Proposed | Agreed (who, date) |
|---|---|---|---|---|
| 1 | Split year | train to 2019, 2020 or 2021 | train to 2020, test 2021 onwards: roughly two thirds of the changes for training, and the test covers the 2023 downgrade wave | |
| 2 | Gold-set observations (26 in training years, 24 in test years) | include; exclude from training; exclude everywhere | exclude from training, keep in test, and report the test with and without them. The gold set must never be tuned on | |
| 3 | XBRL for the withdrawn-rating companies | download their companyfacts from SEC EDGAR (free, about 74 files of 1 to 20 MB, `data.sec.gov/api/xbrl/companyfacts/`); do without | download, into the same gitignored cache; without it M3 learns from half the training changes | |
| 4 | Feature list | as section 6; fewer; more | as section 6, fixed now | |
| 5 | Include the flexible model M4 | yes; no | yes, reported next to M3; it answers the "hidden patterns" question | |
| 6 | Review and consensus before running | Codex review and the chair's agreement; Robert decides to run now, as for Experiment 07 (free, no model, no labels changed) | Robert's decision | |
| 7 | Top-k levels | 5% and 10%; a fixed number per quarter | 5% and 10% | |

## 14. Definitions

| Term | Meaning | Example |
|---|---|---|
| Trailing twelve months | the sum of the latest four quarters of a flow such as revenue | Q3 2024 back to Q4 2023 |
| Point in time | only facts filed on or before the prediction date are used | a 10-Q filed 2024-11-05 cannot be used at 2024-09-30 |
| Precision-recall curve | for every cut-off in the ranking, the share of flagged quarters that changed against the share of changes caught | area 0.078 is what random ranking gets at a 7.8% change rate |
| Brier score | the mean squared distance between predicted probabilities and what happened | lower is better; 0 is perfect |
| Calibrated | predicted probabilities match observed frequencies | of quarters given 20%, about 20% change |
| Gap | rating notch minus the notch the numbers alone imply | rating Ba3 (12), numbers imply Ba1 (10): gap +2, the rating is worse than the numbers |
