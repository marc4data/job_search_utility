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

## Step 1 — Establish the working folder

Ask the user where their job search lives (a folder on their computer). If no
folder is connected, request one. Inside it, create this layout and copy the
engine + templates in:

```
<home>/engine/build_docs.py          ← copy from ${CLAUDE_PLUGIN_ROOT}/engine/
<home>/profile/                      ← you will generate the 3 files here
<home>/scripts/                      ← per-run build/ats scripts go here later
<home>/job_tracker.xlsx             ← copy from ${CLAUDE_PLUGIN_ROOT}/templates/job_tracker_template.xlsx
```

Copy `${CLAUDE_PLUGIN_ROOT}/engine/build_docs.py` to `<home>/engine/`. Copy the
tracker template to `<home>/job_tracker.xlsx`. Keep the `templates/*.py` handy —
each run will copy them into `<home>/scripts/`.

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

## Step 3 — Generate the three profile files

Use the examples as the exact shape:
- `${CLAUDE_PLUGIN_ROOT}/profile/profile.example.py` → write `<home>/profile/profile.py`
- `${CLAUDE_PLUGIN_ROOT}/profile/bases.example.py` → write `<home>/profile/bases.py`
- `${CLAUDE_PLUGIN_ROOT}/profile/verified_skills.example.md` → write `<home>/profile/verified_skills.md`

Build **two** bases from the same history:
- **LEADER** — people-manager framing (strategy, teams, stakeholders, outcomes).
- **HANDSON** — individual-contributor framing (what they personally built, tools, depth).
Most people have done both; reframe the same roles, don't invent new ones.

Every tool named in `bases.py` MUST also appear in `verified_skills.md`. If it's
not verified, leave it out.

## Step 4 — Verify the build works

Write a tiny throwaway script in `<home>/scripts/` that sets
`JS_PROFILE=<home>/profile/profile.py`, execs `<home>/engine/build_docs.py`, and
calls `build_resume(...)` once with the LEADER base to produce a sample résumé.
Open it, confirm the name/contact/education render correctly, then delete the
sample. If it errors, fix the profile files before finishing.

## Step 5 — Hand off

Tell the user setup is done and what they got (their two base résumés, verified-
skills file, and tracker). Explain the daily loop: paste job links into the
tracker, then ask to "process job opportunities" — which runs the
`process-opportunities` skill.

Remind them the verified-skills file is theirs to keep updated; it's what keeps
every application truthful.
