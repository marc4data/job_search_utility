# Backlog — job_search_utility

Starter tickets for turning the `job-search-tailor` plugin from a working
baseline into a viable, shareable product. Priorities: **P0** = do before/around
the first real run, **P1** = correctness & robustness, **P2** = product polish.

Check items off here, or (preferred) create matching GitHub issues — see
`CLAUDE_CODE_KICKOFF.md` step 6.

---

## P0 — Baseline & safety

- [ ] **.gitignore excludes personal data & build artifacts.** Ignore
  `profile/profile.py`, `profile/bases.py`, `profile/verified_skills.md`,
  `*.docx`, `*tracker*.xlsx`, `__pycache__/`, `*.pyc`, `.DS_Store`. Keep
  `profile/*.example.*` tracked.
  *Done when:* running `setup-profile` inside a clone leaves `git status` free of
  any personal file.

- [ ] **Add LICENSE (MIT) and review README for public readers.**
  *Done when:* LICENSE present; README has install + quick-start that a stranger
  can follow.

- [ ] **Lock the scoring invariant in code.** Audit every tracker write; ensure
  only the ATS script writes the *Resume Score*. Remove or retire any
  `direct_score(critique_and_refine(...))` foot-gun from templates; leave a guard
  comment.
  *Done when:* `grep -rn "Resume Score" .` shows the column written only by the
  ATS script.

- [ ] **Automated regression tests (pytest).** (a) `critique_and_refine` never
  writes a tracker; (b) a dummy-profile build renders the profile name and leaves
  no placeholder text; (c) ATS scorer writes the expected column.
  *Done when:* `pytest` passes locally (and in CI, see P2).

## P1 — Correctness & robustness

- [ ] **Tracker robustness.** Don't hardcode sheet name "Applications" or header
  row 3; locate the *Resume Score* column by header and fail with a clear message
  if absent.

- [ ] **Dependency management.** Add `requirements.txt` (python-docx, openpyxl)
  and a friendly check/error in the engine if imports are missing.

- [ ] **Validate `setup-profile` with a real person, end-to-end.** Generate real
  `profile.py`/`bases.py`/`verified_skills.md`, build a sample résumé, eyeball it.
  Log rough edges as new tickets.

- [ ] **JD retrieval UX.** Document the logged-in-Chrome requirement; add a clean
  paste-the-JD fallback path in `process-opportunities`.

- [ ] **`jd_full` helper.** Optional helper that proposes candidate ATS terms from
  pasted JD text (human still curates weights). Speeds up scoring.

## P2 — Product polish

- [ ] **Automate the truthfulness check.** A validator that flags any tool named
  in `bases.py` that is absent from `verified_skills.md`.

- [ ] **Configurable résumé theme** (fonts/colors) via `profile.py`.

- [ ] **Support N bases / arbitrary labels** (not just LEADER/HANDSON).

- [ ] **Reproducible packaging.** A `build.sh`/Makefile target that zips the
  `.plugin` and validates structure.

- [ ] **CI** (GitHub Actions): run `pytest` + plugin-structure validation on push.

- [ ] **Contributor docs + issue templates;** decide attribution/versioning policy.

---

### Suggested first sprint
P0 items 1-4, then P1 "validate setup-profile end-to-end." That gets you a safe,
tested, installable baseline you can hand to a friend with confidence.
