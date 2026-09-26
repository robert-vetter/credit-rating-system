# AGENTS.md

Instructions for any AI coding agent or new session working in this repository.

## Read first

1. `STATUS.md`: where the project stands, open decisions, findings, money. Keep it current.
2. `README.md`: the overview the chair reads, and the map of the repository.
3. The latest report in `reports/`: what the chair has been told, and its specification.
4. The experiment folder you are touching: its `README.md` (specification), `decisions.md`
   (decisions with owner and date), `results.md`.

Private files outside the repository, in `/Users/robert/Developer/giesecke/correspondence/`:
the email log, Robert's thinking log and Xiaowei's expectations. Never copy their contents
into the repository; it is public.

## Who decides what

Robert Vetter directs the project and makes every decision that costs money, changes scope,
touches the gold set or the mapping, or goes to the chair (Prof. Giesecke, Xiaowei Ding). The
chair is the Chair of AI and Quantitative Finance; never call it "the lab". The agent proposes,
implements, measures and writes; it does not spend, commit, publish or send without being
asked. Decisions are recorded in the relevant `decisions.md` with owner and date.

## Rules that must not be relaxed

- No paid model call without a dollar cap Robert approved and a free pre-flight that prices
  the exact worst case; the runner refuses to submit above the cap.
- No `tools` in any model request. Inputs are redacted of rating self-disclosures. 8-Ks are
  never model input, exhibits never. Every input document and every fact carries a date and is
  asserted against the experiment's boundary; the checks are written to `runs/<batch>/audit.json`.
- A memory probe per observation runs before any documents. Model cutoffs are quoted from
  vendor documentation with a dated snapshot under `evidence/`.
- The gold set (`evaluation/goldset.json`) is frozen and never tuned on. `mapping.json`,
  `decisions.jsonl` and every `candidates.json` are human decisions: never regenerate them.
- Point in time everywhere: a value is usable at date t only if it was public on or before t.
- Every result is reported next to the persistence baseline, split into changed and unchanged
  observations. Every mistake is disclosed with the rule that now prevents it.

## Writing style

Plain English, short sentences, no em dashes, no emoji or badges, no marketing words, no
bullet list where two sentences of prose would do, no files nobody asked for. Facts, dates and
numbers go in tables. Write only what is true now and say when something is undecided. Every
note starts with an attribution header saying who wrote it, who directed it, the date, and what
was verified against which source. Commit messages: one line describing the deliverable, no
attribution trailers.

## Where things go

| Folder | Contents |
|---|---|
| `reports/YYYY-MM-DD-topic/` | anything written for the chair; never edited after it is sent |
| `system/` | the rating system under test |
| `experiments/NN-name/` | one folder per experiment: specification, decisions, prompts, code, results, its audits |
| `evaluation/` | the measuring apparatus; pipeline steps in run order in `evaluation/README.md` |
| `data/` | raw and derived data, gitignored except its README |

Generated artefacts (`evaluation/companies/`, `evaluation/runs/`, `experiments/*/runs/`) are
gitignored and on this machine only; do not commit them. The two Moody's 17g-7 zips under
`data/moodys/` cannot be downloaded again without Robert's account; never delete them.

## Environment

macOS, Python 3.13 with anthropic, httpx, jsonschema, transformers, tokenizers, numpy, scipy,
scikit-learn and pandas. Secrets in `.env` (gitignored): `ANTHROPIC_API_KEY` and
`OPEN_ROUTER_API_KEY`. Never print a key. Run scripts from the repository root.

| Command | What it does |
|---|---|
| `python3 system/scorecard.py` | the scorecard on two worked examples |
| `python3 -m unittest discover -s experiments/03-oos-values-first -p 'test_*.py'` | Experiment 03 regressions |
| `cd experiments/04-open-weight-cross-section && python3 -m unittest test_runner` | Experiment 04 acceptance tests |
| `python3 -m unittest discover -s experiments/05-accounting-interventions -p 'test_*.py'` | Experiment 05 tests |
| `python3 -m unittest discover -s evaluation/tests` | evidence-ledger prototype tests |
| `python3 evaluation/pipeline/calibrate_scorecard.py` | the historical calibration study, no cost |
| `python3 evaluation/pipeline/history_pack.py <slug> <date>` | prints a point-in-time history pack |
| `python3 experiments/04-open-weight-cross-section/prepare_inputs.py` | rebuilds every Experiment 04 input offline; refuses if a rating survives redaction |

`run_openrouter.py submit` is the only paid path in the repository. It refuses without an
authorization file bound to the manifest hash. Experiment 03's paid paths are closed.
