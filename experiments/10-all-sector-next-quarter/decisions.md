# Experiment 10: decisions

*Every decision with its owner and date. Append only; a changed decision gets a new entry that
names the one it replaces.*

| # | Date | Owner | Decision | Reason | Replaces |
|---|---|---|---|---|---|
| 0 | 2026-10-01 | Robert | Run the free sizing step for an all-sector GPT-5.1 test, including SEC downloads; Claude decides on its own when to ask | Experiment 09 had only 11 changes; the size of a wider test decides its design and cost | |
| 1 | 2026-10-01 | Robert | Map the all-sector universe by rules (A unique name, B 10-K tie-break) with a spot check of about 30 random proposals instead of reviewing every pair; drop conflicts | keep the review small | |
| 2 | 2026-10-01 | Robert | Store the all-sector data apart from the Retail universe: `data/all-sectors/` (gitignored) and `evaluation/all-sectors/` (committed records) | clarity between the hand-mapped Retail universe and the rule-mapped all-sector universe | |
