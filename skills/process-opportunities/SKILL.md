---
name: process-opportunities
description: Tailor a resume + cover letter for one or more jobs and score each with a True ATS score. Use when the user says "process job opportunities", "tailor my resume for these jobs", "run my job-search batch", "score these against my resume", or pastes/links job descriptions. Requires that setup-profile has been run first.
---

# Process job opportunities

Build one tailored résumé + cover letter per job, run 3-pass content QA, and
write a realistic **True ATS Score** to the tracker. Deliver the documents.

**Read `${CLAUDE_PLUGIN_ROOT}/references/process_rules.md` in full before
starting.** It is the playbook. The two invariants below are non-negotiable.

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

## Step 1 — Get each job description
- If the tracker rows have a Job URL, retrieve the full JD. LinkedIn and most
  boards are logged-in / JavaScript-rendered — use the browser (Claude in
  Chrome) and read the page text; a plain fetch returns an empty shell.
- Or accept JDs the user pastes directly.
- Capture: full requirements text, company, role, location, sector/domain.

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
- Briefly report each score with its top found/missed terms so the gap is visible.
- Offer to keep `verified_skills.md` updated if new facts surfaced.

## Naming
Built documents land in `<home>/docs/current/` (the latest batch only), named
`001_<Name> - <Company> - <Role Stub> - Resume.docx` and `- Cover Letter.docx`.
The `001_` prefix sorts the user's freshest documents to the top of `current/`.
