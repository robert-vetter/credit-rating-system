# evaluation/ — the hand-verified company mapping

*System built by Claude (Opus 5), directed by Robert Vetter, August 2026. The mapping decisions
themselves are made by Robert by hand; that is the point of this folder.*

## Why manual

The evaluation stands on one join: **which Moody's rating history belongs to which SEC filer.**
Everything downstream (labels, persistence baselines, document sets) inherits its correctness.
Automatic name matching built the candidate frame and is documented in
`notes/rating-history-file.md`, including two bugs it needed fixed; for the evaluation itself
every pair is confirmed by a person and recorded with provenance. The mapping is by stable IDs:
Moody's entity id (**OI**) to SEC **CIK**. Names are display only.

## The files

| File | Role | In git |
|---|---|---|
| `mapping.json` | current state: one item per candidate, with proposal, status, decision | yes |
| `decisions.jsonl` | append-only audit log: every decision with timestamp, actor, note; never rewritten, re-deciding appends | yes |
| `lists.md` | the two alphabetical name lists, generated | yes |
| `companies/<slug>/company.json` | per company group: identity, confirmed CIK, decision provenance | no (generated) |
| `companies/<slug>/ratings.json` | raw Moody's rating history of the group's entities (17g-7) | no (bulk Moody's data, ToU open) |

Item statuses: `pending`, `confirmed` (mapped to a CIK), `no_sec_filer` (Moody's-rated but no
SEC counterpart, e.g. private or foreign), `not_rated` (reverse items only). The latest decision
in the log wins; `mapping.json` always reflects it.

## Workflow

```
python3 evaluation/build_queue.py       # build/refresh the item list (server must not be running)
python3 evaluation/review_server.py     # review UI on http://localhost:8531
python3 evaluation/compile_folders.py   # confirmed decisions -> companies/ folders
```

The UI shows every item alphabetically with the automatic proposal prefilled: confirm it,
search the full EDGAR list (~900k names) for a different filer, or mark "no SEC filer". Each
click saves immediately to both files. Decisions survive everything; queue rebuilds and folder
compiles never touch them. The one rule: **do not run `build_queue.py` while the server is
running** — the server holds items in memory and writes them back on each decision.

Note that subsidiary bond issuers map to their **filing** parent (Sally Holdings LLC to Sally
Beauty Holdings' CIK): the confirmed CIK answers "whose SEC financial statements does this
rating belong to", which is the join the evaluation needs.

## Completeness, from both directions

Forward: every Retail/Apparel entity from the automatic frame (164) is an item, including
out-of-scope and inactive ones, so exclusions are decided visibly rather than by silence.
Reverse: `sic_sweep_listed.py` fetches the SIC code of **every** listed SEC company; re-running
`build_queue.py` afterwards adds each listed retailer that no confirmed mapping covers as a
reverse item ("does Moody's rate this, possibly under another name?"). Residual blind spot,
stated openly: SEC filers that are neither listed nor already matched (bond-only private
filers) are not yet swept from the reverse direction; and Moody's-rated retailers with no SEC
filings cannot enter the evaluation at all, whatever the mapping says.

## How the evaluation consumes this

One folder per company group. `ratings.json` holds the raw Moody's records (entity-level and
instrument-level); the label at an observation date is **derived** from them by the documented
label rule (senior unsecured for investment grade, CFR for speculative), so the derivation
stays checkable against the raw data. The evaluation runner walks `companies/*/`, builds
observation dates, fetches the filings for the confirmed CIK, runs the system, and scores
against the derived labels. The runner and the observation-date builder are the next step and
do not exist yet.
