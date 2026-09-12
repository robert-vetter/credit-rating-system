# Experiment 03: post-cutoff cross-section, values first

*Specification of the run actually performed, updated by Codex, directed by Robert Vetter,
2026-09-12. Original design by Robert and Claude, 2026-08-31; execution 2026-09-10.
Verified against saved batch requests, audits, outputs, candidates and the integrity review.
This replaces the earlier prospective specification; original prompts and decisions remain
unchanged. Earlier specification versions remain in Git history.*

## Question and sample unit

Estimate the outstanding long-term Moody's rating at **August 29, 2026**, after the model's
training-data cutoff. One issuer/group at that date is one observation. Unchanged ratings
are included. The primary reported number is exact-match accuracy alongside persistence;
changed/unchanged splits are diagnostics, not a restriction to rating actions.

This is reconstruction of a post-cutoff rating state using information available by the
observation date. It is not a forecast made before a subsequent rating action. Since the
available labels are company disclosures, their validity at the exact observation date is
not fully established. This is a pilot with explicit label and selection limitations.

## Model and execution

| Parameter | Recorded value |
|---|---|
| Model/API ID | Claude Opus 4.6, `claude-opus-4-6`; same model ID recorded in results |
| Training-data cutoff | August 2025, vendor-reported |
| Reliable knowledge cutoff | May 2025; the broader training cutoff determines the boundary |
| Document boundary B | September 30, 2025, a one-month buffer after the cutoff month |
| Observation date | August 29, 2026 |
| Thinking | Adaptive |
| Effort | High for document analysis; low for memory probes |
| Output | JSON-schema structured output |
| Sampling | API defaults; temperature, top_p and top_k not supplied |
| Document output ceiling | 9,000 tokens initially; 24,000 for the two reruns, including thinking |
| Probe output ceiling | 1,200 tokens |
| Transport | Anthropic Message Batches API |
| Internet grounding/RAG | No tools declared, no external retrieval supplied by the runner |
| Cache directives | None |
| Context | Separate single-user API requests; probe answers were not fed into document requests |

The cutoff is recorded in [the dated evidence note](evidence/opus-4-6-cutoff-2026-09-10.md)
and was rechecked against [vendor documentation](https://platform.claude.com/docs/en/models/opus-4-6/overview)
on September 12. It is not a proof that all post-cutoff information is absent from model
weights. A negative memory probe is also not such a proof.

## Population, labels and selection

The design starts from 63 in-scope current filers in the Retail/Apparel frame. The label
harvester scans post-boundary 10-Ks, 10-Qs and 8-Ks for Moody's rating disclosures. Candidate
statements were read to distinguish actual ratings from covenant thresholds and pricing
grids; Robert confirmed 20 candidates. See [candidates.json](candidates.json) and
[label-review.md](label-review.md).

The rating-history archive's latest recorded action date is August 28, 2025. The run's
persistence reference is the rating selected from that archive at this history cutoff.
The archive does not supply labels for the August 2026 observation date, so the pilot uses
the latest accepted company disclosure on or before that date. An unchanged candidate means
its accepted disclosure equals its persistence reference. It does not prove no intervening
rating action occurred.

Under the original budget selection rule, both recorded changed cases and the 14 cheapest
unchanged document sets were scheduled. Eleven initial document requests exhausted the
output ceiling. The two changed cases were rerun with a higher ceiling. There are therefore
seven successful cases, not a random seven-issuer sample: five initial unchanged successes
plus two changed reruns. Nine scheduled cases have no scored answer and four confirmed
cases were never scheduled. These failures and exclusions remain disclosed.

Qurate's accepted label is especially weak: its evidence was filed November 5, 2025, while
its model input includes 2026 filings describing bankruptcy. Its label identifies LI LLC's
CFR and its input covers consolidated QVC Group. The broader candidate set also mixes
issuer/CFR and senior-debt ratings. Neither labels nor mapping were changed in the review.
Results must be shown with and without Qurate; the latter is a sensitivity, not a newly
certified sample.

## Inputs and prompt

For each document request, the saved message supplied:

1. The latest 10-K filed strictly after B, followed by all subsequent 10-Qs filed on or
   before the observation date. Only cached primary documents were included. No exhibits
   or 8-Ks were model input. HTML was converted to line-preserving text and rating
   disclosures were removed with `system/redact.py`.
2. A history pack: recorded rating events through August 28, 2025 and the persistence
   rating; the latest available annual XBRL fundamentals plus up to three prior years;
   implied average qualitative anchors derived from historical ratings and numerical
   factors; recent quarterly figures where available. The anchors are not Moody's actual
   published factor grades.
3. A peer financial table inside the history pack, without peer ratings.
4. The observation date and the values-first task.

The verbatim [system prompt](prompts/system.txt), [task](prompts/task_values_first.txt) and
[output schema](prompts/schema_values_first.json) ask for ten financial inputs in USD
millions for the latest full fiscal year, four qualitative grades, relative movements and
reasons, and a separate overall rating judgement. The financial inputs are revenue,
operating income, D&A, capex, interest, cash, dividends, operating cash flow, working-capital
swing and debt.

This is a structured, history-conditioned prompt. Its limitations matter: the full
methodology rubric and adjustment definitions were not supplied; missing figures cannot
be represented as null; explanations have no machine-verified source citations. Current
XBRL figures were already in the input, so agreement against those figures is not an
independent extraction test. Nike, Qurate and Walmart had no quarterly rows in their saved
packs. The other 13 scheduled issuers had four each.

## Date and contamination controls: executed versus intended

| Control | What the original evidence establishes |
|---|---|
| Document boundary | All saved input filing dates satisfy `B < filed <= as_of`; allowed forms and cached primary-document metadata replay successfully. |
| Label evidence date | All accepted evidence filing dates are in the boundary window. This does not certify the rating remained outstanding at as-of. |
| Rating history | Saved event dates are no later than the history cutoff. Source paths can mix entity and instrument events. |
| Fundamentals and peers | Builders filtered by filing date. Original audits did not preserve every field's source date/tag. They cannot support the earlier claim of complete per-fact provenance. |
| Redaction | All 18 saved document packages reproduce exactly from cached primary documents and the redactor. This verifies reproducibility, not perfect semantic removal. |
| Memory probes | Separate no-document requests were submitted for all 16 scheduled cases. Probes and document requests shared the first batch, so probe-first processing is unverified. |
| Probe interpretation | No demonstrated recall of either new changed-case label; Nike recalled A1, its prior rating. The offline review joins original probes to reruns. It does not certify a clean subset. |

The [probe prompt](prompts/probe.txt) requests recalled ratings, financial metrics, fiscal
periods and recent rating actions. Its inability to retrieve a fact is evidence about that
probe, not proof the fact is absent from the model.

A post-B disclosure also does not automatically date its rating action after B. Nike's
December 30, 2025 10-Q explicitly dates its downgrade to November, and Qurate's November 5
filing refers to October. This is supporting evidence for the changed-case diagnostic.
It is not an eligibility requirement that all issuers changed after the cutoff.

## Scoring and uncertainty

The primary values-first channel sends the ten numerical inputs and four qualitative
grades through `system/scorecard.py`. The overall model judgement is reported separately.
Exact accuracy is `number of exact matches / number of scored cases`. MAE is the average
absolute difference in positions on the 21-notch Moody's scale. Within-one accuracy is
also reported. Persistence uses the same cases and labels.

[Results](results.md) contain the original and corrected arithmetic, changed/unchanged
splits, false alarms, and the without-Qurate sensitivity. Wilson accuracy intervals and
paired error bootstrap intervals are descriptive only: they do not remove small-sample,
disclosure-selection or response-failure bias. No channel demonstrates superiority to
persistence on this pilot.

## Budget and current status

The original cap was $10. Recorded spend was approximately $8.74, including the miniature
paid preflight, original batch and two reruns. Original worst-case pricing used token
counts and the output ceilings; a miniature preflight checked API parameter acceptance,
not full-document output headroom.

Robert closed paid completion on September 12 ([D11](decisions.md)). The remaining 13
cases will not be run. Submit, rerun and paid preflight entry points now reject execution.
There is no new paid budget or authorization.

## Repairs, reproducibility and remaining work

The September 12 review fixed negative-leverage and net-cash scoring, outcome rounding,
per-field date checks, matching fiscal periods and source logging in peer/history packs,
and gold/nested-fitting separation in the independent calibration study. These repairs
are not retroactive claims about the original model input. Original prompts, saved paid
artifacts and candidate decisions remain unchanged.

From the repository root, with the saved local data present:

```sh
python3 experiments/03-oos-values-first/audit_saved_run.py
python3 -m unittest discover -s experiments/03-oos-values-first -p 'test_*.py' -v
```

The audit writes `runs/offline-review-2026-09-12/audit.json` without model or network calls.
Raw requests, outputs and caches are gitignored; a fresh clone contains the specifications,
source and result summaries, not a complete replay bundle.

A stronger subsequent experiment needs a fixed target entity/rating type, verified
outstanding labels, the supplied methodology rubric, citation validation, and completed
probe review before document submission. The [integrity review](../../docs/oos-integrity-review.md)
details these limitations and proposes the analyst architecture. No new experiment has
been launched.
