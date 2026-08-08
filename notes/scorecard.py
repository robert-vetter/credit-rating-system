"""
Retail and Apparel scorecard arithmetic, Moody's methodology of 12 Sep 2025.
Inputs are hand-extracted from the Walmart FY2026 10-K, see walmart-first-test.md.
Run it with plain python3, no dependencies.
"""

# quantitative bands, (metric at the good end, metric at the bad end, numeric good, numeric bad)
# the good end is the one that maps to the lower numeric score
BANDS = {
    "revenue_usd_bn": [
        (150.0, 100.0, 0.5, 1.5),   # Aaa, footnote 1 puts the endpoint at 150
        (100.0, 50.0, 1.5, 4.5),    # Aa
        (50.0, 25.0, 4.5, 7.5),     # A
        (25.0, 10.0, 7.5, 10.5),    # Baa
        (10.0, 4.0, 10.5, 13.5),    # Ba
        (4.0, 1.5, 13.5, 16.5),     # B
        (1.5, 0.5, 16.5, 19.5),     # Caa
        (0.5, 0.0, 19.5, 20.5),     # Ca
    ],
    "debt_ebitda": [
        (0.0, 0.5, 0.5, 1.5),
        (0.5, 1.0, 1.5, 4.5),
        (1.0, 2.0, 4.5, 7.5),
        (2.0, 3.0, 7.5, 10.5),
        (3.0, 4.0, 10.5, 13.5),
        (4.0, 6.0, 13.5, 16.5),
        (6.0, 8.0, 16.5, 19.5),
        (8.0, 12.0, 19.5, 20.5),
    ],
    "rcf_net_debt_pct": [
        (100.0, 80.0, 0.5, 1.5),    # no Aaa band is printed, footnote 3 gives the 100% endpoint
        (80.0, 60.0, 1.5, 4.5),
        (60.0, 40.0, 4.5, 7.5),
        (40.0, 25.0, 7.5, 10.5),
        (25.0, 15.0, 10.5, 13.5),
        (15.0, 10.0, 13.5, 16.5),
        (10.0, 5.0, 16.5, 19.5),
        (5.0, 0.0, 19.5, 20.5),
    ],
    "ebitda_capex_interest": [
        (25.0, 20.0, 0.5, 1.5),     # no Aaa band is printed, footnote 4 gives the 25x endpoint
        (20.0, 16.0, 1.5, 4.5),
        (16.0, 9.0, 4.5, 7.5),
        (9.0, 4.5, 7.5, 10.5),
        (4.5, 2.5, 10.5, 13.5),
        (2.5, 1.25, 13.5, 16.5),
        (1.25, 0.25, 16.5, 19.5),
        (0.25, 0.0, 19.5, 20.5),
    ],
}

QUALITATIVE = {"Aaa": 1, "Aa": 3, "A": 6, "Baa": 9, "Ba": 12, "B": 15, "Caa": 18, "Ca": 20}

OUTCOME = [
    (1.5, "Aaa"), (2.5, "Aa1"), (3.5, "Aa2"), (4.5, "Aa3"),
    (5.5, "A1"), (6.5, "A2"), (7.5, "A3"),
    (8.5, "Baa1"), (9.5, "Baa2"), (10.5, "Baa3"),
    (11.5, "Ba1"), (12.5, "Ba2"), (13.5, "Ba3"),
    (14.5, "B1"), (15.5, "B2"), (16.5, "B3"),
    (17.5, "Caa1"), (18.5, "Caa2"), (19.5, "Caa3"),
    (20.5, "Ca"),
]


def score_quant(metric, value):
    bands = BANDS[metric]
    best = bands[0][0]
    worst = bands[-1][1]
    ascending = best > worst          # true when a higher metric value is better
    if (ascending and value >= best) or (not ascending and value <= best):
        return 0.5
    if (ascending and value <= worst) or (not ascending and value >= worst):
        return 20.5
    for good, bad, n_good, n_bad in bands:
        inside = good >= value >= bad if ascending else good <= value <= bad
        if inside:
            frac = (good - value) / (good - bad)
            return n_good + frac * (n_bad - n_good)
    raise ValueError(f"{value} fell through the bands for {metric}")


def outcome(aggregate):
    for ceiling, label in OUTCOME:
        if aggregate <= ceiling:
            return label
    return "C"


# Walmart FY2026, year ended 31 January 2026, USD millions, straight off the filing
revenue = 713_163
operating_income = 29_825
d_and_a = 14_203
capex = 26_642
interest_debt = 2_318
interest_finance_lease = 481
cash = 10_727
dividends_common = 7_507
cfo = 41_565
working_capital_swing = -1_136 - 1_443 + 1_611 + 1_607 + 113

debt = (
    6_596      # short-term borrowings
    + 3_542    # long-term debt due within one year
    + 34_624   # long-term debt
    + 856 + 5_905      # finance leases, current and long term
    + 1_631 + 13_941   # operating leases, current and long term
)

ebitda = operating_income + d_and_a
gross_interest = interest_debt + interest_finance_lease
ffo = cfo - working_capital_swing
rcf = ffo - dividends_common
net_debt = debt - cash

metrics = {
    "revenue_usd_bn": revenue / 1000,
    "debt_ebitda": debt / ebitda,
    "ebitda_capex_interest": (ebitda - capex) / gross_interest,
    "rcf_net_debt_pct": 100 * rcf / net_debt,
}

scorecard = [
    ("Revenue",                      0.15, score_quant("revenue_usd_bn", metrics["revenue_usd_bn"])),
    ("Market Characteristics",       0.10, QUALITATIVE["A"]),
    ("Market Position",              0.10, QUALITATIVE["Aa"]),
    ("Revenue and Earnings Stability", 0.10, QUALITATIVE["Aa"]),
    ("Debt/EBITDA",                  0.15, score_quant("debt_ebitda", metrics["debt_ebitda"])),
    ("(EBITDA-Capex)/Interest",      0.15, score_quant("ebitda_capex_interest", metrics["ebitda_capex_interest"])),
    ("RCF/Net Debt",                 0.10, score_quant("rcf_net_debt_pct", metrics["rcf_net_debt_pct"])),
    ("Financial Policy",             0.15, QUALITATIVE["Aa"]),
]

if __name__ == "__main__":
    print("inputs")
    print(f"  EBITDA                {ebitda:,}")
    print(f"  total debt            {debt:,}")
    print(f"  net debt              {net_debt:,}")
    print(f"  gross interest        {gross_interest:,}")
    print(f"  FFO                   {ffo:,}")
    print(f"  RCF                   {rcf:,}")
    print()
    print("metrics")
    print(f"  revenue               ${metrics['revenue_usd_bn']:.1f}bn")
    print(f"  debt/EBITDA           {metrics['debt_ebitda']:.2f}x")
    print(f"  (EBITDA-capex)/int    {metrics['ebitda_capex_interest']:.2f}x")
    print(f"  RCF/net debt          {metrics['rcf_net_debt_pct']:.1f}%")
    print()
    print("scorecard")
    total = 0.0
    for name, weight, score in scorecard:
        total += weight * score
        print(f"  {name:<32} {weight:>5.0%}  {score:>6.2f}  {weight*score:>6.3f}")
    print(f"  {'aggregate':<32} {'':>5}  {'':>6}  {total:>6.3f}")
    print()
    print(f"scorecard-indicated outcome: {outcome(total)}")
    margin = min(abs(total - c) for c, _ in OUTCOME)
    print(f"distance to the nearest notch boundary: {margin:.3f}")
