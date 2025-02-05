import unittest

import fontforge
from fontforge import font as Font

from src.utils import calc_actual_size, draw_square


def calc_weight(font: Font, unicode: int, rel_position: float = 1 / 2) -> float | None:
    if unicode not in font:
        return None

    _, height = calc_actual_size(font[unicode])
    font.selection.select(unicode)
    pen = font[unicode].glyphPen(replace=False)
    draw_square(pen, (0, height * rel_position), font[unicode].width, 1)
    font.intersect()
    font.selection.none()
    weight, _ = calc_actual_size(font[unicode])

    return weight


class TestWeight(unittest.TestCase):
    """test weight"""

    def test_weight(self) -> None:
        """calculate weight"""
        font_files = [
            "./dist/Pennywort-Regular.ttf",
            "./dist/Pennywort-Bold.ttf",
        ]

        for path in font_files:
            font = fontforge.open(path)

            print()
            print(font.fullname)
            print("EN:", calc_weight(font, ord("l")))
            print("JP:", calc_weight(font, ord("し"), 2 / 3))


if __name__ == "__main__":
    unittest.main()
