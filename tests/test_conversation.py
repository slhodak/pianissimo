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
