# Accounting interventions: what changes the scorecard?

*Written by OpenAI Codex, directed by Robert Vetter, 17 September 2026. Verified against nine saved Qwen current-arm responses, original dispatched input hashes, 23 cited filing operands and deterministic replay. Source-supported accounting interpretations remain pending human review. An independent agent checked cited evidence and mechanics; this is not expert hand-labelled ground truth.*

## Main finding

**Financial-input changes do not translate directly into rating improvements.** Supported interventions move one saved response by two notches, but leave all three issuer-consensus ratings unchanged. Once financial vectors are equalized for Signet, its stored qualitative grades alone produce a **three-notch within-issuer spread**, A1 to Baa1. This isolates a source of instability in this calculation, not the correct grades or the cause of all label error.

Scope: Walmart, Nike and Signet, three saved replicates each, original fiscal years and target 2026-08-29. Each intervention retains that response's original four qualitative grades. No LLM rerun, new retrieval or claim of a fresh holdout.

## 1. Interventions and source support

Values in USD millions. The [specification](interventions.json) records source hashes, exact inline element/context IDs, quoted evidence, signed operands and unresolved fields. Source choices were fixed before replacement scores were computed. Known prior results were not blinded.

| Issuer | Intervention | Original → tested | Interpretation |
|---|---|---|---|
| Walmart | Gross interest | 2,431 → 2,799 in all three responses | Debt interest2,318 + income-statement finance-lease/financing interest481; net expense2,431 subtracts interest income368. Standard lease-note interest383 is narrower than the custom income-statement line. |
| Walmart | Revenue | 706,413 → 713,163 | Total reported revenue includes membership/other income6,750. Methodology p6 specifies total reported revenue. |
| Walmart | Working-capital subtotal | 1,007 / 1,071 / 1,000 → 752 | Sum the five displayed operating asset/liability changes, with cash-flow signs. Follows the executed task, not certified agency FFO. |
| Nike | Operating subtotal | 3,850 → 3,797 | Gross profit19,911 − selling/administrative16,114. Company EBIT3,850 includes other nonoperating income53. This is an explicit operating-subtotal convention sensitivity, not a certified Moody's adjustment. |
| Nike | Working-capital subtotal | −1,678 → −1,678 | Source-supported zero-change control under the executed task definition. |
| Signet | Minimum lease inclusion | 1,217.3 / 1,217.3 / 0 → 1,217.3 | `max(original debt, recognized operating leases)`. A minimum-inclusion test, not complete adjusted total debt; avoids adding leases twice. |
| Signet | Working-capital subtotal | 10.4 / 10.8 / 10.8 → 92.5 | Sum all seven displayed operating asset/liability changes, including lease, deferred-revenue and tax lines as specified by the executed task. Not certified agency RCF. |

**Not estimable:** gross interest for Nike/Signet; full adjusted debt for all three. No inference of gross expense from net interest, cash payments or a partial interest-income disclosure. Walmart/Nike have no debt-condition patch; Signet's debt condition is only the floor above. Other financial inputs remain original and are not certified correct.

## 2. Before/after outcomes

The combined condition applies all supported patches to a fresh original vector. For Nike it duplicates the other-accounting condition because interest and debt are unresolved. The Signet combined and debt-only conditions happen to have identical scores, although their financial vectors differ in working capital.

| Issuer | Scorecard r1 / r2 / r3 before | After combined | Combined aggregate changes r1 / r2 / r3 | Accepted label / persistence |
|---|---|---|---|---|
| Walmart | Aa3 / Aa2 / Aa3 | Aa3 / Aa2 / Aa3 | +0.087243 / +0.085540 / +0.087429 | Aa2 / Aa2 |
| Nike | Aa2 / Aa3 / A1 | Aa2 / Aa3 / A1 | +0.012597 / +0.012597 / +0.023145 | A2 / A1 |
| Signet | A3 / Baa1 / Aa2 | A3 / Baa1 / A1 | 0 / 0 / +1.163291 | Ba3 / Ba3 |

Positive score changes indicate weaker credit quality. Whether that is closer to the label is measured separately. Signet r3 improves from ten to eight notches of label error; it remains far from its accepted Ba3 label.

### Why some changed inputs produce no rating movement

- **Walmart revenue:** both values exceed the top scale endpoint, so the Revenue score stays0.5. The source definition changes, but the score does not.
- **Walmart interest:** coverage falls from **7.1518× to 6.2115×**. Its factor score moves8.7321→9.3590, adding **0.094029** to the weighted aggregate. No rating threshold is crossed. Working-capital changes offset a small part of this effect.
- **Signet working capital:** in r1 the implemented RCF/net-debt ratio falls **180.0%→156.0292%**, but both exceed the100% best-score endpoint. Its factor remains0.5. This is a property of this task-defined calculation, not a verified Moody's RCF measure.
- **Signet lease floor:** r3 debt/EBITDA moves **0→2.2518×**, changing that factor0.5→8.2553 and adding **1.163291** to the aggregate. This crosses two rating notches. The other two responses already included the disclosed lease amount.

These examples distinguish source correctness, ratio changes, score saturation and discrete rating boundaries. A zero-notch effect is not evidence that the original accounting definition was correct.

## 3. What remains unstable after supported interventions?

This descriptive check was added after the first intervention run. It does not change the conditions or source choices.

| Issuer | Complete financial vectors identical across replicates after combined? | Quantitative weighted-score range | Qualitative weighted-score range | Rating range |
|---|---|---:|---:|---|
| Walmart | Yes | 0 | 0.900000 | Aa2–Aa3: one notch |
| Signet | Yes | 0 | 3.000000 | A1–Baa1: three notches |
| Nike | No: interest remains50 /50 /323 | 0.860327 | 0.900000 | Aa2–A1: two notches |

For Signet, the common quantitative contribution is3.177271. Stored qualitative contributions are4.05,4.35,1.35, giving aggregate scores7.227271,7.527271,4.527271. Hence the remaining within-issuer spread is exactly due to stored grades in this fixed calculation. The same reasoning applies to Walmart. It does **not** establish which grade is justified, or attribute the remaining difference from agency ratings to qualitative judgement. Nike retains incompatible interest inputs, so that attribution cannot be made there.

## 4. Matched descriptive accuracy, not generalization

Issuer consensus requires all three valid ratings and takes their ordinal median. The main experimental unit remains the issuer, not the response repetition.

| Condition | Eligible issuers / planned | Consensus exact: intervention / matched original / persistence | Consensus MAE: intervention / matched original / persistence |
|---|---:|---|---|
| Original | 3/3 | 0/3 / 0/3 / 2/3 | 3.000 / 3.000 / 0.333 |
| Interest only | 1/3: Walmart | 0/1 / 0/1 / 1/1 | 1.000 / 1.000 / 0.000 |
| Debt floor only | 1/3: Signet | 0/1 / 0/1 / 1/1 | 6.000 / 6.000 / 0.000 |
| Other supported accounting | 3/3 | 0/3 / 0/3 / 2/3 | 3.000 / 3.000 / 0.333 |
| Combined supported | 3/3 | 0/3 / 0/3 / 2/3 | 3.000 / 3.000 / 0.333 |

Across the nine response repetitions, combined MAE decreases **29/9=3.222→27/9=3.000**, entirely from Signet r3. Exact matches remain1/9; persistence is6/9 exact, MAE3/9=0.333. This is a descriptive repetition summary, not nine independent observations. Consensus MAE does not improve because the changed response does not alter Signet's median. Nike is the only changed accepted label; its consensus remains Aa3 and still misses A2. Both unchanged issuers' consensuses remain different from their labels. Original model judgements are not recomputed.

## 5. Implication for the next experiment

**A useful next study distinguishes insufficient evidence from inconsistent application of the rubric.** Hold both financial inputs and the evidence package fixed. Independent reviewers should assess each factor under those same information constraints, recording a justified grade or range, missing evidence and disagreement. Compare model reference agreement and repeatability separately; a stable but unsupported grade is not success. Reference assessments are not yet available and must not be inferred from the target rating. This informs when to automate a grade and when to flag uncertainty, rather than merely testing whether different inputs produce different outputs. Use new development cases and a separately defined evaluation cohort. Preserve unresolved gross-interest/agency-adjustment issues rather than treating all financial inputs as solved.

This study does not justify a claim of beating persistence, complete accounting correction, stable extraction, or correct qualitative grades. It does supply measured reasons to distinguish (a) accounting correctness, (b) scorecard sensitivity, and (c) grading stability before building a larger analyst.

## Reproducibility and verification

```sh
python3 experiments/05-accounting-interventions/run_study.py
python3 -m unittest discover -s experiments/05-accounting-interventions -p 'test_*.py' -v
```

The saved local run is `evaluation/runs/accounting-interventions-2026-09-17/`, with `study.json` and a complete45-slot results table (nine baselines plus36 intervention slots;12 not estimable). The runner refuses to overwrite an existing output directory. Raw source caches and saved API artifacts are gitignored, so a fresh clone cannot replay the real cases without them.

All nine original financial vectors/grades, aggregates and outcomes reproduce the saved result records and valid ledger entries. The source filing's redacted representation is hash-bound to the dispatched request. Original fiscal metadata is checked; Nike r3 says only FY2026, so its year-to-annual-anchor alignment is explicitly weaker than an exact original date. None of this independently verifies every original field.

Twenty-one study tests pass, along with19 accounting-prototype and61 existing Experiment03/04 regressions. Test development exposed an incorrect expected notch count (A1–Baa1 is three, not four) and an overly strict original-period parser; both were fixed before final output. A focused evidence/code review checked all23 operands and prompted original-period and input-body-binding safeguards. Review does not replace human accounting adjudication. No old run, label, scorecard or cache was rewritten; no model calls, downloads, commits or publication.
