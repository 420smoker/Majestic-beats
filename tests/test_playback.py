import pytest
from majestic_beats import playback
from majestic_beats.cli import main


def test_play_uses_first_backend(monkeypatch):
    seen = []
    monkeypatch.setattr(playback, "detect_backend",
                        lambda: ("termux-media-player",
                                 ["termux-media-player", "play"]))
    monkeypatch.setattr(playback.subprocess, "run",
                        lambda cmd, check: seen.append(cmd))
    name = playback.play("x.wav")
    assert name == "termux-media-player"
    assert seen and seen[0][0] == "termux-media-player"


def test_play_raises_when_no_backend(monkeypatch):
    monkeypatch.setattr(playback, "detect_backend", lambda: (None, None))
    with pytest.raises(RuntimeError, match="no audio player"):
        playback.play("x.wav")


def test_play_command_writes_and_plays(tmp_path, monkeypatch):
    monkeypatch.setattr("majestic_beats.cli.play_audio", lambda p: "fake")
    out = tmp_path / "loop.wav"
    assert main(["play", "--seed", "1", "-o", str(out)]) == 0
    assert out.exists() and out.stat().st_size > 1000


def test_play_command_missing_backend_exits_2(tmp_path, monkeypatch, capsys):
    def boom(p):
        raise RuntimeError("no audio player found")
    monkeypatch.setattr("majestic_beats.cli.play_audio", boom)
    assert main(["play", "--seed", "1", "-o", str(tmp_path / "x.wav")]) == 2
    assert "no audio player" in capsys.readouterr().out


def test_play_accepts_preset(tmp_path, monkeypatch):
    monkeypatch.setattr("majestic_beats.cli.play_audio", lambda p: "fake")
    out = tmp_path / "loop.wav"
    assert main(["play", "--preset", "trap-basic", "-o", str(out)]) == 0


def test_play_rejects_prompt_plus_style(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert main(["play", "--prompt", "x", "--style", "trap",
                 "-o", str(tmp_path / "y.wav")]) == 2
    assert "cannot be combined" in capsys.readouterr().out
