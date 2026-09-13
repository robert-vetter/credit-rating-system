# Analyst architecture, proposal v0.2 (superseded)

*Superseded on 2026-09-13 by docs/architecture-codex-2026-09-13.md, written from the evidence
of all four experiments. Kept as history. Codex's audit corrected three claims made here: the
scorecard-indicated outcome is an input to rating analysis, not a deterministic assignment
rule; the "four notches too high" anecdote used defective arithmetic and an unresolved
target; and "annual numbers cannot time changes" was not shown, only that four tested
signals and their selection rule chose persistence. The 8-K evidence step and the "move only
if both scorecards move" rule were never authorized or validated.*

*Claude (Fable 5.1), directed by Robert Vetter, 2026-09-12. Page numbers refer to the Moody's
Retail and Apparel methodology of 12 September 2025. Every "why" is a result measured in this
repository (experiments/, notes/scorecard-calibration.md, docs/oos-integrity-review.md).*

## The idea

Moody's assigns a rating by a fixed arithmetic over eight scorecard subfactors, then adjusts
for considerations outside the scorecard, by committee (Exhibit 1, page 2). The system keeps
the arithmetic in tested code and uses the model only where judgement is needed: reading the
filings, grading the qualitative factors, spotting events, and deciding whether the current
rating still holds. Ratings change in 6% of quarters, so the output is an action relative to
the current rating, not a level from scratch.

## The pipeline

| Step | What it does | Why |
|---|---|---|
| 1 Target | Fix the rated entity, the rating type (corporate family rating if speculative grade, senior unsecured if investment grade, page 14), the as-of date and the information boundary | Current labels mix rating types |
| 2 Evidence | Collect 10-K, 10-Qs, 8-K items and XBRL filed before the as-of date; redact rating disclosures; date and hash every fact and quote | Filings disclose their own ratings; the pilot's inputs had no per-fact provenance |
| 3 Numbers | The ten scorecard inputs from XBRL, annual and trailing twelve months, with Moody's standard adjustments itemised (leases, pensions, hybrids); missing values stay explicit; the model reads only what XBRL lacks, with reference figures withheld | Numbers alone place an issuer within one notch 61% of the time; an untested scoring rule cost three notches on one issuer |
| 4 Forecast | Expected inputs over the next 12 to 18 months, with intervals | Moody's rates on expectations (page 6); realised figures give dense, checkable supervision, where the lab's EDGAR-Forecast work fits |
| 5 Qualitative | Grade the four qualitative subfactors against the rubric text of Exhibit 2, relative to the grade the current rating implies; every grade cites quotes that code verifies against the source | Grading relative to the issuer's own history is the only change that moved the model off persistence in the right direction (Experiments 02 and 03) |
| 6 Other considerations | Flags with evidence: liquidity, seasonality and peak debt, financial controls, event risk, distress (going concern, Chapter 11), parental support (pages 9 to 12) | Distress is not in the scorecard; the scorecard put a bankrupt issuer four notches too high |
| 7 Score | Scorecard-indicated outcome (Exhibits 3 to 5) on historical and forecast inputs; a calibrated numbers-only level as a diagnostic | The raw scorecard sits a median one notch above assigned ratings; calibration cuts the level error from 1.92 to 1.49 notches |
| 8 Decide | Start from the current rating; move only if the scorecard moves at least one notch on both historical and forecast inputs, or step 6 overrides; write the rationale with citations; flag disagreement between scorecard and judgement | Annual numbers cannot time changes; the timing lives in steps 4 to 6. On Nike the scorecard moved and the judgement did not |
| 9 Evaluate | Persistence baseline, changed and unchanged split, memory probe per issuer, cutoff boundary, cost cap | Persistence wins every raw cross-section; memory is confidently wrong off famous names |

## What exists and what comes first

Steps 7 and 9 exist and are tested; steps 1 and 3 exist in part (annual figures, no
adjustments). Build order, free work first: the evidence ledger and trailing-twelve-month
numbers with the lease adjustment; then qualitative grading with the rubric and verified
quotes, the first paid step at about $0.50 per issuer; then the distress and event flags and
the decision rule; forecasting together with the lab's EDGAR-Forecast work. Each step is
evaluated by switching it off against the numbers-only floor.

## Decisions needed

1. Post-cutoff labels from the lab's data, which turns 7 issuers into a few hundred.
2. Rating type: corporate family rating for speculative grade, senior unsecured for
   investment grade?
3. Peer ratings as input: admissible, or leakage?
4. Horizon: the rating at the as-of date, as now, or one year ahead?
