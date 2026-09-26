# Experiment 07: results

*Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Follows section 6 of
[EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Verified against run R2-2026-09-26
(`runs/R2-2026-09-26/`: manifest with 320 input hashes, results.json, tables.md, the post-hoc
direction check), its rebuilt inputs (`runs/R2-inputs-withdrawn/`) and run R1-2026-09-26, the
survivors-only run it corrects. Independent post-run audit: waived by Robert for this study
(decision 2). 17 tests pass.*

This note replaces the version written after run R1 on the same day. R1 contained only companies
still rated in 2025 (section 10). R2 adds the 74 groups whose ratings were withdrawn earlier and
is the result. The R1 figures appear as the survivors-only comparison.

## 1. Summary

| Item | Answer |
|---|---|
| Question | How often, by how much and in which direction do Moody's Retail and Apparel ratings change, 2012 to 2025? |
| Next quarter (target horizon, decision 5) | 7.8% of company-quarters change; persistence is right on 92.2% |
| Within 12 months (context) | 26.7% change; persistence is right on 73.3% |
| Size | 81% of changes are one notch |
| Strongest pattern | the rating level: next-quarter change rate 2.5% at A, 4.4% at Baa, 7.1% at Ba, 12.9% at B, 18.5% at Caa |
| Survivorship | companies whose rating was later withdrawn change twice as often as survivors (12.7% against 6.2% per quarter) |

## 2. Headline

Primary cohort: every in-scope group with quarterly records, active or withdrawn (125
companies). Persistence is the complement of the change rate.

| Horizon | n | Changed | Change rate (95% Wilson) | Company bootstrap | Persistence right | Upgrades | Downgrades |
|---|---|---|---|---|---|---|---|
| **Next quarter** | 4,002 | 314 | **7.8%** (7.1 to 8.7) | 6.7 to 9.1 | 92.2% | 145 | 169 |
| Year, Q4 to Q4 | 905 | 245 | 27.1% (24.3 to 30.1) | | 72.9% | 125 | 120 |
| Within the next 12 months | 3,614 | 965 | 26.7% (25.3 to 28.2) | 23.1 to 30.6 | 73.3% | 506 | 485 |
| Three years | 2,697 | 1,367 | 50.7% (48.8 to 52.6) | | 49.3% | 753 | 614 |

For the 12-month and three-year rows, upgrades and downgrades count windows containing at least
one move in that direction; a window with both counts twice.

How much the missing companies mattered:

| Cohort | Companies | Next quarter | Within 12 months | Three years |
|---|---|---|---|---|
| Survivors only (run R1) | 72 | 6.2% | 22.1% | 45.9% |
| Withdrawn-rating companies only | 53 | 12.7% | 42.2% | 73.2% |
| **Both (primary)** | 125 | **7.8%** | **26.7%** | **50.7%** |
| All groups regardless of scope | | 7.5% | 26.0% | 51.2% |

## 3. Dates

| Date concept | Value |
|---|---|
| Moody's files | dated 2026-08-11, actions through August 2025 |
| Quarterly grid | 2012-09-30 to 2025-06-30 |
| Runs | R1 and R2, both 2026-09-26 |

## 4. Input data characteristics

| Characteristic | Value |
|---|---|
| Confirmed mapping groups | 161; 86 with an active rating at the file end (existing folders), 75 without |
| Rebuilt for R2 | 74 withdrawn-rating groups; 1 skipped (CDW CORPORATION, an earlier entity of CDW, out of scope) |
| Companies in the primary cohort with quarterly records | 125 (72 survivors, 53 withdrawn-rating) |
| In-scope rebuilt groups that contribute no quarterly record | 5: Toys 'R' Us and Birkenstock carry only secured-debt ratings in the files, which the label rule does not use; Oxford Industries was withdrawn in July 2012, before the grid; Claire's and Destination Maternity have a single labelled quarter (the Claire's entity in the files is the one rated after its 2018 bankruptcy) |
| Quarterly records (a label at t and at t-1) | 4,002 |
| Companies whose rating ends before 2025-06-30 | 54 |
| Gap quarters | 64 |
| Rating actions on the line that carries the label | 302 |
| Input files hashed | 320 |

## 5. Results in detail

### 5.1 Next quarter, by rating at the start of the quarter

The table for a next-quarter predictor. Rates are per company-quarter.

| Rating | Quarters | Any change (95% Wilson) | Downgrade | Upgrade | Change within 12 months |
|---|---|---|---|---|---|
| Aa | 83 | 0.0% (0.0 to 4.4) | 0.0% | 0.0% | 0.0% |
| A | 439 | 2.5% (1.4 to 4.4) | 0.7% | 1.8% | 10.7% |
| Baa | 1,051 | 4.4% (3.3 to 5.8) | 2.4% | 2.0% | 16.8% |
| Ba | 1,229 | 7.1% (5.8 to 8.7) | 3.7% | 3.3% | 24.2% |
| B | 923 | 12.9% (10.9 to 15.2) | 7.7% | 5.2% | 44.8% |
| Caa | 260 | 18.5% (14.2 to 23.6) | 8.8% | 9.6% | 58.5% |
| Ca to C | 17 | 17.6% (6.2 to 41.0) | 5.9% | 11.8% | 50.0% (6 windows) |
| Investment grade | 1,573 | 3.6% (2.8 to 4.7) | 1.8% | 1.8% | 14.2% |
| Speculative grade | 2,429 | 10.6% (9.4 to 11.9) | 5.8% | 4.8% | 35.4% |

The 12-month column by rating was added while writing the analysis code, before any result
was seen. The downgrade and upgrade columns were computed from the saved counts after the run.

### 5.2 Size of changes, next quarter

| Notches | Upgrades | Downgrades | Total | Share |
|---|---|---|---|---|
| 1 | 130 | 125 | 255 | 81.2% |
| 2 | 11 | 35 | 46 | 14.6% |
| 3 or more | 4 | 9 | 13 | 4.1% |
| Total | 145 | 169 | 314 | |

Mean size 1.26 notches. Downgrades are larger: 44 of 169 downgrades moved two or more notches,
against 15 of 145 upgrades.

### 5.3 One-year moves between categories (Q4 to Q4, counts)

| From \ to | Aa | A | Baa | Ba | B | Caa | Ca-C |
|---|---|---|---|---|---|---|---|
| Aa | 19 | | | | | | |
| A | 2 | 98 | 2 | | | | |
| Baa | | 4 | 233 | 9 | 2 | | |
| Ba | | | 6 | 254 | 14 | 3 | |
| B | | | | 21 | 154 | 25 | |
| Caa | | | | | 18 | 38 | 2 |
| Ca-C | | | | | | | 1 |

The diagonal is "stayed in the category" and includes notch moves inside it.

### 5.4 By company

| Item | Value |
|---|---|
| Companies with at least one change | 98 of 125 |
| Never changed | 27, among them Walmart, Target, Nike (until its 2025-11-12 downgrade, after the file ends), Tapestry, Tractor Supply |
| Share of all changes from the ten most active companies | 23.2% |
| Median company change rate per quarter | 7.3% |

Changes are spread across most companies. The full per-company table is in the appendix.

### 5.5 By year

| Year | Quarters | Changed | Rate | Upgrades | Downgrades |
|---|---|---|---|---|---|
| 2012 (Q4 only) | 70 | 3 | 4.3% | 0 | 3 |
| 2013 | 293 | 29 | 9.9% | 18 | 11 |
| 2014 | 312 | 17 | 5.4% | 13 | 4 |
| 2015 | 327 | 29 | 8.9% | 23 | 6 |
| 2016 | 336 | 16 | 4.8% | 8 | 8 |
| 2017 | 343 | 31 | 9.0% | 8 | 23 |
| 2018 | 333 | 26 | 7.8% | 15 | 11 |
| 2019 | 331 | 18 | 5.4% | 5 | 13 |
| 2020 | 301 | 42 | 14.0% | 13 | 29 |
| 2021 | 302 | 28 | 9.3% | 22 | 6 |
| 2022 | 306 | 19 | 6.2% | 7 | 12 |
| 2023 | 300 | 27 | 9.0% | 4 | 23 |
| 2024 | 301 | 17 | 5.6% | 7 | 10 |
| 2025 (Q1 and Q2) | 147 | 12 | 8.2% | 2 | 10 |

Direction follows the cycle: mostly upgrades 2013 to 2015 and 2021, mostly downgrades in 2017
(retail store closures), 2020 and from 2023 on.

### 5.6 Follow-on changes

| Starting quarter | n | Another change within 4 quarters | Rate (95% Wilson) |
|---|---|---|---|
| After a change | 255 | 97 | 38.0% (32.3 to 44.1) |
| After no change | 3,234 | 837 | 25.9% (24.4 to 27.4) |

After a change, the next move is usually in the same direction: 80 windows had another move in
the same direction, 22 a reversal.

### 5.7 Ratings that end

54 companies' ratings end before 2025-06-30. The files carry no reason: a withdrawal can follow
a default, a buyout or the repayment of all rated debt.

| Last rating | Companies |
|---|---|
| Baa | 1 |
| Ba | 12 |
| B | 18 |
| Caa | 18 |
| Ca to C | 5 |

23 of the 54 end at Caa or below, the zone where defaults happen (Sears Holdings, Gymboree,
Bon-Ton, Ascena, Guitar Center, Party City and others). A default followed by a withdrawal is not counted as a change under the definitions, so
the default itself is invisible in the change rates. The full list is in `tables.md` of run R2.

### 5.8 What this means for a next-quarter predictor

| Item | Value |
|---|---|
| Changed company-quarters available | 314, from 98 companies |
| All of these are before the training cutoff of current LLMs | usable for counting and for analysis without a model, not as an out-of-sample LLM test |

How often an alarm would be right, for an illustrative detector:

| Framing | Base rate | Finds changes | Correct on stable | Alarm is right |
|---|---|---|---|---|
| Next quarter, all ratings | 7.8% | 90% | 90% | 43.4% |
| Next quarter, all ratings | 7.8% | 80% | 95% | 57.7% |
| Within 12 months | 26.7% | 90% | 90% | 76.6% |
| Within 12 months | 26.7% | 80% | 95% | 85.4% |

At the next-quarter horizon most alarms are false unless the detector is very specific, because
92% of quarters do not change. The rating level already sorts companies: a B-rated company is
five times as likely to change next quarter as an A-rated one.

## 6. Model, settings and cost

No model. $0. Seed 20260926, 2,000 company bootstrap resamples.

## 7. Coverage

| Item | Count |
|---|---|
| Quarterly records | 4,002 |
| 12-month windows kept | 3,614 |
| 12-month windows censored (last four quarters of each company, gaps, ratings that end) | 522 |
| Annual pairs | 905 |
| Three-year pairs | 2,697 |

## 8. Where a counted change may not be a real change

| Check | Count | Meaning |
|---|---|---|
| Change agrees with a rating action on the label line in the same direction | 290 of 314 | real |
| Change with no rating action on the label line | 21 | all coincide with a level or entity switch; mostly companies falling from investment grade that receive a new corporate family rating. Direction real, size measured across two rating types |
| Change contradicting the action | 3 | all coincide with a switch (Albertsons 2015 during the Safeway merger among them) |
| Level switches | 30 (27 with a change) | |
| Entity switches | 15 (12 with a change) | |
| Ambiguous labels | 43 records | |
| Reversal inside a quarter, invisible on the grid | 1 | |
| Quarters with two or more actions | 8 | |

The direction check (first three rows) is post-hoc: added after reading run R1, prompted by the
Albertsons case, saved separately (`posthoc_direction.py`).

## 9. Sensitivities

| Variant | n | Changed | Rate | 95% Wilson |
|---|---|---|---|---|
| Primary, next quarter | 4,002 | 314 | 7.8% | 7.1 to 8.7 |
| Level switches excluded, next quarter | 3,972 | 287 | 7.2% | 6.5 to 8.1 |
| Ambiguous labels excluded, next quarter | 3,959 | 309 | 7.8% | 7.0 to 8.7 |
| Survivors only (R1), next quarter | 3,011 | 188 | 6.2% | 5.4 to 7.2 |
| Withdrawn-rating companies only, next quarter | 991 | 126 | 12.7% | 10.8 to 14.9 |
| All groups regardless of scope, next quarter | 4,792 | 359 | 7.5% | 6.8 to 8.3 |
| Primary, within 12 months | 3,614 | 965 | 26.7% | 25.3 to 28.2 |
| Level switches excluded, within 12 months | 3,511 | 871 | 24.8% | 23.4 to 26.3 |

Only the cohort matters: excluding switches or ambiguous labels moves the rate by less than a
percentage point; leaving out the withdrawn-rating companies moves it by 1.6 points per quarter
and 4.6 points over 12 months.

## 10. What went wrong

| Defect | Effect | Fix | Rule that now prevents it |
|---|---|---|---|
| **Run R1 saw survivors only.** `compile_folders.py` writes folders only for groups with an active rating at the file end; 75 of 161 confirmed groups were skipped, 58 in scope | R1 understated the change rate (6.2% against 7.8% per quarter) and showed more upgrades than downgrades (101 against 87); with all companies, downgrades lead (169 against 145) | the skipped groups rebuilt for R2 inside the run folder; `evaluation/companies/` unchanged | the specification template's limitations must name how companies entered the sample, and whether companies that left are included |
| Specification 0.1 described bond switches as visible in `label_oi`; they are not | none; found by the tests before R1 | corrected to version 0.2 before R1 | tests before every run (P13) |
| The label rule reads only company-wide ratings and senior unsecured bonds | companies rated only on secured debt (Toys 'R' Us, Birkenstock) are invisible, in R1 and R2 alike | not fixed; a label rule for secured-only issuers is a separate decision | limitations name the label rule's coverage |
| The first R1 attempt crashed in table T6 on a missing field | nothing written | fixed; a whole-analysis test added | same |
| The rebuild first collided with an existing folder (CDW) | none; found by the tests before R2 | the builder skips and lists such groups | same |
| In chat on 2026-09-26 the Kohl's switch was described as one notch; it is two (Baa2 to Ba1) | none on results | test corrected | |

Expectations written in the specification, checked on R2:

| Expectation | Result |
|---|---|
| Speculative grade changes more often than investment grade | confirmed: 10.6% against 3.6% per quarter |
| Downgrades outnumber upgrades | confirmed on the full cohort: 169 against 145 per quarter; not on survivors alone |
| Changes concentrate in few companies | not confirmed: 98 of 125 companies changed; the top ten hold 23% |

## 11. Decipher and encode

| | What this study adds |
|---|---|
| Decipher | Four measured regularities of Moody's behaviour: the chance of a change rises steeply as the rating falls; a change is almost always one notch, and large moves are mostly downgrades; a change raises the chance of another in the same direction; the direction follows the economic cycle. All come from the rating history alone, not from filings |
| Encode | nothing encoded. These regularities define the baselines a next-quarter predictor must beat |

## 12. Decisions for consensus

| # | Decision | Options | State |
|---|---|---|---|
| 1 | Horizon of the predictor | next quarter; 12 months | **decided by Robert 2026-09-26: next quarter** (decision 5) |
| 2 | Baselines a next-quarter predictor must beat | persistence only; plus a rating-level rule (section 5.1) and a momentum rule (section 5.6) | proposed: all three |
| 3 | Survivorship | accept; rebuild the withdrawn-rating companies | **done in R2** (decision 4) |
| 4 | Source of changed cases for testing an LLM | historical cases (in the models' training data); post-cutoff cases from the chair's histories; an older window with an older model | open, as in the 2026-09-18 specification |
| 5 | Unit of observation for the uses Robert described (faster agency reviews, trading ahead of an action) | calendar quarter end, as here; each filing or disclosure, with the rating action dated to the day | open; the 17g-7 files date every action to the day, so a filing-based design is possible |
| 6 | Ratings that end at Caa or below | leave as withdrawals; treat as default events from a default source | open; needs a source that says which withdrawals were defaults |

## Appendix: changes per company, primary cohort (run R2)

| Company | Scope | Quarters | Changes | Upgrades | Downgrades | Largest move |
|---|---|---|---|---|---|---|
| j-jill | in | 40 | 9 | 6 | 3 | 2 |
| joann | in | 45 | 9 | 3 | 6 | 3 |
| party-city | in | 41 | 9 | 4 | 5 | 2 |
| national-vision | in | 45 | 8 | 5 | 3 | 1 |
| old-copper-company | in | 30 | 7 | 2 | 5 | 3 |
| petco | in | 50 | 7 | 3 | 4 | 2 |
| albertsons | in | 51 | 6 | 4 | 2 | 5 |
| caleres | in | 37 | 6 | 4 | 2 | 1 |
| guitar-center | in | 32 | 6 | 2 | 4 | 2 |
| leslie-s-poolmart | in | 33 | 6 | 2 | 4 | 2 |
| macy-s | in | 51 | 6 | 3 | 3 | 2 |
| petsmart | in | 41 | 6 | 3 | 3 | 2 |
| rite-aid | in | 51 | 6 | 3 | 3 | 2 |
| wolverine-world-wide | in | 51 | 6 | 2 | 4 | 2 |
| ascena-retail-group | in | 22 | 5 | 0 | 5 | 2 |
| bath-body-works | in | 51 | 5 | 2 | 3 | 2 |
| bj-s-wholesale-club | in | 51 | 5 | 4 | 1 | 2 |
| carvana | in | 27 | 5 | 3 | 2 | 3 |
| fresh-market-inc-the | in | 24 | 5 | 2 | 3 | 1 |
| gap-inc-the | in | 51 | 5 | 2 | 3 | 2 |
| general-nutrition-centers | in | 30 | 5 | 2 | 3 | 3 |
| hanesbrands | in | 51 | 5 | 2 | 3 | 1 |
| jones-group-inc-the | in | 22 | 5 | 0 | 5 | 5 |
| kohl-s | in | 51 | 5 | 0 | 5 | 2 |
| michaels | in | 38 | 5 | 0 | 5 | 1 |
| under-armour | in | 36 | 5 | 1 | 4 | 2 |
| v-f | in | 51 | 5 | 0 | 5 | 1 |
| abercrombie-fitch | in | 39 | 4 | 3 | 1 | 1 |
| gamestop | in | 26 | 4 | 1 | 3 | 3 |
| nordstrom | in | 51 | 4 | 0 | 4 | 1 |
| qurate-qvc | in | 51 | 4 | 1 | 3 | 2 |
| signet | in | 44 | 4 | 1 | 3 | 1 |
| true-religion-apparel | in | 15 | 4 | 0 | 4 | 2 |
| walgreens | in | 51 | 4 | 0 | 4 | 2 |
| whole-foods-market | in | 38 | 4 | 4 | 0 | 2 |
| advance-auto-parts | in | 51 | 3 | 1 | 2 | 1 |
| at-home-group | in | 15 | 3 | 0 | 3 | 2 |
| bon-ton | in | 21 | 3 | 1 | 2 | 2 |
| conn-s | in | 31 | 3 | 1 | 2 | 1 |
| dillard-s | in | 51 | 3 | 3 | 0 | 1 |
| dollar-general | in | 51 | 3 | 2 | 1 | 1 |
| dollar-tree | in | 41 | 3 | 3 | 0 | 1 |
| foot-locker | in | 51 | 3 | 1 | 2 | 1 |
| jd-com | in | 36 | 3 | 3 | 0 | 1 |
| levi-strauss | in | 51 | 3 | 3 | 0 | 1 |
| restoration-hardware | in | 15 | 3 | 0 | 3 | 2 |
| rue21 | in | 14 | 3 | 1 | 2 | 1 |
| sears-holdings | in | 20 | 3 | 1 | 2 | 1 |
| sprouts | in | 10 | 3 | 3 | 0 | 1 |
| staples | in | 51 | 3 | 0 | 3 | 5 |
| talbots-inc-the | in | 30 | 3 | 1 | 2 | 3 |
| torrid | in | 16 | 3 | 1 | 2 | 1 |
| ahold-delhaize | in | 51 | 2 | 2 | 0 | 1 |
| asbury-automotive-group | in | 51 | 2 | 2 | 0 | 1 |
| best-buy-co | in | 51 | 2 | 2 | 0 | 1 |
| bluestem-brands | in | 20 | 2 | 0 | 2 | 2 |
| fairway-group-holdings | in | 14 | 2 | 0 | 2 | 2 |
| family-dollar-stores | in | 21 | 2 | 1 | 1 | 2 |
| floor-decor | in | 35 | 2 | 2 | 0 | 1 |
| gymboree-corporation-the | in | 18 | 2 | 0 | 2 | 2 |
| hot-topic | in | 8 | 2 | 1 | 1 | 2 |
| ingles-markets-incorporated | in | 51 | 2 | 2 | 0 | 1 |
| kate-spade | in | 19 | 2 | 2 | 0 | 1 |
| lands-end | in | 26 | 2 | 0 | 2 | 1 |
| o-reilly | in | 51 | 2 | 2 | 0 | 1 |
| odp-corporation-the | in | 30 | 2 | 2 | 0 | 1 |
| orchard-supply | in | 2 | 2 | 0 | 2 | 1 |
| penske-automotive-group | in | 51 | 2 | 2 | 0 | 1 |
| pvh | in | 51 | 2 | 2 | 0 | 1 |
| radioshack | in | 9 | 2 | 0 | 2 | 1 |
| ralph-lauren | in | 51 | 2 | 1 | 1 | 1 |
| sally-beauty | in | 51 | 2 | 2 | 0 | 1 |
| sonic-automotive | in | 51 | 2 | 2 | 0 | 1 |
| tiffany | in | 43 | 2 | 2 | 0 | 4 |
| vince | in | 19 | 2 | 0 | 2 | 2 |
| 7-eleven | in | 51 | 1 | 0 | 1 | 1 |
| academy-sports-outdoors | in | 10 | 1 | 1 | 0 | 2 |
| amer-sports | in | 5 | 1 | 1 | 0 | 1 |
| autonation | in | 51 | 1 | 1 | 0 | 1 |
| autozone | in | 51 | 1 | 1 | 0 | 1 |
| burlington | in | 5 | 1 | 1 | 0 | 1 |
| canada-goose | in | 19 | 1 | 1 | 0 | 1 |
| costco-wholesale | in | 51 | 1 | 1 | 0 | 1 |
| cumberland-farms | in | 9 | 1 | 1 | 0 | 1 |
| dick-s-sporting-goods | in | 13 | 1 | 1 | 0 | 1 |
| great-atlantic-pacific-tea-co-inc-the | in | 8 | 1 | 0 | 1 | 1 |
| group-1-automotive | in | 51 | 1 | 1 | 0 | 1 |
| home-depot-inc-the | in | 51 | 1 | 1 | 0 | 1 |
| j-crew-group | in | 16 | 1 | 0 | 1 | 1 |
| kroger-co-the | in | 51 | 1 | 1 | 0 | 1 |
| lowe-s-companies | in | 51 | 1 | 0 | 1 | 1 |
| men-s-wearhouse-llc-the | in | 18 | 1 | 1 | 0 | 3 |
| murphy-usa | in | 47 | 1 | 1 | 0 | 1 |
| ross-stores | in | 43 | 1 | 1 | 0 | 1 |
| saks-incorporated | in | 4 | 1 | 1 | 0 | 1 |
| smart-final-stores | in | 20 | 1 | 0 | 1 | 1 |
| tjx-companies-inc-the | in | 51 | 1 | 1 | 0 | 1 |
| tops | in | 21 | 1 | 0 | 1 | 1 |
| arko | in | 14 | 0 | 0 | 0 | 0 |
| birkenstock | in | 0 | 0 | 0 | 0 | 0 |
| carter-s | in | 15 | 0 | 0 | 0 | 0 |
| cencosud-s-a | in | 51 | 0 | 0 | 0 | 0 |
| charlotte-russe-holding | in | 8 | 0 | 0 | 0 | 0 |
| claire-s-stores | in | 0 | 0 | 0 | 0 | 0 |
| container-store-group-inc-the | in | 14 | 0 | 0 | 0 | 0 |
| controladora-comercial-mexicana-s-a-b-de-c-v | in | 10 | 0 | 0 | 0 | 0 |
| crocs | in | 17 | 0 | 0 | 0 | 0 |
| cst-brands | in | 16 | 0 | 0 | 0 | 0 |
| david-s-bridal | in | 1 | 0 | 0 | 0 | 0 |
| destination-maternity | in | 0 | 0 | 0 | 0 | 0 |
| g-iii-apparel | in | 32 | 0 | 0 | 0 | 0 |
| gildan-activewear | in | 0 | 0 | 0 | 0 | 0 |
| kontoor-brands | in | 24 | 0 | 0 | 0 | 0 |
| lithia-motors | in | 31 | 0 | 0 | 0 | 0 |
| mattress-holding | in | 3 | 0 | 0 | 0 | 0 |
| nike | in | 51 | 0 | 0 | 0 | 0 |
| oxford-industries | in | 0 | 0 | 0 | 0 | 0 |
| pep-boys | in | 13 | 0 | 0 | 0 | 0 |
| perry-ellis-international | in | 22 | 0 | 0 | 0 | 0 |
| sears | in | 5 | 0 | 0 | 0 | 0 |
| sportsman-s-warehouse | in | 7 | 0 | 0 | 0 | 0 |
| stater-bros-holdings | in | 10 | 0 | 0 | 0 | 0 |
| tapestry | in | 41 | 0 | 0 | 0 | 0 |
| target | in | 51 | 0 | 0 | 0 | 0 |
| toys-r-us | in | 0 | 0 | 0 | 0 | 0 |
| tractor-supply | in | 18 | 0 | 0 | 0 | 0 |
| victoria-s-secret | in | 16 | 0 | 0 | 0 | 0 |
| vipshop-holdings-limited | in | 33 | 0 | 0 | 0 | 0 |
| walmart | in | 51 | 0 | 0 | 0 | 0 |
| warnaco | in | 1 | 0 | 0 | 0 | 0 |
| wayfair | in | 3 | 0 | 0 | 0 | 0 |
