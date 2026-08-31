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

## Release workflow (Epic P)

Cutting a Release is a **tag** action, not a push action.
[`.github/workflows/release.yml`](.github/workflows/release.yml) fires on a
`vX.Y.Z` tag and does three things in order:

1. **Verifies the tag matches `plugin.json`.** A `v0.5.0` tag on a commit whose
   `plugin.json` says `0.4.0` fails the release — that mismatch would ship a
   package announcing a different version than the Release it lives under, which
   is exactly the drift K1 exists to prevent.
2. **Runs `./build.sh`** — the same required-files and personal-data guards CI
   runs, so a Release can never ship a package CI would have rejected.
3. **Publishes the Release** with the `.plugin` attached and the CHANGELOG's
   section for that version as its notes (via `tools/release_notes.py`). Release
   notes are never hand-written, so they cannot drift from the CHANGELOG.

### Cutting a release

```bash
# 1. main must already carry the version bump + CHANGELOG entry (see the
#    "[v0.5.0] Bump version" commit convention).
git checkout main && git pull

# 2. Confirm what will be published before tagging.
python3 tools/release_notes.py "$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")"

# 3. Tag and push — the workflow does the rest.
git tag -a v0.5.0 -m "job-search-tailor v0.5.0"
git push origin v0.5.0
```

Watch it with `gh run list --workflow=release.yml`; the result appears in
`gh release list`.

### Retroactive tags

`v0.4.0` predates this workflow. A tag on a commit that has no `release.yml`
triggers nothing, so its Release was created directly with
`gh release create --notes-file` from the same `tools/release_notes.py` output —
same notes, same source of truth, just no automated build attached.
