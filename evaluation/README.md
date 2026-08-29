# evaluation/ — the evaluation system

*System built by Claude (Opus 5), directed by Robert Vetter, August 2026. The mapping decisions
were made by Robert (as recorded); everything else is generated, reproducible code output.*

The evaluation stands on one join: **which Moody's rating history belongs to which SEC filer.**
It is keyed by stable IDs, Moody's entity id (**OI**) to SEC **CIK**; names are display only.
From the confirmed join, one folder per company is compiled that holds everything the evaluation
needs about that company: identity, the full rating history (the answers), the SEC filing
inventory (the inputs), and the verification evidence.

## Layout

| Path | What it is | In git |
|---|---|---|
| `mapping.json` | current mapping state: one item per candidate pair with proposal, status, decision | yes |
| `decisions.jsonl` | append-only audit log: every decision with timestamp, actor, note. Never rewritten; re-deciding appends and the latest wins | yes |
| `lists.md` | the two alphabetical name lists (Moody's side, EDGAR side), generated | yes |
| `mapping-verification.md` | summary of the self-disclosure verification | yes |
| `observations-summary.md` | summary of the observation build (samples per company), generated | yes |
| `pipeline/` | all pipeline code, in run order below | yes |
| `companies/<slug>/` | one folder per actively rated company group, generated | no (generated/bulk) |

Per company folder:

    company.json        identity: OIs, LEIs, confirmed CIK, decision provenance, scope, group
    ratings.json        raw Moody's rating history, entity-level (ORD) and instrument-level
                        (IND/INRD), verbatim from the 17g-7 archives - the evaluation answers
    filings/manifest.json   complete SEC filing metadata (every 10-K/10-Q/8-K/20-F/40-F/6-K
                        with date, accession number, primary document), all submissions-API pages
    filings/*.htm       downloaded documents (latest annual report for current filers; older
                        ones are fetched on demand from the manifest URLs)
    verification.json   self-disclosure check result with evidence snippets
    observations.json   the evaluation samples for this company (see "Observations" below)

## Pipeline, in run order

| Step | Script | Does |
|---|---|---|
| 1 | `pipeline/build_frame.py` | parses the two 17g-7 zips, unions Corporate entities, matches names to EDGAR CIKs (three normalisation forms, strictly ordered), fetches SIC codes, filters to Retail and Apparel, writes `data/frame/retail_frame.json` |
| 2 | `pipeline/sic_sweep_listed.py` | fetches the SIC code of every listed SEC company (~8,000), enabling the reverse completeness check |
| 3 | `pipeline/build_queue.py` | turns the frame into mapping items (plus reverse items: listed retailers with no mapping); merges into `mapping.json` without touching decided items |
| 4 | `pipeline/bulk_accept.py` | records Robert's wholesale acceptance of the automatic proposals as bulk decisions in the log |
| 5 | `pipeline/compile_folders.py` | confirmed decisions → `companies/` folders (company.json + ratings.json); never deletes, only rewrites those two files |
| 6 | `pipeline/fetch_filings.py` | SEC filing manifest + latest annual report into each folder |
| 7 | `pipeline/verify_mapping.py` | the independent check: compares ratings the filer discloses in its own annual report against the mapped Moody's entity's ratings in effect at the filing date → `mapping-verification.md` |
| 8 | `pipeline/build_observations.py` | the observation builder ("Tripel-Builder"): per company a quarterly grid of observation dates, each with label-at-t, documents-before-t, rating-path-to-t, changed flag and persistence baseline → `observations.json` per folder + `observations-summary.md` |

Every step is re-runnable and deterministic given `data/` (see `data/README.md` for where each
input comes from). Decisions are the only human input and survive every re-run.

## Status of the decisions

All mappings are decided. On 2026-08-29 Robert accepted the automatic proposals wholesale
(recorded per item as a bulk decision, explicitly not an individual review); the substantively
non-trivial pairs, where a Moody's entity maps to a different filer than its own CIK
(bond-issuing subsidiaries, re-listed successors, dormant co-registrant CIKs), were surfaced
and checked in chat first. The 180 reverse items without any Moody's candidate (token Jaccard
>= 0.5 against all 13,025 Moody's corporate names) were bulk-marked not_rated. The interactive
review UI used to support per-item decisions was removed in the 2026-08-29 reorganisation once
the decisions were final; it lives in git history (`evaluation/review_server.py` before commit
"Reorganize repository") should per-item review ever be needed again.

## Verification

Beyond name matching, the join is verified through **self-disclosure**: companies print their
own ratings in filings, so a MATCH in `mapping-verification.md` means the mapped SEC filer
itself names the rating the mapped Moody's entity carries — immune to every name-matching
failure class. Result: 21 MATCH (including all seven original study companies), 1 DISAGREE that
turned out to be a discovery (Nike was downgraded inside Moody's 12-month publication embargo;
the mapping is confirmed by the same snippet), the rest neutral non-mentions.

## Completeness

Forward: every Retail/Apparel entity from the frame is an item, including inactive and
out-of-scope ones, so exclusions are visible decisions. Reverse: every listed SEC company with
a retail SIC and no mapping was raised as a question and answered. Stated residual: SEC filers
that are neither listed nor already matched (bond-only private filers) are not reverse-checked,
and a rated subsidiary with a name unlike its parent and no listed parent survives both
directions.

## Observations (the samples)

`observations.json` per company is what the evaluation actually consumes; the design and field
reference live in `pipeline/build_observations.py` and the aggregate numbers in
`observations-summary.md`. One observation = (company, date t, label at t, document references
filed before t, rating path up to t, changed flag, persistence baseline). The label horizon
ends 2025-06-30 because the public rating file is embargoed twelve months (dated 2026-08-11,
content through August 2025); observation dates beyond that need the lab's dataset.
