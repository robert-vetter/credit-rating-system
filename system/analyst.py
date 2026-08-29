"""
The analyst: one API call that reads filings and proposes the scorecard inputs.

Written by Claude (Opus 5), directed by Robert Vetter.

Division of labour, per the architecture in the repo README: the model proposes the eight
subfactor inputs (ten raw financial figures for the four quantitative subfactors, four
qualitative letter grades), the deterministic engine in system/scorecard.py turns them into a
rating. The model also states a direct rating guess, recorded as a secondary output so
scorecard-mediated and free-form prediction can be compared.

Contamination controls built into the request shape: a raw Messages API call with NO tools
array (retrieval and web access structurally impossible, per the verified finding in
docs/experiment-plan.md), documents redacted by system/redact.py before they get here, and an
instruction not to use recalled knowledge of the company's actual rating. Model memory of the
company itself cannot be switched off; the experiment design (update prediction against a
persistence baseline, docs/experiment-plan.md) is what neutralises it, not this prompt.

Structured output via output_config JSON schema: the response is machine-readable by
construction, no parsing heuristics. Streaming is used because inputs run to hundreds of
thousands of tokens. Requires ANTHROPIC_API_KEY (or an `ant auth login` profile).
"""
import json

import anthropic

# The scorecard's quantitative inputs, exactly the fields system/scorecard.py derives from.
FIELDS = {
    "revenue": "total revenue, most recent full fiscal year",
    "operating_income": "operating income, same fiscal year",
    "d_and_a": "depreciation and amortisation (cash-flow statement)",
    "capex": "capital expenditures",
    "interest": "gross interest expense incl. finance-lease interest where split out; if only net interest is disclosed, use it and say so in notes",
    "cash": "cash and cash equivalents at fiscal year end",
    "dividends": "dividends paid (cash-flow statement); 0 if none",
    "cfo": "net cash provided by operating activities",
    "wc_swing": "sum of working-capital change lines inside operating cash flow (sign as reported: negative if working capital consumed cash)",
    "debt": "Moody's-adjusted total debt: short-term debt + current portion + long-term debt + finance-lease liabilities (current and noncurrent) + operating-lease liabilities (current and noncurrent) + financing obligations",
}
GRADES = ["Aaa", "Aa", "A", "Baa", "Ba", "B", "Caa", "Ca"]
NOTCHES = ["Aaa", "Aa1", "Aa2", "Aa3", "A1", "A2", "A3", "Baa1", "Baa2", "Baa3",
           "Ba1", "Ba2", "Ba3", "B1", "B2", "B3", "Caa1", "Caa2", "Caa3", "Ca", "C"]

SCHEMA = {
    "type": "object",
    "properties": {
        "fiscal_year_label": {"type": "string"},
        "figures_usd_m": {
            "type": "object",
            "properties": {k: {"type": "number", "description": v} for k, v in FIELDS.items()},
            "required": list(FIELDS), "additionalProperties": False,
        },
        "figure_notes": {"type": "string",
                         "description": "which lines were summed for debt/interest/wc_swing, any judgement calls"},
        "qualitative": {
            "type": "object",
            "properties": {
                "Market Characteristics": {"type": "string", "enum": GRADES},
                "Market Position": {"type": "string", "enum": GRADES},
                "Revenue and Earnings Stability": {"type": "string", "enum": GRADES},
                "Financial Policy": {"type": "string", "enum": GRADES},
            },
            "required": ["Market Characteristics", "Market Position",
                         "Revenue and Earnings Stability", "Financial Policy"],
            "additionalProperties": False,
        },
        "qualitative_rationale": {"type": "string", "description": "one sentence per factor"},
        "direct_rating": {"type": "string", "enum": NOTCHES,
                          "description": "your own overall rating judgement for this issuer, independent of the scorecard arithmetic"},
        "direct_rationale": {"type": "string"},
    },
    "required": ["fiscal_year_label", "figures_usd_m", "figure_notes", "qualitative",
                 "qualitative_rationale", "direct_rating", "direct_rationale"],
    "additionalProperties": False,
}

SYSTEM = """You are a credit analyst applying Moody's Retail and Apparel rating methodology
(September 2025) to SEC filings. From the filings provided, produce the scorecard inputs.

Quantitative: report the ten figures in USD millions for the most recent full fiscal year in
the documents (translate at a disclosed or reasonable rate if reporting currency differs).
Follow Moody's standard adjustments: debt is lease-adjusted (include operating-lease
liabilities and financing obligations), EBITDA will be computed as operating income plus D&A,
FFO as cash from operations minus the working-capital swing, RCF as FFO minus dividends.

Qualitative, graded Aaa/Aa/A/Baa/Ba/B/Caa/Ca per the methodology's factor descriptions:
- Market Characteristics: scale, stability and growth of the segments the issuer sells into,
  cyclicality of its demand, exposure to discretionary spending and disruption.
- Market Position: strength versus competitors, share trajectory, brand strength, pricing
  power, moat against e-commerce and discounters.
- Revenue and Earnings Stability: track record and expected volatility of revenue and margins
  through cycles; secular decline grades low even if currently profitable.
- Financial Policy: management and ownership's appetite for leverage, buybacks, dividends and
  M&A versus creditor protection; PE ownership or large debt-funded returns grade low.

Rules: use only the documents provided. Do not use any recollection of this company's actual
credit ratings or of rating agency reports; if rating fragments survive in the text, ignore
them. Where a figure is not directly disclosed, derive it from what is disclosed and explain
in figure_notes rather than guessing round numbers."""


def analyze(documents, rating_path=None, model="claude-opus-5", effort=None, client=None):
    """documents: [(name, text)]. rating_path: list of (date, rating, action) or None (Task A).

    Returns (parsed dict, meta dict). No tools array on purpose."""
    client = client or anthropic.Anthropic()
    parts = []
    for name, text in documents:
        parts.append(f"<document name=\"{name}\">\n{text}\n</document>")
    if rating_path:
        hist = "\n".join(f"  {d}  {r}  ({a})" for d, r, a in rating_path)
        parts.append("<rating_history note=\"the issuer's Moody's rating history up to the "
                     "start of the observation quarter; the task is to judge whether the "
                     "fundamentals in the documents justify keeping or changing the last "
                     f"rating\">\n{hist}\n</rating_history>")
    parts.append("Produce the scorecard inputs as specified.")
    output_config = {"format": {"type": "json_schema", "schema": SCHEMA}}
    if effort:
        output_config["effort"] = effort
    with client.messages.stream(
        model=model,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": "\n\n".join(parts)}],
        output_config=output_config,
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"model refused: {msg.stop_details}")
    text = next(b.text for b in msg.content if b.type == "text")
    meta = {"model": msg.model, "stop_reason": msg.stop_reason,
            "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens,
            "effort": effort}
    return json.loads(text), meta
