# Decision log — Experiment 02 (relative rating determination with history)

## DECIDED (2026-08-30, Robert via chat)

**D1 — History pack, full:** rating path to the previous quarter end, XBRL fundamentals of the
three prior fiscal years plus the current one, implied qualitative anchors (with 3-year
median; shock-year caveat), peer table at t, and the current filing. Both variants receive
the identical pack.

**D2 — Gold set rule: one shot per variant.** Prompts are fixed beforehand on a small
non-gold dev slice; then exactly one run per variant on the 50 gold observations. No tuning
against gold.

**D3 — Model order: Opus 4.5 first** (training cutoff Aug 2025 lies inside the data, enabling
the within-model in-sample vs out-of-sample contrast), Opus 5 afterwards if funded.

**D4 — Budget: up to $5 total** (Robert: "das sollte reichen"). See README §Budget for what
$5 buys and what it does not; the scope actually run is chosen with that table on the
table.

**D5 — Scope under the $5 cap: 10 gold observations, drawn at random** (Robert, 2026-08-30:
"einfach zufällig 10 observations aus dem goldset"). Implemented as a seeded draw (seed
20260830), then trimmed for the cap: two oversized changed items swapped for the next
seeded ones that fit, one oversized unchanged item dropped - final 9 (6 changed / 3
unchanged), rule and bias disclosed in selection.json. Documents: the 10-K only (`annual`
config; the 10-Q added little and cost much). Both variants with the
current filing plus the history pack, contamination probes on the same 10, all via the
Batch API (50% off): ~$3.30. The full-gold-set run stays a later, separately funded step;
D2's one-shot rule applies to these 10 (no tuning against them).

**Post-run note (2026-08-30):** metered spend $5.21, 21 cents over the cap, caused by the
cache-write premium in batch mode (see results.md). Runner fixed. Robert to decide whether
the full-gold-set run (~$15 batched) is funded.

## OPEN

*(none)*
