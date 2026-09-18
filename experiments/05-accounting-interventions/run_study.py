"""Offline fixed-grade accounting interventions on nine saved current-arm responses.

OpenAI Codex, directed by Robert Vetter, 2026-09-17.
Reads frozen protocol, raw responses, original input audits and local filing evidence.
Default: verify and print. --out creates a fresh ignored directory, never overwrites.
No network/model calls; interpretations are pending human accounting review.
"""
import argparse
import copy
from decimal import Decimal
from html import unescape
import json
import math
from pathlib import Path
import re
import statistics
import sys

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "system"))
from evidence_ledger import FilingIndex, digest
from scorecard import derive, build, aggregate, outcome

RATINGS = ['Aaa','Aa1','Aa2','Aa3','A1','A2','A3','Baa1','Baa2','Baa3','Ba1','Ba2','Ba3','B1','B2','B3','Caa1','Caa2','Caa3','Ca','C']
FIELDS = {'revenue','operating_income','d_and_a','capex','interest','cash','dividends','cfo','wc_swing','debt'}
QUAL = {'Market Characteristics','Market Position','Revenue and Earnings Stability','Financial Policy'}
CONDITIONS = ('original','interest','debt','other','combined')


def load(path):
    return json.loads(path.read_text())


def score(figures, qualitative):
    if set(figures) != FIELDS or any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in figures.values()):
        raise ValueError('Invalid numeric vector')
    c = {**figures, 'qualitative': copy.deepcopy(qualitative)}
    metrics = derive(c)
    factors = [{'name': n, 'weight': w, 'score': s, 'weighted': w*s} for n,w,s in build(c)]
    total = aggregate([(x['name'],x['weight'],x['score']) for x in factors])
    return {'metrics': metrics, 'factors': factors, 'aggregate': total, 'rating': outcome(total),
            'qualitative_contribution': sum(x['weighted'] for x in factors if x['name'] in QUAL),
            'quantitative_contribution': sum(x['weighted'] for x in factors if x['name'] not in QUAL)}


def validate_patches(case, ownership):
    seen = set()
    for p in case['patches']:
        if p['field'] in seen or p['group'] not in ownership or p['field'] not in ownership[p['group']]:
            raise ValueError('Conflicting or unauthorized patch field')
        seen.add(p['field'])
        if p['operation'] not in ('replace','floor') or (p['operation']=='floor' and p['field']!='debt'):
            raise ValueError('Unsupported patch operation')
        if isinstance(p['value_usd_m'],bool) or not isinstance(p['value_usd_m'],(int,float)) or not math.isfinite(p['value_usd_m']):
            raise ValueError('Invalid patch value')
        if not p['operands'] or not p['quotes'] or not p['rationale']:
            raise ValueError('Unsupported patch without evidence')
        value=sum((Decimal(str(x['value_usd_m']))*Decimal(str(x['coefficient'])) for x in p['operands']),Decimal(0))
        if value != Decimal(str(p['value_usd_m'])):
            raise ValueError('Operand sum does not reproduce proposed value')


def verify_source(root, run, case, as_of):
    source=case['source']; path=root/source['path']
    if digest(path.read_bytes()) != source['sha256']:
        raise ValueError('Filing hash mismatch')
    audit=load(run/f"audit/current/{case['id']}.json")
    docs=[d for d in audit['documents'] if d['accession']==source['accession']]
    if len(docs)!=1 or docs[0]['filed']!=source['filed'] or docs[0]['source_sha256']!=source['sha256'] or docs[0]['form']!=source['form']:
        raise ValueError('Source not the original supplied filing')
    from datetime import date
    start,end,filed,boundary=map(date.fromisoformat,(case['start'],case['end'],source['filed'],as_of))
    if not start<=end<=filed<=boundary:
        raise ValueError('Invalid evidence dates')
    text=path.read_text(); index=FilingIndex(text)
    normalized=re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',text)))
    checked=[]
    for patch in case['patches']:
        quotes=[]
        for quote in patch['quotes']:
            offset=normalized.find(quote)
            if offset<0: raise ValueError(f"Missing quoted evidence: {case['id']} {patch['field']}")
            quotes.append({'quote':quote,'normalized_text_offset':offset,'normalization':'strip tags; HTML-unescape; collapse whitespace'})
        facts=[]
        for operand in patch['operands']:
            ns,tag=operand['tag'].split(':',1)
            instant=patch['field']=='debt'
            record={'namespace':ns,'tag':tag,'start':None if instant else case['start'],'end':case['end'],
                    'cik':case['cik'],'val':float(Decimal(str(operand['value_usd_m']))*1000000)}
            match=index.locate(record,source)
            if match['status']!='matched_inline_fact' or not any(m['element_id']==operand['element_id'] and m['context_ref']==operand['context'] for m in match['matches']):
                raise ValueError(f"Operand not supported by exact element/context/value: {operand}")
            facts.append({**operand,'locator':match})
        checked.append({'field':patch['field'],'operation':patch['operation'],'quotes':quotes,'operands':facts,
                        'rationale':patch['rationale'],'review_status':'pending_human_review'})
    return checked


def verify_original_period(obj, case):
    """Check the declared annual period; disclose weaker year-only alignment."""
    text=obj['fiscal_year_label']+' '+obj['figure_notes']
    explicit=re.findall(r'\b\d{4}-\d{2}-\d{2}\b',obj['fiscal_year_label'])
    if explicit and set(explicit)!={case['end']}:
        raise ValueError('Original response fiscal period is incompatible')
    from datetime import date
    natural=date.fromisoformat(case['end']).strftime('%B %d, %Y').replace(' 0',' ')
    exact_end=case['end'] in text or natural in text
    fiscal_year=re.fullmatch(r'FY\s*(\d{4})',obj['fiscal_year_label'].strip())
    year_matches=fiscal_year is not None and fiscal_year.group(1)==case['end'][:4]
    if (not exact_end and not year_matches) or re.search(r'\b(TTM|trailing twelve|trailing 12)\b',text,re.I):
        raise ValueError('Original annual fiscal period is not established')
    return {'start':case['start'],'end':case['end'],'fiscal_year_label':obj['fiscal_year_label'],
            'basis':('Exact fiscal end in original label/notes.' if exact_end else 'Year-only original FY label aligned to this study case annual anchor; weaker than explicit date.'),
            'limitation':'Annual task and source duration agree; does not independently validate each original input period.'}


def bind_original_document(body, audit, case):
    docs=[d for d in audit['documents'] if d['accession']==case['source']['accession']]
    if len(docs)!=1:raise ValueError('Original input audit lacks source accession')
    d=docs[0];marker=f'<document name="{d["form"]} filed {d["filed"]}">'
    text=body['messages'][1]['content']
    if text.count(marker)!=1:raise ValueError('Original body lacks unique audited document block')
    start=text.index(marker)+len(marker);end=text.index('</document>',start)
    payload=text[start:end].strip('\n')
    if digest(payload.encode())!=d['redacted_text_sha256']:raise ValueError('Audited document is not the dispatched representation')
    return {'accession':d['accession'],'supplied_text_sha256':d['redacted_text_sha256']}


def load_baselines(root, run, spec):
    manifest=load(run/'manifest.json')
    ledger=[json.loads(l) for l in (run/'ledger.jsonl').read_text().splitlines() if l.strip()]
    gold={(x['slug'],x['date']) for x in load(root/'evaluation/goldset.json')['items']}
    records=[]
    for case in spec['cases']:
        if (case['slug'],spec['as_of']) in gold: raise ValueError('Gold observation excluded')
        for rep in (1,2,3):
            request=f"doc-current-{case['id']}-r{rep}"
            valid=[e for e in ledger if e['event']=='valid' and e.get('request_id')==request]
            if not valid: raise ValueError('Missing valid logical response')
            event=valid[-1]; attempt=event['attempt_id']
            body_path=run/f'bodies/{request}.json'; response_path=run/f'responses/{attempt}.json'
            dispatch=[e for e in ledger if e['event']=='dispatch' and e.get('attempt_id')==attempt]
            if len(dispatch)!=1 or dispatch[0]['body_sha256']!=digest(body_path.read_bytes()): raise ValueError('Dispatch/body mismatch')
            wrapper=load(response_path)
            if wrapper['attempt_id']!=attempt or wrapper['request_id']!=request or wrapper['status']!=200: raise ValueError('Response wrapper mismatch')
            api=json.loads(wrapper['body_utf8']); body=load(body_path)
            if api['choices'][0]['finish_reason']!='stop': raise ValueError('Incomplete response')
            obj=json.loads(api['choices'][0]['message']['content'])
            jsonschema.validate(obj,body['response_format']['json_schema']['schema'])
            period=verify_original_period(obj,case)
            audit_path=run/f"audit/current/{case['id']}.json"
            input_binding=bind_original_document(body,load(audit_path),case)
            baseline=score(obj['figures_usd_m'],obj['qualitative'])
            flat_path=run/f'results/results_current_r{rep}.json'
            flats=[x for x in load(flat_path) if x['id']==case['id']]
            if len(flats)!=1:raise ValueError('Missing/duplicate stored comparison')
            flat=flats[0]; label=manifest['cohort']['labels'][case['id']]
            if (flat['figures']!=obj['figures_usd_m'] or flat['qualitative']!=obj['qualitative'] or
                flat['aggregate']!=baseline['aggregate'] or flat['pred_scorecard']!=baseline['rating'] or
                event['aggregate']!=baseline['aggregate'] or event['pred_scorecard']!=baseline['rating'] or
                flat['pred_direct']!=obj['direct_rating'] or flat['label']!=label['label'] or flat['persistence']!=label['persistence']):
                raise ValueError('Baseline replay mismatch; stop without modifying old records')
            records.append({'id':case['id'],'slug':case['slug'],'replicate':rep,'request_id':request,
                            'attempt_id':attempt,'transport_attempts':[e['attempt_id'] for e in ledger if e['event']=='dispatch' and e.get('request_id')==request],
                            'figures':obj['figures_usd_m'],'qualitative':obj['qualitative'],'direct_rating':obj['direct_rating'],
                            'figure_notes':obj['figure_notes'],'label':label['label'],'persistence':label['persistence'],
                            'baseline':baseline,'original_period_check':period,'original_input_binding':input_binding,
                            'source_hashes':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (body_path,response_path,flat_path,audit_path)}})
    return records


def intervene(original, case, condition):
    figures=copy.deepcopy(original['figures']); qual=copy.deepcopy(original['qualitative'])
    selected=[] if condition=='original' else [p for p in case['patches'] if condition=='combined' or p['group']==condition]
    base={'id':original['id'],'slug':original['slug'],'replicate':original['replicate'],'condition':condition,
          'label':original['label'],'persistence':original['persistence'],'direct_rating_unchanged':original['direct_rating'],
          'qualitative':qual,'changes':[],'untouched_fields':sorted(FIELDS-{p['field'] for p in selected})}
    if condition!='original' and not selected:
        return {**base,'status':'not_estimable','reason':'No source-supported patch for this condition.'}
    for p in selected:
        before=figures[p['field']]; after=max(before,p['value_usd_m']) if p['operation']=='floor' else p['value_usd_m']
        figures[p['field']]=after
        base['changes'].append({'field':p['field'],'before':before,'after':after,'operation':p['operation'],'group':p['group']})
    try: result=score(figures,qual)
    except (ValueError,ZeroDivisionError) as exc:
        return {**base,'figures':figures,'status':'undefined_scorecard','reason':str(exc)}
    baseline=original['baseline']
    delta_factors={x['name']:x['weighted']-next(y['weighted'] for y in baseline['factors'] if y['name']==x['name']) for x in result['factors']}
    return {**base,'status':'scored','figures':figures,'result':result,
            'delta_aggregate':result['aggregate']-baseline['aggregate'],
            'delta_notches':RATINGS.index(result['rating'])-RATINGS.index(baseline['rating']),
            'delta_metrics':{k:v-baseline['metrics'][k] for k,v in result['metrics'].items()},
            'delta_weighted_factors':delta_factors,
            'absolute_error':abs(RATINGS.index(result['rating'])-RATINGS.index(original['label'])),
            'baseline_absolute_error':abs(RATINGS.index(baseline['rating'])-RATINGS.index(original['label'])),
            'persistence_absolute_error':abs(RATINGS.index(original['persistence'])-RATINGS.index(original['label']))}


def metrics(rows, field):
    errors=[r[field] for r in rows]
    return {'n':len(errors),'exact':sum(x==0 for x in errors),'mae':sum(errors)/len(errors) if errors else None}


def summarize(rows, cases):
    summaries=[]
    for condition in CONDITIONS:
        eligible=[r for r in rows if r['condition']==condition and r['status']=='scored']
        issuer=[]
        for case in cases:
            group=[r for r in eligible if r['id']==case['id']]
            if len(group)!=3:
                issuer.append({'id':case['id'],'status':'no_consensus','valid_replicates':len(group)})
                continue
            rating=RATINGS[int(statistics.median(RATINGS.index(r['result']['rating']) for r in group))]
            original_rating=RATINGS[int(statistics.median(RATINGS.index(r['result']['rating'])-r['delta_notches'] for r in group))]
            target=group[0]['label']; prior=group[0]['persistence']
            issuer.append({'id':case['id'],'status':'consensus','rating':rating,'baseline_rating':original_rating,
                           'label':target,'persistence':prior,'absolute_error':abs(RATINGS.index(rating)-RATINGS.index(target)),
                           'baseline_absolute_error':abs(RATINGS.index(original_rating)-RATINGS.index(target)),
                           'persistence_absolute_error':abs(RATINGS.index(prior)-RATINGS.index(target))})
        good=[x for x in issuer if x['status']=='consensus']
        summaries.append({'condition':condition,'planned_responses':len(cases)*3,
                          'replicate_metrics':{name:metrics(eligible,key) for name,key in [('intervention','absolute_error'),('matched_original','baseline_absolute_error'),('persistence','persistence_absolute_error')]},
                          'issuer_consensus':issuer,'issuer_metrics':{name:metrics(good,key) for name,key in [('intervention','absolute_error'),('matched_original','baseline_absolute_error'),('persistence','persistence_absolute_error')]}})
    return summaries


def spread_diagnostics(rows, cases):
    """Describe fixed-calculation variation, without claiming grade correctness."""
    diagnostics=[]
    for case in cases:
        group=[r for r in rows if r['id']==case['id'] and r['condition']=='combined' and r['status']=='scored']
        if len(group)!=3:
            diagnostics.append({'id':case['id'],'status':'unavailable'})
            continue
        same=all(r['figures']==group[0]['figures'] for r in group)
        differing=[f for f in sorted(FIELDS) if len({r['figures'][f] for r in group})>1]
        q=[r['result']['quantitative_contribution'] for r in group]
        grades=[r['result']['qualitative_contribution'] for r in group]
        totals=[r['result']['aggregate'] for r in group]
        diagnostics.append({'id':case['id'],'status':'descriptive','identical_financial_vectors':same,
                            'differing_financial_fields':differing,'quantitative_contributions':q,
                            'qualitative_contributions':grades,'aggregate_range':max(totals)-min(totals),
                            'quantitative_range':max(q)-min(q),'qualitative_range':max(grades)-min(grades),
                            'ratings':[r['result']['rating'] for r in group],
                            'notch_range':max(RATINGS.index(r['result']['rating']) for r in group)-min(RATINGS.index(r['result']['rating']) for r in group),
                            'interpretation':'With identical financial vectors, remaining score spread is exactly due to the stored grades.' if same else 'Financial differences remain; do not attribute all spread to grades.'})
    return diagnostics


def run(root=ROOT, spec_path=HERE/'interventions.json'):
    spec=load(spec_path); run_dir=root/spec['original_run']
    if tuple(spec['conditions'])!=CONDITIONS: raise ValueError('Unexpected conditions')
    if len(spec['cases'])!=3 or {c['id'] for c in spec['cases']}!={'X12','X15','X20'}:raise ValueError('Unexpected cohort')
    for case in spec['cases']:validate_patches(case,spec['field_ownership'])
    method=root/spec['methodology']['path']
    if digest(method.read_bytes())!=spec['methodology']['sha256']:raise ValueError('Methodology hash mismatch')
    evidence={c['id']:verify_source(root,run_dir,c,spec['as_of']) for c in spec['cases']}
    baselines=load_baselines(root,run_dir,spec)
    rows=[]
    for original in baselines:
        case=next(c for c in spec['cases'] if c['id']==original['id'])
        rows.extend(intervene(original,case,condition) for condition in CONDITIONS)
    hashes={str(p.relative_to(root)):digest(p.read_bytes()) for p in
            (spec_path,method,run_dir/'manifest.json',run_dir/'ledger.jsonl',root/'system/scorecard.py',root/'evaluation/goldset.json')}
    return {'study':spec['study'],'as_of':spec['as_of'],'spec':spec,'hashes':hashes,
            'evidence':evidence,'baselines':baselines,'rows':rows,'summary':summarize(rows,spec['cases']),
            'spread_diagnostics':spread_diagnostics(rows,spec['cases']),
            'review_status':'source-supported researcher interpretations pending human review',
            'limitations':'Three exposed development issuers; reported/task-defined constructs, not complete Moody adjustments. No LLM rerun.'}


def report_text(result):
    lines=['# Accounting intervention results','',
           '*OpenAI Codex, directed by Robert Vetter, 17 September 2026. Offline saved-response replay; source-supported researcher interpretations pending human review.*','',
           result['limitations'],'','Positive aggregate/notch deltas mean a weaker indicated rating, not necessarily a larger error.',
           'All qualitative grades and original direct judgements are fixed. Debt for Signet is a disclosed-lease floor, not a complete adjusted-debt replacement.',
           'Combined uses only supported patches; Nike combined duplicates other-supported. Missing gross expense is not guessed.','',
           '| Issuer / replicate | Condition | Original → intervention | Aggregate delta | Notch delta | Label error before → after |',
           '|---|---|---|---:|---:|---|']
    for r in result['rows']:
        if r['status']!='scored':lines.append(f"| {r['slug']} r{r['replicate']} | {r['condition']} | {r['status']} | — | — | — |")
        else:
            old=RATINGS[RATINGS.index(r['result']['rating'])-r['delta_notches']]
            lines.append(f"| {r['slug']} r{r['replicate']} | {r['condition']} | {old} → {r['result']['rating']} | {r['delta_aggregate']:+.6f} | {r['delta_notches']:+d} | {r['baseline_absolute_error']} → {r['absolute_error']} |")
    lines.extend(['','## Matched issuer-consensus comparisons','',
                  '| Condition | Issuers | Exact, intervention / original / persistence | MAE, intervention / original / persistence |',
                  '|---|---:|---|---|'])
    for s in result['summary']:
        m=s['issuer_metrics'];items=[m[k] for k in ('intervention','matched_original','persistence')]
        lines.append(f"| {s['condition']} | {items[0]['n']}/3 | " + ' / '.join(str(x['exact']) for x in items)+' | '+' / '.join('not estimable' if x['mae'] is None else f"{x['mae']:.3f}" for x in items)+' |')
    lines.extend(['','## Remaining within-issuer spread after combined interventions','',
                  '| Issuer | Identical financial vectors? | Ratings r1 / r2 / r3 | Aggregate range | Quantitative range | Qualitative range |',
                  '|---|---|---|---:|---:|---:|'])
    for d in result['spread_diagnostics']:
        if d['status']=='descriptive':
            lines.append(f"| {d['id']} | {d['identical_financial_vectors']} | {' / '.join(d['ratings'])} | {d['aggregate_range']:.6f} | {d['quantitative_range']:.6f} | {d['qualitative_range']:.6f} |")
    lines.extend(['','Identical financial vectors isolate the stored grades as the source of remaining numerical spread, not the source of all label error or proof that those grades are wrong.',
                  'The three response repetitions are not independent issuers. Matched baselines change with condition eligibility.',
                  'Remaining discrepancy is unexplained residual, not automatically qualitative error. Working-capital interventions follow the executed task, not a verified agency RCF adjustment.',
                  'Full ratios, factor scores, operands, hashes and original/intervened vectors are in study.json.'])
    return '\n'.join(lines)+'\n'


def save(result, destination, root=ROOT):
    destination=Path(destination).resolve();base=(root/'evaluation/runs').resolve()
    if destination.parent!=base or not destination.name.startswith('accounting-interventions-'):raise ValueError('Fresh accounting-interventions-* directory required under evaluation/runs')
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    destination.mkdir(exist_ok=False)
    (destination/'study.json').write_text(payload)
    (destination/'results.md').write_text(report_text(result))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path)
    args=parser.parse_args();result=run();print(report_text(result),end='')
    if args.out:save(result,args.out)


if __name__=='__main__':main()
