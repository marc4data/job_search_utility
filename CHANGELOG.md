# Changelog

All notable changes to **job-search-tailor** are recorded here. Versioning is
semantic: a **minor** bump per feature round, a **patch** for fix-only rounds.
The running version is the single source of truth in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json); each skill announces
it as its first line at runtime.

## Unreleased — tooling

- **Release workflow (Epic P).** `.github/workflows/release.yml` fires on a
  `vX.Y.Z` tag: it verifies the tag matches `plugin.json`, runs `build.sh`'s
  integrity guards, and publishes a GitHub Release with the `.plugin` attached
  and this file's section for that version as the notes (via
  `tools/release_notes.py`) — so a Release can never drift from the CHANGELOG.
  Documented in CONTRIBUTING.md. **No plugin behavior change**, so no version
  bump; `v0.4.0` and `v0.5.0` were tagged once P landed.

## [0.5.0] — 2026-08-31

Round shaped by running v0.4.0 in daily use. Two friction points (postings that
can't be fetched, permission prompts mid-retrieval) and one craft correction (the
cover letter was too presumptive). No change to the ATS scorer's computation or
the checklist/ATS boundary.

### Added
- **Manual job-description fallback (W1).** When a posting can't be read — taken
  down, login-walled, client-rendered, or blocked — the run reads it from
  `<home>/docs/manual_job_descriptions/` instead of asking for a paste. Files
  follow `YYYYMMDD Company - Job Title.docx` and are matched on **company + job
  title** (the date only breaks ties); `.docx` / `.md` / `.txt` are read.
  `templates/manual_jd.py` does the matching and reading; `jd_retrieval.py` gains
  `read_job_rows()` / `plan_for_role()`, which attach the matched document to
  every row — even one with a good link — so a failed fetch falls back instantly.
  A matched file whose format can't be read (e.g. `.pdf`) is **reported by name
  with its reason**, never guessed past.
- **Manual-JD archiving (W3).** Files a run consumed move to
  `docs/manual_job_descriptions/archive/`, and leftovers a *previous* run
  consumed are swept at the start of the next one — matched against the
  skills-demand index, so a description just dropped in for today is never
  archived. Best-effort per U1: a declined move never aborts a run, and anything
  left behind is named.

### Changed
- **Retrieval is prompt-free (W2).** A run no longer asks permission to fetch a
  URL, whether to try the browser, or about Chrome mid-batch; it works the whole
  preflight silently and reports once. `setup-profile` now writes
  `<home>/.claude/settings.json` (from
  `templates/workspace_settings_template.json`) pre-approving `WebFetch` /
  `WebSearch` **inside the job-search folder only**, merging into any existing
  settings rather than overwriting them.
- **Cover-letter strategy (W4) — less presumptive.** The letter no longer
  diagnoses the company's problems or asserts what the candidate would do in the
  role. New three moves: **Para 1** one specific, verifiable thing about the
  company or its mission and why it genuinely interests you; **Para 2** the
  résumé items this JD actually asks for, each tied to the requirement it
  answers; **Para 3** the close — strongest alignment, honest gap with its
  counterweight, interest in the conversation. A new **presumption rule** bans
  plans, priorities, first-90-days, and "I would…" aimed at their business, and
  the Recruiter Review checklist gains a **presumption audit** plus a **match
  traceability** check. Order of operations updated: the résumé summary is now
  written before CL Para 1.

### Notes
- Engine and scoring math unchanged. Both invariants hold: the tracker's *Resume
  Score* is only ever the True ATS Score, and nothing is claimed that isn't in
  `verified_skills.md`.

## [0.4.0] — 2026-06-19

Field-feedback round from running v0.3.0 on ~40 real roles. No change to the ATS
scorer's computation or the checklist/ATS boundary; the demand index stays
demand-only (never writes the Skills Matrix, bases, or verified_skills).

### Added
- **Continuous build gate (Q1/Q2).** `.github/workflows/ci.yml` runs `build.sh`
  (required-files + personal-data guards) on every push/PR and uploads the
  `.plugin` as an artifact; `build` is a required check on `main` (see
  CONTRIBUTING.md). No tag/Release here — that stays the Release workflow.
- **Skills-demand index v2 (R1–R5).** Readable corpus filenames
  (`YYYY-MM-DD_company_jobtitle.md`); a four-category taxonomy
  (tool / technical_competency / leadership / domain) in one editable reference
  file (`templates/skills_taxonomy.py`); guaranteed per-role coverage with an
  explicit `no_extract` marker (no silent drops); synonym folding + a stop-list
  that strips pipeline self-references like `claude`; and an Excel **Skills
  Demand** review tab classifying each demanded skill Covered/Weak/Gap by
  category (recommend-only).

### Fixed
- **Canonical-tracker scoring (T1).** The scorer resolves the canonical tracker
  by an explicit filename contract (not "first `.xlsx`"), never writes a
  user-made backup/`OG`/copy, and **halts and asks** on ambiguous resolution.
- **Folder/permission robustness (U1).** Delete/move are best-effort and
  self-reporting; declining a permission or leaving backups never aborts a run or
  treats a leftover as canonical.
- **Paste-fallback UX (V1).** Unretrievable JDs are gathered into one paste
  request with a per-role reason; an unpasted role is deferred with that reason,
  never scored from a guess.

### Deferred → resolved
- Tagging `v0.4.0` / cutting a GitHub Release depended on the Release workflow
  (Epic P), which wasn't in the repo at the time. **P has since landed**
  (`.github/workflows/release.yml`), and `v0.4.0` was tagged retroactively at
  this round's merge commit.

## [0.3.0] — 2026-06-18

Makes the profile tunable by the end user, and turns processed jobs into market
intelligence.

### Added
- **Profile Workbook + compiler (Epic L).** A single friendly Excel workbook
  (`templates/profile_workbook_template.xlsx`) is now the source of truth the
  user edits. `templates/compile_profile.py` compiles it into
  `profile.py` / `bases.py` / `verified_skills.md` in the exact formats the
  engine already consumes — **the engine is unchanged.** `setup-profile` builds
  and compiles the workbook; "update my profile" recompiles.
- **Truthfulness validator.** `templates/validate_profile.py` flags any tool the
  résumé would claim (Areas of Expertise or cert line) that the Skills Matrix
  doesn't back — catching tuning drift before it reaches an application. Shared
  tool vocabulary in `templates/skills_vocab.py`.
- **Skills-demand repository (Epic H).** `templates/skills_demand.py` persists
  every processed JD's requested skills to a visible `docs/job_descriptions/`
  corpus + index, aggregates demand by skill × level, and surfaces in-demand
  skills the user isn't yet employer-backed for — so they can decide what to add
  to the Profile Workbook.

### Notes
- Engine and scoring math unchanged. Invariants hold: the tracker's *Resume
  Score* is only ever the True ATS Score; nothing is claimed that isn't in
  `verified_skills.md`.

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
