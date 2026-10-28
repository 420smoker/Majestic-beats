from pydub import AudioSegment
from .pattern import Pattern
from . import generators

PALETTE = {
    "kick":  generators.kick,
    "snare": generators.snare,
    "hihat": generators.hihat,
}


def render(pattern: Pattern) -> AudioSegment:
    pattern.validate()
    sounds = {name: fn() for name, fn in PALETTE.items()}
    tail_ms = max(len(s) for s in sounds.values())
    total_ms = int(pattern.total_steps * pattern.step_ms)

    canvas = AudioSegment.silent(
        duration=total_ms + tail_ms, frame_rate=generators.SAMPLE_RATE
    )
    for name, steps in pattern.hits.items():
        sound = sounds[name]
        for step in steps:
            canvas = canvas.overlay(sound, position=int(step * pattern.step_ms))

    return canvas[:total_ms]
