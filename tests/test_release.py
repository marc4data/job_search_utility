"""Regression tests for the Release workflow (Epic P).

The deferred promise in the v0.4.0 CHANGELOG was that tagging waits for a real
release path. These lock that path's contract: release notes always come from
the CHANGELOG (never hand-written), and the workflow refuses to publish a tag
that disagrees with the version the plugin announces at runtime (K1).
"""
import json
import os

import pytest

from conftest import _load_module

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO_ROOT, ".github", "workflows", "release.yml")
CHANGELOG = os.path.join(REPO_ROOT, "CHANGELOG.md")
PLUGIN_JSON = os.path.join(REPO_ROOT, ".claude-plugin", "plugin.json")


def _notes():
    return _load_module("release_notes_under_test",
                        os.path.join(REPO_ROOT, "tools", "release_notes.py"))


SAMPLE = """\
# Changelog

Preamble that must never leak into a release.

## [0.5.0] — 2026-08-31

Body for 0.5.0.

### Added
- A thing.

## [0.4.0] — 2026-06-19

Body for 0.4.0.
"""


def test_extract_returns_only_that_versions_section():
    n = _notes()
    got = n.extract(SAMPLE, "0.5.0")
    assert "Body for 0.5.0." in got and "### Added" in got
    # Neither the preamble above nor the next version below bleeds in.
    assert "Preamble" not in got
    assert "0.4.0" not in got and "Body for 0.4.0." not in got
    # The section's own header is not repeated in the notes.
    assert not got.startswith("## [")


def test_extract_handles_the_last_section():
    n = _notes()
    assert "Body for 0.4.0." in n.extract(SAMPLE, "0.4.0")


def test_extract_raises_for_a_version_with_no_entry():
    n = _notes()
    with pytest.raises(KeyError):
        n.extract(SAMPLE, "9.9.9")


def test_cli_fails_loudly_on_a_missing_entry(tmp_path, capsys):
    n = _notes()
    path = tmp_path / "CHANGELOG.md"
    path.write_text(SAMPLE)
    assert n.main(["release_notes.py", "9.9.9", str(path)]) == 1
    assert "no '## [9.9.9]' entry" in capsys.readouterr().err
    # A leading "v" is accepted, so the tag name can be passed through directly.
    assert n.main(["release_notes.py", "v0.5.0", str(path)]) == 0


def test_current_version_has_extractable_release_notes():
    """The shipped version must always be releasable — no empty Release."""
    n = _notes()
    version = json.load(open(PLUGIN_JSON))["version"]
    body = n.extract(open(CHANGELOG).read(), version)
    assert len(body.strip()) > 100, f"CHANGELOG entry for {version} is too thin to release"


# ── the workflow's contract ─────────────────────────────────────────────────
def test_release_workflow_is_tag_triggered_and_can_publish():
    text = open(WORKFLOW).read()
    assert 'tags: ["v[0-9]+.[0-9]+.[0-9]+"]' in text   # tags only, not every push
    assert "pull_request" not in text                   # never fires on a PR
    assert "contents: write" in text                    # can create the Release
    assert "./build.sh" in text                         # same integrity guards as CI


def test_release_workflow_refuses_a_tag_version_mismatch():
    text = open(WORKFLOW).read()
    assert 'TAG_VERSION="${GITHUB_REF_NAME#v}"' in text
    assert 'if [ "$TAG_VERSION" != "$PLUGIN_VERSION" ]; then' in text
    assert "exit 1" in text


def test_release_notes_come_from_the_changelog_not_hand_written():
    text = open(WORKFLOW).read()
    assert "tools/release_notes.py" in text
    assert "--notes-file RELEASE_NOTES.md" in text
    # A hand-written blurb would let the Release drift from the CHANGELOG.
    assert "--notes " not in text


def test_release_asset_is_the_built_plugin():
    text = open(WORKFLOW).read()
    assert "job-search-tailor.plugin" in text
