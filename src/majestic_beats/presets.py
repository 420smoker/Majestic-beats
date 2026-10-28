from __future__ import annotations
import json
from importlib import resources

from .pattern import Pattern
from .randomize import STYLES, randomize

_DIR = resources.files("majestic_beats") / "presets"


def _read(name: str) -> dict:
    path = _DIR / f"{name}.json"
    try:
        if not path.is_file():
            raise FileNotFoundError
        return json.loads(path.read_text())
    except (FileNotFoundError, NotADirectoryError):
        raise ValueError(f"unknown preset {name!r} — run `majestic-beats presets`")


def list_presets() -> dict[str, dict]:
    if not _DIR.is_dir():
        return {}
    return {p.name[:-5]: json.loads(p.read_text())
            for p in _DIR.iterdir() if p.name.endswith(".json")}


def load_preset(name: str, *, bpm=None, bars=None, seed=None) -> Pattern:
    data = _read(name)

    # Fixed pattern: anything containing "hits"
    if "hits" in data:
        if bars is not None and bars != data.get("bars", 4):
            raise ValueError(
                f"preset {name!r} is a fixed pattern; --bars cannot override it"
            )
        pat = Pattern.from_dict(data)
        if bpm is not None:
            pat.bpm = bpm
        if seed is not None:
            pat.seed = seed
        pat.validate()
        return pat

    # Generative: {"style": ..., "bpm": ..., "bars": ..., "seed": ...}
    if "style" in data:
        style = data["style"]
        if style not in STYLES:
            raise ValueError(f"preset {name!r}: unknown style {style!r}")
        return randomize(
            bpm=bpm if bpm is not None else data.get("bpm", 100),
            bars=bars if bars is not None else data.get("bars", 4),
            style=style,
            seed=seed if seed is not None else data.get("seed"),
        )

    raise ValueError(f"preset {name!r} is neither a Pattern nor a generative spec")
