# Experiment 07: results

*Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Follows section 6 of
[EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Verified against run R1-2026-09-26
(`runs/R1-2026-09-26/`: manifest with 172 input hashes, results.json, tables.md) and the post-hoc
direction check (`posthoc_direction.json`). Independent post-run audit: waived by Robert for this
study (decision 2). 15 tests pass.*

## 1. Summary

| Item | Answer |
|---|---|
| Question | How often, by how much and in which direction do Moody's Retail and Apparel ratings change, 2012 to 2025? |
| Answer | 6.2% of company-quarters change; 22.1% of companies see a change within the next 12 months; 45.9% within three years. 85% of changes are one notch |
| Next to persistence | persistence is right on 93.8% of quarters and 77.9% of 12-month windows |
| Strongest pattern | the rating level: 3.5% per quarter for investment grade, 9.1% for speculative grade, 45.5% within 12 months for B and 87.5% for Caa |
| Most important limitation | only companies still rated in 2025 are in the data; retailers whose ratings were withdrawn earlier (Sears, Toys 'R' Us, Bon-Ton and others) are missing |

## 2. Headline

In-scope companies (primary cohort, 72 companies with quarterly records). Persistence is the
complement of the change rate.

| Horizon | n | Changed | Change rate (95% Wilson) | Company bootstrap | Persistence right | Upgrades | Downgrades |
|---|---|---|---|---|---|---|---|
| Quarter | 3,011 | 188 | 6.2% (5.4 to 7.2) | 5.1 to 7.5 | 93.8% | 101 | 87 |
| Year, Q4 to Q4 | 693 | 154 | 22.2% (19.3 to 25.5) | | 77.8% | 90 | 64 |
| Within the next 12 months | 2,792 | 618 | 22.1% (20.6 to 23.7) | 18.5 to 26.1 | 77.9% | 364 | 264 |
| Three years | 2,226 | 1,022 | 45.9% (43.9 to 48.0) | | 54.1% | 618 | 404 |

The earlier figure of 6.0% (218 of 3,646) divided by all observations including each company's
first quarter, which cannot change. With the correct denominator the same 218 changes over all 86
companies give 6.1%.

For the 12-month and three-year rows, upgrades and downgrades count windows containing at least
one move in that direction; a window with both counts twice.

## 3. Dates

| Date concept | Value |
|---|---|
| Moody's files | dated 2026-08-11, actions through August 2025 |
| Quarterly grid | 2012-09-30 to 2025-06-30 |
| Run | 2026-09-26 |

No date changed from the specification.

## 4. Input data characteristics

| Characteristic | Value |
|---|---|
| Companies in the primary cohort | 73 in scope, 72 with quarterly records (Gildan has none) |
| Quarterly records (a label at t and at t-1) | 3,011 |
| Gap quarters (no label inside a company's span) | 12 |
| Companies whose label ends before 2025-06-30 | 0: every company in the data is still rated at the end, see section 10 |
| Rating actions on the line that carries the label | 175 |
| Input files hashed | 172 |

## 5. Results in detail

### 5.1 Size of changes (quarterly)

| Notches | Upgrades | Downgrades | Total | Share |
|---|---|---|---|---|
| 1 | 91 | 69 | 160 | 85.1% |
| 2 | 7 | 14 | 21 | 11.2% |
| 3 or more | 3 | 4 | 7 | 3.7% |
| Total | 101 | 87 | 188 | |

Mean size 1.23 notches. Downgrades are more often large: 18 of 87 downgrades moved two or more
notches, against 10 of 101 upgrades.

### 5.2 By rating at the start of the quarter

| Rating | Quarters | Quarterly change rate | Upgrades | Downgrades | 12-month windows | Change within 12 months |
|---|---|---|---|---|---|---|
| Aa | 83 | 0.0% | 0 | 0 | 74 | 0.0% |
| A | 439 | 2.5% | 8 | 3 | 412 | 10.7% |
| Baa | 1,030 | 4.3% | 20 | 24 | 981 | 16.7% |
| Ba | 1,017 | 6.9% | 37 | 33 | 935 | 23.3% |
| B | 405 | 12.6% | 26 | 25 | 356 | 45.5% |
| Caa | 35 | 31.4% | 9 | 2 | 32 | 87.5% |
| Ca to C | 2 | 50.0% | 1 | 0 | 2 | 100.0% |
| Investment grade | 1,552 | 3.5% | 28 | 27 | 1,467 | 14.2% |
| Speculative grade | 1,459 | 9.1% | 73 | 60 | 1,325 | 30.9% |

The 12-month column by rating category was added while writing the analysis code, before any
result was seen; it is not in the specification's list.

One-year moves between categories, Q4 to Q4 (counts; the diagonal is "stayed in the category",
which includes notch moves inside it):

| From \ to | Aa | A | Baa | Ba | B | Caa |
|---|---|---|---|---|---|---|
| Aa | 19 | | | | | |
| A | 2 | 98 | 2 | | | |
| Baa | | 4 | 229 | 9 | 2 | |
| Ba | | | 6 | 216 | 9 | |
| B | | | | 12 | 72 | 4 |
| Caa | | | | | 5 | 4 |

### 5.3 By company

| Item | Value |
|---|---|
| Companies with at least one change | 59 of 72 |
| Never changed in the period | 13: Arko, Cencosud, Crocs, Kontoor Brands, Lithia Motors, Nike (until its 2025-11-12 downgrade, after the file ends), Tapestry, Target, Tractor Supply, Victoria's Secret, Vipshop, Walmart, Wayfair |
| Share of all changes from the ten most active companies | 34.0% |
| Median company change rate per quarter | 5.6% |
| Most changes | J.Jill 9 in 40 quarters, National Vision 8 in 45, Petco 7 in 50 |

Changes are spread across most companies, not concentrated in a few. The full per-company
table is in the appendix.

### 5.4 By year

| Year | Quarters | Changed | Rate | Upgrades | Downgrades |
|---|---|---|---|---|---|
| 2012 (Q4 only) | 42 | 0 | 0.0% | 0 | 0 |
| 2013 | 173 | 13 | 7.5% | 11 | 2 |
| 2014 | 181 | 11 | 6.1% | 10 | 1 |
| 2015 | 199 | 15 | 7.5% | 13 | 2 |
| 2016 | 213 | 4 | 1.9% | 3 | 1 |
| 2017 | 228 | 9 | 3.9% | 5 | 4 |
| 2018 | 237 | 15 | 6.3% | 11 | 4 |
| 2019 | 242 | 9 | 3.7% | 4 | 5 |
| 2020 | 245 | 27 | 11.0% | 10 | 17 |
| 2021 | 264 | 21 | 8.0% | 16 | 5 |
| 2022 | 279 | 13 | 4.7% | 6 | 7 |
| 2023 | 280 | 24 | 8.6% | 4 | 20 |
| 2024 | 284 | 15 | 5.3% | 6 | 9 |
| 2025 (Q1 and Q2) | 144 | 12 | 8.3% | 2 | 10 |

Direction follows the cycle: mostly upgrades 2013 to 2015 and 2021, mostly downgrades in 2020
and from 2023 on.

### 5.5 Follow-on changes

| Starting quarter | n | Another change within 4 quarters | Rate (95% Wilson) |
|---|---|---|---|
| After a change | 164 | 54 | 32.9% (26.2 to 40.4) |
| After no change | 2,556 | 551 | 21.6% (20.0 to 23.2) |

After a change, the next move is usually in the same direction: 46 windows had another move in
the same direction, 11 a reversal.

### 5.6 What this means for a balanced test set

| Item | Value |
|---|---|
| Changed company-quarters available | 188, from 59 companies |
| 12-month windows with a change / without | 618 / 2,174 |
| All of these are before the training cutoff of current LLMs | usable for counting and for analysis without a model, not as an out-of-sample LLM test |

How often an alarm would be right, for an illustrative detector:

| Framing | Base rate | Finds changes | Correct on stable | Alarm is right |
|---|---|---|---|---|
| Next quarter | 6.2% | 90% | 90% | 37.5% |
| Next quarter | 6.2% | 80% | 95% | 51.6% |
| Within 12 months | 22.1% | 90% | 90% | 71.9% |
| Within 12 months | 22.1% | 80% | 95% | 82.0% |

## 6. Model, settings and cost

No model. $0. Seed 20260926, 2,000 company bootstrap resamples.

## 7. Coverage

| Item | Count |
|---|---|
| Quarterly records | 3,011 |
| 12-month windows kept | 2,792 |
| 12-month windows censored (the last four quarters of each company, and gaps) | 292 |
| Annual pairs | 693 |
| Three-year pairs | 2,226 |

## 8. Where a counted change may not be a real change

| Check | Count | Meaning |
|---|---|---|
| Change agrees with a rating action on the label line in the same direction | 172 of 188 | real |
| Change with no rating action on the label line | 15 | all coincide with a level or entity switch; mostly companies falling from investment grade that receive a new corporate family rating (Gap, Macy's, Kohl's, Under Armour, V.F. and others), so the direction is real but the size is measured across two rating types |
| Change contradicting the action | 1 | Albertsons 2015-09-30, label moved between Albertsons and Safeway bonds during the merger (B2 to Baa3 while the action was a downgrade) |
| Level switches | 23 (21 with a change) | |
| Entity switches | 11 (9 with a change) | |
| Ambiguous labels | 43 records | |
| Reversals inside a quarter, invisible on the grid | 0 | |
| Quarters with two or more actions | 2 | |

The direction check (rows 1 to 3) is post-hoc: it was added after reading the run, prompted by the
Albertsons case, and is saved separately (`posthoc_direction.py`).

## 9. Sensitivities

| Variant | n | Changed | Rate | 95% Wilson |
|---|---|---|---|---|
| Primary, quarter | 3,011 | 188 | 6.2% | 5.4 to 7.2 |
| Level switches excluded, quarter | 2,988 | 167 | 5.6% | 4.8 to 6.5 |
| Ambiguous labels excluded, quarter | 2,968 | 183 | 6.2% | 5.4 to 7.1 |
| All 86 companies, quarter | 3,560 | 218 | 6.1% | 5.4 to 7.0 |
| Primary, within 12 months | 2,792 | 618 | 22.1% | 20.6 to 23.7 |
| Level switches excluded, within 12 months | 2,707 | 539 | 19.9% | 18.5 to 21.5 |
| Ambiguous labels excluded, within 12 months | 2,743 | 603 | 22.0% | 20.5 to 23.6 |
| All 86 companies, within 12 months | 3,302 | 727 | 22.0% | 20.6 to 23.5 |

No variant moves the picture: about 6% per quarter, about 20 to 22% within 12 months.

## 10. What went wrong

| Defect | Effect | Fix | Rule that now prevents it |
|---|---|---|---|
| **Survivorship: only companies still rated in 2025 are in the company folders.** Retailers whose ratings were withdrawn before then (Abercrombie & Fitch, Birkenstock, Sportsman's Warehouse, Sprouts, Vince, Pep Boys, Bon-Ton, Sears, Toys 'R' Us) are in the frame but have no folder | companies that defaulted or were bought out are missing, so downgrades, large moves and the Caa end are under-counted. This may be why upgrades (101) outnumber downgrades (87), against the stated expectation | not fixed. Their rating histories are in the local Moody's files; building folders for them is a free follow-up | the specification template's limitations must now name how companies entered the sample |
| Specification 0.1 described bond switches as visible in `label_oi`; they are not | none on results; found by the tests before the run | corrected to version 0.2 before the run | tests before every run (P13) |
| The first run attempt crashed in table T6 on a missing field | nothing written; the run folder did not exist yet | fixed; a whole-analysis test added | same |
| In chat on 2026-09-26 the Kohl's switch was described as one notch; it is two (Baa2 to Ba1) | none on results | test corrected | |

Expectations written in the specification, checked:

| Expectation | Result |
|---|---|
| Speculative grade changes more often than investment grade | confirmed: 9.1% against 3.5% per quarter |
| Downgrades outnumber upgrades | not confirmed: 87 against 101; likely affected by survivorship |
| Changes concentrate in few companies | not confirmed: 59 of 72 companies changed; the top ten hold 34% |

## 11. Decipher and encode

| | What this study adds |
|---|---|
| Decipher | Three measured regularities of Moody's behaviour: the chance of a change rises steeply as the rating falls; a change is almost always one notch; a change raises the chance of another in the same direction. None of these comes from filings; they come from the rating history alone |
| Encode | nothing encoded. These regularities define the baselines a change detector must beat before it adds anything |

## 12. Decisions for consensus

| # | Decision | Options | Proposed |
|---|---|---|---|
| 1 | Horizon of a change test | next quarter (6% base rate); within 12 months (22%) | within 12 months: it matches annual filings, the imbalance is moderate, and an alarm can be right most of the time |
| 2 | Baselines a change detector must beat | persistence only; plus a rating-level rule (flag speculative grade) and a momentum rule (flag after a change) | all three |
| 3 | Survivorship | accept; build folders for the withdrawn-rating retailers and rerun | rerun with them before using these rates in a report to the chair |
| 4 | Source of changed cases for testing an LLM | historical cases (in the models' training data); post-cutoff cases from the chair's histories; an older window with an older model | unchanged from the 2026-09-18 specification: this study does not solve it |

## Appendix: changes per company, primary cohort

| Company | Quarters | Changes | Upgrades | Downgrades | Largest move |
|---|---|---|---|---|---|
| J.Jill | 40 | 9 | 6 | 3 | 2 |
| National Vision | 45 | 8 | 5 | 3 | 1 |
| Petco | 50 | 7 | 3 | 4 | 2 |
| Albertsons | 51 | 6 | 4 | 2 | 5 |
| Leslie's | 33 | 6 | 2 | 4 | 2 |
| Macy's | 51 | 6 | 3 | 3 | 2 |
| PetSmart | 41 | 6 | 3 | 3 | 2 |
| Wolverine World Wide | 51 | 6 | 2 | 4 | 2 |
| Bath & Body Works | 51 | 5 | 2 | 3 | 2 |
| BJ's Wholesale Club | 51 | 5 | 4 | 1 | 2 |
| Carvana | 27 | 5 | 3 | 2 | 3 |
| Gap | 51 | 5 | 2 | 3 | 2 |
| Hanesbrands | 51 | 5 | 2 | 3 | 1 |
| Kohl's | 51 | 5 | 0 | 5 | 2 |
| Michaels | 38 | 5 | 0 | 5 | 1 |
| Under Armour | 36 | 5 | 1 | 4 | 2 |
| V.F. | 51 | 5 | 0 | 5 | 1 |
| Nordstrom | 51 | 4 | 0 | 4 | 1 |
| Qurate/QVC | 51 | 4 | 1 | 3 | 2 |
| Signet | 44 | 4 | 1 | 3 | 1 |
| Walgreens | 51 | 4 | 0 | 4 | 2 |
| Whole Foods Market | 38 | 4 | 4 | 0 | 2 |
| Advance Auto Parts | 51 | 3 | 1 | 2 | 1 |
| Dillard's | 51 | 3 | 3 | 0 | 1 |
| Dollar General | 51 | 3 | 2 | 1 | 1 |
| Dollar Tree | 41 | 3 | 3 | 0 | 1 |
| Foot Locker | 51 | 3 | 1 | 2 | 1 |
| JD.com | 36 | 3 | 3 | 0 | 1 |
| Levi Strauss | 51 | 3 | 3 | 0 | 1 |
| RH | 15 | 3 | 0 | 3 | 2 |
| Staples | 51 | 3 | 0 | 3 | 5 |
| Torrid | 16 | 3 | 1 | 2 | 1 |
| Ahold Delhaize | 51 | 2 | 2 | 0 | 1 |
| Asbury Automotive | 51 | 2 | 2 | 0 | 1 |
| Best Buy | 51 | 2 | 2 | 0 | 1 |
| Floor & Decor | 35 | 2 | 2 | 0 | 1 |
| Ingles Markets | 51 | 2 | 2 | 0 | 1 |
| O'Reilly | 51 | 2 | 2 | 0 | 1 |
| Penske Automotive | 51 | 2 | 2 | 0 | 1 |
| PVH | 51 | 2 | 2 | 0 | 1 |
| Ralph Lauren | 51 | 2 | 1 | 1 | 1 |
| Sally Beauty | 51 | 2 | 2 | 0 | 1 |
| Sonic Automotive | 51 | 2 | 2 | 0 | 1 |
| Tiffany | 43 | 2 | 2 | 0 | 4 |
| 7-Eleven | 51 | 1 | 0 | 1 | 1 |
| Amer Sports | 5 | 1 | 1 | 0 | 1 |
| AutoNation | 51 | 1 | 1 | 0 | 1 |
| AutoZone | 51 | 1 | 1 | 0 | 1 |
| Canada Goose | 19 | 1 | 1 | 0 | 1 |
| Costco | 51 | 1 | 1 | 0 | 1 |
| Dick's Sporting Goods | 13 | 1 | 1 | 0 | 1 |
| Group 1 Automotive | 51 | 1 | 1 | 0 | 1 |
| Home Depot | 51 | 1 | 1 | 0 | 1 |
| Kroger | 51 | 1 | 1 | 0 | 1 |
| Lowe's | 51 | 1 | 0 | 1 | 1 |
| Men's Wearhouse | 18 | 1 | 1 | 0 | 3 |
| Murphy USA | 47 | 1 | 1 | 0 | 1 |
| Ross Stores | 43 | 1 | 1 | 0 | 1 |
| TJX | 51 | 1 | 1 | 0 | 1 |
| 13 companies, listed in 5.3 | | 0 | 0 | 0 | 0 |
