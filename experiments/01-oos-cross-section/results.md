# Experiment 01 — Results of the first pass (2026-08-30)

*Run under the decisions in decisions.md: Opus 5 + Opus 4.5, paired variants on the same
observations, clean-subset headline, hard $5 budget cap. Actual spend: ≤ $4.78 by our meter
(probes $0.26 + paired runs; prompt caching engaged — variant B paid only ~3k fresh tokens
per call; the Anthropic console is authoritative). One planned pair (Opus 5 / Floor & Decor)
was cut by the budget guard.*

## Contamination probes: everything clean — and memory is confidently wrong

24 probes (15 companies on Opus 4.5, 9 on Opus 5), each asked from memory for the current
rating, Moody's-adjusted metrics, and a post-cutoff fact, before any documents. **No probe
reproduced any post-cutoff specifics** — all observations count as clean under D4. Two
findings worth reporting upward:

- **Neither model knows the one genuine post-cutoff rating change.** Both claim Nike is A1
  (it is A2, disclosed in Nike's own filings since April 2026). For Opus 4.5 this certifies
  the Nike observation as truly out of sample; for Opus 5 it additionally shows the change
  was not memorized even though the action may predate its cutoff.
- **Recalled ratings are frequently wrong**: Macy's "Ba3" (actual Ba1), Signet "Ba2" (Ba3),
  Floor & Decor "Ba2" (Ba3), Dollar General "Baa2" (Baa3 since March 2025 — inside both
  models' training windows), Dick's "Baa3" on Opus 5 (Baa2). This replicates the project's
  earlier blind-test finding: model memory of ratings is confidently unreliable off the very
  famous names. Claimed revenues were consistently pre-cutoff fiscal years.

## Paired document runs (n = 6)

| Model | Company | Label (self-disclosed) | Persistence | A: extract→scorecard | B: direct + history + peers |
|---|---|---|---|---|---|
| Opus 4.5 | **Nike (the changed case)** | **A2** | A1 ✗ | A1 ✗ | A1 ✗ |
| Opus 4.5 | Walmart | Aa2 | Aa2 ✓ | A1 (−2) | Aa2 ✓ |
| Opus 4.5 | Gap | Ba2 | Ba2 ✓ | Baa3 (+2*) | Ba2 ✓ |
| Opus 4.5 | PVH | Baa3 | Baa3 ✓ | Baa3 ✓ | Baa3 ✓ |
| Opus 5 | Target | A2 | A2 ✓ | A2 ✓ | A2 ✓ |
| Opus 5 | Dollar General | Baa3 | Baa3 ✓ | Baa2 (−1) | Baa3 ✓ |

\* toward investment grade. Metrics: **variant B 5/6 exact (83%), MAE 0.17 — identical to
persistence.** Variant A (extract-then-score): 2/6 exact, MAE 1.00; its embedded direct
field 3/6. The famous compression of the scorecard channel shows again (Walmart pulled down
to A1, Gap pulled up to Baa3).

## What this first pass actually says

1. **The accuracy ratio Xiaowei asked for is ~83% exact / 100% within one notch (variant B)
   on truly out-of-sample companies — but that equals the persistence baseline exactly.**
   On a cross-section dominated by unchanged ratings, a high accuracy ratio is almost
   entirely inertia, which is why every number here is reported next to persistence.
2. **The single genuine rating change was missed by everything** — both variants and, by
   definition, persistence. The input was Nike's April 2026 10-Q (its July 10-K exceeds
   Opus 4.5's 200K context); whether a richer document set catches it is exactly the
   system-design question the main project is about. One case proves nothing either way;
   it is the whole reason larger changed samples (the gold set, the 218 changed quarters)
   exist.
3. **Leakage is controlled and measured, not assumed**: no tools, redacted inputs, training
   cutoffs from Anthropic's documentation, per-observation probes stored verbatim — and the
   probes show memory would have *hurt*, not helped (it holds stale, wrong ratings).
4. Operational learnings for the next pass, already fixed in code: budget projection must
   assume cache misses; usage fields read via model_dump (the cache-read counter hid behind
   a field-name mismatch and briefly looked like caching failed).

## Cost note

Probes $0.26; paired runs ~$3.5–4.5 depending on the authoritative console number; total
within the $5 cap. Scaling this design to all 15 labeled companies × both models × both
variants would be roughly $12–15; adding quarterly dates through the Opus 4.5 window
roughly triples that. Both are new budget decisions.
