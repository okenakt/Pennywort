from pathlib import Path

import fontforge
from fontforge import font as Font

from .modify_hack import modify_hack
from .modify_mgenplus import modify_mgenplus
from .parameter import Parameter
from .utils import log


def build_font(parameter: Parameter, source_fonts_dir: Path) -> Font:
    log("Modify Hack")
    hack = fontforge.open(str(source_fonts_dir / parameter.hack.source))
    modify_hack(hack, parameter.hack.config)

    log("Modify Mgen+")
    mgenplus = fontforge.open(str(source_fonts_dir / parameter.mgenplus.source))
    modify_mgenplus(mgenplus, parameter.mgenplus.config)

    log("Load Nerd Font")
    nerd = fontforge.open(str(source_fonts_dir / parameter.nerd.source))

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

    pennywort.ascent = parameter.ascent
    pennywort.descent = parameter.descent
    pennywort.upos = parameter.upos

    for key, value in parameter.os2_table.items():
        if isinstance(value, list):
            value = tuple(value)
        setattr(pennywort, key, value)

    return pennywort
