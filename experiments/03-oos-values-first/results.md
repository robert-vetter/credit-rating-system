# Experiment 03 — Results: out-of-sample accuracy ratio, values-first

*Run 2026-09-10 by Robert Vetter and Claude. Model **claude-opus-4-6**, training data cutoff
**Aug 2025** (https://platform.claude.com/docs/en/models/opus-4-6/overview, Capabilities
table), adaptive thinking, effort `high`, structured output, **no tools array**. Every
observation is strictly after the boundary B = 2025-09-30. Design in README.md, decisions in
decisions.md, prompts verbatim in prompts/, per-observation date checks in
runs/&lt;batch&gt;/audit.json, raw model outputs in runs/&lt;batch&gt;/raw_outputs.json.*

## Headline: the accuracy ratio Xiaowei asked for

Seven out-of-sample observations (2 rating changes, 5 unchanged), each scored against the
company's own post-cutoff rating disclosure:

| Channel | Exact hit | Within 1 notch | MAE (notches) |
|---|---|---|---|
| **Values-first → deterministic scorecard** | **3/7 (43%)** | 5/7 (71%) | 1.57 |
| **Model's own judgement after extracting** | **4/7 (57%)** | 6/7 (86%) | 0.57 |
| Persistence baseline (carry last known rating) | 5/7 (71%) | 6/7 (86%) | 0.43 |

**The honest reading: on this cross-section no channel beats persistence on raw accuracy,**
because five of seven ratings did not move and persistence gets those for free. The accuracy
ratio in isolation is therefore not the interesting number — which is exactly why the design
reports it next to persistence and splits by changed/unchanged.

## Per observation

| ID | Company | Label (self-disclosed) | Persistence | Scorecard | Direct | Probe |
|---|---|---|---|---|---|---|
| X12 | Nike | **A2** (changed) | A1 | **A2 ✓** | A1 ✗ | no post-cutoff knowledge |
| X14 | Qurate/QVC | **Caa3** (changed) | Caa1 | B2 ✗ (4 notches, wrong direction) | Ca (1 notch, right direction) | no post-cutoff knowledge |
| X15 | Signet | Ba3 | Ba3 | Baa1 ✗ (5) | Ba1 ✗ (2, false alarm) | recalls prior Ba3 |
| X16 | Target | A2 | A2 | A2 ✓ | A2 ✓ | recalls prior |
| X17 | Tractor Supply | Baa1 | Baa1 | Baa2 ✗ (1) | Baa1 ✓ | recalls prior |
| X19 | Victoria's Secret | Ba3 | Ba3 | Ba3 ✓ | Ba3 ✓ | wrong/none |
| X20 | Walmart | Aa2 | Aa2 | Aa3 ✗ (1) | Aa2 ✓ | recalls prior |

**Changed subset (n = 2):** persistence is wrong by construction (MAE 1.5). Scorecard MAE 2.0,
direct MAE 1.0. Direction: **each channel caught exactly one of the two changes, and not the
same one.** The scorecard nailed Nike's downgrade to A2 exactly; the direct judgement caught
Qurate's collapse in direction (Ca, one notch past the actual Caa3) while the scorecard put it
four notches too high.

**Unchanged subset (n = 5):** false-alarm rate — scorecard 3/5, direct 1/5 (Signet).

## What the model actually did, in its own grades

Nike is the instructive case. Asked to grade relative to the implied anchor, the model marked
**Market Position "down" and Revenue and Earnings Stability "down"** ("revenue has
plateaued/declined"), which is precisely the deterioration behind Moody's November 2025
downgrade. The arithmetic converted that into A2 — the correct new rating. Its own free-form
judgement, however, said "unchanged A1": **it detected the deterioration but was not willing
to call the downgrade.** The decomposition captured what the holistic judgement suppressed.

Qurate is the mirror image. The model graded the business honestly ("TV home-shopping in
multi-year secular decline, revenue fell ~24% over 2022-2025") and its direct judgement said
Ca — a downgrade, essentially right. But the scorecard arithmetic returned B2, four notches
too generous, because the methodology's quantitative bands do not model a distressed issuer's
liquidity and exchange risk. This is the same systematic optimism measured in Experiments 01
and 02, now visible at its extreme.

## Leakage: controlled and measured, not assumed

- **Training memory.** Every observation lies after the model's Aug 2025 training cutoff.
  Per-observation memory probes (no documents, separate request) ran first: **no probe
  reproduced any post-cutoff specific.** For both changed cases the probe returned no usable
  rating knowledge — the model did not know Nike's or Qurate's new rating. Four probes
  recalled the *prior* rating, which the history pack supplies anyway.
- **Live access.** No `tools` array in any request; retrieval is structurally impossible.
- **Documents.** Every input filing has `filingDate > 2025-09-30`, asserted per observation
  and logged in audit.json. Rating self-disclosures stripped before input; removed lines
  stored. 8-K filings were used for label harvesting only, never as model input.
- **History pack.** Rating path ends at the 17g-7 file's true content end (2025-08-28,
  measured); all quantitative facts filed on or before the as-of date.
- **Labels.** Company self-disclosures in post-boundary filings, every one hand-read to
  separate a statement of the current rating from covenant thresholds and pricing grids.

## Extraction quality, verified for free

The ten scorecard figures were checked against SEC XBRL company facts: **46 of 47 comparable
figures within 2%, median deviation 0.0%.** The reading step is not the weak link — the
weighting and the qualitative judgement are.

## What went wrong, and what it cost

**11 of the original 16 observations were lost to a max_tokens ceiling I set too low.**
`max_tokens` caps thinking and answer together; at effort `high` the successful runs spent
6.6k–8.6k output tokens, so the 9,000 ceiling chosen as a cost control was borderline, and 11
requests exhausted it inside the thinking block and returned no answer — billed, worthless.
Both changed cases were among the losses. Fixed (ceiling raised to 24,000, with the reason in
the code) and the two changed cases were re-run within the remaining budget; nine unchanged
observations stayed unrun. A second defect surfaced with it: the collector crashed on a
text-free response instead of recording it; it now logs stop reason and block types.

Spend: first batch $7.49, re-run $1.21, pre-flight $0.04 — **$8.74 of the $10 balance**, about
$1.26 left. The n = 7 sample is a direct consequence of that mistake, and the confidence
intervals on every number above are correspondingly wide.

## Conclusions

1. **The accuracy ratio is 43% (scorecard) / 57% (direct) exact, 71% / 86% within one notch,
   on genuinely out-of-sample data with leakage controlled and measured.** Persistence scores
   71% / 86%. On an inert cross-section, accuracy alone cannot separate a working system from
   inertia.
2. **The signal is in the changed cases, and it is real but thin:** each channel caught one of
   two changes, and the model's relative grades pointed the right way on both. Two cases
   cannot support a stronger claim.
3. **Extraction is solved; aggregation is not.** Perfect figure reading, systematically
   optimistic arithmetic, and a holistic judgement that is well calibrated on stable issuers
   but reluctant to call a change.
4. **Next, cheaply:** re-run the nine unrun unchanged observations (~$3 at the corrected
   ceiling) to firm up the false-alarm rate, and calibrate the scorecard's optimism against
   the 218 changed quarters in the historical frame.
