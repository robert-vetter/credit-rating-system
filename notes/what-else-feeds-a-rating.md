# Which documents a rating actually needs

*Analysis and write-up by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert raised the
question of whether one filing is sufficient; the model checked it against the methodology text and
against Kohl's actual EDGAR filing history. Findings marked as verified were checked against source
documents. Findings marked as assumption were not.*

Both baseline runs used a single document, the 10-K. This file records what else the task requires,
based on what turned up while doing those runs.

## Blocking issue: the label is inside the input

**Verified.** Companies disclose their own credit ratings in the 10-K, because ratings are material to
financing costs and therefore reportable.

Walmart's filing lists Moody's Investors Service at Aa2. Kohl's states directly that Moody's lowered
its corporate credit rating from Ba3 to B2 during 2025, includes a table showing B2, and separately
records that senior unsecured moved from B1 to B3. Kohl's also notes that downgrades have already
raised the coupon on its 2031 notes by 175 basis points in total, which is exactly why the disclosure
is required.

Consequence: any pipeline that puts a full 10-K in front of a model and asks for a rating has supplied
the answer along with the question. An evaluation built that way would partly measure retrieval, and it
would appear to be working well.

Stripping this is not trivial. The rating appears in a labelled table, in running MD&A prose, and
indirectly through instrument terms such as coupon step-up clauses that only exist because a downgrade
occurred.

This is a distinct problem from the memorisation issue in `walmart-first-test.md`. That one concerns
what the model already knows. This one concerns what the pipeline hands it.

## Subfactor by subfactor: can this be sourced from the 10-K

**Verified against both filings.**

| Subfactor | Weight | Available from 10-K | Note |
|---|---|---|---|
| Revenue | 15% | Yes, direct read | The only clean case of the eight |
| Debt/EBITDA | 15% | Raw parts yes, adjustments no | Spread across three chapters; Moody's restatements partly in notes, partly in debt exhibits, partly judgement |
| (EBITDA-Capex)/Interest | 15% | Company dependent | Walmart splits gross interest on the face; Kohl's shows only net on the face, and supplemental disclosures (cash interest paid, lease interest) allow partial gross reconstruction, so extraction needs per-field fallback chains |
| RCF/Net Debt | 10% | Reconstruction only | FFO is not a US GAAP line item and appears in no filing; Moody's definitions are published in its cross-sector adjustments methodology, not yet applied here |
| Market Characteristics | 10% | Partly | Item 1 and 1A give self-reported competitive narrative; the economic strength of countries of operation is external macro data |
| Market Position | 10% | Partly | Distinguishing a share leader from one of several leaders requires market share, which appears in no 10-K |
| Revenue and Earnings Stability | 10% | No | Scored against the peer group and against the company's own targets; neither is in the filing |
| Financial Policy | 15% | History yes, substance no | Descriptions concern expectations, event risk and public commitments |

Summary: one subfactor is cleanly available. Three are constructible; the definitional layer for them
is published in Moody's cross-sector adjustments methodology, though applying it takes judgment. Four
require sources outside the filing.

By weight, the 10-K supports the 55% of the scorecard that is quantitative. The 45% that is qualitative
is not in it.

Note on a methodological error in both runs: Revenue and Earnings Stability was scored anyway, without
peer data, in both Walmart and Kohl's. That score should be treated as unfounded in both cases.

## The methodology asks for inputs no single filing contains

**Verified against the methodology text.**

Revenue and Earnings Stability is scored relative to the peer group at every level of the scale, from
performance being on par with peers through to meaningfully lagging them. Scoring it requires a peer
set, which is itself a judgement, and then financial data for each peer.

The same subfactor asks whether the company meets its own financial targets. Targets appear in guidance
and on earnings calls. Kohl's states in its 10-K that it does not reconcile forward-looking guidance to
GAAP measures, so even the targets it publishes are elsewhere.

Market Characteristics states that the economic strength of the countries of operation influences the
score. That is external macro data.

Financial Policy is largely about expectations, event risk, M&A likelihood, shareholder distributions
and liquidity management, rather than anything readable off a balance sheet.

The methodology also states that ratings are forward-looking and that historical results are useful for
understanding trends. Both runs treated the prior year's accounts as the input, which is not what the
document asks for.

## What is on EDGAR and was not used

**Verified.** Filing type counts for Kohl's, recent history:

| Form | Count | Content |
|---|---|---|
| 4 | 637 | Insider transactions |
| 8-K | 113 | Material events |
| DFAN14A / PREC14A / DEFC14A / DEFA14A | 108 | Proxy contest material, 2020 to 2026 |
| 10-Q | 19 | Quarterly |
| 10-K | 6 | Used |
| DEF 14A | 5 | Proxy, executive compensation |
| SD | 7 | Conflict minerals |

The 10-Q was tested and moved net debt by 12%, see run 2.

The 8-K stream carries more than expected. Kohl's has filed 25 since January 2025. The most recent
several include item code 5.02 three times in three months, which is departure or election of directors
and officers, plus a 1.01, entry into a material definitive agreement. Management turnover and new
agreements feed Financial Policy and governance directly and appear in no 10-K.

The proxy contest material is the clearest case: 108 filings across six years, including contested
proxy statements. An activist campaign is a direct input to event risk and to whether financial policy
favours creditors or shareholders. Reading only the 10-K gives no indication it is occurring.

DEF 14A supplies executive compensation structure, which indicates what management is paid to optimise.
Compensation tied to earnings per share raises the likelihood of buybacks, which is a Financial Policy
signal.

Credit agreements and indentures are filed as exhibits rather than as their own form type. Covenants,
maturity schedules and security sit there. None were examined, and instrument-level ratings depend on
them.

## Staleness

**Verified.** As of August 2026, Kohl's most recent 10-K covers the year ended 31 January 2026 and was
filed on 13 March 2026. Since then there is a 10-Q for the quarter ended 2 May, and eight 8-Ks
including three management changes.

Rating Kohl's today from the 10-K alone therefore ignores five months of filed events. This is the
normal state rather than an edge case: a 10-K is current for a few weeks per year.

## Not on EDGAR at all

Earnings call transcripts, where guidance and management tone live. The release is sometimes attached to
an 8-K as exhibit 99.1; the call itself usually is not.

Peer financials are on EDGAR, but only once the peer set has been chosen, which is a modelling decision
that directly moves one of the eight subfactors.

Macro and country data for Market Characteristics.

Moody's own prior rating actions and press releases. Public, but they contain the answer, so they
should be excluded as inputs for the same reason as the ratings disclosure above.

## Rough priority ordering

**Assumption, not verified.** Based on two companies, so treat as a hypothesis.

The 10-Q looks like the highest-value addition. It is cheap, structured identically to the 10-K, and
directly corrects a measured distortion in three of the four quantitative subfactors.

The 8-K stream second, because event risk is written explicitly into the Financial Policy descriptions
and that is where it surfaces.

Peer data third, and awkward, because it is not a document to fetch but a modelling decision followed by
a second extraction pipeline per peer.

Proxy material is high value but only where a campaign exists, so it fits better as a conditional fetch
than a standing input.

## Suggested next checks

Re-run Kohl's with a four-quarter average balance sheet rather than a year-end snapshot, to see whether
the seasonal distortion is systematic rather than visible at one date.

Read every 8-K from one company over two years and measure what fraction is rating-relevant against
routine. The expectation is that the useful fraction is small but material; that is a guess and it is
checkable.

Select a peer set for Kohl's by hand, score Revenue and Earnings Stability properly against it, and
measure the distance from the unfounded score used in run 2.

Add a third and fourth company, including an apparel name, since the methodology contains
apparel-specific wording in the Market Position descriptions that neither Walmart nor Kohl's exercised.
