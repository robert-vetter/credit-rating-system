# credit-rating-system

Research project with Prof. Kay Giesecke (HPI / Stanford) and Xiaowei Ding, building a system that
reproduces what a credit rating analyst does: read a company's recent SEC filings, apply a
published rating methodology, and produce a credit rating with an evaluation harness that says how
well it did.

The first sector methodology in scope is Moody's Retail and Apparel.

## Status

Early. Reading the methodology and background material. Nothing built yet.

Waiting on the lab's initial dataset and the rest of the reading material before sketching the
architecture.

## Layout

    methodologies/   Moody's rating methodologies, for reference
    notes/           reading notes
    docs/            design and architecture notes, once there are any
    data/            filings and datasets, not tracked in git

## Open questions

- Size and shape of the initial dataset: how many companies, which years, which sectors.
- Which rating is the target: senior unsecured, or the corporate family rating.
- Whether the sector methodologies share the same scoring mechanics, so that the scorecard engine
  can be generic with one configuration per sector.
- How amendments and restatements are handled, so that evaluation stays point-in-time.
- What may be done with the Moody's documents beyond keeping them here for reference.

## Notes on the methodology

The retail scorecard has eight subfactors. Four are quantitative and computed from the accounts
(revenue, Debt/EBITDA, (EBITDA − capex)/interest, RCF/net debt) and carry 55% of the weight. Four
are qualitative and scored from narrative sections of the filing (market characteristics, market
position, revenue and earnings stability, financial policy) and carry the other 45%.

Once the subfactor scores are fixed, the aggregation is deterministic: weighted sum, then a lookup
table onto the rating scale. So the scoring engine can be a plain function with tests, and the
model's job is to propose inputs rather than to produce a rating.
