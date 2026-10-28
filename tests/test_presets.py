import pytest
from majestic_beats.presets import list_presets, load_preset


def test_all_presets_loadable():
    for name in list_presets():
        load_preset(name, seed=1).validate()


def test_generative_preset_cli_override():
    assert load_preset("boom-bap-lofi", bpm=90, seed=1).bpm == 90


def test_fixed_preset_rejects_bars():
    with pytest.raises(ValueError, match="fixed pattern"):
        load_preset("signature-trap-01", bars=4)


def test_unknown_preset():
    with pytest.raises(ValueError, match="unknown preset"):
        load_preset("nope")
