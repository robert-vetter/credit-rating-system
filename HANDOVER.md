# Handover: where this project stands, how it got here, and what is open

*Written 2026-09-12 by Claude (Fable 5.1) at Robert Vetter's request, so that a new session in
any tool (Claude, OpenAI, a human) can pick the project up without prior context. Everything
here is either in the repository or in Robert's chat with Claude; where a fact comes from
correspondence that is not in the repository, that is said. Read this file first, then
README.md, then the experiment folders. Keep this file current: append a dated entry to
section 13 whenever the state changes.*

## Latest increment: reply to the lab's eight-point review, 2026-09-18

*Claude (Fable 5.1), directed by Robert Vetter. Verified against the executed Experiment 04
specification and results, candidates.json, the frozen token counts, the local 17g-7 records,
the Experiment 05 study record, system/scorecard.py, and the vendor and agency pages named in
the new files with their retrieval dates. No label, run record or result changed.*

Xiaowei replied to the 2026-09-17 folder with eight points (input-data table, imbalance, a
top commercial model, filing and action dates in one table with day precision, the Signet
sentence, one deterministic calculation, the meaning of hand-labelled data, a specification)
and framed the main problem as decipher the Moody's logic from real data with LLMs as a tool,
then encode it into agents. New files, committed and pushed to public GitHub main on 2026-09-18 at Robert's instruction; the email is not sent:
`docs/lab-update-2026-09-18/SPECIFICATION.md` (the experiment as executed, data tables, the
per-issuer table with prior-rating type and date, filings, label, action and results, the ten
input definitions, the calculation, controls, defects, nine decisions for consensus) and
`docs/lab-update-2026-09-18/README.md` (point-by-point answers with the Signet worked
calculation and the decipher/encode status table). The reply draft is outside the repository
at `/Users/robert/Developer/giesecke/lab-reply-2026-09-18.txt`; the correspondence log and
Xiaowei's expectations are in `/Users/robert/Developer/giesecke/correspondence/`.

External facts read on 2026-09-18 and not yet snapshotted under an `evidence/` folder: Nike's
downgrade is dated 12 November 2025 (Moody's release, ratings.moodys.com/ratings-news/454361);
GPT-5.2's vendor page states a 31 August 2025 knowledge cutoff, 400,000 context, $1.75/$14
per million tokens; GPT-5.5's states 1 December 2025. Qurate's October 2025 action day was
not found without the Moody's login. Proposed and not authorized: GPT-5.2 on the frozen
Experiment 04 inputs as Experiment 07, three replicates, cap about $25. The folder is
on public GitHub main; the repository itself is still public, which remains Robert's open decision.

## Latest result: accounting interventions, 2026-09-17

*OpenAI Codex, directed by Robert Vetter. Verified against original current-arm outputs,
23 exact filing operands and deterministic replay; source interpretations pending human review.*

Robert asked for substantive new research before finalizing the lab reply. Experiment05
(`experiments/05-accounting-interventions/`) is complete locally: nine current-arm responses
for Walmart/Nike/Signet, fixed original qualitative grades, original/interest/debt/other/
combined conditions, no new model calls. The Signet debt intervention is a recognized-lease
floor, not certified total adjusted debt; Nike operating income is a declared subtotal
sensitivity, not an agency-adjustment claim. Gross interest stays unresolved for Nike/Signet.

Main results: Walmart gross expense2799 versus net2431 changes coverage7.1518x→6.2115x but
no notch; Signet r3 lease inclusion moves Aa2→A1 (two notches). Combined issuer consensuses
remain Aa3/Aa3/A3, 0/3 exact and MAE3.000 versus persistence2/3 and0.333. Repetition-level
MAE29/9→27/9, entirely the one Signet response; not nine independent observations. After
supported interventions Signet and Walmart have identical within-issuer financial vectors;
stored grades alone yield three-notch and one-notch within-issuer spreads respectively.
This isolates grading instability in the fixed calculation, not grade correctness or all
remaining label error. Nike interest remains unequal, so no full grade attribution there.

Saved new local output: `evaluation/runs/accounting-interventions-2026-09-17/study.json`
and `results.md`. Source choices are in `interventions.json`, fixed before replacement
scoring; spread diagnostics are a disclosed follow-up after the initial computation. All21
study tests,19 prototype tests and61 old regressions pass. No edits to old labels/runs,
scorecard/caches; no paid calls, downloads, commit, push or external publication. Next useful
study distinguishes insufficient evidence from inconsistent rubric application using fixed
financial inputs AND evidence, independent reviewer assessments/ranges and separate reference
agreement/repeatability measures. Reference annotations are not yet available; do not infer them
from agency ratings or claim lower variability alone is improvement. The lab packet/email should lead with the measured study,
not retrospective prompt criticism; material limitations remain documented.

## Earlier increment, 2026-09-17

*Written by OpenAI Codex, directed by Robert Vetter. Verified against local raw facts,
matching cached numeric filing elements and offline tests. Human accounting review pending.*

Robert has sent the earlier email and received a request from Xiaowei for clearer tables
of cutoff dates, filing dates, rating changes and results. The immediate approved work is
an offline accounting/evidence prototype, not a full agent or new paid experiment.

New modules `system/evidence_ledger.py`, `system/accounting_checks.py` and
`evaluation/pipeline/accounting_benchmark.py` produce a three-case development review
for Walmart, Nike and Signet at 2026-08-29. Existing gold, mapping, candidate labels,
run bodies, scoring code and compact financial caches are not rewritten. The new reader
uses true elapsed calendar days, while the legacy duration approximation remains unchanged.
See `evaluation/README.md` for commands and test scope.

The prototype separates source matching and arithmetic checks from accounting adjudication.
All interpretations remain machine-proposed, pending Robert's review. It reports conflicting
Walmart revenue concepts, gross/net/cash-interest distinctions, and debt/lease component
reconciliations without asserting a complete adjusted total or final rating. Full TTM and
rating-model comparisons are later work. These are known development issuers, not a holdout.

For the next email, Robert is unsure whether Xiaowei or Prof. Giesecke previously mentioned
hand-labelled data. Ask whether such data exists and is accessible; do not assert it does:
“I may be remembering our earlier discussion incorrectly: do you or Prof. Giesecke have
any hand-labelled credit-analysis examples, such as checked financial inputs or factor
assessments, that might be available for this research? Separately, do we have access to
complete dated rating histories that would let me verify the outstanding ratings at the
evaluation date?” A later task in this session prepared a full English reply at
`/Users/robert/Developer/giesecke/lab-reply-2026-09-17.txt`, outside the public repository.
It is not sent. Its GitHub URL is a future destination until the local packet is approved,
committed/pushed and checked for recipient access.

The 2026-09-13 snapshot below is historical, including its unsent-email and unpushed-commit
statements. At the start of this increment local main matched origin/main at 0588c64;
no network synchronization or repository-visibility change was performed.

## State of the project, 2026-09-13 (historical snapshot)

*Written by Claude (Opus 5) at Robert Vetter's direction on 2026-09-13, as a gapless handover
for a new session in any tool. It replaces the earlier continuation sections at the top of
this file; those, and Codex's note below, remain valid history. Everything here was measured
or decided on 2026-09-12 and 2026-09-13 and supersedes older statements where they conflict.*

**Where the project stands.** Four experiments are done. The fourth, Experiment 04 Arm 1, was
specified, independently reviewed, refused once, repaired, authorized, executed, independently
audited after the run, and corrected. It is the current answer to Xiaowei's first-step ask
(section 9). No work is in flight. Nothing has been sent to the lab. Five commits sit on local
`main` and are not pushed; the GitHub repository is public and the visibility question is still
open (section 2).

**The result, Experiment 04 Arm 1, consensus of three replicates per issuer.** Model
Qwen3-235B-A22B-Instruct-2507, open weights, public checkpoint of 2025-07-21, served fp8 by
DeepInfra through OpenRouter. Labels are the issuers' own rating disclosures in filings after
the 2025-09-30 boundary, target date 2026-08-29.

| Cohort, current inputs | Judgement exact, MAE | Scorecard exact, MAE | Persistence exact, MAE |
|---|---|---|---|
| Primary 19 (Qurate held out as a diagnostic) | 17/19, 0.11 | 3/19, 1.84 | 18/19, 0.05 |
| Post-hoc 18, without Kohl's | 16/18, 0.11 | 3/18, 1.78 | 17/18, 0.06 |
| Post-hoc 17, without Kohl's and Dollar General | 16/17, 0.06 | 3/17, 1.71 | 16/17, 0.06 |
| All 20 | 17/20, 0.20 | 3/20, 1.80 | 18/20, 0.15 |

Neither channel beats persistence on any cohort. The judgement channel returned the supplied
prior in 56 of 60 answers and all three replicates returned it on 18 of 20 issuers; it made one
false alarm (Dollar General) and missed both rating changes. The scorecard channel runs 1.23
notches favourable on average and disagrees with persistence on 15 of 18 unchanged issuers. On
the seven issuers Opus 4.6 scored in Experiment 03, with byte-identical supplied information,
two of Qwen's three judgement replicates reproduce Opus's aggregate numbers (4/7 exact, MAE
0.57) with different mistakes, and its scorecard is worse. Full tables, coverage, every failed
request and the limitations are in `experiments/04-open-weight-cross-section/results.md`.

**The two findings that matter more than the numbers.** First, the post-run audit
(`experiments/04-open-weight-cross-section/review-codex-2026-09-13.md`) found that Kohl's
disclosed B2 rating survived redaction in all three of its replicates: the filing renders its
rating table one cell per line, the redactor removed the agency line and stopped at the row
label, and a lone "B2" was not recognised as a rating row. A follow-up scan found Dollar
General's short-term rating and outlook cells the same way. The frozen bodies are unchanged and
the leak is disclosed with post-hoc sensitivities. Second, the extracted scorecard inputs are
consistent across replicates without being correct: net interest income used as interest
expense (Nike, Signet), lease liabilities dropped from debt (Signet, which returned zero debt),
pretax income used as operating income (Nike), a wrong fiscal-year date (Gap). Consistency is
not extraction accuracy, and the favourable bias is not only missing Moody's adjustments.

**Repairs made on 2026-09-13, all tested, none retroactive to the paid bodies.**

| Repair | Where |
|---|---|
| Structural second pass that removes rating-table blocks and orphan symbol cells, plus a scan that must return nothing before a run | `system/redact.py`, functions `redact_v2` and `rating_fragments`; the original `redact` is untouched so Experiment 03's replay stays byte exact |
| Kohl's and Dollar General cases as regressions, and a check that no cached filing of the run has a fragment after the second pass | `experiments/04-open-weight-cross-section/test_runner.py`, class `RedactionV2` |
| An error response that carries usage or an id is never released as unbilled; it is reconciled and halts, or stays unresolved | `run_openrouter.py`, `_settle` |
| A charge above its reservation, or an exposure above the cap, halts the run | `run_openrouter.py`, after the reconcile event |
| Every process performs its own live price check; a recorded check from an earlier process does not count | `run_openrouter.py`, `guards` and `live_price_check` |
| Raw generation payloads archived next to the responses | `run_openrouter.py`, `_generation` |
| Exact MAE from the error sum (a double rounding had printed 2/19 as 0.10), matched persistence baselines on the valid subset, and the post-hoc cohorts | `report.py`, `run_openrouter.metrics` and `score` |

51 Experiment 04 tests and 10 Experiment 03 regressions pass. The Experiment 03 offline replay
still reproduces all 18 saved document packages exactly.

**What exists in the Experiment 04 folder.**

| File | What it is |
|---|---|
| `RUN-SPEC.md` | the specification as frozen and executed, with the incidents and repairs in section 12 |
| `results.md` | the results note, corrected after the audit, with the sixteen corrections listed at the end |
| `decisions.md` | D1 to D12; D5 to D10 and D12 decided by Robert on 2026-09-12, D11 (Arm 2) still open |
| `authorization.json` | the $3.00 cap and the scope, bound to the manifest hash; the runner refuses to dispatch without it |
| `review-codex-2026-09-12.md` | the pre-run review that refused the first specification and set twelve acceptance gates |
| `review-codex-2026-09-13.md` | the post-run audit: reconstructed tables, the leak, the guard defects, sixteen corrections |
| `prepare_inputs.py` | offline preparation: cohort, documents, packs, bodies, rendered token counts, hashes, manifest, free pre-flight |
| `run_openrouter.py` | the runner: ledger, reservations, guards, dispatch, validation, scoring, gates |
| `test_runner.py` | 51 acceptance tests against the production dispatch path with a fake transport |
| `legacy_provenance.py`, `legacy_builders/` | the saved-input control: the vendored 2026-09-10 builders and the per-figure source dates |
| `report.py` | the tables in results.md, from `results/scores.json` |
| `count_tokens_qwen.py`, `evidence/` | the token evidence and the cutoff, model-list and per-provider snapshots |

**The run record.** `experiments/04-open-weight-cross-section/runs/EXP04-ARM1-A1/`, 55 MB,
gitignored, on this machine only. It holds `manifest.json` and `bodies/` (the frozen plan and
every body sent), `ledger.jsonl` (555 events: every reservation, dispatch, charge, failure,
halt and reviewer note), `responses/` (raw bytes of all 104 HTTP responses, saved before
parsing), `audit/` (per-issuer document and pack provenance, the saved-input evidence, removed
lines, probes, residual scan, hashes, environment), `gates/`, `probe_review.json`,
`pilot_review.json`, `results/` (attempts, flat records, consensus, scores, report) and the
execution log. A fresh clone does not contain it; the results notes are the public record.

**Money.** Experiment 04 spent $1.242279 in reconciled charges for 104 responses and holds
$0.141521 for seven attempts that failed before any HTTP response, so $1.383800 of the $3.00
cap. The OpenRouter balance is about $6.31 (usage 48.69 of 55 credits). The Anthropic prepaid
balance is about $1.26 and Experiment 03 is closed to paid calls by decision D11. No paid call
is authorized now: authorization EXP04-ARM1-A1 covered exactly the plan that ran.

**What a new session must not do without a fresh decision from Robert.** Do not make any paid
model call. Do not edit `evaluation/mapping.json`, `decisions.jsonl`, `goldset.json`, any
`candidates.json`, `label-review.md`, the `prompts/` folders, the saved Experiment 03 batch
artefacts, or anything under `runs/`. Do not reopen Experiment 03's paid-call guard. Do not
push, and do not send anything to the lab. Full rules in `AGENTS.md` and section 8.

**Verify the state offline, from the repository root.**

```
python3 -m unittest discover -s experiments/03-oos-values-first -p 'test_*.py' -v
cd experiments/04-open-weight-cross-section && python3 -m unittest -v test_runner
python3 experiments/03-oos-values-first/audit_saved_run.py
python3 experiments/04-open-weight-cross-section/legacy_provenance.py X12 X14 X15 X16 X17 X19 X20
python3 experiments/04-open-weight-cross-section/run_openrouter.py score
python3 experiments/04-open-weight-cross-section/report.py
```

The last two write into the run directory and need it present. `run_openrouter.py submit` is
the only path that spends money; it refuses without the authorization file and a matching
manifest hash.

**Open, and all Robert's.**

1. Send the lab update. The final draft in Robert's voice is
   `/Users/robert/Developer/giesecke/lab-update-final-2026-09-13.md`, outside the repository,
   unsent, with the attachment list at the end. It supersedes the three earlier drafts.
2. Repository visibility. It is public and holds Moody's copyrighted methodology PDF and
   Moody's-derived rating data. Five commits are unpushed. Decide before pushing or sharing a
   link; the email attaches files instead.
3. What follows Experiment 04. The evidence points at the architecture draft
   (`docs/architecture-codex-2026-09-13.md`), whose free first steps are closing the redaction
   and billing controls, then the evidence ledger and the trailing-twelve-month accounting
   baseline, then a rubric and event specification. A second model, more replicates and Arm 2
   (D11) are not authorized.
4. The lab's rating data. Dated Moody's histories for September 2025 to August 2026 with legal
   entity, rating type, actions and withdrawals would verify these disclosure labels and give
   the change decision more than two cases. The email asks for it.

**Files outside the repository** in `/Users/robert/Developer/giesecke/`: the day-one brief
(`session-brief.md`, superseded), the two Codex briefs of 2026-09-12 and 2026-09-13, three
superseded lab drafts, and `lab-update-final-2026-09-13.md`. They live outside because the
repository is public and they carry correspondence.

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

**The last five commits are local only.** On 2026-09-13 local `main` is five commits ahead of
`origin/main`: the whole of Experiment 04, its two reviews, the corrections and the repairs.
They were not pushed because of the visibility question above. The working tree is clean.
Everything through commit f93c0c5 (the calibration study, the integrity repairs and the
Experiment 03 pages) is on the remote. Always consult Git status rather than an older
description.

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
| 2026-09-12 | Codex's integrity review: negative-EBITDA scoring bug (three notches on one issuer), net-cash sign, rounding, unstaged probes, gold rows in the calibration folds, reusable paid cap; repairs made and Experiment 03 closed to paid calls | docs/oos-integrity-review.md, experiments/03-oos-values-first/audit_saved_run.py |
| 2026-09-12 | Experiment 04 designed: the capability-versus-labels trade-off measured, Qwen3-235B-2507 chosen, the Arm 1 specification written, corrected twice, then refused by Codex's review with twelve acceptance gates; Robert decided D5 to D12 | experiments/04-open-weight-cross-section/, review-codex-2026-09-12.md |
| 2026-09-13 | Experiment 04 Arm 1 implemented to the gates and executed: 111 dispatches, 99 valid, $1.38 of a $3.00 cap, three hours; then audited after the run, which found a redaction failure and two billing-guard defects; corrections and repairs applied | experiments/04-open-weight-cross-section/results.md, review-codex-2026-09-13.md |

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

## 6. The four experiments and the calibration study

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

**Experiment 04, Arm 1, post-release cross-section on an open-weight model (run 2026-09-13).**
Qwen3-235B-A22B-Instruct-2507, public checkpoint 2025-07-21, DeepInfra fp8 through OpenRouter,
temperature 0, seed 20260912, three replicates per issuer, one memory probe per issuer first.
Same boundary, labels, prompts and scoring arithmetic as Experiment 03. Two arms: all 20
confirmed issuers on current, repaired history packs, and the seven issuers Opus scored on the
exact saved Experiment 03 inputs. 20 of 20 probes and 79 of 81 document requests valid;
$1.242279 committed plus $0.141521 held, against a $3.00 cap.

| Channel, primary cohort of 19, consensus | Exact | Within 1 | MAE | False alarms on 18 unchanged |
|---|---|---|---|---|
| Model judgement | 17/19 | 19/19 | 0.11 | 1 |
| Scorecard from extracted inputs | 3/19 | 10/19 | 1.84 | 15 |
| Persistence | 18/19 | 19/19 | 0.05 | 0 |

Neither channel beats persistence. Both rating changes were missed by the judgement channel,
which returned the supplied prior in 56 of 60 answers. The post-run audit found that Kohl's
disclosed rating survived redaction in all three of its replicates, so a post-hoc sensitivity
without it gives judgement 16/18 against persistence 17/18, and without Dollar General's
surviving short-term rating cells 16/17 against 16/17. The scorecard channel is 1.23 notches
favourable on average, with documented accounting-concept errors in its inputs. Full note:
experiments/04-open-weight-cross-section/results.md; the audit: review-codex-2026-09-13.md.

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
11. Given the issuer's own prior rating, the model returns it: 56 of 60 post-cutoff answers and
    all three replicates on 18 of 20 issuers, on a frontier and an open-weight model alike.
    Anchoring is the plausible explanation and is untested; no prior-withheld control has run
    (Experiment 04).
12. A 235B open-weight model matched the frontier model's aggregate judgement accuracy on
    byte-identical inputs at a fraction of the cost, which makes full cross-sections and
    replicates affordable. Its extracted scorecard inputs were worse (Experiment 04).
13. Extracted figures repeat across replicates without being right: net interest income used as
    interest expense, lease liabilities dropped from debt, pretax income used as operating
    income. Consistency is not extraction accuracy (Experiment 04 audit).
14. Lexical redaction is not enough. Filings render rating tables one cell per line, and a lone
    rating symbol survived an agency-name-based stripper and its residual scan. Redaction needs
    structure-aware removal and an independent scan of the assembled input (Experiment 04 audit,
    repaired in system/redact.py).

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
not be run on Opus.

**Experiment 04, Arm 1 (2026-09-13) extends the answer to 19 disclosure labels** on
Qwen3-235B-A22B-Instruct-2507 (public checkpoint of 2025-07-21, DeepInfra fp8 through
OpenRouter), three replicates each: judgement 17/19 exact, MAE 0.11; scorecard 3/19, MAE
1.84; persistence 18/19, MAE 0.05; one issuer's disclosed rating survived redaction, and
without it the sensitivity is 16/18 against persistence's 17/18. Both rating changes were
missed by the judgement channel. On the seven issuers Opus scored, the same supplied
information gave the same aggregate judgement accuracy in two of three replicates (4/7, MAE
0.57). Full tables, coverage, the audit and limitations:
experiments/04-open-weight-cross-section/results.md and review-codex-2026-09-13.md.
Next work needs Robert's decision; new paid work or label decisions require separate
authorization.

## 10. Open items and dependencies

| Item | Owner | State |
|---|---|---|
| Repository visibility (public, contains Moody's PDF) | Robert | flagged 2026-09-12, undecided; five commits are unpushed for this reason |
| Repository synchronization | Robert | local `main` is five commits ahead of `origin/main` as of 2026-09-13; do not push without the visibility decision |
| Experiment 03 completion, 13 observations | Robert | Closed 2026-09-12 at Robert's request. Do not run or request a top-up; see D11. |
| Send specification and results to the lab | Robert | Final draft of 2026-09-13 in Robert's voice, outside the repository, with the attachment list; not sent |
| Experiment 04, Arm 1 | done 2026-09-13 | 79 of 81 document requests valid, $1.38 of the $3.00 cap; audited, corrected; a second model, more replicates and Arm 2 (D11) not authorized |
| Analyst architecture | Robert / lab | First draft from the evidence in docs/architecture-codex-2026-09-13.md (supersedes docs/architecture.md); nothing built yet; its free first steps are the redaction and billing controls, then the evidence ledger and TTM accounting baseline |
| Verified outstanding labels for the post-cutoff window | Robert / Ding | the disclosure labels are unverified at the observation date; the lab's dated histories would settle it and give the change decision more cases |
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

- Machine: macOS, Python 3.13.7. Packages present: anthropic 1.2.0, httpx 0.28.1, httpx2,
  jsonschema 4.25.1, transformers 4.57.6, tokenizers 0.22.2, numpy 2.3.3, scipy 1.17.1,
  scikit-learn 1.8.0, pandas 2.3.2. The `openai` package is not installed and is not needed:
  Experiment 04 talks to OpenRouter over HTTPS with `httpx`.
- Secrets: `.env` in the repository root (gitignored) holds `ANTHROPIC_API_KEY` and
  `OPEN_ROUTER_API_KEY` (that spelling). The runners read them from the environment
  (`set -a; source .env; set +a`) or from `.env` directly. Never print a key.
- The Qwen tokenizer is in the Hugging Face cache, revision
  `ac9c66cc9b46af7306746a9250f23d47083d689e`, and every Experiment 04 script runs with
  `HF_HUB_OFFLINE=1`, so token counting needs no network.
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
  - `python3 experiments/04-open-weight-cross-section/prepare_inputs.py` : rebuilds every
    Experiment 04 body, hash, token count and the manifest, offline, no spend. It refuses if a
    rating fragment survives redaction.
  - `python3 experiments/04-open-weight-cross-section/run_openrouter.py gates` : the acceptance
    gates and the test suite, offline. `status` reads the ledger. `score` and `report.py`
    rebuild the tables. `submit` is the only paid path and needs `authorization.json`.
  - `python3 experiments/04-open-weight-cross-section/legacy_provenance.py <ids>` : proves the
    saved Experiment 03 inputs reconstruct byte for byte and prints their source dates.
- Run artefacts: experiments/*/runs/ and evaluation/runs/ are gitignored; each holds the
  verbatim requests, raw outputs, audit.json with the date checks, and results.json. Batch IDs
  in LAST_BATCH files. Experiment 03 batches: msgbatch_01EwnHhsKjahuwhmL8S5h2Sx (16) and
  msgbatch_01QsBQnMF1itHj1Ysz3jguKZ (the two changed cases).
- Identifiers: X01 to X20 are Experiment 03 candidates (candidates.json); G01 to G50 are gold
  items; slugs such as `kohl-s` name company folders; Moody's OI and SEC CIK are the join keys.
- The parent folder /Users/robert/Developer/giesecke holds the day-one brief
  (session-brief.md, superseded by this file) and an unrelated screenshot in personal/.

## 12. If the next session uses another vendor

A working non-Anthropic path already exists: `experiments/04-open-weight-cross-section/`
reaches an open-weight model through OpenRouter with `httpx`, an OpenAI-shaped chat
completions body, `response_format` for the JSON schema, and pinned provider routing. Reuse
`prepare_inputs.py` and `run_openrouter.py` rather than writing a new runner, and keep the
guards: the authorization file bound to a manifest hash, reservations before dispatch, price
ceilings, a live price check per process, staged memory probes, halts on anything unexplained,
and a raw record of every response. The notes below about the Anthropic call sites still apply
to `system/analyst.py`, `evaluation/pipeline/run_eval.py` and the Experiment 01 to 03 runners.

### If the next session uses OpenAI models

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

- 2026-09-18, Claude (Fable 5.1) at Robert's direction: wrote the reply package to Xiaowei's
  eight-point review: `docs/lab-update-2026-09-18/SPECIFICATION.md` and `README.md`, the
  email draft and the private correspondence log outside the repository. Read Nike's action
  date and the GPT-5.2 and GPT-5.5 cutoffs from public pages (recorded inline with dates).
  No model calls, no spend, no label or result change. Committed and pushed at Robert's
  instruction the same day; the email is not sent.
- 2026-09-17, publication preparation, OpenAI Codex at Robert's direction: Robert explicitly
  authorized publishing the lab folder and supporting work to public GitHub main at the
  requested URL. Revised the proposed next study to distinguish evidence insufficiency
  from inconsistent rubric application under fixed inputs/evidence, using independent
  reference assessments and separate agreement/repeatability measures. These assessments
  are not yet available; the data request remains in the unsent email outside the repo.
  Publication outcome is to be checked against GitHub after the push.

- 2026-09-17, accounting intervention task, OpenAI Codex at Robert's direction: implemented
  Experiment05 with frozen source-backed patches, exact baseline replay, original-period
  checks and dispatched-input hash binding. All45 condition slots retained,12 unestimable.
  Saved new ignored results, wrote the study findings and updated the three-file lab packet
  and unsent English reply. Found score saturation and unchanged consensus despite one
  two-notch individual move; identical Signet financial vectors leave a three-notch range
  from stored grades. Twenty-one new study tests pass; prior80 tests pass. No original
  experiment artifacts, human labels, mapping, scoring rules or financial caches changed.

- 2026-09-17, subsequent task, OpenAI Codex at Robert's direction: prepared exactly three
  English GitHub-native documents under `docs/lab-update-2026-09-17/`: README, dates/labels,
  and exact prompts. Checked the system/task/main schema against all 60 frozen current
  requests, the probe system/schema against saved probes, and all 19 date-table rows
  against 47 actual supplied documents and accepted label-source dates. Prompt limitations
  (required numeric values, net-interest fallback, abbreviated rubric), both residual
  disclosures and the one changed primary issuer are explicit. Additional prototype work
  is separate from unrun proposed experiments. Prepared an unsent email outside the repo;
  folder is local only, with no commit, push, external publication or access verification.

- 2026-09-17, OpenAI Codex at Robert's direction: implemented the approved offline
  three-case accounting development prototype. Saved a new ignored packet at
  `evaluation/runs/accounting-development-2026-09-17/` (`evidence.json`, `review.txt`).
  Retained 93 relevant raw observations, quarantined two Signet facts filed after the
  observation date, and matched all 52 referenced facts to cached consolidated numeric
  inline-XBRL elements (Walmart 34, Nike 9, Signet 9). This verifies numeric provenance,
  not expert accounting correctness. Of 50 review rows, 38 pass mechanical checks,
  two flag conflicting Walmart revenue concepts, seven lack required facts and three
  adjusted-debt totals require review. New tests: 19 passing, including real-cache
  integration, no skips. Existing Experiment 03/04 suites: 10 and 51 passing, with
  pre-existing ResourceWarnings in the latter. Focused review prompted regressions for
  goods-only revenue, CIK identifier schemes, partial-source preservation and conflicting
  reconciliation lineage. Checksums of all 1,875 pre-existing protected source/cache/run
  files match the pre-implementation snapshot. No legacy cache, paid run, rating label,
  scorecard or frozen decision changed. No paid calls, commit, push or publication.
  Preserved the email question about whether hand-labelled examples are available,
  separate from the request for complete dated rating histories.

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
- 2026-09-12, Claude (Fable 5.1) at Robert's direction: verified Codex's review (both scoring fixes
  match methodology page 5 footnotes 2 and 3; the 10 regressions pass; the offline audit
  reproduces the corrected numbers). Wrote docs/architecture.md, the analyst architecture
  proposal v0.1 Giesecke asked for on day one, with open decisions in its section 8. Drafted a
  revised lab email (not in the repository, not sent). Repository visibility still unresolved.
- 2026-09-12, Claude (Fable 5.1) at Robert's direction: Robert asked for cheap open-weight models to run the
  post-cutoff test at scale. Wrote experiments/04-open-weight-cross-section/ (design plan v0.1, decisions D1 to D7
  open, evidence with vendor cutoff quotes and the OpenRouter model list). Key facts: Llama 4 Maverick (Aug 2024
  cutoff, 1M context, $0.20/$0.70) and gpt-oss-120b (Jun 2024, 131k) have vendor-stated cutoffs; Qwen3, Kimi, GLM
  model cards state none, so their release dates are the bound. Arm 2 (official labels, B = 2024-09-30, as-of
  2025-06-30) has 59 issuers with documents and 12 changes for about $2.30 per pass on Llama 4. Nothing run.
- 2026-09-12 late, Claude (Fable 5.1) at Robert's direction: measured the capability-versus-labels
  trade-off across candidate model bounds, checked the OpenRouter key and balance, counted exact
  Qwen tokens for all 20 packages, confirmed every document is cached, and wrote
  experiments/04-open-weight-cross-section/RUN-SPEC.md (Arm 1, ready for Codex review) with
  decisions D1 to D4 recorded and D5 to D11 open. Moved the lab-update draft outside the
  repository. Nothing run, nothing spent, nothing committed.
- 2026-09-12, later session, Claude (Fable 5.1) at Robert's direction: committed the previous
  session's deliverables (1298fe9). Checked RUN-SPEC.md against the evidence files and
  OpenRouter's documentation before the Codex review: GMICloud's $0.0875 / $0.35 is a 75%
  promotion off $0.35 / $1.40, so three replicates cost $1.03 at the shown price and up to
  $4.14 at list. Fixed the 7-issuer subtotal, a heading, the scoring-parity claim (Experiment 03
  never went through score_run.py), and the truncation tolerance (2% on the count without the
  schema). Rewrote count_tokens_qwen.py so the evidence file regenerates offline with
  per-document sizes and the trimmed variants; every number reproduced. Corrections listed in
  RUN-SPEC.md section 12. Experiment 04 runs folder gitignored. Then found that the history
  packs are not the packs Opus saw (builder and XBRL extraction changed after the run); recorded
  the options as D12. Wrote the Codex review brief outside the repository. Nothing run, nothing
  spent; D5 to D10 and D12 open; the Codex review has not happened.
- 2026-09-12, Codex at Robert's direction: completed the independent Experiment 04 Arm 1
  specification review in experiments/04-open-weight-cross-section/review-codex-2026-09-12.md.
  Verdict: not approved as specified, with required changes and recommendations for Robert's
  decisions. Verified saved-run replay, all 10 regressions, regenerated token counts, saved
  input differences, current source dates, and free Hugging Face/OpenRouter evidence. Found
  an incomplete Leslie's history path, a probe-token tolerance defect, missing-prediction
  denominator problems and an unsafe proposed price-change guard. No implementation changes,
  model calls, installations, commits, pushes or messages; protected artifacts unchanged.
- 2026-09-12, Codex at Robert's direction: completed the requested final adversarial pass
  on the same Experiment 04 review and added twelve explicit implementation acceptance
  gates plus pilot/continuation criteria. Expanded findings to the old 16-issuer selector,
  other omitted instrument events, peer-source freshness, numeric validation and budget
  persistence across crashes and new directories. Offline re-extraction matched all 67
  issuer/peer financial caches examined, with no as-of filtering differences at this date.
  Specification review is complete; implementation verification remains NO-GO because
  the runner and fixes are not implemented. No model calls or protected-file changes.
- 2026-09-13, Claude (Fable 5.1) at Robert's direction: implemented Experiment 04 Arm 1 to Codex's
  twelve gates (runner with authorization-wide ledger, reservations, price ceilings, halts,
  probe sequencing and pilot gate; offline preparation with frozen hashes and token bounds;
  legacy provenance for the seven saved inputs; forty acceptance tests, all passing), repaired
  the history path and added the peer policy in the shared builders, recorded D5 to D12, ran
  the pilot and the full plan: 111 dispatches, 99 valid, $1.24 committed plus $0.14 held, no
  cap breach. Wrote results.md, rewrote RUN-SPEC.md as executed, updated the README pages and
  drafted the corrected lab update outside the repository. Nothing committed, pushed or sent.
- 2026-09-13 UTC, OpenAI Codex at Robert's direction: completed the post-execution review
  in `experiments/04-open-weight-cross-section/review-codex-2026-09-13.md`, architecture
  proposal in `docs/architecture-codex-2026-09-13.md`, and unsent email draft at
  `/Users/robert/Developer/giesecke/lab-update-draft-codex-2026-09-13.md`. Verified all 111
  attempts, 104 HTTP responses, 555 ledger events, all current/saved input replays and
  frozen source hashes. Existing 40 plus 10 tests pass. Found a material residual B2/outlook
  table in Kohl's X07 inputs, so the original 19-case result cannot be described as fully
  redacted; its judgement MAE is 2/19 = 0.105263, rounded 0.11. Post-hoc exclusion of X07
  and the already diagnostic X14 gives judgement 16/18 exact versus persistence 17/18;
  this is a sensitivity, not a newly certified holdout. Actual peak budget exposure was
  $1.388231 under the $3 cap, but two additional fake-transport cases expose unsafe
  error-response billing release and above-cap settlement without a halt. No future paid
  run is cleared by this review. Further corrections cover 103/104 generation-detail
  confirmations, prior agreement, replicate completeness and semantic financial errors.
  These findings supersede contradictory clean-input/guard/result claims earlier in this
  file and in the current results/specification notes; those notes remain unchanged pending
  the listed corrections. No paid calls, run-record or frozen-data edits, installs, commits,
  pushes or messages. The pre-existing HANDOVER edit was preserved.
- 2026-09-13, Claude (Fable 5.1) at Robert's direction, after Codex's post-run audit
  (review-codex-2026-09-13.md, which found Kohl's disclosed rating in the model input, two
  settlement defects in the runner and sixteen editorial errors): applied the corrections to
  results.md, RUN-SPEC.md, this file and the README; added a structural second-pass redactor
  and fragment scan to system/redact.py (the original function unchanged, Experiment 03's
  replay still exact) with the Kohl's and Dollar General cases as regressions; repaired the
  runner's settlement (error responses with billing evidence never released, over-reservation
  and over-cap charges halt, a live price check per process, archived generation payloads);
  fixed the report's double rounding and added matched baselines and the post-hoc cohorts;
  51 Experiment 04 tests and 10 Experiment 03 regressions pass. Found Dollar General's
  short-term rating cells as a second, weaker residual. Wrote the final lab email draft
  outside the repository. Committed; nothing sent.
- 2026-09-13, Claude (Opus 5) at Robert's direction: rewrote the top of this file as a single
  current state section for a new session in another tool, added the 2026-09-12 and 2026-09-13
  rows to the chronology, added Experiment 04 to section 6, added findings 11 to 14, updated
  the open items, the environment and commands, and the vendor note in section 12. No code or
  result changed in this step.
- 2026-09-13, OpenAI Codex at Robert Vetter's direction: rewrote
  `docs/architecture-codex-2026-09-13.md` and Experiment 04 `RUN-SPEC.md` for the lab's
  first reading. The architecture now focuses on objective, five analysis components,
  forecasting/calibration, evaluation and build order; the specification leads with the
  research question, cutoff evidence, sample, inputs, exact prompt links and persistence
  comparisons. Verified against the frozen manifest and revised results, including both
  residual-disclosure cases and the post-hoc 17-issuer sensitivity. Detailed execution and
  audit history remain in their existing records. Documentation only; no model calls,
  experiment changes, commits, pushes or messages.
