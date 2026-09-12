# Experiment 03 results: outstanding-rating pilot after the model cutoff

*Updated by Codex, directed by Robert Vetter, 2026-09-12. Model runs by Robert and Claude
on 2026-09-10. Verified against the two saved batches, offline replay and methodology
page 5 footnotes. The correction uses saved model outputs; no new model calls were made.*

## Result and interpretation

The model was Claude Opus 4.6, with a vendor-reported August 2025 training-data cutoff.
The target was the outstanding rating at August 29, 2026. See the [full specification](README.md)
for inputs, prompts, parameters, labels and control limitations.

There are seven completed cases, compared with the latest accepted company disclosure.
One label, Qurate, is materially stale relative to its input documents. These are pilot
results, not a certified outstanding-rating benchmark or evidence of superior predictive
accuracy. Unchanged issuers are included; persistence is scored on the same labels.

| Channel | Exact accuracy | Within one notch | MAE, notches |
|---|---|---|---|
| Scorecard, corrected arithmetic | 3/7 (43%) | 6/7 (86%) | 1.14 |
| Model judgement after extraction | 4/7 (57%) | 6/7 (86%) | 0.57 |
| Persistence | 5/7 (71%) | 6/7 (86%) | 0.43 |
| Original scorecard, before correction | 3/7 (43%) | 5/7 (71%) | 1.57 |

The correction changes Qurate's scorecard rating from B2 to Caa2. Negative Debt/EBITDA had
received the best leverage score; methodology page 5 footnote 2 requires the worst. Its
aggregate changes from the saved rounded 15.346 to 18.346 under corrected arithmetic.
No label or model output was modified. The earlier explanation that this discrepancy was
solely an aggregation limitation was incorrect.

## Per observation

| ID | Company | Accepted disclosure label | Persistence | Corrected scorecard | Model judgement |
|---|---|---|---|---|---|
| X12 | Nike | A2 | A1 | A2 | A1 |
| X14 | Qurate/QVC | Caa3 | Caa1 | Caa2 | Ca |
| X15 | Signet | Ba3 | Ba3 | Baa1 | Ba1 |
| X16 | Target | A2 | A2 | A2 | A2 |
| X17 | Tractor Supply | Baa1 | Baa1 | Baa2 | Baa1 |
| X19 | Victoria's Secret | Ba3 | Ba3 | Ba3 | Ba3 |
| X20 | Walmart | Aa2 | Aa2 | Aa3 | Aa2 |

Qurate's accepted Caa3 evidence identifies LI LLC's corporate family rating in a filing
of November 5, 2025. Its input covers consolidated QVC Group and contains 2026 filings
reporting April bankruptcy. The label is 297 days old by the observation date, measured
from its evidence filing date. Its outstanding rating and target-entity alignment need
verification. The model's Ca rationale explicitly uses the bankruptcy information; this
must not be described as forecasting the bankruptcy or the earlier downgrade.

## Changed and unchanged diagnostics

Here, changed means the accepted disclosure label differs from the archive-based
persistence rating. It does not redefine the sample as rating actions.

| Channel | Changed exact, n=2 | Changed MAE | Correct direction, n=2 | Unchanged exact, n=5 | Unchanged MAE | False alarms, n=5 |
|---|---|---|---|---|---|---|
| Corrected scorecard | 1/2 | 0.50 | 2/2 | 2/5 | 1.40 | 3/5 |
| Model judgement | 0/2 | 1.00 | 1/2 | 4/5 | 0.40 | 1/5 |
| Persistence | 0/2 | 1.50 | 0/2 | 5/5 | 0.00 | 0/5 |
| Original scorecard | 1/2 | 2.00 | 1/2 | 2/5 | 1.40 | 3/5 |

Two changed cases, including Qurate's unresolved label, cannot establish change-detection
skill. Nike illustrates a disagreement worth investigating: its qualitative deterioration
translated into A2 through the scorecard, while the model's overall judgement stayed at A1.
That is a case observation, not an independently established causal explanation.

## Sensitivity excluding Qurate

| Channel, n=6 | Exact accuracy | Within one notch | MAE |
|---|---|---|---|
| Scorecard | 3/6 (50%) | 5/6 (83%) | 1.17 |
| Model judgement | 4/6 (67%) | 5/6 (83%) | 0.50 |
| Persistence | 5/6 (83%) | 6/6 (100%) | 0.17 |

Nike is the single changed case in this sensitivity. Its scorecard, judgement and
persistence errors are 0, 1 and 1 notches respectively. The five unchanged cases and their
false-alarm rates are unchanged from the table above. Excluding Qurate does not establish
that the remaining six labels were still outstanding on August 29.

## Sample attrition, uncertainty and cost

Twenty candidates were confirmed. The budget rule scheduled both changed cases and the
14 cheapest unchanged input packages. Eleven of 16 initial document requests exhausted a
9,000-token output ceiling, which includes thinking, and returned no usable answer. The
two changed cases were rerun at 24,000 tokens. The seven successes therefore comprise five
initial unchanged successes and two selected changed reruns. The remaining nine scheduled
cases are X01-X07, X10 and X11; the four never scheduled are X08, X09, X13 and X18.

Descriptive 95% Wilson intervals for exact accuracy on n=7 are 15.8%-74.9% for the
scorecard, 25.0%-84.2% for judgement and 35.9%-91.8% for persistence. The offline audit
also records paired bootstrap intervals for the MAE difference against persistence.
These intervals do not correct disclosure-selection, cost-selection or response-failure bias.

Recorded spending was approximately $8.74: $7.49 for the first batch, $1.21 for the
rerun and $0.04 for the miniature preflight. Robert closed paid completion on September 12
([D11](decisions.md)); the 13 remaining cases will not be run. The preflight checked API
parameter compatibility, but did not establish adequate output headroom for full filings.

## What the audit establishes and what it does not

All 18 saved document-request packages replay exactly from their cached primary filings.
The request/form/date checks pass, and no model request declares tools or cache directives.
This verifies specific controls, not complete absence of rating information or training
contamination. The first batch did not establish that probes completed before documents.
The offline join restores the original probes to the reruns; Nike's original probe recalled
A1, its prior rating, rather than having no rating knowledge.

The original history/peer packs lacked per-field source provenance. The prompt supplied
short qualitative descriptions rather than the complete methodology rubric. Its 46/47
reported agreement with XBRL is a consistency result, since XBRL was already part of the
input. It does not prove that extraction or financial adjustments are solved.

The [integrity review](../../docs/oos-integrity-review.md) records the full findings and
repairs. Original paid artifacts remain under the two ignored run directories:
`msgbatch_01EwnHhsKjahuwhmL8S5h2Sx` and `msgbatch_01QsBQnMF1itHj1Ysz3jguKZ`.
The local offline audit is `runs/offline-review-2026-09-12/audit.json`; raw files are not
included in a fresh repository clone. The previous results narrative is retained in Git
history, while this page is the current interpretation.
