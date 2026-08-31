#!/usr/bin/env python3
"""release_notes.py — pull one version's section out of CHANGELOG.md (Epic P).

The Release workflow feeds this to `gh release create --notes-file`, so a
published Release always says exactly what the CHANGELOG says — there is no
second, hand-written description to drift from it.

    python3 tools/release_notes.py 0.5.0 [CHANGELOG.md]

Exits non-zero with a clear message when the version has no entry, which fails
the release rather than publishing an empty one. (tests/test_release.py and the
existing CHANGELOG-entry test in test_round2.py keep both halves honest.)
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A section header: "## [0.5.0] — 2026-08-31". Any "## " starts the next one.
_HEADER = "## [{version}]"


def extract(changelog_text, version):
    """The body of `version`'s section, without its own header line.

    Raises KeyError when that version has no entry.
    """
    lines = changelog_text.splitlines()
    want = _HEADER.format(version=version)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(want):
            start = i
            break
    if start is None:
        raise KeyError(version)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start + 1:end]).strip() + "\n"


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    version = argv[1].lstrip("v")
    path = argv[2] if len(argv) > 2 else os.path.join(REPO_ROOT, "CHANGELOG.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        sys.stdout.write(extract(text, version))
    except KeyError:
        print(f"ERROR: {os.path.basename(path)} has no '## [{version}]' entry — "
              "add one before tagging this release.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
