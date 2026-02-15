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
        assert interval <= 7, f"Interval {interval} too large between {notes[i-1].pitch} and {notes[i].pitch}"
