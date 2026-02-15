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
    # Strip .pdf — music21 appends it automatically
    base = output_path
    while base.lower().endswith(".pdf"):
        base = base[:-4]
    lp = score.write("lilypond.pdf", fp=base)
    # Clean up intermediate LilyPond source file
    ly_file = base + ".ly"
    if os.path.exists(ly_file):
        os.remove(ly_file)
    # Also clean up the extensionless intermediate file if it exists
    if os.path.exists(base) and os.path.isfile(base):
        os.remove(base)
    return str(lp)
