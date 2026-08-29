# Assumptions review

*Written by Claude (Opus 5), directed by Robert Vetter, August 2026. Robert asked for a full audit of
every assumption behind the work so far, before committing to the large experiment. This document is
the register: every load-bearing claim, its verification status, and what breaks if it is wrong. Two
claims in earlier notes were found to be wrong and have been corrected in place; the corrections are
listed here.*

Status codes: **verified** (checked against a primary source), **corrected** (was wrong, now fixed),
**unverified, blocking** (must be resolved before the main experiment), **unverified, tolerable**
(should be resolved, does not block), **decision** (not a fact question; needs an explicit call).

## The goal, restated once

Build a system that does what a Moody's analyst does: read a company's SEC filings, apply the
published sector methodology, produce a rating, with an evaluation harness that says how well it did.
The near-term deliverable is a baseline experiment whose numbers survive review, and an architecture
that follows from measured facts rather than guesses. Every experiment below exists to answer one
architecture question; the mapping is at the end.

## Finding 1, the biggest hole: ground truth for the clean window does not exist yet

The experiment plan assumes we can get correct Moody's ratings, with dates, for issuers observed
after the model cutoff. Where from?

**Verified:** SEC Rule 17g-7(b) requires every rating agency to publish its full rating history in
machine-readable XBRL, free, on its own website. This is the ideal ground-truth source: every action,
dated, machine-readable, legally mandated. **But the rule allows a delay of up to 12 months for
issuer-paid ratings** (24 for others). The clean window is, by construction, the most recent months
after the model cutoff. Those are exactly the months the public file is allowed to be missing.

Consequence: the public XBRL history works as ground truth for **historical** evaluation (anything
older than ~12 months) and for the persistence baseline, but **cannot be assumed to cover the
post-cutoff window**. For the clean window the label must come from the lab's dataset, a commercial
feed, Moody's issuer pages, or company disclosures. Each has problems: the lab dataset is still
unspecified, commercial feeds cost money, Moody's website has licensing terms we have not read (this
is the same open question as the methodology PDFs), and company disclosures are stale and ambiguous
(next finding).

**Update, measured (notes/rating-history-file.md): Moody's uses the full 12 months.** The file set
dated 11 August 2026 ends with actions from August 2025. The worst case is the actual case: the
public file fully powers the historical arm and provides nothing for the post-cutoff clean window,
which makes the lab dataset strictly blocking for that arm.

## Finding 2: our blind-test labels have two defects the write-up did not state

Both are as-of-date and which-rating problems, and both must be fixed in the next run's design. The
blind-test conclusion (memory beats analysis by 3.5x) is not overturned, but the numbers carry more
uncertainty than the write-up conveys, and this should be said to the lab rather than discovered by
them.

**Defect 1, timestamps.** The labels were taken from ratings disclosures inside the filings, which
state the rating as of the fiscal year end or filing date (January to March 2026, mixed). The memory
control recalls the rating as of the model's cutoff (May 2026). If any of the five ratings moved
between filing and cutoff, the memory control was graded against a stale label. With n=5, one such
case moves the MAE by 0.2 notches. A search found no post-filing action for the one case checked
(Gap), but this was not verified for all five. Every future sample needs an explicit triple:
observation date, label as of that date, documents filed before that date. No mixed dates.

**Defect 2, which rating.** The methodology targets senior unsecured for investment grade and the
corporate family rating for speculative grade. The filings do not always disclose the CFR. Macy's
discloses "long-term debt: Ba1"; whether that is the CFR or an instrument rating is not determinable
from the filing, and for a company whose notes sit at a subsidiary with structural subordination the
two can differ by a notch. **Update: resolved.** The 17g-7 file shows Macy's CFR at Ba1 since
February 2022, matching the filing's disclosure, so the exact hit stands (notes/rating-history-file.md). Walmart (Aa2 senior unsecured, IG), Kohl's (B2 corporate), VSCO (Ba3 corporate), DG
(Baa3), Gap (Ba2 corporate) are consistent with the rule; Target (A2 long-term debt, IG) is fine.

## Finding 3, corrected: Moody's adjustment definitions ARE published

Three of our notes claimed Moody's definitions for FFO and its balance-sheet adjustments are
unpublished, making the restatement layer "a guess at somebody else's definition." **That is wrong.**
Moody's publishes a cross-sector methodology, "Financial Statement Adjustments in the Analysis of
Non-Financial Corporations," on the same methodology library page Ding linked, covering leases,
pensions, hybrids, securitisations and the rest. There is also a published basic-definitions guide
for the credit statistics.

This changes two things. For credibility: the wrong claim has been corrected in all three notes
before anyone cites it. For architecture: the restatement layer is not a judgment black box, it is a
published specification plus judgment at the edges, which means it can be built as explicit rules
with tests, exactly like the scorecard engine. The adjustments document should be pulled into
`methodologies/` next to the sector methodology.

## Finding 4, design flaw fixed: the cutoff gradient was confounded

The plan proposed running the same samples across models with different cutoffs and reading
degradation as memorisation. As written, that is confounded: Opus 4.5 differs from Opus 5 in
capability, not just cutoff, so accuracy differences across models mix the two.

Fix, now in the plan: **within-model contrast**. For each model, compare its accuracy on samples
observed before its own cutoff against samples observed after it, holding everything else fixed. The
drop at the boundary is that model's memorisation estimate, with capability controlled because the
model is its own control. Comparing the size of the drop across models is then a clean second read.
This requires samples spanning observation dates on both sides of each cutoff, which is another
requirement on the dataset (historical depth), not just on the recent window.

## Finding 5, decision needed: which target are we predicting?

Our system reproduces the **scorecard-indicated outcome**: deterministic function of eight inputs.
Moody's assigns the final rating after committee judgment, notching, and the "other considerations"
the methodology lists. Its own Limitations section says the two align loosely at the scale extremes.
Evaluating our output against assigned ratings therefore conflates two errors: our input errors, and
the SIO-to-assigned gap that exists even with perfect inputs.

The assigned rating is the observable and should stay the primary label. But the report must say the
measured error contains an irreducible component, and where possible we should decompose it. Moody's
rating-action announcements sometimes state the scorecard-indicated outcome per issuer; whether
systematically is **unverified** and worth an afternoon, because even a few dozen published SIOs would
let us measure the gap directly instead of estimating it.

The compression finding (predictions span 8 notches where truth spans 12) is partly this instrument
property, as already noted; the decomposition would tell us how much.

## Register of remaining assumptions

| # | Claim | Status | If wrong |
|---|---|---|---|
| 1 | Scorecard mechanics (weights, bands, endpoints, mapping) as coded in scorecard.py | verified against the methodology PDF | Engine wrong, everything wrong. Re-checked line by line; arithmetic re-added by hand for both companies |
| 2 | Retrieval is impossible when no tools are declared on the API request | verified, API docs | Blind runs contaminated by search. Next runs use the raw API, not agent sessions |
| 3 | Sampling params removed on Opus 5/4.8/4.7, present on 4.5 and older | verified, API docs | Replicate design unnecessary or model choice changes |
| 4 | Model cutoffs (Opus 5: May 2026; Opus 4.8/Sonnet 5: Jan 2026; Opus 4.5/4.6: Aug 2025; Sonnet 4.5: Jul 2025) | verified, models overview page | Clean-window arithmetic shifts |
| 5 | Batch API halves cost; prompt caching reads at ~0.1x | verified individually; **their combination is unverified** (cache hits inside a concurrent batch are plausibly best-effort) | Budget estimate off by up to ~2x. Verify empirically on a 10-request batch before budgeting |
| 6 | Structured outputs constrain responses to a JSON schema | verified, API docs. Caveat: incompatible with the citations API feature, so quote spans must be schema fields, which means quotes are model-asserted and must be validated by string match against the source document | Silent fake citations if the validation step is skipped |
| 7 | Blind-test stripping left zero rating tokens in the five filings | verified mechanically (zero agency mentions, zero symbols) | Blind results contaminated. Note: verification was lexical; Finding 2 limits are separate |
| 8 | Pricing grids sit in credit agreements attached to 10-Q and 8-K exhibits, mapping rating symbols to margins | verified on Target's EX-10.20 (grid read directly); Gap has a credit agreement as an 8-K exhibit, found during this review, grid unread | Per-part ingestion is unnecessary. It is necessary |
| 9 | Coupon step-ups always co-occur with agency names | verified only on n=7 | Stripper misses agency-free step-ups at scale. Re-test on larger sample before trusting |
| 10 | Retail and Apparel covers 150-250 Moody's issuers | **measured and hand-curated** (notes/rating-history-file.md): after the manual scope pass, group dedupe and filing verification, 57 groups are in scope, actively rated and current filers (23 IG, 34 spec); 9 more usable historically only. A few hundred samples requires issuer-dates or added sectors | Was the basis for sample-size hopes; now a curated frame |
| 11 | Kohl's filing contains no usable gross interest anywhere | **overclaimed, softened** in the notes: the face shows only net, but supplemental disclosures (cash interest paid, lease interest split) permit partial reconstruction | Extraction spec needs per-field fallback chains, which it now says |
| 12 | Lab dataset contents (firms, years, sectors, which rating, action dates) | unverified, **blocking** for sample construction | Cannot fix sample or sector scope. Waiting on Ding |
| 13 | Sector methodologies share scoring mechanics | unverified, tolerable (one afternoon, two PDFs) | Multi-sector expansion costs a rewrite instead of config |
| 14 | Moody's website/PDF licensing permits our use | unverified, open since day one | Legal constraint on data sourcing; ask the lab, it is their relationship |
| 15 | Market-derived signals (bond coupons) count as input or leakage | **decision**, owner: Robert with the lab | Baseline spec ambiguous; either answer is defensible, silence is not |
| 16 | Moody's 17g-7(b) rating history is freely downloadable | **done**: downloaded via Robert's free account and parsed (notes/rating-history-file.md). 21,383 obligors, 106,590 actions, 8,146 corporates. Publication delay measured at the full 12 months; label pipeline requires joining obligor and issuer sets; all seven study labels verified | Historical arm fully powered; clean-window labels still need the lab dataset |
| 17 | Blinding can hide issuer identity from the model | **measured, mostly no** (notes/blinding-minitest.md): 7 of 7 identified from exact numbers, 6 of 7 from coarsened inputs; works only in crowded strata with ordinary ratios | Rung 2 of the ladder restricted to smaller issuers with per-sample verification; Task B carries contamination control for covered issuers |

## What was corrected in place today

The unpublished-definitions claim in `walmart-first-test.md`, `kohls-second-test.md` and
`what-else-feeds-a-rating.md` (Finding 3). The absolute no-gross-interest claim in two notes
(register #11). The cutoff-gradient design in `experiment-plan.md` (Finding 4). The plan's
ground-truth section (Finding 1) and label rules (Finding 2).

## Experiments to architecture: the mapping this all serves

Each experiment exists to fix one module decision. If an experiment does not decide anything in this
table, it is cut.

| Architecture question | Deciding experiment |
|---|---|
| Is extraction structured (XBRL-first) or text-first? | Extraction ablation: XBRL-tagged quant values vs text extraction, error rate per field |
| Does the restatement layer earn its place? | Ablation with/without published Moody's adjustments applied |
| Is the scoring engine model or code? | Decided: code. Arithmetic contributed zero errors in seven runs; the engine is forty tested lines |
| Do qualitative scores need retrieval over narrative sections plus citation validation? | Citation-forced runs: do validated quote spans change scores vs free assertion |
| Does the stability subfactor need a peer pipeline? | Peer-set ablation on the stability score |
| Does the system need the 10-Q body? | Seasonality ablation, body only, exhibits excluded per the leakage audit |
| Is a calibration layer needed and fittable? | Monotone recalibration on held-out split; decided by whether compression persists and corrects |
| Which model family can be evaluated at all? | Within-model cutoff contrast (Finding 4); decides whether frontier models are usable for evaluation or only for production |
| What must the evaluation harness store? | Decided by Findings 1 and 2: point-in-time triples (observation date, label source and date, document accessions), plus standing memory probe and persistence baseline |

The end state this feeds: extraction, restatement, qualitative scoring with citations, deterministic
scorecard, calibration, evaluation harness. Six candidate modules; the experiments decide which four
to six survive and in what form. That is the architecture answer the lab asked for, derived from
measurements instead of taste.
