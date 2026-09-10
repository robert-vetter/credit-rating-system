"""
Pre-flight for Experiment 03: one tiny real request with EXACTLY the batch's parameter set
(claude-opus-4-6, adaptive thinking, effort high, JSON-schema output, no tools). Costs a few
cents; proves the parameter combination is accepted and the response parses before the batch
is submitted. Also confirms the account has credit (the API refuses even free endpoints when
the balance is exhausted).

Run: python3 experiments/03-oos-values-first/preflight.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "system"))
import run_batch as rb  # noqa: E402

MINI = ("MINIATURE TEST FILING, Retail Co. FY ended 2026-01-31, USD millions: revenue 1,000; "
        "operating income 80; D&A 40; capex 30; gross interest 20; cash 50; dividends 10; CFO 110; "
        "working-capital change +5; long-term debt 300; finance leases 20; operating leases 80. "
        "Mid-size apparel retailer, stable position.")


def main():
    client = rb.make_client()
    body = [{"type": "text", "text": f'<document name="test">{MINI}</document>'},
            {"type": "text", "text": "<history_pack>rating history: 2023-05-01 Ba2 (NW); => rating in effect "
                                     "at the end of the available history (2025-08-28): Ba2</history_pack>"},
            {"type": "text", "text": f"As-of date: {rb.AS_OF}.\n\n{rb.TASK}"}]
    with client.messages.stream(model=rb.MODEL, max_tokens=rb.VF_MAX_TOKENS, system=rb.SYSTEM,
                                thinking={"type": "adaptive"},
                                messages=[{"role": "user", "content": body}],
                                output_config={"format": {"type": "json_schema", "schema": rb.SCHEMA},
                                               "effort": "high"}) as st:
        m = st.get_final_message()
    text = next(b.text for b in m.content if b.type == "text")
    parsed = json.loads(text[text.index("{"):text.rindex("}") + 1])
    u = m.usage.model_dump()
    ok = set(parsed["figures_usd_m"]) == set(rb.SCHEMA["properties"]["figures_usd_m"]["properties"])
    print(f"PRE-FLIGHT OK: model={m.model} stop={m.stop_reason} in={u['input_tokens']} out={u['output_tokens']} "
          f"figures_complete={ok} direct={parsed['direct_rating']} vs_last_known={parsed['vs_last_known']} "
          f"cost~${(u['input_tokens'] * 5 + u['output_tokens'] * 25) / 1e6:.3f}")
    json.dump({"model": m.model, "stop_reason": m.stop_reason, "usage": u, "parsed": parsed},
              open(os.path.join(HERE, "runs", "preflight.json"), "w"), indent=1)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
    main()
