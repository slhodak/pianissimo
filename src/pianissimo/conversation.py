import json
import os
import re
from typing import Optional

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


def parse_drill_spec_from_response(response: str) -> Optional[DrillSpec]:
    match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        return DrillSpec.from_dict(data)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"[Warning: could not parse drill spec: {e}]")
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
