# Experiment 08: decisions

*Every decision with its owner and date. Append only; a changed decision gets a new entry that
names the one it replaces. Open decisions are listed in the specification, section 13.*

| # | Date | Owner | Decision | Reason | Replaces |
|---|---|---|---|---|---|
| 0 | 2026-09-27 | Robert | Experiment 08 is the next experiment: a next-quarter predictor without an LLM, fitting a function that turns observable inputs into probabilities, plus a search for patterns in the numbers | Robert's notes of 2026-09-27; sets the bar for Experiment 09 | |
| 1 | 2026-09-27 | Robert | Moody's qualitative factor grades are not used as inputs; the quantitative numbers are | they are not observable at prediction time | |
| 2 | 2026-09-27 | Robert | Run now; pre-checks P1 (review by the other model family) and P2 (chair consensus) waived for this study (specification decision 6) | no model, no spend, no label changed, as for Experiment 07 | |
| 3 | 2026-09-27 | Robert | Download the SEC companyfacts files of the withdrawn-rating companies (specification decision 3) | half the training changes come from them | |
| 4 | 2026-09-27 | Robert | Specification decisions 1, 2, 4, 5 and 7 accepted as proposed: train to 2020, test from 2021; gold observations excluded from training, kept in test with a sensitivity; feature list of section 6; M4 included; top 5% and 10% | | |
