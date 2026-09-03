# Experiment 02 — Results (batch msgbatch_016jjPxBbXaxaowQymd9LSuH, collected 2026-08-30)

*Nine gold-set observations (6 rating changes / 3 unchanged, 2013–2025, nine companies), Opus
4.5 (`claude-opus-4-5-20251101`, training cutoff Aug 2025), input = the observation's 10-K
(redacted) + the history pack, paired variants A and B plus a memory probe per observation,
all via the Batch API. Every prompt verbatim in `runs/msgbatch_016jjPxBbXaxaowQymd9LSuH/requests.json`, raw outputs in
`raw_outputs.json`, scored records in `results.json`.*

## Headline: with the issuer's own history in the input, direct judgement beat persistence for the first time

| Channel | Exact | MAE (notches) | Changed cases (6): moved in the right direction | Unchanged (3): false alarms |
|---|---|---|---|---|
| Persistence baseline | 3/9 | 0.89 | 0/6 (by construction) | 0/3 |
| A — extract → deterministic scorecard | 2/9 | 1.89 | 4/6 moved, but overshoots | 2/3 |
| **A-direct — the model's own rating after extracting and grading** | **6/9** | **0.44** | **4/6 (3 exact)** | **0/3** |
| B — direct rating, same inputs, no extraction step | 4/9 | 0.56 | 3/6 (1 exact) | 0/3 |

| ID | Company | Date | Kind | Prev→Label | A | A-direct | B (its own change call) | Probe |
|---|---|---|---|---|---|---|---|---|
| G05 | DOLLAR GENERAL CORPORA | 2013-03-31 | changed | Ba1→Baa3 | A3 | **Baa3** | Ba1 (unchanged) | wrong_or_none |
| G13 | KOHL'S CORPORATION | 2025-06-30 | changed | Ba3→B2 | Ba3 | **B1** | B1 (downgrade) | recalls_prior |
| G14 | LESLIE'S POOLMART, INC | 2024-09-30 | changed | B1→B2 | B2 | **B1** | B1 (unchanged) | wrong_or_none |
| G17 | MACY'S | 2022-03-31 | changed | Ba2→Ba1 | Baa1 | **Ba1** | Ba2 (unchanged) | recalls_prior |
| G20 | O'REILLY | 2013-12-31 | changed | Baa3→Baa2 | A2 | **Baa2** | Baa2 (upgrade) | wrong_or_none |
| G27 | UNDER ARMOUR, INC. | 2020-06-30 | changed | Ba1→Ba3 | Baa3 | **Ba1** | Ba2 (unchanged) | recalls_prior |
| G37 | GROUP 1 AUTOMOTIVE, IN | 2023-09-30 | unchanged | Ba1→Ba1 | Baa2 | **Ba1** | Ba1 (unchanged) | wrong_or_none |
| G39 | J.JILL | 2022-03-31 | unchanged | Caa1→Caa1 | B3 | **Caa1** | Caa1 (unchanged) | wrong_or_none |
| G49 | VICTORIA'S SECRET & CO | 2024-12-31 | unchanged | Ba3→Ba3 | Ba3 | **Ba3** | Ba3 (unchanged) | wrong_or_none |

## What the nine observations say

1. **The history pack changed the picture.** In Experiment 01 (no history) the direct channel
   exactly matched persistence. Here the model's direct judgement, formed after extracting
   the figures and grading the four factors *relative to the implied anchors*, called four
   of six rating changes in the right direction (three exactly: Dollar General's 2013 upgrade
   to investment grade, Macy's 2022 upgrade, O'Reilly's 2013 upgrade) with **no false alarm**
   on the three unchanged cases. MAE 0.44 against persistence's 0.89. n = 9 — a signal, not
   a result; the intervals are wide.
2. **Decomposition helps the judgement; the arithmetic hurts the number.** The same run's
   deterministic scorecard output (channel A) is the worst channel (MAE 1.89), pulled toward
   investment grade in six of nine cases — the scorecard-indicated outcome sits systematically
   above Moody's actual rating for these retailers (notching and "other considerations" are
   not modelled). Yet the model that *went through* that extraction (A-direct) judged better
   than the model asked directly (B). The structured step is worth keeping as reasoning
   scaffold even where its arithmetic is not the final answer.
3. **B is persistence-biased.** Asked "keep or change the quarter-start rating?", B answered
   "unchanged, high confidence" on Dollar General, Macy's and Leslie's where the rating did
   change, reasoning from strong fundamentals in the prior fiscal year. The direct prompt
   defaults to inertia; the decomposed one does not.
4. **Misses are informative.** Under Armour's two-notch COVID cut (May 2020) was missed by
   every channel: the input was the FY2019 10-K, filed February 2020 — before the pandemic
   hit. The document could not contain the reason for the action. Leslie's B1→B2 was called
   only by the scorecard arithmetic (from collapsed EBITDA), not by either judgement channel.
5. **Contamination probes: no channel got the answer from memory.** No probe reproduced a
   post-change label. Three probes recalled the *prior* rating (Kohl's, Macy's, Under
   Armour) — the persistence information the pack provides anyway. Two probes carried
   partial era memory worth flagging: Under Armour "downgraded Baa3→Ba1 in early 2020, COVID"
   (the previous quarter's action, true) and Leslie's "downgraded to Caa1 in 2024" (wrong
   level, wrong timing — the actual Caa ratings came in 2025 — but the model knew Leslie's
   was deteriorating). Neither recollection propagated: B rated Leslie's "unchanged B1".
   Memory in this era is directional at best and wrong on specifics, consistent with every
   earlier probe in this project.

## Defect found in the post-run check (disclosed, fixed, scored)

The history pack's line "rating in effect at quarter start" was computed with an inclusive
date, so a Moody's action dated exactly on the quarter's first day counted as prior
knowledge. It happened once in this run: **Under Armour (G27)** was cut Ba1→Ba2 on
2020-04-01 and Ba2→Ba3 on 2020-05-21; the pack told the model "Ba2 in effect", which is
information from inside the observation quarter. The event list itself was filtered strictly
and did not contain the action; only the summary line leaked. Fixed in history_pack.py (the
line now states the rating as of the day before the quarter starts). G27 is therefore not a
leak-free observation; every channel still missed the label (Ba3), so the leak manufactured
no hit. **Metrics without G27 (n = 8): persistence 3/8 exact, MAE 0.75; A-direct 6/8 exact, MAE 0.25; B 4/8 exact, MAE 0.50; A 2/8 exact, MAE 1.75.** The other eight observations
have no action on their quarter-start day (checked against the raw records).

## Cost — and a miss on my side

Metered spend **$5.21** (probes + 18 document requests, batch prices), **21 cents over
Robert's $5 cap.** Cause: `cache_control` on the document block. In the Batch API the A and
B requests were processed in parallel, so both paid the cache-*write* premium (1.25×) and
neither got a read — 1.57M cache-creation tokens, zero cache-read tokens. The pre-submission
worst case ($4.59) assumed no cache, not a write premium without reads. Fixed in
`run_batch.py`: no `cache_control` in batch mode, and the guard now prices the premium if it
is ever used. The Anthropic console is the authoritative bill.

## What this changes for the plan

Robert's design choice — determine the rating *relative* to the issuer's own history — is
the first input change in this project that produced lift over persistence. The next
questions are mechanical and cheap to answer at this scale: does A-direct hold on the full
gold set (50, ~$15 batched without the cache premium)? Does adding the latest 10-Q catch
document-timing misses like Under Armour's? And should the scorecard arithmetic be
calibrated against Moody's actual ratings (its systematic optimism is measurable) rather
than used raw?
