import psMat
from fontforge import font as Font

from .parameter import GlyphShape
from .utils import copy_glyph, fit, resize_width


def modify_zenkaku_space(bizud: Font) -> None:
    space_unicode = 0x3000  # ideographic space

    copy_glyph(
        (bizud, 0x25A1),  # white square
        (bizud, space_unicode),
        replace=True,
    )
    copy_glyph(
        (bizud, 0x25C6),  # black diamond
        (bizud, space_unicode),
    )

    bizud.selection.select(space_unicode)
    bizud.intersect()
    bizud.selection.none()


def modify_bizud(
    bizud: Font,
    shape_as: GlyphShape,
    shape_to: GlyphShape,
    skew: float = 0,
    visualize_zenkaku_space: bool = True,
    baseline_shift: float = 0,
    weight: float = 0,
) -> None:
    if visualize_zenkaku_space:
        modify_zenkaku_space(bizud)

    # reshape
    original_em = bizud.em
    bizud.ascent = shape_as.ascent
    bizud.descent = shape_as.descent
    for glyph in bizud.glyphs():
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
        for glyph in bizud.glyphs():
            if glyph.isWorthOutputting:
                glyph.transform(psMat.skew(skew))
