# Credit rating system

*Robert Vetter, with Prof. Kay Giesecke and Xiaowei Ding, Chair of AI and Quantitative Finance.
This page updated 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Every number is
taken from the report or results file it links to.*

The goal is a system that does what a Moody's credit rating analyst does. The main problem, as
Xiaowei put it, has two parts. First, use LLMs as a tool to decipher Moody's rating logic from
real data. Second, encode that logic into agents that can rate. The first sector is Retail and
Apparel, under Moody's methodology of 12 September 2025.

## Where it stands

| Part of the problem | State on 2026-09-26 |
|---|---|
| Published scorecard arithmetic (weights, bands, mapping, footnote rules) | encoded and tested in [system/scorecard.py](system/scorecard.py) |
| Input definitions and Moody's adjustments | written down ([specification, section 8](reports/2026-09-18-specification/SPECIFICATION.md#8-the-deterministic-calculation)); an evidence ledger for them exists as an offline prototype |
| Assigned rating versus numbers-only scorecard, from historical data | one study: Moody's rates on average 0.71 notches worse than the numbers imply ([calibration summary](evaluation/calibration-summary.md)) |
| Qualitative factor grades | not deciphered; model grades are unstable (Signet: Aa to Ba on identical inputs) |
| Agent | not built; the model side is one structured call without tools |

## Current result

The test is the outstanding Moody's rating on 2026-08-29, after the model's training cutoff,
with no tools and no retrieval. Persistence means carrying the last known rating forward.

| Model, issuers | Changed / unchanged | Model judgement, exact | Scorecard, exact | Persistence, exact |
|---|---|---|---|---|
| Qwen3-235B, 19 issuers, 3 runs each | 1 / 18 | 17/19, MAE 0.11 | 3/19, MAE 1.84 | 18/19, MAE 0.05 |
| Claude Opus 4.6, 7 issuers | 2 / 5 | 4/7, MAE 0.57 | 3/7, MAE 1.14 | 5/7, MAE 0.43 |

Neither channel beats persistence. The sample is highly imbalanced: one change in nineteen,
against a historical rate of 6.0% per quarter. A sample with enough rating changes and a run
on a widely used commercial model (GPT-5.2) are proposed and not yet run.

## Reports to the chair

| Date | Report |
|---|---|
| 2026-09-13 | [Analyst architecture proposal](reports/2026-09-13-architecture-proposal/README.md) |
| 2026-09-17 | [Results, dates and labels, prompts](reports/2026-09-17-results-dates-prompts/README.md) |
| 2026-09-18 | [Specification](reports/2026-09-18-specification/SPECIFICATION.md) and [answers to the eight review points](reports/2026-09-18-specification/README.md) |

## Experiments

| # | Question | State |
|---|---|---|
| [01](experiments/01-oos-cross-section/) | Does one filing without history place an issuer on the scale? | done 2026-08-30; the direct rating equalled persistence |
| [02](experiments/02-relative-with-history/) | Does the issuer's rating history move the judgement off persistence? | done 2026-09-04; it did, but all cases predate the model's cutoff |
| [03](experiments/03-oos-values-first/) | Outstanding rating after the cutoff, frontier model | done 2026-09-10 on Opus 4.6; 7 usable issuers, $8.74 |
| [04](experiments/04-open-weight-cross-section/) | Same test on the whole cross-section with replicates | done 2026-09-13 on Qwen3-235B; 20 issuers, 3 runs, $1.24 |
| [05](experiments/05-accounting-interventions/) | Do corrected financial inputs fix the scorecard? | done 2026-09-17, no model calls; they do not fix it alone |
| [06](experiments/06-qualitative-evidence/) | What does the evidence support for each qualitative grade? | protocol drafted, not run |

Each folder holds the specification, the decisions with owner and date, the prompts, the code
and the results.

## Repository

| Folder | Contents |
|---|---|
| [reports/](reports/) | everything written for the chair, one dated folder per report |
| [system/](system/) | the rating system: scorecard, analyst call, redaction, evidence ledger |
| [experiments/](experiments/) | one folder per experiment |
| [evaluation/](evaluation/) | the measuring apparatus: company mapping, observations, gold set, pipeline, audits |
| [methodologies/](methodologies/) | the Moody's methodology |
| [STATUS.md](STATUS.md) | current state, open decisions, findings |

Raw filings, rating files and run records are not in the repository. They are listed in
[data/README.md](data/README.md).
