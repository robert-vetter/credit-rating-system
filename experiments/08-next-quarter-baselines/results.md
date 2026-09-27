# Experiment 08: results

*Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Follows section 6 of
[EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Verified against run R1-2026-09-27
(`runs/R1-2026-09-27/`: features.json, audit.json, manifest.json with input and script hashes,
results.json, tables.md) and its supplement (supplement.json, supplement.md, predictions.json),
which refits from the saved features and reproduces every R1 test metric exactly. Independent
review and chair consensus: waived by Robert for this study (decision 2). 13 tests pass.*

## 1. Summary

| Item | Answer |
|---|---|
| Question | Which observable facts at a quarter end predict whether a Moody's rating goes down, stays or goes up next quarter? |
| Will it change at all? | The rating level carries most of the signal (ranking score 0.148 against 0.076 for random ranking). Rating history and reported numbers add a little on average, not measurably. The null hypothesis is not rejected for "any change" |
| Which way? | The reported numbers help clearly: 74.8% of real changes get the right direction with them, 42.7% from the rating level alone (difference +16 to +47 points, 95% interval) |
| Downgrades on their own (post-hoc) | The numbers double the ranking score (0.142 against 0.071; difference +0.034 to +0.117) |
| Upgrades on their own (post-hoc) | Nothing beats the rating level (0.095) |
| In plain words | Weak numbers (falling margins, low coverage, negative EBITDA, a rating better than the numbers justify) come before downgrades. Nothing observable here comes before upgrades beyond the rating level itself |
| Next to persistence | Persistence ranks nothing (score 0.076, the base rate); every model beats it on every measure except precision at the top for the flexible model |

## 2. Headline, test years 2021 to mid-2025

1,356 company-quarters, 103 changes (61 downgrades, 42 upgrades), base rate 7.6%. Training:
2,620 company-quarters to 2020 (195 changes), gold observations excluded. "PR area" is the area
under the precision-recall curve for ranking "any change"; random ranking scores the base rate.

| Model | PR area (95% interval) | ROC area | Precision top 5% | Precision top 10% | Recall top 10% | Direction correct (95% interval) | Brier | Log loss |
|---|---|---|---|---|---|---|---|---|
| M0 persistence | 0.076 | 0.500 | 5.9% | 5.1% | 6.8% | | 0.152 | |
| M1 rating level | 0.148 (0.109 to 0.193) | 0.700 | 23.5% | 17.6% | 23.3% | 42.7% (33.1 to 53.3) | 0.139 | 0.304 |
| M2 + rating history | 0.160 (0.111 to 0.223) | 0.712 | 16.2% | 15.4% | 20.4% | 64.1% (55.7 to 72.8) | 0.139 | 0.294 |
| M3 + reported numbers | 0.155 (0.119 to 0.206) | 0.706 | 19.1% | 14.7% | 19.4% | 74.8% (64.4 to 84.1) | 0.138 | 0.292 |
| M4 flexible (trees) | 0.133 (0.100 to 0.183) | 0.683 | 13.2% | 15.4% | 20.4% | 73.8% (65.0 to 81.6) | 0.149 | 0.334 |

Differences, company-block bootstrap, 2,000 resamples:

| Comparison | Any change, PR area | Direction correct |
|---|---|---|
| M2 minus M1 | -0.017 to +0.049 (above zero in 82%) | +8.0 to +35.7 points |
| M3 minus M1 | -0.022 to +0.044 (76%) | +16.0 to +46.9 points |
| M3 minus M2 | -0.032 to +0.023 (43%) | +0.9 to +19.7 points |
| M4 minus M1 | -0.046 to +0.023 (25%) | +18.1 to +44.6 points |

The direction intervals were computed in the supplement: the specification asks for 95% intervals
on every metric, and R1 had computed them for the PR area only.

## 3. Dates

| Date concept | Value |
|---|---|
| Labels | Moody's 17g-7 files dated 2026-08-11 (Experiment 07 run R2) |
| Training outcome quarters | 2012-12-31 to 2020-12-31 |
| Test outcome quarters | 2021-03-31 to 2025-06-30 |
| XBRL | still-rated companies cached 2026-09-11; withdrawn-rating companies downloaded 2026-09-27 |
| Run | 2026-09-27 |

## 4. Input data characteristics

| Characteristic | Value |
|---|---|
| Company-quarters | 4,002 (125 companies) |
| With financial features (F0 = 1) | 2,841 (71%); training changes with financials 153 of 211, test 82 of 103 |
| SEC identifiers of withdrawn-rating companies downloaded | 65; 53 with data, 12 not found at SEC (among them Toys 'R' Us, Sears, Roebuck and Co., David's Bridal, Charlotte Russe, General Nutrition Centers) |
| Point-in-time audit | 0 of 4,002 rows use a fact filed after the prediction date |
| Feature coverage | revenue growth 3,334 rows; margin 2,841; leverage 2,450; coverage 2,476; full scorecard score and gap 1,772 (needs all four quantitative factors) |
| Gold observations excluded from training | 26 rows, 16 of them changes |

## 5. Results in detail

### 5.1 Downgrades and upgrades ranked on their own (post-hoc)

Not in the specification. Added after the training-years pattern search (5.5) showed the numbers
separating downgrades far more than upgrades, and after the R1 test results had been read.
Treat as a hypothesis for the next experiment, not a confirmed result.

| Model | Downgrades, PR area (61 events) | Upgrades, PR area (42 events) |
|---|---|---|
| M0 | 0.045 | 0.031 |
| M1 | 0.071 (0.050 to 0.095) | **0.095** (0.053 to 0.148) |
| M2 | 0.112 (0.086 to 0.148) | 0.077 (0.048 to 0.135) |
| M3 | **0.142** (0.103 to 0.190) | 0.070 (0.044 to 0.139) |
| M4 | 0.104 (0.067 to 0.173) | 0.087 (0.053 to 0.169) |
| M3 minus M1 | +0.034 to +0.117 (above zero in 100% of resamples) | -0.056 to +0.023 |

### 5.2 By test year, PR area for any change

| Year | Company-quarters | Changes | M1 | M2 | M3 | M4 |
|---|---|---|---|---|---|---|
| 2021 | 302 | 28 | 0.178 | 0.204 | 0.179 | 0.135 |
| 2022 | 306 | 19 | 0.191 | 0.245 | 0.239 | 0.218 |
| 2023 | 300 | 27 | 0.157 | 0.210 | 0.206 | 0.214 |
| 2024 | 301 | 17 | 0.100 | 0.170 | 0.152 | 0.093 |
| 2025 (Q1, Q2) | 147 | 12 | 0.133 | 0.144 | 0.225 | 0.172 |

M2 and M3 are ahead of M1 in every year; each year alone is too small for a claim.

### 5.3 The fitted function (M3)

The model gives three probabilities. For each outcome, the log odds against "unchanged" are a sum
of coefficient times input (inputs standardised: one unit is one standard deviation in the
training years, missing values set to the training median). The probability is then
P(down) = e^down / (1 + e^down + e^up), and the same for up. Strong regularisation was chosen by the
validation years (C = 0.01), so the coefficients are shrunk: read their sign and relative size,
not their exact value.

| Input | Down vs unchanged | Up vs unchanged |
|---|---|---|
| Notch (higher is worse) | +0.36 | +0.42 |
| Downgrade in the last 4 quarters | +0.19 | -0.12 |
| Upgrade in the last 4 quarters | -0.14 | -0.09 |
| Sector share upgraded, last 4 quarters | -0.23 | -0.03 |
| Sector share downgraded, last 4 quarters | -0.03 | +0.13 |
| Numbers-only scorecard score (higher is worse) | +0.17 | +0.03 |
| Gap: rating notch minus numbers-implied notch | -0.17 | +0.06 |
| Days since the latest figures were filed | +0.10 | +0.03 |
| Negative EBITDA | +0.10 | -0.06 |
| Cash / debt | -0.08 | 0.00 |
| Change in EBITDA margin | -0.07 | 0.00 |
| Change in coverage | -0.06 | 0.00 |
| Debt / EBITDA | -0.03 | -0.13 |
| Rating B (indicator) | +0.16 | +0.10 |
| All other inputs | within ±0.08 | within ±0.08 |

How to read it. Lower ratings move more in both directions. A recent downgrade raises the chance of
another and lowers the chance of an upgrade. A worse numbers-only score and a rating that is better
than the numbers justify (negative gap) both raise the chance of a downgrade. Full coefficient
tables for M1 to M3 are in `runs/R1-2026-09-27/tables.md`.

Worked example (the first test downgrade with financials, alphabetically): Advance Auto Parts at
2023-12-31, rated Baa2, downgraded in the first quarter of 2024. Inputs: no change for 20 quarters,
leverage 6.3 times, EBITDA margin down 3.2 points in a year. P(down) was 1.8% from M1, 2.8% from
M2, 2.6% from M3 and 0.7% from M4, against 4.5% for downgrades on average in the test years. The
models moved it up only slightly: a miss. Coverage and the full scorecard score were missing for
this company-quarter.

### 5.4 Calibration of P(change), test years

| Tenth of predicted probability | M1 predicted | M1 observed | M3 predicted | M3 observed |
|---|---|---|---|---|
| lowest | 1.7% | 2.2% | 2.6% | 0.7% |
| 5th | 6.2% | 4.4% | 5.5% | 6.6% |
| 9th | 12.0% | 15.6% | 11.7% | 18.5% |
| highest | 13.8% | 18.5% | 18.7% | 14.8% |

Both are roughly calibrated; the highest tenths are 15% to 19% observed. No model finds a group
where a change is more likely than not.

### 5.5 Patterns in the training years (exploratory)

Change rates next quarter by fifth of each input, training years only. These guided nothing in the
models, which were fixed beforehand.

| Input, extreme fifth | Downgrade next quarter | Upgrade | Middle fifths, downgrade |
|---|---|---|---|
| Lowest coverage, (EBITDA - capex) / interest | 11.9% | 2.6% | 1.3% to 4.2% |
| Worst numbers-only scorecard score | 12.4% | 2.0% | 1.5% to 2.5% |
| Negative EBITDA (yes against no) | 12.3% | 3.1% | 3.4% when no |
| Largest fall in EBITDA margin | 10.2% | 2.9% | 1.2% to 3.7% |
| Rating much better than the numbers (lowest gap) | 10.2% | 0.6% | 0.8% to 5.7% |
| Highest leverage, debt / EBITDA | 9.3% | 3.7% | 0.7% to 3.0% |
| Lowest notch (best ratings) | 0.6% | 0.6% | |

Strongest pairs (median splits, at least 50 rows per cell): negative EBITDA in a quarter when many
sector peers were being downgraded, 20.7% change rate against 6.3% for the opposite cell; a low
rating with a high margin, 17.2%, against 2.9% for a high rating with a high margin.

### 5.6 The Experiment 09 window: the baselines GPT-5.1 must beat

Models refitted on outcomes up to 2024-12-31; evaluated on outcome quarters 2025-03-31 and
2025-06-30. 147 company-quarters, 12 changes (10 downgrades, 2 upgrades). Per-row predictions are
saved in `predictions.json` for the comparison.

| Model | PR area | ROC area | Precision top 5% (8 flagged) | Precision top 10% (15 flagged) | Direction correct | Brier |
|---|---|---|---|---|---|---|
| M0 | 0.082 | 0.500 | 25.0% | 13.3% | | 0.163 |
| M1 | 0.133 | 0.694 | 37.5% | 26.7% | 91.7% | 0.150 |
| M2 | 0.155 | 0.724 | 12.5% | 6.7% | 91.7% | 0.149 |
| M3 | 0.175 | 0.723 | 12.5% | 6.7% | 75.0% | 0.147 |
| M4 | 0.175 | 0.784 | 0.0% | 6.7% | 83.3% | 0.152 |

Twelve changes are too few for any of these differences to mean much; the top-5% column moves by
12.5 points per company. For Experiment 09 the comparison should use the ranking score and
direction, with intervals, and M1 as the main bar.

## 6. Model, settings and cost

No LLM. scikit-learn 1.8.0, seed 20260927. M1 to M3: multinomial logistic regression, L2, C chosen
by mean validation log loss over the validation years 2017 to 2020 (M1 C = 1.0, M2 0.03, M3 0.01).
M4: gradient-boosted trees, 200 iterations, learning rate 0.05, depth 3, 20 rows per leaf. $0; one
free SEC download (76 MB).

## 7. Coverage

| Subset of the test years | n | Changes | M1 | M2 | M3 | M4 |
|---|---|---|---|---|---|---|
| All | 1,356 | 103 | 0.148 | 0.160 | 0.155 | 0.133 |
| Without gold observations | 1,332 | 89 | 0.146 | 0.156 | 0.141 | 0.121 |
| With financials | 1,025 | 82 | 0.138 | 0.148 | 0.154 | 0.134 |
| Still-rated companies only | 1,251 | 85 | 0.130 | 0.136 | 0.134 | 0.122 |

## 8. Where the errors sit

| Layer | Finding |
|---|---|
| Labels | the Experiment 07 R2 labels, with its caveats (defaults hidden behind withdrawals, secured-only issuers invisible) |
| Extraction | figures computed in code from XBRL, point in time. Walmart's revenue tag excludes membership income (about 1% of revenue); Nike tags no operating income, so it has no EBITDA-based features |
| Missing data | 29% of company-quarters have no financials; the full scorecard score exists for 44% |
| Model | the flexible model M4 does worse than the regression on ranking: with 195 training changes it overfits |
| What is not observable | the qualitative factors, events, management statements; none is in these inputs |

## 9. Sensitivities

Gold observations out of the test: same ordering, M3 slightly lower (0.141). Financials only: M3
is best (0.154). Still-rated companies only: all models lower, same ordering. Section 7.

## 10. What went wrong

| Defect | Effect | Fix | Rule that now prevents it |
|---|---|---|---|
| `fetch_xbrl.py` measures a period as months × 30 days and drops quarters that run from the 1st to the last day of a month (about 26 companies) | found while specifying; this experiment re-extracted from the raw files with true days | worked around here; the shared code and its effect on Experiments 03 and 04 are a separate task | tests with a first-of-month quarter (P13) |
| The first feature build crashed on the gold-set file format | nothing written | fixed | |
| A test expected the wrong TTM method for a first quarter | the code was right (a first quarter is its own year to date) | test corrected, a second test added for the derived fourth quarter | |
| R1's pattern search split the yes/no feature F9 into fifths, which cannot work | one line of the exploratory output was meaningless | shown correctly in the supplement | |
| R1 computed intervals only for the PR area, although the specification asks for them on every metric | direction intervals missing | computed in the supplement from an exact refit | |
| 12 SEC identifiers of withdrawn-rating companies not found | those companies have rating features only | stated in coverage | |

Null hypothesis: not rejected for "any change" (no model beats M1 on the PR area with an interval
above zero). Rejected for direction: M3 beats M1. The downgrade result is post-hoc.

## 11. Decipher and encode

| | What this experiment adds |
|---|---|
| Decipher | Downgrades follow weak numbers: low coverage, a falling margin, negative EBITDA, a poor numbers-only score, and a rating better than the numbers justify. Upgrades do not follow anything observable here beyond the rating level. The sector cycle and a recent downgrade raise the chance of the next downgrade |
| Encode | the M3 regression is the first function learned from data: inputs in, three probabilities out (section 5.3), saved with its predictions |

## 12. Decisions for consensus

| # | Decision | Options | Proposed |
|---|---|---|---|
| 1 | How Experiment 09 is judged | any change only; plus direction; plus downgrades and upgrades separately | all three, fixed in the Experiment 09 specification before the run, since this experiment shows the signal sits in direction and downgrades |
| 2 | The bar for GPT-5.1 | M1 only; M1 and M3 | M1 as the main bar, M3 next to it, both from `predictions.json` |
| 3 | Two models instead of one (your two-stage idea, refined) | keep one three-way model; separate downgrade and upgrade models | test separate models in a follow-up on these data before any LLM uses them; the upgrade side needs other inputs |
| 4 | More upgrades and downgrades | stay in one sector; widen | the numbers here (61 downgrades, 42 upgrades in the test) are near the limit; see the sector question in the flight notes |
| 5 | The extractor defect | fix `fetch_xbrl.py` now; after checking its effect on Experiments 03 and 04 | after the check (a separate task was proposed) |
