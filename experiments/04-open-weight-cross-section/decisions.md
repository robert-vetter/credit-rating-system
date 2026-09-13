# Decision log, Experiment 04

## DECIDED (Robert, 2026-09-12, via chat)

**D1 Model: Qwen3-235B-A22B-2507 through OpenRouter.** Robert's reasoning, recorded for the
lab update: Opus 4.6 is the strongest model but at 60,000 to 300,000 tokens per issuer it cost
about a dollar per observation, which capped Experiment 03 at seven. He then looked for the
sweet spot between model strength and cutoff date, early enough that labelled rating changes
lie after the bound, recent enough to be strong, cheap enough to run the whole cross-section.

**D2 Budget: the OpenRouter balance, about $7.54 measured on 2026-09-12.** Cap for the run to
be fixed before submission; $3.00 proposed in RUN-SPEC.md section 8.

**D3 Arm 1 first:** the Experiment 03 window and labels, all 20 issuers, so the only change
against Opus 4.6 is the model.

**D4 Review before spending:** the specification goes to Codex for review (RUN-SPEC.md
section 10) before any paid call.

## DECIDED (Robert, 2026-09-12, via the execution instruction to Claude; recorded by Claude, Fable 5.1)

**D5 Cap: a cumulative maximum of $3.00 for this experiment**, covering every model request,
probe, inspected pilot, failed attempt, retry and saved-input comparison. One authorization
across processes, restarts and output folders. No top-up, no larger cap. Recorded in
`authorization.json` and enforced by the ledger of `run_openrouter.py`.

**D6 Provider: Qwen3-235B-A22B-Instruct-2507 through OpenRouter, pinned to DeepInfra fp8**
(`deepinfra/fp8`), with enforced maximum prices of $0.09 per million input tokens and $0.55 per
million output tokens. No automatic provider or model fallback.

**D7 Replicates: three document replicates per issuer and input variant**, temperature 0,
seed 20260912.

**D8 Qurate (X14): the frozen candidate stays unchanged and its diagnostic requests are
executed**, but it is excluded from the primary accuracy interpretation while its target and
as-of validity remain unresolved. The 19-case disclosure-label cohort and the 20-case legacy
sensitivity are reported separately, each with its matching persistence baseline.

**D9 Trim: the documented oldest-10-Q trim applies only where the finalized current package
exceeds the context allowance** (measured: Levi X09 and Qurate X14). Qurate's original
documents stay untrimmed in the saved-input comparison.

**D10 Second model: deferred**, with every other model.

**D12 History packs: option (c).** Current, repaired packs (typed history from the raw rating
records, 24-month peer policy) for all 20 confirmed issuers, plus three replicates on the
original saved inputs for the seven Opus successes. The saved inputs' source-date evidence is
recovered without changing the supplied text (`legacy_provenance.py`, byte-identical
reconstruction from the raw XBRL cache with the 2026-09-10 builder).

**Peer policy, current arm:** peer rows whose latest fiscal-year end is more than 24 calendar
months before the observation date are excluded and logged, and all affected bodies recounted.
The saved-input control keeps its original table.

**Retries:** at most ten additional attempts across the entire experiment and at most one
retry per logical request, under the same cap and review rules. A potentially billed timeout
is never retried blindly: its reservation stays charged and the run halts for a decision.

**Not authorized:** Experiment 03 calls, a second model, Arm 2, a capability shootout, or a
full rerun after a defect.

**Execution plan:** 20 probes, 60 current-input document requests and 21 saved-input document
requests, the 20 confirmed IDs selected explicitly (Experiment 03's `in_run` exclusions are
not inherited). Execution membership is separate from reporting eligibility.

## OPEN

**D11 Arm 2** (official Moody's labels, boundary 2024-09-30, 59 issuers, 12 changes) needs a
model whose bound predates August 2024, so DeepSeek V3-0324 or Llama 4 Maverick, not Qwen.
Not authorized by the 2026-09-12 instruction; separate decision.
