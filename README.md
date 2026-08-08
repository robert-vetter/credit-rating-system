# credit-rating-system

Research project with Prof. Kay Giesecke (HPI / Stanford) and Xiaowei Ding, building a system that
reproduces what a credit rating analyst does: read a company's recent SEC filings, apply a
published rating methodology, and produce a credit rating with an evaluation harness that says how
well it did.

The first sector methodology in scope is Moody's Retail and Apparel.

## Status

Early. Reading the methodology and background material. Nothing built yet.

Two runs of the rating task done by hand so far, no system around them, just the methodology and one
10-K each. Walmart in notes/walmart-first-test.md, Kohl's in notes/kohls-second-test.md. Walmart came
out A1 against an actual Aa2, Kohl's came out Ba3 against an actual B2, so both are two notches off in
opposite directions. In both cases the outcome was decided by the four qualitative scores rather than
by anything computed. The scoring arithmetic itself is exact and is in notes/scorecard.py.

notes/what-else-feeds-a-rating.md goes through all eight subfactors and asks which of them a 10-K can
actually support. One can. It also covers the leakage problem, which is that companies disclose their
own credit ratings in the filing, so the label sits inside the input.

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
