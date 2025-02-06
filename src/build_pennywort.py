import argparse
import json
from pathlib import Path

import fontforge
from fontforge import font as Font

from .modify_bizud import modify_bizud
from .modify_hack import modify_hack
from .parameter import Parameter
from .utils import append_sfnt_name, log, set_os2_table

# Language IDs
US = 0x0409  # en-US English (US)
JP = 0x0411  # ja-JP Japanese


def build_pennywort(
    parameter: Parameter,
    source_fonts_dir: Path,
    version: str | None,
    copyright_file: str | None,
    license_url: str | None,
) -> Font:
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

    log("Modify BIZUD")
    bizud = open_font(parameter.bizud.source)
    modify_bizud(
        bizud,
        parameter.bizud.shape_as,
        parameter.shape_to,
        parameter.skew,
        parameter.bizud.visualize_zenkaku_space,
        parameter.bizud.baseline_shift,
        parameter.bizud.weight,
    )

    log("Load Nerd Font")
    nerd = open_font(parameter.nerd.source)

    log("Merge fonts")
    pennywort = Font()
    pennywort.mergeFonts(hack)
    pennywort.mergeFonts(bizud)
    pennywort.mergeFonts(nerd)

    hack.close()
    bizud.close()
    nerd.close()

    log("Set properties")
    family_name = parameter.family_name
    style_name = parameter.style_name

    pennywort.fontname = f"{family_name}-{style_name}".replace(" ", "")
    pennywort.fullname = f"{family_name} {style_name}"
    pennywort.familyname = family_name
    pennywort.weight = parameter.weight_name
    pennywort.ascent = parameter.shape_to.ascent
    pennywort.descent = parameter.shape_to.descent
    pennywort.upos = parameter.upos
    if version is not None:
        pennywort.version = version

    # sfnt name table
    append_sfnt_name(pennywort, [US], "SubFamily", style_name)
    if copyright_file is not None:
        append_sfnt_name(pennywort, [US, JP], "Copyright", open(copyright_file).read())
    if license_url is not None:
        append_sfnt_name(pennywort, [US, JP], "License URL", license_url)

    # os2 table
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
        + "--version {major}.{minor}"
        + "--copyright-file /path/to/copyright"
        + "--license-url https://github.com/you/project/license"
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
    parser.add_argument(
        "--version",
        type=str,
        default="1.000",
        help="Font version.",
    )
    parser.add_argument(
        "--copyright-file",
        type=str,
        required=False,
        help="Copyright file.",
    )
    parser.add_argument(
        "--license-url",
        type=str,
        required=False,
        help="License URL.",
    )
    parser.add_argument("parameter_file", type=str, help="Path to parameter.json.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    source_fonts_dir = Path(args.src_dir)
    with open(args.parameter_file) as f:
        parameter = Parameter.from_dict(json.load(f))

    log(f"Build {parameter.family_name} {parameter.style_name} {args.version}")
    pennywort = build_pennywort(
        parameter,
        source_fonts_dir,
        args.version,
        args.copyright_file,
        args.license_url,
    )

    output_path = str(Path(args.dst_dir) / f"{pennywort.fontname}.ttf")
    log(f"Generate {output_path}")
    pennywort.generate(output_path)
