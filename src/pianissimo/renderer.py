import os
import shutil

from music21 import stream


def check_lilypond() -> bool:
    if not shutil.which("lilypond"):
        raise RuntimeError(
            "LilyPond is not installed. Install it:\n"
            "  macOS: brew install lilypond\n"
            "  Ubuntu: sudo apt install lilypond\n"
            "  Windows: https://lilypond.org/download.html"
        )
    return True


def render_to_pdf(score: stream.Score, output_path: str) -> str:
    check_lilypond()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    lp = score.write("lilypond.pdf", fp=output_path)
    return str(lp)
