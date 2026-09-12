> Review correction, 2026-09-12, written by Codex at Robert's direction and verified against
> the fitting code and a free corrected run: the original claim that gold never entered a
> fit was false. Company folds protected a company's own prediction but allowed its gold
> rows to train other folds. Threshold features also required nested fitting. Both paths
> are fixed. The corrected development run excludes all 50 gold observations, covers 1,665
> rows and has raw/calibrated/persistence MAE 1.919/1.492/0.053. All tested change detectors
> still choose persistence. See [the review](../docs/oos-integrity-review.md) for all splits.
> The earlier study below is retained as historical evidence. It is not a rolling forecast
> evaluation; its causal and "extraction solved" language is not supported by these tests.

# Scorecard calibration: the numbers-only rung, measured on the whole frame

*Written by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-11. Robert chose this study
for the day over re-running Experiment 03 (the API balance is exhausted, and the Experiment 03
conclusions pointed here). Every number below comes from
`evaluation/pipeline/calibrate_scorecard.py` run on the historical frame; the tables are in
`evaluation/calibration-summary.md`, the per-observation rows in
`evaluation/runs/calibration/rows.json` (regenerable). No model was called. Verified: the XBRL
re-extraction against the previous files (zero changed values, only additions), the history
pack still building after the metric fix, the double-count cases by enumeration, the
fallback tags against the primary tags where an issuer carries both. Not verified: any
fallback value against the filing text itself.*

## Why this study

Experiments 01 to 03 left the picture: reading the figures out of a filing is solved (46 of 47
within 2% of XBRL), the scorecard arithmetic sits above Moody's assigned rating, and the
model's holistic judgement is reluctant to call a change. docs/experiment-plan.md named two
cheap things for exactly this situation: rung 1 of the blinding ladder (numbers only, no
model, so no memory and no document leakage), and a monotone recalibration of the scorecard
as the most promising ablation. Both can be measured on the historical frame for nothing.
This note does that.

## What was done

**Coverage first.** With the XBRL files as they were, 1,233 in-scope observations had all
four quantitative subfactors; the rest lacked mainly an interest-expense, D&A or debt tag.
The fetcher now keeps the raw SEC companyfacts response per company under
`data/edgar/companyfacts/` (218 MB, gitignored, documented in data/README.md) and re-extracts
offline, and its tag chains got fallbacks: cash interest paid where no interest-expense
concept is tagged (0.96 of expense at the median where both exist), depreciation plus
intangibles amortisation where no combined D&A concept exists, and the combined
debt-and-capital-lease concepts, DebtCurrent and LineOfCredit for debt. Each fallback is last
in its chain, so no previously extracted value changed (checked by diff); every value carries
its tag. A double count was found and fixed on the way: 157 company-years tag a combined
debt-and-capital-lease concept next to a separate finance-lease liability, and 19 tag total
long-term debt next to its current portion; `history_pack.metrics_for` now skips the part a
combined concept already contains. This also touches the history pack the experiments use,
slightly and in the right direction. Coverage after: 1,696 of 3,084 in-scope observations, 101
of 188 rating changes, 31 of the 50 gold observations.

**The measurement.** For each covered observation at date t: the latest fiscal year whose
10-K was filed on or before t, the four quantitative subfactor scores from
`system/scorecard.py`, and the quantitative-only aggregate, defined as the weighted
quantitative score carried to the full scale (as if the four qualitative factors sat at the
quantitative average). Its Exhibit 5 outcome is the raw numbers-only rating. The gap is the
assigned rating minus that outcome, in notches; positive means Moody's rates the issuer
worse than its numbers.

**Level calibration** (Task A of the plan): isotonic regression from the aggregate to the
assigned notch, fitted and evaluated with whole companies held out (five folds, seed
20260911). Every prediction reported is from a fit that never saw the company; the gold
set is therefore never fitted on.

**Change detection** (Task B): from the persistence rating and the movement of the numbers,
predict up, unchanged or down by one notch. Four signals: the change of the aggregate since
the previous quarter end, the change since Moody's last rating action, the distance between
the calibrated level and the current rating, and that distance anchored by the company's own
mean past gap (the numbers-only version of the history pack). The alarm threshold is chosen
on the training folds by overall MAE. Metrics are those of `score_run.py`.

## Findings

### 1. The gap is about one notch, level-dependent, and mostly an accounting artefact before 2019

| Subset | n | mean gap | median | sd |
|---|---|---|---|---|
| all | 1,696 | +0.70 | +1 | 2.38 |
| Aa | 57 | -1.81 | -2 | 0.66 |
| A | 184 | +0.20 | 0 | 2.21 |
| Baa | 532 | +1.09 | +1 | 2.41 |
| Ba | 788 | +0.84 | +1 | 2.35 |
| B | 127 | +0.17 | 0 | 2.37 |
| fiscal years without operating-lease tags | 821 | +1.18 | +1 | 2.05 |
| fiscal years with operating-lease tags | 875 | +0.25 | 0 | 2.57 |

The raw numbers-only outcome is exactly right in 18% of observations and within one notch
in 46%. In the Baa and Ba range Moody's rates a median one notch below the numbers; Aa
issuers (Walmart, Costco, Home Depot) are rated about two notches above theirs, which is the
scale and market-position premium the qualitative factors carry. By observation year the
mean gap runs between +1.1 and +1.7 notches from 2012 to 2019 and is close to zero from 2020
on. That is ASC 842: before 2019 the XBRL debt excludes operating-lease liabilities, which
Moody's always capitalised, so the pre-2019 "optimism" is mostly the missing lease adjustment,
not a property of the scorecard. After 2019 the raw scorecard is nearly unbiased on average
but still spread 2.6 notches around the assigned rating.

What the gap contains, by example. Rated well above their numbers: National Vision (-2.3),
Men's Wearhouse (-2.0), Walmart (-1.8), Dollar Tree (-1.6). Rated well below: Crocs (+4.9),
Dick's (+4.2), Best Buy (+3.5), Murphy USA (+3.1), Staples and Signet (+3.1). The positive
tail is strong numbers with fashion or concentration risk, secular decline, fuel-margin
volatility, or large pre-2019 leases; the negative tail is scale, private-equity histories
and Moody's looking through shock years. The gap is the sum of Moody's adjustments, the
four qualitative factors, notching and committee judgement. It is not a qualitative grade.

The gap is not a stable per-company constant: 35% of its variance lies between companies
and 65% within them (median within-company sd 1.6 notches). The implied anchor the history
pack derives from a prior year is therefore a rough guide, not a fixed offset.

### 2. A monotone recalibration recovers about half a notch; the numbers alone place an issuer within one notch 61% of the time

| Channel, numbers only, out-of-fold | n | MAE | exact | within 1 | Spearman |
|---|---|---|---|---|---|
| raw scorecard outcome | 1,696 | 1.92 | 18% | 46% | 0.74 |
| calibrated, pooled | 1,696 | 1.48 | 25% | 61% | 0.72 |
| calibrated, fitted per lease era | 1,696 | 1.58 | 21% | 57% | 0.69 |
| sector prior (median of the training companies) | 1,696 | 2.16 | 20% | 40% | n/a |
| persistence, for context (not a Task A channel) | 1,696 | 0.07 | 94% | 99% | 0.99 |
| raw, gold subset | 31 | 2.10 | 13% | 45% | 0.75 |
| calibrated pooled, gold subset | 31 | 1.32 | 26% | 58% | 0.75 |

The fitted map is, in words, a one-notch shift down from A1 through Ba1 with compression at
both ends: an aggregate that reads A2 raw calibrates to Baa1, Baa1 to Baa3, Ba1 to Ba2; at
the weak end B1 and B2 raw calibrate to Ba3, because issuers with B-like numbers are more
often rated Ba than B. Splitting the fit by lease era does not help; the pooled map is the
one to use. The ordering the numbers give is decent (Spearman 0.74) and the calibration does
not change it; it fixes the level.

### 3. No numbers-only signal detects rating changes at quarterly resolution

With the threshold chosen on training folds by overall MAE, every signal in every fold chose
"never alarm": the numbers-only channel collapses to persistence (MAE 0.068 on this subset,
101 changed quarters all missed). The in-sample threshold curves show why. An alarm has to be
right more than half the time to pay for itself under a one-notch rule; the best precision
any signal reaches is 0.21, and only at a threshold that fires 24 times in 1,696 quarters.
There is a signal, it is just weak: at strict thresholds the aggregate's move since the
previous quarter fires two to three times as often on changed quarters as on unchanged ones,
and the median absolute move since Moody's last action is 1.1 notches on changed quarters
against 0.7 on unchanged ones. The overlap is far too large to act on.

The timing bound explains most of it. New annual figures arrived in 17.8% of the changed
quarters and in 18.0% of the unchanged ones: rating changes do not cluster in the quarters
when a 10-K lands. Moody's acts on quarterly results, guidance, transactions and events, and
89 of the 101 covered changes are single notches. An annual-figures channel is structurally
a year late and a notch coarse.

## What this changes for the design

- **Apply the calibration as a deterministic post-step of the scorecard channel**, pooled map,
  refitted only on non-gold observations before any gold claim. It is worth about half a notch
  of level error and costs nothing. The larger pre-2019 correction is not a calibration matter
  but a missing adjustment: Moody's capitalised operating leases with a rent multiple before
  ASC 842. The rule and the multiple sit in Moody's cross-sector financial statement
  adjustments methodology, not in the retail one, and should be read before implementing;
  rent expense is tagged in XBRL for those years, so it is computable.
- **This is the floor for the document channels.** A model-based change detector has to beat
  alarm precision around 0.1 to 0.2 and odds around two to three, which the numbers alone
  achieve only at thresholds that almost never fire. Experiment 02's four of six directions
  and Experiment 03's one of two are above this floor, on tiny samples.
- **The information that times a change is not in the annual figures.** The next numbers-only
  step is a trailing-twelve-month aggregate from the quarterly XBRL the fetcher already
  stores (balance-sheet instants at quarter end, flows from single quarters plus the fiscal
  year), which would give a fresh aggregate every quarter instead of once a year. For the
  document channel it confirms that the latest 10-Q belongs in the input, as in Experiment 03.
- **The implied anchor is a guide, not an offset.** Within-company variation of the gap is
  larger than between-company variation, so "relative to the prior year" must be read with a
  1.6-notch spread in mind.

## Caveats

- XBRL figures are as reported, not Moody's-adjusted; RCF is approximated as CFO minus
  dividends; debt is the sum of tagged debt and lease parts. The gap therefore includes
  Moody's adjustments, and the pre-2019 rows include the lease effect described above.
- Fallback tags are second best by construction: cash interest paid is not interest expense
  (0.76 to 1.19 of it between the 10th and 90th percentile where both exist), and depreciation
  alone understates D&A where amortisation is not tagged separately (42 fiscal years).
- Coverage is biased toward larger and more recent filers; IFRS filers and pre-2010 fiscal
  years are absent. 1,315 in-scope observations remain uncovered, mostly for missing
  operating-income or capex tags with no clean fallback.
- The threshold curves are in sample and are for reading the tradeoff, not results; the
  out-of-fold selection is the result, and it chose persistence.
- Persistence's 0.068 MAE is on the covered subset (6.0% changed), not on the full frame.
- The gold set was never used to fit or choose anything; 31 of its 50 observations are
  covered, and their out-of-fold numbers are reported for reference only.
