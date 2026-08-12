# Leakage audit

*Written by Claude (Opus 5), directed by Robert Vetter, August 2026. Prompted by Giesecke's point that
ratings are published widely and can leak through channels other than the filing. Every finding below
was tested against actual EDGAR documents; the sample is the seven companies already used (Walmart,
Kohl's, Target, Dollar General, Gap, Macy's, Victoria's Secret). Findings are labelled confirmed,
where a source document was read, or untested.*

## Summary

Five channels examined. Two are real problems, one is a false alarm, one is handled, and one is
undecidable and needs a policy call.

The headline finding is that **rating-based pricing grids live in 10-Q exhibits**, and the 10-Q is the
document the experiment plan recommends adding first. Adding it naively would import an explicit
mapping from Moody's rating symbols to interest margins.

The second finding is that **not all leaks can be stripped**, because at least one sits inside a
disclosure that is also legitimate input.

## Channel 1: ratings disclosure in the 10-K

**Confirmed, handled.** Found in all seven companies, both as a labelled table and in running MD&A
prose. Line-based stripping on agency names, the phrases credit rating and investment grade, and
orphaned table rows containing rating symbols removes it. Verified afterwards: zero agency mentions
and zero rating symbols remaining in all five stripped filings, with the financial statements intact.

## Channel 2: rating-informative language that names no agency

**Confirmed, and only partly strippable.** This is the channel Giesecke's point implies, and it turns
out to be real but subtle.

Scanning all seven filings for step-up language, investment-grade status references, downgrade
references and pricing-grid language, then filtering to lines that mention no rating agency:

| Company | Agency-free hits | Verdict |
|---|---|---|
| Kohl's | 2 | False positive, SOFR plus applicable margin, no grid in the 10-K |
| Dollar General | 3 | **One real leak**, two false positives |
| Macy's | 2 | One weak leak, one false positive |
| Victoria's Secret | 1 | False positive, equity analyst downgrade of the stock |
| Walmart, Target, Gap | 0 | Clean |

The real leak is Dollar General's fair-value note, which states that it values its senior notes using
"an index of the credit spreads for all North American investment grade companies by rating" and "the
estimated credit spread improvement that would result from an upgrade of one ratings classification".
That establishes that the issuer is investment grade and that management models an upgrade, without
naming any agency.

**Why this one matters more than its size suggests:** the sentence is simultaneously a rating leak and
a legitimate debt-valuation disclosure. Removing it removes real input. This is the case that shows
leak-stripping cannot be a regex pass over word lists.

The false positives matter too. An equity analyst downgrading a stock, the risk-free rate in an option
pricing model, and a pension fund holding investment grade corporate bonds all match the obvious
patterns and none of them leak anything. A stripper tuned on the vocabulary alone would delete
legitimate content in three of seven companies.

## Channel 3: coupon step-up clauses

**Confirmed present, but not a leak in this sample.** Kohl's discloses that downgrades triggered a 175
basis point cumulative coupon increase. Every step-up sentence found also names Moody's or S&P in the
same line, so line-based stripping removes them. Zero agency-free step-up disclosures were found
across the seven filings.

This should be re-tested on a larger sample rather than treated as settled, since a step-up clause need
not name an agency and the sample is small.

## Channel 4: credit agreement pricing grids

**Confirmed, and this is the serious one.**

Credit agreements are almost never attached to the 10-K. Of the seven companies, one had a
credit-related exhibit on the 10-K (Victoria's Secret, EX-10.18), and that document is a short
amendment containing no rating references and no grid. The full agreements are incorporated by
reference and live in other filings.

They land in 10-Q and 8-K exhibits. Target's case shows the 10-Q path in full; a Gap credit
agreement attached directly to an 8-K (exhibit 10.1, FY2026) was found later during the assumptions
review, confirming the 8-K path with a second issuer. Target's case in detail, and it is the worst
possible place for this project:

Target's 8-K of 9 October 2025 announces a new $1.0bn revolving facility and states that borrowings
bear interest at a rate plus "an applicable margin, which varies based on the type of loan and
Target's debt ratings". The same 8-K states that the full agreement "will be filed as an exhibit to
Target's Quarterly Report on Form 10-Q".

That exhibit is EX-10.20 on the 10-Q for the quarter ended 1 November 2025. It runs to 210,608
characters and contains 13 mentions of Moody's, 13 of S&P, 23 of "Debt Rating", and this grid:

| Level | Debt Rating | Applicable margin, Term SOFR |
|---|---|---|
| I | ≥ AA- (S&P) or Aa3 (Moody's) | 0.460% |
| II | A+ or A1 | 0.585% |
| III | A or A2 | 0.710% |
| IV | A- or A3 | 0.835% |
| V | ≤ BBB+ or Baa1 | 0.960% |

Target's actual rating is A2, which is Level III.

**What this leaks.** The agreement does not state which level is currently in effect, so it is not an
exact disclosure. But it bounds the issuer tightly: a lender writes a ladder around where the borrower
actually sits, so a five-tier grid spanning Aa3 to Baa1 establishes that the issuer is investment grade
and places it in roughly the A range. That is six notches out of twenty-one, and it settles the
investment-grade boundary, which is the economically decisive distinction.

**Why it matters for the design.** The experiment plan lists the 10-Q as the highest-value document to
add, on the grounds that it corrects a measured seasonal distortion in three of the four quantitative
subfactors. That recommendation stands for the 10-Q **body**. It does not stand for the 10-Q
**exhibits**.

Document ingestion therefore has to operate per document part, not per filing. "Add the 10-Q" is not a
safe instruction; "add the 10-Q financial statements and MD&A, exclude EX-10 exhibits" is.

## Channel 5: bond coupons and market-derived pricing

**Untested, and undecidable without a policy call.** A 10% coupon on senior secured notes communicates
speculative grade without naming a rating. Kohl's issued 10.000% senior secured notes in 2025 and
discloses the coupon in the ordinary course. This cannot be stripped without removing the debt
schedule, which is required input for three of the four quantitative subfactors.

There is a real question underneath it: market-derived information is something a Moody's analyst sees
and legitimately uses, so excluding it is not obviously correct either. The decision is whether market
pricing counts as input or as label leakage. It should be made explicitly and written into the baseline
specification rather than left to whatever the stripper happens to do.

## Consequences for the design

**Ingestion is per document part.** Filing-level allowlists are not safe. The unit is (filing type,
document part), and EX-10 exhibits are excluded by default.

**Stripping cannot be purely lexical.** The Dollar General case has the leak and the signal in one
sentence, and three of seven companies produce false positives on the obvious word lists. Either a
classifier decides per passage, or affected disclosures are dropped wholesale and the lost input is
accepted and recorded. Whichever is chosen, the stripper needs a regression test built from the
findings above, so that a future change cannot silently reopen a channel.

**Leak detection needs to be continuous, not a one-off.** The channels found here were found by looking
for them. The cheapest standing check is the memory probe already in the plan: if a stripped-document
run and a no-document run agree too often, something is leaking, whether or not anyone has named the
channel.

## What was not tested

Whether 10-Q bodies carry the same ratings table as 10-Ks. Expected yes, not verified.

Whether step-up clauses appear without agency names in a larger sample.

Whether other sectors' filings differ. The sample is entirely Retail and Apparel.

Proxy statements and earnings releases, which the document review flagged as useful inputs, have not
been checked for rating disclosures at all.
