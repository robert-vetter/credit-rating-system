# notes

Reading notes and experiment logs.

The files in here were written by Claude (Opus 5) working with Robert, who set the questions and the
test design. They are model-authored analysis rather than hand-written notes, and each file carries an
attribution header saying what was verified against source documents and what was not.

- `walmart-first-test.md` and `kohls-second-test.md` are the two baseline runs of the rating task, one
  at each end of the rating scale, using the methodology plus a single 10-K each.
- `blind-test.md` is the five-company blind test with stripped filings and a memory control, plus
  `blind_metrics.py` for the error numbers. This supersedes the two earlier runs as evidence.
- `what-else-feeds-a-rating.md` goes through all eight subfactors and asks which of them a 10-K can
  support, and records the leakage problem: companies disclose their own credit ratings in the filing.
- `scorecard.py` is the scoring arithmetic for both runs, kept separate so the inputs can be changed
  and the numbers rerun.
