"""validate_profile.py — truthfulness validator.

Reports where a TOOL the résumé would claim (in the bases' Areas of Expertise, or
on the certifications line) is not BACKED by verified_skills.md — i.e. not tied to
any employer, not marked portfolio-only, or outright contradicted. This is the
safety net that stops "tuning drift" (e.g. a tool on your cert line that no job
actually used) from reaching a résumé.

Only TOOLS are checked. Domains (Healthcare), soft skills (Team Leadership),
methods (Dimensional Modeling) and training courses are not tools and need no
employer attribution, so they're ignored. The tool vocabulary lives in
skills_vocab.py (shared with skills_demand.py).

Usage:
    python3 validate_profile.py [<home>/profile]   # defaults to ./profile
"""
import importlib.util
import os
import re
import sys

from skills_vocab import TOOLS, DISPLAY, tools_in, canon_claim


def _resolve_profile_dir(arg=None):
    if arg:
        return arg
    d = os.path.abspath(".")
    for _ in range(6):
        if os.path.isdir(os.path.join(d, "profile")):
            return os.path.join(d, "profile")
        d = os.path.dirname(d)
    return os.path.join(os.path.abspath("."), "profile")


def load_claims(profile_dir):
    """Canonical TOOLS the résumé would claim: bases' Areas of Expertise + certs."""
    expertise, certs = set(), set()

    bases_path = os.path.join(profile_dir, "bases.py")
    if os.path.exists(bases_path):
        spec = importlib.util.spec_from_file_location("p_bases", bases_path)
        b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
        for base in b.BASES.values():
            for _label, items in base.get("tech_expertise", []):
                for tok in items.split(","):
                    t = canon_claim(tok)
                    if t:
                        expertise.add(t)

    prof_path = os.path.join(profile_dir, "profile.py")
    if os.path.exists(prof_path):
        spec = importlib.util.spec_from_file_location("p_profile", prof_path)
        p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
        for line in p.PROFILE.get("certifications", []):
            if line.lower().startswith("training"):
                continue
            for tok in re.sub(r"^Certifications:", "", line).split(","):
                t = canon_claim(tok)
                if t:
                    certs.add(t)
    return expertise, certs


def load_truth(profile_dir):
    """From verified_skills.md: tools backed per-company, portfolio-only, to-confirm, never."""
    text = open(os.path.join(profile_dir, "verified_skills.md")).read()

    def section(header):
        m = re.search(rf"##[^\n]*{re.escape(header)}[^\n]*\n(.*?)(?:\n##|\Z)", text, re.S)
        return m.group(1) if m else ""

    backed = set()
    for m in re.finditer(r"\*\*Stack ?/ ?tools:\*\*(.*)", text):
        backed |= tools_in(m.group(1))
    return backed, tools_in(section("PORTFOLIO")), tools_in(section("Confirm")), tools_in(section("NEVER used"))


def validate(profile_dir):
    expertise, certs = load_claims(profile_dir)
    backed, portfolio, confirm, never = load_truth(profile_dir)

    errors, warnings, ok = [], [], []
    for claim in sorted(expertise | certs):
        where = "certs + expertise" if claim in certs and claim in expertise else \
                ("certs" if claim in certs else "expertise")
        label = DISPLAY.get(claim, claim.title())
        if claim in never:
            errors.append(f"❌ {label} ({where}) — marked NEVER USED, but the résumé claims it.")
        elif claim in backed:
            ok.append(f"✅ {label} — backed by an employer.")
        elif claim in portfolio:
            warnings.append(f"⚠️  {label} ({where}) — portfolio-only; never let it attach to an employer.")
        elif claim in confirm:
            warnings.append(f"⚠️  {label} ({where}) — flagged to CONFIRM; not yet tied to an employer.")
        else:
            errors.append(f"❌ {label} ({where}) — NOT backed anywhere: no employer, not portfolio-only. "
                          f"Confirm where you used it, mark it portfolio-only, or drop it.")

    print(f"\nTruthfulness check — {profile_dir}\n" + "=" * 64)
    print(f"{len(ok)} tools backed · {len(warnings)} to confirm · {len(errors)} contradictions\n")
    for e in errors:   print(e)
    for w in warnings: print(w)
    if "--all" in sys.argv and ok:
        print(); [print(o) for o in ok]
    return errors, warnings


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    validate(_resolve_profile_dir(args[0] if args else None))
