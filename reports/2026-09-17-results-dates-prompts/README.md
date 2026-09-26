# Post-cutoff rating estimation: five-minute update

*Prepared by OpenAI Codex, directed by Robert Vetter, 17 September 2026. Experiment implemented with Claude and reviewed with Codex. Checked against saved requests, input audits, accepted disclosure labels, corrected results and the local accounting prototype. This is a research summary, not an independently certified benchmark.*

**Question:** Can an existing model estimate outstanding Moody's ratings at a date after its information boundary, more accurately than carrying the earlier rating forward?

**Answer so far:** No improvement over persistence has been demonstrated. The primary sample has only one changed issuer, and the labels' continuing validity at the target date is not independently verified.

| Read | Contents |
|---|---|
| **This page** | Setup, results, limitations and next work |
| [DATES-AND-LABELS.md](DATES-AND-LABELS.md) | Every supplied filing's period/publication date; label sources; known rating-action timing |
| [PROMPTS.md](PROMPTS.md) | Verbatim instructions, request structure, settings and complete output schemas |

## 1. Experiment setup

| Item | Main experiment: Qwen, run 13 September 2026 |
|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507; DeepInfra fp8 through OpenRouter, no provider fallback |
| Training-data bound | **Public checkpoint released 21 July 2025. No vendor-stated training-data cutoff.** Release bounds the released weights; hosted identity is provider-reported. |
| Prior-rating history ends | **28 August 2025**; this rating is the persistence baseline |
| Primary-document eligibility | Publicly filed **after 30 September 2025 and on/before 29 August 2026** |
| Actual primary-cohort input filings | **18 December 2025 to 28 August 2026**, 47 documents for 19 issuers |
| Target date | **29 August 2026** |
| Sample | 20 disclosure-labelled issuers executed; Qurate excluded from the primary 19 before execution because of label/entity problems |
| Inputs | Latest eligible 10-K and subsequent 10-Qs; dated XBRL financials, historical ratings, implied qualitative anchors and peer financials without peer ratings |
| Controls | No model tools, Internet grounding or live retrieval; no 8-Ks/exhibits as model input; separate memory probes completed/reviewed before documents |
| Repetitions | Three calls per issuer; identical inputs, temperature 0, fixed seed; ordinal-median consensus |
| Outputs | Model's overall rating judgement; separately, a deterministic scorecard from extracted figures and qualitative grades |

Older financial periods and historical ratings were deliberately supplied. A filing published after the model bound need not contain only post-bound economic information. This is **rating-state estimation using information available by the target date**, not a forecast made before a rating action.

## 2. Results, with matched persistence baselines

**Exact accuracy** = exact label matches / issuers in the stated cohort. All 60 main-arm document responses were valid. Repeated calls measure stability, not additional independent issuers.

| Cohort | Changed / unchanged at endpoints | Model judgement exact | Scorecard exact | Persistence exact |
|---|---:|---:|---:|---:|
| Original primary 19, excluding Qurate | 1 / 18 | 17/19 (89.5%) | 3/19 (15.8%) | 18/19 (94.7%) |
| Post-hoc: also exclude Kohl's | 1 / 17 | 16/18 (88.9%) | 3/18 (16.7%) | 17/18 (94.4%) |
| Post-hoc: also exclude Dollar General | 1 / 16 | 16/17 (94.1%) | 3/17 (17.6%) | 16/17 (94.1%) |

In the primary 19, judgement MAE is **0.11 notches**, scorecard MAE **1.84**, persistence MAE **0.05**. The model judgement missed Nike's A1 to A2 downgrade and introduced one false alarm, Dollar General. In the 17-case sensitivity, judgement equals persistence and still misses Nike.

**Why the sensitivities?** The audit found Kohl's B2 rating in the supposedly redacted input, then residual short-term rating/outlook cells for Dollar General. Both are disclosed here; the previous email mentioned only Kohl's. Original records are preserved. Exclusions and later redaction fixes do **not** turn this into a prospectively clean test.

**Earlier Opus pilot:** vendor-reported **August 2025 training cutoff**; judgement **4/7**, scorecard **3/7**, persistence **5/7**. Without diagnostic Qurate: **4/6**, **3/6**, **5/6**. Selected successful responses after output-limit failures, not a representative sample or directly comparable to Qwen's 19-case headline.

## 3. What remains unresolved

- **Labels:** disclosures are not complete histories through the target date. Entity/CFR and debt ratings need a consistent target definition.
- **Leakage and sample size:** date checks and negative probes do not establish no contamination; only one primary issuer changed.
- **Prompt:** abbreviated rubric; required numeric answers even when evidence was missing; net interest explicitly allowed as a fallback. These are design limitations, not solely model errors.
- **Validation:** XBRL was already in the input, so agreement is not independent extraction validation. Anchoring on the prior remains an untested hypothesis.

## 4. Further work: completed versus proposed

**Completed since the earlier experiment:** a controlled accounting intervention study on all nine saved Walmart/Nike/Signet responses. Replace only source-supported financial inputs, holding each response's qualitative grades fixed.

| New observation | Measured result |
|---|---|
| Accounting changes can be masked by scorecard boundaries | Walmart gross-interest treatment changes coverage **7.15×→6.21×**, but no rating changes. |
| A material individual effect need not change consensus | Signet's minimum disclosed-lease inclusion moves one response **Aa2→A1**, but its three-response median stays A3. |
| Financial consistency does not ensure rating stability | After supported interventions, Signet's complete financial vectors are identical across replicates, but stored grades yield **A1–Baa1, a three-notch spread**. This does not establish which grades are correct. |

All three issuer consensuses remain unchanged: **0/3 exact, MAE3.00**, versus persistence **2/3, MAE0.33**. This is a diagnostic on known development cases, not a new holdout or complete accounting correction. Gross interest remains unresolved for Nike/Signet; the Signet debt test is a disclosed-lease floor, not full adjusted debt. Twenty-one study tests and80 prior regressions pass. [Study and evidence](../../experiments/05-accounting-interventions/results.md).

<details>
<summary>Source-tracing foundation used for the study</summary>

| Development case | Verified observation | Why it matters |
|---|---|---|
| Walmart | A February-April quarter has 88 elapsed days; legacy date approximation treated it as 60. Two revenue concepts also disagree for the same period. | Preserve exact fiscal intervals and review concept definitions rather than silently select a value. |
| Nike | Net interest income and cash interest paid are separately identified; gross expense remains unresolved in this prototype. | Neither is automatically a valid gross-interest denominator. |
| Signet | $1,217.3m operating lease liabilities reconcile to $286.9m current + $930.4m noncurrent. Two later-filed comparative facts are excluded. | Missing borrowing tags are not zero debt; every fact needs its own public date. |

Accounting interpretations remain pending human review. Earlier experiment records and compact caches are unchanged; the exact-date fix is in the new reader only.

</details>

**Next study, not yet run:** distinguish insufficient evidence from inconsistent application of rating criteria. Hold both financial inputs and evidence fixed. Compare factor grades with independent reviewers' assessments under the same information constraints, allowing justified grade ranges or insufficient-evidence decisions. Measure reference agreement separately from repeatability; consistent but unsupported grades are not success. Reviewer disagreement itself can reveal ambiguity. This requires reference assessments that are not yet available, not another run with different evidence. Verifying outstanding-rating labels remains necessary before broader rating-accuracy claims.

**Two focused questions for discussion:**
1. Are hand-labelled credit-analysis examples available for research, particularly checked financial inputs, accounting adjustments or qualitative factor assessments?
2. Can we obtain complete dated rating histories, including the initial rating, actions and withdrawals, with rated-entity and rating-type identifiers, to verify outstanding ratings and expand the post-bound sample?

<details>
<summary>Optional provenance and execution details</summary>

This folder is self-contained for the main interpretation. Underlying records: [executed specification](../../experiments/04-open-weight-cross-section/RUN-SPEC.md), [corrected results](../../experiments/04-open-weight-cross-section/results.md), [post-run audit](../../experiments/04-open-weight-cross-section/review-codex-2026-09-13.md), [Opus specification](../../experiments/03-oos-values-first/README.md), and [accounting prototype commands](../../evaluation/README.md#offline-accounting-development-review).

Qwen's full execution also included 21 planned saved-input comparison calls on the seven successful Opus cases. Two Qwen replicates matched Opus's aggregate judgement accuracy on those inputs, with different mistakes; this is not evidence of model equivalence. Total Qwen spend: $1.24 reconciled plus $0.14 reserved for uncertain transport failures. Opus pilot spend: $8.74. The totals buy different sets of calls and are not a like-for-like cost benchmark.

Saved raw requests, responses and company caches are local/gitignored. This folder publishes neither those full documents nor an end-to-end replay dataset. The prototype made no new paid model calls.

</details>
