from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise

SAMPLE_RATE = 44100


def kick(duration_ms: int = 120, gain_db: float = -3) -> AudioSegment:
    body = Sine(55).to_audio_segment(duration=duration_ms).fade_in(2).fade_out(90)
    click = Sine(150).to_audio_segment(duration=25).fade_out(20).apply_gain(-8)
    return body.overlay(click, position=0).apply_gain(gain_db)


def snare(duration_ms: int = 150, gain_db: float = -8) -> AudioSegment:
    noise = WhiteNoise().to_audio_segment(duration=duration_ms, volume=-3)
    noise = noise.high_pass_filter(1500).fade_in(1).fade_out(int(duration_ms * 0.7))
    tone = Sine(180).to_audio_segment(duration=60).fade_out(50).apply_gain(-6)
    return noise.overlay(tone, position=0).apply_gain(gain_db)


def hihat(duration_ms: int = 30, gain_db: float = -18) -> AudioSegment:
    noise = WhiteNoise().to_audio_segment(duration=duration_ms, volume=-3)
    noise = noise.high_pass_filter(7000).fade_in(1).fade_out(int(duration_ms * 0.8))
    return noise.apply_gain(gain_db)
