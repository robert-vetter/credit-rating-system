# Experiment NN: <short name>, specification

*Written YYYY-MM-DD by <author>, directed by Robert Vetter. Version 0.1, for review and
consensus. Follows [EXPERIMENT-POLICY.md](../../EXPERIMENT-POLICY.md). Checked against: <sources>.*

State: design / awaiting consensus / pre-checks / running / done.

## 1. Purpose and question

| Item | Specification |
|---|---|
| Question | |
| Null hypothesis | the model does not beat persistence on ... |
| Target | outstanding rating at a date / rating change within a horizon / both |
| Unit of observation | |
| What it is | |
| What it is not | |
| Place in the programme | decipher / encode / baseline measurement |

## 2. Dates

| Date concept | Value (YYYY-MM-DD) | Source |
|---|---|---|
| Model training cutoff or release bound | | vendor page, retrieved YYYY-MM-DD, snapshot in `evidence/` |
| Rating history supplied ends | | |
| Document boundary | | |
| Filings eligible | from ... to ... | |
| Target date | | |
| Known rating actions in the window, each to the day | | Moody's release / 17g-7 file |

## 3. Sample and data characteristics

### 3.1 How the sample is built

| Step | Count | Where |
|---|---|---|

### 3.2 Label characteristics

| Characteristic | Value |
|---|---|
| Changed / unchanged | |
| Upgrades / downgrades | |
| Investment grade / speculative grade | |
| Rating types | |
| Label source and validity check | |

### 3.3 Imbalance plan

| Item | Value |
|---|---|
| Changed/unchanged ratio and why | |
| Claim the number of changed cases can support | |
| Cost of a missed change against a false alarm | agreed / DECISION |

### 3.4 Input characteristics

| Characteristic | Value |
|---|---|
| Documents by form | |
| Filing dates | |
| Request size in tokens, min / median / max | |

## 4. Per-observation table

| ID | Issuer | Prior rating (type, date) | Filings (period end / filing date) | Label (source, date) | Rating action (day) |
|---|---|---|---|---|---|

## 5. Models and settings

| Setting | Value |
|---|---|
| Model ID and provider | |
| Commercial baseline model | |
| Temperature, seed, output ceiling, reasoning effort | |
| Replicates | |
| Tools, retrieval, grounding | none |
| Memory probe before documents | yes |

## 6. Inputs to the model

| Input | Content | Point-in-time rule |
|---|---|---|
| Prior rating | visible / withheld (arm) | |

Excluded: 8-Ks, exhibits, press releases, peer ratings, any tool or retrieval.

## 7. Prompt and output

Verbatim prompts and schemas in `prompts/`. Missing values allowed: yes.

## 8. The deterministic calculation

All arithmetic in `system/scorecard.py`. One definition per input:

| Input | Definition | Methodology basis | Computed by |
|---|---|---|---|

## 9. Metrics and baselines

| Item | Rule |
|---|---|
| Baseline | persistence on the same observations |
| Metrics | exact, within one, MAE from the error sum |
| Split | changed / unchanged |
| Consensus | median of valid replicates |
| Missing outputs | stay missing; matched persistence |

## 10. Controls and pre-checks

| # | Check (EXPERIMENT-POLICY section 3) | Status | Evidence |
|---|---|---|---|
| P1 to P14 | | | |

## 11. Budget

| Item | Value |
|---|---|
| Worst-case cost | |
| Cap approved by Robert | |

## 12. Known defects and limitations before the run

| Defect | Effect | Handling |
|---|---|---|

## 13. Decisions that need consensus before the run

| # | Decision | Options | Proposed | Agreed (who, date) |
|---|---|---|---|---|

## 14. Definitions

| Term | Meaning | Example |
|---|---|---|
