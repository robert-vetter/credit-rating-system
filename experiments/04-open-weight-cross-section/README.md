# Experiment 04: the post-cutoff test on cheap models, design plan v0.2

> **Status: Arm 1 ran on 2026-09-13.** This page is the design plan that chose the model and
> the window, written before the run. The specification as executed is [RUN-SPEC.md](RUN-SPEC.md),
> the results are [results.md](results.md), the decisions are [decisions.md](decisions.md), and
> the two independent reviews are [review-codex-2026-09-12.md](review-codex-2026-09-12.md),
> before the run, and [review-codex-2026-09-13.md](review-codex-2026-09-13.md), after it.
> Section 5a records what changed between this plan and the run. Arm 2 is not authorized.

*Written 2026-09-12 by Claude (Fable 5.1), directed by Robert Vetter. Nothing had been run when
this plan was written.
Prices, context lengths, quantisation and parameter support per provider were read from
OpenRouter's public endpoints API on 2026-09-12 (evidence/); cutoff statements from the vendor
documents named in evidence/cutoffs-2026-09-12.md; label and document counts computed locally
from the rating histories and filing manifests. Decisions for Robert are in decisions.md.*

## 1. The trade-off, measured

A model can only be tested on ratings it cannot have seen, so the earlier its training data
ends, the more labelled rating changes lie after it. But earlier models are weaker. The
labels we hold end on two dates: Moody's official file runs to 2025-08-28, and company
disclosures give 20 hand-read labels for the window to 2026-08-29 with two changes (October
and November 2025). For each candidate boundary B (the model's data bound plus one month),
this is what the official file offers at its end date, counting in-scope issuers that have a
10-K or 10-Q filed after B:

| Boundary B | Issuers with documents | Of which rating changed after B | With a post-B 10-K | Median package, tokens | Packages over 262k |
|---|---|---|---|---|---|
| 2024-09-30 | 59 | 12 | 59 | 182,000 | 11 |
| 2024-12-31 | 59 | 11 | 53 | 175,000 | 8 |
| 2025-01-31 | 59 | 10 | 52 | 171,000 | 8 |
| 2025-02-28 | 59 | 9 | 32 | 135,000 | 1 |
| 2025-03-31 | 58 | 7 | 13 | 117,000 | 1 |
| 2025-04-30 | 58 | 5 | 5 | 81,000 | 1 |
| 2025-05-31 | 55 | 3 | 2 | 61,000 | 1 |
| 2025-06-30 | 36 | 2 | 2 | 65,000 | 0 |
| 2025-07-31 | 23 | 1 | 1 | 58,000 | 0 |
| 2025-08-31 and later | disclosure window instead: 20 issuers, 2 changes if the bound is before October 2025, otherwise 0 | | | 137,000 | 0 |

Two things stand out. The retail 10-K season is February to April, so a bound after January
2025 loses the 10-Ks and leaves 10-Q packages, which are smaller and thinner. And the
official window dries up after May 2025; from there on the only labels are the 20
disclosures. Every month Moody's extends its file adds roughly two changes among our issuers
to the official window; with the lab's rating data the gap closes at once.

## 2. Candidates and where each one sits

Bound = the vendor's stated cutoff where one exists (Meta, OpenAI, Anthropic), otherwise the
release date of the pinned checkpoint, since a model cannot contain data published after its
release. Model cards of Qwen, Kimi, GLM and DeepSeek state no cutoff; the dates that circulate
for them are hearsay and are not used. Capability tiers are the public consensus of the
model's generation, not our measurement; section 4 measures it on our task.

| Model, pinned ID | Bound | B | Labelled changes available now | Context served (best provider) | Price in / out per MTok | Generation and tier |
|---|---|---|---|---|---|---|
| Llama 4 Maverick, `meta-llama/llama-4-maverick` | stated: Aug 2024 | 2024-09-30 | 12 official + 2 disclosed = 14 | 1M (DeepInfra, Novita, fp8) | $0.20 / $0.80 | Apr 2025, weak for its date |
| DeepSeek V3, `deepseek/deepseek-chat` | release 2024-12-26 | 2025-01-31 | 10 + 2 = 12 | 164k (DeepInfra, fp4 only) | $0.32 / $0.89 | Dec 2024, the best open model of its time |
| DeepSeek V3-0324, `deepseek/deepseek-chat-v3-0324` | release 2025-03-24 | 2025-04-30 | 5 + 2 = 7 | 164k (Crusoe bf16, SiliconFlow fp8) | $0.25 to $0.50 / $1.00 to $1.50 | Mar 2025, strong non-reasoning |
| Qwen3-235B-A22B, `qwen/qwen3-235b-a22b` | release 2025-04-28 | 2025-05-31 | 3 + 2 = 5 | 131k (Alibaba only) | $0.45 / $1.82 | Apr 2025, hybrid reasoning, context too small for full packages |
| Qwen3-235B-A22B-2507, `qwen/qwen3-235b-a22b-2507` | release 2025-07-21 | 2025-08-31 | 1 + 2 = 3 | 262k (GMICloud, DeepInfra, Nebius, Google; fp8) | $0.0875 / $0.35 at GMICloud, a 75% promotion off $0.35 / $1.40; DeepInfra $0.09 / $0.55 | Jul 2025, strong non-reasoning, cheapest fit |
| Kimi K2-0905, `moonshotai/kimi-k2-0905` | release 2025-09-04 | 2025-10-31 | 2 | 262k (Novita, fp8) | $0.60 / $2.50 | Sep 2025, strong non-reasoning |
| Qwen3-Max, `qwen/qwen3-max` | release 2025-09-23 | 2025-10-31 | 2 | 262k (Alibaba, closed weights) | $0.78 / $3.90 | Sep 2025, Alibaba flagship |
| GLM-4.6, `z-ai/glm-4.6` | release 2025-09-30 | 2025-10-31 | 2 | 205k (Novita, bf16) | $0.55 / $2.20 | Sep 2025, strong, reasoning mode |
| DeepSeek V3.2-Exp, `deepseek/deepseek-v3.2-exp` | release 2025-09-29 | 2025-10-31 | 2 | 164k (fp8) | $0.27 / $0.41 | Sep 2025, reasoning mode, context short |
| Claude Haiku 4.5, `claude-haiku-4-5-20251001` | stated: Jul 2025 | 2025-08-31 | 1 + 2 = 3 | 200k | $1 / $5, half in batch | Oct 2025, same code as Exp 03 |
| Claude Opus 4.6, done | stated: Aug 2025 | 2025-09-30 | 2 | 1M | $5 / $25, half in batch | n = 7 measured |

Anything released after October 2025 (Kimi K2 Thinking, GLM-4.7 and 5, DeepSeek V3.2 and V4,
Qwen3.5 and later, Mistral Large 3) has zero labelled changes today, however strong.

The sweet spot with today's labels is not one model but two tiers:

- **Same window as Opus 4.6, strong and cheap:** Qwen3-235B-A22B-2507 (fits every package at
  262k, $0.30 per pass over the 20 issuers), with GLM-4.6 as the reasoning-mode counterpart
  (205k, fits 15 of 16) and Kimi K2-0905 or Qwen3-Max if a third opinion is wanted. Two
  changes now, growing as the official file catches up.
- **More changes, one generation older:** DeepSeek V3-0324 on the combined window (official
  May to August 2025 plus the disclosure window: 78 observations, 7 changes), at 164k with
  10-K plus latest 10-Q only. DeepSeek V3 of December 2024 reaches 12 changes with the full
  10-K season, but is served only at fp4 and is a year older.

Llama 4 Maverick has the most changes and a real 1M context, but its generation is weak; it
is a floor, not a candidate.

## 3. Is 262k enough

Yes. All 16 Experiment 03 packages fit (largest 246,000 tokens on the Anthropic tokenizer;
Qwen's tokenizer is comparable); for boundaries from February 2025 on, at most one package
exceeds 262k, and it loses its oldest 10-Q. 200k fits 15 of 16. 164k needs the 10-K plus the
latest 10-Q for about a third of packages. 131k is too small for full packages. One rule for
all: a package that does not fit is trimmed by dropping the oldest 10-Q and flagged, never
truncated by the provider (section 5, rule 4).

## 4. Order of work

1. **Capability shootout, in sample, cheap.** The same 30 non-gold historical observations
   (2019 to 2023, all inside every model's training data) through the Experiment 03 prompt on
   every candidate: agreement with the label, within-one rate, false alarms, extraction
   agreement with XBRL, and the replicate spread. About $0.10 to $0.60 per model. This ranks
   the models on our task, which public benchmarks do not measure, and it is not an
   out-of-sample claim.
2. **Arm 1**, the Experiment 03 window on the two best of the September 2025 tier plus
   Qwen3-235B-2507: 20 issuers, three replicates, about $5 in total, next to Opus 4.6's 7.
3. **Arm 2**, the combined window on DeepSeek V3-0324 (and DeepSeek V3 if the fp4 serving is
   accepted): 58 official-label issuers at 2025-08-28 plus the 20 disclosures, three
   replicates, about $10. The in-sample contrast on the 2023 cross-section adds the
   memorisation estimate for the same models at the same cost.
4. **Rerun as labels grow**, monthly, for cents: each refresh of the Moody's file moves
   changes from unlabelled into the official window for the September 2025 tier.

## 5. Rules that make an open-model run valid

1. Pinned checkpoints only; the `model` field of every response stored.
2. One provider per model, pinned through OpenRouter's provider routing, with context
   length and quantisation recorded; prefer bf16 or fp8 over fp4. US or EU hosts for the
   Chinese-origin weights if HPI policy requires; the inputs are public SEC filings.
3. The bound recorded with evidence per model (release announcement or vendor cutoff
   statement, quoted and dated).
4. No silent truncation: the provider's prompt-token count must match the local count within
   2% (RUN-SPEC.md section 7), otherwise the observation is discarded and logged.
5. Three replicates at temperature 0 with a fixed seed where accepted; spread reported.
6. JSON schema through `response_format` (every shortlisted provider supports it); one re-ask
   on a parse failure, failures counted.
7. Every Experiment 03 control unchanged: documents strictly after B and on or before the
   observation date; exhibits and 8-Ks never input; redaction with removed lines stored; the
   history pack capped at B, not at the file end, because everything after B is label; peer
   facts filed before the observation date; a memory probe per issuer completed and reviewed
   before any document request.
8. Labels: Arm 1 as Experiment 03 (Qurate kept or dropped by decision); Arm 2 from the 17g-7
   records, changed meaning an action dated in (B, observation date], scored as in
   score_run.py.
9. Cost guard: local token count and a cap set by Robert before submission; actual cost read
   back per request.
10. Transport: OpenRouter's chat completions endpoint over HTTPS with `httpx` (the `openai`
    package is not installed and not needed); the request record keeps the Experiment 03
    shape so results are comparable.

## 5a. Status, 2026-09-13

Arm 1 was frozen, reviewed and executed. Codex's review of 2026-09-12
([review-codex-2026-09-12.md](review-codex-2026-09-12.md)) refused the first specification and
set twelve acceptance gates; the implementation of 2026-09-13 satisfies them with recorded
evidence (runs/EXP04-ARM1-A1/gates/, forty offline tests against the production dispatch path).
Robert's decisions D5 to D12 are in [decisions.md](decisions.md); the specification as
executed is [RUN-SPEC.md](RUN-SPEC.md); the results, with every attempt and the actual spend,
are in [results.md](results.md). Two rules in this plan changed on the way: rule 4's tolerance
became the rendered-count policy of RUN-SPEC.md section 7, and rule 10's transport is `httpx`.

## 6. Deliverables

This README (design plan), RUN-SPEC.md (the run as executed), decisions.md, the Codex review,
authorization.json (the cap and scope bound to the manifest hash), evidence/ (cutoff notes,
OpenRouter model list, per-provider endpoint snapshots, exact token counts), prepare_inputs.py
(offline preparation of every body, hash and bound), run_openrouter.py (guarded submission,
ledger, validation, scoring, gates), test_runner.py (the acceptance tests), legacy_provenance.py
with legacy_builders/ (the 2026-09-10 builders, vendored, for the saved-input control's source
dates), count_tokens_qwen.py, runs/ (gitignored: manifest, bodies, ledger, raw responses,
audit, results), and results.md. Prompts are read from Experiment 03's folder, unchanged.
