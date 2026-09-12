"""Free regression checks for the 2026-09-12 review. No network or model calls.

Written by Codex, directed by Robert. Inputs: synthetic edge cases and cached XBRL.
Run: python3 -m unittest discover -s experiments/03-oos-values-first -p 'test_*.py' -v
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT / "system"), str(ROOT / "evaluation/pipeline"), str(HERE)]
import scorecard
import history_pack as hp
import peer_table
import check_extraction
import calibrate_scorecard as calibration
import audit_saved_run


class ScorecardTests(unittest.TestCase):
    def test_negative_ebitda_worst_leverage(self):
        self.assertEqual(scorecard.score_quant("debt_ebitda", -5.05), 20.5)
        self.assertEqual(scorecard.score_quant("debt_ebitda", 0), 0.5)

    def test_net_cash_uses_rcf_sign(self):
        for rcf, expected in ((10, 0.5), (-10, 20.5), (0, 20.5)):
            c = copy.deepcopy(scorecard.WALMART)
            c.update(debt=10, cash=20, cfo=rcf, wc_swing=0, dividends=0)
            scores = {name: value for name, _, value in scorecard.build(c)}
            self.assertEqual(scores["RCF/Net Debt"], expected)

    def test_nonfinite_and_zero_denominators_fail(self):
        for change in ({"operating_income": -scorecard.WALMART["d_and_a"]},
                       {"interest": 0}, {"cash": scorecard.WALMART["debt"]},
                       {"revenue": float("nan")}):
            with self.assertRaises(ValueError):
                scorecard.build({**scorecard.WALMART, **change})
        with self.assertRaises(ValueError):
            scorecard.outcome(float("nan"))

    def test_band_endpoints_and_lookup_precision(self):
        for metric, bands in scorecard.BANDS.items():
            for good, bad, low, high in bands:
                self.assertAlmostEqual(scorecard.score_quant(metric, good), low)
                self.assertAlmostEqual(scorecard.score_quant(metric, bad), high)
        self.assertEqual(scorecard.outcome(5.50001), "A2")


def fact(end, filed, val, tag="test"):
    return {"end": end, "filed": filed, "val": val, "tag": tag, "form": "10-K"}


class PointInTimeTests(unittest.TestCase):
    def test_missing_future_and_invalid_publication_dates(self):
        self.assertFalse(hp.fact_available(fact("2025-01-31", "", 1), "2025-03-31"))
        self.assertFalse(hp.fact_available(fact("2025-01-31", "2025-04-01", 1), "2025-03-31"))
        self.assertTrue(hp.fact_available(fact("2025-01-31", "2025-03-31", 1), "2025-03-31"))
        self.assertFalse(hp.fact_available(fact("2026-01-31", "2025-03-31", 1), "2025-03-31"))
        bad = {"fields": {"cash": {"annual": [fact("2026-01-31", "2025-03-31", 1)]}}}
        self.assertEqual(len(hp.invalid_fact_dates(bad)), 1)

    def test_each_extraction_field_obeys_date(self):
        with tempfile.TemporaryDirectory() as folder:
            company = Path(folder)/"test"
            company.mkdir()
            (company/"xbrl.json").write_text(json.dumps({"fields": {
                "revenue": {"annual": [fact("2025-01-31", "2025-03-01", 10)]},
                "cash": {"annual": [fact("2025-01-31", "2025-04-01", 5)]}}}))
            with patch.object(check_extraction, "OUT", folder):
                _, values = check_extraction.xbrl_year("test", "2025-03-31", "2025-03-31")
            self.assertNotIn("cash", values)

    def test_peers_cannot_mix_fiscal_years_or_double_count_debt(self):
        with tempfile.TemporaryDirectory() as folder:
            for i in range(5):
                d = Path(folder)/str(i)
                d.mkdir()
                (d/"company.json").write_text(json.dumps({"scope": "in", "group": str(i)}))
                fields = {"revenue": [fact("2025-01-31", "2025-03-01", 100)],
                          "operating_income": [fact("2024-01-31", "2024-03-01", 10)],
                          "d_and_a": [fact("2025-01-31", "2025-03-01", 5)],
                          "lt_debt_noncurrent": [fact("2025-01-31", "2025-03-01", 50, "LongTermDebt")],
                          "lt_debt_current": [fact("2025-01-31", "2025-03-01", 10)]}
                (d/"xbrl.json").write_text(json.dumps({"fields": {k: {"annual": v} for k, v in fields.items()}}))
            log = {}
            with patch.object(peer_table, "OUT", folder):
                text = peer_table.build("2025-03-31", audit=log)
            self.assertIsNotNone(text)
            self.assertNotIn("operating_income", log["0"]["sources"])
            self.assertEqual(log["0"]["debt_components"], ["lt_debt_noncurrent"])


class ExecutionTests(unittest.TestCase):
    def test_paid_commands_stop_before_client_creation(self):
        for script, args in (("run_batch.py", ["--submit"]), ("run_batch.py", ["--rerun", "X01"]),
                             ("preflight.py", [])):
            result = subprocess.run([sys.executable, str(HERE/script), *args], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("closed to paid calls", result.stderr)

    def test_gold_never_enters_fit_or_threshold(self):
        with self.assertRaises(ValueError):
            calibration.fit_iso([{"gold": True}])
        with self.assertRaises(ValueError):
            calibration.choose_theta([{"gold": True}], "s_q")

    def test_request_boundary_and_tools(self):
        params = {"model": "claude-opus-4-6", "tools": [], "messages": [{"content": [{"text":
            '<document name="8-K filed 2025-09-30">bad</document>'}]}]}
        checks = audit_saved_run.check_request(params, "2025-09-30", "2026-08-29")
        self.assertFalse(checks["no_tools"])
        self.assertFalse(checks["document_dates"])
        self.assertFalse(checks["document_forms"])


if __name__ == "__main__":
    unittest.main()
