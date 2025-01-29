import psMat
from fontforge import font as Font

from .parameter import GlyphShape
from .utils import (
    copy_glyph,
    draw_square,
    fit,
    resize_width,
)


def modify_m(hack: Font, cutoff: int) -> None:
    m_unicode = 0x6D
    hack.selection.select(m_unicode)
    pen = hack[m_unicode].glyphPen(replace=False)

    draw_square(pen, (0, 0), 1200, 1200)  # cover the whole
    draw_square(pen, (500, 0), 250, cutoff, erase=True)  # erase center bottom

    hack.intersect()
    hack.selection.none()


def modify_zero(hack: Font) -> None:
    zero_unicode = 0x30
    hack.selection.select(zero_unicode)
    pen = hack[zero_unicode].glyphPen(replace=False)

    draw_square(pen, (0, -50), 1200, 1600)  # cover the whole
    draw_square(pen, (500, 250), 250, 900, erase=True)  # erase center hole

    hack.intersect()
    hack.selection.none()

    # copy middle dot
    copy_glyph((hack, 0xB7), (hack, zero_unicode))


def modify_vline(hack: Font) -> None:
    vline_unicode = 0x007C
    vline = hack[vline_unicode]

    # copy broken bar
    copy_glyph((hack, 0x00A6), (hack, vline_unicode), replace=True)

    # move to top edge
    _, _, _, top = vline.boundingBox()
    vline.transform(psMat.translate((0, hack.ascent - top)))


def modify_hack(
    hack: Font,
    shape_as: GlyphShape,
    shape_to: GlyphShape,
    skew: float = 0,
    m_cutoff: int = 400,
    dot_zero: bool = True,
    broken_vline: bool = True,
) -> None:
    if m_cutoff > 0:
        modify_m(hack, m_cutoff)

    if dot_zero:
        modify_zero(hack)

    if broken_vline:
        modify_vline(hack)

    # reshape
    hack.ascent = shape_as.ascent
    hack.descent = shape_as.descent
    for glyph in hack.glyphs():
        if glyph.width:
            resize_width(glyph, shape_as.half_width, rescale_glyph=False)
            fit(glyph, shape_to.half_width, shape_to.ascent, shape_to.descent)

    # italic
    if skew:
        for glyph in hack.glyphs():
            if glyph.isWorthOutputting:
                glyph.transform(psMat.skew(skew))
