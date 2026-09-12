# Experiment 04, Arm 1: exact run specification for review

*Written 2026-09-12 by Claude (Fable 5.1), directed by Robert Vetter. Nothing has been run.
Every number here was measured locally on 2026-09-12: token counts with the Qwen3 tokenizer
(transformers 4.57.6, `Qwen/Qwen3-235B-A22B-Instruct-2507`) on the actual assembled requests,
provider facts from OpenRouter's endpoints API (evidence/endpoints-2026-09-12/), credit balance
from OpenRouter's credits endpoint. **This document is for Codex to review before any money is
spent.** Section 10 lists what to attack.*

## 1. What this run is and is not

The same test as Experiment 03, same boundary, same documents, same prompts, same labels, one
thing changed: the model. Opus 4.6 produced 7 usable observations of 20 because of cost. Qwen3
costs about 2% as much per token, so all 20 run with three replicates for about a dollar.

It is a post-cutoff cross-section of the outstanding rating at one date, scored against
persistence. It is not a forecast, not a certified benchmark, and not a claim about label
validity beyond what Experiment 03 already documented.

## 2. Model and provider

| Item | Value | Source |
|---|---|---|
| Model ID | `qwen/qwen3-235b-a22b-2507` | OpenRouter model list |
| Weights | Qwen3-235B-A22B-Instruct-2507, open weights, Apache 2.0 | Hugging Face model card |
| Training data bound | **release 2025-07-21**; the model card states no cutoff, so the release date of the pinned checkpoint is the bound | evidence/cutoffs-2026-09-12.md |
| Reasoning | none; this is the non-thinking Instruct variant (`reasoning` not offered by its endpoints) | endpoints API |
| Context served | 262,144 (GMICloud, DeepInfra, Nebius, Google) | endpoints API |
| Price | $0.09 in / $0.35 out per MTok (GMICloud); DeepInfra $0.09 / $0.55 | endpoints API |
| Provider to pin | **GMICloud**, fp8, 262k, supports `response_format`, `seed`, `temperature`; fallback DeepInfra, same precision and context | endpoints API |
| Quantisation | fp8 (recorded per response; fp4 providers are excluded) | endpoints API |

**Why this model.** Its bound (2025-07-21) lies before the boundary below, so the run is out of
sample by the same rule as Experiment 03. It is the most recent open-weight model whose bound
still clears the boundary, and 262k fits the packages. Everything stronger and newer (GLM-5,
DeepSeek V4, Qwen3.5, Kimi K2.5) was released after the labelled rating actions and is
therefore ineligible, however cheap.

**Boundary check for this model.** Documents used are filed 2025-12-18 to 2026-08-28, all after
2025-07-21. The two labelled rating actions are October and November 2025, also after it. The
history pack ends 2025-08-28, which is public information the model may legitimately hold.

## 3. Boundary and dates, unchanged from Experiment 03

| Object | Rule |
|---|---|
| Document boundary B | 2025-09-30, every input filing has `filingDate > B` |
| Observation date | 2026-08-29, every input filing has `filingDate <= as_of` |
| History pack | rating events through 2025-08-28 only; XBRL facts filed on or before as_of |
| Peer table | XBRL facts filed on or before as_of, no peer ratings |
| Labels | the issuer's own rating disclosure in a filing in (B, as_of], hand-read, confirmed by Robert 2026-08-31 |

## 4. The 20 issuers, their documents, and exact token counts

Counted on the fully assembled request (system prompt, redacted documents, history pack with
peer table, task, schema) with the Qwen3 tokenizer. Limit is 253,952 = 262,144 minus 8,192
reserved for output.

| ID | Issuer | Persistence | Label | Changed | Documents used | Qwen tokens | Fit |
|---|---|---|---|---|---|---|---|
| X01 | Bath & Body Works | Ba2 | Ba2 | no | 10-K 2026-03-12, 10-Q 2026-05-27, 10-Q 2026-08-26 | 148,071 | yes |
| X02 | Best Buy | A3 | A3 | no | 10-K 2026-03-18, 10-Q 2026-06-05 | 124,993 | yes |
| X03 | Dick's Sporting Goods | Baa2 | Baa2 | no | 10-K 2026-03-27, 10-Q 2026-06-04 | 156,121 | yes |
| X04 | Dollar General | Baa3 | Baa3 | no | 10-K 2026-03-20, 10-Q 2026-06-02, 10-Q 2026-08-27 | 167,207 | yes |
| X05 | Floor & Decor | Ba3 | Ba3 | no | 10-K 2026-02-19, 10-Q 2026-04-30, 10-Q 2026-07-30 | 155,707 | yes |
| X06 | Gap | Ba2 | Ba2 | no | 10-K 2026-03-17, 10-Q 2026-05-29, 10-Q 2026-08-28 | 146,783 | yes |
| X07 | Kohl's | B2 | B2 | no | 10-K 2026-03-19, 10-Q 2026-06-04 | 92,748 | yes |
| X08 | Leslie's | Caa3 | Caa3 | no | 10-K 2025-12-18, 10-Q 2026-02-18, 10-Q 2026-05-13, 10-Q 2026-08-12 | 200,033 | yes |
| X09 | Levi Strauss | Ba1 | Ba1 | no | 10-K 2026-01-28, 10-Q 2026-07-08 (oldest 10-Q dropped) | 235,598 | trimmed |
| X10 | Lowe's | Baa1 | Baa1 | no | 10-K 2026-03-23, 10-Q 2026-05-28, 10-Q 2026-08-27 | 162,053 | yes |
| X11 | Macy's | Ba1 | Ba1 | no | 10-K 2026-03-27, 10-Q 2026-06-04 | 127,584 | yes |
| X12 | Nike | A1 | **A2** | **yes** | 10-K 2026-07-15 | 128,813 | yes |
| X13 | PVH | Baa3 | Baa3 | no | 10-K 2026-03-31, 10-Q 2026-06-05 | 210,531 | yes |
| X14 | Qurate / QVC | Caa1 | **Caa3** | **yes** | 10-K 2026-04-15, 10-Q 2026-08-04 (oldest 10-Q dropped) | 212,906 | trimmed |
| X15 | Signet | Ba3 | Ba3 | no | 10-K 2026-03-19, 10-Q 2026-06-02 | 189,926 | yes |
| X16 | Target | A2 | A2 | no | 10-K 2026-03-11, 10-Q 2026-05-29, 10-Q 2026-08-28 | 132,137 | yes |
| X17 | Tractor Supply | Baa1 | Baa1 | no | 10-K 2026-02-19, 10-Q 2026-05-07, 10-Q 2026-08-06 | 149,955 | yes |
| X18 | V.F. | Ba2 | Ba2 | no | 10-K 2026-05-20, 10-Q 2026-07-29 | 214,412 | yes |
| X19 | Victoria's Secret | Ba3 | Ba3 | no | 10-K 2026-03-20, 10-Q 2026-06-05 | 135,215 | yes |
| X20 | Walmart | Aa2 | Aa2 | no | 10-K 2026-03-13, 10-Q 2026-05-29, 10-Q 2026-08-28 | 194,370 | yes |

Totals: 51 documents, all already cached locally under
`evaluation/companies/<slug>/filings/`, so the run needs no SEC download. Input for one pass
after trimming: **3,285,163 tokens**. Largest package 235,598. The history pack is 17,700 to
18,800 tokens per issuer, most of it the peer table.

**Trim rule.** Two packages exceed the limit with the full document set (Levi 285,930, Qurate
257,089). Dropping the single oldest 10-Q brings both under it, as shown. This is the only
deviation from Experiment 03's document rule and it must be flagged per observation in the
results: for these two issuers the model sees one 10-Q less than Opus 4.6 did. Never allow the
provider to truncate instead (section 7).

**Eight issuers Opus never ran.** X01, X02, X03, X04, X05, X06, X07, X10, X11 were scheduled
but lost to the output ceiling; X08, X09, X13, X18 were never scheduled. All 13 are in this
run. The seven Opus scored (X12, X14, X15, X16, X17, X19, X20) are also in it, which gives a
direct model-to-model comparison on identical inputs.

## 5. Request contents, unchanged from Experiment 03

Per issuer, one document request containing, in this order:

1. `prompts/system.txt` of Experiment 03, verbatim, as the system message.
2. The redacted documents, each wrapped as
   `<document name="10-K filed 2026-03-12">...</document>`. Text extraction by
   `run_eval.to_text`, rating self-disclosures removed by `system/redact.py`, removed lines
   stored per observation. No exhibits, no 8-Ks.
3. The history pack from `evaluation/pipeline/history_pack.py` with
   `history_end="2025-08-28"`: rating path to that date, the rating then in effect, three
   prior fiscal years plus the current one from XBRL with filed dates, the implied qualitative
   anchors, recent quarterly rows, and the peer table without ratings.
4. `As-of date: 2026-08-29.` followed by `prompts/task_values_first.txt`, verbatim.
5. The output schema, `prompts/schema_values_first.json`, as a JSON-schema response format.

Per issuer, one memory probe request submitted and reviewed **before** the document request:
`prompts/probe.txt` system and user, the issuer's EDGAR name, the probe schema from
`run_batch.py`, no documents. This fixes the Experiment 03 defect where probes and documents
shared one batch and probe-first processing could not be proven.

No tools array, no retrieval, no web access, no RAG. OpenRouter's plugins and web search are
not used; the request carries no `tools` and no `plugins` field.

## 6. Sampling, replicates, output

| Parameter | Value | Reason |
|---|---|---|
| `temperature` | 0 | determinism as far as the provider allows |
| `seed` | 20260912 | accepted by GMICloud and DeepInfra |
| `max_tokens` | 8,192 for documents, 1,200 for probes | the Experiment 03 lesson: the ceiling must comfortably exceed the answer. This model has no thinking tokens, and the Opus answers were 6.6k to 8.6k including thinking, so 8,192 for answer only is generous |
| `response_format` | `{"type":"json_schema","json_schema":{"name":"scorecard_inputs","strict":true,"schema": <prompts/schema_values_first.json>}}` | the Anthropic `output_config.format` equivalent |
| Replicates | 3 per issuer, same seed, submitted as separate requests | a third-party fp8 MoE is not bit-reproducible; the spread is the measurement, per the experiment plan's Phase 0 |
| Transport | OpenRouter chat completions, synchronous, sequential with retry | OpenRouter has no batch discount; there is nothing to gain from concurrency here |

## 7. Guards

1. **Cumulative cost ledger.** A JSON file that every request appends to: request id, issuer,
   replicate, reported prompt and completion tokens, cost from the response's usage. The
   runner refuses to start a request if the ledger total plus the worst case of that request
   would exceed the cap. This replaces Experiment 03's per-submission constants, which the
   integrity review flagged as reusable.
2. **Pre-flight, free.** Local token count per request, printed, compared against the limit,
   and a cost projection, with no network call. Then exactly one real request on one issuer,
   inspected, before the remaining 59.
3. **Truncation check.** The provider's reported `prompt_tokens` must be within 10% of the
   local Qwen count. A shortfall means the input was silently truncated: the observation is
   discarded, logged, and not scored. This is the main new risk relative to a first-party API.
4. **Parse failures.** One re-ask per failed JSON parse, then the observation is recorded as
   failed and counted in the results. Never silently dropped.
5. **Provenance.** Per response store the `model` string, the provider name, the finish
   reason, usage, and the OpenRouter generation id, so the served model and provider are
   evidence rather than an assumption.
6. **The fixed scorecard.** Scoring uses `system/scorecard.py` as of 2026-09-12, with the
   negative-EBITDA and net-cash rules. Qurate is exactly the case that triggers the negative
   Debt/EBITDA rule, so an unfixed engine would silently produce the old wrong answer.

## 8. Cost against the real balance

OpenRouter balance on 2026-09-12: 55.00 credits granted, 47.46 used, **7.536 remaining**
(credits endpoint). The key is in `.env` as `OPEN_ROUTER_API_KEY`.

| Item | Input tokens | Cost at $0.09 / $0.35 per MTok |
|---|---|---|
| One pass, 20 issuers | 3,285,163 | $0.296 input, about $0.03 output, **$0.33** |
| Three replicates | 9,855,489 | **$0.98** |
| 20 memory probes | about 8,000 | under $0.01 |
| One pass on the 7 Opus issuers only, for the direct comparison | 1,141,046 | $0.11 |
| **Proposed run total** | | **about $1.00 of $7.54** |

Proposed cap: **$3.00**, which leaves room for one full re-run after a defect and still keeps
more than half the balance. Robert sets the final number.

## 9. Outputs and scoring

Everything under `experiments/04-open-weight-cross-section/runs/<timestamp>/` (gitignored):
`requests.json` with every prompt verbatim, `raw_outputs.json`, `audit.json` with the date
checks, per-observation token counts, trim flags, provider and model strings, redacted-line
counts and the cost ledger, and `results.json` with the scored records.

Scored exactly as Experiment 03 and `evaluation/pipeline/score_run.py`: exact accuracy, within
one notch, MAE, all next to persistence on the same labels, split changed and unchanged, false
alarms on the unchanged subset, and the replicate spread per observation. Reported both on all
20 and on the 7 issuers Opus scored, so the model comparison is like for like. Qurate reported
with and without, as in Experiment 03.

## 10. What Codex should attack in this specification

1. **The response-format translation.** Anthropic's `output_config.format` became OpenRouter's
   `response_format` with `strict: true`. Does the schema in `prompts/schema_values_first.json`
   satisfy the provider's strict-mode constraints (required keys, `additionalProperties`,
   nested objects), and does GMICloud actually enforce it rather than ignoring it?
2. **The truncation check.** Is comparing the provider's `prompt_tokens` against a local
   `AutoTokenizer` count sound, given the chat template adds tokens? What tolerance is right,
   and is 10% too loose to catch a dropped document?
3. **The trim.** Levi and Qurate lose their oldest 10-Q. Does that break the model-to-model
   comparison for Qurate, which is one of only two changed cases?
4. **Determinism.** Temperature 0 with a seed on an fp8 MoE served by a third party. Is three
   replicates enough to characterise the spread, and should the spread be measured on the
   scorecard inputs or only on the final rating?
5. **The bound.** Using the release date as the training-data bound where the vendor states no
   cutoff. Is the release date of `Qwen3-235B-A22B-Instruct-2507` (2025-07-21) established well
   enough, and is a bound of this kind defensible in the write-up?
6. **Leakage.** The history pack and peer table are byte-identical to Experiment 03, so no new
   channel opens; confirm that, and confirm that OpenRouter adds no retrieval by default.
7. **The cost ledger.** Does the guard actually prevent an overrun mid-run, including retries
   and re-asks?
8. **Scoring parity.** Are the Qwen results scored through exactly the same code path as the
   Opus results, so the comparison is not an artefact of two scoring paths?

## 11. Decisions still needed from Robert

- Cap: $3.00 proposed against a $7.54 balance.
- Provider: GMICloud proposed, DeepInfra as fallback; fp4 providers excluded.
- Replicates: three proposed.
- Qurate: keep in the set and report with and without, as in Experiment 03.
- Whether to also run the second-tier model (GLM-4.6 or Kimi K2-0905) for a second opinion at
  about $2 per pass, or keep that for later.
