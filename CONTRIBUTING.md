# Contributing / Maintainer notes

## Continuous build gate (Epic Q)

Every push and pull request runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml),
which executes `./build.sh` on a clean, full-history checkout. That runs the same
two integrity guards a release does:

- **required-files check** — the built `.plugin` must contain every runtime file.
- **personal-data guard** — the build *fails* if any real profile file
  (`profile/profile.py`, `bases.py`, `verified_skills.md`) is tracked.

A passing run uploads the `.plugin` as a downloadable **build artifact** (it does
**not** tag or cut a Release — that stays the Release workflow's job).

### Q2 — require the build check on `main`

`main` must be protected so a failing build (or a PII-leaking commit) cannot land.
The CI job's status-check context is **`build`** (the job id in `ci.yml`).

Set it once (needs admin on the repo):

```bash
gh api -X PUT repos/marc4data/job_search_utility/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f 'required_status_checks[strict]=true' \
  -f 'required_status_checks[contexts][]=build' \
  -f 'enforce_admins=false' \
  -F 'required_pull_request_reviews=null' \
  -F 'restrictions=null'
```

Or in the UI: **Settings → Branches → Add branch protection rule** for `main` →
*Require status checks to pass before merging* → select **build**.

Once set, a PR whose CI build fails cannot be merged, and direct pushes to `main`
that fail the build are rejected.
