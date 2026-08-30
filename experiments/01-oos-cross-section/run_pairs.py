"""
Paired variant-A/variant-B document runs for experiment 01 (README.md §4, decisions D1-D5).

Per (model, observation): one shared redacted post-cutoff filing as a cached prefix, then
  A - extract-then-score: the model proposes scorecard inputs, system/scorecard.py computes
      the rating deterministically;
  B - direct rating: the model gets the same document plus the issuer's rating path up to
      the embargoed file end (Aug 2025) and an XBRL peer table, and rates directly.
Same system prompt for both so the document prefix cache carries from A to B (cache write
1.25x on A, cache read 0.1x on B). No tools array. Hard budget guard: aborts before any
call that would push total experiment spend past the cap.

Run: python3 experiments/01-oos-cross-section/run_pairs.py
"""
import json
import os
import sys

import anthropic

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "system"))
sys.path.insert(0, os.path.join(ROOT, "evaluation", "pipeline"))
import analyst        # noqa: E402  (SCHEMA for variant A)
import peer_table     # noqa: E402
import redact         # noqa: E402
import run_eval       # noqa: E402  (ensure_doc, to_text)
import scorecard      # noqa: E402

CAND = json.load(open(os.path.join(HERE, "candidates.json")))
CAP_USD = 4.60
ALREADY = 0.26  # probes
PRICE_IN, PRICE_OUT, PRICE_CW, PRICE_CR = 5 / 1e6, 25 / 1e6, 6.25 / 1e6, 0.5 / 1e6

SYSTEM = ("You are a credit analyst working with Moody's Retail and Apparel rating "
          "methodology (September 2025). Use only the material provided in this "
          "conversation; ignore any recollections about this company's current ratings.")

B_SCHEMA = {"type": "object", "properties": {
    "rating": {"type": "string", "enum": analyst.NOTCHES},
    "vs_last_known": {"type": "string", "enum": ["upgrade", "unchanged", "downgrade"],
                      "description": "your rating relative to the last rating in the provided history"},
    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    "key_drivers": {"type": "string"}},
    "required": ["rating", "vs_last_known", "confidence", "key_drivers"],
    "additionalProperties": False}

A_TASK = ("TASK A: From the document above, produce the scorecard inputs as JSON per the "
          "schema. Figures in USD millions. Prefer the most recent FULL fiscal year the "
          "document contains (a 10-K's current year, or the prior-year comparatives in a "
          "10-Q); state in figure_notes which period you used and any derivations. "
          "Qualitative grades per the methodology factors: Market Characteristics, Market "
          "Position, Revenue and Earnings Stability, Financial Policy (Aaa/Aa/A/Baa/Ba/B/"
          "Caa/Ca). Also give direct_rating as your own overall judgement.")


def b_task(path, peers):
    hist = "\n".join(f"  {d}  {r}  ({a})" for d, r, a in path)
    return (f"TASK B: Determine the issuer's current Moody's-style long-term rating as of "
            f"{CAND['as_of']}, using the document above, the rating history below (complete "
            "through August 2025; anything later is unknown to us), and the peer table. "
            "Judge whether fundamentals justify keeping or changing the last known rating.\n\n"
            f"<rating_history>\n{hist}\n</rating_history>\n\n<peer_table>\n{peers}\n</peer_table>")


def call(client, model, sys_prompt, blocks, schema, effort=None):
    kw = dict(model=model, max_tokens=8000, system=sys_prompt,
              messages=[{"role": "user", "content": blocks}],
              output_config={"format": {"type": "json_schema", "schema": schema}})
    if effort:
        kw["output_config"]["effort"] = effort
    try:
        with client.messages.stream(**kw) as s:
            m = s.get_final_message()
    except anthropic.BadRequestError:
        kw.pop("output_config", None)
        kw["system"] = sys_prompt + " Reply ONLY with a JSON object matching the requested fields."
        with client.messages.stream(**kw) as s:
            m = s.get_final_message()
    text = next(b.text for b in m.content if b.type == "text")
    parsed = json.loads(text[text.index("{"):text.rindex("}") + 1])
    ud = m.usage.model_dump() if hasattr(m.usage, "model_dump") else dict(m.usage)
    cw = ud.get("cache_creation_input_tokens") or 0
    cr = ud.get("cache_read_input_tokens") or 0
    cost = (ud["input_tokens"] * PRICE_IN + ud["output_tokens"] * PRICE_OUT
            + cw * PRICE_CW + cr * PRICE_CR)
    return parsed, {"in": ud["input_tokens"], "out": ud["output_tokens"],
                    "cache_write": cw, "cache_read": cr, "cost_usd": round(cost, 4),
                    "usage_raw": ud}


def main():
    client = anthropic.Anthropic()
    outdir = os.path.join(HERE, "runs", "paired")
    os.makedirs(outdir, exist_ok=True)
    spent = ALREADY
    results = []
    for model, obs_map in CAND["paired_runs"].items():
        for slug, (form, filed) in obs_map.items():
            c = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "company.json")))
            manifest = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug,
                                                   "filings", "manifest.json")))["filings"]
            f = next(x for x in manifest if x["form"] == form and x["filingDate"] == filed)
            path, _ = run_eval.ensure_doc(slug, c["cik"], f)
            clean, removed = redact.redact(run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore")))
            doc_block = {"type": "text",
                         "text": f"<document name=\"{form} filed {filed}\">\n{clean}\n</document>",
                         "cache_control": {"type": "ephemeral"}}
            # free preflight against the budget guard
            ct = client.messages.count_tokens(model=model, system=SYSTEM,
                                              messages=[{"role": "user", "content": [
                                                  {"type": "text", "text": doc_block["text"]},
                                                  {"type": "text", "text": A_TASK}]}])
            projected = ct.input_tokens * (PRICE_CW + PRICE_IN) + 2 * 5000 * PRICE_OUT  # worst case: B misses cache
            if spent + projected > CAP_USD:
                print(f"  BUDGET-STOP vor {model} {slug}: {spent:.2f} + ~{projected:.2f} > {CAP_USD}")
                break

            cand = CAND["candidates"][slug]
            parsed_a, ua = call(client, model, SYSTEM,
                                [doc_block, {"type": "text", "text": A_TASK}], analyst.SCHEMA)
            fig = dict(parsed_a["figures_usd_m"]); fig["qualitative"] = parsed_a["qualitative"]
            fig["label"] = f"{slug} expA"
            rows = scorecard.build(fig); agg = scorecard.aggregate(rows)
            pred_a = scorecard.outcome(agg)

            obs = json.load(open(os.path.join(ROOT, "evaluation", "companies", slug, "observations.json")))
            rp = [(e[0], e[1], e[2]) for e in obs["observations"][-1]["rating_path"]]
            peers = peer_table.build(CAND["as_of"], exclude_slug=slug) or "(peer table unavailable)"
            parsed_b, ub = call(client, model, SYSTEM,
                                [doc_block, {"type": "text", "text": b_task(rp, peers)}], B_SCHEMA)

            spent += ua["cost_usd"] + ub["cost_usd"]
            r = {"model": model, "slug": slug, "doc": f"{form} {filed}",
                 "label": cand["label"], "persistence": cand["persistence_at_cutoff"],
                 "changed": cand["changed_vs_aug2025_file"],
                 "A": {"extraction": parsed_a, "scorecard_aggregate": round(agg, 3),
                       "pred": pred_a, "direct_in_A": parsed_a["direct_rating"], "usage": ua},
                 "B": {"pred": parsed_b["rating"], "vs_last_known": parsed_b["vs_last_known"],
                       "confidence": parsed_b["confidence"], "drivers": parsed_b["key_drivers"],
                       "usage": ub},
                 "redacted_lines": len(removed)}
            results.append(r)
            json.dump(results, open(os.path.join(outdir, "results.json"), "w"),
                      indent=1, ensure_ascii=False)
            print(f"  {model.split('-2')[0]:<18} {slug:<22} label {r['label']:<5} "
                  f"A={pred_a:<5} B={parsed_b['rating']:<5} pers={r['persistence']:<5} "
                  f"(${ua['cost_usd'] + ub['cost_usd']:.2f}, cacheB={ub['cache_read']})", flush=True)
    print(f"\nGesamtausgaben Experiment (inkl. Probes): ${spent:.2f} / Cap {CAP_USD}")


if __name__ == "__main__":
    main()
