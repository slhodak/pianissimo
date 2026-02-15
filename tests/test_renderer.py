import os
import tempfile

from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill
from pianissimo.renderer import render_to_pdf, check_lilypond


def test_check_lilypond():
    import shutil
    if not shutil.which("lilypond"):
        import pytest
        pytest.skip("LilyPond not installed")
    assert check_lilypond() is True


def test_render_to_pdf_creates_file():
    import shutil
    if not shutil.which("lilypond"):
        import pytest
        pytest.skip("LilyPond not installed")

    spec = DrillSpec(clef="treble", key="C major", measures=2)
    score = generate_drill(spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "test_drill.pdf")
        result = render_to_pdf(score, pdf_path)
        assert os.path.exists(result)
        assert result.endswith(".pdf")


def test_render_missing_lilypond_raises(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda x: None)
    try:
        check_lilypond()
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "lilypond" in str(e).lower()
