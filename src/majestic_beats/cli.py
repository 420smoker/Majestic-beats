import argparse
import json
from pathlib import Path

from .pattern import Pattern
from .randomize import STYLES, randomize
from .render import render


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="majestic-beats",
                                description="Programmatic drum loop generator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Randomize and render a loop")
    g.add_argument("-b", "--bpm", type=int, default=100)
    g.add_argument("--bars", type=int, default=4)
    g.add_argument("--style", choices=list(STYLES), default="boom-bap")
    g.add_argument("--seed", type=int, default=None)
    g.add_argument("-o", "--output", default="output/loop.wav")
    g.add_argument("--save-pattern", default=None,
                   help="Also write the Pattern as JSON")

    r = sub.add_parser("render", help="Render an existing Pattern JSON file")
    r.add_argument("pattern")
    r.add_argument("-o", "--output", default="output/loop.wav")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "generate":
        pat = randomize(bpm=args.bpm, bars=args.bars,
                        style=args.style, seed=args.seed)
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
