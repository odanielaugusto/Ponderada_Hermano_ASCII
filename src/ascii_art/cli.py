from __future__ import annotations

import argparse

from ascii_art.renderer import print_animated, render_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render text as ASCII art in the terminal.")
    parser.add_argument("--text", help="Text to render. If omitted, the CLI asks for input.")
    parser.add_argument("--fill", default="#", help="Single character used to draw the letters.")
    parser.add_argument("--gap", default=1, type=int, help="Spaces between rendered characters.")
    parser.add_argument("--delay", default=0.03, type=float, help="Delay between printed lines.")
    parser.add_argument("--no-animate", action="store_true", help="Print the full output at once.")
    args = parser.parse_args(argv)

    text = args.text if args.text is not None else input("Texto para virar ASCII art: ")
    art = render_text(text, fill=args.fill, gap=args.gap)

    if args.no_animate:
        print(art)
    else:
        print_animated(art, delay=args.delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
