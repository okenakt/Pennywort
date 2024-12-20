import argparse
from dataclasses import dataclass
from pathlib import Path

import fontforge
from dataclasses_json import DataClassJsonMixin
from fontforge import font as Font

from .utils import copy_glyph, fit, log

ASCENT = 810
DESCENT = 270


@dataclass(frozen=True)
class FontMap(DataClassJsonMixin):
    @dataclass(frozen=True)
    class GlyphMap(DataClassJsonMixin):
        src_range: tuple[int, int]  # [start, stop]
        dst_start: int

    source: str
    glyph_maps: list[GlyphMap]

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

    return parser.parse_args()


def build_nerd(source_fonts_dir: Path) -> Font:
    name = "NerdFont"
    nerd = Font()
    nerd.familyname = name
    nerd.fontname = name
    nerd.fullname = name
    nerd.encoding = "UnicodeFull"
    nerd.ascent = ASCENT
    nerd.descent = DESCENT
    nerd.em = nerd.ascent + nerd.descent
    width = nerd.em

    for glyph_set in GLYPH_SETS:
        log(f"Merge {glyph_set.source}")
        src_font = fontforge.open(str(source_fonts_dir / glyph_set.source))
        src_font.ascent = nerd.ascent
        src_font.descent = nerd.descent
        src_font.em = nerd.em

        for glyph_map in glyph_set.glyph_maps:
            start, stop = glyph_map.src_range
            log(f"Copy {hex(start)}~{hex(stop)} -> {hex(glyph_map.dst_start)}~")

            for i, s in enumerate(range(start, stop + 1)):
                if s in src_font:
                    # ToDo: resize
                    fit(src_font[s], width, nerd.ascent)
                    copy_glyph(
                        (src_font, s),
                        (nerd, glyph_map.dst_start + i),
                        replace=True,
                    )

        src_font.close()

    return nerd


if __name__ == "__main__":
    args = parse_args()

    source_fonts_dir = Path(args.src_dir)

    log("Build Nerd Font")
    nerd = build_nerd(source_fonts_dir)

    output_path = str(Path(args.dst_dir) / f"{nerd.fullname}.ttf")
    log(f"Generate {output_path}")
    nerd.generate(output_path)
