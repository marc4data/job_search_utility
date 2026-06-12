# profile.py — YOUR personal header data (NOT skills; those go in bases.py).
# The setup-profile skill generates this for you from a short interview.
# Copy this file to profile.py and replace every value with your own.
#
# This file contains ONLY contact/identity/education info that is identical
# on every resume you send. Nothing here is tailored per job.

PROFILE = {
    # Appears as the large name header on the resume and the cover-letter signature.
    "name": "Jordan Rivera, MBA",

    # The contact line under your name on the resume. Plain text; use "  •  "
    # between items. Do NOT put clickable links here — those go in "links".
    "contact": "Austin, TX  •  (555) 010-2020  •  jordan@example.com",

    # The plain contact line under your cover-letter signature.
    "cl_contact": "Austin, TX  |  (555) 010-2020  |  jordan@example.com",

    # Clickable links rendered after the contact line on the resume.
    # List of (label, url) pairs. Keep to 1-3.
    "links": [
        ("LinkedIn", "https://www.linkedin.com/in/your-handle/"),
        ("Portfolio", "https://your-portfolio-site.example.com"),
    ],

    # Education — one string per line, most recent first.
    "education": [
        "Master of Business Administration (MBA)  •  Your University  •  City, ST",
        "Bachelor of Science in Your Field  •  Your University  •  City, ST",
    ],

    # Certifications & training — usually 1-2 lines. Start lines with a label.
    # ONLY list certs you actually hold (this is part of staying truthful).
    "certifications": [
        "Certifications: PMP, Google Analytics, Tableau Desktop Specialist",
        "Training: Relevant courses, bootcamps, or programs",
    ],

    # Older roles shown compactly under "Additional Experience" (no bullets).
    # Leave as [] to omit the section entirely.
    "additional_experience": [
        "Earlier Role Title  •  Earlier Company, City, ST",
    ],
}
