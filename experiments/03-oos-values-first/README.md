# Experiment 03 — Out-of-sample cross-section, values-first: the leakage-free answer to Xiaowei's question

*Design plan v0.1, 2026-08-31, by Robert Vetter and Claude (Opus 5). Status: READY — decisions D1–D10 taken (decisions.md), 20 labels confirmed, 16 selected for the
run under the $10 cap; waiting only on API credits for the count_tokens preflight and submission. This document supersedes the fresh
arm of Experiment 01 and replaces Experiment 02's historical arm as the basis for any
out-of-sample claim.*

## 0. The question and the standard

Xiaowei: *"Take an LLM, note its training data cutoff, run a relatively good prompt on truly
out-of-sample cross-sectional data — what's the accuracy ratio? Provide the specification."*

Standard we hold ourselves to, learned the hard way in Experiments 01 and 02: **every input
the model sees is provably dated; every label is provably after the model's training data
cutoff; every claim in the write-up points at a file.** Section 9 lists each earlier mistake
and the rule that now prevents it.

## 1. Model and parameters (verified 2026-08-31)

| Item | Value | Source |
|---|---|---|
| Model | Claude Opus 4.6, API ID `claude-opus-4-6` (dateless IDs are pinned snapshots) | https://platform.claude.com/docs/en/models/opus-4-6/overview |
| **Training data cutoff** | **Aug 2025** | same page, "Capabilities" table |
| Reliable knowledge cutoff | May 2025 (not used as boundary — we take the broader training cutoff) | same page |
| Context window / max output | 1M tokens / 128K | same page |
| Price | $5 / $25 per MTok; Batch API 50% off; cache write $6.25, read $0.50 | same page, "Pricing" |
| Status | Active (legacy); retirement not sooner than 2027-02-05 | same page + https://platform.claude.com/docs/en/about-claude/model-deprecations |
| Thinking | `thinking: {"type": "adaptive"}` set explicitly (on Opus 4.6 omitting it runs without thinking) | https://platform.claude.com/docs/en/build-with-claude/thinking |
| Effort | `output_config.effort` — decision D5 | https://platform.claude.com/docs/en/build-with-claude/effort |
| Output | structured output, `output_config.format` JSON schema (schema in prompts/schema_values_first.json) | https://platform.claude.com/docs/en/build-with-claude/structured-outputs |
| Sampling | defaults; no temperature/top_p/top_k set | — |
| Tools | **none** — no `tools` array in any request (no retrieval, no web) | structural |
| Transport | Message Batches API, **without** `cache_control` (see §9, Exp 02 lesson); `count_tokens` preflight on every request before submission | https://platform.claude.com/docs/en/build-with-claude/batch-processing |

Why Opus 4.6 and not Opus 4.5 or Opus 5: same Aug 2025 training cutoff as 4.5 (longest
window among available strong models) but a 1M context, so full 10-K + 10-Q sets fit
(Nike's 10-K alone exceeded 4.5's 200K). Opus 5's cutoff (May 2026) leaves a 3-month window
with almost no verifiable rating changes. Older models with earlier cutoffs are retired on
the Claude API (Sonnet 4, Opus 4, Opus 4.1, Sonnet 3.7 — deprecations page above); the
Bedrock route to Sonnet 4 / Opus 4.1 is parked (decisions.md, D8) pending AWS access.

## 2. The out-of-sample boundary and how it is enforced mechanically

**Boundary B = 2025-09-30** (training cutoff Aug 2025 plus a one-month buffer, decision D1),
applied to every date that matters:

| Object | Rule | Enforced by |
|---|---|---|
| Input documents | `filingDate > B` for every 10-K / 10-Q given to the model | assertion in the runner; violating observation is skipped and logged |
| Observation as-of date | `as_of = 2026-08-29` (cross-section date) > B | constant |
| Label (rating in effect at as-of) | evidence = company self-disclosure in a filing with `filingDate > B` and `filingDate <= as_of`; hand-validated statement of the *current* rating (not a covenant threshold, not a pricing grid) | candidates.json carries filing date, URL, snippet, validator, date of validation |
| Changed-vs-unchanged | changed if disclosed rating ≠ last file rating (Moody's 17g-7 file, content through Aug 2025). The action's uncertainty window is (last file confirmation, first disclosure]; it lies after B by construction because the file ends before B | derived, stored per candidate |
| History pack | rating events from the 17g-7 file (all ≤ Aug 2025, i.e. pre-cutoff public facts the model may know anyway — not leakage of the label); quantitative XBRL values only with `filed <= as_of` | assertion in pack builder; every fact printed with its filed date |
| Peer table | XBRL facts with `filed <= as_of`, no ratings | peer_table.py filter |
| Audit | each observation's run record lists every input document date, every pack fact date, and the boundary check result | runs/<batch>/audit.json |

No date is ever taken from a document's text; all come from EDGAR filing metadata (manifest)
and the 17g-7 records. The 8-K form is used for **label harvesting only** (downgrade
announcements), never as model input (decision D4).

## 3. Cross-section and labels

Universe: the 63 in-scope Retail & Apparel current filers of the evaluation frame. Eligible:
(a) at least one 10-K or 10-Q with `filingDate > B`; (b) a hand-validated label per §2.
Label harvest procedure (`harvest_labels.py`, to be written): scan **every** 10-K, 10-Q and
8-K filed in (B, as_of] for rating symbols within 400 characters of "Moody"; render every
hit with its snippet into `label-review.md`; Claude classifies (current-rating statement /
threshold or grid language / historical reference), Robert confirms; accepted labels go to
`candidates.json` with evidence. Expected from the Experiment 01 harvest (latest four filings
only): 15 companies, 1 change; with all filings and 8-Ks: more coverage, plausibly 3–6
changes. The true count is a result of the harvest, not an assumption.

Persistence baseline per company = rating in effect at the end of the 17g-7 file's content
(2025-08-28, the latest action date in the file — measured, not assumed from the file date),
the last rating anyone could have known without post-cutoff information.

## 4. Inputs — everything useful the model may legitimately see (decision D2/D3)

Per observation, in this order inside one request:

1. **Documents (redacted):** the most recent 10-K filed after B, plus every 10-Q filed after
   it up to as_of (D2). Rating self-disclosures removed by `system/redact.py`; removed lines
   stored.
2. **History pack** (`evaluation/pipeline/history_pack.py`, fixed after Exp 02):
   - the issuer's full Moody's rating path to Aug 2025 with dates and action codes, and the
     rating in effect at file end (the persistence value);
   - the **implied scorecard anchors** for that rating (Exhibit 3/4 bands), so grades are
     assessed *relative* to the prior state rather than from scratch;
   - **prior-period quantitative values** from XBRL: the last three fiscal years and the
     last four quarters of the ten figures where tagged (D3 extends fetch_xbrl.py to quarterly
     facts), each with its filed date, so the model has the trajectory, not a snapshot.
   - Note on "historical qualitative values": Moody's does not publish per-factor grades; no
     public source exists. The implied anchors are the closest legitimate substitute and are
     labelled as such in the pack.
3. **Peer table** at as_of: point-in-time XBRL key figures of the in-scope peers, no ratings.
4. **Task** (prompts/task_values_first.txt): produce the ten figures for the most recent
   fiscal year in the documents and the four qualitative grades, each with a one-line
   justification tied to the documents and a "relative to prior implied anchor: up / same /
   down" flag; then, as a separate field, the model's own overall rating judgement.

## 5. Method — values first, arithmetic second, judgement recorded (decision D6)

- **Primary channel (this experiment's method):** the ten figures → `system/scorecard.py`
  computes the four quantitative subfactor scores deterministically; the four grades map via
  Exhibit 3; weighted sum → Exhibit 5 lookup → scorecard-indicated rating.
- **Recorded alongside:** the model's overall judgement from the same call (`direct_rating`),
  because in Experiment 02 this post-extraction judgement was the strongest channel.
- **Retired: the pure direct-rating variant (Experiment 01's and 02's variant B).** Evidence,
  documented so it is not re-litigated: Exp 01 (post-cutoff, no history): B exactly matched
  persistence (5/6). Exp 02 (historical arm, with history): B was persistence-biased —
  "unchanged, high confidence" on three of six actual changes — 4/9 exact vs. A-direct 6/9.
  The raw scorecard arithmetic was the *worst* channel in both (systematic pull toward
  investment grade); it stays because it is the methodology-faithful, auditable number and
  its optimism is itself a measurable, correctable finding.

## 6. Contamination probes (unchanged from Exp 01/02, decision D7)

Per observation a separate request with no documents: current Moody's rating, adjusted
metrics, most recent fiscal-year revenue and its end date, recent rating actions —
classified CLEAN / RECALLS_PRIOR / CONTAMINATED (post-cutoff specifics reproduced). Headline
metrics on the clean subset; the rest reported alongside, never dropped. Prompt in
prompts/probe.txt.

## 7. Metrics

Xiaowei's accuracy ratio = exact-hit share of the scorecard-indicated rating against the
label; also within-one-notch share and MAE; all next to the persistence baseline; split by
changed / unchanged (false-alarm rate on unchanged; direction accuracy on changed); the
recorded judgement channel scored the same way; paired bootstrap CI. Extraction accuracy of
the ten figures scored against XBRL (`check_extraction.py`) at zero model cost.

## 8. Cost (decision D9)

Per observation: documents 60–300k tokens (10-K plus up to three 10-Qs) + pack/peers ~6k,
output ~4k with thinking. At Opus 4.6 batch prices (input $2.50/M, output $12.50/M): roughly
$0.30–0.90 per observation plus ~$0.02 per probe. For ~20 labeled companies: **$10–20**
including probes. Exact figure from `count_tokens` before submission; hard guard at the cap.

## 9. Lessons from Experiments 01 and 02, each turned into a rule here

| Mistake | Rule in Experiment 03 |
|---|---|
| Exp 02 used pre-cutoff observations and the headline read as leakage-free | Every observation strictly after B; the historical arm is explicitly *not* part of any OOS claim |
| Kohl's "Baa3" harvested from a covenant threshold clause | Every label snippet classified and hand-validated; classification stored |
| Nike counted as OOS for Opus 5 although its action predated May 2026 | OOS judged on the action's uncertainty window, which here lies after B by construction (file ends before B) |
| Under Armour: quarter-start rating computed inclusively leaked an in-quarter action | Pack states the rating as of file end (Aug 2025), all pack dates printed and asserted ≤ as_of; no in-window rating information anywhere in the input |
| Nike's 10-K did not fit Opus 4.5's 200K context | Opus 4.6, 1M context; count_tokens preflight per request |
| `cache_control` in batch charged the write premium twice, 21 cents over cap | No cache_control in batch; guard prices the worst case; cap enforced before submission |
| Memory can hold the answer (blind test) | Probes per observation; clean-subset headline |
| Filings disclose their own ratings (leakage audit) | Redaction before input, removed lines stored; 8-Ks never used as input |

## 10. Deliverables

`README.md` (this plan, updated to v1.0 at sign-off), `decisions.md`, `prompts/` (verbatim
prompt texts and schema), `harvest_labels.py`, `label-review.md`, `candidates.json`,
`run_batch.py`, `runs/<batch>/` (requests, raw outputs, audit.json with all date checks,
results.json), `results.md`. Reused: `system/redact.py`, `system/scorecard.py`,
`evaluation/pipeline/history_pack.py`, `peer_table.py`, `fetch_xbrl.py`, `check_extraction.py`.
