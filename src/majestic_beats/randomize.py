from __future__ import annotations
import random
from .pattern import Pattern

STYLES = {
    "boom-bap": {
        "kick":  [1.0, 0,   0,   .3,  0,   0,   0,   0,   .9,  0,   .4,  0,   0,   0,   .2,  0],
        "snare": [0,   0,   0,   0,   1.0, 0,   0,   .15, 0,   0,   0,   0,   1.0, 0,   0,   .15],
        "hihat": [.9,  .1,  .9,  .1,  .9,  .1,  .9,  .1,  .9,  .1,  .9,  .1,  .9,  .1,  .9,  .1],
    },
    "trap": {
        "kick":  [1.0, 0,   0,   0,   0,   0,   .5,  0,   0,   0,   .5,  .3,  0,   0,   0,   0],
        "snare": [0,   0,   0,   0,   0,   0,   0,   0,   1.0, 0,   0,   0,   0,   0,   0,   .2],
        "hihat": [.9,  .5,  .9,  .5,  .9,  .5,  .9,  .5,  .9,  .5,  .9,  .5,  .9,  .5,  .9,  .5],
    },
    "house": {
        "kick":  [1.0, 0,   0,   0,   1.0, 0,   0,   0,   1.0, 0,   0,   0,   1.0, 0,   0,   0],
        "snare": [0,   0,   0,   0,   1.0, 0,   0,   0,   0,   0,   0,   0,   1.0, 0,   0,   0],
        "hihat": [.3,  .1,  .8,  .1,  .3,  .1,  .8,  .1,  .3,  .1,  .8,  .1,  .3,  .1,  .8,  .1],
    },
}


def randomize(bpm: int = 100, bars: int = 4, style: str = "boom-bap",
              seed: int | None = None) -> Pattern:
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}; choose from {list(STYLES)}")
    rng = random.Random(seed)
    table = STYLES[style]
    steps_per_bar = len(next(iter(table.values())))

    hits = {name: [] for name in table}
    for bar in range(bars):
        offset = bar * steps_per_bar
        for name, vec in table.items():
            for i, p in enumerate(vec):
                if rng.random() < p:
                    hits[name].append(offset + i)

    if 0 not in hits["kick"]:
        hits["kick"].insert(0, 0)

    return Pattern(bpm=bpm, bars=bars, hits=hits, seed=seed, style=style)
