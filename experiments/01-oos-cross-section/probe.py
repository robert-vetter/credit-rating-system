"""
Contamination probes: what does the model claim to know from memory alone?

Part of experiment 01 (see README.md §4). One request per (model, company), BEFORE any
document run and sharing no context with them. The model is asked, from memory only, for
(1) the company's current Moody's rating as of the as-of date, (2) specific Moody's-adjusted
metrics, (3) a post-cutoff fact (latest fiscal-year revenue). Design: Robert, 2026-08-30.

Classification (per decisions.md D4): an observation is CONTAMINATED if the probe reproduces
post-cutoff specifics correctly (auto-graded against XBRL where a reference exists, else
hand-graded from the stored transcript). A correct rating claim alone is a prior, not
knowledge - ratings are inert. Everything is stored verbatim in runs/probes/.

Run: python3 experiments/01-oos-cross-section/probe.py
"""
import json
import os
import sys

import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CAND = json.load(open(os.path.join(HERE, "candidates.json")))

SCHEMA = {"type": "object", "properties": {
    "knows_company": {"type": "boolean"},
    "claimed_moodys_rating": {"type": ["string", "null"],
        "description": "the company's current Moody's long-term rating as of the as-of date, from memory; null if unsure"},
    "rating_confidence": {"type": "string", "enum": ["high", "medium", "low", "none"]},
    "claimed_debt_ebitda": {"type": ["number", "null"],
        "description": "Moody's-adjusted debt/EBITDA you recall for this issuer, latest known; null if unknown"},
    "claimed_latest_fy_revenue_usd_bn": {"type": ["number", "null"],
        "description": "the most recent full-fiscal-year total revenue you know, in USD billions"},
    "claimed_fy_end": {"type": ["string", "null"], "description": "that fiscal year's end date, YYYY-MM"},
    "claimed_recent_rating_actions": {"type": "string",
        "description": "any Moody's rating actions on this issuer since mid-2025 that you recall, or 'none known'"},
    "notes": {"type": "string"}},
    "required": ["knows_company", "claimed_moodys_rating", "rating_confidence",
                 "claimed_debt_ebitda", "claimed_latest_fy_revenue_usd_bn", "claimed_fy_end",
                 "claimed_recent_rating_actions", "notes"], "additionalProperties": False}

SYSTEM = ("You are being probed for what you know FROM MEMORY about a company's credit "
          "profile. Answer strictly from your training knowledge. Do not guess plausible "
          "values: if you do not specifically recall a number or rating, return null and say "
          "so. Honest 'I don't know' answers are the desired behavior here.")


def main():
    client = anthropic.Anthropic()
    outdir = os.path.join(HERE, "runs", "probes")
    os.makedirs(outdir, exist_ok=True)
    spent_in = spent_out = 0
    for model, mcfg in CAND["models"].items():
        results = {}
        for slug in mcfg["probe_companies"]:
            group = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "company.json")))
            q = (f"As of {CAND['as_of']}: {group['edgar_name']} (US retailer, ticker-level "
                 f"parent of the {group['group']} group). What is its current Moody's "
                 "long-term credit rating, what Moody's-adjusted metrics do you recall, what "
                 "was its most recent full fiscal year's revenue and when did that fiscal "
                 "year end, and what Moody's rating actions on it since mid-2025 do you know?")
            kw = dict(model=model, max_tokens=1500, system=SYSTEM,
                      messages=[{"role": "user", "content": q}],
                      output_config={"format": {"type": "json_schema", "schema": SCHEMA}})
            if model == "claude-opus-5":
                kw["output_config"]["effort"] = "low"
            try:
                r = client.messages.create(**kw)
            except anthropic.BadRequestError:
                kw.pop("output_config")
                kw["system"] += " Reply ONLY with a JSON object with keys: " + ", ".join(SCHEMA["required"])
                r = client.messages.create(**kw)
            text = next(b.text for b in r.content if b.type == "text")
            try:
                parsed = json.loads(text[text.index("{"):text.rindex("}") + 1])
            except Exception:
                parsed = {"parse_error": text[:500]}
            spent_in += r.usage.input_tokens; spent_out += r.usage.output_tokens
            results[slug] = {"raw": parsed, "usage": {"in": r.usage.input_tokens, "out": r.usage.output_tokens}}
            cl = parsed.get("claimed_moodys_rating"); rv = parsed.get("claimed_latest_fy_revenue_usd_bn")
            print(f"  {model.split('-2')[0]:<18} {slug:<24} rating={cl} conf={parsed.get('rating_confidence')} "
                  f"rev={rv} actions='{str(parsed.get('claimed_recent_rating_actions'))[:40]}'", flush=True)
        json.dump(results, open(os.path.join(outdir, f"{model}.json"), "w"), indent=1, ensure_ascii=False)
    cost = spent_in * 5 / 1e6 + spent_out * 25 / 1e6
    print(f"\nProbes: {spent_in:,} in / {spent_out:,} out  ~= ${cost:.2f}")


if __name__ == "__main__":
    main()
