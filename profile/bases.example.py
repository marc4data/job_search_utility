# bases.py — YOUR two base resumes. The setup-profile skill builds this from
# your real work history. Copy to bases.py and replace with your own content.
#
# WHY TWO BASES?
#   Most job searches span two flavors of the same career:
#     LEADER  — people-manager / director / head-of roles. Emphasizes team
#               leadership, strategy, stakeholders, outcomes.
#     HANDSON — individual-contributor / player-coach / senior-IC roles.
#               Emphasizes what YOU personally built, tools, and depth.
#   The process-opportunities skill picks the right base per job, then writes a
#   tailored summary + cover letter on top of it. The base stays constant; only
#   the summary, expertise line, and cover letter change per role.
#
# TRUTHFULNESS: every tool/skill named here must also appear in
# verified_skills.md. If you didn't do it, it doesn't go in the base.

# Each experience entry:
#   {"role": ..., "company_loc": "Company  •  City, ST", "dates": "Mon YYYY - Mon YYYY",
#    "desc": "one-line role summary", "bullets": ["achievement", ...]}

BASES = {
    "LEADER": {
        # 4-6 narrative one-liners — your biggest career outcomes, leadership framing.
        "career_highlights": [
            "Built the analytics function from scratch at Company A — hired the team, "
            "selected the stack, and delivered the reporting leadership relied on through 3x growth.",
            "Led a post-merger data integration at Company B — consolidated two reporting "
            "environments, cutting $1M+ in annual tooling and unifying KPIs.",
            "Turned around an underperforming BI team at Company C — rebuilt delivery and "
            "lifted dashboard adoption 400%.",
        ],
        # Role-by-role history (people-manager framing in the bullets).
        "experience": [
            {"role": "Director of Analytics", "company_loc": "Company A  •  City, ST",
             "dates": "2022 - Present", "desc": "Leads the analytics and BI organization.",
             "bullets": [
                 "Set the analytics strategy and built the KPI framework adopted company-wide.",
                 "Grew and mentored a team of analysts and engineers.",
             ]},
            {"role": "Analytics Manager", "company_loc": "Company B  •  City, ST",
             "dates": "2018 - 2022", "desc": "Managed reporting across the business.",
             "bullets": [
                 "Owned executive reporting and the data governance process.",
             ]},
        ],
        # Areas of Expertise grid: 4-5 (label, comma-separated items) rows.
        # Put real keywords here — this is heavily scanned by ATS.
        "tech_expertise": [
            ("Leadership",     "Team Leadership, Org Design, Stakeholder Management, Agile"),
            ("Analytic Tools", "Tableau, Power BI, Looker, SQL, Python"),
            ("Data/Analytics", "Business Intelligence, KPI Frameworks, Data Governance, Data Strategy, Executive Reporting"),
            ("Data Eng",       "dbt, Snowflake, ETL/ELT, SQL"),
        ],
        "projects": None,            # leader base usually omits a projects section
        "certs_before_edu": False,   # education listed before certifications
    },

    "HANDSON": {
        # Same career, but framed around what YOU personally designed/built/coded.
        "career_highlights": [
            "Personally built the data stack at Company A from an empty slate — authored "
            "the pipelines, models, and dashboards across a dozen source systems.",
            "Wrote the classification models at Company B that cut default rates 25%.",
            "Architected the consolidated data warehouse at Company C — schema, "
            "transformation layer, and the design stakeholders voted #1 in UAT.",
            "Built a portfolio analytics-engineering project end to end (see portfolio link).",
        ],
        "experience": [
            {"role": "Senior Analytics Engineer", "company_loc": "Company A  •  City, ST",
             "dates": "2022 - Present", "desc": "Hands-on builder and player-coach.",
             "bullets": [
                 "Authored the dbt model layer and the BigQuery/Snowflake dimensional schemas.",
                 "Wrote Python pipelines ingesting a dozen source systems.",
             ]},
            {"role": "Data Engineer", "company_loc": "Company B  •  City, ST",
             "dates": "2018 - 2022", "desc": "Built and ran the data platform.",
             "bullets": [
                 "Designed the ETL/ELT pipelines and data-quality tests.",
             ]},
        ],
        "tech_expertise": [
            ("Leadership",               "Player-Coach Leadership, Mentoring, Agile"),
            ("Data Engineering",         "Python, SQL, dbt, Snowflake, BigQuery, ETL/ELT, git"),
            ("Analytics & Visualization","Tableau, Power BI, Looker, Python, SQL"),
            ("Data Concepts",            "Dimensional Modeling, Data Warehouse Design, Data Quality, Data Governance"),
        ],
        # Optional "Selected Projects" section (great for IC/portfolio roles).
        "projects": [
            {"name": "Portfolio Analytics Project",
             "tech": "BigQuery  •  dbt  •  Python  •  github.com/your-handle/portfolio",
             "bullets": [
                 "Built dimensional models and a mart layer from raw data end to end.",
                 "Integrated an LLM API to generate executive summaries from live data.",
             ]},
        ],
        "certs_before_edu": True,    # technical roles: certs above education
    },
}
