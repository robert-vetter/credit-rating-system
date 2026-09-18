# Answers to the review questions of 17 September 2026

*Written 18 September 2026 by Claude (Fable 5.1), directed by Robert Vetter. Answers to the eight points and the two main-problem questions raised in the lab's review of the previous folder. Checked against the [specification](SPECIFICATION.md) in this folder, the [accounting study](../../experiments/05-accounting-interventions/results.md) and its saved study record, the [calibration summary](../../evaluation/calibration-summary.md), `system/`, and the vendor pages named inline. Nothing was rerun; no label or result changed.*

| # | Question | Short answer | Detail |
|---|---|---|---|
| 1 | Input data characteristics as a table | Done. 19 issuers, 47 filings, 1 changed in 19, 9 investment grade and 10 speculative, median request 155,707 tokens | [Spec section 3](SPECIFICATION.md#3-sample-and-data-characteristics) |
| 2 | Highly imbalanced data: special treatment? | Yes, it is imbalanced (1 in 19; 6.0% base rate). Treatment: persistence baseline, changed/unchanged split, false-alarm and direction metrics, stratified gold set. Not done: resampling or class weights, because nothing is trained | section 2 below; [Spec section 9](SPECIFICATION.md#9-metrics-baselines-and-the-imbalance) |
| 3 | A top commercial LLM | Claude Opus 4.6 was the first pilot (7 issuers, $8.74). GPT not yet run. GPT-5.2 fits the boundary; a run costs about $10 to $25 | section 3 below |
| 4 | Filing and report dates per issuer in one table; day precision | Done, one table with prior rating, filings, label, action and results. Nike's action is 12 November 2025. Qurate's day is still to be read from the Moody's release | [Spec section 4](SPECIFICATION.md#4-per-issuer-table-prior-rating-filings-label-action-and-results) |
| 5 | The Signet sentence | Three runs with identical corrected numbers gave A3, Baa1 and A1 because their four qualitative grades differed | section 5 below, worked calculation |
| 6 | Only one deterministic calculation | Agreed, and that is how it is built. The deviations were the model's extraction errors, which the experiment measured rather than corrected | section 6 below; [Spec section 8](SPECIFICATION.md#8-the-deterministic-calculation) |
| 7 | "Hand-labelled data" | A human analyst's checked record of the inputs, adjustments, factor grades and scorecard outcome for an issuer at a date | section 7 below |
| 8 | A specification | Written: [SPECIFICATION.md](SPECIFICATION.md), with nine decisions for consensus in its section 13 | |
| M1 | Have Codex or Claude Code been used to decipher the Moody's logic from real data? | As engineering and audit tools, yes. As a decipher tool on real data, only one statistical step so far | section 8 below |
| M2 | Has deciphered logic been encoded into agents? | The published scorecard arithmetic is encoded and tested. Nothing deciphered from data is encoded yet. The model side is a single structured call, not an agent | section 8 below |

## 2. Imbalance

The post-cutoff sample has one changed issuer in nineteen. The historical grid says this is normal: 218 changes in 3,646 issuer-quarters, 6.0%. Two consequences follow. A predictor that never moves is right 94% of the time, so raw accuracy says nothing. And any signal for a change must be judged on very few cases.

| Measure | Done | Where |
|---|---|---|
| Persistence baseline next to every number | yes | every results note |
| Every metric split into changed and unchanged | yes | results tables |
| False alarms on unchanged; direction on changed | yes | results tables |
| Sample built to over-represent changes | yes, for the historical gold set: 30 changed of 50 against a 6% base rate | `evaluation/goldset.json` |
| Changed cases scheduled first under the budget | yes | Experiment 03 rule D9 |
| Resampling, class weights, cost-sensitive loss | no. No component is trained on these labels; the LLM is used as is | |
| Precision and recall of the change decision | not possible with one changed case | |
| A stated cost of a missed change against a false alarm | not agreed; needed for any decision rule | Spec decision 3 |

The one fitted component, the change thresholds in the historical calibration study, selected "never alarm" in all five folds on 1,665 observations with 78 changes. That is the textbook result of imbalance plus a weak signal, and it is reported as a negative result, not hidden behind accuracy. More changed cases can only come from the lab's dated rating histories for the post-cutoff window, or from an older boundary with official labels (Arm 2: 59 issuers, 12 changes, not yet authorized).

## 3. A top commercial model

| Model | Vendor-stated bound | Fits boundary 2025-09-30? | Run? | Result |
|---|---|---|---|---|
| Claude Opus 4.6 | training cutoff August 2025 | yes | yes, 2026-09-10, 7 usable issuers, $8.74 | judgement 4/7, scorecard 3/7, persistence 5/7 |
| Qwen3-235B-A22B-Instruct-2507 | none stated; checkpoint 2025-07-21 | yes | yes, 2026-09-13, 20 issuers, 3 replicates, $1.24 | judgement 17/19, scorecard 3/19, persistence 18/19 |
| GPT-5.2 | knowledge cutoff 31 August 2025; 400,000-token context; $1.75 / $14 per million tokens (vendor page, read 2026-09-18) | yes | no | proposed as Experiment 07 |
| GPT-5.5 | knowledge cutoff 1 December 2025 (vendor page, read 2026-09-18) | no: Nike's 12 November 2025 and Qurate's October 2025 actions are inside its data | no | not usable for this window |

Opus was the first pilot precisely because it was the strongest available model; its cost at 60,000 to 300,000 tokens per issuer capped that run at seven. On the same seven inputs Qwen reproduced Opus's aggregate judgement accuracy in two of three replicates, with different mistakes. That is one data point, not evidence that a stronger model would not do better. A GPT-5.2 run on the identical frozen inputs, three replicates, all 20 issuers, needs about 3.4 million input tokens per replicate at Qwen counts, so roughly $10 to $25 depending on the tokenizer and whether a batch discount applies. It needs an approved cap, a pre-flight, and a dated snapshot of the vendor cutoff page, as for every run.

## 5. The Signet sentence, worked out

Signet was run three times with identical inputs (replicates r1, r2, r3). Each run returned ten financial figures and four qualitative grades. The accounting study then replaced only figures that the filing supports with an exact number, holding each run's four grades fixed. For Signet the one supported change was debt: r3 had returned zero debt although the 10-K discloses $1,217.3 million of operating-lease liabilities, so its debt was set to at least that amount, as r1 and r2 had already done.

After that change the ten figures were identical in all three runs, so the quantitative half of the scorecard was identical. The ratings still differed, and the difference is exactly the qualitative grades, which carry 45% of the weight.

| | r1 | r2 | r3 |
|---|---|---|---|
| Financial inputs after the supported change | identical | identical | identical |
| Quantitative weighted score (55% of weight) | 3.18 | 3.18 | 3.18 |
| Market Characteristics (10%) | Baa = 9 | Baa = 9 | Aa = 3 |
| Market Position (10%) | Baa = 9 | Baa = 9 | Aa = 3 |
| Revenue and Earnings Stability (10%) | Baa = 9 | Ba = 12 | Aa = 3 |
| Financial Policy (15%) | Baa = 9 | Baa = 9 | Aa = 3 |
| Qualitative weighted score (45% of weight) | 4.05 | 4.35 | 1.35 |
| Aggregate | 7.23 | 7.53 | 4.53 |
| Scorecard rating | A3 | Baa1 | A1 |
| Label / persistence | Ba3 / Ba3 | Ba3 / Ba3 | Ba3 / Ba3 |

Two things follow. First, the same model reading the same documents at temperature zero graded Signet's business anywhere from Aa to Ba, a three-notch spread in the result. Second, all three are far from Ba3, so on this issuer the grading is both unstable and too favourable. The study does not say which grades are right. It says that fixing the numbers alone would not have fixed Signet.

## 6. One deterministic calculation

Agreed. The calculation has three layers and the sentence quoted mixed two of them.

| Layer | What it is | Deterministic? | In Experiments 03 and 04 |
|---|---|---|---|
| Arithmetic | ratios, bands, weights, mapping to a notch | yes, one tested function | computed by code, identical for every run and model |
| Input definitions | what counts as revenue, EBITDA, interest, debt, and Moody's adjustments | yes, once written down; the methodology defines them | the model was asked to extract the ten numbers from the filings itself |
| Extraction | finding the numbers in a filing | should be deterministic given the definition | the model made errors: net interest income as interest expense, leases left out of debt, pretax income as operating income |

The Walmart and Signet sentences describe layer three errors, not alternative calculations. Gross interest is the definition; net interest is an error the model made and the prompt allowed. The experiment measured what the model does unaided and deliberately did not correct it, because correcting it would have hidden the finding. The accounting study then measured what the corrected inputs would have given: Walmart's coverage moves from 7.15 to 6.21 times without crossing a notch boundary; Signet's r3 moves two notches.

The consequence is written into the specification: one definition per input (section 8.1), computed in code from XBRL through the evidence ledger, with the model used only for facts XBRL lacks and only with a cited quote. One caveat remains. Moody's own adjusted figures are not public, so "the one correct calculation" is our written reading of the methodology until it can be checked against a reference, which is question 7.

## 7. Hand-labelled data

For one issuer at one date, a human analyst's checked record of:

| Element | Example |
|---|---|
| the ten inputs after Moody's adjustments | debt including leases and pensions as Moody's counts them |
| the adjustments themselves, with the source line for each | operating-lease liabilities $1,217.3 million added to debt |
| the four qualitative factor grades with the reasons | Market Position: Baa, because ... |
| the scorecard-indicated outcome next to the assigned rating | scorecard Ba2, assigned Ba3, difference explained by ... |

Why it matters: the final rating alone cannot tell whether an error came from extraction, from an adjustment, from a grade or from committee judgement. Moody's Credit Opinions contain this grid for each rated issuer. Access through Robert's Moody's account was being checked and is not concluded. Moody's rating-action releases sometimes state the scorecard-indicated outcome as well. If the lab holds anything like this, or the dataset mentioned at the start of the project contains it, it changes what can be measured. If not, a small set is built here (the Experiment 06 protocol drafts how, and is pending human review) and the lab reviews it.

## 8. The main problem: decipher and encode

| | Decipher: LLMs as a tool to find Moody's logic in real data | Encode: the logic as code or agent |
|---|---|---|
| Published part of the methodology (weights, bands, mapping, footnote rules) | no deciphering needed; transcribed from the PDF | **encoded** in `system/scorecard.py`, tested, corrected 2026-09-12 |
| Input definitions and Moody's adjustments | partly written down (spec section 8.1); Moody's adjusted figures not available to check against | **partly**: evidence ledger and accounting checks exist since 2026-09-17, offline, pending review; no adjusted total yet |
| Assigned rating versus numbers-only scorecard, from real data | **one statistical step done**: calibration study on 1,665 historical observations. Moody's assigns on average 0.71 notches (median 1) worse than the numbers imply; a fitted correction cuts MAE from 1.92 to 1.49; no annual-number signal times a change | not encoded; the correction is a diagnostic, not part of the analyst |
| Qualitative grading logic | not deciphered; the model grades from brief descriptions | encoded only as a prompt; grades are unstable (section 5) |
| Considerations outside the scorecard, committee judgement, timing of changes | not deciphered | not encoded |
| Reading Moody's rating-action releases and Credit Opinions with an LLM to extract stated adjustments, grades and scorecard outcomes into an explicit rule set | **not done**; the natural next decipher step; depends on document access (spec decision 8) | |
| Agent | | not built. The model side is one structured call with no tools by design (leakage control). The architecture is a [proposal](../architecture-codex-2026-09-13.md) |

Codex and Claude Code have been used throughout as the engineering and audit tools: they built the apparatus, ran the experiments and audited each other, which found the three-notch scoring bug and the redaction failure. As a decipher tool on real data they have been used once, for the calibration study. The honest state is that deciphering from data is at its beginning, and nothing beyond the published arithmetic has been deciphered, so nothing beyond it is encoded.
