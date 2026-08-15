# credit-rating-system

Research project with Prof. Kay Giesecke (HPI / Stanford) and Xiaowei Ding, building a system that
reproduces what a credit rating analyst does: read a company's recent SEC filings, apply a
published rating methodology, and produce a credit rating with an evaluation harness that says how
well it did.

The first sector methodology in scope is Moody's Retail and Apparel.

## Status

Early. Reading the methodology and background material. Nothing built yet.

Seven companies run through the scorecard so far. The first two, Walmart and Kohl's, were done inside a
session that already knew the answers. The other five were run blind: separate sessions with no
conversation history, no web access, and filings with the credit-ratings disclosure stripped out, plus
a control session that was asked for the same ratings from memory with no documents at all.

The headline result is in notes/blind-test.md. The memory-only control scores 0.40 notches mean
absolute error. The full document-based analysis scores 1.40. Guessing from a company name beats
working through the methodology and the filing, so on companies of this profile an accuracy number
from a pipeline like this cannot be interpreted. Ranking is a different story: Spearman correlation
against the actual ratings is 0.937, and the errors are compression rather than noise, with the
predictions squeezing a 12-notch spread into 8.

notes/what-else-feeds-a-rating.md goes through all eight subfactors and asks which of them a 10-K can
actually support. One can. It also covers the leakage problem, which is that companies disclose their
own credit ratings in the filing, so the label sits inside the input.

notes/blinding-minitest.md answers whether the model can be stopped from recognising the company it
is rating: mostly no. All seven companies were identified from seven numbers alone (dividends paid is
effectively a public identifier), and six of seven survived coarsening. Blinding is only a lever for
smaller issuers, verified per sample.

The files under notes/ were produced by Claude working to questions and test designs set by me, and
they are labelled as such. They are experiment logs, not hand-written notes.

docs/assumptions-review.md is the audit of every assumption behind all of the above: what is verified,
what was wrong and has been corrected (two claims), and what must be resolved before the main
experiment. Read it before citing numbers from the notes.

docs/leakage-audit.md is the first piece of that plan, done: five channels through which a rating can
reach the model, tested against real filings. The one that matters is that credit agreements map
Moody's symbols straight to interest margins and are attached to 10-Q exhibits, which is the document
the plan wanted to add next.

docs/experiment-plan.md is the current plan: what to freeze, what to measure, and in what order. The
headline constraint is that ratings are inert, so the baseline to beat is not zero, it is persistence
(carry the last known rating forward). Anything that does not beat that is not evidence of anything.
The primary experiment is update prediction: fundamentals plus the issuer's rating path in the input,
scored as lift over persistence on post-cutoff dates, which also neutralises most of what the model's
training memory could contribute. A blinding ladder (numbers only, blinded documents, named documents)
decomposes the rest.

Still waiting on the lab's initial dataset before sample construction and sector scope can be fixed.

## Layout

    methodologies/   Moody's rating methodologies, for reference
    notes/           experiment logs and reading notes
    docs/            design and architecture notes
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
