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

No engine or scoring-math dependency. Import from
${CLAUDE_PLUGIN_ROOT}/templates/jd_retrieval.py during Step 1.
"""
import os
import re

# Default header for the tracker's link column; matched case-insensitively, with
# a fallback to any header containing "link" (so a rename doesn't break it).
LINK_HEADER = "Sourced From (w/link)"

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
    collected into one paste request (G3), never silently skipped.
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
