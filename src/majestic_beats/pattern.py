from __future__ import annotations
from dataclasses import dataclass, field, asdict

INSTRUMENTS = ("kick", "snare", "hihat")


@dataclass
class Pattern:
    bpm: int = 100
    bars: int = 4
    beats_per_bar: int = 4
    steps_per_beat: int = 4
    hits: dict[str, list[int]] = field(default_factory=dict)
    seed: int | None = None
    style: str = "boom-bap"

    @property
    def steps_per_bar(self) -> int:
        return self.beats_per_bar * self.steps_per_beat

    @property
    def total_steps(self) -> int:
        return self.bars * self.steps_per_bar

    @property
    def step_ms(self) -> float:
        return (60000 / self.bpm) / self.steps_per_beat

    def validate(self) -> None:
        for name, steps in self.hits.items():
            if name not in INSTRUMENTS:
                raise ValueError(f"unknown instrument {name!r}; expected {INSTRUMENTS}")
            for s in steps:
                if not 0 <= s < self.total_steps:
                    raise ValueError(f"{name}: step {s} outside 0..{self.total_steps - 1}")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Pattern":
        p = cls(**d)
        p.validate()
        return p
