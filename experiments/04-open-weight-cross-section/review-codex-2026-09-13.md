# Experiment 04 Arm 1: independent review after execution

*Written by OpenAI Codex, directed by Robert Vetter, 2026-09-13 UTC. Verified against repository commit 8a5df67, the frozen EXP04-ARM1-A1 manifest, all 111 attempt records, 104 saved HTTP responses, 555 ledger events, cached source documents, reconstructed packs, and the corrected Experiment 03 audit. Conclusions below distinguish measured results, failed controls and proposed repairs. No model requests, installations, changes to run records, commits, pushes or messages.*

## Overall verdict

**The records and arithmetic stand, but the 19-issuer result fails the claim of a fully redacted experiment.** Kohl's, X07, received its disclosed B2 corporate credit rating in both input filings, in all three current-input replicates. The redactor removed the agency headings and left the rating-table cells. The absence of the word Moody's did not establish successful redaction.

Keep the frozen 19-issuer result, disclose the failed control, and add an explicitly post-hoc sensitivity excluding X07 as well as the already excluded X14. Do not rename that sensitivity a prospectively selected clean benchmark. The saved seven-issuer arm does not contain X07 and survives this specific finding, subject to its original label and selection limitations.

The run stayed within its $3 cap. However, two additional fake-transport checks expose unsafe billing paths in the runner. **This review does not clear the runner for another paid run.** Repair redaction and billing guards and validate new inputs before any separately authorized spending. No rerun is needed to disclose what this execution established.

| Current-input consensus | Judgement exact / MAE | Scorecard exact / MAE | Persistence exact / MAE |
|---|---|---|---|
| Original 19, including the now known X07 leak | 17/19 / 0.105263 | 3/19 / 1.842105 | 18/19 / 0.052632 |
| Post-hoc 18, excluding X07 and X14 | 16/18 / 0.111111 | 3/18 / 1.777778 | 17/18 / 0.055556 |
| All 20, original sensitivity | 17/20 / 0.20 | 3/20 / 1.80 | 18/20 / 0.15 |

On the post-hoc 18, judgement and persistence are within one notch on 18/18; scorecard on 10/18. Judgement misses Nike, the one changed case, and creates one false alarm among 17 unchanged issuers. Scorecard also misses Nike and creates 14 false alarms. None of these cohorts has independently certified outstanding labels at the observation date.

## 1. Reproduce the numbers: pass with corrections

I reconstructed all replicate and consensus predictions from `results/attempts.json`, using the manifest labels and an independently defined ordered Moody's scale. Every valid parsed output also matches its saved HTTP content. All 79 document outputs pass their frozen schemas and reproduce their recorded scorecard/direct channels through the shared arithmetic. All 20 valid probes pass their respective frozen schema. The independent counts match all 32 serialized model metric blocks in `results/scores.json`, allowing its three-decimal rounding. All per-issuer predictions in the flat files and consensus files match; no failed output was replaced by persistence. The tables at the end give the independent counts, error sums and diagnostics.

The primary judgement MAE is 2/19, which rounds directly to **0.11**, not 0.10. `report.py` formats the already rounded 0.105 to two decimals, causing double rounding. Replicates 1, 3 and consensus need the correction. The integer counts are unaffected.

A consensus requires three valid predictions for that channel. The saved arm has five complete direct consensuses and four complete scorecard consensuses. Signet's saved replicate 2 has a valid direct rating and an undefined scorecard. Qurate and Victoria's Secret have no valid third response. Incomplete predictions remain missing.

The saved-arm report includes a full-cohort persistence row, but its conditional MAEs also need **matched valid-subset baselines**. For example, scorecard consensus MAE 3/4 = 0.75 must be compared with persistence MAE 1/4 = 0.25 on those four, not persistence's 3/7 on the full seven. Direct consensus MAE 2/5 = 0.40 compares with persistence 1/5 = 0.20. This does not change the conclusion.

The corrected Opus conversion gives scorecard 3/7 exact, 6/7 within one, MAE 8/7; judgement 4/7, 6/7, MAE 4/7; persistence 5/7, 6/7, MAE 3/7. Removing X14 gives scorecard 3/6, 5/6, MAE 7/6; judgement 4/6, 5/6, MAE 3/6; persistence 5/6, 6/6, MAE 1/6. These are from `experiments/03-oos-values-first/runs/offline-review-2026-09-12/audit.json`, not the original defective scorecard labels.

## 2. Ledger and execution decisions: executed accounting passes; reusable guard fails

Independent Decimal replay confirms the authorization/manifest hash, consecutive ledger sequence, reservation before every dispatch, exact reservation formula, dispatch body hashes, no dispatch while halted, at most two attempts per request, ten extra attempts, and all 11 halts cleared after a reviewer note. Probe reviews precede the first documents and follow the matching valid probe; non-pilot requests follow the pilot review.

| Accounting item | Verified value |
|---|---|
| Planned logical requests / dispatches | 101 / 111 |
| Valid / invalid / unresolved attempts | 99 / 5 / 7 |
| Reconciled HTTP responses | 104 |
| Exact sum of response usage costs | $1.24222887 |
| Sum rounded upward per reconciliation | $1.242279 |
| Retained unresolved reservations | $0.141521 |
| Final counted total | $1.383800 |
| Highest counted total at any ledger event | $1.388231, sequence 552 |
| Open reservations / active halts at end | 0 / 0 |
| Preflight worst case, including ten maximum-size retries | $1.822559 |

All actual reconciled charges are below their individual reservations. There are 111 reserve, 111 dispatch, 104 reconcile, 99 valid, 5 invalid, 7 unresolved, 11 halt, 11 clear_halt, 12 note, 83 price_check and one open event. The twelve notes include a correction to an erroneous clock time in an earlier note.

There were **six retries after TLS failures, three after length failures and one after malformed probe JSON**. Nine retries succeeded. The other retry, saved X14 r3, followed a TLS failure and then failed by length. The seventh TLS failure, saved X19 r3, was not retried. The brief's seven transport retries and four length retries are wrong.

Keeping the unknown-billing reservations made the six transport retries defensible within Robert's explicit allowance. Changing to one process per request preserved the frozen bodies and shared cap; it was a reasonable operational mitigation, but later failures show connection reuse was not the sole cause. TLS failures occurred 0.028 to 0.155 seconds after dispatch, not all within 0.1 seconds. The account readings quoted in reviewer notes are only corroborative aggregate evidence. They do not resolve any individual unknown bill; keeping all seven reservations was correct.

The three identical-body retries after length loops respected the one-retry limit, unchanged ceiling and cap. They select a valid response after a generation failure, not a better rating after an incorrect answer. Their first failures remain part of the completion/cost evidence. Leaving the two exhausted requests missing was correct. Walmart's malformed probe was retried within the allowance, but the parser-invalid branch does not itself halt and no separate reviewer note for that retry is in this ledger. Do not claim that every invalid output halted for review.

### Failures to repair before reuse

Two additional checks used only `test_runner.Fake` and disposable fixtures:

1. An HTTP 500 JSON response containing `usage.cost = 0.01` was classified `failed_not_billed`; the entire reservation was released, with zero committed/unresolved cost and no halt. `_settle` assumes all recognized JSON error responses are unbilled, even when they carry a charge. Preserve the reservation on ambiguous errors; reconcile explicit usage/generation evidence before releasing it.
2. A normal-looking response carrying a $3.50 cost under a $3 cap was accepted as `valid`, committed $3.500000 and left no halt. The settlement path never checks charge against reservation or total against cap. Record the actual charge, flag the overrun and halt immediately; test both over-reservation and over-cap responses. A post-response check cannot undo a provider overcharge, so an absolute billing guarantee still depends on provider enforcement of prices and token limits.

Neither path occurred in this run. They invalidate the general statement that all cost/protocol failure modes are handled, not the observed $1.388231 maximum. Also address request-level fees if offered, require a fresh price check for each submitting session rather than accepting any historical ledger price check, and retain generation-detail responses for independent future reconciliation. The existing 40 acceptance tests pass but do not cover these adversarial cases. Gate labels are not proof of complete coverage.

## 3. Inputs, dates and redaction: fail on X07; reconstruction passes

Every one of the 101 stored bodies matches its manifest hash and expected request configuration. All hash groups match their sources: 19 code/prompt files, 50 primary documents across both arms, 87 raw companyfacts files, 86 extracted financial caches, 20 rating caches, seven observation caches and two archived request files. This verifies present identity with the frozen evidence; it is not a cryptographic history of every past filesystem state.

I rebuilt all 20 current packs and redacted document assemblies in memory. The pack logs and hashes, exact final user text, terminal persistence, dates and selected forms match the frozen audit. Each replay satisfies the implemented per-source eligibility and common-fiscal-period checks. The current arm has 49 primary filings; the union with the saved arm has 50. Levi drops its 2026-04-07 10-Q; Qurate drops its 2026-05-15 10-Q only in the current arm. Ten peers are excluded by the 24-month fiscal-end rule and 56 retained. The saved arm retains its older 66-peer policy.

All seven legacy provenance reconstructions pass, with 43 to 60 annual, 0 to 45 quarterly and 843 to 847 peer source records per pack, and 66 printed peers traced. Reassembling the three archived Opus text blocks reproduces each saved-arm Qwen body. The system prompt, task and schema also match. This is identity of supplied information under the documented join rule, not identical cross-vendor HTTP envelopes or tokenization. The repaired current arm is not a matched-input model comparison with Opus.

### Direct disclosure left in the body

In both Kohl's filings, the final model input contains:

```text
Financing Activities
Corporate credit
B2
B+
Outlook
Stable [Positive in the 10-Q]
Negative
Negative
```

Sources: `evaluation/companies/kohl-s/filings/2026-03-19_10-K_000119312526115982.htm` and `2026-06-04_10-Q_000119312526257402.htm`. The definitive executed evidence is `runs/EXP04-ARM1-A1/bodies/doc-current-X07-r1.json`, identically repeated in r2 and r3, and `audit/removed_lines/X07.json`.

The removed text identifies these as the corporate ratings/outlooks at January 31 and May 2, 2026. The B2 cell equals the frozen target label. `system/redact.py` stops the agency-following deletion at the non-rating row "Corporate credit" and its orphan-row rule does not delete a single soft symbol such as B2 on its own line. Agency-free residual scanning then misses the disclosure. The retained positive outlook is additional current information from the same rating table. The prior B2 was intentionally supplied, but a current disclosure confirming it is still prohibited target information. The system prompt asks the model to ignore surviving rating fragments; that instruction does not remove the leak or establish that it was ignored. We cannot determine whether the model used that leak to choose B2.

Required prevention: recognize and remove complete rating tables using their structure and surrounding labels, including row headers, standalone soft symbols, outlooks and agency-free fragments; preserve non-rating tables. Add this exact two-filing failure as an offline regression and scan assembled model-visible text independently of removed agency names. Never repair or overwrite the paid bodies retroactively.

The broader scan found no other explicit Moody's-grade disclosure in the inspected final filing text. PVH retains generic conditional wording about a future downgrade of its "investment rating". Dick's retains a Unicode-hyphenated reference to investment-grade counterparties, not its own rating. Victoria's Secret's four upgrade/downgrade hits concern systems and equity analysts. Several A2/A3 hits are XML debt-coupon identifiers, not ratings. These distinctions matter: a lexical hit is not automatically a target leak. Coupon amounts, business identity, distress and financing facts still prevent any claim of universal semantic decontamination.

Qurate's bankruptcy narrative is dated, permitted business evidence. Removing it to fit the stale label would corrupt the task. It instead exposes the unresolved entity/rating-type/as-of contract. Date eligibility at t also does not prove that an old annual reconstruction was exactly what an analyst knew at that earlier fiscal year end; restated values public by t are a separate issue from vintage historical simulation.

## 4. Provenance and tokens: pass with evidentiary corrections

Offline tokenization from the recorded local snapshot reproduces every planned rendered count. All 104 HTTP responses, including invalid outputs, report exactly that count: 83 document responses and 21 probe responses. The pilot probe is **165 locally rendered and 165 reported**, not 161 versus 165 as recorded in the pilot/probe reviews and RUN-SPEC section 7. The largest document is 242,155 in both.

Equality is consistent with compatible chat rendering and accounting. It does not prove that no server-side transformation occurred, that the schema was never processed internally, or that the model attended to every document. `transforms: []` and sufficient context are useful controls, not an attention measurement. JSON schema was requested, but the malformed probe proves output conformity was not guaranteed.

All responses identify the authorized model and DeepInfra and have generation IDs. **Only 103/104 ledger reconciliations contain generation-detail costs and native token counts.** `probe-X03#a1` has `generation_total_cost`, `native_prompt_tokens` and `native_completion_tokens` null; it was reconciled from its response cost, $0.00010248, alone. The other 103 saved generation costs agree with response usage costs. Full generation-detail HTTP payloads were not archived, so their extraction can be checked against the ledger but not independently reread from raw generation responses. The served fp8 weight revision is the host's identity claim, not an independently verified weight hash.

## 5. Output validity and use of evidence: machine validity passes; substantive reliability fails

Four document attempts end at 8,192 tokens. They are Gap current r2, PVH current r3, Qurate saved r3 retry, and Target current r1. Gap, PVH and Qurate loop inside `direct_rationale`; Target has passed that field and loops later in qualitative rationale. Inputs range from 129,192 to 242,155 tokens. All four lie within context; the failure is repetitive generation, not evidence that the input was truncated. Three corresponding first-attempt loops recover on identical-body retries. The precise cause of the degeneration is not established.

Walmart's initial probe returns 64 completion tokens and `finish_reason: stop`, but terminates inside `claimed_recent_rating_actions`. It is invalid JSON despite the requested strict schema. Rejecting it was correct. Valid document responses use 441 to 1,029 completion tokens, median 607.

The five current-input action-field contradictions are X06 r1/r3 and X07 r3 (say upgrade, return the prior); X15 r2 (says upgrade, returns B1 instead of prior Ba3); X15 r3 (says upgrade, returns prior Ba3). Derive actions from ordinal predictions and the recorded prior, not `vs_last_known`.

**Signet's problem is broader than the one undefined channel.** Saved r2 returns zero debt and zero interest, so its scorecard is correctly undefined and direct Ba3 retained. Current r3 also returns zero debt and remains computationally valid because interest is 4. The source 10-K explicitly shows $1,217.3 million of operating-lease liabilities, and its own adjusted debt is the same amount. Four other responses include it. Moreover, $4.0 million is **net interest income**, not verified gross interest expense. Repeated use of +4 is not extraction correctness. Returning zero or taking the magnitude of net income does not resolve the required denominator.

**Nike's interest is also a semantic error, not just numeric variability.** Its filing reports (50) under net interest income/expense; two current responses use +50 as interest, while the third uses 323, which the cash-flow statement identifies as cash interest paid, net of capitalized interest. Neither can silently be called the methodology's verified adjusted interest expense. Saved r1/r3 use pretax income 3,900 as operating income instead of EBIT 3,850. Current r1 gives all four qualitative grades Aaa and produces Aa2 despite the target A2 and stated deterioration. This warrants a source-definition audit and rubric evidence, not an assertion that arithmetic itself is biased.

Fiscal-year naming differences often describe the same period, but they are not all harmless formatting: Gap current r3 says `2025-01-31` while its 15,366 revenue and 1,115 operating income are from the FY2025 column ending January 31, **2026**. Require an ISO fiscal-end field validated against cited inputs. USD-million scale is consistent in the inspected numeric examples, but all 790 figure values have not been independently certified for accounting meaning, sign and period.

There is observable use of quarterly material: Qurate cites June 2026 cash, and Target saved r1 discusses the quarterly tariff-refund improvement. Some responses only use annual commentary. Nike says subsequent quarters show no material changes although its selected package has only a 10-K. The experiment does not measure comprehensive 10-Q utilization or factual support. Generated mentions alone are not verified citations.

## 6. Probe and pilot reviews: reasonable retention decisions; overstated quality checks

All 20 probes have timely reviews before documents. Nineteen valid probes give no rating; Bath & Body Works gives Baa3 with low confidence and explicitly calls its values fabricated. Its claimed June 2025 action is not a verified post-bound recall. Flagging invented action text, retaining the issuer and avoiding a clean-memory certificate were appropriate. Probing the contemporary EDGAR name "Old QVC Group" rather than all historical aliases limits sensitivity; a negative answer cannot clear memory contamination.

The pilot was the largest document body, with a valid completed probe and a review before rollout. Passing transport, schema, cap and period plausibility was defensible as permission to measure a flawed analyst. It was not an analyst-quality pass. Its claim that Qurate had successfully emerged from bankruptcy is unsupported by the supplied August 4 filing, which says the confirmed plan still has conditions outstanding and emergence is uncertain. Keep this failure and do not retry it for quality. The review's "nine of ten figures identical" is also contradicted by its own three listed differences: debt, dividends and working-capital swing leave seven of ten, not nine. Its "no figure invented" conclusion was too strong without a complete definition/source check. The 161-token assertion is wrong as noted above.

The free gate file is timestamped before the first dispatch and the original 40-test suite passes again. Ten Experiment 03 regressions also pass. The redaction test merely confirms that removed long lines stayed removed; it cannot detect the remaining table cells. The pilot did not inspect Kohl's. This explains how a passed gate suite and a genuine leak coexist.

## 7. Interpretation and reading rules: pass only after correction

The accurate narrow finding is that neither recorded output channel beats persistence. On all 60 current responses, direct ratings equal the prior **56 times**; all three equal the prior on **18/20 issuers**, not 19. Dollar General upgrades in all three, and Signet downgrades in r2. Separately, direct predictions have zero replicate spread on 19/20. The consensus does equal persistence except Dollar General, but the replicate claim is different.

The current scorecard is better than the label in 36 responses, equal in nine and worse in 15, with mean signed error 74/60 = 1.2333 notches in the issuer's favour. Relative to persistence, the counts are 32 better, 11 equal and 17 worse. These are measured properties of these inputs, including a known leak. They do not prove a defect in the deterministic arithmetic or establish which missing adjustments caused the gap. Calibration uses a quantitative-only approximation, not the same model-extracted qualitative pipeline; the analogy is descriptive.

| Input field | Issuers with identical values/grades in all three current replicates |
|---|---|
| Revenue / operating income / D&A / dividends | 18 / 18 / 18 / 18 |
| Cash / CFO | 17 / 17 |
| Capex / interest | 16 / 16 |
| Debt / working-capital swing | 13 / 6 |
| Market Characteristics / Market Position | 13 / 13 |
| Revenue and Earnings Stability / Financial Policy | 11 / 10 |

All four qualitative grades agree jointly on only 8/20 issuers. The brief's nine figures stable on 15 to 18 issuers is wrong because debt is stable on only 13. Consistency does not establish independent extraction when reference XBRL rows are already supplied.

The saved comparison supports **equal aggregate direct metrics in Qwen replicates 1 and 2 and the one Opus response**, not equal predictions or equivalent models. Qwen r1 predicts Signet Ba2 and Qurate Caa1, whereas Opus predicts Ba1 and Ca. Different mistakes offset in the aggregate. Qwen r2 makes a Victoria's Secret false alarm instead of the Signet false alarm. Without X14, Qwen direct MAE is 2/6 versus Opus 3/6. Qwen's scorecard is worse in r1 but r2 and consensus have different coverage; Opus has no replicate-based stability estimate.

Do not claim identical inference settings: provider, quantization, reasoning, schema mechanism, context handling and sampling differ. Do not claim "2% of the cost" without a specified matched denominator and actual per-call costs. The selected Qwen token prices were 3.6% of Opus's documented batch input price and 4.4% of its batch output price; total experiment costs buy different sets of calls. The measured $1.24 run is sufficient to explain the affordability gain.

Anchoring is a plausible hypothesis, not a demonstrated mechanism without an otherwise matched prior-withheld control. The six-case Experiment 01 direct result equalling persistence is not proof that history caused the later inertia; its variant labels and information sets need care. A few changed cases can show a descriptive advantage, but cannot establish general superiority or a reliable change policy. Replace "none could be shown to" with the actual descriptive finding and uncertainty.

R1 remains appropriate. R2 must preserve the original 19 and 20 denominators while separately labelling the post-hoc 18. R3 remains essential. R4 needs the redaction incident, corrected MAE, 103/104 provenance qualification and the replicate-specific Opus comparison. R5 remains in force: no additional paid work authorized. The "what is not claimed" list should add successful redaction for every current input and guaranteed semantic correctness of extracted figures.

## 8. Robert's decisions: mostly sound; execution claims need narrowing

D5, the authorization-wide $3 cap, was the right control; observed spending complied, but the implementation needs the settlement repairs above. D6, DeepInfra with ceilings and no fallback, was a defensible alternative to relying on GMICloud's promotion. This run tests that deployment, not the best possible Qwen implementation. D7, three frozen-body replicates, usefully exposed instability; a seed did not make the host bit-reproducible. D8, excluding Qurate from the primary interpretation before execution while retaining its diagnostic outputs, was sound. It does not certify the other labels. The X07 sensitivity is a new audit finding, not a retroactive D8 expansion.

D9, deterministic oldest-quarter trimming only when necessary, was appropriate and correctly executed; state the resulting information loss. D10 correctly defers another model. **D11 remains open**, not an executed decision: Arm 2 requires separate target, cutoff, label and budget decisions. D12 correctly separates repaired current inputs from saved matched inputs. Calling the whole experiment "only the model changes" is inaccurate outside that saved information comparison and still omits differing inference settings within it.

The 24-month peer rule is explicit, reproducible and preferable to unlimited age. It is an initial policy, not an empirically established optimal age; report stale and excluded peers and do not assume both arms use the same peer pool. The ten pooled retries were a defensible fixed cost limit, although late requests consequently receive less recovery opportunity. Report this order-dependent missingness.

A public release date is an upper information bound for the identified released weights, not a vendor-stated training cutoff, nor proof of the hosted weights' identity. Arm 1 first was a reasonable affordable control against the existing Opus work. It is not the experiment that can validate a change detector with one usable primary change. The next step should address evidence and target contracts before buying another model comparison.

## 9. Validity verdict and exact editorial corrections

Retain this as an auditable post-release, history-conditioned **disclosure-label pilot with a discovered redaction violation**. Retain the seven-case matched-information comparison with failure/selection qualifications. Do not certify a clean 19-case outstanding-rating benchmark, causal anchoring, model equivalence, extraction accuracy, or a production-ready runner. A future clean run would need newly frozen validated inputs and fresh authorization; this review neither requests nor performs it.

Numbered corrections to apply before sharing `results.md` and `RUN-SPEC.md`:

1. Replace the opening claim of measuring outstanding ratings at t with measurement against accepted disclosed labels whose validity at t is unverified.
2. Disclose the X07 B2/outlook table leak, mark the original 19-issuer result as affected, and add the post-hoc 18-issuer sensitivity without altering the frozen cohort or records.
3. Replace primary judgement MAE 0.10 with 2/19 = 0.105263, rounded once to 0.11, including replicates 1 and 3, consensus and R4.
4. Replace "all three returned the prior on 19/20" with 18/20 and record Signet r2 as the second exception alongside Dollar General.
5. Report 56/60 direct ratings equal to the prior and the five action-field contradictions instead of using the 52 textual unchanged declarations as an action count.
6. Add the matched valid-subset persistence baselines for incomplete saved-arm channels and distinguish complete-three replicate spread from partial observed spread.
7. Replace universal generation-record agreement with 103 confirmed pairs and one response-only reconciliation, `probe-X03#a1`, and disclose that full generation-detail responses were not archived.
8. Correct the pilot probe count to 165 locally rendered and 165 reported, and replace claims of proved absence of compression/schema injection with the observed accounting equality.
9. Describe strict schema as requested rather than guaranteed, given the invalid Walmart probe and four length failures.
10. Correct TLS timing to 0.028 to 0.155 seconds and describe six transport retries, three length retries and one malformed-probe retry.
11. Add the $1.388231 maximum exposure during replay, keep unresolved reservations counted, and avoid inferring individual non-billing from aggregate account readings.
12. Qualify guard and all-gates claims with the demonstrated error-response release and overcharge-without-halt defects, plus the absence of a halt on parser-invalid JSON.
13. Add Signet's current-r3 zero-debt error, net-interest semantic errors for Signet and Nike, Nike's saved pretax-income substitution, and Gap's incorrect ISO fiscal-end date.
14. Correct the pilot's nine-of-ten agreement to seven-of-ten given its three named differences, and describe its bankruptcy-emergence statement as unsupported by the supplied filing.
15. Limit the Opus comparison to matched supplied information and specified Qwen replicates, remove equivalence and unspecified 2%-cost claims, and present anchoring and missing-adjustment explanations as hypotheses.
16. Keep D11 open and clarify that current and saved arms differ in pack/peer policy and trimming, so only the saved arm provides the matched-information comparison.

The same headline corrections are needed in the root README, HANDOVER's older current-result paragraph, the external brief and email. The original calibration note also still contains superseded 1,696-row/gold-independence claims; use the corrected 1,665-row integrity review. These documents were not silently rewritten in this audit.

## Verification boundaries

The 40 Experiment 04 tests and ten Experiment 03 regressions pass. The two additional fake billing cases fail as described. All seven legacy proofs and all 20 current pack reconstructions pass. Offline tokenizer counts and every frozen source-hash group match. Independent source inspections establish the X07 disclosure leak and the cited output errors; they do not certify every extracted value or all possible semantic leakage.

`score` and `report.py` were not run against the original directory because they write result files despite being listed as free commands. Reproduction used in-memory calculations and scratch files instead. All 304 protected paid/frozen artifacts hashed before review have the same SHA-256 values afterwards. No changes to them were needed to find or report these defects.

## Appendix: independently reconstructed tables

Exact and within-one entries are integer counts; MAE is shown as the exact notch-error sum divided by the valid count, so no rounding enters verification. Missing responses are excluded only from conditional metrics. Their planned denominator remains visible. In each block persistence is defined on the stated full cohort; conditional baselines are in the following table.

### Current, all 20

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 20/20 | 17/20 | 19/20 | 4/20 | 0/2 | 0 | 1/18 |
| Scorecard | 1 | 20/20 | 2/20 | 13/20 | 34/20 | 0/2 | 1 | 16/18 |
| Judgement | 2 | 20/20 | 16/20 | 19/20 | 5/20 | 0/2 | 0 | 2/18 |
| Scorecard | 2 | 20/20 | 5/20 | 10/20 | 34/20 | 0/2 | 0 | 13/18 |
| Judgement | 3 | 20/20 | 17/20 | 19/20 | 4/20 | 0/2 | 0 | 1/18 |
| Scorecard | 3 | 20/20 | 2/20 | 11/20 | 42/20 | 0/2 | 1 | 16/18 |
| Judgement | consensus | 20/20 | 17/20 | 19/20 | 4/20 | 0/2 | 0 | 1/18 |
| Scorecard | consensus | 20/20 | 3/20 | 11/20 | 36/20 | 0/2 | 1 | 15/18 |
| Persistence | consensus | 20/20 | 18/20 | 19/20 | 3/20 | 0/2 | 0 | 0/18 |

### Current, original 19

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 19/19 | 17/19 | 19/19 | 2/19 | 0/1 | 0 | 1/18 |
| Scorecard | 1 | 19/19 | 2/19 | 12/19 | 33/19 | 0/1 | 0 | 16/18 |
| Judgement | 2 | 19/19 | 16/19 | 19/19 | 3/19 | 0/1 | 0 | 2/18 |
| Scorecard | 2 | 19/19 | 5/19 | 10/19 | 32/19 | 0/1 | 0 | 13/18 |
| Judgement | 3 | 19/19 | 17/19 | 19/19 | 2/19 | 0/1 | 0 | 1/18 |
| Scorecard | 3 | 19/19 | 2/19 | 10/19 | 41/19 | 0/1 | 0 | 16/18 |
| Judgement | consensus | 19/19 | 17/19 | 19/19 | 2/19 | 0/1 | 0 | 1/18 |
| Scorecard | consensus | 19/19 | 3/19 | 10/19 | 35/19 | 0/1 | 0 | 15/18 |
| Persistence | consensus | 19/19 | 18/19 | 19/19 | 1/19 | 0/1 | 0 | 0/18 |

### Saved, seven

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 7/7 | 4/7 | 6/7 | 4/7 | 0/2 | 0 | 1/5 |
| Scorecard | 1 | 7/7 | 2/7 | 5/7 | 13/7 | 0/2 | 2 | 3/5 |
| Judgement | 2 | 7/7 | 4/7 | 6/7 | 4/7 | 0/2 | 0 | 1/5 |
| Scorecard | 2 | 6/7 | 2/7 | 4/6 | 6/6 | 0/2 | 1 | 2/4 |
| Judgement | 3 | 5/7 | 3/7 | 5/5 | 2/5 | 0/1 | 0 | 1/4 |
| Scorecard | 3 | 5/7 | 0/7 | 4/5 | 9/5 | 0/1 | 1 | 4/4 |
| Judgement | consensus | 5/7 | 3/7 | 5/5 | 2/5 | 0/1 | 0 | 1/4 |
| Scorecard | consensus | 4/7 | 1/7 | 4/4 | 3/4 | 0/1 | 1 | 2/3 |
| Persistence | consensus | 7/7 | 5/7 | 6/7 | 3/7 | 0/2 | 0 | 0/5 |

### Saved, six without X14

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 6/6 | 4/6 | 6/6 | 2/6 | 0/1 | 0 | 1/5 |
| Scorecard | 1 | 6/6 | 2/6 | 4/6 | 12/6 | 0/1 | 1 | 3/5 |
| Judgement | 2 | 6/6 | 4/6 | 6/6 | 2/6 | 0/1 | 0 | 1/5 |
| Scorecard | 2 | 5/6 | 2/6 | 4/5 | 4/5 | 0/1 | 1 | 2/4 |
| Judgement | 3 | 5/6 | 3/6 | 5/5 | 2/5 | 0/1 | 0 | 1/4 |
| Scorecard | 3 | 5/6 | 0/6 | 4/5 | 9/5 | 0/1 | 1 | 4/4 |
| Judgement | consensus | 5/6 | 3/6 | 5/5 | 2/5 | 0/1 | 0 | 1/4 |
| Scorecard | consensus | 4/6 | 1/6 | 4/4 | 3/4 | 0/1 | 1 | 2/3 |
| Persistence | consensus | 6/6 | 5/6 | 6/6 | 1/6 | 0/1 | 0 | 0/5 |

### Current, post-hoc 18 without X07 and X14

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 18/18 | 16/18 | 18/18 | 2/18 | 0/1 | 0 | 1/17 |
| Scorecard | 1 | 18/18 | 2/18 | 12/18 | 29/18 | 0/1 | 0 | 15/17 |
| Judgement | 2 | 18/18 | 15/18 | 18/18 | 3/18 | 0/1 | 0 | 2/17 |
| Scorecard | 2 | 18/18 | 5/18 | 10/18 | 29/18 | 0/1 | 0 | 12/17 |
| Judgement | 3 | 18/18 | 16/18 | 18/18 | 2/18 | 0/1 | 0 | 1/17 |
| Scorecard | 3 | 18/18 | 2/18 | 10/18 | 38/18 | 0/1 | 0 | 15/17 |
| Judgement | consensus | 18/18 | 16/18 | 18/18 | 2/18 | 0/1 | 0 | 1/17 |
| Scorecard | consensus | 18/18 | 3/18 | 10/18 | 32/18 | 0/1 | 0 | 14/17 |
| Persistence | consensus | 18/18 | 17/18 | 18/18 | 1/18 | 0/1 | 0 | 0/17 |

### Opus, corrected seven

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 7/7 | 4/7 | 6/7 | 4/7 | 0/2 | 1 | 1/5 |
| Scorecard | 1 | 7/7 | 3/7 | 6/7 | 8/7 | 1/2 | 2 | 3/5 |
| Persistence | 1 | 7/7 | 5/7 | 6/7 | 3/7 | 0/2 | 0 | 0/5 |

### Opus, corrected six

| Channel | Replicate | Valid/planned | Exact/planned | Within one/valid | MAE | Changed exact/valid | Correct direction | False alarms/unchanged |
|---|---|---|---|---|---|---|---|---|
| Judgement | 1 | 6/6 | 4/6 | 5/6 | 3/6 | 0/1 | 0 | 1/5 |
| Scorecard | 1 | 6/6 | 3/6 | 5/6 | 7/6 | 1/1 | 1 | 3/5 |
| Persistence | 1 | 6/6 | 5/6 | 6/6 | 1/6 | 0/1 | 0 | 0/5 |

### Matched persistence for incomplete saved channels

| Cohort | Channel / replicate | Valid n | Model exact / MAE | Persistence exact / MAE, same valid issuers |
|---|---|---|---|---|
| 7 | scorecard / 2 | 6 | 2/6 / 6/6 | 4/6 / 3/6 |
| 6 | scorecard / 2 | 5 | 2/5 / 4/5 | 4/5 / 1/5 |
| 7 | direct / 3 | 5 | 3/5 / 2/5 | 4/5 / 1/5 |
| 7 | scorecard / 3 | 5 | 0/5 / 9/5 | 4/5 / 1/5 |
| 6 | direct / 3 | 5 | 3/5 / 2/5 | 4/5 / 1/5 |
| 6 | scorecard / 3 | 5 | 0/5 / 9/5 | 4/5 / 1/5 |
| 7 | direct / consensus | 5 | 3/5 / 2/5 | 4/5 / 1/5 |
| 7 | scorecard / consensus | 4 | 1/4 / 3/4 | 3/4 / 1/4 |
| 6 | direct / consensus | 5 | 3/5 / 2/5 | 4/5 / 1/5 |
| 6 | scorecard / consensus | 4 | 1/4 / 3/4 | 3/4 / 1/4 |

### Per-issuer reconstruction

Consensus is the middle ordinal rating only when all three channel predictions exist. A dash remains missing; it is not persistence. Original fiscal-year strings remain visible in the original tables and their semantic problems are discussed above.

| Arm | ID | Prior | Label | Scorecard r1 / r2 / r3 | Judgement r1 / r2 / r3 |
|---|---|---|---|---|---|
| current | X01 | Ba2 | Ba2 | Ba2 / Ba2 / Ba1 | Ba2 / Ba2 / Ba2 |
| current | X02 | A3 | A3 | A3 / A3 / A3 | A3 / A3 / A3 |
| current | X03 | Baa2 | Baa2 | Baa3 / Baa3 / Baa3 | Baa2 / Baa2 / Baa2 |
| current | X04 | Baa3 | Baa3 | A3 / Baa1 / A3 | Baa2 / Baa2 / Baa2 |
| current | X05 | Ba3 | Ba3 | Baa3 / Baa3 / Baa3 | Ba3 / Ba3 / Ba3 |
| current | X06 | Ba2 | Ba2 | Baa3 / Baa2 / Baa3 | Ba2 / Ba2 / Ba2 |
| current | X07 | B2 | B2 | Ba1 / Ba2 / Ba2 | B2 / B2 / B2 |
| current | X08 | Caa3 | Caa3 | Caa2 / Caa3 / B3 | Caa3 / Caa3 / Caa3 |
| current | X09 | Ba1 | Ba1 | Baa3 / A2 / A2 | Ba1 / Ba1 / Ba1 |
| current | X10 | Baa1 | Baa1 | Baa2 / Baa2 / Baa2 | Baa1 / Baa1 / Baa1 |
| current | X11 | Ba1 | Ba1 | Baa3 / Baa3 / Baa3 | Ba1 / Ba1 / Ba1 |
| current | X12 | A1 | A2 | Aa2 / Aa3 / A1 | A1 / A1 / A1 |
| current | X13 | Baa3 | Baa3 | Ba2 / Ba2 / Ba2 | Baa3 / Baa3 / Baa3 |
| current | X14 | Caa1 | Caa3 | Caa2 / Caa1 / Caa2 | Caa1 / Caa1 / Caa1 |
| current | X15 | Ba3 | Ba3 | A3 / Baa1 / Aa2 | Ba3 / B1 / Ba3 |
| current | X16 | A2 | A2 | A1 / Aa3 / Aa3 | A2 / A2 / A2 |
| current | X17 | Baa1 | Baa1 | Baa2 / Baa1 / Baa1 | Baa1 / Baa1 / Baa1 |
| current | X18 | Ba2 | Ba2 | Ba1 / Ba1 / Ba1 | Ba2 / Ba2 / Ba2 |
| current | X19 | Ba3 | Ba3 | B1 / B1 / B1 | Ba3 / Ba3 / Ba3 |
| current | X20 | Aa2 | Aa2 | Aa3 / Aa2 / Aa3 | Aa2 / Aa2 / Aa2 |
| saved | X12 | A1 | A2 | A3 / A3 / A3 | A1 / A1 / A1 |
| saved | X14 | Caa1 | Caa3 | Caa2 / Caa1 / missing | Caa1 / Caa1 / missing |
| saved | X15 | Ba3 | Ba3 | A1 / missing / Baa1 | Ba2 / Ba3 / Ba2 |
| saved | X16 | A2 | A2 | A2 / A1 / A1 | A2 / A2 / A2 |
| saved | X17 | Baa1 | Baa1 | Baa2 / Baa1 / Baa2 | Baa1 / Baa1 / Baa1 |
| saved | X19 | Ba3 | Ba3 | Ba1 / Ba1 / missing | Ba3 / Ba2 / missing |
| saved | X20 | Aa2 | Aa2 | Aa2 / Aa2 / Aa3 | Aa2 / Aa2 / Aa2 |

### Spread, requiring three valid predictions

| Arm / channel | Spread 0 | Spread 1 | Spread >1 | Incomplete |
|---|---|---|---|---|
| current / direct | 19 | 1 | 0 | 0 |
| current / scorecard | 8 | 8 | 4 | 0 |
| saved / direct | 4 | 1 | 0 | 2 |
| saved / scorecard | 1 | 3 | 0 | 3 |

The original saved spread counts also reproduce when using only available responses: scorecard 2 at zero, 4 at one and 1 above one; judgement 5 at zero and 2 at one. Those are partial observed spreads, not seven complete three-replicate measurements. Joint qualitative agreement is 8/20 current and 2/7 saved.
