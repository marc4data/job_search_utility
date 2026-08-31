"""jd_retrieval.py — helpers the process-opportunities skill uses in Step 1 to
turn a tracker's link cells into fetchable job descriptions.

These are pure, dependency-light functions (unit-tested in tests/test_round2.py).
The skill still performs the actual network / browser fetches; this module only
does the deterministic parsing and classification that tripped up clean-room
Run 1:

  • G1 — read the URL embedded as a cell's *hyperlink target*, not its display
        text; find the link column by header, not a fixed index.
  • G2 — parse a LinkedIn jobId from a posting URL and build its guest-endpoint
        URL (which returns the JD even for already-applied jobs).
  • G3 — classify each link into a retrieval *plan* so the batch can preflight
        every role up front and ask for any pastes once.
  • W1 — resolve an unfetchable role against the user's manual-JD folder
        (docs/manual_job_descriptions/) before it ever becomes a paste request.

No engine or scoring-math dependency. Import from
${CLAUDE_PLUGIN_ROOT}/templates/jd_retrieval.py during Step 1.
"""
import os
import re

# Default header for the tracker's link column; matched case-insensitively, with
# a fallback to any header containing "link" (so a rename doesn't break it).
LINK_HEADER = "Sourced From (w/link)"

# Headers the manual-JD fallback matches a row on; both are located by header
# text (with a "contains" fallback) so a tracker rename doesn't break retrieval.
COMPANY_HEADER = "Company"
ROLE_HEADER = "Role / Title"

# LinkedIn's guest posting endpoint returns the raw JD without a logged-in
# session — the reliable path for jobs you've already applied to.
LINKEDIN_GUEST = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_LINKEDIN_ID_RE = re.compile(r"(?:/jobs/view/|currentJobId=)(\d+)")


# ── G1: resolve the real link behind a cell, and find the link column ────────
def is_url(text):
    """True if text *starts* with an http(s) URL."""
    return bool(text) and bool(_URL_RE.match(str(text).strip()))


def find_url_in_text(text):
    """First http(s) URL embedded anywhere in a string, or None."""
    if not text:
        return None
    m = _URL_RE.search(str(text))
    return m.group(0).rstrip(").,;") if m else None


def resolve_cell_link(cell):
    """The effective job link for a tracker cell.

    Prefers the embedded hyperlink *target* (what display text like "Linkedin"
    hides); falls back to a URL found in the visible value. Returns None when
    there is nothing to fetch from. The target may be a URL or a local path —
    classify_link() decides what to do with it.
    """
    hyperlink = getattr(cell, "hyperlink", None)
    target = getattr(hyperlink, "target", None) if hyperlink else None
    if target:
        return target
    value = getattr(cell, "value", None)
    return find_url_in_text(value)


def find_link_column(header_values, header_name=LINK_HEADER):
    """1-based index of the link column, located by header text.

    Exact (case-insensitive) match on header_name first; otherwise the first
    header containing 'link'. Returns None if neither is found.
    """
    norm = [(str(h).strip().lower() if h is not None else "") for h in header_values]
    want = header_name.strip().lower()
    if want in norm:
        return norm.index(want) + 1
    for i, h in enumerate(norm):
        if "link" in h:
            return i + 1
    return None


def find_column_by_header(header_values, *names):
    """1-based index of the first header exactly matching (case-insensitively)
    any of `names`; otherwise the first header *containing* one of them. Returns
    None when no header looks right — callers degrade rather than guess a column.
    """
    norm = [(str(h).strip().lower() if h is not None else "") for h in header_values]
    wants = [n.strip().lower() for n in names]
    for want in wants:
        if want in norm:
            return norm.index(want) + 1
    for i, h in enumerate(norm):
        if h and any(want in h for want in wants):
            return i + 1
    return None


# ── G2: LinkedIn jobId + guest endpoint ─────────────────────────────────────
def parse_linkedin_job_id(url):
    """Numeric jobId from a /jobs/view/<id> or currentJobId=<id> URL, else None."""
    if not url:
        return None
    m = _LINKEDIN_ID_RE.search(str(url))
    return m.group(1) if m else None


def linkedin_guest_url(job_id):
    """The guest-endpoint URL for a parsed jobId."""
    return LINKEDIN_GUEST.format(job_id=job_id)


# ── G3: classify each link into a preflight plan ────────────────────────────
def classify_link(target, project_dir=None):
    """Map a resolved link target to the retrieval PLAN the skill preflights on:

      'linkedin-guest' — a LinkedIn posting with a parseable jobId; fetch the
                         guest endpoint first (browser, then paste, as fallback)
      'web-fetch'      — any other URL (incl. a LinkedIn URL with no jobId);
                         try a headless fetch, then browser, then paste
      'local-file'     — an existing local document to read
      'needs-paste'    — nothing fetchable: blank, or a missing local file

    A run never builds or scores from a guessed JD — 'needs-paste' roles are
    collected into one paste request (G3), never silently skipped. Use
    plan_for_role() instead of this function when you have the row's company and
    role: it also resolves the manual-JD folder, which turns many 'needs-paste'
    roles into 'manual-file' (W1).
    """
    if not target or not str(target).strip():
        return "needs-paste"
    target = str(target).strip()
    if is_url(target):
        if "linkedin.com" in target.lower() and parse_linkedin_job_id(target):
            return "linkedin-guest"
        return "web-fetch"
    # Non-URL target: treat as a local file path (e.g. a saved JD PDF).
    path = target
    if project_dir and not os.path.isabs(path):
        path = os.path.join(project_dir, path)
    return "local-file" if os.path.isfile(path) else "needs-paste"


# ── W1: the manual-JD fallback ──────────────────────────────────────────────
_MANUAL_JD = []          # one-slot cache: [] unloaded, [None] absent, [module]


def _manual_jd():
    """The sibling manual_jd helper, imported lazily by path.

    Loaded on demand (and cached) so the pure link-parsing functions above keep
    working even if this file is used on its own.
    """
    if not _MANUAL_JD:
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_jd.py")
        if not os.path.isfile(path):
            _MANUAL_JD.append(None)
        else:
            spec = importlib.util.spec_from_file_location("_manual_jd_helper", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _MANUAL_JD.append(mod)
    return _MANUAL_JD[0]


def plan_for_role(target, home=None, company=None, role=None, project_dir=None):
    """The retrieval plan for one role, with the manual-JD fallback applied.

    Returns `(plan, manual_match)`. `plan` is classify_link()'s result plus one
    more value:

      'manual-file' — nothing fetchable online, but a document matching this
                      row's Company + Job Title sits in the user's
                      docs/manual_job_descriptions/ folder (W1)

    `manual_match` is filled in whenever such a document matches — **even for a
    role with a perfectly good link** — so the caller can fall back to it the
    instant a live fetch fails, without stopping to ask the user for anything.
    """
    plan = classify_link(target, project_dir=project_dir)
    mj = _manual_jd() if (home and (company or role)) else None
    match = mj.find_manual_jd(home, company or "", role or "") if mj else None
    if match and plan == "needs-paste":
        plan = "manual-file"
    return plan, match


def read_job_rows(ws, home=None, header_row=3, first_data_row=4):
    """Rich preflight: one dict per tracker data row.

    Each dict is `{row, company, role, target, plan, manual}` where `manual` is
    the matched manual-JD document (or None). Pass `home` (the job-search working
    folder) to enable the manual-JD fallback; without it this is read_job_links()
    with the company/role columns attached.
    """
    headers = [c.value for c in ws[header_row]]
    link_col = find_link_column(headers)
    if link_col is None:
        raise ValueError(
            "No link column (e.g. 'Sourced From (w/link)') found in the header row."
        )
    company_col = find_column_by_header(headers, COMPANY_HEADER)
    role_col = find_column_by_header(headers, ROLE_HEADER, "title")

    def _val(r, col):
        v = ws.cell(row=r, column=col).value if col else None
        return str(v).strip() if v is not None else ""

    rows = []
    for r in range(first_data_row, ws.max_row + 1):
        company, role = _val(r, company_col), _val(r, role_col)
        target = resolve_cell_link(ws.cell(row=r, column=link_col))
        plan, match = plan_for_role(target, home=home, company=company, role=role)
        rows.append({"row": r, "company": company, "role": role,
                     "target": target, "plan": plan, "manual": match})
    return rows


def read_job_links(ws, header_row=3, first_data_row=4):
    """Walk an openpyxl worksheet and return [(row, target, plan), ...] for each
    data row, locating the link column by header. Drives the Step-1 preflight.
    """
    headers = [c.value for c in ws[header_row]]
    col = find_link_column(headers)
    if col is None:
        raise ValueError(
            "No link column (e.g. 'Sourced From (w/link)') found in the header row."
        )
    rows = []
    for r in range(first_data_row, ws.max_row + 1):
        target = resolve_cell_link(ws.cell(row=r, column=col))
        rows.append((r, target, classify_link(target)))
    return rows
