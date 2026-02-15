from dataclasses import dataclass, field, asdict

VALID_CLEFS = ("treble", "bass", "grand")
VALID_RHYTHMS = ("whole", "half", "quarter", "eighth", "dotted_quarter", "dotted_half", "sixteenth")
VALID_HANDS = ("right", "left", "both")

DEFAULT_RANGE_TREBLE = ("C4", "C6")
DEFAULT_RANGE_BASS = ("C2", "C4")


@dataclass
class DrillSpec:
    clef: str = "treble"
    key: str = "C major"
    note_range: tuple[str, str] = None
    rhythms: list[str] = field(default_factory=lambda: ["quarter"])
    time_signature: str = "4/4"
    measures: int = 8
    hands: str = "right"
    rests: bool = False
    max_interval: int = 5

    def __post_init__(self):
        if self.note_range is None:
            if self.clef == "bass":
                self.note_range = DEFAULT_RANGE_BASS
            else:
                self.note_range = DEFAULT_RANGE_TREBLE
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
