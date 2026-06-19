"""skills_taxonomy.py — the ONE editable reference for demand extraction (R2/R4).

Tune this file (no code changes elsewhere) to control what the skills-demand index
captures, how it's categorized, what's folded together, and what's ignored.

Four fixed categories:
  tool                  — named software/platform (vocabulary in skills_vocab.py)
  technical_competency  — methods, not products (modeling, ETL, ML, governance…)
  leadership            — team leadership, strategy, stakeholder/exec communication
  domain                — sector knowledge (healthcare, fintech, retail…)

Extraction is alias/word-boundary aware (reuses skills_vocab matching) and one-way:
demand data only — it never writes the Skills Matrix, bases.py, or verified_skills.md.
"""
import re

from skills_vocab import TOOLS, DISPLAY, _pat, tools_in

CATEGORIES = ["tool", "technical_competency", "leadership", "domain"]

# R4 — pipeline-internal / non-skill tokens that must never count as demand.
STOPLIST = {"claude"}

# R4 — fold a canonical tool onto another canonical tool so counts aren't
# fragmented (editable). Keys/values are skills_vocab canonical labels.
TOOL_FOLD = {"mssql": "sql"}

# Non-tool taxonomy: canonical label -> surface phrases (synonyms) to match.
NONTOOL = {
    "technical_competency": {
        "data modeling": ["data modeling", "data modelling", "dimensional modeling", "schema design"],
        "etl/elt": ["etl", "elt", "etl/elt", "data pipelines", "pipeline development"],
        "experimentation": ["a/b testing", "ab testing", "experimentation", "causal inference"],
        "statistics": ["statistical analysis", "statistics", "statistical modeling"],
        "machine learning": ["machine learning", "predictive modeling", "predictive analytics"],
        "forecasting": ["forecasting", "demand forecasting", "time series"],
        "data governance": ["data governance", "governance", "data stewardship"],
        "data quality": ["data quality", "data-quality", "data validation"],
        "generative ai": ["generative ai", "gen ai", "genai", "llm", "llms", "rag"],
    },
    "leadership": {
        "team leadership": ["team leadership", "leading teams", "people management",
                            "managing teams", "lead a team", "manage a team"],
        "hiring & mentoring": ["hiring", "mentoring", "coaching", "talent development",
                               "developing teams", "build the team"],
        "data strategy": ["data strategy", "analytics strategy", "data roadmap", "strategic roadmap"],
        "stakeholder management": ["stakeholder", "cross-functional", "business partner"],
        "executive communication": ["executive communication", "storytelling", "board-level",
                                    "present to executives", "executive presence", "exec audience"],
    },
    "domain": {
        "healthcare": ["healthcare", "health care", "clinical", "hipaa", "patient"],
        "pharma/life sciences": ["pharmaceutical", "life sciences", "pharma", "hcp",
                                 "claims data", "specialty pharmacy", "21 cfr"],
        "fintech": ["fintech", "financial services", "banking", "credit", "lending", "payments"],
        "ecommerce/retail": ["e-commerce", "ecommerce", "retail", "dtc", "consumer goods"],
        "insurance": ["insurance", "actuarial", "underwriting"],
        "ad-tech": ["ad-tech", "adtech", "advertising", "martech"],
        "edtech": ["edtech", "ed-tech", "higher education", "online university"],
    },
}


def _phrase_present(phrase, text):
    return bool(re.search(_pat(phrase) if " " not in phrase else r"\b" + re.escape(phrase) + r"\b", text))


def extract(text):
    """Return a deduped list of (category, canonical_label, raw_span) for one JD."""
    low = f" {text.lower()} "
    found = {}   # (category, canonical) -> raw span

    # tools (reuse skills_vocab), minus the stop-list, with folding
    for t in tools_in(text):
        if t in STOPLIST:
            continue
        canon = TOOL_FOLD.get(t, t)
        found[("tool", canon)] = DISPLAY.get(canon, canon)

    # non-tool categories
    for category, mapping in NONTOOL.items():
        for canonical, phrases in mapping.items():
            for ph in phrases:
                if _phrase_present(ph, low):
                    found[(category, canonical)] = ph
                    break

    return [(cat, canon, raw) for (cat, canon), raw in found.items()]


def display(category, label):
    if category == "tool":
        return DISPLAY.get(label, label.title())
    return label.replace("/", " / ").title() if label.islower() else label
