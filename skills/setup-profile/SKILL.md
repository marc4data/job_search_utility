---
name: setup-profile
description: One-time setup for the job-search-tailor workflow. Use when the user says "set up my job search", "onboard me to job-search-tailor", "create my resume profile", "build my base resumes", or is using this plugin for the first time. Interviews the user and generates their personal profile, two base resumes, verified-skills corpus, and job tracker.
---

# Set up the job-search-tailor profile

This is the one-time intake. Goal: produce a clean working folder containing the
person's own `profile/`, two base résumés, the anti-fabrication corpus, and a
tracker — so the `process-opportunities` skill can tailor applications for them.

Read `${CLAUDE_PLUGIN_ROOT}/references/process_rules.md` first. Keep the
conversation in plain language; do not expose file paths unless asked.

## Step 0 — Announce the build (first user-visible line)
Before anything else, read the `version` field from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and make your **first
user-visible line**: `job-search-tailor v<version> — setting up your profile`.
Always read the version from that file; never hardcode it.

## Step 1 — Establish the working folder

Ask the user where their job search lives (a folder on their computer). If no
folder is connected, request one. Inside it, create this **canonical structure**.
The top layer is plain-language (the user reads it); the hidden `.system/` holds
the technical guts (safe to ignore).

```
<home>/
├── README.md            ← plain-language "how this works" (you generate it)
├── tracker/             ← job_search_tracker_<name>.xlsx
├── docs/
│   ├── current/         ← the latest batch ONLY (built résumés + cover letters)
│   ├── submitted/       ← flat archive of all prior batches
│   └── manual_job_descriptions/   ← JDs the user saves when a posting can't be fetched
│       └── archive/     ← manual JDs already used by a run
├── profile/
│   ├── Profile_Workbook_<name>.xlsx   ← the user EDITS this (source of truth)
│   ├── profile.py, bases.py, verified_skills.md   ← COMPILED from the workbook
│   └── history/         ← dated snapshots (used later)
├── .claude/
│   └── settings.json    ← pre-approves web fetches so runs never stop to ask
└── .system/
    ├── engine/build_docs.py   ← copy from ${CLAUDE_PLUGIN_ROOT}/engine/
    └── scripts/               ← per-run build/ats scripts go here, under <date>/
```

Create every folder above (leave `docs/current/`, `docs/submitted/`,
`docs/manual_job_descriptions/archive/`, `profile/history/` empty for now). Copy
`${CLAUDE_PLUGIN_ROOT}/engine/build_docs.py` to `<home>/.system/engine/`. Copy the
tracker template `${CLAUDE_PLUGIN_ROOT}/templates/job_tracker_template.xlsx` to
`<home>/tracker/job_search_tracker_<name>.xlsx`, and the Profile Workbook template
`${CLAUDE_PLUGIN_ROOT}/templates/profile_workbook_template.xlsx` to
`<home>/profile/Profile_Workbook_<name>.xlsx` (slugify the user's name). Keep the
`templates/*.py` handy — each run copies them into `<home>/.system/scripts/<date>/`.

Copy `${CLAUDE_PLUGIN_ROOT}/templates/manual_jd_README_template.md` to
`<home>/docs/manual_job_descriptions/README.md` — it's the naming guide the user
reads when a posting can't be fetched (`YYYYMMDD Company - Job Title.docx`).

Copy `${CLAUDE_PLUGIN_ROOT}/templates/workspace_settings_template.json` to
`<home>/.claude/settings.json` (**merge** its `permissions.allow` entries into any
settings file already there — never overwrite the user's own settings). This
pre-approves `WebFetch`/`WebSearch` inside this folder so a processing run never
stops to ask permission for the job links it was told to read. Mention it in one
line at hand-off; the user can delete an entry to be asked again.

Finally, write a plain-language `<home>/README.md` from
`${CLAUDE_PLUGIN_ROOT}/templates/workspace_README_template.md`, filling in the
user's name. It explains each top-level folder in user terms — no internal paths.

## Step 2 — Interview the user

Gather everything needed. Prefer an elicitation form or `AskUserQuestion`; offer
a résumé/LinkedIn upload so you can pre-fill instead of asking cold. Collect:

**Identity & contact** (→ `profile.py`)
- Name (with any suffix like MBA), city/state, phone, email
- 1-3 links (LinkedIn, portfolio, GitHub)
- Education (degrees, schools)
- Certifications & training (ONLY ones they actually hold)
- Older roles for a compact "Additional Experience" section

**Work history for the two bases** (→ `bases.py`)
- For each significant role: title, company, location, dates, a one-line
  summary, and 2-4 achievement bullets (with numbers where possible)
- Their 4-6 biggest career highlights
- The tools/skills grid (Areas of Expertise) — real keywords only
- Any portfolio/personal project (for the HANDSON base's projects section)

**Verified skills** (→ `verified_skills.md`) — the most important part
- Which tools/skills they used at EACH company, with honest depth
- Tools they've NEVER used (especially ones adjacent to theirs)
- Tools that are portfolio/learning ONLY (must always be attributed as such)
- Their domains/sectors; their reusable quantified proof stories

## Step 3 — Fill the Profile Workbook, then compile + validate

The workbook (`<home>/profile/Profile_Workbook_<name>.xlsx`) is the **single
source of truth the user edits**; the `.py`/`.md` files are *compiled* from it
(the engine reads those, but the user never edits them by hand). Fill the
workbook tabs from the interview:
- **Identity** — name, contact, links, education, certifications, training.
- **Skills Matrix** — one row per (tool, company): the truth source. Mark
  portfolio-only / never-used honestly. A tool with no company and no flag is
  treated as "confirm" — not yet attributed.
- **Experience** — per-company domain / what-you-did / leadership.
- **Career Highlights, Roles, Role Bullets, Tech Expertise, Projects, Bases
  Config** — the two bases. Build **LEADER** (people-manager framing) and
  **HANDSON** (IC/builder framing) from the *same* roles; reframe, don't invent.

Then compile and validate:
```
python3 ${CLAUDE_PLUGIN_ROOT}/templates/compile_profile.py \
    <home>/profile/Profile_Workbook_<name>.xlsx  <home>/profile
python3 ${CLAUDE_PLUGIN_ROOT}/templates/validate_profile.py <home>/profile
```
`compile_profile.py` writes `profile.py`, `bases.py`, `verified_skills.md`.
`validate_profile.py` is the **truthfulness check**: it flags any tool the bases'
Areas of Expertise or cert line claims that the Skills Matrix doesn't back. Fix
flagged items in the workbook (attribute to a company, mark portfolio-only, or
remove) and recompile until it's clean. Every tool in the bases MUST trace to the
Skills Matrix — that's what keeps applications truthful.

## Step 4 — Verify the build works

Write a tiny throwaway script in `<home>/.system/scripts/` that sets
`JS_PROFILE=<home>/profile/profile.py`, execs `<home>/.system/engine/build_docs.py`,
and calls `build_resume(...)` once with the LEADER base to write a sample résumé
**into a scratch dir (`<home>/.system/scripts/`), not `docs/current/`** — so no
self-test artifact lands in the user's batch folder. Open it, confirm the
name/contact/education render correctly, then remove it. Removal is **best-effort
(U1)**: if the delete permission is declined, leave the sample where it is and
tell the user it's a harmless self-test file they can delete. If the build errors,
fix the profile files before finishing.

## Step 5 — Hand off

Tell the user setup is done and what they got: their **Profile Workbook** (the one
file they edit), two base résumés, and a tracker. Explain the daily loop: paste
job links into the tracker, then ask to "process job opportunities."

Also point out the **manual job descriptions** folder: when a posting can't be
read from the web (taken down, behind a login, blocked), save the description
into `docs/manual_job_descriptions/` as `YYYYMMDD Company - Job Title.docx` and
the next run picks it up automatically — no pasting. Used files move to its
`archive/` subfolder.

Explain how to **tune over time**: edit the Profile Workbook, then say "update my
profile" — you'll recompile `profile.py`/`bases.py`/`verified_skills.md` and re-run
the truthfulness check. The workbook is the source of truth; never hand-edit the
compiled files.

## Updating later ("update my profile")
When the user edits the workbook (or asks to add/confirm a skill), re-run the
compile + validate from Step 3 and report what the truthfulness check found. This
is also where the skills-demand report (from `process-opportunities`) pays off:
add the in-demand skills they can legitimately claim to the Skills Matrix.
