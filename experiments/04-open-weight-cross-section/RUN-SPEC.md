# Experiment 04: post-release credit rating accuracy

*Written by OpenAI Codex, directed by Robert Vetter, 13 September 2026. Experiment implemented with Claude; verified against the frozen EXP04-ARM1-A1 manifest and [revised results](results.md).*

## Research question

Can an existing LLM estimate outstanding Moody's ratings from company filings after its training-data boundary, more accurately than retaining the earlier rating?

This Retail and Apparel pilot uses a checkpoint release date as the model's information bound and company disclosures as labels. **It does not establish a vendor-stated training cutoff or independently verified outstanding ratings.**

## Model, dates and sample

| Item | Specification |
|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507, API ID `qwen/qwen3-235b-a22b-2507`; non-thinking variant. |
| Training-data evidence | No vendor-stated cutoff. The public checkpoint was released on **21 July 2025**, an upper information bound for those released weights. Hosted identity is provider-reported. [Evidence and checkpoint verification](review-codex-2026-09-12.md). |
| Deployment | DeepInfra fp8 through OpenRouter, pinned provider with no fallback; 262,144-token context. |
| Observation date | **29 August 2026**. |
| Primary filing window | Filed after **30 September 2025** and on or before the observation date. |
| Earlier rating history | Ends **28 August 2025**; intentionally supplied to the model and used for persistence. |
| Sample | All 20 confirmed disclosure-labelled issuers in the [candidate set](../03-oos-values-first/candidates.json): 18 unchanged and two changed relative to the earlier rating. |
| Primary cohort | 19 issuers, excluding Qurate before execution because its label's entity/rating-type match and validity after bankruptcy events were unresolved. |
| Repetitions | Three separate document calls per issuer with identical inputs, temperature 0 and seed 20260912; maximum 8,192 output tokens each. |

Labels were hand-read from filings because the available public Moody's history ends in August 2025. Their continuing validity at the observation date is unverified. Selection depends on disclosure availability; the two changed labels are Nike and Qurate.

## Inputs and prompt

Each issuer receives its latest eligible 10-K and subsequent 10-Qs, dated annual/quarterly financials from XBRL, historical ratings, and a peer table without ratings. All supplied facts must have been public by the observation date. Current peer rows must have a fiscal-year end within the preceding 24 months. No 8-Ks or exhibits are model input.

The fixed context rule drops the oldest 10-Q when necessary: Levi Strauss's 7 April 2026 filing and Qurate's 15 May 2026 filing were removed, leaving 49 documents. Full requests were counted with chat-template, schema and output allowances before submission.

The structured prompt asks the model to:

1. Extract ten financial inputs in USD millions from the most recent full fiscal year: revenue, operating income, D&A, capex, interest, cash, dividends, operating cash flow, working-capital movement and adjusted debt; note material subsequent-quarter developments.
2. Grade four qualitative factors relative to the history pack's implied anchor: market characteristics, market position, revenue/earnings stability and financial policy.
3. Give a separate overall rating judgement and explain whether it retains or changes the earlier rating.

Code converts the extracted figures and grades into a scorecard-indicated rating. This is scored separately from the model's judgement. The prompt supplies brief factor descriptions, rather than the full methodology rubric. Verbatim [system prompt](../03-oos-values-first/prompts/system.txt), [task](../03-oos-values-first/prompts/task_values_first.txt) and [output schema](../03-oos-values-first/prompts/schema_values_first.json) are preserved.

Internet grounding, model tools and live retrieval were absent. A separate [memory probe](../03-oos-values-first/prompts/probe.txt), limited to 1,200 output tokens, completed and was reviewed before each issuer's documents; probe answers were not supplied to subsequent calls. No probe produced verified post-bound rating/action recall, but a negative probe cannot establish absent contamination.

## Scoring and findings

**Exact accuracy** is exact matches divided by planned issuers. Also report within-one-notch accuracy and mean absolute notch error (MAE). Consensus requires three valid ratings and takes their ordinal median. Persistence retains the earlier rating. Missing outputs remain missing; conditional metrics use matching persistence subsets.

The post-run review found surviving rating information in Kohl's inputs and, in a follow-up scan, short-term rating/outlook cells in Dollar General's. Original results are retained; exclusions are explicitly post-hoc sensitivities, not a prospectively selected clean test.

| Cohort, current-input consensus | Judgement exact / MAE | Scorecard exact / MAE | Persistence exact / MAE |
|---|---|---|---|
| Original 19 | 17/19 (89.5%) / 0.11 | 3/19 (15.8%) / 1.84 | 18/19 (94.7%) / 0.05 |
| Excluding Kohl's: 18 | 16/18 (88.9%) / 0.11 | 3/18 (16.7%) / 1.78 | 17/18 (94.4%) / 0.06 |
| Excluding both: 17 | 16/17 (94.1%) / 0.06 | 3/17 (17.6%) / 1.71 | 16/17 (94.1%) / 0.06 |
| All 20, including Qurate | 17/20 (85.0%) / 0.20 | 3/20 (15.0%) / 1.80 | 18/20 (90.0%) / 0.15 |

Neither channel beats persistence. In the original 19, judgement is within one notch on 19/19 and scorecard on 10/19; both miss Nike, with respectively one and 15 false alarms among 18 unchanged issuers. Excluding both residual cases leaves judgement equal to persistence, still missing Nike, and scorecard with 13 false alarms among 16 unchanged issuers. One primary change cannot establish general change-detection performance. [Full tables and replicate results](results.md).

## Matched comparison and completion

A secondary arm repeats the saved inputs of seven successful Opus 4.6 cases, three times each. Qwen's first two replicates match Opus's aggregate judgement: 4/7 exact, MAE 0.57, versus persistence's 5/7, MAE 0.43. Different mistakes, inference settings and selection of Opus successes preclude an equivalence claim. The main arm's revised history/peer inputs are not matched to Opus.

Completion after ten extra attempts: 20/20 probes, 60/60 current-input and 19/21 saved-input document requests, with one additional undefined saved scorecard. Reconciled cost was **$1.24**, plus **$0.14** reserved for uncertain transport failures, under a $3 cap.

The [decision log](decisions.md) and [audit](review-codex-2026-09-13.md) document authorization, failures and subsequent repairs. Repairs do not change the paid inputs or establish that the executed run was free of leakage.
