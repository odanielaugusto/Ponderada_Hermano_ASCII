from __future__ import annotations

import sys
import time
from typing import TextIO

from ascii_art.font import FONT, FONT_HEIGHT, UNKNOWN_GLYPH


def render_text(text: str, *, fill: str = "#", gap: int = 1) -> str:
    """Render text using a small fixed-height ASCII font."""
    if len(fill) != 1:
        raise ValueError("fill must be exactly one character")
    if gap < 0:
        raise ValueError("gap must be zero or greater")

    rendered_blocks = [_render_line(line, fill=fill, gap=gap) for line in text.splitlines()]
    return "\n\n".join(rendered_blocks)


def print_animated(art: str, *, delay: float = 0.03, stream: TextIO | None = None) -> None:
    """Print rendered art line by line to make the drawing appear in the terminal."""
    output = stream or sys.stdout
    for line in art.splitlines():
        print(line, file=output)
        output.flush()
        if delay > 0:
            time.sleep(delay)


def _render_line(text: str, *, fill: str, gap: int) -> str:
    rows = [""] * FONT_HEIGHT
    spacing = " " * gap

    for char in text.upper():
        glyph = FONT.get(char, UNKNOWN_GLYPH)
        for row_index, pattern in enumerate(glyph):
            rows[row_index] += pattern.replace("#", fill) + spacing

    return "\n".join(row.rstrip() for row in rows)
