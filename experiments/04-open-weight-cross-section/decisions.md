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

## OPEN (Robert)

**D5 Cap** exact number, $3.00 proposed.

**D6 Provider:** GMICloud proposed (262k, fp8, $0.09/$0.35, supports response_format, seed,
temperature), DeepInfra as fallback; fp4 providers excluded.

**D7 Replicates:** three proposed, temperature 0, seed 20260912.

**D8 Qurate (X14):** keep and report with and without, as in Experiment 03 (proposed), or drop.

**D9 Trim rule:** Levi (X09) and Qurate (X14) exceed 253,952 tokens with the full document
set; dropping the single oldest 10-Q brings both under it (measured). Proposed: trim and flag
per observation. Never let the provider truncate.

**D10 Second model:** GLM-4.6 or Kimi K2-0905 for a second opinion at about $2 per pass, now
or later.

**D11 Arm 2** (official Moody's labels, boundary 2024-09-30, 59 issuers, 12 changes) needs a
model whose bound predates August 2024, so DeepSeek V3-0324 or Llama 4 Maverick, not Qwen.
Separate decision.
