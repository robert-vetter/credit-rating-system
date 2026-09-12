# Review of the cutoff simulation and next research step

*Written by Codex, directed by Robert Vetter, 2026-09-12. Verified against the two saved
Experiment 03 batches, cached SEC primary filings, current pipeline code, frozen candidate
records, and the local Moody's Retail and Apparel methodology, especially page 5 footnotes
2 and 3. Vendor cutoff and batch documentation rechecked on 2026-09-12. All computations
in this review were local; no model requests were made. Labels, mapping, gold set, original
prompts and paid-run artifacts were not changed. Nothing was committed or sent.*

## Assessment of the work so far

The strongest asset is the reusable evaluation apparatus: the issuer-to-filer join, the
rating histories, the filing inventory, persistence comparisons, and saved requests. These
make it possible to investigate a mistake without buying another model response. Experiment
01 demonstrated the need for persistence and memory controls. Experiment 02 motivated the
relative-to-history design, but is historical evidence, with a disclosed contaminated case.
Experiment 03 implements a useful post-cutoff pilot. It is not yet a certified clean benchmark.

The earlier claim that extraction is solved is unsupported. Current XBRL fundamentals were
part of the model input, and the comparison checked agreement with XBRL. That is useful
consistency evidence, not an independent test of reading figures from filings. The comparison
also excludes the working-capital calculation and does not validate every debt adjustment.
The original 46/47 statistic is not a demonstration that all ten input fields are correct.

Robert stopped the remaining 13 observations on 2026-09-12 for cost reasons. Experiment 03
is closed at seven successful observations. There is no pending top-up or paid completion.

## What the saved evidence establishes

The offline audit replays all 18 document-request packages across the original batch and
the two reruns exactly from their cached primary filings and the redactor. The 52 groups
of mechanical checks pass: model/request configuration, allowed forms and filing dates,
document replay, accession metadata, dated rating events and label filing boundaries.
Hashes and reconstructed removed lines are in
`experiments/03-oos-values-first/runs/offline-review-2026-09-12/audit.json`.

This verifies these specific controls. It does not prove absence of semantic leakage or
training contamination. The source files were not hashed at original submission, so the
hashes establish the evidence examined today, not an independently timestamped archive.

Anthropic's [Opus 4.6 documentation](https://platform.claude.com/docs/en/models/opus-4-6/overview)
still lists an August 2025 training-data cutoff, consistent with the saved evidence note.
That is a vendor-reported boundary. A failed memory probe does not establish that the model
could not recall the answer under another prompt.

The experiment asks for a rating at August 29, 2026 using information available up to that
date. This is retrospective reconstruction of a post-cutoff rating state. It is not a
forecast of a future rating action. Nike's July 2026 filing was published after its November
2025 downgrade. That is admissible for reconstruction at August 2026; it would be look-ahead
for a claim of predicting the November downgrade in advance.

## Findings and repairs

| Finding | Evidence and consequence | Status |
|---|---|---|
| Negative EBITDA was rewarded | Qurate's saved EBITDA is -1,700m. Debt/EBITDA of -5.05 received 0.5, the best score. Methodology page 5 footnote 2 requires 20.5. | Fixed in `system/scorecard.py`; saved predictions preserved. |
| Net-cash ratio sign was mishandled | Page 5 footnote 3 uses the signs of net debt and RCF, not just their ratio. | Fixed. Non-finite values and undefined zero-denominator cases now fail explicitly. Zero-case methodology interpretation remains open. |
| Rounding could change a rating | The collector rounded the aggregate before the outcome lookup. | Lookup now uses full precision; rounding is only for the displayed aggregate. |
| Qurate's label does not establish the August rating | Label evidence was filed November 5, 2025, 297 days before as-of. Inputs include May 15 and August 4, 2026 10-Qs describing Chapter 11, filed April 16. The model's Ca rationale explicitly discusses bankruptcy. | Label unchanged. Results without Qurate are mandatory sensitivity evidence. Current rating and legal-entity alignment need Robert's review. |
| Rating types and entities are mixed | Candidate labels include issuer/CFR and senior debt ratings. Qurate's Caa3 evidence identifies LI LLC's CFR, while the input is consolidated QVC Group. Its history mixes entity and instrument events. | Not silently remapped. A target contract must specify rated entity, OI, rating type and seniority for label, persistence and prompt. |
| Post-boundary action dates were not enforced | The runner checks the filing date, not the action date. An interval starting August 28 and ending after September 30 can include September. | Corrected specification claim. Nike's December 30, 2025 10-Q explicitly dates its downgrade to November; Qurate's November 5 filing explicitly says October. General automatic action-window validation remains required. |
| Probe execution was not staged | Original probes and document requests share one batch. A list order is not proof of processing order. Reruns correctly had earlier probes, but the collector did not join them and mislabeled Nike's prior recall. | Offline audit joins probes by ID across batches. Original Nike probe recalled A1. Future execution must complete and review probes before submitting documents. Paid execution is closed now. |
| The full methodology rubric was absent | The saved prompt names the September 2025 methodology and gives short factor descriptions. It does not include the qualitative category-by-category rubric or the full financial adjustment definitions. | Original prompts preserved. No claim that the model received or followed the full methodology. A dated, supplied rubric is required for a future variant. |
| Inputs and benchmark were not independent for extraction | Current issuer XBRL and peer figures were provided before the model supplied its figures. | Reclassified as input/output consistency. An independent extraction test must withhold reference values from its input. |
| Per-fact provenance was missing | Original audits contain pack text and a quarterly-row count, not the asserted source dates/tags for each fact. Nike, Qurate and Walmart had zero quarterly rows. | Future packs now print filing dates and log annual, quarterly and peer sources. Historical provenance remains incomplete; today's data cannot replace the old input snapshot. |
| Peer figures could mix periods and overlap debt | The builder selected each field's latest year independently and summed overlapping combined debt tags. Old annual values from inactive companies were also displayed without dates. | Peer rows now use one revenue fiscal-year end, matching-period facts, shared debt-overlap rules and visible source dates. Peer membership and maximum age still need a stated research policy. |
| One XBRL source date was impossible | Walmart cash record: period end 2012-12-31, filed 2012-03-27. | Excluded from usable facts and retained in invalid-date audit logs. Raw cache unchanged. |
| Extraction check filtered only revenue by filing date | Other fields from the same fiscal year could have been filed after the requested date. | Every compared field now obeys the filing-date ceiling. |
| Gold labels entered calibration | Holding a company out of its own prediction does not stop its gold observations training other folds. Training-fold calibrated features also depended on outer test labels. | Gold observations excluded before development analysis; fitting and threshold functions reject gold rows; threshold training features recomputed within the outer training set. Earlier gold exposure cannot be undone. |
| The paid cap could be reused | The per-submission constants are not a cumulative spending ledger. The miniature preflight itself makes a paid call. | Submit, rerun and paid preflight now stop before client creation. Reopening needs a new explicit decision and a cumulative, request-complete cost guard. |

The redactor remains a heuristic. A lexical scan and a request without tools establish
limited properties; they do not establish the absence of all rating information. The
[batch documentation](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
describes asynchronous processing. Future protocol records need actual probe completion and
review events, not an assumption based on the order of requests in a list.

## Results after replay, with the original labels retained

The saved execution configuration is consistent with a bounded API experiment: independent
single-user requests, no tools, no cache directives, adaptive thinking, high effort for
document analysis and low effort for probes. The initial document ceiling was 9,000 tokens;
the two reruns used 24,000. A miniature parameter test did not validate output headroom on
full filings. The audit records the current Python/package versions separately from the
original-run evidence; a complete original environment lock was not captured.

The prompt has useful structure: common units, an annual reporting period, explicit
quantitative fields, relative qualitative grades and a separate overall judgement. But its
schema requires every figure to be a number. It cannot honestly represent an unavailable
input. Rationale fields are free text without source IDs or mechanically checkable quote
spans. A future variant should allow missing values with reasons, supply the full rubric,
record provenance per factor, and distinguish reported facts from forecasts and analyst
judgement. Those changes are proposed, not retrospectively applied to the saved experiment.

| Channel | Exact, n=7 | Within one | MAE | Changed MAE, n=2 | Unchanged MAE, n=5 | False alarms, n=5 |
|---|---|---|---|---|---|---|
| Recorded scorecard | 3/7 | 5/7 | 1.57 | 2.00 | 1.40 | 3/5 |
| Corrected scorecard arithmetic | 3/7 | 6/7 | 1.14 | 0.50 | 1.40 | 3/5 |
| Recorded model judgement | 4/7 | 6/7 | 0.57 | 1.00 | 0.40 | 1/5 |
| Persistence | 5/7 | 6/7 | 0.43 | 1.50 | 0.00 | 0/5 |

Only Qurate's scorecard outcome changes, from B2 to Caa2. Its unchanged inputs and the
published negative-ratio rule produce this correction. It is not a newly measured model
prediction. The old explanation that the B2 error was solely a limitation of scorecard
aggregation was wrong: a scoring implementation defect accounted for three notches.

Without Qurate, there are six observations and one changed case. Scorecard exact accuracy
is 3/6 and MAE 1.17; judgement is 4/6 and 0.50; persistence is 5/6 and 0.17. On the single
changed case, scorecard MAE is 0, judgement 1 and persistence 1. The unchanged subset is the
same five issuers shown above. This sensitivity does not certify the remaining labels.

Descriptive 95% Wilson intervals for exact accuracy on seven observations are 15.8%-74.9%
for the scorecard, 25.0%-84.2% for judgement, and 35.9%-91.8% for persistence. Paired error
bootstrap intervals and all splits are in the offline audit. These intervals do not fix
selection bias: the sample consists of five initial successes and two selectively rerun
changed cases. There were 16 distinct scheduled issuers, 18 document attempts and 11 failed
attempts. Four confirmed issuers were never scheduled. Missing outputs must stay visible.

## Calibration rechecked without model calls

The corrected development run excludes all 50 gold observations before fitting or selection.
It covers 1,665 observations, including 78 changed and 1,587 unchanged. Its files are under
`evaluation/runs/calibration-integrity-2026-09-12/`. The original study files are retained.

| Channel | Exact, all | MAE, all | MAE, changed | MAE, unchanged |
|---|---|---|---|---|
| Raw quantitative scorecard | 18.0% | 1.919 | 1.744 | 1.928 |
| Pooled calibration | 24.3% | 1.492 | 1.385 | 1.497 |
| Persistence | 95.3% | 0.053 | 1.128 | 0.000 |

All four threshold-selected change detectors still choose never to signal a change in all
five folds. Each has the same 0.053 overall MAE and 1.128 changed-case MAE as persistence,
zero correct change directions out of 78, and zero false alarms out of 1,587.

This supports using calibration as a candidate level-estimation module. It does not show
that calibrated levels should replace persistence. It does not prove that numerical data
cannot detect changes: only these annual-data signals and this selection criterion were
tested. Company-held-out folds also use later calendar years, so this remains retrospective
cross-company validation, not a historical simulation of a model trained only before t.
The association with lease-accounting eras is descriptive, not proof of causality.

## Proposed next step: an evidence-backed analyst architecture

The useful next deliverable for Giesecke and Ding is an architecture whose modules follow
from the experiments, together with a candid pilot result and this audit. The proposal stays
within Retail and Apparel and does not require another paid batch.

| Module | Contract and reason |
|---|---|
| Observation and source boundary | One target entity/rating type; as-of date and forecast horizon separate; filing date and economic period separate; unresolved or stale labels explicitly unverified. |
| Evidence ledger | Every value and narrative claim carries accession, filing date, period, units, source span, transformation, and verification state. Retain raw, redacted and assembled-input hashes. |
| Quantitative engine | Use XBRL where reliable, normalize periods and non-overlapping debt components, keep missing values explicit. Add text extraction only for missing facts or adjustments. |
| Qualitative and event analysis | Supply the actual dated rubric. Require a grade, exact source quote, adverse and supporting evidence, uncertainty and the reason for moving from the prior state. Validate citations in code. |
| Scoring and judgement | Apply tested methodology arithmetic. Keep scorecard, persistence and analyst judgement separate. Route distress and source conflicts for review; do not choose whichever channel happened to win the two known changes. |
| Evaluation | Freeze input/configuration; stage probes; score coverage, failures, changed/unchanged splits and persistence. Fit development models on non-gold data with time-aware splits for any forecast claim. |

The next free implementation I recommend is a narrow version of the evidence ledger plus
a quarterly/TTM quantitative baseline. Start with synthetic date, restatement, missing-data
and overlapping-debt cases. Then use non-gold issuers. For cumulative cash flows, derive a
quarter only from compatible YTD periods; a TTM flow can use latest FY plus current YTD
minus prior comparable YTD, with every component public by t. Never treat a missing quarter
as zero. Do not fit a final policy until the target and evaluation split are fixed.

Two alternatives are useful but secondary. A factor-by-factor methodology specification
and citation validator would directly strengthen the analyst prompts. Additional labels from
the lab would strengthen later evaluation, but changing the labels or sample remains Robert's
decision. Buying 13 more responses does not resolve the defects identified here.

For the lab update, the defensible story is: the evaluation apparatus is built; a small
post-cutoff pilot is recorded with persistence; the audit found and repaired a methodology
implementation bug; the free calibration finding survived stricter validation; and the
next architecture addresses source evidence, events and update decisions. Do not claim
superior predictive accuracy, solved extraction, or a bulletproof simulation. No message
has been sent.

## Verification and limits

Run `python3 experiments/03-oos-values-first/audit_saved_run.py` for offline replay and
`python3 -m unittest discover -s experiments/03-oos-values-first -p 'test_*.py' -v` for the
integrity regressions. All 10 regressions passed. All 16 currently scheduled packages also
built locally with network connections disabled; their logged annual, quarterly and peer
dates obeyed the ceiling and peer fields used matching fiscal periods. The 17 protected
files hashed before the review were unchanged afterwards. The review fixes specified failure
modes; it does not certify the
entire repository. Full methodology adjustment coverage, independent label verification,
semantic redaction review, historical entity naming, raw XBRL versioning and a future
execution protocol remain explicit work items. The original gold set has been exposed in
earlier analyses; future exclusion does not restore it to a never-seen holdout.
