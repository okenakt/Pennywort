import psMat
from fontforge import font as Font

from .parameter import GlyphShape
from .utils import copy_glyph, fit, resize_width


def modify_zenkaku_space(mgenplus: Font) -> None:
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

    mgenplus.selection.select(space_unicode)
    mgenplus.intersect()
    mgenplus.selection.none()


def modify_mgenplus(
    mgenplus: Font,
    shape_as: GlyphShape,
    shape_to: GlyphShape,
    skew: float = 0,
    visualize_zenkaku_space: bool = True,
    baseline_shift: float = 0,
    weight: float = 0,
) -> None:
    if visualize_zenkaku_space:
        modify_zenkaku_space(mgenplus)

    # reshape
    original_em = mgenplus.em
    mgenplus.ascent = shape_as.ascent
    mgenplus.descent = shape_as.descent
    for glyph in mgenplus.glyphs():
        if glyph.width > original_em / 2:
            source_width = shape_as.full_width
            target_width = shape_to.full_width
        elif glyph.width > 0:
            source_width = shape_as.half_width
            target_width = shape_to.half_width
        else:
            continue

        if baseline_shift != 0:
            glyph.transform(psMat.translate((0, baseline_shift)))

        resize_width(glyph, source_width, rescale_glyph=False)
        fit(glyph, target_width, shape_to.ascent, shape_to.descent)

        if weight != 0:
            glyph.changeWeight(weight, "auto", 0, 0, "auto")
            resize_width(glyph, target_width, rescale_glyph=False)

    # italic
    if skew:
        for glyph in mgenplus.glyphs():
            if glyph.isWorthOutputting:
                glyph.transform(psMat.skew(skew))
