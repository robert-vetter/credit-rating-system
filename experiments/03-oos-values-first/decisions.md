# Decision log — Experiment 03

## OPEN (Robert)

**D8** remains open (AWS/Bedrock access for Sonnet 4 / Opus 4.1).

## DECIDED (Robert, 2026-08-31, via chat)

**D1 — Boundary B = 2025-09-30** (training cutoff Aug 2025 + one-month buffer). Alternative
considered: 2025-08-31 without buffer.

**D2 — Document set: latest post-B 10-K plus all subsequent 10-Qs up to as_of.** Alternative
considered: 10-K + latest 10-Q only.

**D3 — Quarterly XBRL in the pack: yes** (default accepted): extend fetch_xbrl.py to quarterly facts so
the pack carries the last four quarters of the ten figures (Robert's "values from the last
quarters"). Cost: one script extension, no model cost.

**D4 — 8-Ks: label harvesting only, never model input** (default accepted).

**D5 — Effort `high`** with adaptive thinking set explicitly. Alternative considered: medium.

**D6 — Method** (default accepted): values-first primary; post-extraction judgement
recorded; pure direct variant retired with the documented evidence.

**D7 — Probe rule** (default accepted): clean subset = headline, rest reported alongside.

**D8 — Bedrock route (Sonnet 4 / Opus 4.1, Mar-2025 cutoffs, file-labeled window Apr–Aug
2025 with 11 actions at 8 companies).** Parked: requires an AWS account with existing Bedrock
usage (new customers cannot use Legacy models) and re-verification of those cutoffs from
system cards (their docs pages are gone). Robert to check HPI/lab access.

**D9 — Budget cap: $10 total** (Robert). Consequence: if the full document package for all
labeled companies exceeds the cap at count_tokens time, the subset rule is: all changed cases
first, then unchanged cases by ascending token cost until the cap - documented per run.

## DECIDED

**D0 — Option A chosen** (leakage-free post-cutoff window with disclosure labels, Opus 4.6),
Robert, 2026-08-31, after the review that found Experiment 02 not out of sample.
