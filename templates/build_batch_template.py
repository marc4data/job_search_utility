"""
build_batch_TEMPLATE.py — copy to scripts/build_batch_<date>.py for each run.

WHAT THIS DOES
  Builds one tailored resume + cover letter per role and runs the 3-pass
  content-QA (critique_and_refine). It does NOT write any score to the tracker.
  The tracker score is written ONLY by ats_score_<date>.py (run that after this).

WORKING-FOLDER LAYOUT this expects (created by the setup-profile skill):
  <home>/.system/engine/build_docs.py
  <home>/profile/profile.py, bases.py, verified_skills.md
  <home>/.system/scripts/<date>/   (this file)
  <home>/tracker/job_search_tracker_<name>.xlsx
  <home>/docs/current/             (built .docx land here)
"""
import os, sys, importlib.util

# ── resolve the working folder by walking up to the dir that holds .system/ ──
# Robust regardless of how deep under .system/scripts/<date>/ this copy sits.
def _find_home(start):
    d = os.path.dirname(os.path.abspath(start))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".system")) and os.path.isdir(os.path.join(d, "profile")):
            return d
        d = os.path.dirname(d)
    raise SystemExit("Could not locate the job-search working folder "
                     "(no .system/ ancestor of this script).")

HOME    = _find_home(__file__)
ENGINE  = os.path.join(HOME, ".system", "engine", "build_docs.py")
PROFILE = os.path.join(HOME, "profile", "profile.py")
BASES   = os.path.join(HOME, "profile", "bases.py")
OUT     = os.path.join(HOME, "docs", "current") + os.sep

os.makedirs(OUT, exist_ok=True)
os.environ["JS_PROFILE"] = PROFILE
os.environ["JS_OUT_DIR"] = OUT

# load the engine (defines build_resume, build_cover_letter, critique_and_refine, ...)
exec(compile(open(ENGINE).read(), ENGINE, "exec"), globals())

# load the two base resumes
_spec = importlib.util.spec_from_file_location("bases", BASES)
_b = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_b)
BASES = _b.BASES


def do_role(base, company, role, location, stub, target_title,
            summary, expertise, jd_hard, gap_patches=None, tight_patches=None, cover=None):
    """Build resume + cover letter and run 3-pass content QA. NO tracker write.

    base: "LEADER" or "HANDSON"
    """
    b = BASES[base]
    rpath = OUT + stub + " - Resume.docx"
    build_resume(rpath, target_title, summary, expertise,
                 career_highlights=b["career_highlights"], experience=b["experience"],
                 projects=b.get("projects"), tech_expertise=b["tech_expertise"],
                 certs_before_edu=b.get("certs_before_edu", False))
    build_cover_letter(OUT + stub + " - Cover Letter.docx",
                       company, role, location, cover or [])
    rd = {"company": company, "role": role, "jd_hard": jd_hard,
          "gap_patches": gap_patches or {}, "tight_patches": tight_patches or {}}
    critique_and_refine(
        rpath, company, role, target_title, summary, expertise, rd,
        career_highlights=b["career_highlights"], experience=b["experience"],
        tech_expertise=b["tech_expertise"], certs_before_edu=b.get("certs_before_edu", False))
    print(f"✓  {company} — {role}\n")


# ════════════════════════════════════════════════════════════════════════════
# ONE BLOCK PER ROLE. Pick base by reading the JD (see references/process_rules.md):
#   LEADER  = people-manager / director / head-of role
#   HANDSON = IC / player-coach / hands-on technical role
# Write the summary + cover letter AFTER reading the JD and verified_skills.md.
# jd_hard = 5-10 genuine discriminators for the 3-pass QA (not the tracker score).
# ════════════════════════════════════════════════════════════════════════════
do_role(
    base="LEADER",
    company="Example Co",
    role="Director of Analytics",
    location="Remote",
    stub="001_Your Name - Example Co - Director of Analytics",
    target_title="Director of Analytics",
    summary=[
        "Para 1 — who you are for THIS role + core proof (companies, scale, what you did). "
        "Evidence-dense, short declarative sentences, no 'brings', no generic opener.",
        "Para 2 — technical depth or a supporting credential not covered in Para 1. Shorter.",
    ],
    expertise=["Business Intelligence", "KPI Frameworks", "Executive Reporting",
               "Data Governance", "Team Leadership"],
    jd_hard=[("business intelligence", 3), ("data quality", 3), ("stakeholder", 3),
             ("kpi", 2), ("executive", 2), ("team leadership", 2)],
    gap_patches={}, tight_patches={},
    cover=[
        "Para 1 — the COMPANY's specific situation. You don't appear here.",
        "Para 2 — ONE vivid story that maps to the problem in Para 1.",
        "Para 3 — forward-looking judgment: what you'd prioritize, or an honest gap "
        "acknowledged with a counterweight.",
    ],
)

print("=" * 68)
print("Build complete. Tracker NOT written here.")
print("Now run scripts/ats_score_<date>.py to compute & write True ATS Scores.")
print("=" * 68)
