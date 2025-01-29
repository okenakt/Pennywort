import statistics
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import psMat
from fontforge import font as Font
from fontforge import glyph as Glyph
from fontforge import glyphPen as GlyphPen


def log(msg: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def round_half_up(f: float, e: str = "0") -> Decimal:
    return Decimal(str(f)).quantize(Decimal(e), ROUND_HALF_UP)


def get_max_width(glyphs: list[Glyph]) -> float:
    max_width = 0
    for glyph in glyphs:
        left, _, right, _ = glyph.boundingBox()
        max_width = max(right - left, max_width)

    return max_width


def get_max_height(glyphs: list[Glyph]) -> float:
    max_height = 0
    for glyph in glyphs:
        _, bottom, _, top = glyph.boundingBox()
        max_height = max(top - bottom, max_height)

    return max_height


def get_max_box(glyphs: list[Glyph]) -> tuple[int, ...]:
    xmin, ymin, xmax, ymax = 0, 0, 0, 0
    for glyph in glyphs:
        left, bottom, right, top = glyph.boundingBox()
        xmin = min(left, xmin)
        ymin = min(bottom, ymin)
        xmax = max(right, xmax)
        ymax = max(top, ymax)

    return xmin, ymin, xmax, ymax


def get_box_mode(glyphs: list[Glyph]) -> tuple[int, ...]:
    coords: list[tuple[int, ...]] = []
    for glyph in glyphs:
        coord = glyph.boundingBox()
        coords.append(tuple([int(round_half_up(c)) for c in coord]))

    return tuple(map(statistics.mode, [*zip(*coords)]))


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


def align_center(glyph: Glyph) -> None:
    width = glyph.width
    left, _, right, _ = glyph.boundingBox()
    left_margin = left
    right_margin = width - right
    glyph.transform(psMat.translate((right_margin - left_margin) / 2))
    glyph.width = width


def resize_width(
    glyph: Glyph,
    width: int,
    rescale_glyph: bool = True,
    retain_position: bool = True,
) -> None:
    if rescale_glyph:
        glyph.transform(psMat.scale(width / glyph.width))

    if retain_position:
        glyph.transform(psMat.translate((width - glyph.width) / 2))

    glyph.width = width


def fit(glyph: Glyph, width: int, ascent: int, descent: int) -> None:
    # fit to shortest one
    scale = min(
        width / glyph.width,
        ascent / glyph.font.ascent,
        descent / glyph.font.descent,
    )
    glyph.transform(psMat.scale(scale))

    # shift to original position
    resize_width(glyph, width, rescale_glyph=False)


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


def set_os2_table(
    font: Font,
    os2_table: dict,
    ascent: int | None = None,
    descent: int | None = None,
) -> None:
    def set_absent(key: str, value: Any) -> None:
        if key not in os2_table:
            os2_table[key] = value

    if ascent is not None:
        set_absent("os2_typoascent", ascent)
        set_absent("os2_winascent", ascent)
        set_absent("hhea_ascent", ascent)

    if descent is not None:
        set_absent("os2_typodescent", -descent)
        set_absent("os2_windescent", descent)
        set_absent("hhea_descent", -descent)

    if "os2_panose" in os2_table:
        os2_table["os2_panose"] = tuple(os2_table["os2_panose"])

    for key, value in os2_table.items():
        setattr(font, key, value)


def print_metrics(glyph: Glyph) -> None:
    ascent = glyph.font.ascent
    descent = glyph.font.descent
    width = glyph.width
    left, bottom, right, top = glyph.boundingBox()

    print("ascent:", ascent)
    print("descent:", descent)
    print("left:", left)
    print("right:", right)
    print("bottom:", bottom)
    print("top:", top)
    print("width:", width)
    print("actual_width:", right - left)
    print("height:", ascent + descent)
    print("actual_height:", top - bottom)
    print("ascent / descent:", ascent / descent)
    print("ascent / width:", ascent / width)
    print("width / ascent:", width / ascent)
    print("height / width:", (ascent + descent) / width)
    print("width / height:", width / (ascent + descent))
    print()
