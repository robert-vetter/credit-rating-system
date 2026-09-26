# Qualitative evidence study

*OpenAI Codex, directed by Robert Vetter, 17 September 2026. Retrospective, provisional research assessment; not expert factor labels.*

State on 2026-09-26: only this protocol and `rubric.json` exist. The deliverables below are planned, not built, and nothing has run.

## Question and scope

What do the original supplied sources support about the four qualitative factors, and how do the saved assessments relate to that evidence?

Twelve issuer-factor cases: Walmart X20, Nike X12, Signet X15, crossed with Market Characteristics, Market Position, Revenue and Earnings Stability, Financial Policy. Thirty-six saved replicate grades from nine current-arm Experiment04 outputs. All cases are previously exposed; no blindness, prospective preregistration or independent-observation claim. No new model call.

Use original dispatched documents and financial/peer context at 2026-08-29, not corrected Experiment05 figures. Preserve original prior/anchor exposure as a protocol characteristic, never independent justification for a factor grade. Do not import omitted filing passages, later facts or target ratings into adjudication.

## Assessment protocol

1. `rubric.json` fixes paraphrased criteria before new rationale comparison. The methodology is holistic best fit, not an all-criteria checklist. Criteria pages3–9 are an analytical reference, not instructions the original model received: it saw abbreviated descriptions.
2. Assemble supporting/adverse evidence and missing information first. Quotes must match the original decoded user message, with zero-based half-open Unicode offsets, message/body hashes and source date. Distinguish company statements from independent measurements. Source-match success does not imply semantic support.
3. Preserve the complete original rationale, one string for all factors. Attribute slices only with explicit factor labels, with offsets. Otherwise mark not separately articulated.
4. Classify factual claim support separately from grade identifiability. Availability: adequate_for_assessment / partial / not_found_in_reviewed_material. Support: supported / contradicted / unsupported / ambiguous. Review coverage is bounded and stated; a search miss is not proof of absence. A contradicted claim does not automatically make its associated grade wrong.
5. All annotations are machine-proposed and pending Robert's review. Do not infer correct grades from agency ratings or anchors. Leave a reference grade unassigned if a best-fit interpretation cannot be justified. Stable outputs do not establish correctness.

The source map is fixed before new comparisons, but prior grades and issuer results were already known. The saved rationales are then compared to that map; any later source additions must be identified as follow-up checks rather than silently called pre-comparison evidence.

## Deliverables and limits

`assessments.json` stores12 provisional case reviews, evidence and review coverage. `run_review.py` validates original body/ledger/audit bindings, exact sources and36 saved grade comparisons; no scorecard or target-label loader is called. Generated full records stay in a fresh ignored `evaluation/runs/qualitative-evidence-2026-09-17/`. Refuse overwrite. No changes to the live report to the chair or the email, no publication.

`results.md` reports all12 cases and up to3 concrete human adjudication questions. This is not an independent grading benchmark, causal diagnosis of why the model chose a grade, or evidence that a revised agent performs better.
