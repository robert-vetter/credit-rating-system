# Scorecard calibration summary

*Generated 2026-09-12 by evaluation/pipeline/calibrate_scorecard.py; reviewed by Codex, directed by Robert Vetter. Verified against the local XBRL and observation records. Gold excluded before development analysis; threshold-feature fitting nested within outer training folds. No model calls. Seed 20260911, 5 folds by company. Retrospective cross-company validation, not a rolling forecast. Definitions and caveats in the script; study history in notes/scorecard-calibration.md.*

## Coverage

| Item | Count |
|---|---|
| changed_in_scope | 158 |
| covered | 1665 |
| covered_changed | 78 |
| gold_excluded | 50 |
| invalid_fact_dates_quarantined | 1 |
| no_full_quant | 1296 |
| no_label_or_persistence | 73 |
| obs_in_scope | 3084 |
| obs_out_of_scope | 562 |

## The gap: assigned rating minus quantitative-only scorecard outcome (notches; positive = Moody's rates worse than the numbers)

| Subset | n | mean | median | sd |
|---|---|---|---|---|
| all | 1665 | 0.71 | 1 | 2.38 |
| Aa | 57 | -1.81 | -2 | 0.66 |
| A | 180 | 0.17 | 0.0 | 2.22 |
| Baa | 523 | 1.1 | 1 | 2.4 |
| Ba | 773 | 0.85 | 1 | 2.34 |
| B | 125 | 0.18 | 0 | 2.37 |
| Caa | 7 | -0.29 | 0 | 0.45 |
| no operating-lease tags | 807 | 1.18 | 1 | 2.05 |
| operating-lease tags | 858 | 0.26 | 0.0 | 2.57 |

Share of observations where the numbers-only outcome is too good: 0.54; exact: 0.18; within one notch: 0.46.

Variance of the gap: between companies 0.361, within companies 0.639 (median within-company sd 1.61 notches over 57 companies).

## Level from numbers only (Task A), out-of-fold

| Channel | subset | n | MAE | exact | within 1 | Spearman | mean signed gap |
|---|---|---|---|---|---|---|---|
| raw scorecard outcome | all | 1665 | 1.919 | 0.18 | 0.46 | 0.74 | 0.71 |
| raw scorecard outcome | changed | 78 | 1.744 | 0.128 | 0.538 | 0.726 | 0.13 |
| raw scorecard outcome | unchanged | 1587 | 1.928 | 0.182 | 0.456 | 0.734 | 0.74 |
| calibrated (pooled) | all | 1665 | 1.492 | 0.243 | 0.607 | 0.722 | -0.06 |
| calibrated (pooled) | changed | 78 | 1.385 | 0.244 | 0.641 | 0.685 | 0.23 |
| calibrated (pooled) | unchanged | 1587 | 1.497 | 0.243 | 0.606 | 0.715 | -0.07 |
| calibrated (era-split) | all | 1665 | 1.599 | 0.208 | 0.558 | 0.691 | -0.06 |
| calibrated (era-split) | changed | 78 | 1.41 | 0.244 | 0.615 | 0.659 | 0.13 |
| calibrated (era-split) | unchanged | 1587 | 1.609 | 0.206 | 0.555 | 0.684 | -0.07 |
| sector prior (train median) | all | 1665 | 2.166 | 0.201 | 0.398 | None | -0.8 |
| sector prior (train median) | changed | 78 | 2.167 | 0.141 | 0.397 | None | 0.71 |
| sector prior (train median) | unchanged | 1587 | 2.166 | 0.204 | 0.398 | None | -0.87 |
| persistence (context) | all | 1665 | 0.053 | 0.953 | 0.995 | 0.996 | -0.0 |
| persistence (context) | changed | 78 | 1.128 | 0.0 | 0.885 | 0.864 | -0.08 |
| persistence (context) | unchanged | 1587 | 0.0 | 1.0 | 1.0 | 1.0 | 0 |

## Change detection from numbers only (Task B), out-of-fold, one-notch rule

| Signal | theta per fold | n | MAE | MAE persistence | changed n | changed MAE | lift | direction correct | moved on changed | false alarm on unchanged | alarms | precision of alarm | bootstrap p(beats persistence) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s_q | [99.0, 99.0, 99.0, 99.0, 99.0] | 1665 | 0.053 | 0.053 | 78 | 1.128 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | None | 0.0 |
| s_a | [99.0, 99.0, 99.0, 99.0, 99.0] | 1665 | 0.053 | 0.053 | 78 | 1.128 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | None | 0.0 |
| s_lvl | [99.0, 99.0, 99.0, 99.0, 99.0] | 1665 | 0.053 | 0.053 | 78 | 1.128 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | None | 0.0 |
| s_anch | [99.0, 99.0, 99.0, 99.0, 99.0] | 1665 | 0.053 | 0.053 | 78 | 1.128 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | None | 0.0 |

Signals: s_q = change of the quantitative aggregate since the previous quarter end; s_a = change since Moody's last rating action; s_lvl = calibrated level minus current rating; s_anch = s_lvl plus the company's own mean past residual (needs four prior observations). Threshold theta chosen per fold on training rows by overall MAE; theta 99 means never alarm (equals persistence).

## When do the numbers move relative to the rating? (timing bound for annual figures)

| Condition | share of changed quarters | share of unchanged quarters |
|---|---|---|
| new annual figures arrived this quarter | 0.167 | 0.181 |
| latest fiscal year ended within two quarters | 0.385 | 0.361 |

Changed quarters by size of move (notches: count): {'1': 69, '2': 8, '3': 1}.

## Threshold curves (in sample, for reading the tradeoff only)

An alarm is a prediction that differs from persistence. Precision = share of alarms that moved the right way on a quarter that did change; with the one-notch rule a channel beats persistence on MAE only above one half. Odds = alarm rate on changed quarters divided by alarm rate on unchanged quarters (1 = no signal).

### s_q (signal available on 1604 of 1665 observations)

| theta | MAE | alarms | precision | odds | direction-correct recall on changed | moved on changed | false alarm on unchanged |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.2 | 261 | 0.031 | 1.07 | 0.103 | 0.167 | 0.156 |
| 0.5 | 0.176 | 221 | 0.036 | 1.17 | 0.103 | 0.154 | 0.132 |
| 0.75 | 0.154 | 184 | 0.043 | 1.29 | 0.103 | 0.141 | 0.109 |
| 1.0 | 0.139 | 159 | 0.05 | 1.52 | 0.103 | 0.141 | 0.093 |
| 1.25 | 0.122 | 131 | 0.061 | 1.86 | 0.103 | 0.141 | 0.076 |
| 1.5 | 0.113 | 116 | 0.069 | 2.14 | 0.103 | 0.141 | 0.066 |
| 2.0 | 0.096 | 86 | 0.081 | 2.35 | 0.09 | 0.115 | 0.049 |
| 2.5 | 0.085 | 66 | 0.091 | 2.43 | 0.077 | 0.09 | 0.037 |
| 3.0 | 0.079 | 52 | 0.077 | 2.13 | 0.051 | 0.064 | 0.03 |
| 4.0 | 0.071 | 38 | 0.105 | 3.05 | 0.051 | 0.064 | 0.021 |
| 99.0 | 0.053 | 0 | None | None | 0.0 | 0.0 | 0.0 |

### s_a (signal available on 1413 of 1665 observations)

| theta | MAE | alarms | precision | odds | direction-correct recall on changed | moved on changed | false alarm on unchanged |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.526 | 844 | 0.033 | 0.96 | 0.359 | 0.487 | 0.508 |
| 0.5 | 0.484 | 770 | 0.034 | 0.94 | 0.333 | 0.436 | 0.464 |
| 0.75 | 0.428 | 669 | 0.033 | 0.96 | 0.282 | 0.385 | 0.403 |
| 1.0 | 0.36 | 553 | 0.038 | 1.13 | 0.269 | 0.372 | 0.33 |
| 1.25 | 0.328 | 496 | 0.038 | 1.17 | 0.244 | 0.346 | 0.296 |
| 1.5 | 0.292 | 435 | 0.041 | 1.29 | 0.231 | 0.333 | 0.258 |
| 2.0 | 0.239 | 342 | 0.047 | 1.33 | 0.205 | 0.269 | 0.202 |
| 2.5 | 0.199 | 271 | 0.052 | 1.36 | 0.179 | 0.218 | 0.16 |
| 3.0 | 0.171 | 219 | 0.05 | 1.39 | 0.141 | 0.179 | 0.129 |
| 4.0 | 0.133 | 151 | 0.06 | 1.6 | 0.115 | 0.141 | 0.088 |
| 99.0 | 0.053 | 0 | None | None | 0.0 | 0.0 | 0.0 |

### s_lvl (signal available on 1665 of 1665 observations)

| theta | MAE | alarms | precision | odds | direction-correct recall on changed | moved on changed | false alarm on unchanged |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.864 | 1454 | 0.036 | 1.06 | 0.667 | 0.923 | 0.871 |
| 0.5 | 0.758 | 1266 | 0.036 | 1.1 | 0.59 | 0.833 | 0.757 |
| 0.75 | 0.674 | 1119 | 0.038 | 1.13 | 0.538 | 0.756 | 0.668 |
| 1.0 | 0.611 | 1004 | 0.037 | 1.09 | 0.474 | 0.654 | 0.601 |
| 1.25 | 0.509 | 821 | 0.038 | 1.18 | 0.397 | 0.577 | 0.489 |
| 1.5 | 0.417 | 658 | 0.04 | 1.18 | 0.333 | 0.462 | 0.392 |
| 2.0 | 0.311 | 463 | 0.037 | 1.01 | 0.218 | 0.282 | 0.278 |
| 2.5 | 0.228 | 315 | 0.038 | 1.02 | 0.154 | 0.192 | 0.189 |
| 3.0 | 0.183 | 232 | 0.034 | 0.82 | 0.103 | 0.115 | 0.141 |
| 4.0 | 0.109 | 99 | 0.03 | 0.63 | 0.038 | 0.038 | 0.06 |
| 99.0 | 0.053 | 0 | None | None | 0.0 | 0.0 | 0.0 |

### s_anch (signal available on 1446 of 1665 observations)

| theta | MAE | alarms | precision | odds | direction-correct recall on changed | moved on changed | false alarm on unchanged |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.674 | 1089 | 0.025 | 0.88 | 0.346 | 0.577 | 0.658 |
| 0.5 | 0.529 | 840 | 0.029 | 0.96 | 0.308 | 0.487 | 0.505 |
| 0.75 | 0.429 | 665 | 0.029 | 0.96 | 0.244 | 0.385 | 0.4 |
| 1.0 | 0.35 | 524 | 0.029 | 1.06 | 0.192 | 0.333 | 0.314 |
| 1.25 | 0.291 | 421 | 0.029 | 1.07 | 0.154 | 0.269 | 0.252 |
| 1.5 | 0.243 | 335 | 0.027 | 1.02 | 0.115 | 0.205 | 0.201 |
| 2.0 | 0.169 | 209 | 0.038 | 1.02 | 0.103 | 0.128 | 0.125 |
| 2.5 | 0.124 | 128 | 0.039 | 1.18 | 0.064 | 0.09 | 0.076 |
| 3.0 | 0.105 | 94 | 0.043 | 1.14 | 0.051 | 0.064 | 0.056 |
| 4.0 | 0.062 | 23 | 0.174 | 4.25 | 0.051 | 0.051 | 0.012 |
| 99.0 | 0.053 | 0 | None | None | 0.0 | 0.0 | 0.0 |
