from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

# Ordered by preference: first one found on PATH wins.
BACKENDS = (
    ("termux-media-player", ["termux-media-player", "play"]),
    ("ffplay",              ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]),
    ("afplay",              ["afplay"]),
    ("aplay",               ["aplay", "-q"]),
    ("paplay",              ["paplay"]),
    ("play",                ["play", "-q"]),   # sox
)


def detect_backend():
    for name, cmd in BACKENDS:
        if shutil.which(cmd[0]):
            return name, cmd
    return None, None


def play(path) -> str:
    name, cmd = detect_backend()
    if cmd is None:
        raise RuntimeError(
            "no audio player found. Install one:\n"
            "  Termux:  pkg install termux-api   (+ the Termux:API app)\n"
            "  Debian:  apt install ffmpeg  or  apt install sox\n"
            "  macOS:   brew install ffmpeg  or  brew install sox"
        )
    path = str(Path(path).resolve())
    try:
        subprocess.run(cmd + [path], check=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"playback via {name} timed out")
    return name
