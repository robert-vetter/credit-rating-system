# Experiment 02 — Relative rating determination with the issuer's own history

*Specification v0.1, 2026-08-30. Designed jointly by Robert Vetter and Claude; decisions in
decisions.md. Status: inputs built, scope under the budget cap pending (D5).*

## 1. What changes versus Experiment 01

Experiment 01 handed the model a single filing and nothing else, so every quantity and every
qualitative grade had to be produced from scratch. Robert's assessment: the best way to
determine a rating is *relative* to the issuer's own prior years — and both prompt variants
should receive all historical information that could help. Experiment 02 implements that
with a **history pack** (evaluation/pipeline/history_pack.py), identical for both variants:

| Component | Source | Point-in-time rule |
|---|---|---|
| Moody's rating path, deduplicated to actual rating states, plus the rating in effect at quarter start | 17g-7 file | events strictly before the observation quarter |
| Fundamentals of the three prior fiscal years and the current one: revenue, EBITDA, capex, interest, cash, CFO, dividends, debt (tagged debt + leases) and the four scorecard metrics | SEC XBRL, deterministic | only values filed before t |
| **Implied qualitative anchor** per prior year: the average qualitative grade the scorecard arithmetic requires given that year's actual rating and quantitative scores; plus the 3-year median | derived | — |
| Peer key-figure table (no ratings) | XBRL | filed before t |
| The current filing (document arm only) | EDGAR, redacted | filed before t |

Two honesty notes baked into the pack text: fiscal years before mid-2019 predate ASC 842 and
lack operating-lease tags (the debt jump at adoption is accounting), and single shock years
(2020) distort one-year anchors — Kohl's FY2020 arithmetic implies "Aa" qualitative because
Moody's looked through the collapse; the median anchor is the robust one. Moody's own
factor scores are not public; the anchor is a checkable proxy. (Robert is checking whether
his Moody's account opens Credit Opinions, which contain the real factor grids.)

## 2. Variants (paired, same observations, same pack)

- **A — grade-then-score:** quantitative inputs come from the pack (XBRL) or, in the
  document arm, from the model's reading; the model grades the four qualitative factors
  relative to the anchors and states whether each changed; scorecard.py computes the rating.
- **B — direct:** the model states the rating directly, with an explicit "changed vs.
  quarter-start rating: up / unchanged / down" field and drivers.

Both variants answer the same question Robert set: *given everything known about this
issuer up to the previous quarter, and what is new, is the rating still right?*

## 3. Two arms, one leakage discipline

- **Historical arm — the gold set** (50 hand-validated observations, 30 changed / 20
  unchanged, 2012–2025, 44 companies). Leakage control against training memory: (i)
  per-observation contamination probes before any documents, dated to the observation;
  (ii) redaction of rating disclosures; (iii) no tools array; (iv) history hard-cut at the
  previous quarter; (v) the **within-model contrast** for Opus 4.5 — its training cutoff
  (Aug 2025) lies inside the data, so accuracy on pre-cutoff vs post-cutoff observations
  can be compared: if memory drove results, the post-cutoff side should drop.
- **Fresh arm — the post-cutoff cross-section** from Experiment 01 (15 self-disclosed
  labels), rerun with the pack: the cutoff-free number.

Gold-set rule (D2): prompts fixed on a small non-gold dev slice first, then one run per
variant, no tuning against gold.

## 4. Budget

Robert's cap for the whole experiment: **$5**. What that buys is tabulated from free
`count_tokens` measurements on the real prompts (see decisions.md D5 for the choice):

Measured on the real prompts with Opus 4.5 (`count_tokens`, free): a history pack alone is
2,600–3,700 input tokens (median 3,297); pack plus the observation's filings is 54k–94k.

| Scope | Sync price | Batch API (50% off) |
|---|---|---|
| 50 contamination probes | $0.50 | $0.25 |
| Pack-only, both variants, all 50 gold observations | $5.40 | **$2.70** |
| Pack-only, both variants, 15 fresh-window companies | $1.60 | $0.80 |
| Document + pack, paired A/B, per observation | $0.65 | $0.32 |
| Document + pack, paired, all 50 gold | $33 | $16 |

Reading: under the $5 cap the **structured-data arm can cover the full gold set and the
fresh window with all probes (~$4.1 via Batch)**, while the **document-reading arm cannot
be run at gold-set scale** (7 observations synchronously, ~14 batched, without probes).
The choice is D5 in decisions.md.

## 5. Logging

As in Experiment 01: prompts verbatim in code, `candidates`/gold references, per-observation
transcripts (probe, pack, model output, scorecard arithmetic, label evidence) under
`runs/` (gitignored, regenerable), results and interpretation in results.md.
