"""Offline accounting evidence regressions, synthetic fixtures plus optional cache.

Written by OpenAI Codex, directed by Robert Vetter, 2026-09-17.
Tests mechanics, not human adjudication or rating accuracy.
"""
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))
sys.path.insert(0, str(ROOT / "evaluation/pipeline"))
from evidence_ledger import normalize, select, FilingIndex, REVENUE, digest
from accounting_checks import annual_checks, reconcile
from accounting_benchmark import build_report, save_report, render, CASES, AS_OF

SOURCE = {"path": "fixture.json", "sha256": "a" * 64}


def fact(**kwargs):
    return {"start": "2025-02-01", "end": "2026-01-31", "val": 100,
            "accn": "0000000001-26-000001", "filed": "2026-03-01", "form": "10-K", **kwargs}


def raw(tags, unit="USD"):
    return {"entityName": "Fixture", "cik": 1, "facts": {"us-gaap": {
        tag: {"units": {unit: values}} for tag, values in tags.items()}}}


def records(tags, unit="USD", ends=("2026-01-31",)):
    return normalize(raw(tags, unit), SOURCE, AS_OF, set(ends))


class EvidenceTests(unittest.TestCase):
    def test_exact_calendar_quarter(self):
        rows = records({"Revenues": [fact(start="2026-02-01", end="2026-04-30")]}, ends=("2026-04-30",))
        self.assertEqual(rows[0]["elapsed_days"], 88)
        self.assertEqual(rows[0]["duration_kind"], "quarter_length")

    def test_leap_quarter(self):
        rows = records({"Revenues": [fact(start="2024-02-01", end="2024-04-30", filed="2024-05-31")]}, ends=("2024-04-30",))
        self.assertEqual(rows[0]["elapsed_days"], 89)

    def test_exact_start_prevents_ytd_substitution(self):
        rows = records({"Revenues": [fact(start="2025-08-01", val=60), fact(val=100)]})
        self.assertEqual(select(rows, ("Revenues",), "2025-08-01", "2026-01-31")["value"], 60)
        self.assertEqual(select(rows, ("Revenues",), "2025-11-01", "2026-01-31")["status"], "missing")

    def test_invalid_inputs_quarantined(self):
        for change, issue in [({"filed": None}, "missing_or_invalid_date"),
                              ({"filed": "not-a-date"}, "missing_or_invalid_date"),
                              ({"filed": "2026-09-01"}, "filed_after_observation"),
                              ({"filed": "2025-01-01"}, "period_after_filing"),
                              ({"start": "2026-02-01"}, "reversed_period"),
                              ({"val": float("nan")}, "invalid_value"),
                              ({"val": True}, "invalid_value"),
                              ({"form": "8-K"}, "unsupported_form"),
                              ({"accn": None}, "missing_accession")]:
            with self.subTest(change=change):
                r = records({"Revenues": [fact(**change)]})[0]
                self.assertIn(issue, r["issues"])
                self.assertEqual(r["availability"], "quarantined")
                json.dumps(r, allow_nan=False)

    def test_wrong_unit(self):
        r = records({"Revenues": [fact()]}, "EUR")
        self.assertEqual(select(r, ("Revenues",), "2025-02-01", "2026-01-31")["status"], "missing")

    def test_future_preferred_tag_does_not_hide_available_tag(self):
        rows = records({REVENUE[0]: [fact(filed="2026-09-01", val=999)], "Revenues": [fact()]})
        result = select(rows, REVENUE, "2025-02-01", "2026-01-31")
        self.assertEqual(result["value"], 100)
        self.assertEqual(result["tag"], "Revenues")

    def test_revisions_conflict_only_when_available(self):
        rows = records({"Revenues": [fact(), fact(val=110, filed="2026-08-01"), fact(val=900, filed="2026-09-01")]})
        result = select(rows, ("Revenues",), "2025-02-01", "2026-01-31")
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(len(result["evidence_ids"]), 2)

    def test_provenance_and_zero(self):
        rows = records({"Revenues": [fact(val=0)]})
        self.assertEqual(rows[0]["source"]["pointer"], "/facts/us-gaap/Revenues/units/USD/0")
        result = select(rows, ("Revenues",), "2025-02-01", "2026-01-31")
        self.assertEqual(result["value"], 0)
        self.assertEqual(result["review_status"], "pending_human_review")
        self.assertEqual(records({"Revenues": [fact(val=0)]}), rows)

    def test_net_and_cash_not_gross(self):
        rows = records({"InterestIncomeExpenseNet": [fact(val=4)], "InterestPaidNet": [fact(val=7.6)]})
        checks = annual_checks(rows, "2025-02-01", "2026-01-31")
        gross = next(r for r in checks if r["metric"] == "gross_interest_expense")
        self.assertEqual(gross["status"], "missing")
        self.assertIsNone(gross["value"])

    def test_lease_reconciliation_lineage(self):
        rows = records({tag: [fact(start=None, val=value)] for tag, value in
                        [("OperatingLeaseLiability", 100), ("OperatingLeaseLiabilityCurrent", 20),
                         ("OperatingLeaseLiabilityNoncurrent", 80)]})
        result = reconcile(rows, "OperatingLeaseLiability", "OperatingLeaseLiabilityCurrent",
                           "OperatingLeaseLiabilityNoncurrent", "2026-01-31")
        self.assertEqual(result["value"], 0)
        self.assertEqual(len(result["dependencies"]), 3)
        total = annual_checks(rows, "2025-02-01", "2026-01-31")[-1]
        self.assertIsNone(total["value"])
        self.assertEqual(total["status"], "needs_review")

    def test_goods_revenue_not_total(self):
        checks = annual_checks(records({"SalesRevenueGoodsNet": [fact()]}), "2025-02-01", "2026-01-31")
        self.assertEqual(checks[0]["status"], "missing")
        self.assertTrue(any(r["metric"] == "SalesRevenueGoodsNet" for r in checks))

    def test_conflicting_reconciliation_keeps_candidates(self):
        rows = records({"OperatingLeaseLiability": [fact(start=None), fact(start=None, val=110)],
                        "OperatingLeaseLiabilityCurrent": [fact(start=None, val=20)],
                        "OperatingLeaseLiabilityNoncurrent": [fact(start=None, val=80)]})
        result = reconcile(rows, "OperatingLeaseLiability", "OperatingLeaseLiabilityCurrent",
                           "OperatingLeaseLiabilityNoncurrent", "2026-01-31")
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(set(result["evidence_ids"]), {r["id"] for r in rows})
        self.assertEqual(result["operands"][0]["status"], "conflict")

    def test_missing_component_not_zero(self):
        rows = records({"OperatingLeaseLiability": [fact(start=None, val=100)]})
        self.assertEqual(reconcile(rows, "OperatingLeaseLiability", "OperatingLeaseLiabilityCurrent",
                                   "OperatingLeaseLiabilityNoncurrent", "2026-01-31")["status"], "missing")


HTML = '''<html><xbrli:context id="c"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>2025-02-01</xbrli:startDate><xbrli:endDate>2026-01-31</xbrli:endDate></xbrli:period></xbrli:context>
<xbrli:unit id="u"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
<ix:nonFraction name="us-gaap:Revenues" contextRef="c" unitRef="u" id="n" scale="6" format="ixt:num-dot-decimal">100</ix:nonFraction></html>'''


class LocatorTests(unittest.TestCase):
    def setUp(self):
        self.record = records({"Revenues": [fact(val=100000000)]})[0]

    def test_numeric_locator(self):
        found = FilingIndex(HTML).locate(self.record, {"path": "fixture.htm", "sha256": digest(HTML.encode())})
        self.assertEqual(found["status"], "matched_inline_fact")
        self.assertTrue(HTML[found["matches"][0]["character_offset"]:].startswith("<ix:nonFraction"))

    def test_wrong_context_unit_entity_or_value(self):
        for html in [HTML.replace("http://www.sec.gov/CIK", "urn:other-register"),
                     HTML.replace("iso4217:USD", "iso4217:EUR"),
                     HTML.replace(">1</xbrli:identifier>", ">2</xbrli:identifier>"),
                     HTML.replace("2025-02-01", "2025-11-01"),
                     HTML.replace(">100</ix:", ">999</ix:"),
                     HTML.replace("<xbrli:period>", '<xbrli:segment><xbrldi:explicitMember>part</xbrldi:explicitMember></xbrli:segment><xbrli:period>')]:
            with self.subTest(html=html):
                self.assertEqual(FilingIndex(html).locate(self.record, SOURCE)["status"], "filing_locator_unavailable")


class RunnerTests(unittest.TestCase):
    def test_gold_guard_and_missing_case_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation").mkdir()
            (root / "evaluation/goldset.json").write_text(json.dumps({"items": [{"slug": "walmart", "date": AS_OF}]}))
            with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
                report = build_report(root)
            self.assertEqual([r["status"] for r in report["results"]], ["excluded_gold", "unavailable", "unavailable"])
            self.assertEqual(sorted(p.name for p in root.rglob("*") if p.is_file()), ["goldset.json"])
            self.assertIn("unavailable", render(report))

    def test_missing_supplemental_files_preserve_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation").mkdir()
            (root / "evaluation/goldset.json").write_text('{"items": []}')
            cache = root / "data/edgar/companyfacts"
            cache.mkdir(parents=True)
            (cache / "walmart.json").write_text(json.dumps(raw({"Revenues": [fact()]})))
            report = build_report(root, CASES[:1])
            result = report["results"][0]
            self.assertEqual(result["status"], "completed")
            self.assertEqual(len(result["source_issues"]), 2)
            self.assertEqual(result["rows"][0]["value"], 100)
            self.assertEqual(result["records"][0]["filing_locator"]["status"], "filing_locator_unavailable")

    def test_save_is_explicit_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation/runs").mkdir(parents=True)
            report = {"scope": "fixture", "results": []}
            dest = root / "evaluation/runs/accounting-development-test"
            save_report(report, dest, root)
            with self.assertRaises(FileExistsError):
                save_report(report, dest, root)
            with self.assertRaises(ValueError):
                save_report(report, root / "existing", root)

    @unittest.skipUnless((ROOT / "data/edgar/companyfacts/walmart.json").exists(), "Local source cache unavailable")
    def test_real_cases_and_determinism(self):
        required = [ROOT / "evaluation/goldset.json"]
        for case in CASES:
            slug = case["slug"]
            required.extend([ROOT / f"data/edgar/companyfacts/{slug}.json",
                             ROOT / f"evaluation/companies/{slug}/xbrl.json",
                             ROOT / f"evaluation/companies/{slug}/filings/manifest.json"])
        if not all(p.exists() for p in required):
            self.skipTest("Three-case source cache incomplete")
        with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")):
            report = build_report()
            self.assertEqual(report, build_report())
        self.assertTrue(all(r["status"] == "completed" for r in report["results"]))
        walmart = report["results"][0]
        facts = [r for r in walmart["records"] if r["tag"] == REVENUE[0]
                 and r["start"] == "2026-02-01" and r["end"] == "2026-04-30"]
        self.assertEqual(facts[0]["elapsed_days"], 88)
        self.assertEqual(facts[0]["val"], 175684000000)
        self.assertEqual(facts[0]["accn"], "0000104169-26-000102")
        self.assertEqual(facts[0]["filing_locator"]["status"], "matched_inline_fact")
        for result in report["results"]:
            self.assertEqual(result["coverage"]["referenced_facts"], result["coverage"]["matched_filing_facts"])
            self.assertTrue(all(r["review_status"] == "pending_human_review" for r in result["rows"]))
        json.dumps(report, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
