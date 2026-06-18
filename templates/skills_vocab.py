"""skills_vocab.py — the shared tool vocabulary + matching.

Used by validate_profile.py (truthfulness check) and skills_demand.py (demand
index) so "demand" and "claims" speak one vocabulary. Matching is alias-aware and
word-boundary-based, so "PowerBI"=="Power BI" and the 1-letter tool "R" never
matches inside a word like "Marc".

Only technologies live here. Domains, soft skills, methods and training are NOT
tools and are deliberately absent, so they're never flagged or counted as skills.
"""
import re

# canonical tool  ->  surface variants that mean the same thing
TOOLS = {
    "snowflake": [], "dbt": [], "fivetran": [], "bigquery": ["big query", "gcp/bigquery"],
    "gcp": ["google cloud", "google cloud platform"], "aws": [], "azure": [],
    "databricks": [], "tableau": [], "tableau server": ["tableau online"],
    "power bi": ["powerbi", "power-bi"], "looker": [], "hex": [],
    "apache superset": ["superset"], "ssrs": [], "ssis": [], "talend": [],
    "alteryx": ["alteryx server"], "python": [], "sql": [], "r": [],
    "duckdb": [], "oracle": [], "crystal reports": [], "mssql": ["ms sql", "sql server"],
    "claude": ["claude api", "claude code", "llm", "ai/llm", "ai/llm integration",
               "llm integration", "ml integration", "generative ai", "gen ai"],
    # commonly-demanded tools (so the demand index can flag ones a profile lacks)
    "airflow": ["apache airflow"], "spark": ["apache spark", "pyspark"], "kafka": ["apache kafka"],
    "dagster": [], "prefect": [], "redshift": ["amazon redshift"], "postgres": ["postgresql"],
    "terraform": [], "docker": [], "kubernetes": ["k8s"], "scala": [], "git": [],
    "mode": ["mode analytics"], "sigma": ["sigma computing"], "great expectations": [],
    "omni": [], "spotfire": [], "salesforce": [], "veeva": ["veeva crm", "veeva vault"],
    "iqvia": [], "circleci": [], "github actions": ["gh actions"], "copilot": ["github copilot"],
}

# Pretty display names (acronyms/brands that .title() would mangle).
DISPLAY = {
    "bigquery": "BigQuery", "dbt": "dbt", "gcp": "GCP", "aws": "AWS", "azure": "Azure",
    "power bi": "Power BI", "ssrs": "SSRS", "ssis": "SSIS", "sql": "SQL", "r": "R",
    "mssql": "MS SQL Server", "duckdb": "DuckDB", "apache superset": "Apache Superset",
    "claude": "Claude/LLM", "tableau server": "Tableau Server", "omni": "Omni",
    "github actions": "GitHub Actions", "circleci": "CircleCI", "iqvia": "IQVIA",
}

# Category, for grouping/down-ranking table-stakes tooling in the demand report.
CATEGORY = {
    "snowflake": "warehouse", "bigquery": "warehouse", "redshift": "warehouse",
    "databricks": "warehouse", "duckdb": "warehouse", "postgres": "warehouse",
    "oracle": "warehouse", "mssql": "warehouse",
    "dbt": "transform", "fivetran": "transform", "talend": "transform",
    "ssis": "transform", "great expectations": "transform",
    "airflow": "orchestration", "dagster": "orchestration", "prefect": "orchestration",
    "tableau": "bi", "tableau server": "bi", "power bi": "bi", "looker": "bi",
    "hex": "bi", "apache superset": "bi", "ssrs": "bi", "mode": "bi", "sigma": "bi",
    "omni": "bi", "spotfire": "bi",
    "python": "language", "r": "language", "sql": "language", "scala": "language",
    "gcp": "cloud", "aws": "cloud", "azure": "cloud", "terraform": "cloud",
    "docker": "cloud", "kubernetes": "cloud",
    "git": "ci-cd", "github actions": "ci-cd", "circleci": "ci-cd", "copilot": "ci-cd",
    "alteryx": "etl-viz", "claude": "ai", "kafka": "streaming", "spark": "processing",
    "salesforce": "source-system", "veeva": "source-system", "iqvia": "source-system",
}


def _pat(form):
    """Word-boundary regex for a tool surface form; the 1-letter 'r' is special."""
    return r"(?<![a-z])r(?![a-z])" if form == "r" else r"\b" + re.escape(form) + r"\b"


def _present(tool, text):
    text = f" {text.lower()} "
    return any(re.search(_pat(f.strip()), text) for f in [tool] + TOOLS[tool])


def tools_in(text):
    """The set of canonical tools mentioned anywhere in a block of text."""
    return {t for t in TOOLS if _present(t, text)}


def canon_claim(token):
    """Map a single token to a canonical tool, or None if it isn't a tool."""
    tl = f" {token.lower()} "
    for t in TOOLS:
        if any(re.search(_pat(f.strip()), tl) for f in [t] + TOOLS[t]):
            return t
    return None
