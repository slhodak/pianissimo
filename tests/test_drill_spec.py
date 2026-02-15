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
