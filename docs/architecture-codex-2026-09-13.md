# A first architecture for the credit rating analyst

*Written by OpenAI Codex, directed by Robert Vetter, 2026-09-13 UTC. Proposed design, not an implemented analyst or authorization to spend. Evidence: Experiments 01 to 04, the corrected 2026-09-12 integrity/calibration audit, and the 2026-09-13 post-execution audit of EXP04-ARM1-A1. The module design below follows those findings; the final section reconciles the earlier proposals. Methodology implementation must use a versioned primary source, not an inferred rule from model outputs.*

The first build should be a source-verified analyst with separate estimates of rating level and whether the prior rating should change. Its useful output is an auditable recommendation with stated uncertainty. A high exact-accuracy percentage alone is not success: persistence still wins, and the latest audit found a current rating table left in the model input.

## What the evidence actually supports

| Evidence, dated | Observation | Design implication |
|---|---|---|
| [Experiment 01 results](/Users/robert/Developer/giesecke/credit-rating-system/experiments/01-oos-cross-section/results.md), 2026-08-30 | Six paired cases; direct variant 5/6 exact, equal to persistence; Nike missed; some recalled ratings wrong | Always show persistence; do not infer memory absence from a negative probe or accuracy from change skill |
| [Experiment 02 results](/Users/robert/Developer/giesecke/credit-rating-system/experiments/02-relative-with-history/results.md), corrected scope warning 2026-08-31 | Extraction-then-judgement 6/9 versus persistence 3/9, but dates predate the model cutoff and gold observations were exposed | Decomposition is a hypothesis worth testing, not established out-of-sample lift |
| [Experiment 03 integrity review](/Users/robert/Developer/giesecke/credit-rating-system/docs/oos-integrity-review.md), 2026-09-12 | Seven selected successes; corrected scorecard 3/7, judgement 4/7, persistence 5/7; methodology edge cases changed a prediction by three notches | Keep arithmetic in code, preserve failures and validate target/label compatibility |
| Same review, corrected calibration | 1,665 non-gold observations: quantitative-only MAE 1.919, calibrated 1.492, persistence 0.053; all four tested change rules select no alarms | Treat calibration as a candidate level diagnostic; do not replace the prior automatically or claim numbers cannot time changes |
| [Experiment 04 post-run audit](/Users/robert/Developer/giesecke/credit-rating-system/experiments/04-open-weight-cross-section/review-codex-2026-09-13.md), 2026-09-13 | Original 19 include the X07 disclosure leak; post-hoc 18 give judgement 16/18, scorecard 3/18, persistence 17/18 | Input eligibility needs structural and semantic checks in addition to hashes and dates |
| Same audit, output checks | Debt stable across three calls on 13/20; working capital on 6/20; all four qualitative grades jointly stable on 8/20; net interest confused with expense | Validate accounting concepts and citation support before accepting numbers or grades |
| Same audit, controls | Current and saved packs replay; staged probes and actual cap pass; two additional fake billing cases fail | Preserve the execution apparatus, repair its uncovered branches, and keep free acceptance gates before spending |

These experiments do not identify why the model stays at the prior. They also do not establish that qualitative grades or missing Moody's adjustments alone cause the level gap. Both are plausible contributors to test separately. The original calibration note is superseded where it conflicts with the corrected integrity review.

## Target contract

Each observation must specify a rated legal entity, reporting parent and permitted consolidation relationship, agency, rating type, currency/seniority where relevant, as-of date t, historical-rating cutoff h, input-source boundary, methodology version and forecast horizon. Do not silently switch from corporate-family to senior-unsecured ratings when a prediction crosses investment grade. Resolve the output contract before scoring it.

For the first version, propose an estimate of the rating outstanding at t, with no claim of advance forecasting. A future rating at t + 12 months is a separate target. Forward financial scenarios can inform today's recommendation without turning today's measured target into a forecast.

The evaluator holds the target label, its effective date, disclosure/publication date, entity/rating type, source and verification state. The analyst receives only the permitted earlier rating and evidence public by t. Keep the original pilot labels frozen. An unresolved or stale disclosure is an unverified label, not an assumed outstanding state. Robert and the lab must approve a new target register before a definitive benchmark.

## Proposed modules and interfaces

| Module | Execution | Input and output contract |
|---|---|---|
| Observation resolver | Code plus human decisions | Frozen target contract to eligible sources and independent label status; unresolved entity/type conflicts block headline eligibility |
| Source and redaction ledger | Code plus targeted review | Cached primary 10-K/10-Q and XBRL to eligible, redacted, hashed evidence spans; retain rejected sources and redaction reasons outside model input |
| Accounting engine | Code first; model only for missing text facts | Source facts to annual/quarterly/TTM figures, gross/net distinctions and itemized adjustments; missing or disputed fields remain missing |
| Qualitative analysis | One bounded structured model call initially | Actual versioned rubric plus eligible evidence to four factor grades, supporting/adverse quotes, alternatives and uncertainty |
| Event analysis | Code for candidate spans; model judgement can share the qualitative call | Dated business events to verified state, significance, affected factors and unresolved questions |
| Level engine | Deterministic arithmetic and optional separately fitted calibration | Verified figures and grades to raw scorecard outcome, scenario range and accounting/qualitative sensitivities |
| Update decision | Small model call or explicit policy, to be compared | Prior plus frozen level/event analysis to keep/upgrade/downgrade/review, proposed level, evidence and counterargument |
| Evaluation and execution | Code | Frozen plan to immutable attempts, coverage, paired persistence comparison, costs and failure report |

This is a logical decomposition, not a proposal for eight paid agents. Start with one bounded evidence-analysis call and, when testing the prior-withheld design, a separate small decision call. Probes remain separate and earlier. No model request carries tools or live retrieval. Eligible documents are prepared by the application before a call.

### Evidence before inference

Each fact or quote needs an immutable source ID, raw and redacted document hash, SEC accession, form, public filing date, economic period start/end where relevant, entity scope, units/currency, exact source span and extraction/verification state. Derived values additionally list component IDs and the formula. Their availability date is the latest component date. The assembled input carries a manifest linking exactly which spans were supplied.

Dates, hashes and literal-quote matching are deterministic checks. They cannot establish that a quote supports the model's conclusion. Validate the quoted span's context, accounting meaning, and issuer attribution; disputed conclusions remain review items. Numeric reference tables must be withheld when measuring independent text extraction, even if they are useful in the deployed analyst.

Replace agency-line stripping with table-aware redaction, followed by an independent scan of the final assembled text for orphan symbols, outlooks, rating-conditioned pricing and financing language. Kohl's B2 table is a required regression. Retain whole non-rating business tables and legitimate distress information. A clean scan means that specified checks passed, not that all contamination is impossible.

Current rules exclude 8-Ks and exhibits as model input. The earlier architecture's proposed 8-K module is not authorized here. If the lab later needs faster event coverage, Robert must first approve a separate source policy and leakage evaluation. A filings-only analyst must disclose the events it cannot yet observe.

### Accounting and Moody's adjustments

Normalize annual flows, quarter/YTD flows and balance-sheet instants before calculating ratios. Derive TTM flows from compatible latest FY + current YTD - prior comparable YTD, with every component public by t. Match periods, units, consolidation scope and restatement basis. Never treat a missing quarter or expense as zero. Flag 52/53-week differences and acquisitions that break comparability.

Use a component ledger for debt: distinguish funded debt, current portions already included in totals, finance leases and operating leases. Signet's zero funded borrowing cannot erase its $1,217.3 million of lease liabilities. Distinguish gross interest expense, net interest income, cash interest paid and capitalized interest. Nike's -50 net-interest line and 323 cash payment are different concepts, not interchangeable estimates. Preserve sign and source definition. A fallback must be labelled as an approximation or rejected under the target ratio's definition.

Maintain an adjustment registry keyed to the applicable Moody's methodology version and exact section/page: rule, permitted inputs, calculation, applicability, missing-data treatment and test cases. Investigate leases, pensions, hybrids and other relevant adjustments from the applicable primary financial-adjustments methodology before implementation. Do not invent rent multiples or automatically apply every possible adjustment to every issuer. Separate as-reported, adjusted and approximated figures so discrepancies remain inspectable.

Retain the repaired scorecard boundary behavior for non-positive EBITDA, net cash, undefined ratios and outcome rounding. Add source-semantic checks to those arithmetic tests. A mathematically valid score from an incorrectly defined input is still analytically invalid.

Calibration remains a separate, visibly named diagnostic. The existing map was fitted to a quantitative-only aggregate with proxy qualitative treatment. It must not be applied untested to a full qualitative scorecard, to a new adjusted feature definition, or as a universal one-notch downgrade. Refit only on authorized development data with issuer separation and calendar-time cutoffs; re-evaluate when the accounting basis changes. The old retrospective folds do not establish a model that could have been trained before every historical t.

### Qualitative grades and events

Supply the actual dated rubric for all four qualitative factors. For each factor require its chosen band, the rubric clauses satisfied, exact supporting and adverse source quotes, comparison with the nearest alternative band, and explicit evidence gaps. A globally famous brand does not automatically justify Aaa across market characteristics, position, stability and policy.

First estimate factors from fundamentals with the prior rating and implied qualitative anchor withheld. Freeze that output before the update stage sees the prior. This makes a useful test of prior-induced anchoring possible; it does not remove memorized company identity or prove this design will perform better. Test it against the same evidence with the prior visible, under a separately approved cap.

Qualitative instability should be localized. Repeated ratings are not independent observations. Measure grade disagreement by factor, evidence-span disagreement and its propagated scorecard effect. If plausible supported grades change the proposed decision, surface a range and route the case to review. Do not buy repetitions until one agrees with the target. Any fixed repeat/adjudication rule must be specified before running.

The event record distinguishes announced, agreed, filed, court-approved, completed and uncertain states. Qurate's confirmed restructuring plan cannot be relabelled "emerged". For distress, record filing date, liquidity, covenant/default facts, debt maturity/refinancing pressure, going-concern language, support and structural changes, with citations. An event may justify review independently of a comfortable scorecard; it does not automatically map to a guessed rating notch. Business outlook and rating-agency outlook are different evidence categories, and the latter remains redacted under this experiment's policy.

### Level and change decisions

Keep three outputs visible: persistence, scorecard-indicated level and analyst judgement. The final judgement must identify what evidence supports a departure from the prior and what evidence supports retaining it. Compute direction mechanically from the proposed rating and prior. Validate consistency with all action fields.

A change module should estimate evidence for upgrade, unchanged or downgrade and an associated level/range. Confidence is a claim to calibrate on held-out data, not a validated probability merely because the model prints a number. Review/abstention is a separate outcome with a measured coverage cost. Do not quietly score it as persistence; an explicitly named operational fallback can be evaluated separately.

Do not yet hard-code "move only if both historical and forecast scorecards move one notch." No experiment has validated that conjunction and it could suppress real event-driven changes. Develop a decision policy on a sufficiently broad, independently labelled development panel, using a prespecified tradeoff between missed changes and false alarms. Evaluate its change decision separately from level MAE. A model that never alarms can win aggregate MAE in this distribution while having no value on changes.

Financial forecasting belongs after the source/TTM baseline. A later module can propose 12 to 18 month scenarios for revenue, margins, cash generation, debt and liquidity using information available at t. Define forecast errors against dated realized financial outcomes, including which later revision counts as truth. Evaluate whether those forecasts add rating skill separately. Discuss the interface with the lab rather than assume their EDGAR-Forecast results transfer.

## Evaluation contract

Freeze cohorts, source policy, features, prompt/rubric, provider configuration, hypothesis, stop rules and spending cap before a paid test. Stage a memory probe before every observation's documents; keep its result out of later inputs and report positives/negatives without a contamination certificate. Quote vendor cutoff evidence or clearly distinguish a checkpoint release bound and hosted-identity limitation.

Use natural-prevalence outstanding-rating observations for the headline. Report exact agreement, within-one, notch MAE, valid/planned coverage and matched persistence. Separately report changed-case exactness/direction, unchanged false alarms and abstentions. Add issuer-level uncertainty estimates appropriate to the sample; do not use repeated calls as extra issuers. Report failure-adjusted performance and actual spending, including invalid attempts and unresolved reservations.

A changed-case stress set is useful for development but cannot supply an unweighted natural-cross-section headline. The current 18-case post-hoc sensitivity is an audited pilot result, not a new untouched holdout. The previously exposed gold set remains frozen and excluded from fitting; exclusion cannot restore never-seen status. Robert must designate a genuinely unexposed evaluation set for a confirmatory claim.

Use chronological development/validation/test boundaries and issuer grouping. Distinguish generalization to a new issuer from updating a known issuer; never allow later data into either model fitting or input selection for t. Match observations and eligible inputs in ablations. Measure the quantitative-only baseline, citation/rubric addition, prior-visible versus prior-withheld analysis, event module and later forecasting individually. Do not choose among them using Nike or Qurate after seeing their answers.

## Build order and acceptance criteria

1. **Free: close the observed controls.** Add Kohl's structural-redaction regressions and semantic scans; fix ambiguous error billing, above-reservation/above-cap settlement and fresh-price checks; retain raw generation details; verify that all mutations use the shared authorization ledger. Existing fixtures plus new adversarial cases must pass with zero real network dispatches.
2. **Free: evidence ledger and accounting baseline.** Implement date/period/units contracts and TTM calculations on synthetic edge cases and non-gold cached examples. Verify exact source reproduction, no later filings, no double-counted debt, and explicit missing values. Audit Nike/Signet as regression examples without treating them as held-out performance tests.
3. **Free: rubric and event specifications.** Version the actual rubric, write citation/context validators and model-output contracts, and assemble a review packet with known contradictions and uncertain event states. Draft the two proposed model stages and count their exact worst-case cost locally; do not submit.
4. **After separate approval: one bounded analyst comparison.** Measure whether citations are supported, accounting concepts are correct, the prior-withheld stage changes decisions, and any change skill survives false alarms. Use the approved natural-prevalence cohort and diagnostic split. Predefine technical retry limits and no quality-based replacement.
5. **Only after those measurements: adjustments/calibration expansion and forecasts.** Obtain missing primary methodology rules, extend the audited accounting basis and refit development calibration as needed; test forecast value rather than attach it by default.

The first success criterion is verified evidence integrity, not a higher rating score. On a reviewed development sample, count correctly supported numeric fields, correct dates/units/concepts, citation support, event-state accuracy, factor disagreement and coverage. A later analyst succeeds only if it offers a useful prespecified change/false-alarm tradeoff while reporting its level accuracy against persistence. Current evidence is insufficient to promise that result or set a reliable numerical threshold.

## Decisions for Robert and the lab

The unresolved choices are the exact rating-type/entity contract, current-state estimation versus a future horizon, an independently verified label panel and holdout, the acceptable false-alarm/abstention tradeoff, and the future call budget. Additional source types and peer ratings require explicit decisions; neither is part of this first proposal. Ask for dated rating histories that identify legal entity, type, effective actions and withdrawals so outstanding states can be established. Do not promise that access automatically yields hundreds of eligible Retail and Apparel observations.

## Reconciliation with earlier proposals

The existing [Claude architecture v0.2](/Users/robert/Developer/giesecke/credit-rating-system/docs/architecture.md) and the [earlier Codex module table](/Users/robert/Developer/giesecke/credit-rating-system/docs/oos-integrity-review.md) correctly separate evidence, numbers, qualitative analysis, scorecard and evaluation. This draft retains those components, code-based arithmetic, source dates, TTM work and free development first.

It changes the prior-rating design. An implied grade can absorb accounting adjustments, structural notching and committee judgement; it is not an identified qualitative truth. Withholding it from the first analysis is a testable alternative, not a declaration that the old design caused all inertia.

It removes the unvalidated historical-and-forecast conjunction, unapproved 8-K input, assumed $0.50 per-issuer price and promise of hundreds of labels. It keeps an outstanding **level** as the requested output while evaluating the **change decision** separately, rather than replacing Xiaowei's target with an action-only task.

It also corrects three historical claims. A scorecard-indicated outcome is an input to rating analysis, not a complete deterministic assignment rule. The bankrupt-issuer "four notches too high" anecdote used defective arithmetic and an unresolved target; the repaired result is Caa2 against the stale disclosed Caa3, which is not a verified post-bankruptcy truth. Finally, annual figures' inability to time changes was not proven: the four specific tested signals and their overall-MAE selection criterion chose persistence. The new draft treats adjustments, qualitative reliability, events and forecasts as separately testable additions.
