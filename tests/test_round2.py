"""Regression tests for Round 2 (v0.2.0): versioning banner (K1), JD-retrieval
helper (G1/G2/G3), and the mandatory batch summary table (J1).

Prompt-only behavior (the model actually fetching a JD, the live paste UX) is
validated in clean-room runs, not here. These tests lock the deterministic,
testable surface: the version source of truth, the retrieval helper's pure
functions, and the table the ATS script emits.
"""
import importlib.util
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_JSON = os.path.join(REPO_ROOT, ".claude-plugin", "plugin.json")
SKILLS = [
    os.path.join(REPO_ROOT, "skills", "process-opportunities", "SKILL.md"),
    os.path.join(REPO_ROOT, "skills", "setup-profile", "SKILL.md"),
]

# A semver like 1.2.3 or a v-prefixed one — what a *hardcoded* banner would contain.
_VERSION_LITERAL = re.compile(r"\bv?\d+\.\d+\.\d+\b")


# ── K1: versioning + runtime banner ─────────────────────────────────────────
def test_plugin_version_is_0_2_0():
    with open(PLUGIN_JSON) as f:
        assert json.load(f)["version"] == "0.2.0"


def test_skills_read_version_from_plugin_json_not_hardcoded():
    for path in SKILLS:
        with open(path) as f:
            text = f.read()
        # Each skill must point at the single source of truth...
        assert "plugin.json" in text, f"{path} does not reference plugin.json"
        # ...and must NOT bake in a concrete version that would drift.
        leaked = _VERSION_LITERAL.findall(text)
        assert not leaked, f"{path} contains a hardcoded version literal: {leaked}"
