---
name: process-opportunities
description: Tailor a resume + cover letter for one or more jobs and score each with a True ATS score. Use when the user says "process job opportunities", "tailor my resume for these jobs", "run my job-search batch", "score these against my resume", or pastes/links job descriptions. Requires that setup-profile has been run first.
---

# Process job opportunities

Build one tailored résumé + cover letter per job, run 3-pass content QA, and
write a realistic **True ATS Score** to the tracker. Deliver the documents.

**Read `${CLAUDE_PLUGIN_ROOT}/references/process_rules.md` in full before
starting.** It is the playbook. The two invariants below are non-negotiable.

## Step 0a — Announce the build (first user-visible line)
Before anything else, read the `version` field from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and make your **first
user-visible line**: `job-search-tailor v<version> — processing opportunities`.
Always read the version from that file; never hardcode it (a hardcoded string
drifts the moment the plugin is bumped).

## Invariants (never violate)
1. **Truthfulness** — never claim a tool/skill/domain not in the user's
   `profile/verified_skills.md` for the relevant company. Honest gaps are
   acknowledged, never fabricated. Portfolio-only skills are always attributed.
2. **Scoring integrity** — the tracker's *Resume Score* is ALWAYS the True ATS
   Score from the ATS script. The 3-pass `critique_and_refine()` checklist score
   is QA only and is NEVER written to the tracker. A flat 100 is a red flag.

## Step 0 — Confirm scope
Identify the working folder (`<home>` — the job search folder containing
`profile/`, `tracker/`, `docs/`, and a hidden `.system/`). Read
`<home>/profile/verified_skills.md` now. The tracker is the single
`<home>/tracker/job_search_tracker_<name>.xlsx`. Ask which jobs to process if
unclear: the rows already seeded in the tracker for today, or ones the user will
paste.

**Canonical tracker (T1).** The user may keep backup copies in `tracker/` (e.g.
`… - OG.xlsx`, `…_copy.xlsx`) — that's normal and supported. The scorer resolves
the **canonical** tracker by the filename contract `job_search_tracker_<name>.xlsx`
(backups/copies excluded) and writes the True ATS Score **only** there. If it
can't resolve exactly one canonical tracker, it **halts and asks** — never writes
to a guessed file. Never read or write a backup/`OG`/copy as if it were canonical.

## Step 1 — Get each job description (preflight first)
See `process_rules.md` §1a for the full retrieval playbook. Use
`${CLAUDE_PLUGIN_ROOT}/templates/jd_retrieval.py` — do **not** eyeball the cells.

1. **Resolve + classify every selected role's link up front.** Run a short
   python that opens the tracker and calls `jd_retrieval.read_job_links(ws)`.
   That reads the **embedded hyperlink target** of the *Sourced From (w/link)*
   cell (not the display text like "Linkedin"/"DM Message"), finds the link
   column by header, and returns `(row, target, plan)` per role where `plan` is
   `linkedin-guest` / `web-fetch` / `local-file` / `needs-paste`.
2. **Fetch by plan, headless first:**
   - `linkedin-guest` → fetch the guest endpoint
     (`jd_retrieval.linkedin_guest_url(job_id)`) **before** any browser/login
     path; it returns the JD even for jobs marked "Application submitted".
   - `web-fetch` → try a headless fetch; if it returns an empty/login shell,
     fall back to the browser.
   - `local-file` → read the file's text.
   - `needs-paste` → collect for step 3 (do not skip).
   - Recommend installing Claude in Chrome **only** if a role still fails after
     headless attempts.
3. **Batch the paste request once.** Ask the user a single time to paste the
   JDs for every role that couldn't be retrieved — not one prompt per role.
4. **Never build or score from a guessed JD.** A role with no real JD is
   deferred with a note and shown in the Step 5 table with score `—`.
5. **Record each retrieved JD into the skills-demand repository.** For every JD
   you successfully retrieve, call
   `skills_demand.record_jd(<home>, job_id, company, role, level, jd_text)`
   (from `${CLAUDE_PLUGIN_ROOT}/templates/skills_demand.py`). `level` is
   IC / Manager / Director / VP, inferred from the title. It saves the JD under a
   readable name (`YYYY-MM-DD_company_jobtitle.md`) and extracts demand into four
   categories — **tool, technical_competency, leadership, domain** — so senior
   (Director/VP) demand is captured, not just software. Every processed role
   produces ≥1 row; a role with nothing extractable gets an explicit `no_extract`
   marker (never a silent drop). The taxonomy/synonyms are editable in
   `${CLAUDE_PLUGIN_ROOT}/templates/skills_taxonomy.py`.
- Capture per role: full requirements text, company, role, location, sector/domain.

## Step 2 — Per role: research, choose base, draft, review
For each job, follow the mandatory order from `process_rules.md`:
1. Research the company's *specific* situation.
2. Pick the base: **LEADER** (people-manager) or **HANDSON** (hands-on/IC). If
   the title says Manager/Director but the work is hands-on, use HANDSON.
3. Write cover-letter **Para 1** (company insight) first, then the résumé
   summary (no overlap), then CL Para 2 (one story), then CL Para 3 (forward
   judgment / honest gap + counterweight).
4. Run the **Recruiter Review checklist** (section 5 of process_rules.md) and
   fix anything that fails before building.
Cross-check every claim against `verified_skills.md` as you write.

## Step 3 — Build the documents (3-pass QA, no tracker write)
Copy `${CLAUDE_PLUGIN_ROOT}/templates/build_batch_template.py` to
`<home>/.system/scripts/<date>/build_batch_<date>.py`. Fill in one `do_role(...)` block per job
with the chosen base, the summary, the expertise line, `jd_hard` (5-10 genuine
discriminators), any honest `gap_patches`/`tight_patches`, and the 3 cover-letter
paragraphs. Run it. It prints the 3-pass checklist score and writes the `.docx`
files — it does NOT touch the tracker.

## Step 4 — Score (the authoritative tracker number)
Copy `${CLAUDE_PLUGIN_ROOT}/templates/ats_score_template.py` to
`<home>/.system/scripts/<date>/ats_score_<date>.py`. For each role build a 25-40 term `jd_full`
from the ACTUAL JD (weights 3/2/1), **including the genuine discriminators the
candidate lacks** — required tools they don't have, the company's sector/domain,
exact must-have phrases. Set each role's tracker `row`. Run it: it reads the
built `.docx`, computes the True ATS Score, and writes it to the tracker.

## Step 5 — Verify and deliver
- Confirm each score is realistic (typically 70-95). If anything reads 100,
  the `jd_full` was too soft — add the discriminators a sharp recruiter would
  weigh and re-run.
- Present the résumé + cover-letter files to the user.
- **Always end with the batch summary table (mandatory — see `process_rules.md`
  §9).** The ATS script prints it via `summary_table(...)`; paste that exact
  output. It is sorted by score descending with columns **Score · Role
  (Company — Title) · Base · Why** (`strength; gap: …`), followed by a
  **MIN / AVG / MAX** line. Each row's Score is the True ATS Score written to the
  tracker. Roles whose JD couldn't be retrieved appear with score `—` and a
  reason — never omitted.
- **Show the skills-demand review.** Run
  `python3 ${CLAUDE_PLUGIN_ROOT}/templates/skills_demand.py <home>`. It prints the
  demand inventory by category and writes an Excel **Skills Demand** tab to
  `<home>/docs/job_descriptions/skills_demand.xlsx` — per skill: frequency, % of
  jobs, and a **Covered / Weak / Gap** classification against the user's profile,
  for **leadership / technical_competency / domain** as well as tools. Present the
  Gaps (and Weak items) most-wanted first: "the market keeps asking for these;
  here's where you might augment your Profile Workbook." This is **recommend-only**
  — it never writes the Skills Matrix, bases, or `verified_skills.md`, and you only
  ever suggest skills the user can claim truthfully.
- Offer to update the **Profile Workbook** if new facts surfaced, then recompile
  (see setup-profile "Updating later").

## Folder & permission robustness (U1)
The user may keep manual backups in the working folder and may **decline** a
delete/move permission. Both are normal, supported conditions — not errors.
- Treat every delete/move as **best-effort**. If it's declined or fails, **do not
  abort the run** and do not corrupt state — continue, do the destructive step
  only where allowed.
- When promoting the previous batch from `docs/current/` to `docs/submitted/`,
  move what you can and **report what you couldn't** (name each file and where it
  was left). Never silently pile up duplicates.
- Never read or write a leftover/backup file as if it were canonical (pairs with
  the T1 tracker rule above).

## Naming
Built documents land in `<home>/docs/current/` (the latest batch only), named
`001_<Name> - <Company> - <Role Stub> - Resume.docx` and `- Cover Letter.docx`.
The `001_` prefix sorts the user's freshest documents to the top of `current/`.
