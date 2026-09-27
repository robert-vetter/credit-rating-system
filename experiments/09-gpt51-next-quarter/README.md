# Experiment 09: GPT-5.1 predicting next quarter's rating change after its cutoff, specification

*Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter. Version 0.2 (decisions of 2026-09-27, section 15); 0.1 was the draft. Follows [EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Built on Robert's decisions
of 2026-09-27 (GPT-5.1, all company-quarters of the 2025 window) and the Experiment 08 results.
Checked against: the OpenAI model page for GPT-5.1 and the Batch API guide (read 2026-09-27, not
yet snapshotted), Experiment 08 run R1 (`predictions.json`, window rows), Experiment 07 run R2
(labels), and the SEC filing manifests under `evaluation/companies/*/filings/manifest.json`. No
request has been sent and nothing has been spent.*

State: decisions taken 2026-09-27 (`decisions.md` 2 to 6); implementation. Section 15 lists what changed from 0.1.

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | Given a company's SEC filings and its Moody's rating history up to a quarter end, can GPT-5.1 rank which companies will be downgraded or upgraded in the next quarter better than the rating level alone, on rating actions after its training cutoff? |
| Null hypothesis | GPT-5.1 does not beat M1 (the rating-level model of Experiment 08) on the area under the precision-recall curve for "any change" |
| Secondary questions | direction on real changes against M1 and M3; downgrades ranked on their own against M3; calibration of the probabilities; stability across replicates; what the model cites as reasons |
| Target | P(down), P(unchanged), P(up) for the next calendar quarter (flight notes, file 02, option B) |
| Unit | company-quarter |
| What it is | the first out-of-sample LLM test on the question that now matters, on official Moody's labels dated to the day; a pilot, because the window holds about 11 changes |
| What it is not | a test of the outstanding rating level (Experiments 03 and 04); a test on the newest models; a trading strategy |
| Place in the programme | decipher: whether text in filings carries information the numbers do not (Experiment 08 showed the numbers tell direction, not whether). Also answers Xiaowei's point 3 with a widely used commercial model |

## 2. Dates

| Date concept | Value | Source |
|---|---|---|
| Model | `gpt-5.1-2025-11-13` (default snapshot of `gpt-5.1`) | OpenAI model page, read 2026-09-27 |
| Knowledge cutoff | 2024-09-30 | same page; snapshot to be saved under `evidence/` (pre-check P11) |
| Boundary B | 2024-10-31 (end of the month after the cutoff month) | experiment policy |
| Prediction dates t | 2024-12-31 and 2025-03-31 | both after B |
| Outcome quarters | 2025-01-01 to 2025-03-31, and 2025-04-01 to 2025-06-30 | Experiment 07 grid |
| Filings used | 10-K and 10-Q filed on or before t | point in time |
| Rating history supplied | Moody's actions on or before t | 17g-7 files dated 2026-08-11 |
| Labels | the Experiment 07 run R2 quarterly labels (official, actions dated to the day) | Experiment 07 |
| Rating actions after the grid (July and August 2025) | not used; they fall outside both outcome quarters | |

Everything the model reads is dated on or before t. Some of it (a 10-K filed in early 2024) is
older than the cutoff and may be in the training data; that is allowed. The outcomes, all in 2025,
are after the cutoff.

## 3. Sample and data characteristics

### 3.1 How the sample is built

| Step | Count |
|---|---|
| Company-quarters in the window (Experiment 08, `experiment_09_window`) | 147 (74 companies; 74 at 2024-12-31, 73 at 2025-03-31) |
| Changes in the window | 12 (10 downgrades, 2 upgrades) |
| Eligible: a 10-K filed within 450 days before t, so the model has current filings to read | **118 company-quarters, 11 changes** (9 downgrades, 2 upgrades) |
| Not eligible | 29: no current 10-K. Foreign filers without 10-K (Amer Sports, Canada Goose, Cencosud, JD.com, Vipshop); companies that stopped filing (7-Eleven 2005, Ahold 2007, PetSmart 2014, Staples 2017, Whole Foods 2017, Tiffany 2020, Men's Wearhouse 2020, Michaels 2021); two withdrawn-rating companies without a filing manifest yet (At Home, Rite Aid, 3 rows), to be checked |
| Change lost by the eligibility rule | PetSmart, downgraded in the first quarter of 2025, last 10-K filed 2014 |
| Gold observations in the window | 4; kept (nothing is fitted); reported with and without |

Robert asked for all 147. A filings-reading test can only run where filings exist, so the primary
cohort is the 118 eligible rows (DECISION 1). The 29 others can be run with the rating history
alone, as a secondary arm.

### 3.2 The 11 changes in the eligible cohort

| Company | Prediction date | Rating at t | Move next quarter |
|---|---|---|---|
| Carvana | 2024-12-31 | Caa1 | up |
| Dollar General | 2024-12-31 | Baa2 | down |
| Foot Locker | 2024-12-31 | Ba2 | down |
| Gap | 2024-12-31 | Ba3 | up |
| Kohl's | 2024-12-31 | Ba2 | down |
| Kohl's | 2025-03-31 | Ba3 | down |
| Leslie's | 2024-12-31 | B2 | down |
| Qurate/QVC | 2025-03-31 | B3 | down |
| RH | 2025-03-31 | B1 | down |
| Under Armour | 2025-03-31 | Ba2 | down |
| V.F. | 2025-03-31 | Ba1 | down |

### 3.3 Imbalance plan

Natural rate kept (11 in 118, 9.3%); no resampling. Ranking measures do not depend on a threshold.
With 11 changes the result is a pilot: an interval on the difference to M1 will be wide, and a
single company can move the result. That is stated in advance.

### 3.4 Input characteristics, known before the run

| Characteristic | Value |
|---|---|
| Documents per eligible row | 10-K plus the 10-Qs filed after it and on or before t: 4 documents for 58 rows, 3 for 8, 2 for 8, 1 for 44 |
| Documents cached locally | most 2024 and early 2025 filings are not cached (earlier experiments downloaded other dates); a free EDGAR download is needed (DECISION 7) |
| Request size | not yet counted; Experiment 04 packages of 10-K plus 10-Qs were 93,000 to 286,000 tokens with the Qwen tokenizer, median 156,000. GPT-5.1's context is 400,000 |
| Excluded | 8-Ks, exhibits, press releases, peer ratings, any tool or retrieval |

## 4. Per-observation table

Produced by the run: for each of the 118 rows, the filings supplied (form, period end, filing
date), the rating at t with its type, the label and the action day, GPT-5.1's three probabilities
per replicate, and M1 to M4's probabilities from Experiment 08.

## 5. Models and settings

| Setting | Value |
|---|---|
| Model | `gpt-5.1-2025-11-13`, OpenAI API, pinned snapshot |
| Endpoint | Batch API over the Responses endpoint (50% discount, completion within 24 hours), DECISION 3 |
| Reasoning effort | medium (DECISION 2); the vendor default is "none" |
| Temperature | not set; the vendor page does not document it for this model. Recorded as sent |
| Structured output | JSON schema, strict |
| Output ceiling | set from the pre-flight so that no answer is cut off (Experiment 03 lost 11 of 16 answers to a ceiling) |
| Replicates | 3 per company-quarter |
| Consensus | mean of the valid replicates' probabilities; stability reported as the spread of P(change) across replicates |
| Tools, retrieval, web search | none |
| Memory probe | one per company before any document request (section 10, P12) |
| Compared with | M0 to M4 of Experiment 08 on the same rows, from `experiments/08-next-quarter-baselines/runs/R1-2026-09-27/predictions.json` |

## 6. Inputs to the model

| Input | Content | Rule |
|---|---|---|
| As-of line | "As-of date: YYYY-MM-DD" (t) | nothing later appears anywhere |
| The rating to predict | its current level at t and its type (corporate family rating or senior unsecured, as the label rule selects it) | from the Experiment 07 labels |
| Rating history | Moody's actions on the company up to t: date, rating, action, rating type | 17g-7 file, dated on or before t |
| Filings | the latest 10-K filed on or before t and every 10-Q filed after it and on or before t, as text | redacted of rating self-disclosures (`system/redact.py`, structural second pass and scan), DECISION 6 |
| Not given | numbers computed by us (no XBRL table), base rates, other companies' ratings, the sector cycle | the model reads the filings itself; see DECISION 5 on base rates |

If a package exceeds the context after the output reservation, the oldest 10-Q is dropped, as in
Experiment 04, and the drop is recorded.

## 7. Prompt and output

The verbatim prompts are written into `prompts/` after the decisions and before the pre-checks.
They will contain:

| Part | Content |
|---|---|
| System | the role of a credit analyst following Moody's Retail and Apparel methodology; answer only from the supplied documents and history; do not use knowledge of events after the as-of date |
| Task | for the named rating, the probability that Moody's downgrades it, leaves it unchanged, or upgrades it between the day after the as-of date and the end of the next calendar quarter |
| Output schema | `p_down`, `p_unchanged`, `p_up` (each 0 to 1, summing to 1 within 0.01); `most_likely_rating_at_quarter_end`; `size_if_change` (notches); up to three `reasons`, each with a verbatim `quote` and its document; `insufficient_information` (true or false) |
| Memory probe | separate request, no documents: what the model recalls about the company's Moody's ratings and any rating action from October 2024 on |

Quotes are checked offline against the supplied text; a reason whose quote is not found is
reported as unsupported.

## 8. The calculation

No scorecard arithmetic is used. The metrics are computed in code from the saved answers.

## 9. Metrics and baselines

Fixed before the run.

| Item | Rule |
|---|---|
| Primary | area under the precision-recall curve for "any change" (rank by P(down) + P(up)), GPT-5.1 consensus against M1, on the 118 eligible rows; company-block bootstrap (2,000) interval of the difference |
| Secondary 1 | direction correct on real changes (P(down) > P(up) matches the move), against M1 and M3 |
| Secondary 2 | downgrades ranked on their own by P(down), PR area, against M1 and M3 (9 downgrades). Upgrades (2) are listed, not scored |
| Secondary 3 | Brier score and log loss; calibration table by fifth of P(change) |
| Secondary 4 | precision and recall among the top 5% and 10% |
| Stability | per row, the range of P(change) across the three replicates; share of rows where all three agree on the most likely outcome |
| Reasons | share of reasons with a verified quote; the reasons given for the 11 changes, listed in full |
| Missing answers | stay missing; metrics on answered rows with M-models on the same rows; the count is reported |
| Memory | any probe that states a rating action from October 2024 on is flagged, and the row is reported with and without the flagged companies |
| Sensitivities | without gold rows; each prediction date separately; the 29 ineligible rows with rating history only (if run) |

## 10. Controls and pre-checks

| # | Check | Applies? |
|---|---|---|
| P1 | Specification reviewed by the other model family | yes, unless Robert waives it (DECISION 9) |
| P2 | Chair consensus or Robert's written decision to proceed | yes (DECISION 9) |
| P3 | Authorization: cap approved by Robert, bound to the manifest hash; the runner refuses without it | yes |
| P4 | Cohort frozen: the 118 (or chosen) rows by ID | yes |
| P5 | Inputs frozen: hashes of every document, history, prompt, schema and request body | yes |
| P6 | Point-in-time audit: every document filed on or before t, every history event on or before t | yes |
| P7 | Redaction scan of every assembled request finds no rating fragment (if DECISION 6 keeps redaction) | yes |
| P8 | No tools, no web search in any request | yes |
| P9 | Every request fits 400,000 tokens with the output reserved, counted with OpenAI's published tokenizer (`tiktoken`, o200k_base) | yes; `tiktoken` must be installed |
| P10 | Worst-case price, with retries, under the cap | yes |
| P11 | GPT-5.1 model page saved under `evidence/` with the retrieval date | yes |
| P12 | Memory probe per company, reviewed before its documents are sent | yes |
| P13 | Tests of the runner against a fake transport: no dispatch without authorization, over-cap refusal, schema validation, probabilities that do not sum to 1, truncated answers, a crash and resume | yes |
| P14 | Pilot: the largest request and its probe run first and are inspected for protocol problems before the rest | yes |

The runner reuses the safeguards of Experiment 04 (`run_openrouter.py`): authorization bound to
the manifest hash, a ledger of every reservation and charge, halts on anything unexplained, raw
responses saved before parsing.

## 11. Budget

Estimate before the pre-flight, list prices from the model page:

| Item | Estimate |
|---|---|
| Input per replicate | about 118 requests × 150,000 tokens = 17.7 million tokens, about $22 |
| Output per replicate, including reasoning | about 118 × 5,000 to 10,000 tokens, about $6 to $12 |
| Three replicates | about $85 to $100 at list price; about $45 to $50 with the Batch API discount |
| Probes and pilot | under $1 |
| Proposed cap | set after the exact pre-flight count; likely about $60 with batch, $120 without |

## 12. Known defects and limitations before the run

| Limitation | Effect |
|---|---|
| 11 changes | a pilot; one company can move the result |
| Two of the 11 are upgrades | upgrades cannot be scored separately |
| 29 rows without current filings, including one change (PetSmart) | the filings test covers 118 of 147 rows |
| The model has read much older filings and news about these companies | memory of the companies is unavoidable; the outcomes are after the cutoff, and probes check for recall of them |
| A vendor knowledge cutoff is a statement, not a guarantee | probes; results reported with and without flagged companies |
| Rating outlooks and reviews are removed by redaction (if DECISION 6 keeps it) | the model cannot use a disclosed review for downgrade, which would be legitimate public information at t |
| Qurate's label caveats from Experiments 03 and 04 | the Qurate row is reported with a note |
| The M-model baselines were fitted on the same label source | fair comparison: both use only information up to t |

## 13. Decisions that need consensus before the run

| # | Decision | Options | Proposed | Agreed (who, date) |
|---|---|---|---|---|
| 1 | Cohort | 118 eligible rows; all 147 with the 29 on rating history only | 118 as the primary test; the 29 as a cheap secondary arm with rating history only | |
| 2 | Reasoning effort | none (vendor default); low; medium; high | medium: reasoning helps with long filings; high multiplies output cost | |
| 3 | Endpoint | Batch API (50% off, up to 24 hours); synchronous | batch | |
| 4 | Replicates | 1; 3 | 3 (policy default) | |
| 5 | Base rates in the prompt | none; the historical change rates by rating (from years before t) | none: tests the model as it is; calibration is measured, not supplied | |
| 6 | Redaction of rating disclosures in the filings | redact, as the project rules require; allow, because outlooks and reviews disclosed by t are legitimate information | redact in this experiment, so the comparison with the M-models (which have no outlooks) stays clean; an arm with outlooks later | |
| 7 | Downloads and installation | fetch the 2024 and early 2025 10-K and 10-Q documents from EDGAR (free, several hundred files); fetch filing lists for At Home and Rite Aid; install `tiktoken` for the pre-flight count | all three | |
| 8 | Cap | set after the pre-flight | Robert, after the pre-flight | |
| 9 | Review and consensus | Codex review and chair agreement; Codex review only; waive both | a Codex review of the runner and prompts at least, because this run spends money | |
| 10 | Primary measure | PR area for any change against M1 | as stated; direction and downgrades are secondary because Experiment 08 found the signal there, but with 11 changes they cannot carry the headline | |

## 14. Definitions

| Term | Meaning | Example |
|---|---|---|
| Eligible row | a company-quarter with a 10-K filed within 450 days before the prediction date | Kohl's at 2024-12-31: 10-K filed 2024-03-21 |
| Consensus probability | the mean of the three replicates' probabilities | replicates 0.10, 0.14, 0.12 give 0.12 |
| PR area | area under the precision-recall curve for a ranking; random ranking scores the change rate | 0.093 for 11 changes in 118 rows |
| M1, M3 | Experiment 08's rating-level model and its model with rating history and reported numbers | M1 scored 0.133 on all 147 window rows |

## 15. Changes in version 0.2, 2026-09-27, before any request

| Item | Version 0.1 | Version 0.2 | Decision |
|---|---|---|---|
| Access | OpenAI API | OpenRouter, provider pinned to `openai/flex` (OpenAI's own servers, snapshot `gpt-5.1-20251113`), no fallback | 4, 6 |
| Discount | Batch API, 50% | OpenAI flex tier, 50%: $0.625 input, $5 output per million tokens | 6 |
| Replicates | 3 | 1; stability across replicates is therefore not measured | 3 |
| Consensus | mean of three replicates | the single answer | 3 |
| Cap | after the pre-flight | $50 for now; at the cap the runner stops and progress is reported | 4 |
| Review | Codex review proposed | none; Robert's go stands in for consensus | 5 |
| Budget estimate | $45 to $50 with batch for three replicates | one replicate at the flex price: about $11 input (17.7 million tokens) plus $3 to $6 output, about $15 to $20 in total, exact figure from the pre-flight | |
| Section 9, stability row | range across three replicates | not available; dropped | 3 |
| Redaction | `redact_v2` and the fragment scan | plus a final pass that removes exactly the lines the scan flags (logged per document), then rescans; added after the scan stopped the build on two orphaned "Stable" outlook cells in Best Buy's 2024 10-K. Nothing had been sent | 2 (decision 6 of section 13) |
