# Pianissimo — Sight-Reading Drill Generator

## Purpose

A CLI tool that generates personalized sight-reading drills for an early-intermediate piano player. The user describes their difficulty in natural language, a short LLM-powered conversation narrows it down, and the tool produces a printable PDF of exercises.

## User Profile

- Early intermediate pianist
- Pain points: note identification, rhythm reading, key signatures, hands together
- Wants minimal friction — the tool should feel like talking to a helpful teacher, not filling out a form

## Interaction Model

Primary interface is natural language:

```
$ pianissimo "I keep struggling to read the bass clef"
> Are you struggling more with notes inside the staff, or on ledger lines?
< inside the staff
> Do you want to specify a key, or should I surprise you?
  If I surprise you, should it be a common key or a challenging one?
< surprise me, common key
> Generating: bass clef, C3-B3, quarter and half notes, key of F, 8 measures...
[PDF saved to drills/2026-02-14-bass-clef-notes.pdf]
```

The LLM acts as a brief diagnostic layer (1-3 follow-up questions max), then generates.

## Architecture

Three layers:

1. **LLM conversation layer** — interprets natural language, asks clarifying questions, produces a structured drill spec. The LLM receives the drill spec schema as context so it knows what's possible and what questions are useful.

2. **Generator engine** — takes a drill spec, uses `music21` to produce randomized but musically valid exercises.

3. **Renderer** — exports the `music21` score via LilyPond to PDF.

## Drill Spec

A JSON object with these fields:

- `clef`: treble | bass | grand
- `key`: key signature (e.g. "F major", "Bb major")
- `note_range`: lowest to highest pitch (e.g. "C3-B3")
- `rhythms`: list of note values (whole, half, quarter, eighth, dotted_quarter, etc.)
- `time_signature`: e.g. "4/4", "3/4"
- `measures`: number of measures (default 8)
- `hands`: right | left | both
- `rests`: whether to include rests and which types
- `intervals`: max interval between consecutive notes

## Output

- PDFs saved to `drills/` directory with date-based filenames
- JSON sidecar with the drill spec for regeneration/tweaking
- e.g. `drills/2026-02-14-bass-clef-notes.pdf` + `.json`

## Dependencies

- `music21` — programmatic score generation (MIT)
- LilyPond — music engraving to PDF (GPL, installed separately)
- Anthropic or OpenAI SDK — LLM conversation
- `click` or `argparse` — CLI

## Error Handling

- Detect missing LilyPond and give install instructions
- Detect missing API key and give setup instructions
- Validate LLM-produced drill specs against schema; retry once on invalid

## Testing

- Unit tests: given a drill spec, generator produces valid `music21` scores with correct properties
- Integration test: end-to-end PDF generation
- LLM conversation layer not heavily tested — focus on spec-to-music pipeline

## Future

- Structured CLI flags as power-user mode
- Packaging with all deps
- Preset curricula for progressive difficulty
