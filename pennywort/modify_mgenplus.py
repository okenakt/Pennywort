import psMat
from fontforge import font as Font

from .parameter import MgenplusConfig
from .utils import copy_glyph, fit


def modify_ideographic_space(mgenplus: Font) -> None:
    space_unicode = 0x3000  # ideographic space

    copy_glyph(
        (mgenplus, 0x2610),  # ballot box
        (mgenplus, space_unicode),
        replace=True,
    )
    copy_glyph(
        (mgenplus, 0x271A),  # heavy greek cross
        (mgenplus, space_unicode),
    )

    mgenplus.intersect()


def modify_mgenplus(mgenplus: Font, config: MgenplusConfig) -> None:
    modify_ideographic_space(mgenplus)

    for glyph in mgenplus.glyphs():
        if glyph.width > 512:
            fit(glyph, config.full_width, config.ascent)
        elif glyph.width > 0:
            fit(glyph, config.half_width, config.ascent)

    # italic
    if config.skew:
        for glyph in mgenplus.glyphs():
            if glyph.isWorthOutputting:
                glyph.transform(psMat.skew(config.skew))
