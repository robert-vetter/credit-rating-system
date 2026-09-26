# Status

*Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. It replaces HANDOVER.md,
whose full history is in git at commit f4951ea. Checked against the reports, the experiment
results files and git history. Keep this file current: change the state tables when anything
changes and add a line to the log at the bottom.*

## The project

Robert Vetter runs this research project with Prof. Kay Giesecke and Xiaowei Ding, Chair of AI
and Quantitative Finance. Robert sets the questions, budgets and decisions. Claude and OpenAI
Codex write the code, analysis and notes, and audit each other's work. Related work by the
chair: Bettencourt, Ding and Giesecke, "The Stanford EDGAR Filings Dataset" (arXiv:2606.18192,
June 2026), a layout-faithful SEC filing parser with a post-cutoff forecasting benchmark.

Xiaowei reviews the updates. He wants tables, dates to the day, persistence next to every
number, class imbalance addressed, a commercial model as baseline, one deterministic
calculation and a specification agreed before deeper work. His main problem: (1) decipher
Moody's rating logic from real data with LLMs as a tool, (2) encode it into agents.

## Where things stand, 2026-09-26

| Item | State |
|---|---|
| Last email from the chair | Xiaowei's eight-point review (E07, 2026-09-17 or 18) |
| Reply | Robert writes it himself. Claude's earlier draft (E08) is not sent. Robert's reasoning is logged privately |
| Written answer to the review | [reports/2026-09-18-specification/](reports/2026-09-18-specification/), pushed |
| Work in flight | none |
| Rules for new experiments and reports | [EXPERIMENT-POLICY.md](EXPERIMENT-POLICY.md) and the templates in `experiments/_template/` and `reports/_template/`, from 2026-09-26 |
| Paid calls authorized | none |
| Repository | public on GitHub, holds the Moody's methodology PDF; visibility is Robert's open decision |

## Results so far

| Exp | Model, sample | Model judgement | Scorecard | Persistence |
|---|---|---|---|---|
| 01 | Opus 4.5 and Opus 5, 6 issuers, one filing each | 5/6, MAE 0.17 | 2/6, MAE 1.00 | 5/6, MAE 0.17 |
| 02 | Opus 4.5, 9 gold cases, rating history supplied; **in sample** | 6/9, MAE 0.44 | 2/9, MAE 1.89 | 3/9, MAE 0.89 |
| 03 | Opus 4.6, 7 post-cutoff issuers, $8.74 | 4/7, MAE 0.57 | 3/7, MAE 1.14 | 5/7, MAE 0.43 |
| 04 | Qwen3-235B, 19 post-cutoff issuers, 3 runs, $1.24 | 17/19, MAE 0.11 | 3/19, MAE 1.84 | 18/19, MAE 0.05 |
| 05 | no model; corrected inputs replayed through the scorecard, Walmart, Nike, Signet | | 0/3 | 2/3 |
| 06 | protocol for reviewing the evidence behind qualitative grades; must be brought to the experiment policy before it runs | not run | | |
| Calibration | no model; 1,665 historical observations | | MAE 1.92 raw, 1.49 calibrated | MAE 0.05 |

## Open decisions

| Decision | Owner | State |
|---|---|---|
| A sample with enough rating changes (balanced against unchanged controls) | Robert, then the chair | Robert wants it (2026-09-26). Sources: the chair's dated Moody's histories September 2025 to August 2026 (asked twice, no answer); Arm 2, an older window with official labels (59 issuers, 12 changes); more sectors |
| Is the task the outstanding rating or the change decision? | Robert, then Xiaowei | Robert asks whether, with 94% unchanged, the real difficulty is when a rating changes. In his first-step ask (E01), Xiaowei set the target as the outstanding rating. Not settled |
| A widely used commercial model | Robert | Robert agrees with Xiaowei (2026-09-26). GPT-5.2 fits the window (cutoff 2025-08-31); about $10 to $25 for 20 issuers × 3 runs; no cap approved |
| The nine consensus decisions | the chair | [specification, section 13](reports/2026-09-18-specification/SPECIFICATION.md#13-decisions-that-need-consensus-before-the-next-run) |
| Target rating type (corporate family versus senior unsecured) | the chair | asked 2026-09-13, no answer |
| Hand-checked reference data (inputs, adjustments, factor grades) | the chair | asked 2026-09-17; Xiaowei asked what it means; answered in the 2026-09-18 report |
| Access to Moody's Credit Opinions and rating-action releases | Robert | not settled |
| Qurate's October 2025 action day | Robert | needs the Moody's login |
| Snapshot of the Nike action and GPT cutoff pages under `evidence/` | any session | read 2026-09-18, not yet saved |

## Findings

| # | Finding | Where |
|---|---|---|
| 1 | Ratings are inert: 94% of quarters unchanged. Persistence is the baseline, never zero | [evaluation/observations-summary.md](evaluation/observations-summary.md) |
| 2 | Model memory beats naive document reading on famous issuers (MAE 0.40 against 1.40), so accuracy means nothing without contamination checks | early blind test, git history at f4951ea |
| 3 | Blinding fails: an issuer was identified from seven numbers | same |
| 4 | Filings disclose their own ratings; inputs must be redacted | [evaluation/leakage-audit.md](evaluation/leakage-audit.md) |
| 5 | Moody's public rating file is embargoed twelve months | [evaluation/rating-history-file.md](evaluation/rating-history-file.md) |
| 6 | Shown the prior rating, the model returns it: 56 of 60 answers in Experiment 04. A run with the prior withheld has not been done | [Exp 04 results](experiments/04-open-weight-cross-section/results.md) |
| 7 | Extracted inputs repeat across runs without being right: net interest income as interest expense, leases dropped from debt, pretax income as operating income | [Exp 04 audit](experiments/04-open-weight-cross-section/review-codex-2026-09-13.md) |
| 8 | Lexical redaction is not enough: a rating table rendered one cell per line leaked Kohl's B2. Repaired with a structural second pass | same; [system/redact.py](system/redact.py) |
| 9 | Fixing the numbers alone does not fix the scorecard: Signet's three runs with identical corrected inputs gave A3, Baa1 and A1 from their qualitative grades alone | [Exp 05 results](experiments/05-accounting-interventions/results.md) |
| 10 | Historical numbers-only scorecard: Moody's assigns on average 0.71 notches worse; no tested annual-number signal predicts a change | [evaluation/calibration-summary.md](evaluation/calibration-summary.md) |

## Money

| Account | Spent | Balance (last known) |
|---|---|---|
| Anthropic | Exp 01 under $4.78, Exp 02 $5.21, Exp 03 $8.74, smoke test about $1.60 | about $1.26 (2026-09-13) |
| OpenRouter | Exp 04 $1.24 plus $0.14 held, cap $3.00 | about $6.31 (2026-09-13) |

## Files outside the repository

In `/Users/robert/Developer/giesecke/correspondence/`, private because the repository is public:
`email-log.md` (every email, verbatim where available), `thinking-log.md` (Robert's reasoning
for the next reply), `xiaowei-expectations.md` (what Xiaowei asks for, with a checklist) and
`reply-draft-E08-2026-09-18.txt` (the unsent draft).

## Log

- 2026-09-26, Claude (Opus 5.5) at Robert's direction: wrote EXPERIMENT-POLICY.md (seven
  stages, design requirements from the chair's reviews, pre-checks P1 to P14, analysis and
  report structure) and the experiment and report templates. Robert confirmed the three
  standing rules the same day: chair agreement before every run, a commercial model in every
  baseline experiment, three runs per company by default. Pushed as ea6348c.
- 2026-09-26, Claude (Opus 5.5) at Robert's direction: restructured the repository. Reports
  moved to `reports/`, HANDOVER.md replaced by this file, early notes and superseded planning
  documents deleted (in git history at f4951ea), audits moved next to what they audit,
  "lab" renamed "chair" throughout. Robert's reasoning on E07 logged privately. No experiment,
  label, result or code behaviour changed.
- 2026-09-18, Claude (Fable 5.1): specification and answers to Xiaowei's eight points, pushed.
- 2026-09-17, OpenAI Codex: Experiment 05 and the evidence-ledger prototype; the 2026-09-17
  report, pushed and emailed.
- 2026-09-13: Experiment 04 run, audited by Codex, corrected; architecture proposal.
- 2026-09-12: Codex integrity review of Experiment 03 (a three-notch scoring bug fixed);
  Experiment 03 closed to paid calls; calibration study corrected.
- 2026-08-29 to 09-10: evaluation apparatus built; Experiments 01 to 03.
- 2026-08-07: project start.
