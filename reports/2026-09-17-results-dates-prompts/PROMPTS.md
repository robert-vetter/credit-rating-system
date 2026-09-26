# Exact prompts and request specification

*Prepared by OpenAI Codex, directed by Robert Vetter, 17 September 2026. System/task text checked against the frozen Qwen requests and the original Experiment 03 prompt files. Schemas below retain every field and constraint; JSON whitespace is compacted for readability. No executed prompt was edited.*

[Summary and results](README.md) · [Dates and labels](DATES-AND-LABELS.md)

## What the main call received

Two messages: **system instruction**, then **one user message** containing the following in order. The bracketed payload descriptions below are explanatory placeholders, **not literal model inputs**. Full company documents and variable history packs are not reproduced here.

```text
<document name="10-K filed YYYY-MM-DD">
[Actual filing text after the executed redaction pass]
</document>
[Subsequent supplied 10-Q document blocks, if any]

<history_pack>
[Issuer identity; historical rating path through 2025-08-28;
annual financial history and latest available figures;
implied qualitative anchors; quarterly financial rows where available;
peer financial table without peer ratings; source dates]
</history_pack>

As-of date: 2026-08-29.

[Exact task text below]
```

The anchors were inferred from historical ratings and quantitative factors, **not Moody's actual qualitative factor grades**. Financial context could contain post-model-bound facts public by the target date. The full methodology PDF/rubric was **not** in these requests. No model tools, Internet grounding or live retrieval were provided.

## 1. Main system instruction, verbatim

```text
You are a credit analyst working with Moody's Retail and Apparel rating methodology (September 2025). Use only the material provided in this conversation. Ignore any recollection you may have about this company's current or recent credit ratings; if rating fragments survive in the documents, ignore them too. Where a figure is not directly disclosed, derive it from what is disclosed and explain the derivation; never substitute a round guess.
```

## 2. Main task, verbatim

```text
TASK. From the documents above (the issuer's most recent annual report and subsequent quarterly reports), the history pack and the peer table, produce the scorecard inputs as JSON per the schema.

Quantitative (USD millions, most recent FULL fiscal year contained in the documents; state the period used in figure_notes): revenue, operating_income, d_and_a, capex, interest (gross incl. finance-lease interest where split out; say so if only net is disclosed), cash, dividends, cfo, wc_swing (sum of working-capital lines inside operating cash flow, sign as reported), debt (Moody's-adjusted: short-term debt + current portion + long-term debt + finance-lease liabilities + operating-lease liabilities + financing obligations). Where the quarterly reports show a material change since the fiscal year end (new debt, asset sales, sharp margin moves), note it in figure_notes; the scorecard uses the fiscal-year figures, the notes inform the judgement below.

Qualitative, graded Aaa/Aa/A/Baa/Ba/B/Caa/Ca, each assessed RELATIVE to the implied anchor in the history pack and marked up / same / down with a one-line, document-tied justification: Market Characteristics (scale, growth, cyclicality and disruption exposure of the segments served), Market Position (competitive strength, share trajectory, brand and pricing power), Revenue and Earnings Stability (volatility of revenue and margins through cycles; secular decline grades low), Financial Policy (leverage appetite, buybacks, dividends, M&A, ownership; PE ownership or debt-funded returns grade low).

Then, separately: direct_rating — your overall long-term rating judgement for this issuer as of the as-of date, and vs_last_known (upgrade / unchanged / downgrade) relative to the last rating in the history pack, with the two or three drivers that decide it.
```

**Important design limitations, not corrected retroactively:** the schema below required a number for every financial field and explicitly allowed net interest when gross expense was unavailable. The debt instruction lists potentially overlapping components without a complete adjustment/reconciliation procedure. These are prompt-design limitations, not solely model mistakes. Asking the model to ignore surviving rating fragments did not prevent the disclosed Kohl's/Dollar General leakage.

## 3. Separate memory probe

Executed as a separate request before each issuer's main Qwen document calls. Probe output was **not** included in the main call. The earlier Opus pilot used separate probe requests in the same initial batch; probe-first processing is not established for Opus.

**System, verbatim:**

```text
You are being probed for what you know FROM MEMORY about a company's credit profile. Answer strictly from your training knowledge. Do not guess plausible values: if you do not specifically recall a number or rating, return null and say so. Honest "I don't know" answers are the desired behavior here.
```

**User template, verbatim:** `{as_of}` is replaced with `2026-08-29`; `{edgar_name}` with the SEC issuer name.

```text
As of {as_of}: {edgar_name} (US retailer). What is its current Moody's long-term credit rating, what Moody's-adjusted metrics do you recall (debt/EBITDA), what was its most recent full fiscal year's revenue and when did that fiscal year end, and what Moody's rating actions on it since mid-2025 do you know?
```

For example, the frozen Nike user message starts `As of 2026-08-29: NIKE, Inc. (US retailer).` A negative probe is not proof of no post-bound knowledge.

## 4. Qwen execution settings and output interpretation

| Setting | Executed value |
|---|---|
| Model ID | `qwen/qwen3-235b-a22b-2507` |
| Provider | `deepinfra/fp8`; `allow_fallbacks: false`; `require_parameters: true`; `quantizations: ["fp8"]` |
| Sampling | `temperature: 0`; `seed: 20260912` |
| Output ceiling | Main calls: `max_tokens: 8192`; probes: `1200` |
| Other request settings | `stream: false`; `transforms: []`; no `tools` key |
| Structured output | `response_format.type: "json_schema"`; `strict: true` |
| Replication | Three independent requests per issuer with the same supplied information |
| Consensus | Median of three valid ordinal ratings, separately for judgement and scorecard |
| Direction measurement | Computed from rating symbols, not trusted from `vs_last_known` text |

The scorecard is calculated in code from `figures_usd_m` and `qualitative`; `direct_rating` is the model's separate judgement. Full schemas follow for inspection, not required for the five-minute summary.

<details>
<summary>Complete main output schema (JSON; whitespace compacted only)</summary>

```json
{
 "type":"object",
 "properties":{
  "fiscal_year_label":{"type":"string"},
  "figures_usd_m":{
   "type":"object",
   "properties":{
    "revenue":{"type":"number","description":"total revenue, most recent full fiscal year"},
    "operating_income":{"type":"number","description":"operating income, same fiscal year"},
    "d_and_a":{"type":"number","description":"depreciation and amortisation (cash-flow statement)"},
    "capex":{"type":"number","description":"capital expenditures"},
    "interest":{"type":"number","description":"gross interest expense incl. finance-lease interest where split out; if only net interest is disclosed, use it and say so in notes"},
    "cash":{"type":"number","description":"cash and cash equivalents at fiscal year end"},
    "dividends":{"type":"number","description":"dividends paid (cash-flow statement); 0 if none"},
    "cfo":{"type":"number","description":"net cash provided by operating activities"},
    "wc_swing":{"type":"number","description":"sum of working-capital change lines inside operating cash flow (sign as reported: negative if working capital consumed cash)"},
    "debt":{"type":"number","description":"Moody's-adjusted total debt: short-term debt + current portion + long-term debt + finance-lease liabilities (current and noncurrent) + operating-lease liabilities (current and noncurrent) + financing obligations"}
   },
   "required":["revenue","operating_income","d_and_a","capex","interest","cash","dividends","cfo","wc_swing","debt"],
   "additionalProperties":false
  },
  "figure_notes":{"type":"string","description":"which lines were summed for debt/interest/wc_swing, any judgement calls"},
  "qualitative":{
   "type":"object",
   "properties":{
    "Market Characteristics":{"type":"string","enum":["Aaa","Aa","A","Baa","Ba","B","Caa","Ca"]},
    "Market Position":{"type":"string","enum":["Aaa","Aa","A","Baa","Ba","B","Caa","Ca"]},
    "Revenue and Earnings Stability":{"type":"string","enum":["Aaa","Aa","A","Baa","Ba","B","Caa","Ca"]},
    "Financial Policy":{"type":"string","enum":["Aaa","Aa","A","Baa","Ba","B","Caa","Ca"]}
   },
   "required":["Market Characteristics","Market Position","Revenue and Earnings Stability","Financial Policy"],
   "additionalProperties":false
  },
  "qualitative_rationale":{"type":"string","description":"one sentence per factor"},
  "direct_rating":{"type":"string","enum":["Aaa","Aa1","Aa2","Aa3","A1","A2","A3","Baa1","Baa2","Baa3","Ba1","Ba2","Ba3","B1","B2","B3","Caa1","Caa2","Caa3","Ca","C"],"description":"your own overall rating judgement for this issuer, independent of the scorecard arithmetic"},
  "direct_rationale":{"type":"string"},
  "qualitative_relative":{
   "type":"object",
   "properties":{
    "Market Characteristics":{"type":"string","enum":["up","same","down"]},
    "Market Position":{"type":"string","enum":["up","same","down"]},
    "Revenue and Earnings Stability":{"type":"string","enum":["up","same","down"]},
    "Financial Policy":{"type":"string","enum":["up","same","down"]}
   },
   "required":["Market Characteristics","Market Position","Revenue and Earnings Stability","Financial Policy"],
   "additionalProperties":false
  },
  "vs_last_known":{"type":"string","enum":["upgrade","unchanged","downgrade"]}
 },
 "required":["fiscal_year_label","figures_usd_m","figure_notes","qualitative","qualitative_rationale","direct_rating","direct_rationale","qualitative_relative","vs_last_known"],
 "additionalProperties":false
}
```

</details>

<details>
<summary>Complete memory-probe output schema (JSON)</summary>

```json
{
 "additionalProperties":false,
 "properties":{
  "claimed_debt_ebitda":{"type":["number","null"]},
  "claimed_fy_end":{"type":["string","null"]},
  "claimed_latest_fy_revenue_usd_bn":{"type":["number","null"]},
  "claimed_moodys_rating":{"type":["string","null"]},
  "claimed_recent_rating_actions":{"type":"string"},
  "notes":{"type":"string"},
  "rating_confidence":{"enum":["high","medium","low","none"],"type":"string"}
 },
 "required":["claimed_moodys_rating","rating_confidence","claimed_debt_ebitda","claimed_latest_fy_revenue_usd_bn","claimed_fy_end","claimed_recent_rating_actions","notes"],
 "type":"object"
}
```

</details>

<details>
<summary>Original files and reproducibility boundary</summary>

The fixed system/task/schema are shared with Experiment 03: [system.txt](../../experiments/03-oos-values-first/prompts/system.txt), [task_values_first.txt](../../experiments/03-oos-values-first/prompts/task_values_first.txt), [schema_values_first.json](../../experiments/03-oos-values-first/prompts/schema_values_first.json), [probe.txt](../../experiments/03-oos-values-first/prompts/probe.txt).

Frozen Qwen request bodies are local under `experiments/04-open-weight-cross-section/runs/EXP04-ARM1-A1/bodies/`. This page is the exact instruction/schema specification plus an explanatory payload layout, **not a byte-identical copy of a complete issuer request**. Full documents/history packs are local and are not published here. The main Qwen history/peer inputs were revised after Opus; only the explicitly saved-input comparison uses Opus's original supplied information.

</details>
