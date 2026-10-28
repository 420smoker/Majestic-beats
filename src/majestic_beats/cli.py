import argparse
import json
from pathlib import Path

from .pattern import Pattern
from .presets import list_presets, load_preset
from .randomize import STYLES, randomize
from .render import render


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="majestic-beats",
                                description="Programmatic drum loop generator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Render a loop from a preset or the randomizer")
    g.add_argument("-b", "--bpm", type=int, default=None)
    g.add_argument("--bars", type=int, default=None)
    g.add_argument("--style", choices=list(STYLES), default=None)
    g.add_argument("-p", "--preset", default=None)
    g.add_argument("--seed", type=int, default=None)
    g.add_argument("-o", "--output", default="output/loop.wav")
    g.add_argument("--save-pattern", default=None)

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

    if args.cmd == "generate":
        if args.preset and args.style:
            print("error: --preset and --style are mutually exclusive")
            return 2
        if args.preset:
            try:
                pat = load_preset(args.preset, bpm=args.bpm,
                                  bars=args.bars, seed=args.seed)
            except ValueError as e:
                print(f"error: {e}")
                return 2
        else:
            pat = randomize(
                bpm=args.bpm if args.bpm is not None else 100,
                bars=args.bars if args.bars is not None else 4,
                style=args.style or "boom-bap",
                seed=args.seed,
            )
        if args.save_pattern:
            Path(args.save_pattern).write_text(json.dumps(pat.to_dict(), indent=2))
    else:
        pat = Pattern.from_dict(json.loads(Path(args.pattern).read_text()))

    audio = render(pat)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    audio.export(out, format="wav")
    print(f"wrote {out}  ({pat.bpm} bpm, {pat.bars} bars, "
          f"{pat.style}, {audio.duration_seconds:.2f}s)")
    return 0
