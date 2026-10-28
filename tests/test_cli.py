from majestic_beats.cli import main


def test_presets_command(capsys):
    assert main(["presets"]) == 0
    out = capsys.readouterr().out
    assert "trap-basic" in out and "signature-trap-01" in out


def test_prompt_without_key(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert main(["generate", "--prompt", "x"]) == 2
    assert "no API key" in capsys.readouterr().out


def test_prompt_and_style_conflict(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert main(["generate", "--prompt", "x", "--style", "trap"]) == 2
    assert "cannot be combined" in capsys.readouterr().out


def test_unknown_preset_exits_2(tmp_path, capsys):
    out = tmp_path / "x.wav"
    assert main(["generate", "--preset", "nope", "-o", str(out)]) == 2
    assert "unknown preset" in capsys.readouterr().out
    assert not out.exists()


def test_generate_writes_file(tmp_path):
    out = tmp_path / "loop.wav"
    assert main(["generate", "--seed", "1", "-o", str(out)]) == 0
    assert out.exists() and out.stat().st_size > 1000
