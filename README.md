# Job Search Tailor

A Cowork plugin that turns a job posting into a tailored résumé + cover letter
and scores how well your résumé actually matches the role — with a **realistic
ATS score, not an inflated 100**.

It encodes a recruiter's playbook: a 6-second-scan résumé, a three-move cover
letter, a 3-pass content review, and a separate, honest ATS scorer.

## What you get

Two skills:

- **setup-profile** — a one-time interview that builds *your* two base résumés, a
  verified-skills file (so applications never fabricate experience), and a job
  tracker. Say *"set up my job search."*
- **process-opportunities** — the daily loop. Paste job links into the tracker,
  then say *"process job opportunities."* It tailors a résumé + cover letter for
  each, runs the 3-pass review, and writes a True ATS score per job.

## Two ideas that make it work

1. **Truthfulness.** Your `verified_skills.md` is the source of truth. Nothing
   gets claimed unless it's there. Portfolio-only skills are always labeled as
   such. Genuine gaps are acknowledged with a counterweight, never invented.
2. **Honest scoring.** The number in your tracker is the **True ATS Score** —
   computed from the real job description (25-40 weighted terms) read from the
   finished document, *including* the requirements you don't meet. A strong fit
   lands in the high 80s/90s; a partial fit lands in the 70s. A flat 100 means
   the term list was too soft. The keyword-checklist used during drafting is
   QA only and is never written to the tracker.

## Process flow

Two phases: a **one-time setup** that builds your reusable assets, then a
**per-job loop** you run for every opportunity. The two invariants are baked into
the flow — `verified_skills.md` gates every claim, and the tracker's *Resume
Score* is written **only** by the ATS script (the content-QA score never is).

```mermaid
flowchart TD
    subgraph SETUP["🛠 One-time setup · say &quot;set up my job search&quot;"]
        direction TB
        IV["Interview / upload résumé"] --> PR["profile.py<br/>identity &amp; contact"]
        IV --> BA["bases.py<br/>LEADER + HANDSON base résumés"]
        IV --> VS["verified_skills.md<br/>source of truth for claims"]
        IV --> TK[("job_tracker.xlsx")]
    end

    subgraph LOOP["🔁 Per job · say &quot;process job opportunities&quot;"]
        direction TB
        L1["Paste job link into tracker"] --> L2["Research the company's<br/>specific situation"]
        L2 --> L3{"LEADER or<br/>HANDSON?"}
        L3 --> L4["Draft in order:<br/>CL Para 1 → résumé summary → CL Para 2 &amp; 3"]
        L4 --> L5["Recruiter Review checklist<br/>(10 points)"]
        L5 --> BUILD[["build_batch_&lt;date&gt;.py<br/>→ engine/build_docs.py"]]
        BUILD --> DOCS[/"résumé + cover letter .docx"/]
        DOCS --> QA["critique_and_refine()<br/>3-pass content QA<br/>— QA only, never written —"]
        DOCS --> ATS[["ats_score_&lt;date&gt;.py<br/>True ATS Score<br/>jd_full · 25–40 weighted terms<br/>read from the finished .docx"]]
    end

    TK ==> L1
    VS -. "gates every claim<br/>(truthfulness)" .-> L4
    BA --> BUILD
    PR --> BUILD
    ATS ==>|"writes Resume Score"| TK

    classDef authoritative fill:#1f3864,stroke:#1f3864,color:#fff;
    classDef qaonly fill:#f2f2f2,stroke:#9aa0a6,color:#202124,stroke-dasharray:4 3;
    class ATS,TK authoritative;
    class QA qaonly;
```

**Reading the diagram:** the dark path (`ats_score` → `job_tracker.xlsx`) is the
only thing that writes the *Resume Score*. The dashed `critique_and_refine` box is
a drafting aid whose checklist score is deliberately a dead end. Everything you
claim must trace back to `verified_skills.md`.

## Quick start

1. Install the plugin.
2. *"Set up my job search"* → answer the interview (or upload your résumé).
3. Paste a few job links into `job_tracker.xlsx` (Company, Role, Date, URL).
4. *"Process job opportunities"* → get tailored documents + honest scores.

## How it's organized

```
engine/build_docs.py         the builder + reviewer (no personal data)
profile/                     YOUR data: profile.py, bases.py, verified_skills.md
                             (the *.example.* files show the shape)
templates/                   per-run build + ATS scripts, and the tracker
references/process_rules.md   the full playbook (read by the skills)
skills/                      setup-profile, process-opportunities
```

Your working folder (created during setup) mirrors this: `engine/`, `profile/`,
`scripts/`, and `job_tracker.xlsx`, with finished `.docx` files in the root.

## Notes

- Job descriptions are read with the browser (works with LinkedIn, Indeed, etc.),
  or you can paste them in. No special connector required.
- Document generation uses `python-docx` and `openpyxl` (installed on demand).
- It's deliberately opinionated about résumé/cover-letter craft — that's the point.
