# Handover: where this project stands, how it got here, and what is open

*Written 2026-09-12 by Claude (Fable 5.1) at Robert Vetter's request, so that a new session in
any tool (Claude, OpenAI, a human) can pick the project up without prior context. Everything
here is either in the repository or in Robert's chat with Claude; where a fact comes from
correspondence that is not in the repository, that is said. Read this file first, then
README.md, then the experiment folders. Keep this file current: append a dated entry to
section 13 whenever the state changes.*

## Current instruction and review, 2026-09-12

*Written by Codex, directed by Robert Vetter. Verified against the saved Experiment 03
requests, local filings, methodology PDF, code, and offline replay. This update supersedes
conflicting completion instructions and quality claims in the historical handover below.*

Robert has stopped the remaining 13 Experiment 03 observations because of cost. No top-up,
paid preflight, rerun or new paid experiment is pending. The runner now rejects paid actions.
Current work is the free integrity review and discussion of the analyst architecture.

Read `docs/oos-integrity-review.md` before presenting results. A negative-EBITDA scoring bug
was found and fixed against the methodology: Qurate's saved scorecard output changes from
B2 to Caa2 under corrected arithmetic. Its November 2025 label is stale relative to input
filings describing April 2026 bankruptcy, so the review reports a without-Qurate sensitivity.
Original prompts, paid artifacts, labels, mapping and gold set remain unchanged.

The replay reproduces all 18 submitted document packages exactly and passes 52 groups of
mechanical checks. It does not certify absent leakage. Current XBRL was in the input, so
"extraction is solved" is withdrawn. Same-batch probe order and original per-fact provenance
were not established. The full methodology rubric was not in the prompt. New history and
peer packs have per-fact source dates; peer calculations now use matching fiscal periods.

Calibration now excludes gold observations and nests the training of threshold features.
A free corrected run on 1,665 non-gold observations has raw level MAE 1.919, calibrated MAE
1.492 and persistence MAE 0.053. It remains retrospective company-held-out validation.
All tested change detectors still choose persistence. The older n=1,696 study is historical
and its claim that gold never entered any fit was incorrect. Gold exposure cannot be undone.

## 1. The project in one paragraph

Research project at the Hasso Plattner Institute with Prof. Kay Giesecke (Stanford / HPI,
Advanced Financial Technologies Lab) and Xiaowei Ding (Nanjing University; formerly
Giesecke's PhD student at Stanford, then Morgan Stanley and MSCI). Goal in Giesecke's words:
build a system that does what a human credit rating analyst at Moody's does, following
Moody's published rating methodology. Concretely: read a company's SEC filings, extract the
inputs a Moody's sector scorecard needs, apply the scoring rules, produce a rating, and
measure how well it does against Moody's actual ratings. First sector: Moody's Retail and
Apparel methodology dated 12 September 2025 (methodologies/). Working mode: Robert sets the
questions, decisions, budgets and validations; Claude (Opus 5 until 2026-09-10, Fable 5.1
since 2026-09-11) writes the analysis, code and notes; every note carries an attribution
header saying what was verified against which source.

Related work in the same lab that the filing-parsing side would sit on: Bettencourt, Ding and
Giesecke, "The Stanford EDGAR Filings Dataset" (arXiv:2606.18192, June 2026), a
layout-faithful SEC filing parser and corpus with two benchmarks, EDGAR-Forecast (filing-
grounded numerical forecasting after a model's knowledge cutoff) and EDGAR-OCR.

## 2. Two things a new session must know immediately

**The GitHub repository is public.** `gh repo view robert-vetter/credit-rating-system`
reported `isPrivate: false` on 2026-09-12. The day-one brief and Xiaowei's suggestion both
called for a private repository, and the repository contains Moody's copyrighted methodology
PDF (methodologies/) and Moody's-derived rating data in committed files (evaluation/mapping.json,
goldset.json, decisions.jsonl, lists.md). Whether to make it private or remove the PDF is
Robert's decision; nobody has acted on it yet. The raw Moody's rating-history zips under
data/ are gitignored and not on GitHub.

**Repository update, 2026-09-12.** The calibration study, integrity repairs and current
specification/results are included in the repository update Robert requested. The main
README links the current results. Consult Git status and the remote for synchronization
state; do not assume an old working-tree description is current.

## 3. Correspondence requirements

*Updated by Codex at Robert's direction on 2026-09-12, verified against the email history
Robert supplied in this task. Original email dates were not supplied. This records research
requirements rather than publishing the full correspondence.*

Xiaowei asks for an LLM or agent, its documented training-data cutoff, a reasonably strong
prompt, the accuracy ratio on a truly post-cutoff cross-section, and detailed specifications.
He explicitly clarifies that the target is the outstanding rating after the cutoff, not
rating-change actions. Unchanged companies stay in the sample; persistence and the
changed/unchanged split expose inertia. Internet grounding and RAG must be off.

Giesecke warns that rating information can leak through channels beyond self-disclosures
in filings. Earlier project notes also record his request for an overarching analyst
architecture, including extraction, forecasting and discussion components.

Robert's previous update described the historical evaluation apparatus, the 50 validated
observations and the initial smoke tests. It did not provide the requested post-cutoff
accuracy number. Earlier he questioned the value of a cutoff based on memory outperforming
filing analysis. The corrected position is that a cutoff and memory probes are complementary;
a probe is not a substitute for post-cutoff evaluation.

The new reply should lead with the requested specification and pilot accuracy, explain
label staleness and sample attrition, then mention the integrity repairs and the separate
historical calibration study. Do not present that historical study as the post-cutoff test.
Do not call the seven disclosure labels a fully verified outstanding-rating cross-section.
A reply has been drafted at Robert's request; it has not been sent. Repository synchronization
is authorized by Robert's request to bring it up to date on 2026-09-12.

## 4. What has been done, in order

Dates are commit dates on `main`. Each line names where the evidence lives.

| Date | What | Where |
|---|---|---|
| 2026-08-07 | Repository skeleton | README.md, first commit |
| 2026-08-08 | First manual runs: Walmart and Kohl's, methodology plus one 10-K each; scorecard engine written | notes/walmart-first-test.md, notes/kohls-second-test.md, system/scorecard.py |
| 2026-08-10 | Blind test on five companies with rating disclosures stripped and a memory-only control: memory 0.40 notches MAE, documents 1.40 | notes/blind-test.md |
| 2026-08-11 | Experiment plan (persistence baseline, contamination measurement, two tasks); leakage audit (pricing grids in 10-Q exhibits, not every leak strippable) | docs/experiment-plan.md, docs/leakage-audit.md |
| 2026-08-12 | Assumptions review, register of corrections | docs/assumptions-review.md |
| 2026-08-15 | Primary experiment defined as history-conditioned update prediction; blinding mini-test (identity recovered from seven numbers); Moody's 17g-7 rating histories parsed, 12-month embargo measured | notes/blinding-minitest.md, notes/rating-history-file.md |
| 2026-08-16 | Manual scope pass over the sector frame | notes/rating-history-file.md |
| 2026-08-29 | Evaluation system built: Moody's-entity to SEC-filer mapping (186 entities, every pair decided and logged), 86 company folders, filings and self-disclosure verification, 3,646 quarterly observations (218 changed), runner, metrics, XBRL extraction check, smoke test (n = 2, about $1.60), gold set of 50 frozen, repository reorganised | evaluation/README.md, evaluation/goldset.json, notes/smoke-test.md |
| 2026-08-30 | Experiment 01: post-cutoff cross-section on Opus 4.5 and Opus 5, paired variants, under $5 | experiments/01-oos-cross-section/ |
| 2026-08-30 to 09-04 | Experiment 02: history pack, nine gold observations on Opus 4.5, $5.21; one leak found, fixed and disclosed; declared not out of sample after Robert's review | experiments/02-relative-with-history/ |
| 2026-09-05 | Experiment 03 designed and built: label harvester, quarterly XBRL, candidate proposer; 20 labels hand-confirmed by Robert, 16 selected under the $10 cap | experiments/03-oos-values-first/ |
| 2026-09-10 | Experiment 03 run: pre-flight, batch of 16, 11 lost to a max_tokens ceiling, two changed cases re-run, results on n = 7; cutoff evidence snapshot | experiments/03-oos-values-first/results.md, evidence/ |
| 2026-09-11 | Scorecard calibration study, numbers only, on 1,696 historical observations; XBRL fallback tags and raw companyfacts cache; debt double-count fix (uncommitted) | notes/scorecard-calibration.md, evaluation/calibration-summary.md, evaluation/pipeline/calibrate_scorecard.py |
| 2026-09-12 | This handover; Experiment 03 explained against Xiaowei's ask (section 9) | HANDOVER.md, AGENTS.md |

## 5. The evaluation apparatus (built, frozen, reusable)

- **Labels.** Moody's official Rule 17g-7 rating histories (free download with an account,
  data/moodys/, two zips dated 2026-08-11, content through 2025-08-28 because Moody's uses the
  full 12-month embargo the rule allows). Parsed into per-company ratings.json.
- **The join.** 186 Retail/Apparel Moody's entities mapped to SEC filers by stable IDs (Moody's
  OI to SEC CIK), every pair a logged decision (evaluation/mapping.json, decisions.jsonl,
  append-only), verified from both directions and through companies' own rating disclosures
  in their filings (evaluation/mapping-verification.md).
- **Company folders.** evaluation/companies/<slug>/ (86, gitignored, regenerable): identity,
  rating history, complete SEC filing manifest, downloaded documents, XBRL financials,
  observations.
- **Observations.** One per (company, calendar quarter end) from 2012-09-30 to 2025-06-30:
  label at t, persistence (label at the previous quarter end), changed flag, rating path to t,
  document references filed before t. 3,646 in total, 218 changed (6.0%), 3,084 in scope.
- **Gold set.** 50 hand-validated observations (30 changed, 20 unchanged), frozen 2026-08-29
  with an evidence chain per item (evaluation/goldset.json, goldset-review.md). The fixed labels remain unchanged. Experiment 02 used nine of them, and the original
  calibration study allowed gold rows into other folds. Future development excludes gold;
  earlier exposure cannot be undone.
- **Runner and metrics.** evaluation/pipeline/run_eval.py (documents redacted, no tools, one
  call per observation, full audit trail), score_run.py (changed-subset lift over persistence,
  direction accuracy, false-alarm rate, paired bootstrap), check_extraction.py (extraction
  scored against XBRL at zero model cost), history_pack.py (point-in-time history pack),
  peer_table.py, fetch_xbrl.py, calibrate_scorecard.py. The 13 pipeline steps are listed in
  run order in evaluation/README.md.
- **The system under test.** system/scorecard.py (deterministic scoring engine for the retail
  methodology, Exhibit 3 to 5 arithmetic), system/analyst.py (v0 single-call model half),
  system/redact.py (removes rating self-disclosures, logs what it cut). The experiment folders
  carry their own runners and prompts and import these.

## 6. The three experiments and the calibration study

**Experiment 01, out-of-sample cross-section, first pass (2026-08-30).** Opus 4.5 (training
cutoff Aug 2025) and Opus 5 (May 2026); one filing per company, no history; two prompt
variants; 24 memory probes, 6 paired document runs; spend under $4.78. Direct rating matched
persistence exactly (5 of 6); extract-then-score 2 of 6; the one genuine post-cutoff change
(Nike A1 to A2) was missed by everything. Probes: no post-cutoff knowledge; recalled ratings
often wrong.

**Experiment 02, relative rating with the issuer's history (2026-08-30 to 09-04).** Robert's
design decision: judge the rating relative to the issuer's own prior years. A history pack
(rating path, three prior fiscal years from XBRL, implied qualitative anchors, peer table) plus
the 10-K, nine gold observations (six changed), Opus 4.5, Batch API, $5.21 (21 cents over the
cap, cause found and fixed). The model's judgement after extracting and grading relative to
the anchors hit 6 of 9 exact, MAE 0.44 against persistence 3 of 9, MAE 0.89, no false alarm;
raw scorecard arithmetic was the worst channel (MAE 1.89, systematically too favourable). One
leak (Under Armour, quarter-start rating computed inclusively) found, fixed, disclosed.
**Not out of sample:** all nine observations predate the model's cutoff; the headline stands
only with that qualifier.

**Experiment 03, post-cutoff pilot (designed 2026-08-31, run 2026-09-10).** This is a
first measurement toward Xiaowei's question, with incomplete label-at-date verification. Opus 4.6 (training data cutoff Aug 2025, evidence
snapshot in evidence/), boundary B = 2025-09-30, every input document filed after B (in
practice the earliest is 2026-02-19), cross-section date 2026-08-29, labels from companies'
own post-B disclosures hand-read by Claude and confirmed by Robert (20 labels, two changes:
Nike A1 to A2 in Nov 2025, Qurate Caa1 to Caa3 in Oct 2025), history pack ending at the
Moody's file's true content end, no tools, separate probes in the same initial batch, Batch API without cache_control.
Sixteen observations submitted under the $10 cap; eleven returned no answer because the
9,000-token output ceiling was exhausted by thinking; ceiling raised to 24,000; the two changed
cases re-run; nine unchanged left unrun (X01 to X07, X10, X11); four labels never scheduled
(X08 Leslie's, X09 Levi Strauss, X13 PVH, X18 V.F.). Spend $8.74 of a $10 balance.

| Channel, n = 7 (2 changed, 5 unchanged) | Exact | Within 1 | MAE |
|---|---|---|---|
| Values first, corrected deterministic scorecard | 3/7 | 6/7 | 1.14 |
| Model's own judgement after extracting | 4/7 | 6/7 | 0.57 |
| Persistence | 5/7 | 6/7 | 0.43 |

The corrected arithmetic changes only Qurate, from B2 to Caa2. Its stale label and entity
alignment remain unresolved. False alarms on the five unchanged cases are 3 for the
scorecard, 1 for judgement and 0 for persistence. Without Qurate (n=6), MAEs are 1.17,
0.50 and 0.17 respectively. XBRL agreement is not an independent extraction test because
those figures were available in the model input. Probes did not demonstrate recall of the
new changed-case ratings; this does not prove absent contamination.

**Scorecard calibration, corrected 2026-09-12.** No model calls. Gold excluded before
fitting and development analysis, with nested training for threshold features. Over 1,665
historical observations, raw level MAE is 1.919, pooled calibrated MAE 1.492 and persistence
MAE 0.053. There are 78 changed and 1,587 unchanged observations. All four tested change
signals select persistence in every fold. This is retrospective cross-company validation,
not a time-ordered forecast test. Current tables: evaluation/calibration-summary.md. The
original n=1,696 study and its corrections remain in notes/scorecard-calibration.md.

## 7. Findings register (each with the note behind it)

1. Ratings are inert: 94% of quarters unchanged, so persistence is the baseline, never zero
   (docs/experiment-plan.md, evaluation/observations-summary.md).
2. Model memory beats naive document analysis on famous issuers (0.40 vs 1.40 MAE), so raw
   accuracy is uninterpretable without contamination measurement (notes/blind-test.md).
3. Blinding fails for covered issuers: identified from seven numbers (notes/blinding-minitest.md).
4. Filings disclose their own ratings; inputs must be redacted; the same channel yields labels
   and mapping verification (docs/leakage-audit.md, evaluation/mapping-verification.md).
5. The public Moody's file is embargoed twelve months, fully used (notes/rating-history-file.md).
6. Without history, direct rating equals persistence out of sample (Experiment 01).
7. With the issuer's history and a relative framing, the post-extraction judgement moved off
   persistence in the right direction, in sample (Experiment 02).
8. The post-cutoff pilot does not beat persistence overall. Label validity, prompt rubric
   coverage and independent extraction validation remain open (Experiment 03).
9. Historical calibration reduces level error, but the tested annual-number signals do
   not improve on persistence. Accounting-era associations are descriptive (calibration note).
10. Model memory of ratings is confidently wrong off the famous names (all probe rounds).

## 8. Rules that govern the work (do not relax them silently)

- **Budget.** Robert sets a dollar cap per experiment ($5, $5, $10 so far). The runner prices
  the exact worst case from a free count_tokens pass and refuses to submit above the cap. No
  paid call without a cap Robert approved. The API prepaid balance was about $1.26 after
  Experiment 03; Robert tops up before any paid run.
- **Leakage discipline.** No tools array (no retrieval). Rating self-disclosures redacted,
  removed lines stored. 8-Ks are used for label harvesting only, never as model input.
  Exhibits are never used (pricing grids). Every input document, pack fact and peer fact
  carries a date and is asserted against the boundary; the checks are written to audit.json.
  A memory probe per observation runs before any documents. The model's training cutoff is
  quoted from the vendor's documentation with a dated snapshot in evidence/.
- **Point in time.** A fiscal year's XBRL figures are used at t only if filed on or before t;
  restatements are not applied retroactively. The rating in effect entering a quarter is the
  rating as of the day before the quarter starts (an inclusive date leaked once).
- **Gold set.** Frozen; never tuned on; one shot per variant; iteration happens on non-gold
  observations. Calibration fits must exclude gold before any gold claim.
- **Records.** Decisions go to decisions.md in the experiment folder with owner and date;
  mapping and gold decisions are append-only JSON. Every script states purpose, inputs and
  outputs in its docstring and is listed with its pipeline position in evaluation/README.md.
  Prompts are stored verbatim. Results notes report every number next to persistence, split
  changed versus unchanged, and disclose every mistake with the rule that now prevents it.
- **Style.** Plain English, short sentences, no em dashes, no emoji or badges, no marketing
  words, no files nobody asked for, write only what is true now and say when something is
  undecided. Attribution header on every note. Commit messages describe the deliverable in one
  line, no attribution trailers.

## 9. Xiaowei's first-step ask: current answer

Target: outstanding rating at August 29, 2026. Model: Opus 4.6, documented training cutoff
August 2025. Input primary filings fall after September 30, 2025 and on/before the target
date; older history is supplied explicitly. No tools or RAG. Full executed specification:
experiments/03-oos-values-first/README.md.

The seven-success disclosure-label pilot has exact accuracy 43% for the scorecard, 57% for
model judgement and 71% for persistence. Corrected MAEs are 1.14, 0.57 and 0.43. One stale
label requires a without-Qurate sensitivity: 50%, 67%, 83% exact on six cases and MAEs
1.17, 0.50 and 0.17. This does not certify the other six labels. The response must explain
small-sample and missing-response selection, and distinguish a post-cutoff rating-state
reconstruction from a forecast made before a rating action.

Robert closed the paid experiment at seven successes. The thirteen remaining cases will
not be run. Next work is the proposed analyst architecture and local evidence/TTM baseline;
new paid work or human label decisions require separate authorization.

## 10. Open items and dependencies

| Item | Owner | State |
|---|---|---|
| Repository visibility (public, contains Moody's PDF) | Robert | flagged 2026-09-12, undecided |
| Repository synchronization | Codex, directed by Robert | Documentation and integrity/calibration changes consolidated in the 2026-09-12 update; verify remote with Git |
| Experiment 03 completion, 13 observations | Robert | Closed 2026-09-12 at Robert's request. Do not run or request a top-up; see D11. |
| Send specification and results to the lab | Robert | Reply requested and drafted here; not sent |
| Analyst architecture | Robert / lab | Proposal in docs/oos-integrity-review.md; prototype and TTM baseline not built |
| Sector strategy: methodology-faithful per sector versus sector-agnostic prediction | Giesecke / Ding | open |
| Whether peer ratings (not only peer figures) are admissible input | Giesecke / Ding | open |
| Five scope calls: CVS, Samsonite, Good Sam, Amazon, Sherwin-Williams | Robert | open, currently "uncertain" or "out" in the frame |
| The lab's dataset: firms, years, sectors, rating type | Ding | unknown; blocks only the post-cutoff arm's changed-case count |
| Moody's Credit Opinions via Robert's account (real factor grids) | Robert | was being checked, outcome not recorded |
| AWS Bedrock access for older models with earlier cutoffs (Exp 03, D8) | Robert | parked |
| Moody's terms of use for the documents | Robert | open |
| Trailing-twelve-month numbers channel from quarterly XBRL | any session | proposed in the calibration note, not built |
| Lease capitalisation before 2019 (Moody's cross-sector adjustments) | any session | proposed, the multiple must be read from Moody's document first |

## 11. Practical: environment, data, commands

- Machine: macOS, Python 3.13.7. Packages present: anthropic 1.2.0, httpx2, numpy 2.3.3,
  scipy 1.17.1, scikit-learn 1.8.0, pandas 2.3.2. The `openai` package is not installed.
- Secrets: `.env` in the repository root (gitignored) holds `ANTHROPIC_API_KEY` only. The
  experiment runners read it from the environment (`set -a; source .env; set +a`).
- Data that cannot be regenerated by a script: the two Moody's 17g-7 zips (downloaded with
  Robert's Moody's account, not redistributable). Everything else under data/ and
  evaluation/companies/ regenerates from the pipeline (data/README.md lists sources and dates).
  Sizes: data/moodys 156 MB, data/edgar 257 MB (includes the 218 MB companyfacts cache),
  evaluation/companies 1.0 GB.
- Committed records that are the human input and must not be regenerated: evaluation/mapping.json,
  decisions.jsonl, goldset.json, goldset-review.md; every experiment's candidates.json,
  decisions.md and prompts/.
- Commands (from the repository root):
  - `python3 evaluation/pipeline/calibrate_scorecard.py` : the numbers-only study, no cost.
  - `python3 evaluation/pipeline/fetch_xbrl.py` : re-extract XBRL from the cache; `--refresh` re-downloads.
  - `python3 evaluation/pipeline/run_eval.py --dry-run ...` : cost of a selection, no spend (see evaluation/README.md).
  - `python3 experiments/03-oos-values-first/run_batch.py --dry` : builds every request, counts tokens, prices the worst case, no spend; paid `--submit`, `--rerun` and the miniature preflight are closed by D11. Use the offline audit for saved results.
  - `python3 evaluation/pipeline/history_pack.py <slug> <date>` : prints a history pack.
- Run artefacts: experiments/*/runs/ and evaluation/runs/ are gitignored; each holds the
  verbatim requests, raw outputs, audit.json with the date checks, and results.json. Batch IDs
  in LAST_BATCH files. Experiment 03 batches: msgbatch_01EwnHhsKjahuwhmL8S5h2Sx (16) and
  msgbatch_01QsBQnMF1itHj1Ysz3jguKZ (the two changed cases).
- Identifiers: X01 to X20 are Experiment 03 candidates (candidates.json); G01 to G50 are gold
  items; slugs such as `kohl-s` name company folders; Moody's OI and SEC CIK are the join keys.
- The parent folder /Users/robert/Developer/giesecke holds the day-one brief
  (session-brief.md, superseded by this file) and an unrelated screenshot in personal/.

## 12. If the next session uses OpenAI models

Nothing in the evaluation apparatus depends on the model vendor; the deterministic parts
(mapping, observations, gold set, scorecard, redaction, XBRL, calibration, metrics) run as
they are. The model-facing code is Anthropic-specific and small:

- `system/analyst.py`, `evaluation/pipeline/run_eval.py`, and the three experiment runners
  use the `anthropic` client: `messages.create` with a JSON-schema structured output
  (`output_config`), `messages.count_tokens` for the free pre-flight, `messages.batches` for
  the 50% batch discount, `thinking: adaptive` with `output_config.effort`, and the
  `cache_control` lesson (do not use it in batch). Port these call sites; keep the request
  shape (system prompt, documents, history pack, peer table, task, schema) and the stored
  artefacts (requests verbatim, raw outputs, audit.json, results.json) identical so the two
  vendors' results are comparable.
- Preserve, without exception: no tools or retrieval of any kind in the request; the
  boundary rule (documents and labels dated more than one month after the model's documented
  cutoff); the per-observation memory probe before any documents; redaction; the cost guard
  against a cap Robert approved; the cutoff evidence snapshot.
- Cutoff: OpenAI documents a knowledge cutoff per model on its model pages. Record it
  verbatim with the retrieval date in a new `experiments/04-*/evidence/` file, as done for
  Opus 4.6. If the chosen model's cutoff is later than Aug 2025, the out-of-sample window
  shrinks accordingly and the two known post-cutoff rating changes (Oct and Nov 2025) may fall
  inside training data; check the action dates in candidates.json against the new boundary
  before claiming anything. The label window currently ends 2026-08-29; it can be extended by
  re-running fetch_filings.py and harvest_labels.py for filings after that date, with every
  new label hand-read as before.
- Start a new experiment folder (04-...) with README (specification), decisions.md, prompts/,
  runner, runs/, results.md, in the same shape as 03. Do not edit 03's records.
- Install and key: `pip install openai`, add `OPENAI_API_KEY` to `.env`. Set a cap first.

## 13. Change log of this file

- 2026-09-12: created. State: three experiments done; calibration study uncommitted; Exp 03
  at n = 7 with 13 labels runnable after top-up; repository found public; balance about $1.26.
- 2026-09-12, Codex at Robert's direction: stopped paid Experiment 03 completion (D11);
  added the offline integrity review and regression checks; corrected negative leverage and
  net-cash scoring, date/peer provenance, extraction date filtering and calibration holdout
  handling. Replayed saved requests and reran calibration locally. Original paid records and
  human decisions unchanged. Architecture proposal is in docs/oos-integrity-review.md.
- 2026-09-12, Codex at Robert's direction: incorporated the supplied email history as
  research requirements, without reproducing the full correspondence. Rewrote the main
  README and Experiment 03 pages around outstanding-rating accuracy, executed controls,
  corrected scores and label limitations. Prepared the lab reply and repository update. Verified all 10 regressions, saved-request
  replay, documentation links and unchanged protected artifacts before committing. Raw
  run directories remain ignored; the lab reply has not been sent.
