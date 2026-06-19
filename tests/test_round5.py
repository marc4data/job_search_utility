"""Regression tests for Round 5 (v0.4.0): canonical-tracker resolution (T1),
skills-demand index v2 (R1-R4), and the demand review (R5).

Scoring integrity is strengthened, not changed: T1 guarantees the True ATS Score
reaches the canonical tracker and never a user-made backup/OG/copy.
"""
import importlib.util
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(REPO_ROOT, "templates")
sys.path.insert(0, TEMPLATES)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _ats():
    return _load("ats_t1", os.path.join(TEMPLATES, "ats_score_template.py"))


def _make_tracker_dir(tmp_path, *names):
    tdir = tmp_path / "tracker"
    tdir.mkdir()
    for n in names:
        (tdir / n).write_text("x")
    return tmp_path


# ── T1: canonical tracker resolution ─────────────────────────────────────────
def test_t1_resolves_canonical_ignoring_og_backup(tmp_path):
    ats = _ats()
    home = _make_tracker_dir(
        tmp_path,
        "job_search_tracker_marc_alexander.xlsx",
        "job_search_tracker_marc_alexander - OG.xlsx",   # user backup
        "job_search_tracker_marc_alexander_copy.xlsx",   # a copy
        "~$job_search_tracker_marc_alexander.xlsx",       # lock file
    )
    resolved = ats._find_tracker(str(home))
    assert os.path.basename(resolved) == "job_search_tracker_marc_alexander.xlsx"


def test_t1_halts_when_ambiguous(tmp_path):
    ats = _ats()
    home = _make_tracker_dir(
        tmp_path,
        "job_search_tracker_marc_alexander.xlsx",
        "job_search_tracker_jordan_rivera.xlsx",         # two canonical-looking
    )
    with pytest.raises(SystemExit, match="AMBIGUOUS"):
        ats._find_tracker(str(home))


def test_t1_halts_when_none(tmp_path):
    ats = _ats()
    home = _make_tracker_dir(tmp_path, "my notes.xlsx", "tracker - OG.xlsx")
    with pytest.raises(SystemExit, match="Could not resolve"):
        ats._find_tracker(str(home))


def test_t1_backup_name_detection():
    ats = _ats()
    assert ats._is_backup_name("job_search_tracker_x - OG.xlsx")
    assert ats._is_backup_name("job_search_tracker_x_backup.xlsx")
    assert ats._is_backup_name("job_search_tracker_x (1).xlsx")
    assert not ats._is_backup_name("job_search_tracker_marc_alexander.xlsx")
