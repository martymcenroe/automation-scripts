"""Smoke tests: verify runtime dependencies can be imported / used.

This is the minimum viable test gate for tools/dependabot_review.py's
test-must-pass requirement. If a dependency upgrade breaks the import
graph -- ABI break, transitive-dep incompatibility, removed API --
these tests fail and the PR doesn't merge.

Not a substitute for behavioral tests of the scripts themselves; those
are out of scope (see issue #43 for the rationale).

Pillow is the actual security-vuln target for most current dependabot
PRs against this repo. It's pulled in transitively via weasyprint.
We test Pillow directly (works on any machine) because the weasyprint
import path requires GTK native libs which aren't always available --
those imports skip gracefully on machines without GTK rather than
failing the gate for an environment reason unrelated to dependency
upgrades.
"""

import pytest


def test_trafilatura_imports():
    import trafilatura  # noqa: F401


def test_tzdata_imports():
    import tzdata  # noqa: F401


def test_pillow_basic():
    """Pillow drives weasyprint's image handling; test it directly.

    Image.new + size check exercises the C extension's basic memory /
    pixel-buffer paths. Any ABI break from a major bump (e.g. removed
    deprecated constants, changed default modes) surfaces here.
    """
    from PIL import Image
    img = Image.new("RGB", (10, 10), "red")
    assert img.size == (10, 10)
    assert img.mode == "RGB"


def test_weasyprint_imports():
    """Skip if GTK native libs (libgobject/libpango) aren't installed.

    weasyprint requires GTK on Windows. On machines where GTK isn't
    present, this test skips rather than fails -- the dependabot gate
    should reflect "did the dep upgrade break Python imports", not
    "is the user's machine fully set up for weasyprint runtime".
    """
    try:
        import weasyprint  # noqa: F401
    except OSError as e:
        msg = str(e).lower()
        if "libgobject" in msg or "libgtk" in msg or "libpango" in msg:
            pytest.skip(f"GTK runtime not installed; weasyprint cannot import: {e}")
        raise
