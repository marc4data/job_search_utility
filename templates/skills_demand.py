"""skills_demand.py — the skills-demand repository (Epic H).

A persistent, accumulating record of which skills employers ask for across every
processed job, plus the payoff: which in-demand skills are NOT backed in the
user's profile, so they can decide whether to augment the Profile Workbook.

  record_jd()  persist one processed JD's skills   -> docs/job_descriptions/<id>.md + skills_demand_index.csv
  demand()     aggregate by skill × level
  report()     surface demand -> profile gaps        -> the "skills to consider" list

The index is idempotent on job_id (re-processing a job updates, never dupes).
During process-opportunities, call record_jd() per role after retrieval; at the
end, run `python3 skills_demand.py <home>` to print the demand + gap report.
"""
import csv
import os
import sys

from skills_vocab import TOOLS, DISPLAY, CATEGORY, tools_in
from validate_profile import load_truth

# CI/CD and source-systems are table-stakes/context, not strategic skill gaps.
LOW_PRIORITY = {"ci-cd", "source-system"}


def _corpus_dir(home):
    d = os.path.join(home, "docs", "job_descriptions")
    os.makedirs(d, exist_ok=True)
    return d


def _index_path(home):
    return os.path.join(_corpus_dir(home), "skills_demand_index.csv")


def disp(skill):
    return DISPLAY.get(skill, skill.title())


def record_jd(home, job_id, company, role, level, jd_text):
    """Persist one JD's text + its extracted skills; update the index idempotently."""
    corpus = _corpus_dir(home)
    with open(os.path.join(corpus, f"{job_id}.md"), "w") as f:
        f.write(f"# {company} — {role} ({level})\n\n{jd_text}\n")

    skills = sorted(tools_in(jd_text))
    rows = [r for r in load_index(home) if r["job_id"] != job_id]   # drop old version
    for s in skills:
        rows.append({"job_id": job_id, "company": company, "role": role,
                     "level": level, "skill": s})
    _write_index(home, rows)
    return skills


def load_index(home):
    path = _index_path(home)
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write_index(home, rows):
    with open(_index_path(home), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["job_id", "company", "role", "level", "skill"])
        w.writeheader(); w.writerows(rows)


def demand(rows):
    agg = {}
    for r in rows:
        d = agg.setdefault(r["skill"], {"jobs": set(), "levels": set()})
        d["jobs"].add(r["job_id"]); d["levels"].add(r["level"])
    return agg


def report(home, profile_dir):
    rows = load_index(home)
    if not rows:
        print("No JDs recorded yet — process some opportunities first."); return
    agg = demand(rows)
    backed, portfolio, confirm, never = load_truth(profile_dir)
    n = len({r["job_id"] for r in rows})
    ranked = sorted(agg.items(), key=lambda kv: (-len(kv[1]["jobs"]), kv[0]))

    print(f"\nSKILLS-DEMAND REPOSITORY  ·  {n} jobs  ·  {_index_path(home)}")
    print("=" * 70)
    print("\nDEMAND INVENTORY — how often each skill is asked for\n")
    print(f"  {'Skill':<18}{'Jobs':>5}   {'Category':<14}Levels")
    for skill, d in ranked:
        print(f"  {disp(skill):<18}{len(d['jobs'])}/{n:<3}  {CATEGORY.get(skill,'—'):<14}{', '.join(sorted(d['levels']))}")

    gaps, context = [], []
    for skill, d in ranked:
        if skill in backed:
            continue
        why = ("portfolio-only — mention as a project, not employer experience" if skill in portfolio
               else "on your list but not tied to an employer — confirm or pursue" if skill in confirm
               else "NOT in your profile — a genuine gap")
        (context if CATEGORY.get(skill) in LOW_PRIORITY else gaps).append((skill, d, why))

    print("\nSKILLS TO CONSIDER — in demand, but NOT employer-backed (most-wanted first)\n")
    for skill, d, why in gaps:
        print(f"  ⚠️  {disp(skill):<16}{len(d['jobs'])}/{n} jobs — {why}")
    if context:
        print("\n  (context / table-stakes, lower priority): "
              + ", ".join(f"{disp(s)} {len(d['jobs'])}/{n}" for s, d, _ in context))
    covered = [s for s, _ in ranked if s in backed]
    print(f"\n  ✅ Already employer-backed & in demand: {', '.join(disp(s) for s in covered)}")
    print("\n" + "=" * 70)
    print("Use this to decide what to add/confirm in your Profile Workbook (Skills Matrix).")


if __name__ == "__main__":
    home = sys.argv[1] if len(sys.argv) > 1 else "."
    profile_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(home, "profile")
    report(home, profile_dir)
