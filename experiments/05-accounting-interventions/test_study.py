"""Offline intervention protocol tests; synthetic mechanics and optional saved replay.
OpenAI Codex, directed by Robert Vetter, 2026-09-17.
"""
import copy
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_study as study


def original():
    figures={'revenue':10000,'operating_income':500,'d_and_a':100,'capex':100,'interest':50,
             'cash':100,'dividends':20,'cfo':400,'wc_swing':10,'debt':1000}
    qual={k:'Baa' for k in study.QUAL}
    return {'id':'X15','slug':'signet','replicate':1,'figures':figures,'qualitative':qual,
            'baseline':study.score(figures,qual),'label':'Ba3','persistence':'Ba3','direct_rating':'Ba3'}


def patch_record(field='interest',group='interest',value=70,operation='replace'):
    return {'group':group,'field':field,'operation':operation,'value_usd_m':value,
            'operands':[{'value_usd_m':value,'coefficient':1}],'quotes':['fixture'], 'rationale':'fixture'}


class Mechanics(unittest.TestCase):
    def test_exact_original_replay(self):
        o=original();r=study.intervene(o,{'patches':[]},'original')
        self.assertEqual(r['result'],o['baseline']);self.assertEqual(r['delta_notches'],0)

    def test_original_and_qualitative_unchanged(self):
        o=original();saved=copy.deepcopy(o)
        r=study.intervene(o,{'patches':[patch_record()]},'interest')
        self.assertEqual(o,saved);self.assertEqual(r['qualitative'],o['qualitative'])
        self.assertEqual({k for k in o['figures'] if o['figures'][k]!=r['figures'][k]},{'interest'})
        self.assertEqual(r['direct_rating_unchanged'],o['direct_rating'])

    def test_combined_union_from_original(self):
        o=original();case={'patches':[patch_record(),patch_record('debt','debt',1200)]}
        r=study.intervene(o,case,'combined')
        self.assertEqual(r['figures']['interest'],70);self.assertEqual(r['figures']['debt'],1200)
        self.assertEqual(r['figures']['cash'],100)
        study.intervene(o,case,'debt')
        self.assertEqual(study.intervene(o,case,'combined'),r)

    def test_floor_is_not_addition(self):
        r=study.intervene(original(),{'patches':[patch_record('debt','debt',900,'floor')]},'debt')
        self.assertEqual(r['figures']['debt'],1000);self.assertEqual(r['delta_aggregate'],0)
        self.assertEqual(r['status'],'scored')

    def test_missing_is_not_zero_effect(self):
        r=study.intervene(original(),{'patches':[]},'interest')
        self.assertEqual(r['status'],'not_estimable');self.assertNotIn('result',r)

    def test_undefined_intervention_retained(self):
        for value in (0,-1):
            r=study.intervene(original(),{'patches':[patch_record(value=value)]},'interest')
            self.assertEqual(r['status'],'undefined_scorecard');self.assertIn('figures',r)

    def test_patch_validation(self):
        ownership={'interest':['interest'],'debt':['debt'],'other':['revenue']}
        for patches in [[patch_record(),patch_record()], [patch_record('cash')],
                        [patch_record(operation='add')], [patch_record(value=float('nan'))]]:
            with self.subTest(patches=patches),self.assertRaises(ValueError):study.validate_patches({'patches':patches},ownership)
        p=patch_record();p['operands'][0]['value_usd_m']=9
        with self.assertRaises(ValueError):study.validate_patches({'patches':[p]},ownership)

    def test_decimal_operands(self):
        p=patch_record('wc_swing','other',0.3);p['operands']=[{'value_usd_m':0.1,'coefficient':1},{'value_usd_m':0.2,'coefficient':1}]
        study.validate_patches({'patches':[p]},{'other':['wc_swing']})

    def test_threshold_and_nonlinearity(self):
        self.assertEqual(study.outcome(4.5),'Aa3');self.assertEqual(study.outcome(4.500001),'A1')
        o=original();case={'patches':[patch_record('operating_income','other',100),patch_record(value=400)]}
        a=study.intervene(o,case,'interest');b=study.intervene(o,case,'other');c=study.intervene(o,case,'combined')
        self.assertNotAlmostEqual(a['delta_aggregate']+b['delta_aggregate'],c['delta_aggregate'])

    def test_matched_denominators(self):
        rows=[]
        for rep in (1,2,3):
            o=original();o['replicate']=rep
            rows.extend(study.intervene(o,{'patches':[]},c) for c in study.CONDITIONS)
        summaries=study.summarize(rows,[{'id':'X15'}])
        self.assertEqual(summaries[0]['issuer_metrics']['intervention']['n'],1)
        self.assertEqual(summaries[1]['issuer_metrics']['persistence']['n'],0)
        self.assertIsNone(summaries[1]['issuer_metrics']['intervention']['mae'])

    def test_original_period_gate(self):
        case={'start':'2025-02-01','end':'2026-01-31'}
        for obj in [{'fiscal_year_label':'FY2025 ended 2025-01-31','figure_notes':'2026-01-31 later quarter'},
                    {'fiscal_year_label':'latest year','figure_notes':'No exact period'},
                    {'fiscal_year_label':'2026-01-31','figure_notes':'TTM figures'}]:
            with self.assertRaises(ValueError):study.verify_original_period(obj,case)
        self.assertEqual(study.verify_original_period({'fiscal_year_label':'FY2026','figure_notes':'Fiscal year ended 2026-01-31'},case)['end'],case['end'])

    def test_body_binding(self):
        case={'source':{'accession':'a'}};payload='original text'
        audit={'documents':[{'accession':'a','form':'10-K','filed':'2026-03-01','redacted_text_sha256':study.digest(payload.encode())}]}
        body={'messages':[{}, {'content':'<document name="10-K filed 2026-03-01">\noriginal text\n</document>'}]}
        study.bind_original_document(body,audit,case)
        body['messages'][1]['content']=body['messages'][1]['content'].replace('original text','other text')
        with self.assertRaises(ValueError):study.bind_original_document(body,audit,case)

    def test_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); dest=root/'evaluation/runs/accounting-interventions-test';dest.mkdir(parents=True)
            with self.assertRaises(FileExistsError):study.save({},dest,root)
            with self.assertRaises(ValueError):study.save({},root/'elsewhere',root)


@unittest.skipUnless((study.ROOT/'experiments/04-open-weight-cross-section/runs/EXP04-ARM1-A1/ledger.jsonl').exists(),'Saved run cache unavailable')
class CachedStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(socket,'socket',side_effect=AssertionError('No network allowed')):
            cls.result=study.run()
        cls.spec=cls.result['spec'];cls.run_dir=study.ROOT/cls.spec['original_run']

    def test_nine_baselines_and_attempt_selection(self):
        b=self.result['baselines'];self.assertEqual(len(b),9)
        s=next(x for x in b if x['id']=='X15' and x['replicate']==3)
        self.assertEqual(s['attempt_id'],'doc-current-X15-r3#a2')
        self.assertEqual(len(s['transport_attempts']),2)
        self.assertEqual(len(self.result['rows']),45)

    def test_every_condition_fixed_grades_and_recomputable(self):
        for r in self.result['rows']:
            baseline=next(b for b in self.result['baselines'] if b['id']==r['id'] and b['replicate']==r['replicate'])
            self.assertEqual(r['qualitative'],baseline['qualitative'])
            if r['status']=='scored':self.assertEqual(study.score(r['figures'],r['qualitative']),r['result'])

    def test_source_sign_unit_and_custom_tag(self):
        w=self.result['evidence']['X20'];interest=next(x for x in w if x['field']=='interest')
        self.assertEqual(sum(x['value_usd_m']*x['coefficient'] for x in interest['operands']),2799)
        self.assertIn('wmt:',interest['operands'][1]['tag'])
        for evidences in self.result['evidence'].values():
            for item in evidences:
                for op in item['operands']:self.assertEqual(op['locator']['status'],'matched_inline_fact')

    def test_invalid_source_date_hash_period_and_operand(self):
        base=copy.deepcopy(self.spec['cases'][0])
        for field,value in [('start','2025-03-01'),('end','2026-01-30')]:
            case=copy.deepcopy(base);case[field]=value
            with self.assertRaises(ValueError):study.verify_source(study.ROOT,self.run_dir,case,self.spec['as_of'])
        case=copy.deepcopy(base);case['source']['sha256']='0'*64
        with self.assertRaises(ValueError):study.verify_source(study.ROOT,self.run_dir,case,self.spec['as_of'])
        with self.assertRaises(ValueError):study.verify_source(study.ROOT,self.run_dir,base,'2026-03-01')
        case=copy.deepcopy(base);case['patches'][0]['operands'][0]['value_usd_m']=1
        with self.assertRaises(ValueError):study.verify_source(study.ROOT,self.run_dir,case,self.spec['as_of'])

    def test_baseline_mismatch_stops(self):
        real=study.load
        def altered(path):
            obj=real(path)
            if path.name=='results_current_r1.json':
                for x in obj:
                    if x['id']=='X20':x['aggregate']+=0.01
            return obj
        with patch.object(study,'load',side_effect=altered),self.assertRaisesRegex(ValueError,'Baseline replay mismatch'):
            study.load_baselines(study.ROOT,self.run_dir,self.spec)

    def test_gold_guard(self):
        real=study.load
        def altered(path):
            if path.name=='goldset.json':return {'items':[{'slug':'walmart','date':self.spec['as_of']}]}
            return real(path)
        with patch.object(study,'load',side_effect=altered),self.assertRaisesRegex(ValueError,'Gold observation'):
            study.load_baselines(study.ROOT,self.run_dir,self.spec)

    def test_remaining_spread_is_not_overattributed(self):
        d={x['id']:x for x in self.result['spread_diagnostics']}
        self.assertTrue(d['X15']['identical_financial_vectors'])
        self.assertEqual(d['X15']['notch_range'],3)
        self.assertEqual(d['X15']['quantitative_range'],0)
        self.assertAlmostEqual(d['X15']['aggregate_range'],d['X15']['qualitative_range'])
        self.assertTrue(d['X20']['identical_financial_vectors'])
        self.assertFalse(d['X12']['identical_financial_vectors'])
        self.assertEqual(d['X12']['differing_financial_fields'],['interest'])

    def test_deterministic(self):
        with patch.object(socket,'socket',side_effect=AssertionError('No network allowed')):
            self.assertEqual(self.result,study.run())
        json.dumps(self.result,allow_nan=False)


if __name__=='__main__':unittest.main()
