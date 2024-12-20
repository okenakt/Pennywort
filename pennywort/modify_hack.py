import psMat
from fontforge import font as Font

from .parameter import HackConfig
from .utils import (
    copy_glyph,
    draw_square,
    fit,
)


def modify_m(hack: Font, cutoff: int) -> None:
    m_unicode = 0x6D
    hack.selection.select(m_unicode)
    pen = hack[m_unicode].glyphPen(replace=False)

    draw_square(pen, (0, 0), 1200, 1200)  # cover the whole
    draw_square(pen, (500, 0), 250, cutoff, erase=False)  # erase center bottom

    hack.intersect()
    hack.selection.none()


def modify_zero(hack: Font) -> None:
    zero_unicode = 0x30
    hack.selection.select(zero_unicode)
    pen = hack[zero_unicode].glyphPen(replace=False)

    draw_square(pen, (0, -50), 1200, 1600)  # cover the whole
    draw_square(pen, (500, 250), 250, 900, erase=False)  # erase center hole

    hack.intersect()
    hack.selection.none()

    # copy middle dot
    copy_glyph((hack, 0xB7), (hack, zero_unicode))


def modify_hack(hack: Font, config: HackConfig) -> None:
    modify_m(hack, config.m_cutoff)
    modify_zero(hack)
    copy_glyph((hack, 0x00A6), (hack, 0x007C))  # broken bar -> vertical line

    for glyph in hack.glyphs():
        if glyph.width:
            fit(glyph, config.width, config.ascent)

        # maximize box drawings
        # if glyph.unicode >= 0x2500 and glyph.unicode <= 0x25AF:
        #     glyph.transform(
        #         psMat.compose(psMat.scale(1.024, 1.024), psMat.translate(0, -30))
        #     )

    print(config.skew)

    # italic
    if config.skew:
        for glyph in hack.glyphs():
            if glyph.isWorthOutputting:
                glyph.transform(psMat.skew(config.skew))
