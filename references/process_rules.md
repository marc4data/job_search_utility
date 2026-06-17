# Process Rules — résumé + cover-letter tailoring and True ATS scoring

This is the playbook the `process-opportunities` skill follows for every job.
It is deliberately opinionated; it encodes what makes a tailored application
clear the first 6-second recruiter scan and the cover-letter callback decision.

---

## 0. The two invariants (never violate)

1. **Truthfulness.** Never claim a tool, skill, or domain that is not in
   `profile/verified_skills.md` for the relevant company. A genuine gap is
   acknowledged honestly, never fabricated. Skills that are portfolio/learning
   only are always attributed as such — never to an employer.

2. **Scoring integrity.** The number written to the tracker's *Resume Score*
   column is ALWAYS the **True ATS Score** from the ATS script (a 25-40 term
   `jd_full` read from the actual `.docx`). The 3-pass `critique_and_refine()`
   score is a content-QA checklist only and is NEVER written to the tracker.
   (Writing the checklist score is what inflates every role to 100.)

---

## 1a. JD retrieval — resilient, preflight-first (Epic G)

Getting the real job description is where the first live run lost the most time.
The rules below make it reliable and headless-by-default. The helper
`${CLAUDE_PLUGIN_ROOT}/templates/jd_retrieval.py` does the deterministic parsing;
you do the fetches.

1. **Read the link, not the label.** The *Sourced From (w/link)* cell often shows
   text like "Linkedin" or "DM Message" while the real URL is the cell's
   **hyperlink target**. Always resolve via `resolve_cell_link(cell)` (which
   reads `cell.hyperlink.target` first, then any URL in the value). Find the
   column by header with `find_link_column(headers)`, never by a fixed index.

2. **Preflight the whole batch first.** Call `read_job_links(ws)` to classify
   every selected role before fetching anything: `linkedin-guest` / `web-fetch`
   / `local-file` / `needs-paste`. This lets you ask for all manual pastes once.

3. **LinkedIn → guest endpoint first.** Logged-in LinkedIn pages are JS-rendered
   and **hide the description on jobs you've already applied to**
   ("Application submitted"). Parse the jobId (`parse_linkedin_job_id`) from a
   `/jobs/view/<id>` or `currentJobId=<id>` URL and fetch
   `/jobs-guest/jobs/api/jobPosting/<jobId>` (`linkedin_guest_url`) **before**
   any browser/login path — it returns the raw JD without a session. Only if the
   guest endpoint fails do you fall back to an in-browser read. A LinkedIn URL
   with no parseable jobId degrades to browser, then paste — never an empty shell.

4. **Chrome is a last resort, not a prerequisite.** Most links resolve headlessly
   (embedded link + guest endpoint + plain fetch). Recommend installing Claude in
   Chrome only when a specific role genuinely requires it after headless attempts.

5. **Never guess a JD.** A role whose JD can't be retrieved is added to the single
   batched paste request, or explicitly deferred with a note (it appears in the
   Step 5 summary table with score `—` and a reason). You never build or score a
   role from an assumed or partial description.

---

## 1. Pick the base: LEADER or HANDSON

- **LEADER** — people-manager, director, head-of, VP roles. The job is about
  leading teams, strategy, stakeholders, and outcomes.
- **HANDSON** — individual contributor, player-coach, senior-IC, "manager but
  must be hands-on" roles. The job requires personally building things.
- **Tie-breaker:** if the title says "Manager/Director" but the requirements are
  hands-on (writes code, designs schemas, builds pipelines), use **HANDSON**.

---

## 2. Order of operations (mandatory)

1. Research the company's *specific* situation — not just the JD.
2. Write **cover-letter Para 1** (the company insight) BEFORE the résumé summary.
3. Write the résumé summary (credential-dense; no overlap with the CL narrative).
4. Write **CL Para 2** (one story bridging Para 1's problem to your proof).
5. Write **CL Para 3** (forward-looking judgment / honest-gap handling).
6. Run the Recruiter Review checklist (section 5) on both documents.
7. Write the batch script and build.
8. Run the ATS script to compute and write the True ATS Score.

---

## 3. The résumé: "Does this person qualify?"

A scanning document. First pass is 6-10 seconds. Make the summary evidence-dense,
clinical, restrained.

- **Two paragraphs.** Para 1: who you are for THIS role + core proof (companies,
  scale, specific work). Para 2: technical depth or a supporting credential not
  in Para 1 — noticeably shorter. It supports; it does not repeat.
- Specific companies, numbers, and outcomes in every paragraph.
- Keywords embedded naturally, but the primary reader is a fast-scanning human.
- **Tone rules:** no certifications in the summary; no tenure proclamations
  ("15+ years of…"); no sales-pitch framing ("this rare combination…"); no
  "brings" ("brings deep expertise" → say what you did). Let facts argue.

**Section order:** Professional Summary → Career Highlights → Areas of Expertise
→ Professional Experience → Additional Experience → Education → Certifications →
Technical Expertise. (HANDSON base puts Certifications before Education.)

---

## 4. The cover letter: "Do I want to talk to this person?"

A persuasion document, read only after the résumé clears. Three moves, each
paragraph a different job:

- **Para 1 — their problem, not your bio.** Open with a specific, researched
  observation about the company's situation. You do not appear until Para 2.
  Never "I am writing to express my interest…".
- **Para 2 — one story.** ONE vivid, specific story (situation → action →
  outcome) that maps directly to the pain named in Para 1. Not a career summary.
- **Para 3 — forward, not backward.** Your read on what you'd prioritize in the
  role, OR why it's the right next step, OR an honest gap + counterweight.

**No overlap:** the résumé summary and the cover letter must not tell the same
story. If the CL could be sent to a different company with minor edits, it isn't
specific enough.

---

## 5. Recruiter Review checklist (run on every draft)

1. **Opener test** — Para 1 must not start with a formula ("results-driven…").
2. **"Brings" audit** — replace every "brings" with active, declarative language.
3. **Redundancy check** — Para 2 must add something Para 1 didn't; keep it shorter.
4. **Differentiator placement** — your strongest credential in the first two sentences.
5. **JD pain language** — the JD's specific pain words appear in the résumé summary.
6. **Quantification** — at least two specific numbers/outcomes in the summary.
7. **Cover-letter Para 1 hook** — a company insight, not your credentials.
8. **Genuine-gap handling** — every real gap is acknowledged AND paired with a counterweight.
9. **Scale signaling** — for large employers, name the comparable scale you've operated at.
10. **Differentiation** — résumé is clinical; cover letter is conversational; they don't repeat.

---

## 6. The 3-pass content-QA system (`critique_and_refine`)

A keyword presence check that triggers honest patches. **Its score is QA only —
never the tracker score.**

- **Pass 1 — honest score.** Scans the draft against `jd_hard` (5-10 genuine
  discriminators as `(term, weight)`), word-boundary matched.
- **Pass 2 — gap patches** (conditional). If score < 80 or a weight-3 term is
  missing, apply `gap_patches` (append honest text to a summary paragraph or add
  an expertise item), then re-score. Genuine gaps are mapped to `None` — flagged,
  never fabricated.
- **Pass 3 — tight patches.** Append precise terms to existing Technical
  Expertise rows via `tight_patches`. Genuine gaps stay `None`.

`jd_hard` holds real discriminators, not terms already universal in your base.

---

## 7. True ATS Score (the tracker number)

Built and written ONLY by the ATS script. Construct `jd_full` (25-40 terms,
weights 3/2/1) from:
1. The actual JD text (verbatim required terms).
2. Role-typical vocabulary for that function/level.
3. **The company's domain/sector terms** — and any required tools you lack.

Including genuine gaps is the point: they register as misses and pull the score
to where it honestly belongs.

- weight 3 (~5-6): required / must-have terms; the words that define the role.
- weight 2 (~10): important, repeated, or domain-critical terms.
- weight 1 (~10): nice-to-haves, supporting vocabulary, sector words.

**Expected ranges:** 75-95 for a well-targeted strong fit; 70s for a partial
fit with real tool/domain gaps. **A flat 100 is a red flag** that the term list
was too soft — add the discriminators a sharp recruiter would actually weigh.

---

## 9. The batch summary table (mandatory — Epic J)

Every batch ends with the same fixed-format table so the user always gets a
consistent, scannable result. It is **emitted by the ATS script**
(`summary_table(...)`), not free-authored — so each row's Score is exactly the
True ATS Score written to that role's tracker row.

- Columns, in order: **Score** · **Role** (`Company — Title`) · **Base**
  (`LEADER`/`HANDSON`) · **Why** (the strongest matched strength, then
  `gap: <the genuine gap>`).
- **Sorted by Score, descending.**
- Followed by a one-line **MIN / AVG / MAX** summary and the reminder that these
  are honest True ATS Scores (70s = partial fit; high-80s–90s = strong fit).
- A role deferred for a missing JD (§1a) appears with score `—` and its reason —
  listed, never silently dropped.

The "Why" never invents a strength or hides a real gap (invariant #2); the Score
is always the True ATS Score (invariant #1).

---

## 8. File hygiene

- Prefix every output file `001_` so your documents sort to the top of any folder.
- Naming: `001_<Name> - <Company> - <Role Stub> - Resume.docx` (and `- Cover Letter.docx`).
- Keep each run's `build_batch_<date>.py` and `ats_score_<date>.py` for provenance.
