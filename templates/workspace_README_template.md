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
| **docs/manual_job_descriptions/** | Where you save a job description when the posting can't be read from the web. Name the file `YYYYMMDD Company - Job Title.docx` and the next run uses it automatically — no pasting. See the README inside that folder. |
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

If a posting can't be read (it was taken down, or it's behind a login), save the
description into `docs/manual_job_descriptions/` as
`YYYYMMDD Company - Job Title.docx` — Word, Markdown, or plain text. The next run
finds it by company and job title, uses it, then files it into that folder's
`archive/`. You won't be asked to paste anything.

## Two promises this workflow keeps

- **Honest scoring.** The score in your tracker is a realistic match score that
  *includes* the requirements you don't meet — never an automatic 100.
- **Truthfulness.** Nothing is ever claimed on your résumé that isn't in your
  verified skills. Portfolio/learning-only skills are always labeled as such.
  Your cover letter says what you've actually done and what genuinely interests
  you about the company — it never presumes to tell them how to run their
  business.
