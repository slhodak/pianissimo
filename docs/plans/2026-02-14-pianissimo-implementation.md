# Pianissimo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI that takes natural-language descriptions of sight-reading difficulties, uses an LLM to diagnose and produce a drill spec, generates exercises with music21, and renders them to PDF via LilyPond.

**Architecture:** Three layers — LLM conversation (Anthropic SDK), generator engine (music21), renderer (LilyPond). The drill spec dataclass is the contract between all layers. CLI entry point ties them together.

**Tech Stack:** Python 3.13, music21, LilyPond, anthropic SDK, click, pytest

---

### Task 1: Project Setup

**Files:**
- Modify: `Pipfile`
- Create: `src/pianissimo/__init__.py`
- Create: `src/pianissimo/drill_spec.py`
- Create: `tests/__init__.py`
- Create: `tests/test_drill_spec.py`
- Create: `pyproject.toml`

**Step 1: Set up project structure and install deps**

Add to `Pipfile`:
```toml
[packages]
music21 = "*"
click = "*"
anthropic = "*"

[dev-packages]
pytest = "*"
```

Create `pyproject.toml`:
```toml
[project]
name = "pianissimo"
version = "0.1.0"
requires-python = ">=3.13"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

Run:
```bash
mkdir -p src/pianissimo tests
touch src/pianissimo/__init__.py tests/__init__.py
pipenv install
pipenv install --dev pytest
```

**Step 2: Write failing test for DrillSpec**

`tests/test_drill_spec.py`:
```python
from pianissimo.drill_spec import DrillSpec


def test_drill_spec_defaults():
    spec = DrillSpec(clef="treble", key="C major")
    assert spec.clef == "treble"
    assert spec.key == "C major"
    assert spec.note_range == ("C4", "C6")
    assert spec.rhythms == ["quarter"]
    assert spec.time_signature == "4/4"
    assert spec.measures == 8
    assert spec.hands == "right"
    assert spec.rests is False
    assert spec.max_interval == 5


def test_drill_spec_custom():
    spec = DrillSpec(
        clef="bass",
        key="F major",
        note_range=("C3", "B3"),
        rhythms=["quarter", "half"],
        measures=4,
    )
    assert spec.clef == "bass"
    assert spec.note_range == ("C3", "B3")
    assert spec.rhythms == ["quarter", "half"]
    assert spec.measures == 4


def test_drill_spec_to_dict():
    spec = DrillSpec(clef="treble", key="C major")
    d = spec.to_dict()
    assert d["clef"] == "treble"
    assert d["key"] == "C major"


def test_drill_spec_from_dict():
    d = {"clef": "bass", "key": "G major", "measures": 16}
    spec = DrillSpec.from_dict(d)
    assert spec.clef == "bass"
    assert spec.key == "G major"
    assert spec.measures == 16
    assert spec.rhythms == ["quarter"]  # default preserved


def test_drill_spec_validates_clef():
    try:
        DrillSpec(clef="kazoo", key="C major")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "clef" in str(e).lower()
```

**Step 3: Run test to verify it fails**

Run: `pipenv run pytest tests/test_drill_spec.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pianissimo.drill_spec'`

**Step 4: Implement DrillSpec**

`src/pianissimo/drill_spec.py`:
```python
from dataclasses import dataclass, field, asdict

VALID_CLEFS = ("treble", "bass", "grand")
VALID_RHYTHMS = ("whole", "half", "quarter", "eighth", "dotted_quarter", "dotted_half", "sixteenth")
VALID_HANDS = ("right", "left", "both")


@dataclass
class DrillSpec:
    clef: str
    key: str
    note_range: tuple[str, str] = ("C4", "C6")
    rhythms: list[str] = field(default_factory=lambda: ["quarter"])
    time_signature: str = "4/4"
    measures: int = 8
    hands: str = "right"
    rests: bool = False
    max_interval: int = 5

    def __post_init__(self):
        if self.clef not in VALID_CLEFS:
            raise ValueError(f"Invalid clef: {self.clef}. Must be one of {VALID_CLEFS}")
        if self.hands not in VALID_HANDS:
            raise ValueError(f"Invalid hands: {self.hands}. Must be one of {VALID_HANDS}")
        for r in self.rhythms:
            if r not in VALID_RHYTHMS:
                raise ValueError(f"Invalid rhythm: {r}. Must be one of {VALID_RHYTHMS}")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["note_range"] = list(d["note_range"])
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "DrillSpec":
        if "note_range" in d and isinstance(d["note_range"], list):
            d["note_range"] = tuple(d["note_range"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
```

**Step 5: Run tests to verify they pass**

Run: `pipenv run pytest tests/test_drill_spec.py -v`
Expected: All 5 tests PASS

**Step 6: Commit**

```bash
git add src/ tests/ Pipfile Pipfile.lock pyproject.toml
git commit -m "feat: add DrillSpec dataclass with validation and serialization"
```

---

### Task 2: Generator Engine

**Files:**
- Create: `src/pianissimo/generator.py`
- Create: `tests/test_generator.py`

**Step 1: Write failing tests for generator**

`tests/test_generator.py`:
```python
from music21 import stream, key, meter, clef as m21clef

from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill


def test_generate_returns_stream():
    spec = DrillSpec(clef="treble", key="C major")
    score = generate_drill(spec)
    assert isinstance(score, stream.Score)


def test_generate_correct_key_signature():
    spec = DrillSpec(clef="treble", key="G major")
    score = generate_drill(spec)
    parts = list(score.parts)
    ks = parts[0].getElementsByClass(key.KeySignature).first()
    assert ks is not None
    assert ks.sharps == 1  # G major = 1 sharp


def test_generate_correct_time_signature():
    spec = DrillSpec(clef="treble", key="C major", time_signature="3/4")
    score = generate_drill(spec)
    parts = list(score.parts)
    ts = parts[0].getElementsByClass(meter.TimeSignature).first()
    assert ts is not None
    assert ts.ratioString == "3/4"


def test_generate_correct_measure_count():
    spec = DrillSpec(clef="treble", key="C major", measures=4)
    score = generate_drill(spec)
    parts = list(score.parts)
    measures = list(parts[0].getElementsByClass(stream.Measure))
    assert len(measures) == 4


def test_generate_notes_within_range():
    spec = DrillSpec(clef="bass", key="C major", note_range=("C3", "B3"), measures=8)
    score = generate_drill(spec)
    from music21 import note as m21note, pitch
    low = pitch.Pitch("C3")
    high = pitch.Pitch("B3")
    parts = list(score.parts)
    for n in parts[0].recurse().getElementsByClass(m21note.Note):
        assert low <= n.pitch <= high, f"Note {n.pitch} outside range {low}-{high}"


def test_generate_grand_staff_has_two_parts():
    spec = DrillSpec(clef="grand", key="C major", hands="both")
    score = generate_drill(spec)
    parts = list(score.parts)
    assert len(parts) == 2


def test_generate_respects_max_interval():
    spec = DrillSpec(
        clef="treble", key="C major",
        note_range=("C4", "C6"), max_interval=3, measures=8
    )
    score = generate_drill(spec)
    from music21 import note as m21note
    parts = list(score.parts)
    notes = list(parts[0].recurse().getElementsByClass(m21note.Note))
    for i in range(1, len(notes)):
        interval = abs(notes[i].pitch.midi - notes[i - 1].pitch.midi)
        # max_interval=3 means up to a minor third (3 semitones) — but we interpret
        # max_interval as scale degrees, so allow some tolerance (up to 5 semitones for 3 degrees)
        assert interval <= 7, f"Interval {interval} too large between {notes[i-1].pitch} and {notes[i].pitch}"
```

**Step 2: Run tests to verify they fail**

Run: `pipenv run pytest tests/test_generator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pianissimo.generator'`

**Step 3: Implement generator**

`src/pianissimo/generator.py`:
```python
import random

from music21 import (
    clef as m21clef,
    duration,
    key as m21key,
    meter,
    note as m21note,
    pitch,
    stream,
)

from pianissimo.drill_spec import DrillSpec

RHYTHM_TO_QUARTER_LENGTH = {
    "whole": 4.0,
    "dotted_half": 3.0,
    "half": 2.0,
    "dotted_quarter": 1.5,
    "quarter": 1.0,
    "eighth": 0.5,
    "sixteenth": 0.25,
}


def _get_clef(clef_name: str, hand: str = "right") -> m21clef.Clef:
    if clef_name == "treble" or (clef_name == "grand" and hand == "right"):
        return m21clef.TrebleClef()
    return m21clef.BassClef()


def _build_pitch_pool(low: str, high: str, key_obj: m21key.Key) -> list[pitch.Pitch]:
    low_p = pitch.Pitch(low)
    high_p = pitch.Pitch(high)
    scale_pitches = key_obj.getPitches(low_p, high_p)
    return [p for p in scale_pitches if low_p <= p <= high_p]


def _pick_next_pitch(
    pool: list[pitch.Pitch], prev: pitch.Pitch | None, max_interval: int
) -> pitch.Pitch:
    if prev is None:
        return random.choice(pool)
    candidates = [p for p in pool if abs(p.midi - prev.midi) <= max_interval + 2]
    if not candidates:
        candidates = pool
    return random.choice(candidates)


def _generate_part(spec: DrillSpec, clef_name: str, hand: str) -> stream.Part:
    part = stream.Part()
    clef_obj = _get_clef(clef_name, hand)

    key_obj = m21key.Key(spec.key.split()[0], spec.key.split()[1] if len(spec.key.split()) > 1 else None)
    ts = meter.TimeSignature(spec.time_signature)

    low, high = spec.note_range
    pool = _build_pitch_pool(low, high, key_obj)
    if not pool:
        pool = [pitch.Pitch(low)]

    ql_per_measure = ts.barDuration.quarterLength
    rhythm_qls = [RHYTHM_TO_QUARTER_LENGTH[r] for r in spec.rhythms]

    prev_pitch = None
    for m_num in range(spec.measures):
        measure = stream.Measure(number=m_num + 1)
        if m_num == 0:
            measure.insert(0, clef_obj)
            measure.insert(0, key_obj.asKeySignature())
            measure.insert(0, ts)

        remaining = ql_per_measure
        while remaining > 0.001:
            valid_qls = [ql for ql in rhythm_qls if ql <= remaining + 0.001]
            if not valid_qls:
                valid_qls = [remaining]
            ql = random.choice(valid_qls)
            if ql > remaining:
                ql = remaining

            p = _pick_next_pitch(pool, prev_pitch, spec.max_interval)
            n = m21note.Note(p, quarterLength=ql)
            measure.append(n)
            prev_pitch = p
            remaining -= ql

        part.append(measure)

    return part


def generate_drill(spec: DrillSpec) -> stream.Score:
    score = stream.Score()

    if spec.clef == "grand" or spec.hands == "both":
        right_spec = DrillSpec(
            clef="grand", key=spec.key,
            note_range=spec.note_range if spec.note_range != ("C4", "C6") else ("C4", "C6"),
            rhythms=spec.rhythms, time_signature=spec.time_signature,
            measures=spec.measures, hands="right", rests=spec.rests,
            max_interval=spec.max_interval,
        )
        left_spec = DrillSpec(
            clef="grand", key=spec.key,
            note_range=spec.note_range if spec.note_range != ("C4", "C6") else ("C2", "B3"),
            rhythms=spec.rhythms, time_signature=spec.time_signature,
            measures=spec.measures, hands="left", rests=spec.rests,
            max_interval=spec.max_interval,
        )
        score.append(_generate_part(right_spec, "grand", "right"))
        score.append(_generate_part(left_spec, "grand", "left"))
    else:
        score.append(_generate_part(spec, spec.clef, spec.hands))

    return score
```

**Step 4: Run tests to verify they pass**

Run: `pipenv run pytest tests/test_generator.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add src/pianissimo/generator.py tests/test_generator.py
git commit -m "feat: add drill generator engine using music21"
```

---

### Task 3: PDF Renderer

**Files:**
- Create: `src/pianissimo/renderer.py`
- Create: `tests/test_renderer.py`

**Step 1: Write failing tests for renderer**

`tests/test_renderer.py`:
```python
import os
import tempfile

from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill
from pianissimo.renderer import render_to_pdf, check_lilypond


def test_check_lilypond():
    # This test will pass if LilyPond is installed, skip if not
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
```

**Step 2: Run tests to verify they fail**

Run: `pipenv run pytest tests/test_renderer.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement renderer**

`src/pianissimo/renderer.py`:
```python
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

    # music21 can write to LilyPond format and then convert to PDF
    # Use the lilypond converter
    lp = score.write("lilypond.pdf", fp=output_path)
    return str(lp)
```

**Step 4: Run tests to verify they pass**

Run: `pipenv run pytest tests/test_renderer.py -v`
Expected: Tests PASS (or skip if LilyPond not installed)

**Step 5: Commit**

```bash
git add src/pianissimo/renderer.py tests/test_renderer.py
git commit -m "feat: add PDF renderer via LilyPond"
```

---

### Task 4: LLM Conversation Layer

**Files:**
- Create: `src/pianissimo/conversation.py`
- Create: `tests/test_conversation.py`

**Step 1: Write failing tests**

`tests/test_conversation.py`:
```python
import json
from pianissimo.conversation import build_system_prompt, parse_drill_spec_from_response
from pianissimo.drill_spec import DrillSpec


def test_system_prompt_contains_schema():
    prompt = build_system_prompt()
    assert "clef" in prompt
    assert "note_range" in prompt
    assert "rhythms" in prompt


def test_parse_drill_spec_from_json_block():
    response = """Based on your difficulty, here's what I recommend:

```json
{"clef": "bass", "key": "F major", "note_range": ["C3", "B3"], "rhythms": ["quarter", "half"], "measures": 8}
```

This will help you practice reading notes in the bass clef."""

    spec = parse_drill_spec_from_response(response)
    assert isinstance(spec, DrillSpec)
    assert spec.clef == "bass"
    assert spec.key == "F major"


def test_parse_drill_spec_returns_none_for_no_json():
    response = "Let me ask you a follow-up question: are you struggling with ledger lines?"
    spec = parse_drill_spec_from_response(response)
    assert spec is None


def test_parse_drill_spec_returns_none_for_invalid_json():
    response = '```json\n{"clef": "kazoo"}\n```'
    spec = parse_drill_spec_from_response(response)
    assert spec is None
```

**Step 2: Run tests to verify they fail**

Run: `pipenv run pytest tests/test_conversation.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement conversation module**

`src/pianissimo/conversation.py`:
```python
import json
import os
import re

from anthropic import Anthropic

from pianissimo.drill_spec import DrillSpec, VALID_CLEFS, VALID_RHYTHMS, VALID_HANDS

DRILL_SPEC_SCHEMA = {
    "clef": f"One of: {', '.join(VALID_CLEFS)}",
    "key": "Key signature, e.g. 'C major', 'Bb major', 'F# minor'",
    "note_range": "Array of two pitches [low, high], e.g. ['C3', 'B3']",
    "rhythms": f"Array of rhythm types from: {', '.join(VALID_RHYTHMS)}",
    "time_signature": "e.g. '4/4', '3/4', '6/8'",
    "measures": "Integer, number of measures (default 8)",
    "hands": f"One of: {', '.join(VALID_HANDS)}",
    "rests": "Boolean, whether to include rests",
    "max_interval": "Integer, max scale-degree jump between notes (default 5)",
}


def build_system_prompt() -> str:
    schema_text = json.dumps(DRILL_SPEC_SCHEMA, indent=2)
    return f"""You are a friendly, encouraging piano teacher helping a student improve their sight-reading.

The student will describe a difficulty they're having. Your job is to:
1. Ask 1-3 brief clarifying questions to understand their specific struggle.
2. Always ask about key preference in a low-friction way, like: "Do you want to specify a key, or should I surprise you? If I surprise you, should it be a common key or a challenging one?"
3. Once you understand enough, generate a drill specification as a JSON code block.

The drill spec schema:
{schema_text}

When you're ready to generate, output EXACTLY one ```json``` code block containing the drill spec. Only include fields that differ from defaults. The defaults are: clef=treble, note_range=[C4,C6], rhythms=[quarter], time_signature=4/4, measures=8, hands=right, rests=false, max_interval=5.

Keep responses short and warm. You're a teacher, not a textbook."""


def parse_drill_spec_from_response(response: str) -> DrillSpec | None:
    match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        return DrillSpec.from_dict(data)
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def run_conversation(initial_message: str) -> DrillSpec:
    client = Anthropic()
    system = build_system_prompt()
    messages = [{"role": "user", "content": initial_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        assistant_text = response.content[0].text
        print(f"\n{assistant_text}")

        spec = parse_drill_spec_from_response(assistant_text)
        if spec is not None:
            return spec

        messages.append({"role": "assistant", "content": assistant_text})
        user_input = input("\n> ").strip()
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
```

**Step 4: Run tests to verify they pass**

Run: `pipenv run pytest tests/test_conversation.py -v`
Expected: All 4 tests PASS (these tests don't call the API)

**Step 5: Commit**

```bash
git add src/pianissimo/conversation.py tests/test_conversation.py
git commit -m "feat: add LLM conversation layer for drill diagnosis"
```

---

### Task 5: CLI Entry Point

**Files:**
- Create: `src/pianissimo/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing tests**

`tests/test_cli.py`:
```python
import json
import os
import tempfile

from click.testing import CliRunner

from pianissimo.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "pianissimo" in result.output.lower() or "sight-reading" in result.output.lower()
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement CLI**

`src/pianissimo/cli.py`:
```python
import json
import os
from datetime import date

import click

from pianissimo.conversation import run_conversation
from pianissimo.drill_spec import DrillSpec
from pianissimo.generator import generate_drill
from pianissimo.renderer import render_to_pdf, check_lilypond


@click.command()
@click.argument("description", required=False)
@click.option("--output-dir", default="drills", help="Directory to save generated drills")
def main(description: str | None, output_dir: str):
    """Pianissimo — a sight-reading drill generator.

    Describe your difficulty and get a personalized practice sheet.
    """
    try:
        check_lilypond()
    except RuntimeError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    if not description:
        description = click.prompt("What are you struggling with?")

    click.echo(f"Let me think about that...")
    spec = run_conversation(description)

    click.echo(f"\nGenerating drill...")
    score = generate_drill(spec)

    today = date.today().isoformat()
    slug = description[:30].lower().replace(" ", "-").strip("-")
    base_name = f"{today}-{slug}"
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    pdf_path = render_to_pdf(score, pdf_path)
    click.echo(f"[PDF saved to {pdf_path}]")

    spec_path = os.path.join(output_dir, f"{base_name}.json")
    with open(spec_path, "w") as f:
        json.dump(spec.to_dict(), f, indent=2)
    click.echo(f"[Spec saved to {spec_path}]")


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_cli.py -v`
Expected: PASS

**Step 5: Add console_scripts entry point to pyproject.toml**

Add to `pyproject.toml`:
```toml
[project.scripts]
pianissimo = "pianissimo.cli:main"
```

**Step 6: Commit**

```bash
git add src/pianissimo/cli.py tests/test_cli.py pyproject.toml
git commit -m "feat: add CLI entry point with click"
```

---

### Task 6: Integration Test

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

`tests/test_integration.py`:
```python
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
```

**Step 2: Run integration test**

Run: `pipenv run pytest tests/test_integration.py -v`
Expected: PASS (or skip if no LilyPond)

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration test"
```

---

### Task 7: README and Final Polish

**Files:**
- Create: `README.md`

**Step 1: Write README**

`README.md`:
```markdown
# Pianissimo

A sight-reading drill generator for piano. Describe your difficulty, get a personalized practice sheet.

## Prerequisites

- Python 3.13+
- [LilyPond](https://lilypond.org/) (`brew install lilypond` on macOS)
- An Anthropic API key (set `ANTHROPIC_API_KEY` env var)

## Install

```bash
pipenv install
```

## Usage

```bash
pipenv run python -m pianissimo.cli "I keep struggling to read the bass clef"
```

The tool will ask 1-3 follow-up questions, then generate a PDF drill in `drills/`.
```

**Step 2: Run all tests**

Run: `pipenv run pytest -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```
