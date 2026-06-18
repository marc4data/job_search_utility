"""Regression tests for Round 3 (v0.3.0): truthfulness validator, skills-demand
repository, and the Profile Workbook compiler.

The truthfulness invariant is the point of the validator, so it's covered hardest:
a tool claimed on the résumé but not backed in verified_skills must be flagged.
"""
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(REPO_ROOT, "templates")
sys.path.insert(0, TEMPLATES)


# ── shared vocabulary ────────────────────────────────────────────────────────
def test_vocab_matching_is_word_boundary_and_alias_aware():
    import skills_vocab as v
    assert v.canon_claim("PowerBI") == "power bi"          # alias
    assert v.canon_claim("Power BI") == "power bi"
    assert "r" in v.tools_in("Python, R for stats")        # 1-letter tool, real
    assert "r" not in v.tools_in("Marc runs reports")      # not inside words
    assert v.canon_claim("Team Leadership") is None        # not a tool → ignored


# ── validator: claims vs verified_skills ─────────────────────────────────────
def _write_profile(d, *, certs, verified):
    d.mkdir(parents=True, exist_ok=True)
    (d / "profile.py").write_text(
        "PROFILE = {'name':'T','contact':'c','cl_contact':'c','links':[],"
        "'education':[],'certifications':%r,'additional_experience':[]}" % certs)
    (d / "bases.py").write_text(
        "BASES = {'X': {'tech_expertise': [('Platform','Snowflake, Tableau, dbt')]}}")
    (d / "verified_skills.md").write_text(verified)


def test_validator_flags_unbacked_tool(tmp_path):
    import validate_profile as vp
    prof = tmp_path / "profile"
    _write_profile(
        prof,
        certs=["Certifications: Snowflake, Tableau"],
        verified=(
            "## Tools / skills NEVER used\n- _(none)_\n"
            "## Skills that are PORTFOLIO / LEARNING ONLY\n- _(none)_\n"
            "## Confirm employer attribution\n- _(none)_\n"
            "## Per-company verified experience\n"
            "### Cue\n- **Stack / tools:** dbt, Tableau\n"),
    )
    errors, warnings = vp.validate(str(prof))
    blob = "\n".join(errors)
    assert "Snowflake" in blob                # claimed (cert+expertise) but no employer
    assert "dbt" not in blob and "Tableau" not in blob   # both backed → not flagged


def test_validator_passes_when_everything_backed(tmp_path):
    import validate_profile as vp
    prof = tmp_path / "profile"
    _write_profile(
        prof,
        certs=["Certifications: Tableau"],
        verified=(
            "## Tools / skills NEVER used\n- _(none)_\n"
            "## Skills that are PORTFOLIO / LEARNING ONLY\n- _(none)_\n"
            "## Confirm employer attribution\n- _(none)_\n"
            "## Per-company verified experience\n"
            "### Cue\n- **Stack / tools:** dbt, Tableau, Snowflake\n"),
    )
    errors, _ = vp.validate(str(prof))
    assert errors == []


# ── skills-demand repository ─────────────────────────────────────────────────
def test_skills_demand_records_and_aggregates(tmp_path):
    import skills_demand as sd
    home = str(tmp_path)
    sd.record_jd(home, "j1", "Co A", "Analytics Engineer", "IC",
                 "dbt SQL Snowflake Airflow Tableau")
    sd.record_jd(home, "j2", "Co B", "Manager, Analytics", "Manager",
                 "dbt SQL Snowflake Looker")
    rows = sd.load_index(home)
    agg = sd.demand(rows)
    assert len(agg["snowflake"]["jobs"]) == 2          # in both jobs
    assert agg["airflow"]["jobs"] == {"j1"}            # only j1
    # corpus file persisted (visible docs/ folder)
    assert os.path.exists(os.path.join(home, "docs", "job_descriptions", "j1.md"))


def test_skills_demand_index_is_idempotent(tmp_path):
    import skills_demand as sd
    home = str(tmp_path)
    sd.record_jd(home, "j1", "Co A", "AE", "IC", "dbt SQL")
    sd.record_jd(home, "j1", "Co A", "AE", "IC", "dbt SQL Snowflake")   # reprocess
    rows = [r for r in sd.load_index(home) if r["job_id"] == "j1"]
    skills = {r["skill"] for r in rows}
    assert skills == {"dbt", "sql", "snowflake"}        # updated, not duplicated
