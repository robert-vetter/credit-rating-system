# Experiment 09: results

*Written 2026-09-28 by Claude (Opus 5.5), directed by Robert Vetter. Follows section 6 of
[EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Verified against run R3 (`runs/R3/`: manifest
sha256 3008518368df…, authorization EXP09-R3-A1, ledger, raw responses, `results/results.json` and
`results/tables.md` from `score.py`) and the pilot of run R2. Independent review and chair consensus
waived by Robert (decision 5). 25 runner tests pass.*

## 1. Summary

| Item | Answer |
|---|---|
| Question | Can GPT-5.1, reading a company's filings and rating history at a quarter end, rank which ratings Moody's will change in the next quarter better than the rating level alone, on actions after its training cutoff? |
| Primary result | Better on the point estimate, not proven. Ranking score 0.237 against 0.173 for the rating-level model M1 (random: 0.093). The 95% interval of the difference, -0.17 to +0.30, includes zero. The null hypothesis is not rejected; with 11 changes this was expected to be a pilot |
| Against the best Experiment 08 model | about equal to M3, the model with the reported numbers (0.209) |
| Downgrades | 0.238 against 0.110 for M1; interval of the difference +0.03 to +0.38. About equal to M3 (0.255) |
| Direction | right on all 11 changes (M1: 10, M3: 8) |
| Upgrades | the two upgrades (Gap, Carvana) ranked 6th and 12th of 118; the numbers-based models did not rank them highly |
| Probabilities | too high: median P(change) 13% against a realised 9.3%; best Brier score and log loss of all models nonetheless |
| Without filings (29 rows, rating history only) | no better than the rating-level model; the filings are where the signal comes from |
| Memory | none of 74 probes recalled any Moody's action from October 2024 on |
| Cost | $12.43 charged plus $0.19 held for one timed-out request, $12.63 at most including the R2 pilot, of the $50 cap |

## 2. Headline, documents arm

118 company-quarters with current filings, prediction dates 2024-12-31 and 2025-03-31, 11 changes
(9 downgrades, 2 upgrades), base rate 9.3%. M0 to M4 are the Experiment 08 models refitted on
outcomes up to 2024-12-31, on the same rows.

| Model | PR area | ROC area | Top 5% (6 flagged): changes | Top 10% (12 flagged): changes | Direction right | Brier | Log loss |
|---|---|---|---|---|---|---|---|
| **GPT-5.1** | **0.237** | **0.795** | 2 | **4** | **11 of 11** | **0.159** | **0.301** |
| M0 persistence | 0.093 | 0.500 | 0 | 1 | | 0.186 | |
| M1 rating level | 0.173 | 0.688 | 1 | 2 | 10 of 11 | 0.170 | 0.355 |
| M2 + rating history | 0.185 | 0.736 | 1 | 1 | 10 of 11 | 0.168 | 0.336 |
| M3 + reported numbers | 0.209 | 0.741 | 1 | 1 | 8 of 11 | 0.166 | 0.333 |
| M4 flexible trees | 0.199 | 0.790 | 0 | 1 | 9 of 11 | 0.174 | 0.324 |

Differences in PR area, company-block bootstrap (2,000):

| Comparison | 95% interval | Share of resamples above zero |
|---|---|---|
| GPT-5.1 minus M1 (primary) | -0.171 to +0.295 | 77% |
| GPT-5.1 minus M2 | -0.100 to +0.232 | 79% |
| GPT-5.1 minus M3 | -0.076 to +0.219 | 73% |

The direction interval cannot be bootstrapped when every case is right; 11 of 11 against 10 of 11
for M1 is one case.

## 3. Dates

| Date concept | Value |
|---|---|
| Model | `gpt-5.1-2025-11-13`, knowledge cutoff 2024-09-30 (vendor page saved 2026-09-27) |
| Boundary | 2024-10-31 |
| Prediction dates | 2024-12-31 (59 rows, 6 changes), 2025-03-31 (59 rows, 5 changes) |
| Outcome quarters | 2025-01-01 to 2025-03-31 and 2025-04-01 to 2025-06-30 |
| Run | 2026-09-28, all requests at OpenAI's flex tier |

## 4. Input data characteristics

| Characteristic | Value |
|---|---|
| Forecast requests | 118 with filings, 29 with rating history only; 74 memory probes |
| Filings supplied | the latest 10-K and later 10-Qs filed on or before t; 234 downloaded from EDGAR, 82 cached |
| Request size, documents arm | 45,538 to 264,181 input tokens, median about 137,000 |
| Oldest 10-Q dropped to fit OpenAI's 272,000-token input limit | 11 requests, among them Carvana 2024-12-31 (a change) |
| Redaction | `redact_v2`, the fragment scan, and a final pass that removed 16 flagged lines in total; the scan ends empty for every document |
| Tokens charged | 16,696,514 prompt (47,872 cached), 404,940 completion, of which 316,782 reasoning |

## 5. Results in detail

### 5.1 The 11 changes (and PetSmart, history only)

Rank is the position of P(change) among the 118 documents rows (1 = highest).

| Company | Date | Rating | Move | GPT-5.1 down / up | GPT-5.1 rank | M1 down / up | M3 down / up |
|---|---|---|---|---|---|---|---|
| Qurate/QVC | 2025-03-31 | B3 | down | 30% / 1% | 4 | 7.2% / 5.4% | 8.3% / 4.6% |
| Gap | 2024-12-31 | Ba3 | up | 5% / 25% | 6 | 3.1% / 2.9% | 1.9% / 4.8% |
| Leslie's | 2024-12-31 | B2 | down | 25% / 5% | 6 | 7.2% / 5.4% | 21.1% / 2.8% |
| Carvana | 2024-12-31 | Caa1 | up | 8% / 18% | 12 | 8.8% / 9.1% | 3.3% / 7.1% |
| Kohl's | 2025-03-31 | Ba3 | down | 23% / 1% | 21 | 3.1% / 2.9% | 9.5% / 2.3% |
| Kohl's | 2024-12-31 | Ba2 | down | 22% / 1% | 23 | 3.1% / 2.9% | 2.8% / 3.9% |
| RH | 2025-03-31 | B1 | down | 15% / 5% | 29 | 7.2% / 5.4% | 3.7% / 6.2% |
| Foot Locker | 2024-12-31 | Ba2 | down | 17% / 2% | 42 | 3.1% / 2.9% | 9.4% / 1.7% |
| Under Armour | 2025-03-31 | Ba2 | down | 15% / 2% | 48 | 3.1% / 2.9% | 2.3% / 3.1% |
| V.F. | 2025-03-31 | Ba1 | down | 14% / 2% | 50 | 3.1% / 2.9% | 5.1% / 1.9% |
| Dollar General | 2024-12-31 | Baa2 | down | 13% / 2% | 55 | 2.0% / 1.9% | 2.1% / 1.6% |
| PetSmart (no filings) | 2024-12-31 | B1 | down | 7% / 5% | 13 of 29 | 7.2% / 5.4% | 7.3% / 4.6% |

GPT-5.1 always put more weight on the right direction. It ranked the two upgrades high, which the
numbers-based models did not. Its downgrade calls are spread: Qurate and Leslie's near the top,
Dollar General, V.F. and Under Armour in the middle, where many stable companies received
similar probabilities.

### 5.2 Downgrades ranked on their own (9 events)

| Model | PR area | 95% interval |
|---|---|---|
| GPT-5.1 | 0.238 | 0.117 to 0.522 |
| M1 | 0.110 | 0.046 to 0.215 |
| M3 | 0.255 | 0.078 to 0.517 |
| GPT-5.1 minus M1 | | +0.033 to +0.377 (above zero in 99.6%) |
| GPT-5.1 minus M3 | | -0.243 to +0.225 |

Reading filings, GPT-5.1 reaches what the reported numbers reach in Experiment 08's model: both
roughly double the rating-level score for downgrades.

### 5.3 Calibration

| Fifth of P(change) | Rows | GPT-5.1 predicted | Observed |
|---|---|---|---|
| lowest | 24 | 5.3% | 0.0% |
| 2nd | 24 | 9.3% | 0.0% |
| 3rd | 24 | 14.0% | 12.5% |
| 4th | 23 | 20.1% | 13.0% |
| highest | 23 | 28.1% | 21.7% |

The ordering is right (higher predicted, more changes), the level is too high by about five
points. GPT-5.1 never named a change as the most likely outcome (highest P(change) 43%). The
prompt gave no base rates (decision 5).

### 5.4 Sensitivities

| Cohort | Rows | Changes | GPT-5.1 | M1 | M3 |
|---|---|---|---|---|---|
| Documents arm, all | 118 | 11 | 0.237 | 0.173 | 0.209 |
| Without gold observations | 114 | 8 | 0.222 | 0.183 | 0.210 |
| Prediction date 2024-12-31 | 59 | 6 | 0.377 | 0.280 | 0.332 |
| Prediction date 2025-03-31 | 59 | 5 | 0.195 | 0.146 | 0.188 |
| History only (no filings) | 29 | 1 | 0.077 | 0.091 | 0.091 |

GPT-5.1 is ahead of M1 in every documents cohort; without filings it is not.

### 5.5 Reasons and quotes

| Item | Value |
|---|---|
| Reasons given, documents arm | 407 (3.4 per answer; the prompt asked for up to three) |
| Quote found verbatim, pre-set strict check | 232 (57%) |
| Post-hoc piece check (quotes split at "…", line breaks and sentence ends; pieces of 20+ characters) | 83.5% of pieces found |
| Reasons with no piece found | 22; all 100 figures (3 digits or more) in those quotes appear in the supplied filings. They are table values retyped with added units or spacing, not invented text |
| Answers flagged "insufficient information" | 25 of 147 |

The strict check fails mainly on quotes stitched from several places without an ellipsis and on
table cells retyped. The piece check was added after reading the interim answers and is labelled
post-hoc.

### 5.6 Memory probes

74 of 74 valid. None lists a Moody's action dated October 2024 or later; 21 say their knowledge
runs to about October 2024, consistent with the boundary. Recall of older ratings is vague or wrong
in places (Walgreens called investment grade). No company flagged, so no memory sensitivity.

## 6. Model, settings and cost

| Item | Value |
|---|---|
| Model and tier | `gpt-5.1-2025-11-13`, direct OpenAI Chat Completions, `service_tier: flex`, `store: false`, reasoning effort medium, JSON schema strict, one run per company-quarter |
| Key | OpenAI key registered to info@certus-ai.com (organization certus-ai), read at run time (decision 9) |
| Served | all 222 charged responses as `gpt-5.1-2025-11-13` at the flex tier |
| Cost | $12.433096 charged in R3; $0.191074 held for the timed-out attempt (counted as if billed); $0.005288 in the R2 pilot; total at most $12.63 of the $50 cap |
| Average per forecast with filings | about $0.10 |

## 7. Coverage

| Item | Count |
|---|---|
| Forecasts valid | 147 of 147 (118 documents, 29 history only) |
| Probes valid | 74 of 74 |
| Invalid answers | 0 |
| Not billed failures | 0 in R3; 1 in R2 (input too long, refused by OpenAI) |
| Timeouts | 1 (Ingles Markets, 18 s, connection-level); cleared with a note, retried, valid |

## 8. Where the errors sit

| Layer | Finding |
|---|---|
| Ranking | the downgrades GPT-5.1 missed (Dollar General, V.F., Under Armour, Foot Locker) got 13% to 17%, the same as many stable companies; it spreads probability widely |
| Level of probabilities | about five points too high across the board |
| Evidence | reasons rest on real figures and passages, often stitched or retyped |
| Labels | Experiment 07 R2 labels; Qurate's caveats from Experiments 03 and 04 apply to its row |

## 9. What went wrong

| Defect | Effect | Fix | Rule that now prevents it |
|---|---|---|---|
| The builder checked input plus output against 400,000 tokens; OpenAI limits GPT-5.1's input to 272,000 | the R2 pilot request was refused (not billed) | input limit corrected; the specified rule (drop the oldest 10-Q) applied to 11 requests; new run R3 | the pilot before the full run (P14) |
| A connection-level timeout on one request | halt; billing unknown | attempt kept counted at its reservation, halt cleared with a recorded note, request retried | `clear-halt` records the note and keeps the charge counted |
| Two orphaned "Stable" outlook cells survived the redactor in Best Buy's 2024 10-K | the build stopped before any request | a final pass removes exactly the lines the scan flags | the scan must end empty |
| The strict quote check under-counts stitched and retyped quotes | 57% looked unsupported | post-hoc piece and number checks, labelled as such | report both checks |
| The OpenRouter keys available had no or too little credit | a day's delay | Robert chose the Certus OpenAI key | check credits before building a run |
| One of my tests was malformed | a false failure | test rewritten | |

## 10. Decipher and encode

| | What this experiment adds |
|---|---|
| Decipher | An LLM reading the filings finds about what Experiment 08's reported-number model finds for downgrades, and ranks all changes somewhat better than the rating level. It is the only method so far that ranked the two upgrades high. Without the filings it adds nothing. Where its signal comes from (numbers it reads, or language the numbers do not carry) is not separated by this design |
| Encode | nothing new encoded; the prompts, runner and scoring are reusable for any later window |

## 11. Decisions for consensus

| # | Decision | Options | Proposed |
|---|---|---|---|
| 1 | More changes | the chair's dated histories for September 2025 onwards (Experiment 11, GPT-5.2 and Opus 4.6); widen beyond Retail and Apparel; wait for Moody's public file | ask for the histories in the email; raise the sector question with Prof. Giesecke and Xiaowei. 11 changes cannot settle the primary question |
| 2 | Calibration | leave as is; give the model the historical base rates by rating (decision 5 alternative); recalibrate its probabilities afterwards | test recalibration on these answers first (free); a base-rate arm later |
| 3 | Combine GPT-5.1 with M3 | no; average or stack their probabilities | a free post-hoc check on these data, reported as such, then a pre-registered test on the next window |
| 4 | Stability | one run (as decided); a second run on the 11 changes and a sample of stable rows | a second run of about $2 to $3 on the changes and 25 stable rows would show how much the ranking moves |
| 5 | Outlooks | keep redacted; an arm with outlook and review disclosures | an outlook arm on the same rows, about $12, to measure what that public information adds |
