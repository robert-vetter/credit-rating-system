# Decision log — Experiment 01

Format: decision, options considered, what was decided, by whom, when. Open items first.

## OPEN

*(none - all initial decisions taken)*

## DECIDED (2026-08-30, Robert via chat)

**D1 — Model set: (b) Opus 5 + Opus 4.5.** Options were: (a) Opus 5 only (Xiaowei's literal ask, minimal cost);
(b) Opus 5 + Opus 4.5 (recommended: adds the 12-month window with real rating changes at the
same price, giving a strong-model-short-window vs older-model-long-window contrast);
(c) additionally Sonnet 5. Robert chose (b).

**D2 — As-of dates:** as recommended — single cross-section at 2026-08-29 for Opus 5 (and Sonnet 5
if included); for Opus 4.5 additionally quarter-end dates Sep 2025 – Jun 2026 within its
window (subject to the D5 budget cap).

**D3 — Paired: both variants on the same observations.** Rationale: doubles per-observation cost but makes A-vs-B a within-subject comparison;
with prompt caching the second call's documents cost ~10% via prompt caching.

**D4 — Contamination handling: clean subset is the headline,** 
contaminated observations reported alongside, never silently dropped.

**D5 — Budget: hard cap $5 total for the first pass** (Robert). Consequence: probes run on
all candidates (cheap), but paired A/B document runs on a hand-picked subset of ~6
observations sized to fit the cap, exact cost computed with the free count_tokens endpoint
before any paid call. Scaling beyond that is a new decision with these results on the table.

## DECIDED

**D0 — Leakage boundary = training data cutoff** (broader than "reliable knowledge" cutoff),
per-observation contamination probes on top; probe design per Robert's proposal (rating +
specific adjusted metrics + post-cutoff fact). Proposed by Robert, refined together,
2026-08-30.
