# Pianissimo

A conversational sight-reading drill generator for piano. A user describes what they're struggling with, an AI piano teacher asks clarifying questions, then generates a personalized practice sheet as a PDF.

## How It Works

1. **CLI (`cli.py`)** — Entry point. Prompts the user for a description of their difficulty, orchestrates the pipeline, and saves outputs.
2. **Conversation (`conversation.py`)** — Multi-turn chat with Claude (Sonnet) acting as a piano teacher. The AI asks 1-3 clarifying questions, then emits a JSON drill specification.
3. **Drill Spec (`drill_spec.py`)** — A `DrillSpec` dataclass that defines drill parameters: clef, key, note range, rhythms, time signature, measure count, hands, rests, and max interval. Includes validation and serialization.
4. **Generator (`generator.py`)** — Takes a `DrillSpec` and produces a `music21` `Score` with randomized notes constrained by the spec (pitch pool from key/range, rhythm selection, interval limits). Supports single-hand and grand staff (both hands).
5. **Renderer (`renderer.py`)** — Converts the `music21` Score to a PDF via LilyPond. Cleans up intermediate `.ly` files.

Outputs are saved to `drills/` as a `.pdf` (the sheet music) and a `.json` (the drill spec for reproducibility).

## Key Dependencies

- **music21** — Music theory and score construction
- **anthropic** — Claude API client for the conversational flow
- **click** — CLI framework
- **LilyPond** — External binary for PDF rendering (not a Python package)

## Prerequisites

- Python 3.13+
- [LilyPond](https://lilypond.org/) (`brew install lilypond` on macOS)
- `ANTHROPIC_API_KEY` environment variable (or `.env` file)

## Install

```bash
pipenv install
```

## Usage

```bash
pipenv run pianissimo
```

## Tests

```bash
pipenv run pytest
```
