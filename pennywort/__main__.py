import argparse
import json
import os
from pathlib import Path

from .build_font import build_font
from .parameter import Parameter
from .utils import log

VERSION = os.getenv("VERSION", "v0.0.0")


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
    pennywort = build_font(parameter, source_fonts_dir)

    output_path = str(Path(args.dst_dir) / f"{pennywort.fullname.replace(' ','')}.ttf")
    log(f"Generate {output_path}")
    pennywort.generate(output_path)
