# Codex review of Experiment 04, Arm 1

*Written by Codex, directed by Robert Vetter, 2026-09-12. Reviewed repository HEAD
dd6fe558e94c6a9c19b48eac5d78e20dc1d83a28 against Robert's attached request, Claude's
external review brief, RUN-SPEC.md, the experiment pages, protected candidate records,
cached SEC documents, saved Experiment 03 requests and outputs, current source code,
and free reads of Hugging Face and OpenRouter documentation and listings on this date.
All model-result calculations were offline. No model calls, installations, commits,
pushes or messages were made. This is a review, not spending authorization or a change
to Robert's decisions. Proposed repairs below have not been implemented.*

*Final adversarial pass added by Codex, directed by Robert Vetter, 2026-09-12, after
Robert requested the final review. Rechecked the unchanged source, all candidate selectors,
rating paths, source forms, cached companyfacts extraction, numerical validation and the
proposed execution lifecycle. Additional findings and the finite go/no-go gate appear
at the end of this note; they form part of the ten required changes, not a separate run.*

## Overall verdict

**Not approved as specified.** I would reconsider after the required changes below,
Robert's decisions, and review of the actual runner and complete free pre-flight.
The release-date argument is defensible with qualifications. The cost guarantee,
truncation test, failure accounting and input-comparison claims are not sound as written.
The labels support a disclosure-label pilot, not verified outstanding-rating accuracy
at August 29, 2026.

I agree with two-stage sign-off: specification first, then implementation and free
pre-flight before Robert authorizes an inspected request. The first paid document request
also needs its completed and reviewed memory probe, so this is at least two paid requests,
both included in the cap. No request is authorized by this review. A later inspected
response can test compatibility, not prove that the provider always enforces the schema
or always serves the claimed weights.

**Final-review status:** the design review is complete within the stated Arm 1 scope.
The operational decision is NO-GO today because the fixes are not implemented and
`run_openrouter.py` does not exist. After implementation, all applicable final acceptance
gates must pass against the exact artifacts to be sent; a claim that the ten items are
fixed is not enough. Passing those gates and obtaining Robert's cap and authorization
permits the inspected pilot, followed by the explicitly authorized remainder only after
the pilot gate passes. This is a bounded verification step, not a request for another
open-ended design review. No review can promise that an unimplemented runner is safe.

## Verification completed

The saved-run audit passes all 52 mechanical check groups over 18 document attempts.
All 10 integrity regressions pass, including rejection of paid commands before client
creation. Token evidence regenerates byte-identically. I rebuilt all 20 current packs
and checked 17,952 logged source-date entries, including repeated peer entries, against
`end <= filed <= as_of`. This is a count of checks, not independent facts. Every stored
persistence value matches the current rating selector; that does not establish entity
or instrument comparability.

I independently reconstructed the 16 saved-pack packages. All 16 packs differ from
today's builder. Saved packs contain 3,828 to 4,472 Qwen tokens. Their largest complete
package is Qurate at 243,144 tokens. The seven saved-pack packages total 1,088,487 tokens
per pass. Target's FY2023 debt is 19,147m in the old pack and 19,018m now; Bath & Body
Works' formerly missing EBITDA now also creates an implied qualitative anchor. These
are substantive changes, not merely added date annotations.

An in-memory conversion of the corrected saved outputs through `score_run.score_channel`
reproduces scorecard 3/7 exact, 6/7 within one and MAE 1.143; judgement 4/7, 6/7 and
0.571; persistence 5/7, 6/7 and 0.429. Rounding explains the final decimal. This verifies
the proposed conversion principle, not a converter that has already been implemented.

The regenerated evidence contains **51 cached documents and 49 selected documents after
trimming**, with 3,285,163 local input tokens per main pass. The smallest document has
18,832 tokens; the smallest document share in an original package is 14.15%. The
counting script concatenates the schema as text and omits the chat template from its
totals, exactly as its evidence metadata says. It does not count a fully rendered
provider request.

## Brief section 10: verdict on every item

| Item | Verdict | Reason and evidence |
|---|---|---|
| 1. Out-of-sample claim | Pass with a required change | July 21 is supported as a weight-release bound, not a vendor-stated training cutoff; record the revision and hosted-serving uncertainty, and distinguish release, history, document and observation boundaries as below. |
| 2. Input parity and D12 | Fail | Current packs differ for every saved issuer; current Qurate also loses a document; only a separately frozen saved-input comparison can preserve the material Opus input. |
| 3. Request shape and leakage | Pass with a required change | The schema has required keys and closed nested objects, and endpoint listings advertise support; actual enforcement is untested, while semantic leakage and undeclared account/preset behavior cannot be ruled out from a proposed JSON body. |
| 4. Cost guard | Fail | A price fetched once and an after-response 25% stop cannot prevent the first over-cap charge after a price increase; unknown billed timeouts and whole-run retry limits are unspecified. |
| 5. Truncation | Fail | A 2% tolerance can hide thousands of missing document tokens and falsely reject every short probe because of ordinary template overhead; schema serialization is not known. |
| 6. Labels | Fail | Disclosure dates do not establish outstanding ratings at as-of, and entity/rating types are mixed; Qurate is a concrete unresolved mismatch, not a hypothetical concern. |
| 7. Scoring and criteria | Fail | Conversion is sound, but the scorer silently excludes missing predictions and can exclude a valid direct prediction when no scorecard field exists; V/R rules need the changes below. |
| 8. Determinism | Pass with a required change | Three fixed-seed requests are a reasonable small repeatability diagnostic, not evidence of determinism; report numerical and qualitative variation as well as rating spread and define handling before observing results. |
| 9. Write-up | Fail | Several statements about completeness, probe order, costs, prior results and model comparability contradict the saved evidence; corrections are listed below. |
| 10. Additional findings | Fail | Leslie's path is incomplete, the original methodology rubric is absent, model inputs cannot represent missing numbers, and the early-window DeepSeek claim contradicts the project's own cutoff evidence. |

### Release bound and hosted identity

The Hugging Face upload commit is
`d4dc8b0260055bf2289e8a5c505a229feb9db486`, July 21, 2025 at 08:01:20 UTC.
It is distinct from the earlier empty initial commit. I compared all 118 safetensors
shard object identifiers at that upload with current main
`ac9c66cc9b46af7306746a9250f23d47083d689e`; all match. The sorted weight-map SHA-256 is
`9bc148b4381e99b33a0f27c247a697cb63de36819317ce25d5d8eebd10ba5477`.
Subsequent changes include documentation, license, a 1M configuration and tokenizer
configuration. This is repository-metadata verification, not a download and hash of
the model tensors. See the [vendor commit history](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507/commits/main)
and [upload tree](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507/tree/d4dc8b0260055bf2289e8a5c505a229feb9db486).

The model card has no stated training cutoff and describes this as a non-thinking
model. The defensible wording is: **July 21, 2025 public checkpoint release, used as an
upper bound on training information for those weights**. The hosted fp8 model may be a
derived deployment; an OpenRouter model string is not a cryptographic revision pin or
proof about later fine-tuning or calibration. Save the vendor evidence under `evidence/`,
pin tokenizer revision and endpoint, and record this residual dependency on the host's
identity claim. See the [vendor model card](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507).

The September 30 document boundary is 71 days after release. October and November
actions are later still, so the chronology is adequate for retrospective reconstruction
conditional on model identity and valid labels. An extra month is a research convention,
not a mathematical contamination guarantee. Published financial information after the
model release is deliberately supplied at inference time.

The history endpoint August 28 is also after Qwen's release. That is legitimate supplied
information, but it makes the task history-conditioned. In particular, Leslie's Caa3
action is dated August 13, after Qwen's release, and its Caa3 persistence value is supplied
directly. Thus the brief's claim that all 18 unchanged labels predate both models' bounds
is false. Keep unchanged issuers in the cross-section; do not reclassify them as evidence
of unseen new-rating inference merely because their disclosure is newer.

### Input contents, provenance and leakage

D12(c) best separates the two questions: a current-pack main pilot and a saved-input
comparison on the seven Opus successes. The latter needs the original system/task text,
document text and order, pack, as-of line and semantic schema, verified against saved
requests. Qurate retains all three original documents in that comparison. The current
main arm can apply the fixed trim rule to its two oversized packages. Levi was never
submitted to Opus, so it cannot have seen fewer documents than Opus did.

Even this is a comparison of model configurations: Opus used adaptive high-effort
thinking and API defaults, whereas Qwen is non-thinking, fp8, temperature zero, with a
different host and output interface. Report those differences rather than saying only
the model changed literally. Three-request consensus versus one selected Opus success
also has a different inference budget; show individual Qwen replicates alongside consensus.

The current pack's added filing dates and improved figures do not themselves expose
future facts: the date assertions passed. They do change available information and
anchors. Original saved packs lack full per-fact provenance, so the legacy comparison
must recover source-date evidence in a sidecar before submission under AGENTS.md, or
remain blocked; do not substitute today's changed values and still call it identical.
Neither the new log nor a later source snapshot retrospectively certifies the old input.

**New concrete history defect:** `history_pack.build` uses the latest observation's
`rating_path` when there is no observation at the requested as-of date; these observation
files end June 30, 2025. Leslie's printed path ends at the March 18 Caa1 action, omitting
the August 13 Caa3 action, yet its separately calculated last rating is Caa3. The text
calls this history complete through August 28. Build the current arm's dated path from
the raw eligible rating records, keep any last-N limit explicit, and verify the terminal
state against the selected target. Preserve the old pack in a legacy control, with its
limitations recorded. No observations or human mappings need regeneration.

The redactor is heuristic. A scan of all 51 cached, redacted documents found no matches
for the tested multi-character Moody's symbols; it did retain PVH's generic investment
rating downgrade warning and Qurate's stock-market downgrade language. This is neither
a complete symbol search nor a semantic leakage certificate. Review financing grids,
rating-conditioned coupons and remaining agency-adjacent passages on the exact chosen
inputs; retain audit-only removed lines outside the model payload. Public bankruptcy
events are admissible information at as-of and cannot be called advance forecasts.

No tools, plugins or web suffix is the appropriate baseline request shape. Use an
allowlist for permitted body fields, with candidate labels, evidence snippets, changed
flags, probe answers and audit data excluded. OpenRouter documents web search as an
explicit feature and context compression as a configurable transformation; neither
should be activated for this run. Record relevant preset/account settings rather than
assuming that omission proves their state. See [web search](https://openrouter.ai/docs/guides/features/plugins/web-search)
and [message transforms](https://openrouter.ai/docs/guides/features/message-transforms).

### Provider, schema and costs

The live [endpoint listing](https://openrouter.ai/api/v1/models/qwen/qwen3-235b-a22b-2507/endpoints)
confirms GMICloud `gmicloud/fp8` and DeepInfra `deepinfra/fp8`, 262,144 context tokens,
the listed prices, and support for temperature, seed and structured outputs. Their
completion limits are 235,929 and 16,384 respectively. This supports selecting an
endpoint, not a claim that this exact schema has been exercised there.

`require_parameters` is a support-based routing filter. The proposed single-provider
order with fallbacks disabled is consistent with the documentation; it is not a bug.
Prefer the full endpoint slug to avoid matching future variants. Add `max_price` with
approved per-million prompt/completion ceilings; the documentation says requests will
not run if an eligible price is unavailable. Quantization is an endpoint property, not
necessarily a field in every completion response. Store the endpoint snapshot and
response provenance separately. See [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).

The document schema is structurally suitable: all four object schemas close additional
properties and require all declared properties. That does not guarantee finite,
economically meaningful inputs or correct period selection. Validate JSON, schema,
finite values and scorecard arithmetic locally; retain a valid direct rating if the
scorecard cannot be computed. Missing numerical inputs cannot be honestly represented
in the frozen schema: disclose this limitation and count unresolved outputs, without
quietly coercing them to zero. The later inspected response must test actual compatibility.
See [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).

Recomputed costs below use the existing local counts, full completion allowances and
the specification's approximate 8,000 probe-input tokens; they exclude retries and
unmeasured provider overhead, so they are projections rather than an exact pre-flight.

| Work | GMI promotion | GMI list | DeepInfra |
|---|---:|---:|---:|
| 20 document requests | $0.3448 | $1.3792 | $0.3858 |
| 60 document requests | $1.0344 | $4.1375 | $1.1573 |
| 20 probes, approximate input | $0.0091 | $0.0364 | $0.0139 |
| 21 additional saved-pack requests | $0.3459 | $1.3838 | $0.3885 |
| D12(c), all 101 initial requests | $1.3894 | $5.5577 | $1.5598 |

A simple counterexample defeats the proposed cap: with $2.97 already spent, a request
projected at $0.02 passes a $3 check; a fourfold price increase makes it $0.08 and total
spend $3.05 before the stop executes. Refreshing prices alone still leaves a race.
Reserve a conservative cost before dispatch, enforce a routing price ceiling, and keep
unreconciled reservations charged against the cap. A timeout can already have been
billed; absence of `usage.cost` is not evidence of zero spend. Make ledger writes
durable, prevent duplicate processes, reconcile by generation ID where available,
and stop on unknown billing or provenance rather than blindly retrying. Actual usage
and cost are documented response fields, but an interrupted response need not reach
the client. See [usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting).

**Budget recommendation, not authorization:** retain $3, with no full rerun entitlement.
At DeepInfra's stated rates, 81 document calls reserved at 253,952 input plus 8,192 output
tokens each, 20 probes capped at 2,000 input plus 1,200 output each, and at most ten
additional attempts reserved at the document maximum total **$2.506677**. At GMI's
promotional ceilings the corresponding bound is **$2.294908**. These deliberately
conservative bounds include room for ordinary overhead within those input limits.
They assume no additional per-request fees, exact routing price limits and enforcement
of those input ceilings. The implementation must verify these assumptions and stop
if they do not hold. Ten extra attempts is a recommendation for a pooled retry allowance,
not permission granted now, and it cannot guarantee 100% completion. GMI at list price
cannot complete the proposed three-replicate arm under $3.

### Token accounting and truncation

The exact regenerated content count is useful for sizing, but the provider can render
the schema and chat template differently. Measure messages, template and schema-related
allowance separately for every body and pin the tokenizer revision. Account for any
allowed re-ask body too. Check context headroom including completion reservation.

The current probe texts total 2,994 tokens across 20 issuers, ranging from 146 to 153
per issuer before chat rendering; the probe schema is 185 tokens as JSON text. A sample
probe changes from 147 concatenated text tokens to 161 rendered chat tokens. Even
without injected schema that exceeds 2%, so V3 cannot apply as written to every request.
The proposed 8,000 probe tokens is an estimate, not an exact count.

For document packages a 2% deficit is roughly 1,800 to 4,700 tokens. It can remove
material evidence while passing. Schema overhead can also offset a deficit. Conversely,
a mismatch can arise from tokenization or template differences without any truncation.
Use request-class-specific expected counts with a justified absolute overhead allowance,
disable compression, and investigate discrepancies. Keep affected attempts visible and
withhold their validity designation; never claim that near-equal counts prove complete
semantic delivery. The one inspected request cannot calibrate every provider/schema
combination, so unexplained discrepancies later must halt that configuration.

### Labels and sample interpretation

The frozen candidate file supports persistence **18/20 exact, MAE 0.15**, with errors
of one notch on Nike and two on Qurate. Without Qurate it is **18/19 exact, MAE 1/19**.
The changed flag means disagreement with this August 28 archive reference. It does not
mean an issuer had no intervening action or that an outstanding rating was certified.

The available evidence specifies different targets: Dick's senior notes, Dollar General's
senior unsecured debt, Nike's long-term debt, Bath & Body Works' corporate rating, and
Victoria's Secret's corporate rating alongside distinct secured and unsecured ratings.
A generic overall issuer prompt is not an exact contract for all of these. Define the
legal entity, rating type and instrument/seniority where applicable for label and prior;
do not choose a rating type using the unknown test label after seeing a prediction.
Unresolved alignments need visible status even in a disclosure-label pilot.

Record the rating statement's effective/reference date separately from the filing
date. Levi's January 28 filing describes its November 30 rating; several other labels
refer to fiscal quarter-end dates. A filing-date age understates the age of that rating
assertion. Later silence cannot establish that a rating remained outstanding.

Qurate's November 5, 2025 disclosure is 297 days before the observation date and names
LI LLC's CFR, while the input is consolidated QVC Group with April 2026 bankruptcy
information. Keep the frozen label untouched. My D8 recommendation is to show its legacy
score only in a clearly marked diagnostic/sensitivity panel until alignment and as-of
validity are resolved. A 19-case table is still a disclosure-label pilot, not certified
ground truth. Leslie's August 13 action is before B, so its unchanged flag is correct
under the stated reference; the prose quarter ending October 4 does not date the action
after B.

## RUN-SPEC section 10: verdict on every item

| Item | Verdict | Reason and evidence |
|---|---|---|
| 1. Response-format translation | Pass with a required change | The schema structure passes inspection; require local validation and later observed endpoint compatibility, without treating advertised support as an executed test. |
| 2. Truncation check | Fail | Probe template overhead alone violates 2%; document tolerance can conceal partial loss; replace V3 as described above. |
| 3. Trim | Pass with a required change | The fixed oldest-10-Q rule fits both current packages, but keep untrimmed Qurate for the saved-input comparison and label the 49 selected versus 51 cached documents. |
| 4. Determinism | Pass with a required change | Three replicates can describe observed variation only; preserve per-field outputs, period choices, all factor grades and per-channel spreads. |
| 5. Bound | Pass with a required change | The July upload and unchanged weight identifiers support a release upper bound; freeze evidence and acknowledge hosted revision uncertainty. |
| 6. Leakage/input parity | Fail | Main-arm packs are changed, Leslie's path is incomplete, and saved-pack provenance remains incomplete; no tools is useful but cannot certify all leakage channels. |
| 7. Cost ledger | Fail | The proposed after-response rule permits an overrun; reservations, price ceilings, unknown-charge handling and finite attempts must precede spending. |
| 8. Scoring parity | Pass with a required change | Corrected outputs reproduce through the shared function; implement coverage-aware conversion and channel-specific failure handling before using its reports. |

## Proposed validity conditions V1 to V6

| Rule | Verdict | Required interpretation/change |
|---|---|---|
| V1 | Pass with a required change | Complete and review each probe before its issuer's first document request, keep it outside document context, and timestamp the review; flag substantiated recall of any information published after the model bound, including Leslie's August action and financial facts, without equating a correct guess with proven contamination or a negative probe with cleanliness. |
| V2 | Fail | 20/20 in all three replicates defines completion, not validity; retain a 20-by-3 attempt grid and any extra arm, show coverage per channel, and report incomplete runs without silently buying replacement successes. |
| V3 | Fail | Replace the universal 2% rule with the counting and discrepancy policy above; retain failed attempts and distinguish suspected truncation from confirmed truncation. |
| V4 | Pass with a required change | Store returned model/provider IDs, generation ID, finish reason and endpoint metadata; quantization and upstream revision may be snapshot claims, not returned proof; a `length` finish is a failed attempt even if JSON happens to parse. |
| V5 | Fail | Replace the spending guard, add complete source and request hashes and target/action-date checks, and explicitly allow old source-date gaps only as unresolved evidence rather than claiming all dates passed. |
| V6 | Pass with a required change | Use one corrected arithmetic/scoring path, preserve original outcomes alongside corrections, and add the failure and denominator controls below. |

Probe review should flag rather than automatically remove issuers from the main report.
A separate flagged/unflagged sensitivity avoids making low recall the definition of the
cross-section. Do not let probe performance select prompt variants or preferred outputs.

`score_run.py` currently skips a row inside `score_channel` if its prediction is absent
or invalid. Its CLI additionally filters both channels on the existence of
`pred_scorecard`. A two-row fixture with one exact answer and one null answer returns
`n=1, exact_rate=1.0`. This is a completed-case metric, not 100% coverage or 2/2 accuracy.
Keep the planned denominator, valid-response denominator, failure reason and persistence
on both the full eligible cohort and each paired scored subset. Report exact successes
over the intended denominator alongside conditional accuracy; do not invent notch errors
for missing ratings. Assert unique issuer/variant/replicate IDs and consistency of
`changed == (label != persistence)` after the target has been fixed.

Median notch across three valid ratings is a sensible descriptive consensus per channel.
Do not median the numerical inputs and describe the result as the same procedure; scorecard
nonlinearity makes that a different system. If fewer than three valid ratings remain,
mark consensus incomplete, rather than rounding a two-rating median into a new answer.
A spread above one notch should flag instability, not trigger cherry-picking, exclusion
or extra paid retries. Report the numerical min/max and period choice for all ten inputs,
qualitative grade changes, and derived scorecard spread. Three identical responses do
not prove deterministic service or correctness. Bootstrap issuer-level paired errors;
60 responses are still 20 issuers, not 60 independent cross-sectional observations.

## Proposed reading rules R1 to R5

| Rule | Verdict | Required interpretation/change |
|---|---|---|
| R1 | Pass with a required change | The baseline and fewer-than-three total error condition for beating its MAE are correct; lower sample error is mathematically possible, but a general superiority claim is unsupported by this small, selected, uncertain-label sample. |
| R2 | Pass with a required change | Retain those diagnostics, but lead with exact outstanding/disclosure-label accuracy on the full eligible cross-section, as Ding requested, alongside persistence and coverage; label the seven-issuer comparison as selected Opus successes. |
| R3 | Pass | XBRL agreement is consistency because reference values are already supplied; it is not independent extraction accuracy. |
| R4 | Pass with a required change | Say post-release disclosure-label pilot, give provider, input variant, numerator/denominator, coverage and unresolved labels, and distinguish each replicate from consensus; report the primary scorecard channel as well as judgement. |
| R5 | Fail | Being within one notch of Opus's MAE permits roughly 1.57 versus Opus 0.57 and persistence 0.43 on the seven cases; that is too weak to justify escalation and no empirical threshold authorizes a second model or Arm 2. |

The proposed next-step rule can be replaced with a discussion trigger: review repeatability,
coverage, false alarms, both channels' errors and source/target failures, then let Robert
decide whether further spending answers a specific unresolved question. Keep the one-notch
and 15/20 thresholds only if he wants descriptive diagnostics, not evidence of equivalence
or a validated model-selection policy. The full 20 are already a development-exposed pilot;
neither preserving labels nor repeating on a new model creates a never-seen holdout.

## Required changes before the first paid request

1. Fix the target and reporting contract as a disclosure-label pilot with unresolved entity, rating-type and as-of evidence flagged, or obtain verified outstanding labels before making the stronger claim, and decide Qurate's treatment explicitly.
2. Save dated checkpoint-release evidence and pin tokenizer and endpoint identities while stating the remaining uncertainty about the hosted weight revision.
3. Resolve D12, freeze the complete cohort and peer freshness policy, hash every input variant, recover required saved-pack source dates, and correct the current history paths before recounting the exact requests.
4. Implement and locally test an allowlisted request builder and strict output validator with no tools, retrieval, compression or label-bearing audit fields entering the model context.
5. Replace the proposed ledger with one durable authorization-wide spending record, pre-dispatch reservations, enforced provider price ceilings, unresolved-charge handling and a finite total retry allowance that survives crashes, resumes and new output directories under Robert's approved cap.
6. Replace the universal 2% truncation rule with rendered per-request counts, explicit schema/template allowances, context checks and a documented stop-and-investigate policy for discrepancies.
7. Implement and test shared corrected scoring with independent channel coverage, visible failures, fixed denominators, paired persistence and an explicit three-valid-replicate consensus rule.
8. Record revised V1 to V6 and R1 to R5 before execution, including probe staging, contamination flags, instability handling and no automatic escalation to more paid work.
9. Correct the run specification and decision summaries and identify the frozen prompt's missing-rubric and missing-value limitations, with the separate lab-draft corrections required before sending rather than before execution.
10. Obtain Robert's Arm 1 decisions D5 to D9 and D12, leave D10 deferred unless separately authorized, and complete second-stage verification of the runner plus every free pre-flight body, count and cost bound before authorizing the probe and inspected document request.

## Recommendations that may wait

The full rubric, source-citation schema, explicit missing values, quantitative adjustments
and TTM calculations belong in a separately versioned analyst variant after this pilot's
limitations are accepted. Do not quietly change the frozen prompts to improve known cases.
The evidence ledger and target contract are useful free work now; forecasting and broader
model comparisons need their own experiment design.

More replicates, seed sweeps, another provider and another model can wait. Three repetitions
are sufficient for a small initial repeatability description. An independent, later
holdout and verified as-of labels would improve scientific evidence more than treating
repeat attempts on these 20 as a larger cross-section.

## Open decisions: recommendations only, Robert decides

| Decision | Recommendation |
|---|---|
| D5 Cap | Keep the proposed $3 hard ceiling, inclusive of probes, saved-input control, pilot, failures and a bounded retry allowance; do not treat the account balance as authorization or promise completion at GMI list price. |
| D6 Provider | Prefer DeepInfra fp8 with price ceilings $0.09 input/$0.55 output per million and no automatic fallback, given the small projected premium and GMI's promotional dependency; GMI is acceptable with its promotional ceilings enforced and stopping if unavailable. |
| D7 Replicates | Keep three at temperature zero and seed 20260912, with one provider/configuration fixed throughout a comparison and per-field as well as rating spread reported. |
| D8 Qurate | Keep the protected candidate untouched but quarantine its score from the primary interpretation until target/as-of validity is established, while retaining the legacy 20-case and seven-case sensitivity panels. |
| D9 Trim | Accept oldest-10-Q removal for oversized current packages before outcomes are seen, flag the two omissions, and keep saved-pack Qurate untrimmed in its legacy comparison. |
| D10 Second model | Defer; first inspect this protocol's validity and error evidence, and require a separate cap and model-bound review before any second-model call. |
| D12 Packs | Prefer (c), current packs for the main pilot plus three saved-input replicates on the seven Opus successes, conditional on recovered source-date evidence and the cap; if the legacy control cannot meet those conditions, defer it and report the main arm as a changed-input system evaluation. |

## Answers to the three questions

**1. Will this produce the valid post-cutoff measurement Ding asked for?** Not as written.
It can produce a clearly specified post-release, history-conditioned comparison against
20 accepted company disclosures, with the Qurate caveat and other target limitations.
It cannot establish that these were the 20 outstanding ratings on August 29, 2026.
Ding's full request needs that label validity, a clearly described model data bound and
accuracy on unchanged as well as changed issuers. The release bound is usable if described
honestly; it is not a documented exact training cutoff.

**2. What must change first and what can wait?** The ten required changes above precede
any paid request, including the supposedly small inspection. Full analyst redesign,
extra models, more repetitions and Arm 2 can wait. Verified outstanding labels may also
wait only if Robert explicitly accepts the narrower disclosure-label pilot and its
limited claims. No request to the lab is authorized here.

**3. What may the lab claim afterward?** Once results exist, state the model and provider,
public release bound and source, as-of and history dates, input variant, redaction and
no-retrieval configuration, attempted and valid counts, both channels' exact accuracy,
within-one rate and MAE, persistence on the same cohorts, changed/unchanged diagnostics,
repeatability and label limitations. Describe the seven-issuer comparison as selected
Opus successes with matched saved information only if that control actually runs.
Do not claim certified outstanding labels, absent contamination, solved extraction,
advance prediction of actions, equivalence to Opus or generalized superiority.
Experiment 04 currently has no measured accuracy to report.

## Corrections to the brief, specification and draft

| Claim | Correction supported by the review |
|---|---|
| All 18 unchanged labels were public before both models' bounds | Leslie's Caa3 action is August 13, 2025, after Qwen's release; it is legitimate supplied history, and its memory recall would be informative. |
| History complete through August 28 | Leslie's current path comes from a June 30 observation and omits the August action even though the separately calculated terminal rating includes it. |
| 51 documents used after trimming | 51 are cached; 49 are selected by the proposed main-arm trim. |
| Counts include the 13-token chat template | The executable evidence omits that template and includes schema JSON as ordinary text; it is not the exact hosted rendering. |
| Qwen fits every original package | Current Levi and Qurate exceed the limit; saved-pack Qurate fits untrimmed; Levi never ran on Opus. |
| Only the model changes | Current packs, Qurate's main-arm documents, serving and inference settings differ; D12 is still open. |
| GMI ledger stops at the cap if promotion ends | The stated algorithm can overshoot on the first increased-price request; D12(c) costs about $5.56 at list before retries, not less than $3. |
| Opus produced seven usable observations because of cost alone | Cost restricted scheduling, but 11 initial requests exhausted the output cap and only the two changed cases were rerun; the seven successes are selected. |
| A probe preceded every original document | Probes and document requests shared the original batch; actual processing order is unproved. |
| The probes showed that the model knew neither new rating | They did not demonstrate recall of the two accepted changed-case labels; Nike recalled A1, and a negative probe does not establish absence of knowledge. |
| Each channel caught one change | Correct direction: scorecard 2/2, judgement 1/2; exact changed-case matches: scorecard 1/2, judgement 0/2. |
| Persistence scores best by construction; system value lies entirely in changes | Persistence is exact on unchanged labels by definition, but another model can have lower aggregate error; false alarms and outstanding-level accuracy remain central to Ding's question. |
| Qwen is the most recent eligible open-weight model | The repository itself lists September models; some fail the extra buffer or context preference, but eligibility alone does not establish this superlative, so describe Qwen as the selected affordable candidate. |
| DeepSeek V3-0324 can use the September 2024 boundary with 59 issuers and 12 changes | The repository uses its March 24, 2025 release as its bound and lists an April 30, 2025 boundary instead; D11 and the brief's early-bound claim are inconsistent with that evidence. |
| A few hundred recent issuers follow just by obtaining newer labels | This pipeline's current disclosure search frame is 63; hundreds require additional eligible issuers or sectors and a separate scope decision. |
| Appendix B includes the supplied email history | It contains a placeholder; this review used the actual email history Robert supplied in the task, plus the recorded research requirements. |

The draft's corrected seven-case accuracy table is supported. Its cost explanation should
retain the budget constraint while also disclosing output failures and selective reruns.
Its headline should say pilot accuracy against accepted disclosures and link the detailed
limitations. Robert's preference to avoid a standalone Qurate sentence does not make a
claim of fully verified labels accurate; a short general qualification in the email and
the explicit Qurate detail in the attached results can accommodate that preference.

The proposed architecture attachment also overstates two earlier findings: it still says
the scorecard put a bankrupt issuer four notches too high, although the correction leaves
one notch against an unresolved label, and says annual numbers cannot time changes where
the evidence only tested particular signals and a selection rule. Correct those claims
before attaching it. Its inclusion of 8-K evidence is a future scope proposal requiring
Robert's decision; Arm 1 still excludes 8-Ks and exhibits from model input.

## Reproducibility and limits of this review

The three authorized offline scripts were rerun, followed by independent saved-pack
reconstruction, source-date assertions, token arithmetic, scorer fixtures and a limited
residual-text scan. The live endpoint prices agree with the saved listing. The downloaded
model card SHA-256 is `af233f6e013228859d81a2088521781d4e6a06c5960ab3b7ceee6466f550b5f6`.
No credit balance read or credential access was needed. The review did not re-harvest
labels, independently certify all source financial values, audit every historical study,
benchmark model quality or test live schema enforcement. Those are not implied by passing
the existing mechanical tests. Protected files and the regenerated token evidence remain
unchanged; only this note and the required HANDOVER change-log entry were added or edited.

## Final adversarial pass: additional evidence and closure conditions

### Findings incorporated into the required changes

**Cohort selection must not inherit Experiment 03's budget exclusions (item 3).** The
protected candidates still set `in_run: false` for X08, X09, X13 and X18. The original
runner filters on this flag. The new manifest must explicitly select the 20 confirmed
Arm 1 IDs, with execution membership separate from Qurate's reporting status, and never
edit the old candidate file to accomplish that. Assert the ID set, not just its size.
For D12(c), the unchanged proposed plan has 60 main document requests, 21 saved-input
requests and 20 probes, before retries. Any approved smaller plan needs its own exact
manifest. Do not submit a smaller plan while continuing to call it the full planned run.

**Rebuild the whole current history policy, not just Leslie's row (item 3).** Comparing
the June-ending observation paths with the raw archive finds omitted post-June events
for X07, X08, X09, X11 and X13. X09 and X11 have July 14 Ba2 instrument events; X07,
X09, X11 and X13 also have instrument withdrawals. These instrument events do not change
the selected entity priors. A repair must not substitute the latest mixed instrument
symbol for the target rating or interpret every instrument withdrawal as an issuer
withdrawal. The current selectors reproduce all 20 frozen priors and report no differing
live entity ratings under their existing rule. That still does not resolve comparison
with the disclosure's legal entity and rating type. Build an explicitly typed path and
recheck every historical anchor against the history ceiling.

**Freeze the peer population and acknowledge source age (item 3).** The current union
contains 67 issuer/peer companies. Peer source entries include 804 from 10-Ks and 22
from 20-Fs, with the latter belonging to JD.com and Vipshop. Issuer pack source entries
checked here comprise 1,022 from 10-Ks and 666 from 10-Qs; none of these selected source
entries is from an 8-K. Keep the primary-document rule distinct from allowed XBRL source
forms, and freeze both. The peer table includes PetSmart FY2014, Staples FY2017 and
Whole Foods FY2017. Those values are old public information, not future leakage, but
they are weak contemporary peers. For the current main arm, recommend a predeclared
maximum fiscal-period age, such as 24 months, with excluded/missing peers logged; Robert
must accept the policy before inputs are frozen. If the original peer rows are retained,
describe the table as mixed-age historical reference information. Preserve the old table
unchanged in any authorized saved-input control.

**The date check and source-value check are distinct (items 3 and 4).** An in-memory
re-extraction from raw companyfacts reproduced all 67 compact financial records examined.
Filtering raw facts to `filed <= 2026-08-29` before extraction produced no differences
from the current available values across these records. Thus no actual future-tag
selection defect was found for this frozen date. A synthetic case did show a general
limitation: an unavailable future preferred tag can suppress a previously available
fallback tag because extraction chooses tags before downstream date filtering. This
is not an Arm 1 blocker for the checked frozen cache; it requires repair before extending
the same pipeline to arbitrary historical dates. Preserve and state the existing
earliest-filing policy for restatements instead of calling it latest-restated accounting.
Re-extraction parity verifies reproducibility, not correctness of each economic definition.

**Validate before invoking the scorecard (items 4 and 7).** `scorecard.derive` accepts
Python booleans as numbers: a synthetic `revenue=True` produced revenue of 0.001bn.
JSON-schema validation rejects that value, so applying the complete schema before
arithmetic closes this path without changing the protected prompt. Reject duplicate
JSON keys, NaN/Infinity, and non-finite derived values; do not silently parse or coerce
them into usable figures. A proper finite input can still yield an undefined ratio,
which must become an explicit channel failure. This machine already has `jsonschema`
4.25.1, `httpx` 0.28.1, `transformers` 4.57.6 and `tokenizers` 0.22.2 on Python 3.13.7;
no installation is needed to validate the schemas. Record the versions actually used
for the future run rather than treating this observation as a permanent lock.

**Close lifecycle and interpretation gaps (items 5, 7 and 8).** The cap belongs to one
authorization, not to a timestamp directory or process. A new directory, restart or
rerun flag must not reset it. Use exact decimal accounting or conservatively rounded
integer units, reject non-finite or negative billing data, reserve before network
dispatch, and release a reservation only after authoritative reconciliation. Persist
the raw response and charge even when parsing or scoring fails. A parse re-ask is an
additional attempt, not a fourth replicate from which to select a preferred rating.
Default to at most one identical-body retry for the specified retryable failure; any
error-message augmentation needs its own frozen template, leakage check and token bound.
Transport-library automatic retries must be disabled or represented by the same ledger.
Do not claim three independent service repetitions if an output-response cache served
the same generated answer; distinguish output-response caching from ordinary prefix
token caching in the audit. Finally, the scorer's bootstrap fraction named
`p_system_beats_persistence` is a descriptive resampling fraction, not a hypothesis-test
p-value or posterior probability of superiority.

### Finite final acceptance gate

Implement these checks as assertions and offline tests, then retain their results with
the frozen request manifest. Tests that should block submission must assert **zero
calls to the dispatch transport**, not merely inspect a warning string. Test the actual
production dispatch path with a fake transport. No paid provider test is needed for
these gates. A failed gate is NO-GO; a passed test on different code or request hashes
does not clear the gate for this run.

| Gate | Evidence required before the pilot | Failure must do this |
|---|---|---|
| G1 Authorization | Recorded Robert-approved scope, cap, provider, D12 variant, replicates, retry allowance and reporting/label contract, bound to a unique authorization ID and manifest hash. | No model request without that authorization, including count-token probes or miniature compatibility calls. |
| G2 Cohort and attempts | Exact expected ID sets, unique issuer/variant/replicate IDs, separate probe IDs, correct main/control counts and explicit Qurate reporting status; fixture using the old `in_run` flags still selects the approved cohort. | Refuse an incomplete, duplicated or silently expanded plan. |
| G3 Frozen bytes and environment | Hashes for source files, primary filings, raw financial caches, derived packs, redaction output, schemas, scorer and every final body; tokenizer revision and dependency versions recorded; submit loads the approved bodies instead of rebuilding them. | Refuse changed or missing inputs after pre-flight; a tokenizer or document cache miss must not download through the submission path. |
| G4 Point in time and target | Every supplied fact has supporting source/value/date evidence, derived facts inherit all component dates, forms obey the two source policies, each typed history/anchor stops at August 28, and date-boundary fixtures pass. | Reject missing dates, after-as-of facts and post-history rating events; leave unresolved legacy provenance blocked rather than waive it. |
| G5 Input isolation | Final bodies have no tools, retrieval, active plugins/compression, label evidence, changed flags, removed-line logs, previous probe answers or prior replicate answers; date/redaction review covers each selected document. | No dispatch of a malformed or contaminated body; freeze a newly repaired input variant before proceeding. |
| G6 Schema and tokens | Both probe and document schemas validate locally; every body and allowed retry fits a conservative rendered-input bound plus output reservation; discrepancies have a request-class-specific policy. | Refuse overflow and unexplained counts, rather than truncate or enlarge the output/context allowance automatically. |
| G7 Price and cap arithmetic | Model current and list prices, a changed live price, missing prices, per-request fees, exact-cap arithmetic and invalid cost values using the real reservation logic and approved routing price ceiling. | Zero dispatch whenever committed spend plus unresolved reservations plus the next conservative reservation exceeds the cap, or eligible prices cannot be bounded. |
| G8 Crash, resume and concurrency | Inject a crash before send, after send but before response, and after response but before reconciliation; restart in a new directory, retry a completed ID, and start a second process. | Preserve all possibly billed reservations; reconcile or stop; never duplicate a completed request or open a fresh cap for the same authorization. |
| G9 Response provenance and persistence | Fake wrong-model/provider responses, absent usage, HTTP errors, truncated outputs, malformed JSON, duplicate keys, booleans, non-finite figures and undefined ratios; raw response and charge saved before score acceptance. | Stop on unknown billing/provenance; classify bounded parse/arithmetic failures without losing their cost or selecting extra favorable responses. |
| G10 Probe sequencing | Fake pending, failed, unreviewed and completed/reviewed probes; require a review timestamp before the matching issuer's first document dispatch and keep probe data out of its body. | Block that issuer's documents until the required review is complete, even on resume or in the saved-input arm. |
| G11 Reporting | Golden fixtures reproduce the corrected seven-case metrics and 18/20 persistence baseline; fixtures include a direct-only valid channel, null predictions, all-failed rows, missing replicates and mismatched changed flags. | Retain intended denominators and failures, score channels independently, withhold incomplete consensus, and never turn no answer into persistence. |
| G12 Budgeted rollout | The entire authorized plan, including allowed failures/retries, fits the approved conservative bound; the probe and inspected document are named entries in that plan; further dispatch pauses after the inspection pair. | No automatic full run merely because the first response is received or parseable. |

If Qurate is excluded from primary interpretation, preserve all execution rows and show
the approved 19-case primary cohort and 20-case legacy sensitivity distinctly; the
seven-case versus six-case Opus comparisons likewise need distinct denominators. A
failed observation cannot disappear when making any of these filters.

### Pilot acceptance and permission to continue

Choose the inspected document by a recorded, outcome-independent rule, preferably the
largest eligible finalized request across the arms that will actually run. Its memory
probe must complete and be reviewed first. Count the inspected document as its planned
replicate; do not buy an extra practice response outside the manifest. Retain both raw
responses, charge reconciliation, provenance, parsed schemas, audit checks and token
accounting. Inspect substantive output for the requested annual period, USD-million
units, invented missing figures and obvious failure to use the provided material.
This tests whether the protocol operates sensibly, not whether the prediction matches
the known label. An inaccurate but valid answer is evidence and must not trigger tuning.

Proceed to the authorized remainder only if the inspection pair satisfies the frozen
acceptance rules, its charges are reconciled, the remaining worst-case bound fits the
remaining cap, and the authorization explicitly covers that remainder. Pause on an
output-length failure, unexplained token discrepancy or other protocol failure; do
not enlarge ceilings, switch providers, change prompts or add repetitions by inference
from unused credit. After a fix, regenerate the affected manifest, rerun its gates and
preserve prior attempts and charges under the same authorization-wide ledger.

This closes the specification review: there are no additional known design blockers
beyond the ten required changes as expanded here. Actual implementation verification
and pilot evidence are still outstanding. Passing them supports a controlled experiment
within the approved budget, using disclosure labels and the documented provider assumptions;
it does not certify the labels, guarantee provider internals or establish model quality
before results exist. The unchanged protected artifacts were checked again in this pass.
