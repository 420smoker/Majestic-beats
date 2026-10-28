import pytest
from majestic_beats.pattern import Pattern
from majestic_beats.randomize import randomize, STYLES
from majestic_beats.render import render


def test_pattern_roundtrip():
    p = Pattern(bpm=120, bars=2,
                hits={"kick": [0, 8], "snare": [4, 12], "hihat": [0, 2, 4, 6]})
    p.validate()
    p2 = Pattern.from_dict(p.to_dict())
    assert p2.hits == p.hits and p2.bpm == 120


def test_pattern_rejects_unknown_instrument():
    with pytest.raises(ValueError, match="unknown instrument"):
        Pattern(hits={"cowbell": [0]}).validate()


def test_pattern_rejects_out_of_range_step():
    with pytest.raises(ValueError, match="outside"):
        Pattern(bars=1, hits={"kick": [64]}).validate()


def test_pattern_step_math():
    p = Pattern(bpm=100, bars=4, beats_per_bar=4, steps_per_beat=4)
    assert p.total_steps == 64
    assert p.step_ms == pytest.approx(150.0)


@pytest.mark.parametrize("style", list(STYLES))
def test_randomize_deterministic(style):
    assert randomize(seed=7, style=style).hits == randomize(seed=7, style=style).hits


def test_randomize_kick_on_one():
    for seed in range(20):
        assert 0 in randomize(seed=seed).hits["kick"]


def test_randomize_unknown_style():
    with pytest.raises(ValueError):
        randomize(style="polka")


def test_render_duration_matches_pattern():
    pat = randomize(bpm=100, bars=4, seed=1)
    expected = int(pat.total_steps * pat.step_ms)
    assert abs(len(render(pat)) - expected) <= 1
