# Baseline run 2: Kohl's

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert set the
question and chose the test case; the model did the extraction, the scoring and this write-up. Inputs
were the Moody's Retail and Apparel methodology of 12 September 2025, Kohl's FY2025 10-K, and Kohl's
Q3 10-Q, all from SEC EDGAR. Arithmetic is reproducible with `scorecard.py`.*

*Same caveat as run 1: the model was both the system under test and the author of the assessment.*

## Why this company

Kohl's was selected as the inverse of Walmart on three axes at once: mid-cap rather than the largest
retailer globally, speculative grade rather than Aa, and a department store in a structurally
declining segment. The intent was to force the qualitative descriptions to discriminate instead of
having everything land in the top category, and to test the interpolation at the other end of the
scale.

## Inputs extracted from the filing

Kohl's Corporation, fiscal year ended 31 January 2026, USD millions.

| Item | Value | Note |
|---|---|---|
| Total revenue | 15,527 | |
| Operating income | 624 | |
| D&A | 700 | |
| EBITDA | 1,324 | Derived |
| Capex | 372 | |
| Interest expense | 288 | Reported net on the face. Supplemental disclosures (cash interest paid, lease interest split) permit partial gross reconstruction; not attempted in this run. |
| Total debt | 6,630 | Revolver at zero at year end, plus long-term debt and both lease types |
| Cash | 674 | |
| Net debt | 5,956 | Derived |
| RCF | 1,099 | Derived |

The interest figure is a known defect. The methodology asks for interest expense; the filing provides
only a net figure. An earlier version of this note said no alternative existed in the document; that
was overclaimed. The supplemental cash flow disclosure and the lease note allow a partial gross
reconstruction, which this run did not attempt. The extraction spec needs a per-field fallback chain
rather than a single source per metric.

## Scorecard

| Subfactor | Weight | Metric | Numeric score |
|---|---|---|---|
| Revenue | 15% | $15.5bn | 9.39 |
| Market Characteristics | 10% | scored B | 15.00 |
| Market Position | 10% | scored B | 15.00 |
| Revenue and Earnings Stability | 10% | scored Caa | 18.00 |
| Debt/EBITDA | 15% | 5.01x | 15.01 |
| (EBITDA-Capex)/Interest | 15% | 3.31x | 12.29 |
| RCF/Net Debt | 10% | 18.5% | 12.46 |
| Financial Policy | 15% | scored Ba | 12.00 |
| **Aggregate** | | | **13.351** |

Scorecard-indicated outcome: **Ba3**. Kohl's actual Moody's corporate credit rating is **B2**, with
senior unsecured at **B3**. The run is two notches too generous.

Financial Policy was scored Ba, higher than the business would suggest, because Kohl's cut its dividend
from 222 to 56 and repaid 440 of debt during the year, which is creditor-friendly behaviour regardless
of the trajectory of the business.

## Finding 1: the errors compress toward the middle of the scale

| Company | Scorecard | Actual | Error |
|---|---|---|---|
| Walmart | A1 | Aa2 | 2 notches too harsh |
| Kohl's | Ba3 | B2 | 2 notches too generous |

Equal magnitude, opposite direction. This is not a calibration offset that could be corrected with a
constant; it is compression. The naive run pulls both ends of the scale toward the centre.

Two companies is not evidence. It is, however, a specific and cheaply testable claim, and if it holds
across more names the errors are structural rather than random, which would matter for design.

## Finding 2: less fragile than run 1, but the same mechanism decides it

The aggregate sits 0.149 from the nearest notch boundary, against 0.003 for Walmart. The Walmart knife
edge was therefore partly coincidence rather than a structural property.

Of twelve one-step changes applied to the four qualitative scores, five flip the outcome.

| Change | Aggregate | Outcome |
|---|---|---|
| Market Characteristics scored Caa | 13.651 | B1 |
| Market Position scored Caa | 13.651 | B1 |
| Revenue and Earnings Stability scored Baa | 12.451 | Ba2 |
| Financial Policy scored B | 13.801 | B1 |
| Financial Policy scored Caa | 14.251 | B1 |

The pattern from run 1 holds. What differs is only how much slack happened to exist around the
particular aggregate.

## Finding 3: the balance sheet date changes the answer

The methodology contains a section on seasonality stating that year-end metrics may not be
representative for retailers, because working capital and debt swing through the year. Retailers with
January year-ends close their books immediately after converting holiday inventory to cash, which is
the most favourable point in the cycle.

This is testable. Comparing Kohl's Q3 balance sheet, dated 1 November 2025, against the year-end one
used above:

| Item | Q3 (1 Nov 2025) | Year end (31 Jan 2026) |
|---|---|---|
| Cash | 144 | 674 |
| Inventories | 3,895 | 2,745 |
| Total debt | 6,802 | 6,630 |
| Net debt | 6,658 | 5,956 |

Net debt is 12% higher at the Q3 date, almost entirely because the cash has not yet been released from
inventory. Re-running leverage and RCF off the Q3 balance sheet moves the aggregate from 13.351 to
13.439.

That does not flip the rating here, so the effect should not be overstated. But 0.088 of movement from
nothing but the choice of balance sheet date exceeds the entire margin Walmart had. For a company near
a boundary it decides the outcome, and nothing in the 10-K signals that it is happening. The 10-Q has
to be pulled separately.

## Finding 4: model confidence carried no information

In run 1 the model knew Walmart's rating before reading anything, and was correct.

In run 2 the model's recollection was "Ba2 or Ba3, possibly lower since", stated with explicit
uncertainty. The actual answer is B2 corporate credit and B3 senior unsecured, following downgrades
during 2025. The recollection was wrong by two to three notches.

So the run where the model was confident produced a recalled answer of little evaluative worth, and
the run where it was uncertain produced a genuine derivation alongside a wrong recollection. Neither
confidence signal was diagnostic. If runs are ever scored automatically, model-reported certainty
cannot be used as a proxy for reliability.

## What transfers

The scoring engine ran both companies without modification and the interpolation behaved correctly at
both ends of the scale. The arithmetic is not the problem and probably never will be.

Two runs support no conclusions, but the same mechanism decided both outcomes: four qualitative scores
plus a small number of definitional choices about what counts as debt and what counts as interest. That
is worth treating as the working assumption until something contradicts it.

The document question that came out of this run is in `what-else-feeds-a-rating.md`.
