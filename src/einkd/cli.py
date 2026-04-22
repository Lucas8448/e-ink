"""`eink` command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from .display import Display


def _cmd_info(_: argparse.Namespace) -> int:
    info = Display().info
    print(f"{info.name}  {info.width}x{info.height}  colour={info.colour}")
    return 0


def _cmd_clear(args: argparse.Namespace) -> int:
    Display().clear(colour=args.colour)
    return 0


def _cmd_text(args: argparse.Namespace) -> int:
    Display().show_text(args.text, size=args.size)
    return 0


def _cmd_image(args: argparse.Namespace) -> int:
    img = Image.open(args.path)
    Display(saturation=args.saturation).show_image(img, fit=not args.no_fit)
    return 0


def _cmd_apod(args: argparse.Namespace) -> int:
    from . import apod as apod_mod

    a = apod_mod.render_today(api_key=args.api_key, saturation=args.saturation)
    print(f"APOD {a.date}: {a.title}")
    return 0


def _cmd_hello(_: argparse.Namespace) -> int:
    d = Display()
    w, h = d.size
    canvas = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(canvas)
    palette = [
        (0, 0, 0),
        (255, 255, 255),
        (0, 200, 0),
        (0, 0, 200),
        (200, 0, 0),
        (255, 220, 0),
        (255, 120, 0),
    ]
    band = w // len(palette)
    for i, colour in enumerate(palette):
        draw.rectangle([i * band, 0, (i + 1) * band, h // 2], fill=colour)
    d.show_image(canvas, fit=False)
    d.show_text("hello, e-ink", size=72)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="eink", description="Drive the Inky Impression.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("info", help="print detected display info").set_defaults(func=_cmd_info)

    s_clear = sub.add_parser("clear", help="blank the screen")
    s_clear.add_argument("--colour", "--color", default="white")
    s_clear.set_defaults(func=_cmd_clear)

    s_text = sub.add_parser("text", help="render text centred")
    s_text.add_argument("text")
    s_text.add_argument("--size", type=int, default=64)
    s_text.set_defaults(func=_cmd_text)

    s_img = sub.add_parser("image", help="show an image file")
    s_img.add_argument("path", type=Path)
    s_img.add_argument("--no-fit", action="store_true", help="do not letterbox")
    s_img.add_argument("--saturation", type=float, default=0.6)
    s_img.set_defaults(func=_cmd_image)

    s_apod = sub.add_parser("apod", help="render NASA Astronomy Picture of the Day")
    s_apod.add_argument("--api-key", default=None, help="NASA API key (default: $NASA_API_KEY or DEMO_KEY)")
    s_apod.add_argument("--saturation", type=float, default=0.7)
    s_apod.set_defaults(func=_cmd_apod)

    sub.add_parser("hello", help="render a hello-world test pattern").set_defaults(func=_cmd_hello)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
