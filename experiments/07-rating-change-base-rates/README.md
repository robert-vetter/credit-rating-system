# Experiment 07: how often and how much Moody's ratings change, specification

*Written 2026-09-26 by Claude (Opus 5.5), directed by Robert Vetter. Version 0.2, fixed before the run; 0.1 misdescribed the bond switch (section 8). Follows [EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Checked against: the
observation builder `evaluation/pipeline/build_observations.py`, the field inventory of the 86
local `ratings.json` and `observations.json` files (read 2026-09-26: rating records carry only
rating, action date, action code and rating type; action codes present are NW, HS, UP, DG, WE, WO), [evaluation/observations-summary.md](../../evaluation/observations-summary.md)
and [evaluation/rating-history-file.md](../../evaluation/rating-history-file.md). No result has
been computed yet.*

State: run 2026-09-26 (Robert's decisions 1 to 3 in `decisions.md`). Results in `results.md`.

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | How often, by how many notches, in which direction and for which companies do Moody's Retail and Apparel ratings change, in the official rating history from June 2012 to August 2025? |
| Null hypothesis | None. This is a descriptive study. Expectations written down before counting, to be checked and not tuned: speculative grade changes more often than investment grade; downgrades outnumber upgrades; changes concentrate in few companies |
| Target | the rating change, under the definitions of section 8 |
| Unit of observation | company-quarter (primary); company-year and company-quarter with a 12-month forward window (secondary); the individual rating action (complementary count) |
| What it is | a count of the label data: the base rate the imbalance question rests on |
| What it is not | a model test; no LLM is called. Not evidence that changes are predictable. Not a test of any system |
| Place in the programme | decipher: the first measured fact about how Moody's behaves over time. Design input: the base rate and change profile needed to specify a balanced test set in a later experiment. Answers Xiaowei's review of 2026-09-17, point 2, with data |

How the result will be used:

| Use | Where |
|---|---|
| Answer "how imbalanced, and how much does a rating move" in a table | next report to the chair |
| Choose the changed/unchanged ratio, horizon and strata of a balanced test set | a later specification; this study only reports what is available |
| State what precision a change detector could reach at the real base rate | section 9, table T8 |

## 2. Dates

| Date concept | Value | Source |
|---|---|---|
| Moody's 17g-7 files | dated 2026-08-11 | `data/moodys/`, downloaded by Robert |
| Rating history start (action code HS) | 2012-06-15 | same |
| Latest rating action in the files | August 2025 (twelve-month embargo) | [rating-history-file.md](../../evaluation/rating-history-file.md), finding 1 |
| Quarterly grid | 2012-09-30 to 2025-06-30, 52 quarter ends | `build_observations.py` |
| Model training cutoff | not applicable, no model | |
| Post-cutoff window, September 2025 to August 2026 | not covered by these files; two known changes there (Nike 2025-11-12, Qurate October 2025) | [2026-09-18 specification](../../reports/2026-09-18-specification/SPECIFICATION.md), section 4 |

## 3. Sample and data characteristics

### 3.1 How the sample is built

| Step | Count | Where |
|---|---|---|
| Moody's Retail and Apparel entities joined to SEC filers | 186 | `evaluation/mapping.json` |
| Company folders | 86 | `evaluation/companies/` |
| Companies with at least one observation | 85 (Gildan has none) | observations-summary.md |
| Scope of the 86: in / uncertain / out | 73 / 4 / 9 | `observations.json`, field `scope` |
| Company-quarters, all | 3,646 | observations-summary.md |
| Company-quarters in scope | 3,084 | same |
| Primary cohort | in-scope company-quarters (DECISION 2) | |

### 3.2 Label characteristics, known before counting

| Characteristic | Value |
|---|---|
| Label level | entity rating (corporate family or issuer rating) 2,223 company-quarters; senior unsecured instrument 1,423 |
| Ambiguous labels (group members disagree) | 41 company-quarters |
| Changed against the previous quarter, all companies | 218 of 3,646 (6.0%), already reported; recomputed here under section 8 |
| Gold-set observations inside the grid | 50, included because nothing is fitted (DECISION 4) |

### 3.3 Imbalance plan

This study measures the imbalance itself. It reports the base rate under every definition in
section 8, and how many changed cases each design of a balanced set could draw on. It does not
select a test set.

### 3.4 Input characteristics

| Characteristic | Value |
|---|---|
| Files read | 86 `ratings.json`, 86 `observations.json`, local, derived from the 17g-7 files |
| Rating record fields | rating (R), action date (RAD), action code (RAC), rating type (RT); no outlook, no review for upgrade or downgrade |
| Filings, XBRL, model inputs | not used |

## 4. Per-observation table

Not applicable. Results are published as aggregate and per-company counts (table T4 in section 9;
DECISION 5 on granularity).

## 5. Models and settings

No model call. No API key is read. Cost $0.

## 6. Inputs

| Input | Content | Rule |
|---|---|---|
| `observations.json` per company | quarterly label, persistence, change flag, signed notch change, label level, ambiguity flag, scope | used as built; not regenerated |
| `ratings.json` per company | entity and instrument rating records with action dates and codes | used for the action-level count and withdrawals |

Both are frozen by hash before the count (pre-check P5).

## 7. Prompt and output

Not applicable.

## 8. Definitions and the calculation

All counts are computed by one script, `run_study.py`, covered by tests on hand-built fixtures.

| Term | Definition |
|---|---|
| Notch scale | 21 notches, Aaa = 0 to C = 20, as `SCALE` in `build_observations.py`. A higher number is a worse rating |
| Label at t | the rating in effect at quarter end t, as built: the entity rating where one is alive, else the freshest senior unsecured instrument rating |
| Quarterly change (primary) | label at t differs from the label at the previous quarter end. Size is the signed notch difference; positive is a downgrade, negative an upgrade |
| Annual change | label at a year end (Q4) differs from the label at the previous year end |
| Change within 12 months | at least one quarterly change in the four quarters after t. This is the horizon a change-detection system would work on |
| Three-year change | label at t differs from the label twelve quarters earlier |
| Large move | absolute size of two notches or more |
| Level switch | the label level (entity or instrument) differs between t-1 and t. Counted as a change if the notch differs, flagged, and reported separately (DECISION 3) |
| Rating action | an upgrade (UP) or downgrade (DG) record on the entity or senior unsecured line of the company. Records on several instruments with the same date and same new rating count as one action. Catches moves that reverse within a quarter and are invisible on the grid |
| Withdrawal | the company's label stops existing (the rating value becomes WR, with action code WE or WO, on every line that carried the label). Counted separately; never counted as a change. An instrument withdrawn at maturity while the company stays rated is not a company event |
| Gap | a quarter with no label. The builder then leaves the next quarter without a previous rating, so that quarter drops out of the change denominator. Gaps are counted in T7 |
| Label source switch | the rated entity behind the label (field `label_oi`) changes between t-1 and t, for example between members of a group. A switch between bonds of the same entity is not visible in this field: because the label rule takes the most recently dated live record, a new bond issued at a different rating moves the label without any rating action. Such cases are counted in T7 as grid changes without a rating action (correction of 2026-09-26, found by the tests before the run) |
| Investment grade | Baa3 or better at t-1 |
| Follow-on change | a change within four quarters after a change, split into same direction and reversal |

## 9. Tables to produce

Every rate is given with its count, its denominator and a 95% Wilson interval. The headline rate
also gets a company-level bootstrap interval, because changes cluster within companies.

| # | Table | Rows and columns |
|---|---|---|
| T1 | Base rate by horizon | quarter, year, within 12 months, three years × n, changed, %, upgrades, downgrades |
| T2 | Size of changes | 1, 2, 3+ notches × upgrades, downgrades |
| T3 | By rating at t-1 | Aa, A, Baa, Ba, B, Caa and investment/speculative grade × n, change rate, upgrade rate, downgrade rate; plus a one-year transition matrix between categories |
| T4 | By company | observations, changes, upgrades, downgrades, largest move; companies that never changed; share of all changes from the ten most active companies |
| T5 | By year | 2012 to 2025 × n, changes, rate |
| T6 | Follow-on changes | rate of a change within four quarters after a change, same direction and reversal, against the unconditional rate |
| T7 | Data artefacts | level switches, label source switches, ambiguous labels, withdrawals, gaps, actions invisible on the quarterly grid |
| T8 | What this means for a balanced test set | changed cases available under each horizon and scope; example precision of a detector with stated sensitivity and specificity at the measured base rate |

Sensitivities, each reported next to the primary result: all 86 companies instead of in-scope
only; level switches excluded; ambiguous labels excluded.

## 10. Controls and pre-checks

| # | Check | Applies? | Evidence |
|---|---|---|---|
| P1 | Specification reviewed by the other model family | yes | `review-codex-*.md` |
| P2 | Chair consensus or Robert's written decision to proceed | yes (DECISION 6) | `decisions.md` |
| P3 | Authorization and cap | no, no spend | |
| P4 | Cohort frozen: company list, scope, grid | yes | run folder |
| P5 | Inputs frozen: hashes of the 172 input files | yes | run folder |
| P6 | Point-in-time audit | no model; the observation builder's rules apply as built | |
| P7 to P12, P14 | Redaction, tools, tokens, price, cutoff, probe, pilot | no model | |
| P13 | Tests: fixtures for a level switch, a label source switch, a company withdrawal, a bond maturing while the company stays rated, a gap, a reversal within a quarter, several instruments moving together, the first observation of a company | yes | `test_study.py` |

## 11. Budget

$0. No API calls, no downloads.

## 12. Known limitations before the run

| Limitation | Effect |
|---|---|
| One sector, 86 companies, 2012 to 2025 | rates may differ in other sectors and after 2025 |
| No outlooks or reviews in the files | early warning signals cannot be studied from this source |
| Quarter-end grid | reversals within a quarter are invisible; the action count complements it |
| Label mixes entity and instrument ratings | a level switch can look like a change; flagged and reported separately |
| Companies enter and leave (new ratings, withdrawals, defaults) | coverage per company is uneven, from 4 to 52 quarters |
| Five scope calls still open (CVS, Samsonite, Good Sam, Amazon, Sherwin-Williams) | sensitivity on all 86 covers them |
| Every change in these files predates the training cutoff of current LLMs | fine for counting and for analysis without a model; these changes cannot test an LLM out of sample |
| Descriptive only | no claim that any change was predictable |

## 13. Decisions that need consensus before the run

| # | Decision | Options | Proposed | Agreed (who, date) |
|---|---|---|---|---|
| 1 | Headline horizon | quarter; year; within 12 months | quarter, for continuity with the 6.0% already reported, with the 12-month rate next to it as the horizon relevant for detection | |
| 2 | Primary cohort | in-scope companies; all 86 | in-scope, all 86 as sensitivity | |
| 3 | Level switches | count as changes; exclude | count when the notch differs, flag, and report without them as a sensitivity | |
| 4 | Gold-set observations | include; exclude | include, because nothing is fitted or tuned | |
| 5 | What goes into the public repository | aggregate tables and per-company counts; full rating paths | aggregates and per-company counts only, while the Moody's terms of use are open | |
| 6 | Consensus before running | send this specification to the chair first; Robert decides to run now because it uses no model, no money and changes no label | Robert's decision | |
| 7 | Numbering | this study is 07; the GPT-5.2 run proposed as "Experiment 07" in the 2026-09-18 specification takes the next free number when it starts | as stated | |

## 14. Definitions for the report

| Term | Meaning | Example |
|---|---|---|
| Base rate | share of observations with a change under a stated definition | 218 of 3,646 company-quarters changed against the previous quarter: 6.0% |
| Persistence | predicting that the rating stays what it was | at 6.0% base rate, persistence is right 94% of the time on quarters |
| Notch | one step on Moody's 21-step scale | A1 to A2 is one notch down |
| Balanced test set | a test set with a chosen share of changed cases, larger than the natural rate, plus matched unchanged cases | 30 changed and 20 unchanged in the frozen gold set |
| Precision at the base rate | share of alarms that are real changes | a detector that finds 90% of changes and wrongly flags 10% of stable companies is right on about 1 alarm in 3 at a 6% base rate |
