# Experiment 09: decisions

*Every decision with its owner and date. Append only; a changed decision gets a new entry that
names the one it replaces. Open decisions are listed in the specification, section 13.*

| # | Date | Owner | Decision | Reason | Replaces |
|---|---|---|---|---|---|
| 0 | 2026-09-27 | Robert | Experiment 09 tests GPT-5.1 (knowledge cutoff 2024-09-30) on the 2025 window of next-quarter rating changes, using all company-quarters rather than a balanced subsample | a widely used commercial model whose cutoff lies before the test quarters; the natural rate gives realistic precision | flight notes decision 6 (balanced first) |
| 1 | 2026-09-27 | Robert | Robert provides an OpenAI API key with credits when the run is ready | | |
| 2 | 2026-09-27 | Robert | Go for the run. Specification decisions 1, 2, 5, 6, 7 and 10 accepted as proposed: 118 eligible rows as the primary test and the 29 others with rating history only; reasoning effort medium; no base rates in the prompt; rating disclosures redacted; EDGAR downloads and `tiktoken` installed; primary measure PR area against M1 | | |
| 3 | 2026-09-27 | Robert | One run per company-quarter, not three (specification decision 4) | cost | proposal of 3 replicates |
| 4 | 2026-09-27 | Robert | Cap $50 for this experiment for now; at the cap, stop and report progress, Robert decides how to continue. The OpenRouter key in `.env` is used; Robert set a $50 limit on it (specification decision 8) | | |
| 5 | 2026-09-27 | Robert | No Codex review; Robert's go stands in for chair consensus (pre-checks P1 and P2, specification decision 9) | | proposal of a Codex review |
| 6 | 2026-09-27 | Claude, following decision 2 | OpenRouter has no batch API. Specification decision 3 (batch discount) is implemented with OpenAI's flex tier through OpenRouter: the same snapshot `openai/gpt-5.1-20251113`, served by OpenAI, half the list price ($0.625 / $5 per million tokens, OpenRouter endpoint listing read 2026-09-27), slower and lower priority. Provider pinned to `openai/flex` with no fallback | keeps the discount Robert accepted; no other provider or snapshot can be used silently | Batch API |
| 7 | 2026-09-27 | Robert (decision 4), recorded by Claude | Authorization EXP09-R1-A1: cap $50, bound to manifest sha256 9eb82b9d672a4f18570c6a32ff1c1e942d5abd621c8959654a2724dc9e367e52 (runs/R1/authorization.json). Pre-flight: 118 document forecasts, 29 history-only forecasts, 74 probes; 17,348,050 input tokens; $10.84 input at the flex price; worst case $36.94 with every output ceiling reached | the runner refuses to send without it | |
| 8 | 2026-09-27 | Robert | Use a different OpenRouter key (prefix sk-or-v1-bb1, ending 9e3) because the key in `.env` has no credits. Not found under Developer, Desktop, Documents or Downloads; Robert to place it in `.env` or name its folder. No request sent until then | the `.env` key reports $0 total credits | decision 4, key part |
