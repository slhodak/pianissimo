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
