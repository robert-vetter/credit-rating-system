# Experiment 04, Arm 1: the run specification as frozen and executed

*Written 2026-09-12 by Claude (Fable 5.1), directed by Robert Vetter, reviewed by Codex the same
day (review-codex-2026-09-12.md, twelve acceptance gates), then rewritten on 2026-09-13 to
describe the experiment exactly as it was frozen in the manifest and executed under Robert's
authorization EXP04-ARM1-A1. Every number below is either in the manifest, the ledger or the
audit files under runs/EXP04-ARM1-A1/ (gitignored, on this machine), or in the evidence
folder. Results and actual spend are in results.md. Earlier versions of this file, including
the two rounds of pre-review corrections, are in Git history.*

## 1. What this run is and is not

A post-release, history-conditioned disclosure-label pilot. The same test as Experiment 03
(same boundary, documents, prompts, labels and scoring arithmetic) on an open-weight model
whose public checkpoint release precedes the labelled rating actions, run twice: once on the
current, repaired inputs for all 20 confirmed issuers, and once on the exact saved inputs
Opus 4.6 saw for the seven issuers it scored. Three replicates each, one memory probe per
issuer first.

It is not a certified outstanding-rating benchmark: the labels are the issuers' own
disclosures, hand-read and confirmed, whose validity at the observation date is not
established (Qurate's is unresolved and is reported as a diagnostic only). It does not claim
absent contamination, solved extraction, advance forecasting, equivalence with Opus, or
generalised superiority over persistence.

## 2. Model, provider and bound

| Item | Value | Evidence |
|---|---|---|
| Model | `qwen/qwen3-235b-a22b-2507` (Qwen3-235B-A22B-Instruct-2507, open weights, Apache 2.0, non-thinking) | OpenRouter listing; Hugging Face model card |
| Training-data bound | the public checkpoint release, upload commit `d4dc8b02` of 2025-07-21, weight shards unchanged since; an upper bound on the training information of those weights, not a vendor-stated cutoff | evidence/cutoffs-2026-09-12.md; review-codex-2026-09-12.md |
| Tokenizer used locally | the same repository, snapshot `ac9c66cc9b46af7306746a9250f23d47083d689e`, file hashes in audit/environment.json | Hugging Face cache, offline |
| Provider | DeepInfra, endpoint `deepinfra/fp8`, 262,144 context, 16,384 completion limit; pinned by `provider.order`, `allow_fallbacks: false`, `require_parameters: true`, `quantizations: ["fp8"]`, `max_price` $0.09 / $0.55 per million tokens (decision D6) | evidence/endpoints-2026-09-12/, live listing re-read at every submission |
| Served identity | every response's `model` and `provider` fields and the generation record are compared with the authorization; a mismatch halts the run. The hosted fp8 deployment is the host's identity claim; it is recorded, not proven | ledger |
| Reasoning | none (Instruct variant) | endpoint parameters |

## 3. Boundary and dates

| Object | Rule |
|---|---|
| Document boundary B | 2025-09-30; every input filing has `filingDate > B` |
| Observation date | 2026-08-29; every input filing, pack fact and peer fact has `filingDate <= as_of` |
| History end | 2025-08-28, the true content end of Moody's public file; the rating path and the persistence reference stop there |
| Labels | the issuer's own rating disclosure in a filing in (B, as_of], hand-read, confirmed by Robert on 2026-08-31 (Experiment 03 D10); frozen in candidates.json |
| Margin | 71 days from the checkpoint release to B; the two labelled actions (Nike, November 2025; Qurate, October 2025) lie later still |

The history end is after the model's release, so the task is history-conditioned: rating
events between 2025-07-21 and 2025-08-28 (Leslie's Caa3 of 2025-08-13 among them) are
supplied as input. They are public information, not labels.

## 4. Cohort and reporting contract

All 20 confirmed candidates, X01 to X20, selected explicitly; Experiment 03's cost-driven
`in_run` exclusions are not inherited. Primary cohort: the 19 without Qurate (X14). Qurate is
executed in full and reported as a diagnostic (decision D8). Saved-input arm: the seven Opus
successes X12, X14, X15, X16, X17, X19, X20. Persistence is the rating in effect at the
history end per the documented selector (entity-level long-term rating where alive, else the
senior unsecured instrument rating); on the 20 it is exact 18 times, MAE 0.15; on the 19,
exact 18 times, MAE 1/19. `changed` equals `label != persistence` for every candidate.

## 5. Inputs

**Current arm, 20 issuers.** Documents by the Experiment 03 rule: the latest 10-K filed after
B and every later 10-Q filed on or before the observation date, from the local cache only,
HTML to text, rating self-disclosures removed by `system/redact.py` with the removed lines
stored outside the bodies. Trim (decision D9): the oldest 10-Q is dropped only where the
finalized package exceeds the context allowance; that is Levi Strauss (10-Q of 2026-04-07
dropped) and Qurate (10-Q of 2026-05-15 dropped). 49 of 51 cached documents are used.

The history pack is rebuilt by `evaluation/pipeline/history_pack.py` as repaired on
2026-09-12: the rating path comes from the raw 17g-7 records (entity-level long-term and
senior unsecured instrument events, typed, withdrawals kept and labelled, collapsed only
where consecutive symbols repeat), not from the June 2025 observation grid that omitted
later events; the terminal state is printed with its level and action date and asserted
equal to the frozen persistence for all 20. Fiscal-year and quarterly rows carry per-fact
filing dates; every fact satisfies end <= filed <= as_of; derived rows inherit their
components' dates; anchors stop at the history end. Peer policy (Robert, 2026-09-12): peers
whose latest fiscal year ended before 2024-08-29, 24 calendar months before the observation
date, are excluded and logged (10 excluded, 56 remain). XBRL source forms are 10-K, 10-K/A,
10-Q, 10-Q/A, 20-F and 40-F; primary documents are 10-K and 10-Q only; no 8-K anywhere.

**Saved-input arm, 7 issuers.** The exact user text Opus received (documents, history pack,
as-of line and task) from the saved Experiment 03 requests, the batch that produced the
scored success, verified: the system prompt, task and schema equal the frozen prompt files;
the rerun bodies equal the first-batch bodies; the documents replay byte-identically from the
cache and the redactor; the history pack is reproduced byte-identically by the vendored
2026-09-10 builders (`legacy_builders/`) from the raw companyfacts cache, which yields the
source record (period end, filing date, tag, form, value) for every figure shown: 43 to 60
annual records, 0 to 45 quarterly records and 843 to 847 peer records per issuer, all with
end <= filed <= as_of (`legacy_provenance.py`, audit/legacy/). Qurate keeps its three
original documents untrimmed. The saved packs' rating paths came from the observation grid;
for these seven no raw event after 2025-06-30 exists, so they are complete.

**Assembly.** User message = documents + newline + history pack + blank line + "As-of date:
2026-08-29." + blank line + task, in both arms. System message = the frozen system prompt.
The output schema travels in `response_format`, not in the prompt.

**Probes.** The Experiment 03 probe prompt and schema, one request per issuer with its EDGAR
name; completed and reviewed (probe_review.json, with a review timestamp after the response)
before the issuer's first document request in either arm; never part of any document body.

## 6. Request bodies

Exactly these fields, checked against an allowlist at every submission: `model`, `messages`
(system, user), `temperature` 0, `seed` 20260912, `max_tokens` (8,192 documents, 1,200
probes), `response_format` (`json_schema`, `strict: true`, the frozen schema), `provider` (as
in section 2), `transforms: []`, `stream: false`. No `tools`, no `plugins`, no web suffix.
Bodies contain model input only: no labels, evidence snippets, changed flags, probe answers,
removed lines or audit data. Replicates send byte-identical bodies.

## 7. Token accounting

Rendered input tokens are counted on the full chat template with the pinned tokenizer.
Context allowance: rendered + 2 x schema tokens + 512 + max_tokens <= 262,144 for every
body. Reservation bound = rendered + 2 x schema tokens + 512. Policy for the reported
`prompt_tokens`: it must lie between rendered minus 256 and the reservation bound; below is
suspected truncation, above is an unexplained count; either records the attempt as suspect,
keeps its charge and halts the run. Observed in the pilot: 165 reported against 161 rendered
for the probe, and 242,155 reported against 242,155 rendered for the largest document, so
the provider renders the template as the local tokenizer does and injects nothing.

## 8. Guards as implemented (`run_openrouter.py`, tested by `test_runner.py`)

1. **Authorization (G1).** `authorization.json` binds the cap, model, endpoint, ceilings,
   replicates, retry allowance, cohort, pilot and the manifest's SHA-256. No request leaves
   without it; a manifest that does not match is refused.
2. **Frozen bytes (G3).** Every body file, the code and prompt files, the primary documents
   and the hashes file are re-hashed at every submission against the manifest; submission
   loads bodies from disk and never rebuilds, tokenizes or downloads.
3. **Ledger (G7, G8).** One append-only, fsynced `ledger.jsonl` at the path named in the
   authorization, independent of the run directory. Before dispatch an attempt reserves its
   worst case (exact decimal at the ceilings); dispatch is refused unless committed charges
   plus unresolved reservations plus open reservations plus the new reservation stay within
   the cap. After a response the charge is the larger of `usage.cost` and the generation
   record's `total_cost`; the reservation is released only then. An explicit provider error
   releases the reservation without a charge. A transport failure, an unreadable outcome or a
   missing charge leaves the reservation charged as unresolved and halts the run. A file lock
   refuses a second process; a halt refuses every dispatch until cleared with a note.
4. **Live prices (G7).** The endpoint listing is read before any dispatch in a process:
   prices at or below the ceilings, fp8, context and completion limits sufficient, else refuse.
5. **Attempts (G2).** At most two attempts per request and at most ten attempts beyond the
   101 planned; an unresolved attempt is never retried without an explicit flag.
6. **Provenance and validation (G9).** Raw response bytes are saved before parsing. Model and
   provider must equal the authorized ones. `finish_reason` must be `stop`. Content is parsed
   strictly (duplicate keys, NaN and Infinity rejected), validated against the schema, figures
   checked finite and non-boolean; the scorecard and direct channels fail independently, and a
   valid direct rating survives an undefined scorecard ratio.
7. **Sequencing (G10, G12).** Documents wait for the issuer's reviewed probe; nothing but the
   pilot pair runs before the pilot verdict file says pass.

## 9. Cost

| Item | Value |
|---|---|
| Sum of the 101 reservations (worst case at the ceilings) | $1.557689 |
| Retry allowance, 10 x the largest document reservation $0.026487 | $0.264870 |
| Conservative plan total | $1.822559 |
| Cap (decision D5) | $3.00 |
| Actual spend (2026-09-13) | $1.242279 committed for 104 responses, $0.141521 held for seven transport failures, $1.383800 against the cap; details in results.md |

## 10. Execution order

The pilot: the largest document request by rendered tokens, `doc-saved-X14-r1` at 242,155,
after its probe; both inspected against the review's acceptance conditions
(pilot_review.json). Then the remaining 19 probes, reviewed; then the documents issuer by
issuer, X01 to X20, current replicates 1 to 3 and, for the seven, saved replicates 1 to 3.

## 11. Scoring and reporting

Flat records per arm and replicate (`pred_scorecard`, `pred_direct`, `label`, `persistence`,
`changed`), scored by `evaluation/pipeline/score_run.py`'s `score_channel`, channel by
channel, on the valid subset, with the planned and valid counts, exact hits over the planned
denominator, and persistence on the full cohort and on the same subset. Consensus per
channel: the median notch of three valid ratings; fewer than three is reported as
incomplete, never rounded into an answer. Spread: highest minus lowest notch per channel,
the range of every extracted figure, and whether the qualitative grades agree. Cohorts: all
20 and the 19 primary; for the saved arm, the seven and the six without Qurate, next to Opus
4.6's corrected saved outputs converted to the same flat records (the conversion reproduces
3/7, 6/7, MAE 1.143 for the scorecard and 4/7, 6/7, 0.571 for the judgement). Failed and
suspect attempts stay visible with their charges. Bootstrap fractions are descriptive.

Validity conditions, as revised by the review: probes completed and reviewed first with
flags rather than exclusions; a 20 by 3 attempt grid with per-channel coverage and no bought
replacements; the token policy of section 7; provenance stored per response; complete hashes
and date checks; one corrected scoring path. Reading rules: lead with exact accuracy on the
full eligible cohort next to persistence and coverage; treat the seven-issuer comparison as
selected Opus successes on matched saved information with different inference settings
(Opus: adaptive high-effort thinking; Qwen: non-thinking, fp8, temperature 0); report both
channels, each replicate and the consensus; no automatic escalation to more paid work.

## 12. Corrections and incidents

Before review (2026-09-12): the GMICloud price was a 75% promotion (the run uses DeepInfra
instead); the seven-issuer subtotal and a heading were wrong; the scoring-parity claim was
false and is now implemented; the truncation tolerance was replaced by the rendered-count
policy; the token evidence became regenerable; the history packs were found not to be the
packs Opus saw, which became decision D12. From the review's final pass: the history path
now comes from the raw records (Leslie's August 2025 downgrade had been omitted), the peer
policy is frozen, probes are staged, the ledger is authorization-wide, and the scorer keeps
denominators. During execution (2026-09-13): 111 dispatches for 101 planned requests; seven transport
failures (the same TLS "bad record MAC" error within a tenth of a second of dispatch, before
any HTTP response; from the second one on, every request ran in its own process, which did
not remove the fault), four output-length failures (repetition loops inside a rationale
string, charged and recorded, no ceiling enlarged), and Walmart's first probe answer, which
stopped inside a JSON string with `finish_reason` stop. The ten extra attempts were all
used, one per request; nine retries succeeded. Two saved-input replicates (Qurate 3,
Victoria's Secret 3) have no valid response and are reported as failures; all 60
current-input requests are valid. Every reviewer decision is a `note` event in the ledger.
