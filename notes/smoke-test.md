# Smoke test: the full pipeline live, twice

*Run and write-up by Claude (Opus 5), directed by Robert Vetter, 29 August 2026. Purpose:
prove every stage of the runner on real money before any larger spend - document assembly,
redaction, the API call with structured output, the deterministic scorecard, scoring,
extraction verification. Two observations, chosen as one changed and one unchanged case with
triple-verified labels. This is a plumbing proof on n=2, not evidence about system quality.*

## Cost discipline

Staged so nothing could fail mid-spend: offline checks (Task B path-leak guard verified: the
label-setting 2022-12-12 action is excluded from Kohl's Q4-2022 input path), then the free
`count_tokens` endpoint on the exact payloads (validated the key, the model access, and the
precise input size), then a ~$0.03 micro-call proving the schema/streaming/parse path end to
end, then the real run. Total spend including the micro-call: **about $1.60** (291k input,
4.6k output tokens, claude-opus-5, Task B, docs config annual+q). Runtimes 41s and 19s.

## Results

| Observation | Label | Persistence | Scorecard pred | Direct pred |
|---|---|---|---|---|
| Kohl's 2022-12-31 (changed: IG exit, Baa2 to Ba1) | Ba1 | Baa2 (err 2) | Baa3 (err 1, right direction) | **Ba1 (err 0)** |
| Walmart 2025-06-30 (unchanged) | Aa2 | Aa2 (err 0) | Aa3 (err 1) | **Aa2 (err 0)** |

The pattern matches expectations from the earlier experiments: on the changed quarter the
system beat persistence (which is always wrong there by construction); on the unchanged
quarter it produced no false alarm on the direct channel; the scorecard channel shows the
familiar one-notch compression toward the middle on both ends.

**Extraction, checked against XBRL at zero model cost: 14 of 14 one-to-one figures exact to
the million (median deviation 0.0%).** The two flagged fields are the documented ambiguity
classes, not reading errors: interest (model reports gross including finance-lease interest,
XBRL tags net or debt-only) and Kohl's debt composite (476m gap = financing obligations,
which XBRL does not tag; the model correctly included them per the methodology).

Qualitative grades came out plausible and defensible (Kohl's Ba/Baa across the board in the
quarter of its IG exit; Walmart Aa/Aaa) - these have no automatic ground truth and stay a
judgement channel.

## Caveats carried forward

The Kohl's result is exactly where training-data memory could help (a widely reported 2022
downgrade); nothing on n=2 distinguishes reading from remembering. That is what the planned
contamination probes (same observation, no documents) and the post-cutoff clean window are
for. Also measured in passing: real token counts run ~1.45x the chars/4 estimate; the
runner's dry-run estimator is now calibrated to chars/2.8.
