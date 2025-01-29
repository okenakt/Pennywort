import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import fontforge
import psMat
from dataclasses_json import DataClassJsonMixin
from fontforge import font as Font

from .utils import (
    align_center,
    copy_glyph,
    get_box_mode,
    get_max_box,
    get_max_height,
    get_max_width,
    log,
)

FitTarget = Literal["max_width", "max_height"] | float
HorizontalAlign = Literal["center"] | None
VerticalAlign = Literal["max_top", "mode_bottom"] | None


@dataclass(frozen=True)
class FontMap(DataClassJsonMixin):
    @dataclass(frozen=True)
    class GlyphMap(DataClassJsonMixin):
        src_range: tuple[int, int]  # [start, stop]
        dst_start: int

    source: str
    glyph_maps: list[GlyphMap]
    fit_target: FitTarget = "max_width"
    halign: HorizontalAlign = "center"
    valign: VerticalAlign = "mode_bottom"

    @classmethod
    def bulk_create(cls, kvs: list[dict]) -> list["FontMap"]:
        return [cls.from_dict(kv) for kv in kvs]


GLYPH_SETS = FontMap.bulk_create(
    [
        {  # Seti-UI + Custom
            "source": "original-source.otf",
            "glyph_maps": [
                {
                    "src_range": (0xE4FA, 0xE5B7),
                    "dst_start": 0xE5FA,
                }
            ],
        },
        {  # Devicons
            "source": "devicons/devicons.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xE600, 0xE7EF),
                    "dst_start": 0xE700,
                }
            ],
        },
        {  # Font Awesome
            "source": "font-awesome/FontAwesome.otf",
            "glyph_maps": [
                {
                    "src_range": (0xED00, 0xF2FF),
                    "dst_start": 0xED00,
                }
            ],
        },
        {  # Font Awesome Extension
            "source": "font-awesome-extension.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xE000, 0xE0A9),
                    "dst_start": 0xE200,
                }
            ],
        },
        {  # Material Design Icons
            "source": "materialdesign/MaterialDesignIconsDesktop.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xF0001, 0xF1AF0),
                    "dst_start": 0xF0001,
                }
            ],
        },
        {  # Weather
            "source": "weather-icons/weathericons-regular-webfont.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xF000, 0xF0EB),
                    "dst_start": 0xE300,
                }
            ],
            "fit_target": 2210,
        },
        {  # Octicons
            "source": "octicons/octicons.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xF000, 0xF305),
                    "dst_start": 0xF400,
                },
                {
                    "src_range": (0x2665, 0x2665),
                    "dst_start": 0x2665,
                },
                {
                    "src_range": (0x26A1, 0x26A1),
                    "dst_start": 0x26A1,
                },
            ],
        },
        {  # Powerline Symbols
            "source": "powerline-symbols/PowerlineSymbols.otf",
            "glyph_maps": [
                {
                    "src_range": (0xE0A0, 0xE0A2),
                    "dst_start": 0xE0A0,
                },
                {
                    "src_range": (0xE0B0, 0xE0B3),
                    "dst_start": 0xE0B0,
                },
            ],
            "fit_target": "max_height",
            "halign": None,
            "valign": "max_top",
        },
        {  # Powerline Extra Symbols
            "source": "powerline-extra/PowerlineExtraSymbols.otf",
            "glyph_maps": [
                {
                    "src_range": (0xE0A3, 0xE0A3),
                    "dst_start": 0xE0A3,
                },
                {
                    "src_range": (0xE0B4, 0xE0C8),
                    "dst_start": 0xE0B4,
                },
                {
                    "src_range": (0xE0CA, 0xE0CA),
                    "dst_start": 0xE0CA,
                },
                {
                    "src_range": (0xE0CC, 0xE0D7),
                    "dst_start": 0xE0CC,
                },
            ],
            "fit_target": "max_height",
            "halign": None,
            "valign": "max_top",
        },
        {  # IEC Power Symbols
            "source": "Unicode_IEC_symbol_font.otf",
            "glyph_maps": [
                {
                    "src_range": (0x23FB, 0x23FE),
                    "dst_start": 0x23FB,
                },
                {
                    "src_range": (0x2B58, 0x2B58),
                    "dst_start": 0x2B58,
                },
            ],
        },
        {  # Font Logos
            "source": "font-logos.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xF300, 0xF381),
                    "dst_start": 0xF300,
                },
            ],
        },
        {  # Pomicons
            "source": "pomicons/Pomicons.otf",
            "glyph_maps": [
                {
                    "src_range": (0xE000, 0xE00A),
                    "dst_start": 0xE000,
                },
            ],
        },
        {  # Codicons
            "source": "codicons/codicon.ttf",
            "glyph_maps": [
                {
                    "src_range": (0xEA60, 0xEC1E),
                    "dst_start": 0xEA60,
                },
            ],
        },
        # {  # Additional sets
        #     "source": "extraglyphs.sfd",
        #     "glyph_maps": [],
        # },
    ]
)


def modify(
    font: Font,
    target_ranges: list[tuple[int, int]],
    ascent: int,
    descent: int,
    width: int,
    fit_target: FitTarget,
    halign: HorizontalAlign,
    valign: VerticalAlign,
) -> None:
    glyphs = list(
        {
            font[unicode].unicode: font[unicode]
            for start, stop in target_ranges
            for unicode in range(start, stop + 1)
            if unicode in font
        }.values()
    )

    if fit_target == "max_width":
        max_width = get_max_width(glyphs)
        scale = width / max_width
    elif fit_target == "max_height":
        max_height = get_max_height(glyphs)
        scale = (ascent + descent) / max_height
    else:
        scale = width / fit_target

    if valign == "mode_bottom":
        _, mode_bottom, _, _ = get_box_mode(glyphs)
        shift = (0, -mode_bottom * scale)
    else:
        _, _, _, max_top = get_max_box(glyphs)
        shift = (0, ascent - max_top * scale)

    for glyph in glyphs:
        glyph.transform(psMat.scale(scale))
        glyph.transform(psMat.translate(*shift))
        glyph.width = width
        if halign == "center":
            align_center(glyph)


def build_nerd(source_fonts_dir: Path, ascent: int, descent: int, width: int) -> Font:
    name = "NerdFont"
    nerd = Font()
    nerd.familyname = name
    nerd.fontname = name
    nerd.fullname = name
    nerd.encoding = "UnicodeFull"
    nerd.ascent = ascent
    nerd.descent = descent
    nerd.em = nerd.ascent + nerd.descent

    for glyph_set in GLYPH_SETS:
        src_font = fontforge.open(str(source_fonts_dir / glyph_set.source))

        log(f"Modify {glyph_set.source}")
        log(f"  fit_target: {glyph_set.fit_target}")
        log(f"  halign: {glyph_set.halign}")
        log(f"  valign: {glyph_set.valign}")
        modify(
            src_font,
            [
                (glyph_map.src_range[0], glyph_map.src_range[1])
                for glyph_map in glyph_set.glyph_maps
            ],
            ascent,
            descent,
            width,
            glyph_set.fit_target,
            glyph_set.halign,
            glyph_set.valign,
        )

        for glyph_map in glyph_set.glyph_maps:
            start, stop = glyph_map.src_range
            log(f"Copy {hex(start)}~{hex(stop)} -> {hex(glyph_map.dst_start)}~")

            for i, src_unicode in enumerate(range(start, stop + 1)):
                if src_unicode in src_font:
                    copy_glyph(
                        (src_font, src_unicode),
                        (nerd, glyph_map.dst_start + i),
                        replace=True,
                    )

        src_font.close()

    return nerd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nerd generator.",
        usage="python generate_nerd.py"
        + "--src-dir /path/to/nerd-fonts/FontPatcher/src/glyphs"
        + "--dst-dir /path/to/destination",
    )

    parser.add_argument(
        "--src-dir",
        type=str,
        required=True,
        help="Where the source fonts.",
    )
    parser.add_argument(
        "--dst-dir",
        type=str,
        default="./dist",
        help="Output destination.",
    )
    parser.add_argument(
        "--ascent",
        type=int,
        default=864,
        help="Ascent.",
    )
    parser.add_argument(
        "--descent",
        type=int,
        default=216,
        help="Descent.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=648,
        help="Descent.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    log("Build Nerd Font")
    log(f"  ascent: {args.ascent}")
    log(f"  descent: {args.descent}")
    log(f"  width: {args.width}")
    nerd = build_nerd(Path(args.src_dir), args.ascent, args.descent, args.width)

    output_path = str(Path(args.dst_dir) / f"{nerd.fullname}.ttf")
    log(f"Generate {output_path}")
    nerd.generate(output_path)
