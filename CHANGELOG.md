# Changelog

All notable changes to **job-search-tailor** are recorded here. Versioning is
semantic: a **minor** bump per feature round, a **patch** for fix-only rounds.
The running version is the single source of truth in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json); each skill announces
it as its first line at runtime.

## [0.2.0] — 2026-06-16

First round shaped by a live clean-room run. Focus: make the *path* to good
documents as reliable as the documents themselves.

### Added
- **Runtime build banner (K1).** Both skills announce
  `job-search-tailor v<version> — …` as their first user-visible line, read
  from `plugin.json` so it can never drift.
- **Resilient JD retrieval (G1–G3).**
  - Reads the **embedded hyperlink target** of the tracker's *Sourced From
    (w/link)* cells, not just the display text; the link column is found by
    header. Local-file targets that are missing are routed to paste, not
    dropped.
  - Makes the **LinkedIn guest endpoint**
    (`/jobs-guest/jobs/api/jobPosting/<jobId>`) the first retrieval attempt, so
    even already-applied jobs ("Application submitted") still yield a full JD;
    the browser is a fallback.
  - **Preflights every link** and batches the paste fallback into a single
    request. Chrome is a last resort, never a prerequisite. A role is never
    built or scored from a guessed description.
- **Mandatory end-of-batch summary table (J1).** Every batch ends with a table
  sorted by score (`Score · Role · Base · Why`) plus a MIN/AVG/MAX line. The
  table is emitted by the ATS script, so each row's score is exactly the True
  ATS Score written to the tracker.

### Notes
- No changes to `engine/build_docs.py` or the scoring math. The two invariants
  hold: the tracker's *Resume Score* is only ever the True ATS Score, and
  nothing is claimed that isn't in `verified_skills.md`.

## [0.1.0]

Initial working baseline: `setup-profile` + `process-opportunities`, the honest
True ATS scorer, and the shipped job-tracker template.
