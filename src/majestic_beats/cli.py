import argparse
import json
from pathlib import Path

from .ai import pattern_from_prompt
from .pattern import Pattern
from .playback import play as play_audio
from .presets import list_presets, load_preset
from .randomize import STYLES, randomize
from .render import render


def _add_source_args(p):
    p.add_argument("-b", "--bpm", type=int, default=None)
    p.add_argument("--bars", type=int, default=None)
    p.add_argument("--style", choices=list(STYLES), default=None)
    p.add_argument("-p", "--preset", default=None)
    p.add_argument("--prompt", default=None,
                   help="Natural-language prompt (needs ANTHROPIC_API_KEY "
                        "or OPENAI_API_KEY)")
    p.add_argument("--seed", type=int, default=None)


def _resolve_pattern(args) -> Pattern:
    if args.prompt:
        if args.preset or args.style:
            raise ValueError("--prompt cannot be combined with --preset or --style")
        if args.bars is not None:
            raise ValueError("the AI sets bars; --bars cannot be used with --prompt")
        pat = pattern_from_prompt(args.prompt, seed=args.seed)
        if args.bpm is not None:
            pat.bpm = args.bpm
        return pat

    if args.preset:
        if args.style:
            raise ValueError("--preset and --style are mutually exclusive")
        return load_preset(args.preset, bpm=args.bpm, bars=args.bars, seed=args.seed)

    return randomize(
        bpm=args.bpm if args.bpm is not None else 100,
        bars=args.bars if args.bars is not None else 4,
        style=args.style or "boom-bap",
        seed=args.seed,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="majestic-beats",
                                description="Programmatic drum loop generator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Render a loop to a WAV file")
    _add_source_args(g)
    g.add_argument("-o", "--output", default="output/loop.wav")
    g.add_argument("--save-pattern", default=None)

    pl = sub.add_parser("play", help="Render a loop and play it")
    _add_source_args(pl)
    pl.add_argument("-o", "--output", default="output/loop.wav")
    pl.add_argument("--save-pattern", default=None)

    r = sub.add_parser("render", help="Render an existing Pattern JSON file")
    r.add_argument("pattern")
    r.add_argument("-o", "--output", default="output/loop.wav")

    sub.add_parser("presets", help="List shipped presets")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "presets":
        for name, data in sorted(list_presets().items()):
            kind = ("pattern" if "hits" in data
                    else f"generative ({data.get('style', '?')})")
            print(f"{name:24s} {kind:22s} bpm={data.get('bpm', '?')}")
        return 0

    if args.cmd == "render":
        pat = Pattern.from_dict(json.loads(Path(args.pattern).read_text()))
    else:
        try:
            pat = _resolve_pattern(args)
        except (ValueError, RuntimeError) as e:
            print(f"error: {e}")
            return 2
        if args.save_pattern:
            Path(args.save_pattern).write_text(json.dumps(pat.to_dict(), indent=2))

    audio = render(pat)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    audio.export(out, format="wav")
    print(f"wrote {out}  ({pat.bpm} bpm, {pat.bars} bars, "
          f"{pat.style}, {audio.duration_seconds:.2f}s)")

    if args.cmd == "play":
        try:
            backend = play_audio(out)
        except RuntimeError as e:
            print(f"error: {e}")
            return 2
        except Exception as e:
            print(f"error: playback failed ({e})")
            return 2
        print(f"playing via {backend}")

    return 0
