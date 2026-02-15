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


def _build_pitch_pool(low: str, high: str, key_obj: m21key.Key) -> list:
    low_p = pitch.Pitch(low)
    high_p = pitch.Pitch(high)
    scale_pitches = key_obj.getPitches(low_p, high_p)
    return [p for p in scale_pitches if low_p <= p <= high_p]


def _pick_next_pitch(pool, prev, max_interval: int):
    if prev is None:
        return random.choice(pool)
    candidates = [p for p in pool if abs(p.midi - prev.midi) <= max_interval + 2]
    if not candidates:
        candidates = pool
    return random.choice(candidates)


def _generate_part(spec: DrillSpec, clef_name: str, hand: str) -> stream.Part:
    part = stream.Part()
    clef_obj = _get_clef(clef_name, hand)

    key_parts = spec.key.split()
    key_obj = m21key.Key(key_parts[0], key_parts[1] if len(key_parts) > 1 else None)
    ts = meter.TimeSignature(spec.time_signature)

    low, high = spec.note_range
    pool = _build_pitch_pool(low, high, key_obj)
    if not pool:
        pool = [pitch.Pitch(low)]

    ql_per_measure = ts.barDuration.quarterLength
    rhythm_qls = [RHYTHM_TO_QUARTER_LENGTH[r] for r in spec.rhythms]

    ks = m21key.KeySignature(key_obj.sharps)
    part.insert(0, clef_obj)
    part.insert(0, ks)
    part.insert(0, ts)

    prev_pitch = None
    for m_num in range(spec.measures):
        measure = stream.Measure(number=m_num + 1)

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
