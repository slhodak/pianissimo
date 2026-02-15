import os
import shutil
import tempfile

import pytest

from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill
from pianissimo.renderer import render_to_pdf


@pytest.mark.skipif(not shutil.which("lilypond"), reason="LilyPond not installed")
def test_full_pipeline_spec_to_pdf():
    """End-to-end: DrillSpec -> generate -> render -> PDF exists."""
    spec = DrillSpec(
        clef="treble",
        key="G major",
        note_range=("G4", "D5"),
        rhythms=["quarter", "half"],
        time_signature="4/4",
        measures=4,
    )
    score = generate_drill(spec)

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "integration_test.pdf")
        result = render_to_pdf(score, pdf_path)
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0
