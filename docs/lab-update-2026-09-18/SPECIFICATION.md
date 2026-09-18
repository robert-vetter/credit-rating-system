# Specification: post-cutoff outstanding-rating estimation, Retail and Apparel, target date 29 August 2026

*Written 18 September 2026 by Claude (Fable 5.1), directed by Robert Vetter. Version 1.0, for review and consensus. It specifies the experiment as executed (Experiment 03 on Claude Opus 4.6, Experiment 04 on Qwen3-235B) and marks, as DECISION, every item that must be agreed before the next run. Checked against: the executed [Experiment 04 specification](../../experiments/04-open-weight-cross-section/RUN-SPEC.md) and [results](../../experiments/04-open-weight-cross-section/results.md), the [Experiment 03 specification](../../experiments/03-oos-values-first/README.md), the accepted [candidate labels](../../experiments/03-oos-values-first/candidates.json), the frozen Qwen token counts, the local Moody's 17g-7 rating records, the [accounting study](../../experiments/05-accounting-interventions/results.md), `system/scorecard.py`, and the vendor and agency sources cited inline with their retrieval dates. No label, run record or result was changed.*

[Answers to the review questions](README.md) · [Previous folder: results, dates, prompts](../lab-update-2026-09-17/README.md)

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | Can an existing LLM, given an issuer's SEC filings published after the model's training bound, estimate the Moody's long-term rating outstanding at a target date more accurately than carrying the last known rating forward? |
| Null hypothesis | The model does not beat persistence on exact accuracy or mean absolute notch error. |
| Unit of observation | One issuer at the target date. Unchanged issuers stay in the sample. |
| What it is | Reconstruction of a rating state at a date after the model's bound, from information public by that date. |
| What it is not | A forecast made before a rating action. A multi-step agent. A test of Moody's own adjusted figures, which are not public. |
| Sector and methodology | Moody's Retail and Apparel methodology, 12 September 2025. |
| Place in the programme | Baseline measurement. It tells us how far an unaided LLM is from the target and where the error comes from. It is not the analyst system. |

## 2. Dates

| Date concept | Qwen run (Experiment 04) | Opus run (Experiment 03) | Source |
|---|---|---|---|
| Model | Qwen3-235B-A22B-Instruct-2507 | Claude Opus 4.6 | vendor pages |
| Training-data bound | No vendor-stated cutoff. Public checkpoint released **2025-07-21**, used as the bound | Vendor-stated training cutoff **August 2025**; reliable knowledge cutoff May 2025 | [Qwen model card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507); [Opus evidence snapshot](../../experiments/03-oos-values-first/evidence/opus-4-6-cutoff-2026-09-10.md) |
| Rating history supplied to the model ends | **2025-08-28** | same | Moody's 17g-7 file dated 2026-08-11, embargoed twelve months |
| Document boundary B | **2025-09-30** | same | one month after the Opus cutoff month |
| Primary filings eligible | filed after B and on or before the target date | same | |
| Primary filings actually supplied | **2025-12-18 to 2026-08-28** | earliest 2026-02-19 | filing manifests |
| Target date | **2026-08-29** | same | |
| Executed | **2026-09-13** | **2026-09-10** | run ledgers |
| Rating actions in the window with a known day | Nike A1 to A2 on **2025-11-12** | same | Moody's press release, section 4 |

## 3. Sample and data characteristics

### 3.1 How the sample was built

| Step | Count | Where |
|---|---|---|
| Moody's Retail and Apparel entities joined to SEC filers by stable identifiers | 186 | `evaluation/mapping.json` |
| Distinct in-scope groups with an active Moody's rating at 2025-08-28 | 66 | `notes/rating-history-file.md` |
| Groups that are current annual SEC filers, usable at the target date | 63 | same |
| Filings scanned for the issuer's own Moody's rating disclosure after B | 725 documents, 63 companies | `experiments/03-oos-values-first/label-review.md` |
| Issuers with a hand-read, confirmed disclosure label | 20 | `candidates.json` |
| Primary cohort | **19**; Qurate/QVC held out as a diagnostic before execution (entity and bankruptcy problems) | decision D8 |
| Executed on Qwen | 20 issuers, 3 replicates, 60 valid document responses; 20 memory probes; 21 saved-input comparison calls | results |
| Executed on Opus | 16 scheduled, 7 usable (11 hit an output ceiling; 2 changed cases rerun) | Experiment 03 results |

Selection depends on which issuers disclose their rating in a filing. That is a property of the label supply, not a random sample of the sector.

### 3.2 Label characteristics, primary cohort of 19

| Characteristic | Value |
|---|---|
| Changed against the prior rating | **1 of 19 (5.3%)**: Nike, downgrade. With Qurate: 2 of 20, both downgrades |
| Upgrades | 0 |
| Rating category of the label | Aa 1, A 3, Baa 5, Ba 8, B 1, Caa 1 |
| Investment grade / speculative grade | 9 / 10 |
| Rating type behind the prior rating, from the 17g-7 file | Corporate family rating 10; long-term issuer rating 4; senior unsecured 5 |
| Label source form | 10-K 8; 10-Q 11 |
| Label publication dates | 2025-12-18 to 2026-08-28 |
| Label validity at the target date | Not verified. The label is the latest company disclosure on or before the target date |
| Labels confirmed by | Robert Vetter, 2026-08-31, after hand reading of every candidate statement |

### 3.3 Document characteristics, primary cohort of 19

| Characteristic | Value |
|---|---|
| Documents supplied to the model | **47**: 19 10-Ks and 28 10-Qs |
| Per issuer | one 10-K plus 0 to 3 subsequent 10-Qs (Nike 0, Leslie's 3) |
| Filing dates | 2025-12-18 to 2026-08-28 |
| Fiscal year ends of the 10-Ks | 2025-10-04 to 2026-05-31 |
| Request size in Qwen tokens (documents, history pack, prompt, schema) | min 92,748 (Kohl's); median 155,707; mean 164,347; max 285,930 (Levi Strauss); sum 3,122,589 |
| Of which documents | min 72,446; median 135,739; max 265,875 |
| Of which history pack | 17,694 to 18,822 per issuer |
| Lines removed by redaction (rating self-disclosures) | 5 to 79 per issuer |
| Dropped by the context rule | Levi Strauss's 10-Q filed 2026-04-07 (oldest 10-Q removed to fit 262,144 tokens) |
| Never supplied | 8-Ks, exhibits, press releases, peer ratings, any tool or retrieval |

Token counts are from the Qwen tokenizer, frozen on 2026-09-12. Other tokenizers give different counts of the same text.

### 3.4 Historical data held for other purposes, not part of this test

| Characteristic | Value |
|---|---|
| Companies with a full folder (filings, XBRL, ratings) | 86 |
| Quarterly observations, 2012-09-30 to 2025-06-30 | 3,646 |
| Observations with a rating change against the previous quarter | 218 (6.0%) |
| In scope of the methodology | 3,084 |
| Calibration study coverage (full quantitative inputs, gold excluded) | 1,665, of which 78 changed (4.7%) |
| Gold set, frozen 2026-08-29, hand validated | 50: 30 changed, 20 unchanged |

The 6.0% quarterly change rate is the base rate for the whole sector over thirteen years. Any post-cutoff window of one year will be similarly imbalanced.

## 4. Per-issuer table: prior rating, filings, label, action and results

Prior rating column: the rating in the 17g-7 file at 2025-08-28, its type, and the most recent record at that level (action code and date; NW means a new instrument or rating assigned at that level, HS means the history start of June 2012 with no action since). Filing entries are financial period end / SEC filing date. Results are the consensus of three Qwen replicates on current inputs; a tick means equal to the label.

| ID | Issuer | Prior rating (type, last record) | 10-K | 10-Qs | Label (source, filed) | Rating action in window | Judgement | Scorecard | Persistence |
|---|---|---|---|---|---|---|---|---|---|
| X01 | Bath & Body Works | Ba2 (CFR, up 2021-08-12) | 2026-01-31 / 2026-03-12 | 2026-05-02 / 05-27; 2026-08-01 / 08-26 | Ba2 (10-Q 2026-08-26) | none disclosed | Ba2 ✓ | Ba2 ✓ | Ba2 ✓ |
| X02 | Best Buy | A3 (issuer, up 2021-02-26) | 2026-01-31 / 2026-03-18 | 2026-05-02 / 06-05 | A3 (10-K 2026-03-18) | none disclosed | A3 ✓ | A3 ✓ | A3 ✓ |
| X03 | Dick's Sporting Goods | Baa2 (sen. unsec., up 2024-08-09) | 2026-01-31 / 2026-03-27 | 2026-05-02 / 06-04 | Baa2 (10-Q 2026-06-04) | none disclosed | Baa2 ✓ | Baa3 | Baa2 ✓ |
| X04 | Dollar General | Baa3 (sen. unsec., down 2025-03-28) | 2026-01-30 / 2026-03-20 | 2026-05-01 / 06-02; 2026-07-31 / 08-27 | Baa3 (10-Q 2026-08-27) | none disclosed | Baa2 | A3 | Baa3 ✓ |
| X05 | Floor & Decor | Ba3 (CFR, up 2019-11-22) | 2025-12-25 / 2026-02-19 | 2026-03-26 / 04-30; 2026-06-25 / 07-30 | Ba3 (10-Q 2026-07-30) | none disclosed | Ba3 ✓ | Baa3 | Ba3 ✓ |
| X06 | Gap | Ba2 (CFR, up 2025-02-20) | 2026-01-31 / 2026-03-17 | 2026-05-02 / 05-29; 2026-08-01 / 08-28 | Ba2 (10-K 2026-03-17) | none disclosed | Ba2 ✓ | Baa3 | Ba2 ✓ |
| X07 | Kohl's | B2 (CFR, down 2025-05-13) | 2026-01-31 / 2026-03-19 | 2026-05-02 / 06-04 | B2 (10-Q 2026-06-04) | none disclosed | B2 ✓ | Ba2 | B2 ✓ |
| X08 | Leslie's | Caa3 (CFR, down 2025-08-13) | 2025-10-04 / 2025-12-18 | 2026-01-03 / 02-18; 2026-04-04 / 05-13; 2026-07-04 / 08-12 | Caa3 (10-K 2025-12-18) | none after 2025-08-28; the 2025-08-13 downgrade is inside the prior | Caa3 ✓ | Caa2 | Caa3 ✓ |
| X09 | Levi Strauss | Ba1 (CFR, up 2015-04-16) | 2025-11-30 / 2026-01-28 | 2026-05-31 / 07-08 (2026-04-07 10-Q dropped) | Ba1 (10-K 2026-01-28) | none disclosed | Ba1 ✓ | A2 | Ba1 ✓ |
| X10 | Lowe's | Baa1 (sen. unsec., NW 2023-03-28) | 2026-01-30 / 2026-03-23 | 2026-05-01 / 05-28; 2026-07-31 / 08-27 | Baa1 (10-Q 2026-08-27) | none disclosed | Baa1 ✓ | Baa2 | Baa1 ✓ |
| X11 | Macy's | Ba1 (CFR, up 2022-02-23) | 2026-01-31 / 2026-03-27 | 2026-05-02 / 06-04 | Ba1 (10-K 2026-03-27) | none disclosed | Ba1 ✓ | Baa3 | Ba1 ✓ |
| X12 | **Nike** | A1 (sen. unsec., NW 2020-03-25) | 2026-05-31 / 2026-07-15 | none | **A2** (10-K 2026-07-15) | **Downgrade A1 to A2 on 2025-11-12** | A1 | Aa3 | A1 |
| X13 | PVH | Baa3 (sen. unsec., NW 2025-06-10) | 2026-02-01 / 2026-03-31 | 2026-05-03 / 06-05 | Baa3 (10-Q 2026-06-05) | none disclosed | Baa3 ✓ | Ba2 | Baa3 ✓ |
| X15 | Signet | Ba3 (CFR, down 2020-03-30) | 2026-01-31 / 2026-03-19 | 2026-05-02 / 06-02 | Ba3 (10-K 2026-03-19) | none disclosed | Ba3 ✓ | A3 | Ba3 ✓ |
| X16 | Target | A2 (issuer, HS 2012-06-15) | 2026-01-31 / 2026-03-11 | 2026-05-02 / 05-29; 2026-08-01 / 08-28 | A2 (10-Q 2026-08-28) | none disclosed | A2 ✓ | Aa3 | A2 ✓ |
| X17 | Tractor Supply | Baa1 (issuer, NW 2020-10-21) | 2025-12-27 / 2026-02-19 | 2026-03-28 / 05-07; 2026-06-27 / 08-06 | Baa1 (10-K 2026-02-19) | none disclosed | Baa1 ✓ | Baa1 ✓ | Baa1 ✓ |
| X18 | V.F. | Ba2 (CFR, down 2025-06-16) | 2026-03-28 / 2026-05-20 | 2026-06-27 / 07-29 | Ba2 (10-Q 2026-07-29) | none disclosed | Ba2 ✓ | Ba1 | Ba2 ✓ |
| X19 | Victoria's Secret | Ba3 (CFR, NW 2021-06-21) | 2026-01-31 / 2026-03-20 | 2026-05-02 / 06-05 | Ba3 (10-Q 2026-06-05) | none disclosed | Ba3 ✓ | B1 | Ba3 ✓ |
| X20 | Walmart | Aa2 (issuer, HS 2012-06-15) | 2026-01-31 / 2026-03-13 | 2026-04-30 / 05-29; 2026-07-31 / 08-28 | Aa2 (10-Q 2026-08-28) | none disclosed | Aa2 ✓ | Aa3 | Aa2 ✓ |
| **Totals, 19** | | | | | 1 changed | | **17/19** | **3/19** | **18/19** |
| X14 | Qurate/QVC, diagnostic | Caa1 (CFR of LI LLC, down 2025-05-21) | 2025-12-31 / 2026-04-15 | 2026-06-30 / 08-04 (2026-05-15 10-Q dropped) | Caa3 (10-Q 2025-11-05) | Downgrade Caa1 to Caa3 in **October 2025**, day not yet established | Caa1 | Caa2 | Caa1 |

"None disclosed" means the issuer's later filings state the same rating as the prior. It is not proof that no action occurred; a downgrade followed by an upgrade would be invisible.

Sources for the action days. Nike: Moody's Ratings press release "Moody's Ratings downgrades NIKE's senior unsecured rating to A2 from A1", dated "New York, November 12, 2025", https://ratings.moodys.com/ratings-news/454361, read on 2026-09-18 from a public mirror copy; Nike's own 10-Q filed 2025-12-30 says only "In November 2025". Qurate: the 10-Q filed 2025-11-05 says "during October 2025"; the Moody's release is behind the Moody's login and has not been retrieved. Leslie's 2025-08-13: Moody's 17g-7 file, OI 825431804. All other prior-rating dates: the 17g-7 file. Day precision is available for every action once the Moody's release is read; the previous folder gave months because it was built from filings only.

## 5. Models and settings

| Setting | Qwen, executed | Opus, executed | GPT-5.2, proposed (DECISION 4) |
|---|---|---|---|
| Model ID | `qwen/qwen3-235b-a22b-2507`, DeepInfra fp8 via OpenRouter, no fallback | `claude-opus-4-6` | `gpt-5.2` |
| Bound | checkpoint 2025-07-21, no vendor cutoff | training cutoff Aug 2025 | vendor page: knowledge cutoff **31 August 2025**, 400,000-token context, $1.75 / $14 per million input / output tokens (read 2026-09-18 at developers.openai.com/api/docs/models/gpt-5.2) |
| Fits boundary B = 2025-09-30 | yes | yes | yes, same one-month buffer as Opus |
| Sampling | temperature 0, seed 20260912 | API defaults, adaptive thinking, high effort | temperature 0 if supported, else defaults, recorded |
| Output ceiling | 8,192 tokens | 9,000, then 24,000 for reruns | to be set from a free pre-flight |
| Structured output | JSON schema, strict | JSON schema | JSON schema |
| Replicates | 3 per issuer | 1 | 3 per issuer |
| Tools, retrieval, grounding | none | none | none |
| Memory probe before documents | yes, 20 | yes, 16 | yes |
| Cost | $1.24 reconciled plus $0.14 held, cap $3.00 | $8.74, cap $10 | estimate $10 to $25 for 20 issuers times 3 replicates (about 3.4 million input tokens per replicate at Qwen counts; batch discount and tokenizer differences unknown); cap to be approved |

GPT-5.5 (vendor page: knowledge cutoff 1 December 2025) cannot be used for this window: the Nike and Qurate actions fall inside its training data. GPT-5 and GPT-5.1 are listed with a September 2024 cutoff in third-party tables; the vendor pages were not read for this document.

## 6. Inputs to the model

| Input | Content | Rule |
|---|---|---|
| Primary documents | the latest 10-K filed after B, then every subsequent 10-Q filed on or before the target date | HTML converted to line-preserving text; rating self-disclosures removed by `system/redact.py`; removed lines stored |
| History pack | rating events through 2025-08-28 and the persistence rating; latest annual XBRL figures plus up to three prior years; quarterly rows where available; implied qualitative anchors derived from historical ratings and numerical factors | every fact carries a source date not later than the target date; anchors are not Moody's published factor grades |
| Peer table | financial figures of sector peers, without ratings | peer fiscal-year end within 24 months of the target date |
| As-of line | "As-of date: 2026-08-29" | |
| Task and schema | section 7 | |
| Excluded | 8-Ks, exhibits, press releases, peer ratings, the model's own memory (asked to be ignored, which is a request, not a control) | |

## 7. Prompt and output

The verbatim system prompt, task, memory probe and both output schemas are in [PROMPTS.md](../lab-update-2026-09-17/PROMPTS.md). In summary the model must: (1) extract ten financial inputs in USD millions for the most recent full fiscal year in the documents; (2) grade four qualitative factors on Aaa to Ca relative to the implied anchor, with a one-line justification each; (3) give its own overall rating judgement and whether it is an upgrade, unchanged or downgrade against the last rating in the history pack.

Two channels are scored. The **scorecard channel** sends the ten figures and four grades through the deterministic engine of section 8. The **judgement channel** is the model's own overall rating. The prompt gave brief factor descriptions, not the methodology's full rubric text.

Known prompt defects, not corrected retroactively: every financial field required a number, so a missing figure could not be reported as missing; net interest was explicitly allowed as a fallback for gross interest; the debt instruction listed overlapping components without a reconciliation procedure.

## 8. The deterministic calculation

There is one calculation. It lives in `system/scorecard.py`, is covered by regression tests, and never changes between runs or models. What varied in Experiments 03 and 04 was the ten numbers and four grades the model put in, not the arithmetic.

### 8.1 The ten inputs, one definition each

| Input | Definition as executed (from the task text) | Methodology basis | Defect seen | Next version (DECISION 6) |
|---|---|---|---|---|
| revenue | total reported revenue of the fiscal year, including membership and other income | page 6, total reported revenue | Walmart: net sales used instead of total revenue in one reading (no rating effect, above the top band) | from XBRL `Revenues`, code only |
| operating_income | operating income as reported | EBITDA numerator | Nike: pretax income used in two saved responses | from XBRL, code only |
| d_and_a | depreciation and amortisation from the cash-flow statement | EBITDA numerator | none found | from XBRL, code only |
| capex | capital expenditures | coverage numerator | none found | from XBRL, code only |
| interest | gross interest expense including finance-lease interest; the schema allowed net interest as a fallback | coverage denominator | Nike and Signet: net interest income used; Walmart: net expense used where the gross figure exists | gross expense only; if absent, the field is missing and the ratio is undefined |
| cash | cash and cash equivalents at fiscal year end | net debt | none found | from XBRL, code only |
| dividends | dividends paid, cash-flow statement | RCF | none found | from XBRL, code only |
| cfo | net cash provided by operating activities | FFO | none found | from XBRL, code only |
| wc_swing | sum of working-capital change lines inside operating cash flow, sign as reported | FFO = CFO minus wc_swing | inconsistent line selection across replicates | itemised lines, code only |
| debt | short-term debt + current portion of long-term debt + long-term debt + finance-lease liabilities + operating-lease liabilities + financing obligations | Moody's-adjusted debt | Signet: zero debt returned although $1,217.3 million of operating leases are disclosed; overlapping components | itemised components from XBRL, reconciled current + noncurrent = total, code only; unresolved items stay explicit |

### 8.2 Derived quantities and ratios

| Quantity | Formula |
|---|---|
| EBITDA | operating_income + d_and_a |
| Net debt | debt − cash |
| FFO | cfo − wc_swing |
| RCF | FFO − dividends |
| Revenue, USD billion | revenue / 1000 |
| Debt / EBITDA | debt / EBITDA |
| (EBITDA − capex) / interest | (EBITDA − capex) / interest |
| RCF / net debt, % | 100 × RCF / net debt |

### 8.3 Scoring, weights and mapping

Each quantitative ratio is placed in its band and linearly interpolated to a score between 0.5 and 20.5, lower is better: Aaa 0.5 to 1.5, Aa 1.5 to 4.5, A 4.5 to 7.5, Baa 7.5 to 10.5, Ba 10.5 to 13.5, B 13.5 to 16.5, Caa 16.5 to 19.5, Ca 19.5 to 20.5. Band endpoints per ratio are the methodology's Exhibit values as coded in `BANDS`. Qualitative grades map to fixed scores: Aaa 1, Aa 3, A 6, Baa 9, Ba 12, B 15, Caa 18, Ca 20.

| Factor | Weight | Type |
|---|---|---|
| Revenue | 15% | quantitative |
| Market Characteristics | 10% | qualitative |
| Market Position | 10% | qualitative |
| Revenue and Earnings Stability | 10% | qualitative |
| Debt / EBITDA | 15% | quantitative |
| (EBITDA − capex) / interest | 15% | quantitative |
| RCF / net debt | 10% | quantitative |
| Financial Policy | 15% | qualitative |

The weighted sum maps to a notch, one unit per notch: at most 1.5 Aaa, 2.5 Aa1, 3.5 Aa2, 4.5 Aa3, 5.5 A1, 6.5 A2, 7.5 A3, 8.5 Baa1, 9.5 Baa2, 10.5 Baa3, 11.5 Ba1, 12.5 Ba2, 13.5 Ba3, 14.5 B1, 15.5 B2, 16.5 B3, 17.5 Caa1, 18.5 Caa2, 19.5 Caa3, 20.5 Ca, above that C.

Edge rules from the methodology's page 5 footnotes, corrected on 2026-09-12: negative EBITDA gives the worst leverage score; with net cash, RCF / net debt scores best if RCF is positive and worst otherwise; zero EBITDA, zero net debt or non-positive interest is undefined and the calculation fails explicitly rather than inventing a rating.

The result is the scorecard-indicated outcome. Moody's assigned rating additionally reflects considerations outside the scorecard and committee judgement (methodology Exhibit 1). That gap is irreducible from the scorecard alone and is part of the measured error.

### 8.4 Who computed what

| Step | Experiments 03 and 04 | Next version |
|---|---|---|
| Ten financial inputs | model, reading the filings, with XBRL rows also in the input | code, from XBRL through the evidence ledger; model only for facts XBRL lacks, with a cited quote |
| Four qualitative grades | model, from brief factor descriptions | model, from the rubric text, with supporting and adverse quotes verified against the source |
| Ratios, scores, weights, mapping | code | code |
| Overall judgement | model, prior rating visible | model, evaluated with the prior withheld and with it visible |

## 9. Metrics, baselines and the imbalance

| Item | Rule |
|---|---|
| Baseline | persistence: the rating in the history pack at 2025-08-28, carried forward. Reported next to every number on the same issuers |
| Primary metrics | exact accuracy; within one notch; mean absolute error in notches on the 21-notch scale |
| Split | every metric on changed and on unchanged issuers separately |
| On changed | exact; direction correct |
| On unchanged | false alarms (any move away from the prior) |
| Consensus | median of three valid replicate ratings; issuer is the unit, replicates measure stability |
| Direction | computed from rating symbols, never from the model's own "upgrade / unchanged / downgrade" field, which contradicted its rating in five responses |
| Missing outputs | stay missing; conditional metrics use matched persistence on the same subset |

Imbalance treatment, as executed. The sample has 1 changed issuer in 19; the sector's historical quarterly change rate is 6.0%. What was done: persistence is the baseline, which is the majority-class predictor; every number is split changed versus unchanged; false alarms and direction are reported separately; the historical gold set was built at 30 changed to 20 unchanged against the 6% base rate; both changed cases were always scheduled first (Experiment 03 rule D9); no accuracy figure is reported without its persistence pair. What was not done: no resampling and no class weights, because no component is trained on these labels. The one fitted component, the change-signal thresholds of the calibration study, chose "never alarm" in every fold, which is what imbalance plus a weak signal produces and is reported as such. What cannot be done with this sample: a precision-recall curve or a cost-weighted decision rule with one changed case. DECISION 3 below.

## 10. Controls

| Control | Executed | Evidence |
|---|---|---|
| Boundary check per document and per fact | every supplied filing and pack fact dated and asserted against B and the target date | `runs/<batch>/audit/` |
| No tools, no retrieval | no `tools` key in any request; no grounding; Internet off | frozen request bodies |
| Redaction of rating self-disclosures | lexical pass on every document; removed lines stored | `system/redact.py` |
| Redaction failure found after the run | Kohl's B2 survived in a one-cell-per-line table in all three replicates; Dollar General kept short-term rating and outlook cells | post-run audit; post-hoc sensitivities reported; structural second pass and scan added for future runs |
| Memory probe before documents | one per issuer, no documents, answers not fed forward; no verified post-bound recall found | `probe_review.json` |
| Budget | dollar cap approved before submission; free pre-flight prices the worst case; runner refuses above the cap | `authorization.json`, ledger |
| Provenance | raw bytes of every response archived; manifest hash bound to the authorization | run directory |
| Independent review | specification refused once and repaired before the run; post-run audit by a second model family | `review-codex-2026-09-12.md`, `review-codex-2026-09-13.md` |
| Frozen human decisions | labels, mapping, gold set never regenerated | `AGENTS.md` |

## 11. Results, in one table

| Cohort | Changed / unchanged | Judgement exact, MAE | Scorecard exact, MAE | Persistence exact, MAE |
|---|---:|---:|---:|---:|
| Qwen, primary 19 | 1 / 18 | 17/19, 0.11 | 3/19, 1.84 | 18/19, 0.05 |
| Qwen, post-hoc 17 without Kohl's and Dollar General | 1 / 16 | 16/17, 0.06 | 3/17, 1.71 | 16/17, 0.06 |
| Qwen, all 20 with Qurate | 2 / 18 | 17/20, 0.20 | 3/20, 1.80 | 18/20, 0.15 |
| Opus, 7 usable | 2 / 5 | 4/7, 0.57 | 3/7, 1.14 | 5/7, 0.43 |
| Qwen on the same 7 saved Opus inputs, replicates 1 and 2 | 2 / 5 | 4/7, 0.57 | worse than Opus | 5/7, 0.43 |

Neither channel beats persistence on any cohort. The judgement channel returned the supplied prior in 56 of 60 answers, missed both changes and raised one false alarm. The scorecard channel sits 1.23 notches favourable on average with 15 false alarms on 18 unchanged issuers. Full tables: [results](../../experiments/04-open-weight-cross-section/results.md).

## 12. Known defects and limitations

| Defect | Effect | Status |
|---|---|---|
| Kohl's rating survived redaction; Dollar General short-term cells survived | inputs not fully blind for two issuers | disclosed; sensitivities reported; redactor repaired for future runs |
| Labels are company disclosures, not Moody's histories | validity at the target date unverified; rating types mixed | open; needs dated histories (DECISION 2) |
| One changed issuer in the primary cohort | change detection cannot be measured | open; needs more labelled changes (DECISION 3) |
| Prompt required a number for every field and allowed net interest | extraction errors forced into the scorecard | fixed in the next version (section 8.4) |
| Full rubric not in the prompt | grades rest on brief descriptions | next version supplies the rubric text |
| XBRL rows were in the input | agreement with XBRL is not an independent extraction test | next version withholds reference figures from the model |
| Opus run lost 11 of 16 to an output ceiling | the 7 are selected successes, not a sample | disclosed |
| Prior rating visible to the model | anchoring is plausible, untested | next version runs a prior-withheld arm |
| Qwen bound is a release date, not a stated cutoff | weaker cutoff claim than Opus | disclosed |

## 13. Decisions that need consensus before the next run

| # | Decision | Options | Proposed |
|---|---|---|---|
| 1 | Target rating type | corporate family rating for speculative grade and senior unsecured for investment grade (methodology page 14); or one type for all; or the issuer's own disclosed rating as now | methodology rule, once histories with rating types are available |
| 2 | Label source | the lab's dated Moody's histories September 2025 to August 2026; or company disclosures as now | the lab's histories, if they exist |
| 3 | Imbalance policy | state the cost of a missed change against a false alarm; report precision and recall of the change decision once more changed cases exist; add Arm 2 (boundary 2024-09-30, official labels, 59 issuers, 12 changes) as a second window | all three |
| 4 | Commercial model | GPT-5.2 on the identical frozen inputs, three replicates, all 20 issuers, under a cap of about $25; Gemini optional | run GPT-5.2 as Experiment 07 |
| 5 | Prior visible or withheld | both arms, same inputs | both |
| 6 | Input definitions | the ten definitions of section 8.1, computed in code, signed off by the lab | sign off or amend |
| 7 | Reference data | hand-checked inputs, adjustments and factor grades for a small set of issuers, from Moody's Credit Opinions or the lab; otherwise built here and reviewed by the lab | ask, then build |
| 8 | Moody's documents | access and terms of use for Credit Opinions and rating-action releases through Robert's account | settle before the decipher work of the README |
| 9 | Repository | the repository is public and holds the methodology PDF | Robert's decision |

## 14. Provenance of this document

The per-issuer dates were joined from the frozen input audits and the SEC manifests, the prior-rating types and dates from the local 17g-7 records, the results from the corrected Experiment 04 tables, the token figures from the frozen 2026-09-12 counts, and the calculation from `system/scorecard.py` as of commit 9eac085. External facts read on 2026-09-18 and not yet snapshotted under an `evidence/` folder: the Nike action date and the GPT-5.2 and GPT-5.5 vendor pages.
