"""Exact Qwen token count of the Exp 03 package for all 20 candidates. Offline, no API."""
import json, os, sys
ROOT='/Users/robert/Developer/giesecke/credit-rating-system'
sys.path[:0]=[ROOT+'/system', ROOT+'/evaluation/pipeline', ROOT+'/experiments/03-oos-values-first']
import history_pack, redact, run_eval
from transformers import AutoTokenizer
B='2025-09-30'; ASOF='2026-08-29'; HEND='2025-08-28'
HERE=ROOT+'/experiments/03-oos-values-first'
SYSTEM=open(HERE+'/prompts/system.txt').read().strip()
TASK=open(HERE+'/prompts/task_values_first.txt').read().strip()
SCHEMA=json.load(open(HERE+'/prompts/schema_values_first.json'))
tok=AutoTokenizer.from_pretrained("Qwen/Qwen3-235B-A22B-Instruct-2507")
cand=json.load(open(HERE+'/candidates.json'))
out=[]
for it in cand['items']:
    slug=it['slug']; cdir=f"{ROOT}/evaluation/companies/{slug}"
    c=json.load(open(cdir+'/company.json'))
    man=json.load(open(cdir+'/filings/manifest.json'))['filings']
    post=[f for f in man if B<f['filingDate']<=ASOF and f['form'] in ('10-K','10-Q')]
    ks=sorted([f for f in post if f['form']=='10-K'], key=lambda f:f['filingDate'])
    chosen=([ks[-1]]+sorted([f for f in post if f['form']=='10-Q' and f['filingDate']>ks[-1]['filingDate']], key=lambda f:f['filingDate'])) if ks else []
    docs=''; meta=[]; red=0
    for f in chosen:
        path, fn = run_eval.ensure_doc(slug, c['cik'], f)
        clean, removed = redact.redact(run_eval.to_text(open(path,'rb').read().decode('utf-8','ignore')))
        docs += f'<document name="{f["form"]} filed {f["filingDate"]}">\n{clean}\n</document>\n'
        meta.append(f"{f['form']} {f['filingDate']}"); red+=len(removed)
    pack, plog = history_pack.build(slug, ASOF, history_end=HEND)
    full = SYSTEM + docs + pack + f"As-of date: {ASOF}.\n\n{TASK}" + json.dumps(SCHEMA)
    n=len(tok(full, add_special_tokens=False)['input_ids'])
    nd=len(tok(docs, add_special_tokens=False)['input_ids'])
    np_=len(tok(pack, add_special_tokens=False)['input_ids'])
    out.append({'id':it['id'],'slug':slug,'in_run':it.get('in_run'),'changed':it['changed'],
                'label':it['label'],'persistence':it['persistence'],'docs':meta,'redacted_lines':red,
                'qwen_tokens_total':n,'qwen_tokens_docs':nd,'qwen_tokens_pack':np_,
                'quarterly_rows':plog.get('quarterly_rows')})
    print(f"{it['id']} {slug:<24} {n:>8,} tokens ({nd:,} docs + {np_:,} pack) {'FITS' if n<=253952 else 'OVER'}  {', '.join(meta)}", flush=True)
json.dump(out, open('/private/tmp/claude-502/-Users-robert-Developer-giesecke/6fda2814-dd91-4940-a9a7-d49a1e0dd1fc/scratchpad/qwen_counts.json','w'), indent=1)
tot=sum(r['qwen_tokens_total'] for r in out)
print(f"\n20 packages: total {tot:,} tokens; over 253,952: {[r['id'] for r in out if r['qwen_tokens_total']>253952]}")
print(f"cost at $0.09/M in + 6k out at $0.35/M: ${tot/1e6*0.09 + 20*6000/1e6*0.35:.2f} for one pass over 20")
