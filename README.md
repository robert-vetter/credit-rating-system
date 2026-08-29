# credit-rating-system

Research project with Prof. Kay Giesecke (HPI / Stanford) and Xiaowei Ding: build a system that
reproduces what a Moody's credit rating analyst does — read a company's SEC filings, apply a
published rating methodology, produce a rating — plus an evaluation harness that measures how
well it does. First sector: Moody's Retail and Apparel methodology (September 2025).

Working mode, stated openly: analysis, code and write-ups are produced by Claude (Opus 5)
working to questions, decisions and validations set by Robert Vetter. Notes carry attribution
headers saying what was verified against which source.

## Where things stand (29 August 2026)

**The evaluation harness is built, live-tested and frozen.** The chain: Moody's official 17g-7
rating histories parsed → 186 Retail/Apparel entities mapped to SEC filers by stable IDs (every
pair decided and logged, verified from both directions and via companies' own rating
disclosures) → 86 company folders with rating histories and complete SEC filing inventories →
3,646 quarterly observations 2012–2025, 218 of them with a rating change → a **gold set of 50
hand-validated observations** (frozen 2026-08-29, evidence chain per item) as the fixed
measuring stick → a runner that feeds redacted filings to the model and scores predictions
against label and persistence baseline → metrics, plus extraction scoring against XBRL at zero
model cost.

**System v0 exists and passed its smoke test** (two observations, ~$1.60): a single structured
API call proposes the scorecard inputs, the deterministic engine turns them into a rating.
Extraction accuracy in the smoke test: 14 of 14 comparable figures exact to the million against
XBRL. v0 is deliberately the naivest possible system; designing the real analyst architecture
is the next piece of work.

**Headline findings so far, each with a note behind it:**
- Ratings are inert: 94% of quarters are unchanged, so the baseline to beat is persistence
  (carry the last rating forward), never zero (docs/experiment-plan.md).
- Model memory beats naive document analysis on famous issuers (0.40 vs 1.40 notches MAE,
  notes/blind-test.md), so raw accuracy is uninterpretable; the primary experiment is update
  prediction as lift over persistence on changed quarters.
- Blinding does not work for covered issuers — identified from seven numbers alone
  (notes/blinding-minitest.md).
- Filings disclose their own ratings (docs/leakage-audit.md); inputs are redacted, and the same
  disclosure channel is reused productively to verify the mapping and the gold labels.
- The public rating file is embargoed 12 months, fully used — proven live by Nike's July 2026
  10-K disclosing a downgrade the file cannot see (notes/rating-history-file.md).

## Layout

    README.md            this map
    methodologies/       the Moody's methodology PDF (reference)
    system/              the system under test: scorecard.py (deterministic scoring engine),
                         analyst.py (the model call, v0), redact.py (rating-disclosure removal)
    evaluation/          the measuring apparatus; see evaluation/README.md for the full story:
                         mapping records, gold set + review sheet, pipeline/ (15 documented
                         steps), companies/ (generated per-company folders, gitignored)
    notes/               experiment logs, chronological; notes/README.md is the index
    docs/                experiment plan, leakage audit, assumptions review
    data/                raw and derived data (gitignored); data/README.md documents every
                         file, its source URL and download date

Every script states its purpose, inputs and outputs in its docstring and is listed with its
pipeline position in evaluation/README.md. Decisions (mapping, gold set) live in committed,
append-only records; everything generated is regenerable from data/ plus the scripts.

## Next: the analyst architecture

v0 is one monolithic call. The open design work: decompose per subfactor (peer tables for
Market Position, multi-year filings for Stability — input configurations already exist as
runner switches), decide where XBRL replaces model extraction, add the methodology's notching
factors, and fuse the scorecard and direct channels. Iteration happens on non-gold
observations; the frozen gold set is only for milestone claims.

## Open questions

- Sector strategy: methodology-faithful sector by sector (current mandate) versus
  sector-agnostic pure prediction — a project-scope decision for Giesecke/Ding.
- Whether peer *ratings* (not just peer figures) are admissible input, or leakage.
- Five scope calls: CVS, Samsonite, Good Sam, Amazon, Sherwin-Williams.
- The lab's dataset (Ding): strictly blocking only for the post-cutoff clean-window arm.
- What may be done with the Moody's documents beyond local reference (terms of use).
- Contamination probes (same observation, no documents) are designed but not yet run.

## Notes on the methodology

The retail scorecard has eight subfactors: four quantitative, computed from the accounts
(revenue, Debt/EBITDA, (EBITDA−capex)/interest, RCF/net debt, 55% weight) and four qualitative
(market characteristics, market position, revenue and earnings stability, financial policy,
45%). Aggregation is deterministic: weighted sum, then a lookup onto the 21-notch scale. The
scoring engine is therefore a plain function with tests; the model's job is to propose inputs,
not to produce the rating.
