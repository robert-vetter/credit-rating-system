# Decision log — Experiment 01

Format: decision, options considered, what was decided, by whom, when. Open items first.

## OPEN

**D1 — Model set.** Options: (a) Opus 5 only (Xiaowei's literal ask, minimal cost);
(b) Opus 5 + Opus 4.5 (recommended: adds the 12-month window with real rating changes at the
same price, giving a strong-model-short-window vs older-model-long-window contrast);
(c) additionally Sonnet 5 (middle cutoff, cheap). — Robert to decide.

**D2 — As-of date(s).** Recommend: single cross-section at 2026-08-29 for Opus 5 (and Sonnet 5
if included); for Opus 4.5 additionally quarter-end dates Sep 2025 – Jun 2026 within its
window. — Robert to decide.

**D3 — Variant A and B on the same observations (paired) or split across different ones?**
Recommend paired: doubles per-observation cost but makes A-vs-B a within-subject comparison;
with prompt caching the second call's documents cost ~10%. — Robert to decide.

**D4 — Contaminated observations: exclude from headline or report side by side?** Recommend:
headline = clean subset, contaminated reported alongside (never silently dropped). — Robert
to decide.

**D5 — Budget.** With the harvest numbers: a full first pass (Opus 4.5 window cross-section,
~15 observations x 2 variants + probes, plus the same on Opus 5's ~10) is roughly $30-50
total including probes, halved if run through the Batch API. — Robert to decide.

## DECIDED

**D0 — Leakage boundary = training data cutoff** (broader than "reliable knowledge" cutoff),
per-observation contamination probes on top; probe design per Robert's proposal (rating +
specific adjusted metrics + post-cutoff fact). Proposed by Robert, refined together,
2026-08-30.
