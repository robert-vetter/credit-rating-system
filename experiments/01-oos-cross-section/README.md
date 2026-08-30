# Experiment 01 — Out-of-sample cross-section: what does a current LLM's rating accuracy look like on data it cannot have seen?

*Specification v1.0, 2026-08-30. Designed jointly by Robert Vetter and Claude (Opus 5);
decisions and their owners are logged in decisions.md. Status: first pass EXECUTED under the
$5 cap — see results.md. Files: candidates.json (hand-validated labels with evidence),
probe.py, run_pairs.py, runs/ (full transcripts, gitignored contents regenerable).*

## 1. Objective (Xiaowei's ask, made precise)

> "Take an LLM or agent, note down its training data cutoff date, and run a relatively good
> prompt on truly out of sample cross sectional data — what's the accuracy ratio?"

We measure: for a fixed model with a documented training cutoff, on companies whose relevant
filings and possible rating actions lie strictly AFTER that cutoff, how accurately does the
model determine the current Moody's rating from documents alone — with every channel through
which the answer could reach it other than the documents closed or measured.

## 2. Why "truly out of sample" is the hard part, and how we get labels

Three leakage channels have to be handled, not assumed away:

1. **Training memory.** Solved by the cutoff boundary: only observations whose determining
   documents and rating state postdate the model's training data cutoff. We use the
   *training data* cutoff (the broader bound), not the "reliable knowledge" cutoff.
2. **Live access.** Solved structurally: raw Messages API calls with NO tools array — the
   model has no retrieval, no web access, nothing to call (verified earlier in this project:
   without a tools array there is no mechanism to fetch anything).
3. **The documents themselves.** Filings disclose their own ratings (see
   docs/leakage-audit.md in the main repo); the redaction module strips these before input,
   and every removed line is stored with the run.

**Labels.** Moody's public 17g-7 rating history is embargoed 12 months (file in hand ends
August 2025), so for a post-cutoff window the labels cannot come from it. They come from the
same disclosure channel we redact on the input side: companies print their current Moody's
rating in subsequent filings. A label is accepted only as the company's own disclosure in a
filing AFTER the observation date, cross-checked for consistency with the last embargoed
file rating (a difference means a rating change inside the window — exactly the interesting
cases). Coverage caveat, stated openly: only ~40-60% of issuers print their ratings, so the
cross-section is the disclosing subset; this biases toward larger issuers and is documented
per run. Feasibility numbers from the harvest: see §6.

## 3. Models under test

Cutoffs from Anthropic's model documentation (platform.claude.com/docs/en/models/overview
and per-model pages, retrieved 2026-08-30):

| Model | API ID | Training data cutoff | Reliable cutoff | Context | Price in/out per MTok | OOS window (documents after training cutoff) |
|---|---|---|---|---|---|---|
| Claude Opus 5 | `claude-opus-5` | **May 2026** | May 2026 | 1M | $5 / $25 | Jun–Aug 2026 (~3 months) |
| Claude Sonnet 5 | `claude-sonnet-5` | **Jan 2026** | Jan 2026 | 1M | $2 / $10 | Feb–Aug 2026 (~7 months) |
| Claude Opus 4.5 | `claude-opus-4-5-20251101` | **Aug 2025** | May 2025 | 200K | $5 / $25 | Sep 2025–Aug 2026 (~12 months) |

The tradeoff the model set has to span: newer model = stronger but shorter OOS window with
fewer rating changes; older model = weaker but a 12-month window with many more changes.
(Opus 4.5's 200K context constrains the document set for large filers.)

## 4. Design

**Unit.** One observation = (company, as-of date). Cross-sectional: all eligible companies
at the same as-of date; for the long-window model additionally quarterly dates through its
window. Eligible = in-scope retail/apparel current filer with (a) at least one input filing
inside the OOS window, (b) a harvested post-observation label.

**Two prompt variants, run on the SAME observations (paired):**

- **Variant A — extract-then-score.** The model reads the (redacted) filings and outputs the
  ten quantitative inputs plus four qualitative grades; our deterministic scorecard
  implementation computes the rating. Tests: can it do the analyst's decomposed job?
- **Variant B — direct rating.** The model receives the redacted filings, the issuer's
  rating path up to the model's cutoff (public information the model may know anyway), and
  an XBRL-generated peer key-figure table, and outputs a rating directly. Tests: the
  end-to-end judgement, real-world configuration.

**Contamination probe, per observation, BEFORE any documents (separate request, no shared
context):** the model is asked, from memory only, for (1) the company's current Moody's
rating as of the as-of date, (2) the specific Moody's-adjusted metrics (debt/EBITDA etc.),
(3) a post-cutoff fact checkable in the filing (e.g. latest fiscal-year revenue). Scoring:
an observation is flagged CONTAMINATED if the probe reproduces post-cutoff specifics
correctly; correct *rating* alone with wrong/absent specifics counts as "prior, not
knowledge" (ratings are inert - a stale memory often guesses right; the specifics separate
memory of the answer from a lucky persistent prior). Headline metrics are reported on the
clean subset; the contaminated subset is reported alongside, never silently dropped.

**Baseline.** Persistence = the last rating verifiable before the model's cutoff (embargoed
file plus pre-cutoff disclosures). Any accuracy number is reported next to it; on a
cross-section dominated by unchanged ratings, beating persistence — not zero — is the bar.

## 5. Metrics

Per model × variant: exact-hit rate (Xiaowei's "accuracy ratio"), within-1-notch rate,
MAE in notches, all vs. the persistence baseline; separately on the changed-in-window
subset (the informative one) and the unchanged subset (false-alarm rate). Paired bootstrap
for uncertainty (small n — intervals will be honest and wide).

## 6. Feasibility (disclosure harvest, 2026-08-30)

All post-Sep-2025 filings (latest four per company) of the 63 in-scope current filers were
scanned for Moody's rating self-disclosures. Results:

| Window | Companies disclosing | Unambiguous (single symbol) | Genuine rating changes |
|---|---|---|---|
| Opus 4.5 (Sep 2025+) | 20 | 16 | 1 confirmed (Nike A1→A2) |
| Sonnet 5 (Feb 2026+) | 17 | 15 | 0 cleanly attributable |
| Opus 5 (Jun 2026+) | 12 | 10 | 0 cleanly attributable |

Hand-reading every candidate proved that mechanical harvesting alone cannot be trusted, in
both directions: Kohl's apparent "Baa3" is a coupon step-up *threshold clause* ("...if
downgraded below Baa3..."), not a rating statement — a false positive the single-symbol
heuristic cannot catch; and an apparent Macy's change was an artifact of a crude file-end
reference (the label rule says Ba1, unchanged). Nike's A1→A2 is genuine and twice-disclosed,
but its action date is only bounded to (Aug 2025, Apr 2026], so it is truly out of sample
only for Opus 4.5: **an observation counts as OOS for a model only if the action's entire
uncertainty window lies after that model's training cutoff.**

Consequences baked into the design: (1) every harvested label is hand-validated from its
snippet (current-rating statement vs. threshold/pricing-grid language) before use — same
discipline as the gold set; (2) four companies with multi-symbol disclosures (Bath & Body
Works, Leslie's, Qurate, Victoria's Secret) go to hand reading and may add labels; (3) the
usable first cross-section is roughly 15 companies (Opus 4.5 window) / 10 (Opus 5 window),
dominated by unchanged names — which is fine for Xiaowei's accuracy-ratio question, with the
persistence baseline reported alongside, and thin for change detection (about one genuine
changed case), which is honest and stated rather than papered over.

## 7. Anthropic API usage (the "use it properly" checklist)

- Raw `client.messages` calls, structured outputs via `output_config` JSON schema, streaming
  for large inputs, `count_tokens` preflight (free) before every paid run.
- **No tools array** — this is the leakage control, not an omission.
- **No Files API for these runs**: inputs are extracted text passed in messages, which
  enables prompt caching (the two variants and the probe share document prefixes; cache
  reads cost 10% of input). The Files API adds value for raw-PDF workflows, not here; it
  does not reduce token costs.
- Model IDs pinned exactly as in §3; per-run `run_meta.json` freezes model ID, prompts
  verbatim, document list, token usage, and the docs-page cutoff citation.
- Batch API (50% off) once runs exceed exploratory size.

## 8. Logging & reproducibility

Everything lives under `experiments/01-oos-cross-section/`: this spec, `decisions.md` (each
design decision with options considered, decision, owner, date), `runs/<tag>/` with the full
audit trail per observation (probe transcript, redacted lines, raw model output, extracted
values, scorecard arithmetic, label evidence with EDGAR links). Reused machinery is imported
from the main repo (`system/`, `evaluation/pipeline/`), not copied.
