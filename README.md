# Credit rating system

*Updated by Codex, directed by Robert Vetter, 2026-09-12. Verified against the saved
Experiment 03 requests and outputs, offline integrity audit, and corrected calibration run.
Earlier experiments were implemented with Claude; attribution remains in their notes. The
Experiment 04 paragraph was added by Claude (Fable 5.1), directed by Robert Vetter, 2026-09-13.*

Research with Prof. Kay Giesecke and Xiaowei Ding: build a system that reads SEC filings,
applies Moody's published rating methodology and estimates an issuer's rating. The first
sector is Retail and Apparel, using the September 2025 methodology.

## Current result: a small post-cutoff pilot

The question is the **outstanding rating at a date after the model's training cutoff**.
Unchanged issuers remain in the sample. Persistence is the baseline; changed/unchanged
splits diagnose whether accuracy comes from carrying an earlier rating forward.

Experiment 03 used Claude Opus 4.6, with a documented August 2025 training-data cutoff,
to estimate ratings at August 29, 2026. It supplied post-September 2025 primary filings,
redacted for rating disclosures, plus historical ratings and financial context. Model
requests contained no tools, Internet grounding or RAG. Labels are the latest accepted
company disclosures, with outstanding-rating validity limitations described below.

| Channel, seven completed cases | Exact accuracy | Within one notch | MAE, notches |
|---|---|---|---|
| Scorecard, corrected arithmetic | 3/7 (43%) | 6/7 (86%) | 1.14 |
| Model judgement after extraction | 4/7 (57%) | 6/7 (86%) | 0.57 |
| Persistence | 5/7 (71%) | 6/7 (86%) | 0.43 |

This is pilot evidence, not demonstrated superiority to persistence. One case, Qurate, has
an old label that predates bankruptcy information in its inputs. Excluding it as a
sensitivity leaves six cases: scorecard 3/6 exact, MAE 1.17; judgement 4/6, MAE 0.50;
persistence 5/6, MAE 0.17. The other six are not thereby certified free of label problems.
Full splits, selection failures and uncertainty are in the results.

**Experiment 04, Arm 1 (2026-09-13)** repeats the test on Qwen3-235B-A22B-Instruct-2507
(open weights, public checkpoint of 2025-07-21, DeepInfra fp8 through OpenRouter) for all 20
disclosure labels, three replicates each, at $1.24. On the 19-issuer primary cohort the model's
judgement is 17/19 exact with MAE 0.11 against persistence's 18/19 and 0.05, with one false
alarm and both rating changes missed; the scorecard channel is 3/19 with MAE 1.84 and runs
1.2 notches favourable on average. An independent audit found that one issuer's disclosed
rating survived redaction; without it the sensitivity is 16/18 against persistence's 17/18.
On the seven issuers Opus scored, the same supplied information gave the same aggregate
judgement accuracy in two of three replicates. Tables, coverage, every failed request and the
audit: [Experiment 04 results](experiments/04-open-weight-cross-section/results.md) and
[the review](experiments/04-open-weight-cross-section/review-codex-2026-09-13.md).

Start with the [experiment specification](experiments/03-oos-values-first/README.md),
[results and limitations](experiments/03-oos-values-first/results.md), and
[integrity review](docs/oos-integrity-review.md). The specification distinguishes the
original run from safeguards added afterwards. Original prompts and human label decisions
are preserved. Paid completion is closed; the remaining 13 cases will not be run.

## The four experiments

| Experiment | Question | State |
|---|---|---|
| [01, out-of-sample cross-section](experiments/01-oos-cross-section/) | does a single filing without history place an issuer on the scale, after the cutoff | done 2026-08-30; the direct rating equalled persistence |
| [02, relative with history](experiments/02-relative-with-history/) | does the issuer's own rating history and a relative framing move the judgement off persistence | done 2026-09-04; it did, but all nine observations predate the model's cutoff, so the result is in sample |
| [03, post-cutoff values first](experiments/03-oos-values-first/) | the outstanding rating after a documented training cutoff, on a frontier model | run 2026-09-10 on Opus 4.6; seven usable issuers, closed to further paid calls |
| [04, post-release open weights](experiments/04-open-weight-cross-section/) | the same test at a price that covers the whole cross-section with replicates | run 2026-09-13 on Qwen3-235B-2507; 20 issuers, three replicates, audited afterwards |

Each folder holds the specification, the decision log with owners and dates, the verbatim
prompts and the results note. Experiment 04 additionally holds its two independent reviews,
the runner and its acceptance tests.

## What is built

The evaluation apparatus links 186 Moody's Retail/Apparel entities to SEC filers, grouped
into 86 company folders. The historical grid has 3,646 quarterly observations and 218
rating changes; 3,084 observations are in scope. A fixed set of 50 hand-validated
observations contains 30 changed and 20 unchanged cases. Its earlier exposure is disclosed;
it must not be described as a never-seen holdout.

The system has a structured analyst call, a deterministic scorecard engine, rating
redaction, history and peer inputs, persistence comparisons and saved request/output
records. The integrity review replayed all 18 document-request packages exactly and added
10 passing regression tests. Repairs cover methodology edge cases, per-field filing dates,
peer fiscal-period consistency and calibration training separation. These checks verify
specific properties, not the absence of all contamination.

A separate, free historical calibration study now excludes gold observations before
fitting and development analysis. On 1,665 observations, raw quantitative-scorecard MAE is
1.919 and calibrated MAE is 1.492; persistence MAE is 0.053. All four tested change
signals select persistence. This is retrospective validation with companies held out,
not a rolling forecast experiment. See the [current tables](evaluation/calibration-summary.md)
and [study history](notes/scorecard-calibration.md).

XBRL agreement in Experiment 03 is a consistency check: some reference figures were already
in the input. It does not establish independent extraction accuracy. The prompt supplied
short factor descriptions, not the full methodology rubric. Both limitations inform the
next design.

## Repository map

| Location | Contents |
|---|---|
| [HANDOVER.md](HANDOVER.md) | Current state, correspondence requirements, open work and commands |
| [AGENTS.md](AGENTS.md) | Budget, frozen-data and working rules |
| [system/](system/) | Scorecard, analyst call and redactor |
| [evaluation/](evaluation/) | Mapping, fixed evaluation set and pipeline |
| [experiments/](experiments/) | Specifications, prompts, decisions and results for each experiment |
| [docs/oos-integrity-review.md](docs/oos-integrity-review.md) | Audit findings, repairs and proposed analyst architecture |
| [docs/architecture-codex-2026-09-13.md](docs/architecture-codex-2026-09-13.md) | Analyst architecture, first draft from the evidence of all four experiments (Codex, 2026-09-13); supersedes [docs/architecture.md](docs/architecture.md) |
| [experiments/04-open-weight-cross-section/](experiments/04-open-weight-cross-section/README.md) | The post-release test on an open-weight model: design plan, Codex's review, [RUN-SPEC.md](experiments/04-open-weight-cross-section/RUN-SPEC.md) as executed, and [results.md](experiments/04-open-weight-cross-section/results.md) (Arm 1, 2026-09-13) |
| [notes/](notes/) | Historical experiment logs and their corrections |
| [data/README.md](data/README.md) | Data sources and local cache inventory |
| [methodologies/](methodologies/) | Methodology reference |

Raw company folders and run artifacts are gitignored. The repository contains code,
protocols, human decisions and result summaries, not all data required to replay a run
from a fresh clone. Local replay requires the original saved requests and filing cache.

## Next work

The [architecture draft of 2026-09-13](docs/architecture-codex-2026-09-13.md) is written from
what the four experiments showed, and it is a proposal, not an implementation. It builds the
analyst around verified source evidence, explicit accounting definitions with the methodology's
own adjustments, factor grades tied to the rubric with quotes, and a rating-change decision
evaluated separately from the rating level. Its first steps cost nothing: close the redaction
and billing controls, then build the evidence ledger and a trailing-twelve-month accounting
baseline on non-gold data, then version the rubric and the event specification. Nothing beyond
that is authorized, and no paid run is planned.

Open and not settled by any of this: which entity and rating type the target should be,
independently verified labels for the recent window, sector expansion, whether peer ratings
are admissible input, five scope calls in the frame, and the terms of use of the methodology
documents. They are tracked in [HANDOVER.md](HANDOVER.md) section 10 with an owner each.
