from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

import psMat
from fontforge import font as Font
from fontforge import glyph as Glyph
from fontforge import glyphPen as GlyphPen


def log(msg: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def round_half_up(f: float, e: str = "0") -> Decimal:
    return Decimal(str(f)).quantize(Decimal(e), ROUND_HALF_UP)


def remove_glyphs(font: Font, start: int, stop: int | None = None) -> None:
    if stop is None:
        font.selection.select(start)
    else:
        font.selection.select(("ranges",), start, stop)
    font.clear()
    font.selection.none()


def copy_glyph(
    src: tuple[Font, int],
    dst: tuple[Font, int],
    replace: bool = False,
) -> None:
    src_font, src_unicode = src
    dst_font, dst_unicode = dst

    src_font.selection.select(src_unicode)
    src_font.copy()
    src_font.selection.none()

    dst_font.selection.select(dst_unicode)
    if replace:
        dst_font.paste()
    else:
        dst_font.pasteInto()
    dst_font.selection.none()


def fit(glyph: Glyph, width: int, ascent: int) -> None:
    # fit to short side
    glyph.transform(psMat.scale(min(width / glyph.width, ascent / glyph.font.ascent)))

    # shift to original position
    glyph.transform(psMat.translate((width - glyph.width) / 2))
    glyph.width = width


def draw_square(
    pen: GlyphPen,
    xy: tuple[float, float],
    width: float,
    height: float,
    erase: bool = False,
) -> None:
    x, y = xy
    points = [
        # (x, y),  # lower left
        (x, y + height),  # upper left
        (x + width, y + height),  # upper right
        (x + width, y),  # lower right
    ]
    if erase:
        points = points[::-1]

    pen.moveTo(xy)
    for pt in points:
        pen.lineTo(pt)
    pen.closePath()


def print_metrics(font: Font, unicode: int) -> None:
    print("width:", font[unicode].width)
    print("ascent:", font.ascent)
    print("descent:", font.descent)
    print("height:", font.ascent + font.descent)
    print("ascent / width:", font.ascent / font[unicode].width)
    print("width / ascent:", font[unicode].width / font.ascent)
    print("height / width:", (font.ascent + font.descent) / font[unicode].width)
    print("width / height:", font[unicode].width / (font.ascent + font.descent))
    print()
