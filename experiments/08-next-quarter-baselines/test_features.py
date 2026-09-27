"""
Tests for Experiment 08 (pre-check P13): quarter durations, trailing twelve months, point in
time, restatements, the time split, the sector-cycle feature and gold handling.

Written 2026-09-27 by Claude (Opus 5.5), directed by Robert Vetter.
    python3 -m unittest discover -s experiments/08-next-quarter-baselines -p 'test_*.py'
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_features as B  # noqa: E402
import fit_models as F  # noqa: E402


def fact(start, end, val, filed, form="10-Q", tag="Revenues"):
    e = {"end": end, "val": val, "filed": filed, "form": form}
    if start:
        e["start"] = start
    return e


def raw(entries_by_tag):
    return {"facts": {"us-gaap": {t: {"units": {"USD": es}} for t, es in entries_by_tag.items()}}}


class Durations(unittest.TestCase):
    def test_first_of_month_quarter_is_a_quarter(self):
        # the Walmart case: 2008-05-01 to 2008-07-31 is 91 days, not 60
        f = B.extract_facts(raw({"Revenues": [fact("2008-05-01", "2008-07-31", 100, "2008-09-01")]}))
        v = f["revenue"][0]
        self.assertTrue(80 <= B.days(v["start"], v["end"]) <= 100)


class TrailingTwelveMonths(unittest.TestCase):
    def setUp(self):
        self.facts = B.extract_facts(raw({"Revenues": [
            fact("2023-02-01", "2024-01-31", 1000, "2024-03-20", form="10-K"),
            fact("2023-02-01", "2023-04-30", 200, "2023-06-01"),
            fact("2023-05-01", "2023-07-31", 250, "2023-09-01"),
            fact("2023-08-01", "2023-10-31", 260, "2023-12-01"),
            fact("2024-02-01", "2024-04-30", 230, "2024-06-01"),
            fact("2024-05-01", "2024-07-31", 240, "2024-09-01"),
        ]}))["revenue"]

    def test_annual(self):
        self.assertEqual(B.ttm(self.facts, "2024-01-31", "2024-12-31")[:1], (1000,))

    def test_first_quarter_is_its_own_year_to_date(self):
        # TTM at 2024-04-30 = FY2023 1000 + Q1 2024 230 - Q1 2023 200
        val, filed, method = B.ttm(self.facts, "2024-04-30", "2024-12-31")
        self.assertEqual((val, method, filed), (1030, "ytd", "2024-06-01"))

    def test_derived_fourth_quarter(self):
        # no six-month figure: Q2 240 + Q1 230 + derived Q4 (1000 - 200 - 250 - 260 = 290) + Q3 260
        val, filed, method = B.ttm(self.facts, "2024-07-31", "2024-12-31")
        self.assertEqual((val, method, filed), (1020, "quarters", "2024-09-01"))

    def test_ytd_method(self):
        facts = B.extract_facts(raw({"Revenues": [
            fact("2023-02-01", "2024-01-31", 1000, "2024-03-20", form="10-K"),
            fact("2023-02-01", "2023-07-31", 450, "2023-09-01"),
            fact("2024-02-01", "2024-07-31", 500, "2024-09-01"),
        ]}))["revenue"]
        self.assertEqual(B.ttm(facts, "2024-07-31", "2024-12-31")[::2], (1050, "ytd"))

    def test_value_filed_after_t_is_not_used(self):
        self.assertIsNone(B.ttm(self.facts, "2024-04-30", "2024-05-31"))
        self.assertIsNone(B.ttm(self.facts, "2024-01-31", "2024-03-19"))

    def test_restatement_keeps_the_earliest_filing(self):
        f = B.extract_facts(raw({"Revenues": [
            fact("2023-02-01", "2023-04-30", 200, "2023-06-01"),
            fact("2023-02-01", "2023-04-30", 210, "2024-06-01")]}))["revenue"]
        self.assertEqual((len(f), f[0]["val"], f[0]["filed"]), (1, 200, "2023-06-01"))

    def test_first_tag_in_the_chain_wins(self):
        f = B.extract_facts(raw({
            "Revenues": [fact("2023-02-01", "2023-04-30", 999, "2023-06-01")],
            "RevenueFromContractWithCustomerExcludingAssessedTax": [fact("2023-02-01", "2023-04-30", 200, "2023-06-02")]}))
        self.assertEqual(f["revenue"][0]["val"], 200)


class PointInTime(unittest.TestCase):
    def test_features_never_use_later_filings(self):
        facts = B.extract_facts(raw({
            "Revenues": [fact("2023-02-01", "2024-01-31", 1000, "2024-03-20", form="10-K"),
                         fact("2022-02-01", "2023-01-31", 900, "2023-03-20", form="10-K")],
            "OperatingIncomeLoss": [fact("2023-02-01", "2024-01-31", 80, "2024-03-20", form="10-K")],
            "DepreciationDepletionAndAmortization": [fact("2023-02-01", "2024-01-31", 20, "2024-03-20", form="10-K")]}))
        early = B.financial_features(facts, "2024-03-01")
        self.assertEqual(early["period"], "2023-01-31")
        self.assertLessEqual(early["max_filed"], "2024-03-01")
        late = B.financial_features(facts, "2024-06-30")
        self.assertEqual(late["period"], "2024-01-31")
        self.assertAlmostEqual(late["F1"], 1000 / 900 - 1)
        self.assertAlmostEqual(late["F2"], 0.1)


class RatingFeatures(unittest.TestCase):
    def test_sector_cycle_and_momentum_ignore_later_quarters(self):
        q = lambda c, t, ch, dl: {"company": c, "date": t, "changed": ch, "delta": dl}
        own = [q("a", "2019-12-31", False, None), q("a", "2020-03-31", True, 1), q("a", "2020-06-30", False, None),
               q("a", "2020-09-30", True, -1)]
        by_date = {"2020-03-31": [own[1], q("b", "2020-03-31", False, None)],
                   "2020-06-30": [own[2], q("b", "2020-06-30", False, None)],
                   "2020-09-30": [own[3], q("b", "2020-09-30", True, 1)]}
        r = B.rating_features(own, "2020-06-30", "Ba2", {k: v for k, v in by_date.items() if k <= "2020-06-30"})
        self.assertEqual((r["R3"], r["R4"], r["R5"]), (1, 0, 1))
        self.assertAlmostEqual(r["R6_down"], 1 / 4)
        self.assertEqual(r["R6_up"], 0.0)


class Split(unittest.TestCase):
    def test_time_split_and_gold(self):
        rows = [{"outcome_date": "2020-12-31", "gold": False}, {"outcome_date": "2020-09-30", "gold": True},
                {"outcome_date": "2021-03-31", "gold": True}, {"outcome_date": "2022-06-30", "gold": False}]
        train, test = F.split(rows)
        self.assertEqual([r["outcome_date"] for r in train], ["2020-12-31"])
        self.assertEqual([r["outcome_date"] for r in test], ["2021-03-31", "2022-06-30"])


class Metrics(unittest.TestCase):
    def test_persistence_ranks_at_base_rate(self):
        import numpy as np
        rows = [{"target": t} for t in (0, 0, 0, 1)]
        m = F.metrics(rows, np.tile([1.0, 0, 0], (4, 1)), "M0")
        self.assertAlmostEqual(m["pr_auc"], 0.25)
        self.assertIsNone(m["log_loss"])

    def test_perfect_ranking(self):
        import numpy as np
        rows = [{"target": t} for t in (0, 0, 1, 2)]
        P = np.array([[.9, .05, .05], [.8, .1, .1], [.2, .7, .1], [.3, .1, .6]])
        m = F.metrics(rows, P, "x")
        self.assertAlmostEqual(m["pr_auc"], 1.0)
        self.assertEqual(m["direction_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
