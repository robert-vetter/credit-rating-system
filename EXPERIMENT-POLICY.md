# Experiment policy

*Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Built from Xiaowei's
requests (first-step ask; feedback of September 2026; eight-point review of 2026-09-17),
Prof. Giesecke's leakage warning, the acceptance gates of the Experiment 04 review
(`experiments/04-open-weight-cross-section/review-codex-2026-09-12.md`) and every defect found
in Experiments 01 to 05. It applies to every experiment and every report to the chair from
2026-09-26 on. Earlier experiments are not rewritten to it. Experiment 06 must be brought to it
before it runs.*

Every experiment goes through the same seven stages in order. A stage is finished only when
its checklist is complete. Nothing may skip a stage.

| Stage | Output | Who signs off |
|---|---|---|
| 1. Design | `experiments/NN-name/README.md`, the specification, from `experiments/_template/` | Robert |
| 2. Consensus | the specification's open decisions agreed with the chair | Robert, Xiaowei, Prof. Giesecke |
| 3. Pre-checks | every pre-check passed, results saved in the run folder | independent review by the other model family, then Robert |
| 4. Run | frozen inputs, pilot, full run, raw responses and ledger | Robert authorizes the cap |
| 5. Analysis | `results.md`, from the template | independent post-run audit |
| 6. Report | `reports/YYYY-MM-DD-topic/`, from `reports/_template/` | Robert sends |
| 7. Close-out | STATUS.md, README.md and the private email log updated | agent, confirmed by Robert |

## 1. Design

The specification uses the section order of `experiments/_template/README.md`, which is the
order of the 2026-09-18 specification that the chair reviewed. Each requirement below must be
answered in it, in a table, before stage 2.

### 1.1 Question and place in the programme

| Requirement | Why |
|---|---|
| One question in one sentence, and a null hypothesis against persistence | Xiaowei asks for a clear, testable question; persistence is the baseline for every claim |
| What the experiment is and is not (a rating-state reconstruction, a forecast, a change decision) | Experiment 01 to 04 results were misread when this was left implicit |
| Where it sits in the main problem: decipher Moody's logic from data, encode it into agents, or a baseline measurement | Xiaowei's review of 2026-09-17 asks both questions of every update |
| Target: the outstanding rating at a date, the rating change, or both, stated explicitly | Xiaowei set the outstanding rating as the target in the first-step ask; Robert asked on 2026-09-26 whether the change decision is the real difficulty. If the target changes, the chair agrees first |

### 1.2 Model

| Requirement | Why |
|---|---|
| At least one widely used commercial model (GPT or a frontier Claude) whose training cutoff fits the boundary, or a written reason why not | Xiaowei's review, point 3; Robert agreed on 2026-09-26 |
| Training cutoff quoted from the vendor page, with retrieval date and a saved snapshot under `evidence/` | Xiaowei's first-step ask; Nike and GPT pages were read without a snapshot on 2026-09-18 |
| If the vendor states no cutoff, the public release date is the bound, and the report says so | Qwen had no stated cutoff (Experiment 04) |
| Boundary for documents and labels at least one month after the cutoff month; every known rating action checked against it | Experiment 02 turned out to be in sample; GPT-5.5's cutoff covers Nike's and Qurate's actions |
| No tools, no retrieval, no Internet grounding, no RAG | Xiaowei's first-step ask |
| Settings stated: temperature, seed, output ceiling, reasoning effort, provider and routing | needed to reproduce the run |
| Three replicates per observation unless the specification gives a reason; the issuer is the unit, replicates measure stability | Experiment 04 decision |
| Model comparisons use byte-identical inputs, proven by hashes | Experiment 04 found the planned inputs were not the ones Opus had seen |

### 1.3 Sample, labels and imbalance

| Requirement | Why |
|---|---|
| How the sample was built, step by step with counts, in a table | Xiaowei's review, point 1 |
| Changed and unchanged counts, upgrades and downgrades, investment grade and speculative grade, rating types | Xiaowei's review, points 1 and 2 |
| An imbalance plan: what the changed/unchanged ratio is, why, and what claim the number of changed cases can support. One or two changes support no claim about change detection | Xiaowei's review, point 2; Experiment 04 had 1 change in 19 |
| A sample built around rating changes has matched unchanged controls and states the ratio | Robert, 2026-09-26: a balanced sample is needed; changed-only samples reward a model that always predicts change |
| An agreed cost of a missed change against a false alarm, before any change decision is scored | Specification of 2026-09-18, decision 3 |
| Label source, legal entity and rating type for every label; how validity at the target date was checked | Qurate's label was stale; disclosure labels mix rating types |
| Every rating-action date to the day, with its source (Moody's release or 17g-7 file) | Xiaowei's review, point 4 |
| Labels hand-confirmed by Robert before use; `candidates.json`, mapping and gold set never regenerated | project rule |
| The gold set is never tuned on; development uses non-gold data | calibration study defect of 2026-09-11 |

### 1.4 Inputs

| Requirement | Why |
|---|---|
| A table of every input: what, source, date range, size in tokens | Xiaowei's review, point 1 |
| Point in time: every document and every fact dated and asserted against the boundary and target date | project rule |
| 8-Ks, exhibits, press releases and peer ratings are never model input | leakage audit |
| Redaction is structure-aware, and an independent scan of the assembled input finds no rating fragment | Kohl's B2 survived a lexical redactor (Experiment 04) |
| Other leakage channels considered and listed: coupon step-ups, pricing grids, instrument terms, identity recoverable from numbers | Prof. Giesecke's warning; blinding test |
| Prior rating visible or withheld is a stated design choice; where the question allows, both arms run on the same inputs | the model returned the supplied prior in 56 of 60 answers |
| If extraction accuracy is measured, the reference figures are not in the input | XBRL rows were in the input in Experiments 03 and 04 |

### 1.5 Calculation and prompt

| Requirement | Why |
|---|---|
| One deterministic calculation: all arithmetic in `system/scorecard.py`, never in the model | Xiaowei's review, point 6 |
| One written definition per input, with its methodology source; no fallback definitions such as net for gross interest | Nike and Signet net interest errors |
| Any input the model cannot find may be reported as missing; a missing input stays missing and the ratio is undefined | prompt defect of Experiments 03 and 04 |
| Extraction errors, adjustment choices, grading differences and calculation are reported as separate layers | Xiaowei's reviews, points 5 and 6 |
| Prompts, schemas and settings stored verbatim before the run; the rubric text supplied or its absence stated | abbreviated rubric in Experiments 03 and 04 |

### 1.6 Metrics, fixed before the run

| Metric | Rule |
|---|---|
| Baseline | persistence on the same observations, next to every number |
| Level | exact accuracy, within one notch, mean absolute error in notches computed from the error sum |
| Split | every metric separately on changed and unchanged observations |
| Unchanged | false alarms |
| Changed | exact, and direction computed from the rating symbols, never from the model's own direction field |
| Change decision, when enough changes exist | precision and recall, with the agreed cost |
| Consensus | median of valid replicates; stability reported separately from accuracy |
| Missing outputs | stay missing, never replaced by persistence; conditional metrics use matched persistence on the same subset |
| Post-hoc cuts | allowed only as labelled sensitivities next to the pre-registered result |

### 1.7 Budget and decisions

| Requirement | Why |
|---|---|
| A worst-case cost from a free token count, including output ceilings and failed attempts | Experiment 02 went 21 cents over; Experiment 03 lost 11 of 16 to an output ceiling |
| A dollar cap Robert approves, recorded in an authorization file bound to the manifest hash | project rule |
| Every open choice listed in the specification's final section as a decision for consensus, with options and a proposal | Xiaowei: "SPEC-driven R&D" |

## 2. Consensus

The specification goes to the chair as a report (stage 6 format) before the run. The run does
not start until each decision in the specification's final section is agreed or explicitly
left to Robert. Agreements are recorded in `decisions.md` with owner and date.

## 3. Pre-checks before any paid call

All must pass on the exact files that will be sent. A check that passed on other code or other
inputs does not count. A failed check stops the run.

| # | Check | Evidence saved |
|---|---|---|
| P1 | Specification reviewed by the other model family (Claude builds, Codex reviews, or the reverse); every finding fixed or answered | `review-*.md` in the experiment folder |
| P2 | Chair consensus on the open decisions, or Robert's written decision to proceed | `decisions.md` |
| P3 | Authorization: scope, model, provider, replicates, retries and cap approved by Robert and bound to the manifest hash | `authorization.json` |
| P4 | Cohort frozen: exact observation IDs, no duplicates, excluded cases and their reason listed | manifest |
| P5 | Inputs frozen: hashes of every document, pack, prompt, schema, scorer and request body; the runner sends the frozen bodies, it does not rebuild them | manifest |
| P6 | Point-in-time audit passes for every document and fact | `audit/` |
| P7 | Redaction scan finds no rating fragment in any assembled request | `audit/` |
| P8 | No tools, retrieval or plugins in any request body | test |
| P9 | Every request fits the context window with the output ceiling reserved, counted with the model's own tokenizer | token evidence |
| P10 | Worst-case price, including failures and retries, is below the cap; a live price check in the same process | ledger |
| P11 | Cutoff snapshot saved under `evidence/` | `evidence/` |
| P12 | Memory probe per observation, reviewed before that observation's documents are sent | `probe_review.json` |
| P13 | Tests pass: scorecard edge cases (negative EBITDA, net cash, zero denominators), runner guards against a fake transport, scoring fixtures with missing and failed rows | test output |
| P14 | Pilot: one request chosen by a rule fixed in advance, inspected for protocol problems (not for accuracy); the rest waits until it passes | `pilot_review.json` |

## 4. During the run

| Rule |
|---|
| No change to prompts, inputs, ceilings, providers or replicates after the pilot. A fix means a new manifest, new pre-checks and the same ledger |
| Every raw response and charge is saved before it is parsed |
| Anything unexplained halts the run: a price change, a token mismatch, a missing charge, an unexpected model or provider |
| Failed requests stay in the record and in the denominators |

## 5. Analysis

| Rule | Why |
|---|---|
| Every number next to persistence on the same observations, with n and the changed/unchanged split | Xiaowei's first-step ask |
| Each error attributed to its layer: label, extraction, input definition, qualitative grade, calculation, or the model's overall judgement | Xiaowei's review, points 5 and 6 |
| Consistency across replicates is reported as stability, never as correctness | Experiment 04 audit |
| No claim beyond the sample: one changed case is an anecdote | imbalance |
| Post-hoc exclusions only as labelled sensitivities | Kohl's and Dollar General in Experiment 04 |
| An independent post-run audit by the other model family before the results are reported | Experiment 04 audit found the redaction failure |
| Every mistake found is disclosed with the rule that now prevents it | project rule |
| Results are never used to tune the same test | gold set rule |

## 6. Presenting results, in `results.md` and in every report

Facts, dates and numbers go in tables or lists. Prose is two or three sentences of
interpretation at a time. Every report contains these parts, in this order, or says why a part
does not apply.

| # | Part | Must contain |
|---|---|---|
| 1 | Summary | the question, the answer next to persistence, what changed since the last report, in five lines or fewer |
| 2 | Headline table | each channel and persistence: exact, within one, MAE, false alarms, changed/unchanged counts, n |
| 3 | Dates table | model cutoff and its source, history end, document boundary, filing window, target date, run date, each in its own row |
| 4 | Input data characteristics | issuers, documents by form, filing dates, tokens (min, median, max), rating distribution, investment/speculative grade, rating types, label sources, changed/unchanged |
| 5 | Per-observation table | prior rating with type and date, each filing's period end and filing date, label with source and date, rating action with its day, and every channel's result, all in one table |
| 6 | Model and settings | model ID, cutoff, provider, temperature, seed, ceilings, replicates, cost against cap |
| 7 | Coverage | every attempt, every failure and why, the denominators used |
| 8 | Error breakdown | errors by layer (extraction, definition, grade, calculation, judgement), with at least one worked example with numbers |
| 9 | Defects and limitations | everything that went wrong, its effect, and the fix |
| 10 | Decipher and encode | what this adds to deciphering Moody's logic, and what is now encoded |
| 11 | Decisions for consensus | options and a proposal for each |
| 12 | Definitions | every non-standard term, one sentence each, with an example |

Formatting rules:

| Rule | Why |
|---|---|
| Dates as YYYY-MM-DD, one concept per column, the source named | Xiaowei's feedback of September 2026 |
| One idea per sentence; no sentence that needs "what do you mean" | Xiaowei's review, points 5 and 7 |
| A number that came from a calculation shows the calculation once, in a worked example | Signet example, 2026-09-18 |
| Answer each of the chair's questions point by point, with a short answer column | 2026-09-18 answers |
| Every link is public and opens without login before the report is sent | published-folder check |
| Plain English, no em dashes, no marketing words, an attribution header on every document | writing rules in `AGENTS.md` |

Before sending anything to the chair, check:

1. Every number is in a table, next to persistence, with n and the changed/unchanged split.
2. All dates are in one table, to the day where a source exists, with the source named.
3. The input data has its own characteristics table.
4. Class imbalance is addressed explicitly.
5. A commercial-model comparison exists, or its plan and cost are stated.
6. Arithmetic and extraction are separated, with one written definition per input.
7. Every non-standard term is defined, with a worked example where numbers are involved.
8. The specification is updated and the decisions needing consensus are listed.
9. The update says where it sits in decipher versus encode.
10. The links are public and working.

## 7. Close-out

| Step |
|---|
| `STATUS.md`: results table, open decisions, findings and log updated |
| `README.md`: results and reports tables updated |
| `decisions.md` of the experiment complete with owners and dates |
| After Robert sends a report: the sent text pasted into the private email log, and the chair's open questions updated there |
