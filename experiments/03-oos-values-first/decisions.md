# Decision log — Experiment 03

## OPEN (Robert)

**D1 — Boundary buffer.** Training cutoff "Aug 2025" is month-granular. Recommend B =
2025-09-30 (one-month buffer); alternative B = 2025-08-31 (no buffer, more observations,
slightly more risk that late-August data sits in training).

**D2 — Document set.** Recommend: latest post-B 10-K plus all subsequent 10-Qs up to as_of
(complete picture, 100–300k tokens). Alternative: 10-K + latest 10-Q only (cheaper).

**D3 — Quarterly XBRL in the pack.** Recommend yes: extend fetch_xbrl.py to quarterly facts so
the pack carries the last four quarters of the ten figures (Robert's "values from the last
quarters"). Cost: one script extension, no model cost.

**D4 — 8-Ks.** Recommend: label harvesting only, never model input (they announce downgrades).

**D5 — Effort level.** Recommend `high` (API default) with adaptive thinking; `medium` saves
~30% output cost.

**D6 — Method.** Recommend as specified: values-first primary; post-extraction judgement
recorded; pure direct variant retired with the documented evidence.

**D7 — Probe rule.** Recommend as before: clean subset = headline, rest reported alongside.

**D8 — Bedrock route (Sonnet 4 / Opus 4.1, Mar-2025 cutoffs, file-labeled window Apr–Aug
2025 with 11 actions at 8 companies).** Parked: requires an AWS account with existing Bedrock
usage (new customers cannot use Legacy models) and re-verification of those cutoffs from
system cards (their docs pages are gone). Robert to check HPI/lab access.

**D9 — Budget cap.** Estimate $10–20 for ~20 companies incl. probes. Robert to set the cap.

## DECIDED

**D0 — Option A chosen** (leakage-free post-cutoff window with disclosure labels, Opus 4.6),
Robert, 2026-08-31, after the review that found Experiment 02 not out of sample.
