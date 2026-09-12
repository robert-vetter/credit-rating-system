"""Exact Qwen token counts of the Experiment 03 package for all 20 candidates, offline.

Purpose: the evidence behind RUN-SPEC.md section 4 (package sizes, the trim rule, per-document
sizes for the truncation check). No API call, no download: every document is read from the
local cache under evaluation/companies/<slug>/filings/ and the tokenizer from the Hugging Face
cache (HF_HUB_OFFLINE is set below).

Inputs: experiments/03-oos-values-first/candidates.json and prompts/, evaluation/companies/,
the Qwen/Qwen3-235B-A22B-Instruct-2507 tokenizer (transformers).
Output: evidence/qwen-token-counts-2026-09-12.json next to this script: the fixed overhead
(system prompt, task, schema, chat template) and one record per candidate with total,
document and pack tokens, per-document tokens, and, where the package exceeds the limit, the
trimmed variant after dropping the oldest 10-Q (RUN-SPEC.md section 4, decision D9).

Run from the repository root: python3 experiments/04-open-weight-cross-section/count_tokens_qwen.py
"""
import json
import os
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ROOT + "/system", ROOT + "/evaluation/pipeline", ROOT + "/experiments/03-oos-values-first"]
import history_pack, redact, run_eval  # noqa: E402,E401
import transformers  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

B, ASOF, HEND = "2025-09-30", "2026-08-29", "2025-08-28"
CONTEXT, MAX_OUT = 262144, 8192
LIMIT = CONTEXT - MAX_OUT           # 253,952
E03 = ROOT + "/experiments/03-oos-values-first"
OUT = os.path.join(HERE, "evidence", "qwen-token-counts-2026-09-12.json")
SYSTEM = open(E03 + "/prompts/system.txt").read().strip()
TASK = open(E03 + "/prompts/task_values_first.txt").read().strip()
SCHEMA = json.load(open(E03 + "/prompts/schema_values_first.json"))
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-235B-A22B-Instruct-2507")


def n(s):
    return len(tok(s, add_special_tokens=False)["input_ids"])


def pick(manifest):
    """Experiment 03 rule (run_batch.pick_documents): latest 10-K after B, then every later 10-Q up to as_of."""
    post = [f for f in manifest if B < f["filingDate"] <= ASOF and f["form"] in ("10-K", "10-Q")]
    ks = sorted([f for f in post if f["form"] == "10-K"], key=lambda f: f["filingDate"])
    if not ks:
        return []
    k = ks[-1]
    return [k] + sorted([f for f in post if f["form"] == "10-Q" and f["filingDate"] > k["filingDate"]],
                        key=lambda f: f["filingDate"])


def assemble(docs_text, pack):
    return SYSTEM + docs_text + pack + f"As-of date: {ASOF}.\n\n{TASK}" + json.dumps(SCHEMA)


template = tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": "X"}],
                                   tokenize=False, add_generation_prompt=True)
overhead = {"system": n(SYSTEM), "task": n(TASK), "schema_json_dumps": n(json.dumps(SCHEMA)),
            "chat_template": n(template) - n(SYSTEM) - n("X")}
out = []
for it in json.load(open(E03 + "/candidates.json"))["items"]:
    slug = it["slug"]
    cdir = f"{ROOT}/evaluation/companies/{slug}"
    c = json.load(open(cdir + "/company.json"))
    manifest = json.load(open(cdir + "/filings/manifest.json"))["filings"]
    per_doc = []
    for f in pick(manifest):
        path, fn = run_eval.ensure_doc(slug, c["cik"], f)
        clean, removed = redact.redact(run_eval.to_text(open(path, "rb").read().decode("utf-8", "ignore")))
        text = f'<document name="{f["form"]} filed {f["filingDate"]}">\n{clean}\n</document>\n'
        per_doc.append({"form": f["form"], "filed": f["filingDate"], "file": fn, "tokens": n(text),
                        "redacted_lines": len(removed), "text": text})
    pack, plog = history_pack.build(slug, ASOF, history_end=HEND)
    docs_text = "".join(d["text"] for d in per_doc)
    total = n(assemble(docs_text, pack))
    rec = {"id": it["id"], "slug": slug, "in_run": it.get("in_run"), "changed": it["changed"],
           "label": it["label"], "persistence": it["persistence"],
           "docs": [f"{d['form']} {d['filed']}" for d in per_doc],
           "docs_tokens": [{k: d[k] for k in ("form", "filed", "file", "tokens", "redacted_lines")} for d in per_doc],
           "redacted_lines": sum(d["redacted_lines"] for d in per_doc),
           "qwen_tokens_total": total, "qwen_tokens_docs": n(docs_text), "qwen_tokens_pack": n(pack),
           "quarterly_rows": plog.get("quarterly_rows"), "limit": LIMIT, "fits": total <= LIMIT, "trimmed": False}
    if total > LIMIT:
        qs = [d for d in per_doc if d["form"] == "10-Q"]
        if qs:
            drop = min(qs, key=lambda d: d["filed"])
            kept = [d for d in per_doc if d is not drop]
            t2 = n(assemble("".join(d["text"] for d in kept), pack))
            rec.update({"trimmed": True, "dropped_doc": f"{drop['form']} {drop['filed']}",
                        "docs_used": [f"{d['form']} {d['filed']}" for d in kept],
                        "qwen_tokens_total_trimmed": t2, "fits_after_trim": t2 <= LIMIT})
    out.append(rec)
    status = "FITS" if rec["fits"] else f"OVER, {rec.get('qwen_tokens_total_trimmed')} after dropping {rec.get('dropped_doc')}"
    sizes = ", ".join(f"{d['form']} {d['filed']} {d['tokens']:,}" for d in per_doc)
    print(f"{it['id']} {slug:<24} {total:>8,} tokens ({rec['qwen_tokens_docs']:,} docs + {rec['qwen_tokens_pack']:,} pack) "
          f"{status}  [{sizes}]", flush=True)

json.dump({"generated": "2026-09-12", "tokenizer": "Qwen/Qwen3-235B-A22B-Instruct-2507",
           "transformers": transformers.__version__, "boundary_B": B, "as_of": ASOF, "history_end": HEND,
           "context": CONTEXT, "max_tokens_out": MAX_OUT, "limit": LIMIT,
           "counted": "system + documents + history pack + as-of line + task + json.dumps(schema), "
                      "add_special_tokens=False, without the chat template",
           "fixed_overhead_tokens": overhead, "items": out}, open(OUT, "w"), indent=1)
tot = sum(r.get("qwen_tokens_total_trimmed", r["qwen_tokens_total"]) for r in out)
print(f"\n20 packages after trim: {tot:,} tokens; over {LIMIT:,} before trim: {[r['id'] for r in out if not r['fits']]}")
print("smallest single document:", min((d["tokens"], r["id"], d["form"], d["filed"]) for r in out for d in r["docs_tokens"]))
print("fixed overhead:", overhead)
print("written:", OUT)
