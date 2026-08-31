#!/usr/bin/env bash
# build.sh — package job-search-tailor into a distributable .plugin (zip).
#
# Produces "<name>.plugin" containing only the runtime payload (no dev/test
# files, no git metadata, no personal data), with files at the archive root so
# it unpacks straight into a plugin folder. Backlog #13.
#
# Usage:  ./build.sh
set -euo pipefail
cd "$(dirname "$0")"

NAME=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['name'])")
VERSION=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")
OUT="${NAME}.plugin"

# Safety: never package real (non-example) personal profile files.
for personal in profile/profile.py profile/bases.py profile/verified_skills.md; do
  if git ls-files --error-unmatch "$personal" >/dev/null 2>&1; then
    echo "ERROR: $personal is tracked — refusing to build (would leak personal data)." >&2
    exit 1
  fi
done

# Export tracked runtime files at HEAD. git archive => files at zip root and
# never includes untracked/gitignored junk or the .git dir. We list runtime
# paths explicitly, which naturally omits tests/, pytest.ini, BACKLOG.md, etc.
rm -f "$OUT"
git archive --format=zip -o "$OUT" HEAD \
  .claude-plugin \
  README.md \
  LICENSE \
  requirements.txt \
  engine \
  profile \
  references \
  skills \
  templates

# Validate the package contains the files the plugin needs to run.
# Capture the listing once (piping `unzip | grep -q` would SIGPIPE unzip and,
# under `set -o pipefail`, falsely report a failure).
CONTENTS=$(unzip -l "$OUT")
REQUIRED=(
  ".claude-plugin/plugin.json"
  "skills/setup-profile/SKILL.md"
  "skills/process-opportunities/SKILL.md"
  "engine/build_docs.py"
  "templates/ats_score_template.py"
  "templates/build_batch_template.py"
  "templates/job_tracker_template.xlsx"   # gitignored by *tracker*.xlsx; must stay tracked to ship (B1)
  "templates/jd_retrieval.py"             # Step-1 JD-retrieval helper (G1/G2/G3)
  "templates/skills_vocab.py"             # shared tool vocabulary (v0.3.0)
  "templates/validate_profile.py"         # truthfulness validator (v0.3.0)
  "templates/skills_demand.py"            # skills-demand repository (v0.3.0)
  "templates/skills_taxonomy.py"          # demand taxonomy/synonym reference (v0.4.0)
  "templates/compile_profile.py"          # Profile Workbook compiler (v0.3.0)
  "templates/manual_jd.py"                # manual-JD fallback + archive (v0.5.0)
  "templates/manual_jd_README_template.md"      # naming guide for the drop folder (v0.5.0)
  "templates/workspace_settings_template.json"  # pre-approved web fetches (v0.5.0)
  "templates/profile_workbook_template.xlsx"  # the editable profile source (v0.3.0)
)
for f in "${REQUIRED[@]}"; do
  if ! grep -q " ${f}$" <<<"$CONTENTS"; then
    echo "ERROR: package is missing required file: $f" >&2
    exit 1
  fi
done

echo "Built $OUT  (v$VERSION)"
echo "--- contents ---"
echo "$CONTENTS"
echo "Structure OK — $OUT is ready to load into Cowork."
