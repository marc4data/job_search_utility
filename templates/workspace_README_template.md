<!--
workspace_README_TEMPLATE.md — setup-profile copies this to <home>/README.md and
fills in {{NAME}}. This is the plain-language guide the user reads. Keep it free
of internal file paths beyond the folder names below.
-->
# {{NAME}}'s Job Search

This folder runs your tailored résumé + cover-letter workflow. Here's what each
part is for — you only ever touch the first three.

| Folder | What it's for |
|---|---|
| **tracker/** | Your one living job tracker (an Excel file). Add a row per job — company, role, date, link — and the score for each application lands here. |
| **docs/current/** | Your **latest batch only** — the résumés and cover letters from the most recent run, ready to send. |
| **docs/submitted/** | A flat archive of everything from past batches. Files are named company-first, so a company's documents sort together. |
| **profile/** | Who you are and what you can truthfully claim: your base résumés, your skills, and dated history. The skills file is what keeps every application honest. |
| config.yaml | Your preferences for how the résumé is laid out (added later). |
| .system/ | The technical engine. Safe to ignore — nothing here needs your attention. |

## How you use it

1. **Add jobs** to the tracker in `tracker/` (one row each).
2. Say **"process job opportunities"** — it tailors a résumé + cover letter for
   each job, scores how well your résumé matches, and writes that score back to
   the tracker.
3. **Find your new documents** in `docs/current/`. Older ones move to
   `docs/submitted/` automatically.

## Two promises this workflow keeps

- **Honest scoring.** The score in your tracker is a realistic match score that
  *includes* the requirements you don't meet — never an automatic 100.
- **Truthfulness.** Nothing is ever claimed on your résumé that isn't in your
  verified skills. Portfolio/learning-only skills are always labeled as such.
