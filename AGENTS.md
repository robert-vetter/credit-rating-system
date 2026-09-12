# AGENTS.md

Instructions for any AI coding agent or new session working in this repository.

## Read first

1. `HANDOVER.md` : where the project stands, what was done, the correspondence with the lab,
   open items, and how to run things. Keep its change log (section 13) current.
2. `README.md` : the map of the repository and the headline findings.
3. The experiment folder you are touching: its `README.md` (specification), `decisions.md`
   (decisions with owner and date), `results.md`.

## Who decides what

Robert Vetter directs the project and makes every decision that costs money, changes scope,
touches the gold set or the mapping, or goes to the lab (Prof. Giesecke, Xiaowei Ding). The
agent proposes, implements, measures and writes; it does not spend, commit, publish or send
without being asked. Decisions are recorded in the relevant `decisions.md` with owner and date.

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
bullet list where two sentences of prose would do, no files nobody asked for. Write only what
is true now and say when something is undecided. Every note starts with an attribution header
saying who wrote it, who directed it, the date, and what was verified against which source.
Commit messages: one line describing the deliverable, no attribution trailers.

## Where things go

- `system/` the rating system under test; `evaluation/` the measuring apparatus (pipeline
  steps listed in run order in `evaluation/README.md`); `experiments/NN-name/` one folder per
  experiment; `notes/` chronological experiment logs indexed in `notes/README.md`; `docs/`
  plan, audits, reviews; `data/` raw and derived data, gitignored except its README.
- Generated artefacts (`evaluation/companies/`, `evaluation/runs/`, `experiments/*/runs/`)
  are gitignored and regenerable; do not commit them.

## Environment

Python 3.13, packages in `HANDOVER.md` section 11, secrets in `.env` (gitignored). Run scripts
from the repository root with `python3 path/to/script.py`.
