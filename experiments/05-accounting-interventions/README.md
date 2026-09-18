# Accounting intervention study

*Written by OpenAI Codex, directed by Robert Vetter, 17 September 2026. Protocol specified before replacement-score computation, after inspection of known cases and source disclosures. Not prospectively preregistered or blinded.*

## Question

How do source-supported financial-input changes affect the deterministic scorecard when each saved response's qualitative grades are held fixed?

## Fixed design

- Nine responses: Experiment 04 **current-input arm only**, Walmart X20, Nike X12, Signet X15, replicates 1–3. Signet r3 uses the second attempt following a transport failure. No saved-input comparison arm or Opus results enter this study.
- Observation date 2026-08-29; original full fiscal years, not TTM replacements. These are previously exposed development issuers, not nine independent companies or a holdout.
- Replay original vectors/grades against existing scorecard arithmetic and saved outputs before applying any changes. Failure to reproduce the baseline stops the study.
- Five conditions per response: original, interest-only, debt-only, other-supported-accounting-only, combined. Every condition starts from the same original vector. Qualitative grades and free-form model judgement remain unchanged.
- Source choices are recorded in `interventions.json` before replacement scoring, with rejected/unresolved candidates and exact evidence. This is researcher-produced accounting interpretation pending human review, not independent expert ground truth.
- No eligible patch yields `not_estimable`. A supported patch with zero numerical effect remains valid. Combined is the union of available supported patches, not a fully corrected scorecard. Disclose duplicate conditions and untouched fields.
- Source-adjudication qualification fixed before scoring: Signet's debt condition is a **minimum disclosed-lease inclusion** (`max(original debt, 1217.3)`), not a full adjusted-debt replacement. Nike's operating-income condition is an explicit operating-subtotal convention, not certified agency EBIT. These qualifications are encoded in the frozen intervention specification.
- After initial execution, add a descriptive spread diagnostic: check equality of complete financial vectors before attributing remaining within-issuer aggregate differences to stored grades. This is a follow-up analysis of the same conditions, not an additional intervention or a predeclared hypothesis test.

## Interpretation and limits

Primary outcomes are signed changes in ratios, factor scores, weighted aggregate and rating notches. Lower numeric aggregate means a stronger indicated credit rating; improvement in label error is a separate question. All adverse, null and unavailable results remain in the report. Effects need not add because ratios and scorecard boundaries are nonlinear.

Accepted company-disclosure labels and persistence are used only for descriptive, matched-set error comparisons. Original labels remain unverified outstanding ratings at the target date. Report per-replicate results and issuer ordinal-median consensus separately, requiring all three valid responses for consensus. Do not treat replicates as independent observations or infer population performance.

A patch changes only the stated accounting construct; it does not establish complete Moody's adjustments. The sector methodology references a separate cross-sector adjustment methodology not available in this study. Residual discrepancies may reflect untouched financial inputs, qualitative assumptions, omitted adjustments or labels. They are not automatically qualitative errors. The LLM is not rerun, so changes in scorecard output do not imply changes in its overall judgement.

## Sources and reproducibility

Use cached original supplied 10-Ks, raw requests/responses, ledger and per-replicate results from `EXP04-ARM1-A1`. Verify source hashes, original-input membership, publication dates, exact periods, inline operands or quoted spans. Never choose an unsupported number to make the rating closer to its label.

New generated outputs belong in a fresh `evaluation/runs/accounting-interventions-2026-09-17/`; refuse to overwrite earlier outputs. No network, model calls, cache refresh, changes to frozen decisions or old run records, or changes to scorecard code.

## Verification gates

Exact baseline replay; fixed qualitative grades; original vectors unchanged; patch ownership and combination; original-input source eligibility; unit/sign/period validation; undefined ratios; zero-effect and missing interventions; matched denominators; threshold/nonadditivity; no overwrite. Run existing accounting and Experiment 03/04 regressions as well as the new study tests. A focused independent code/evidence review is not a substitute for human accounting adjudication.
