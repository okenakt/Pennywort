import argparse
import json
import os
from pathlib import Path

import fontforge
from fontforge import font as Font

from .modify_hack import modify_hack
from .modify_mgenplus import modify_mgenplus
from .parameter import Parameter
from .utils import log, set_os2_table

VERSION = os.getenv("VERSION", "v0.0.0")


def build_pennywort(parameter: Parameter, source_fonts_dir: Path) -> Font:
    def open_font(file_name: str) -> Font:
        return fontforge.open(str(source_fonts_dir / file_name))

    log("Modify Hack")
    hack = open_font(parameter.hack.source)
    modify_hack(
        hack,
        parameter.hack.shape_as,
        parameter.shape_to,
        parameter.skew,
        parameter.hack.m_cutoff,
        parameter.hack.dot_zero,
        parameter.hack.broken_vline,
    )

    log("Modify Mgen+")
    mgenplus = open_font(parameter.mgenplus.source)
    modify_mgenplus(
        mgenplus,
        parameter.mgenplus.shape_as,
        parameter.shape_to,
        parameter.skew,
        parameter.mgenplus.visualize_zenkaku_space,
        parameter.mgenplus.baseline_shift,
        parameter.mgenplus.weight,
    )

    log("Load Nerd Font")
    nerd = open_font(parameter.nerd.source)

    log("Merge fonts")
    pennywort = Font()
    pennywort.mergeFonts(hack)
    pennywort.mergeFonts(mgenplus)
    pennywort.mergeFonts(nerd)

    hack.close()
    mgenplus.close()
    nerd.close()

    log("Set attributes")
    pennywort.fontname = parameter.family_name
    pennywort.familyname = parameter.family_name
    pennywort.weight = parameter.weight_name
    pennywort.fullname = f"{parameter.family_name}-{parameter.style_name}"
    pennywort.ascent = parameter.shape_to.ascent
    pennywort.descent = parameter.shape_to.descent
    pennywort.upos = parameter.upos
    pennywort.version = VERSION

    set_os2_table(
        pennywort,
        parameter.os2_table,
        parameter.shape_to.ascent,
        parameter.shape_to.descent,
    )

    return pennywort


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pennywort builder.",
        usage="python -m pennywort"
        + "--src-dir /path/to/source_fonts"
        + "--dst-dir /path/to/destination"
        + "/path/to/parameter/json",
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
    parser.add_argument("parameter_file", type=str, help="Path to parameter.json.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    source_fonts_dir = Path(args.src_dir)
    with open(args.parameter_file) as f:
        parameter = Parameter.from_dict(json.load(f))

    log(f"Build {parameter.family_name}-{parameter.style_name}:{VERSION}")
    pennywort = build_pennywort(parameter, source_fonts_dir)

    output_path = str(Path(args.dst_dir) / f"{pennywort.fullname.replace(' ', '')}.ttf")
    log(f"Generate {output_path}")
    pennywort.generate(output_path)
