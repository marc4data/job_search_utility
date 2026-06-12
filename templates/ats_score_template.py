"""
ats_score_TEMPLATE.py — copy to scripts/ats_score_<date>.py for each run.

THIS IS THE AUTHORITATIVE TRACKER SCORE. Run it AFTER build_batch_<date>.py.

It reads each built resume's actual text and scores it against a 25-40 term
jd_full list (weights 3/2/1) built from the real job description. It writes that
True ATS Score into the tracker's "Resume Score" column.

Honesty rule that keeps scores realistic (not auto-100): INCLUDE the genuine
discriminators a sharp recruiter would weigh — required tools you lack, the
company's domain/sector, exact must-have phrases. They register as misses and
pull the score down to where it honestly belongs. A strong fit lands high-80s/
90s; a partial fit lands 70s. A flat 100 means your term list was too soft.
"""
import os, re, importlib.util
try:
    import openpyxl
    from docx import Document  # imported lazily in get_resume_text; checked here for a clear early error
except ImportError as e:
    import sys
    sys.exit(
        f"\n[job-search-tailor] Missing dependency: {e.name}\n"
        "The scorer needs openpyxl (tracker) and python-docx (read resumes).\n"
        "Install them into the SAME Python you run scripts with:\n\n"
        "    python3 -m pip install -r requirements.txt\n\n"
        "Use 'python3 -m pip' (not bare 'pip') so the installer and the\n"
        "interpreter that runs this script are the same one.\n"
    )

HOME    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT     = HOME + "/"
TRACKER = os.path.join(HOME, "job_tracker.xlsx")
SHEET   = "Applications"            # change if your tracker tab is named differently


def get_resume_text(path):
    from docx import Document
    doc = Document(path)
    chunks = [p.text.lower() for p in doc.paragraphs if p.text.strip()]
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                if cell.text.strip():
                    chunks.append(cell.text.lower())
    return " ".join(chunks)


def ats_score(resume_text, jd_terms):
    total = sum(w for _, w in jd_terms)
    found_w, found, missed = 0, [], []
    for term, w in jd_terms:
        if re.search(r'\b' + re.escape(term.lower()) + r'\b', resume_text):
            found_w += w; found.append(f"{term}[{w}]")
        else:
            missed.append(f"{term}[{w}]")
    return (round(found_w / total * 100) if total else 0), found, missed


def write_tracker(row_num, score):
    """Write score into the 'Resume Score' column of the given row (header on row 3)."""
    wb = openpyxl.load_workbook(TRACKER)
    ws = wb[SHEET] if SHEET in wb.sheetnames else wb.active
    headers = [c.value for c in ws[3]]
    try:
        col = headers.index("Resume Score") + 1
    except ValueError:
        raise SystemExit("Could not find a 'Resume Score' column in row 3 of the tracker.")
    ws.cell(row=row_num, column=col, value=score)
    wb.save(TRACKER)
    print(f"  [tracker → row {row_num}: {score}]")


# ════════════════════════════════════════════════════════════════════════════
# ONE BLOCK PER ROLE. Build jd_full from the ACTUAL job description:
#   weight 3 (~5-6): required / must-have terms + the role's defining words
#   weight 2 (~10):  important terms, repeated in the JD, domain-critical
#   weight 1 (~10):  nice-to-haves, supporting vocabulary, sector/domain words
# Include tools/domains you LACK so the score is honest. 25-40 terms total.
# row = the tracker row number you seeded for this job.
# ════════════════════════════════════════════════════════════════════════════
ROLES = [
    {
        "row": 4,
        "company": "Example Co",
        "role": "Director of Analytics",
        "resume": "001_Your Name - Example Co - Director of Analytics - Resume.docx",
        "jd_full": [
            ("business intelligence", 3), ("analytics", 3), ("data quality", 3),
            ("stakeholder", 3), ("reporting", 3),
            ("kpi", 2), ("executive", 2), ("data governance", 2), ("dashboards", 2),
            ("team leadership", 2), ("data strategy", 2), ("performance", 2),
            ("sql", 1), ("tableau", 1), ("power bi", 1), ("self-service", 1),
            ("transformation", 1), ("mentoring", 1), ("metrics", 1),
            # include genuine gaps so the score stays honest, e.g.:
            ("your_sector_domain", 2), ("a_required_tool_you_lack", 2),
        ],
    },
]

def main():
    results = []
    for r in ROLES:
        txt = get_resume_text(OUT + r["resume"])
        score, found, missed = ats_score(txt, r["jd_full"])
        print(f"\nRow {r['row']} | {r['company']} — {r['role']}")
        print(f"  Score:  {score}/100  ({len(found)}/{len(found)+len(missed)} terms)")
        print(f"  Found:  {', '.join(found)}")
        print(f"  Missed: {', '.join(missed)}")
        write_tracker(r["row"], score)
        results.append((r["row"], r["company"], score))

    print("\n" + "=" * 60)
    print("True ATS Scores written to tracker:")
    for row, company, score in sorted(results, key=lambda x: -x[2]):
        print(f"  Row {row}  {company:<16}  {score}/100")
    print("=" * 60)


# Run only when executed as a script (e.g. python3 scripts/ats_score_<date>.py).
# Guarding this lets the regression tests import write_tracker()/ats_score()
# without triggering a real scoring run.
if __name__ == "__main__":
    main()
