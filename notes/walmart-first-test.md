# Baseline run 1: Walmart

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert set the
question and the test design; the model did the extraction, the scoring and this write-up. Inputs were
the Moody's Retail and Apparel methodology of 12 September 2025 and Walmart's FY2026 10-K from SEC
EDGAR. All arithmetic is reproducible with `scorecard.py` in this directory.*

*Caveat on the setup: the model was both the system under test and the author of the assessment. Where
this write-up judges the quality of the run, that judgement is self-reported and should be treated
accordingly. The quantitative claims are checkable from the script and the filing.*

## Purpose

Establish what a frontier model does with the rating task given no scaffolding at all: the sector
methodology and one filing, in context, asked for a rating. No retrieval, no tools, no pipeline. The
point was to locate the failure modes before designing anything.

## Inputs extracted from the filing

Walmart Inc., fiscal year ended 31 January 2026, USD millions.

| Item | Value | Source in filing |
|---|---|---|
| Total revenues | 713,163 | Income statement |
| Operating income | 29,825 | Income statement |
| D&A | 14,203 | Cash flow statement |
| EBITDA | 44,028 | Derived, operating income + D&A |
| Capex | 26,642 | Cash flow statement |
| Gross interest | 2,799 | Income statement, debt 2,318 + finance lease 481 |
| Total debt | 67,095 | Balance sheet, seven lines including both lease types |
| Cash | 10,727 | Balance sheet |
| Net debt | 56,368 | Derived |
| FFO | 40,813 | Derived, CFO less working capital swing |
| RCF | 33,306 | Derived, FFO less common dividends |

EBITDA, FFO and RCF do not exist as line items in any filing. They are reconstructions. Moody's
publishes its standard adjustment definitions in a cross-sector methodology (Financial Statement
Adjustments in the Analysis of Non-Financial Corporations); this run did not apply them, which is one
of its known gaps. An earlier version of this note wrongly said the definitions were unpublished.

## Scorecard

| Subfactor | Weight | Metric | Numeric score |
|---|---|---|---|
| Revenue | 15% | $713.2bn | 0.50 |
| Market Characteristics | 10% | scored A | 6.00 |
| Market Position | 10% | scored Aa | 3.00 |
| Revenue and Earnings Stability | 10% | scored Aa | 3.00 |
| Debt/EBITDA | 15% | 1.52x | 6.07 |
| (EBITDA-Capex)/Interest | 15% | 6.21x | 9.36 |
| RCF/Net Debt | 10% | 59.1% | 4.64 |
| Financial Policy | 15% | scored Aa | 3.00 |
| **Aggregate** | | | **4.503** |

Scorecard-indicated outcome: **A1**. Walmart's actual Moody's rating is **Aa2**, disclosed in the
filing itself. The run is two notches too harsh.

A gap of one or two notches between scorecard output and assigned rating is normal, since Moody's
applies other considerations on top. The gap is not the interesting result.

## Finding 1: the outcome sits on a notch boundary

The aggregate of 4.503 lies 0.003 above the Aa3/A1 boundary at 4.5.

Re-running with one input changed at a time, seven changes flip the outcome to Aa3. None of them are
errors; each is a defensible reading.

| Change | Aggregate | Outcome |
|---|---|---|
| Market Characteristics scored Aa instead of A | 4.203 | Aa3 |
| Market Position scored Aaa instead of Aa | 4.303 | Aa3 |
| Revenue and Earnings Stability scored Aaa | 4.303 | Aa3 |
| Financial Policy scored Aaa | 4.203 | Aa3 |
| Interest taken net of interest income (7.15x) | 4.409 | Aa3 |
| Operating leases excluded from debt (1.17x) | 4.022 | Aa3 |
| RCF taken straight off CFO (60.4%) | 4.483 | Aa3 |

The scoring arithmetic is exact and deterministic. All variance in the outcome came from four
qualitative judgements made from prose and three definitional choices the methodology does not
specify.

## Finding 2: the Moody's restatements were not performed

The run used reported figures. Moody's restates onto its own definitions before computing anything:
lease obligations, pension deficits, hybrid securities given partial equity credit, securitisations
brought back on balance sheet, unusual items stripped out.

None of that was done. For Walmart the balance sheet is clean enough that it probably does not move
much, but for a levered retailer it would move leverage materially. This layer sits between extraction
and scoring and is the largest single gap between this run and an analyst's work.

## Finding 3: the model already knew the answer

Asked for Walmart's rating with no filing provided, the model returns Aa2 immediately and with a
confident explanation. It is recalling, not deriving.

Because four qualitative subfactors carry 45% of the weight and each is a judgement made from
narrative text, there is no way to establish that the known answer did not influence those four
scores. The reasoning reads equally plausible either way, so the contamination would be invisible in
the output.

This is the look-ahead problem the lab's EDGAR-Forecast benchmark was built around. Any evaluation run
on well-known large caps in the current year measures memory to an unknown degree.

## Implications

Three, stated as observations rather than design decisions.

The scoring engine should be a plain function with tests. It is roughly forty lines, it is exact, and
no variance originated there.

The qualitative subfactors are the central problem rather than a detail. They carry 45% of the weight
and they decided this outcome. Scores need to be argued from cited passages and checkable afterwards,
otherwise analysis cannot be distinguished from recall.

The Moody's adjustments belong in their own stage between extraction and scoring, since some are
mechanical and some are judgement.

Separately, the evaluation harness needs to come early rather than last. Until the point-in-time
problem is addressed there is no way to tell whether any of this works.

## Next

Run the same procedure on a company that is neither investment grade nor widely covered, and on an
older filing year, and measure how much of the apparent competence survives. See
`kohls-second-test.md` for the first of those.
