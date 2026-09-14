# Credit rating analyst: proposed architecture

*Written by OpenAI Codex, directed by Robert Vetter, 13 September 2026. Proposal based on the [experiment results](../experiments/04-open-weight-cross-section/results.md) and [integrity review](oos-integrity-review.md); not yet implemented as a complete system.*

## Objective

Estimate an issuer's outstanding Moody's rating at a specified date, following the Retail and Apparel methodology. Return the proposed rating, the scorecard-indicated outcome, and a cited explanation of why the earlier rating should be retained or changed. Fix the rated legal entity and rating type before analysis; a corporate-family rating and a senior-unsecured rating are different targets.

The experiments point to three requirements: evaluate change decisions against persistence, verify accounting definitions before calculating ratios, and ground qualitative grades in the methodology's rubric. High exact accuracy alone has not demonstrated useful rating skill.

## Analysis pipeline

| Component | Method | Output |
|---|---|---|
| **1. Evidence** | Select primary 10-Ks, subsequent 10-Qs and XBRL facts public by the observation date. Remove rating disclosures, including table fragments and rating-conditioned terms. | Source records with filing dates, economic periods, units, document hashes and exact locations. |
| **2. Financial analysis** | Calculate annual and trailing-twelve-month metrics in code. Reconcile debt and leases, distinguish gross interest expense from net interest income, and itemize applicable Moody's adjustments. Use model extraction for facts missing from structured data. | As-reported and adjusted figures, with component sources and explicit missing values. |
| **3. Qualitative and event analysis** | Give the model the actual rubric for market characteristics, market position, revenue/earnings stability and financial policy. Require supporting and adverse evidence. Assess liquidity, refinancing, transactions and distress separately. | Four factor grades, cited reasoning, uncertainty and material events with their status and dates. |
| **4. Scorecard** | Apply the methodology's weights, ratio definitions and rating boundaries in tested code. Propagate uncertain inputs and alternative supported grades. | Scorecard-indicated rating and sensitivity range. |
| **5. Rating decision** | Compare the completed analysis with the earlier rating. Explain which new facts justify retaining or changing it, including considerations outside the scorecard. | Final rating, direction of change, rationale and unresolved issues requiring review. |

Financial and qualitative analysis can proceed in parallel. Initially use one structured model call for qualitative/event analysis and a smaller call for the final decision; calculations and validation remain in code.

Validate each number's source, period, units and accounting definition. Quotes must support the conclusion, not merely match text in a document. Missing values and material source conflicts remain explicit.

Initially withhold the prior rating and its implied qualitative grades from the first analysis, then reveal the prior at the decision stage. Compare this with a prior-visible version to test whether supplying history induces anchoring. The existing results suggest that possibility but do not establish it.

## Forecasting and calibration

A subsequent component would forecast revenue, margins, cash generation and leverage over 12 to 18 months, with explicit assumptions and scenarios. Evaluate forecasts against realized figures, then test whether they improve today's rating estimate. Predicting a future rating is a separate target.

Keep calibration separate from the methodology scorecard. On 1,665 development observations, quantitative-only calibration reduced notch MAE from 1.919 to 1.492, versus persistence's 0.053. Test it for level estimation; it has not established a useful change signal. Revalidate it when the accounting basis changes.

## Evaluation and first build

Report exact accuracy and notch MAE against persistence on the same issuers, alongside changed-case direction, false alarms on unchanged issuers, and missing or abstained outputs. Use chronological and issuer-separated evaluation; exclude the frozen gold set from development. Repeated calls measure instability, not additional independent observations. Retain dated cutoff evidence, staged memory probes, fixed inputs, no model tools or live retrieval, and a priced call budget.

Build the evidence records and accounting/TTM baseline first using cached data. Then test rubric-grounded grading and the separate rating decision. Add forecasts after those components are reliable. Measure each addition on the same evaluation set so its contribution is identifiable.

For the lab: agree the target rating type, obtain dated histories establishing outstanding ratings, and define the acceptable tradeoff between missed changes and false alarms. Faster event sources beyond 10-Ks/10-Qs would require a separate source policy.
