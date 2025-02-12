import argparse

import fontforge
from fontforge import font as Font

CELL_SIZE = 48
NUM_COLUMNS = 16
SAMPLE_FG_COLOR = "#D8D8D8"
SAMPLE_BG_COLOR = "#181818"
DEEP_SKY_BLUE_3 = "#0087AF"
GREY_19 = "#303030"
GREY_35 = "#585858"
GREY_74 = "#BCBCBC"
GREY_82 = "#D0D0D0"

sample_sentences = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "あいうえおぱぴぷぺぽ",
    "アイウエオパピプペポ",
    "[]{}()<>=+-*/\|!?@#$%^&_,.:;'\"",
    "0O 1Il| mrn 　←全角スペース",
    "Boost your 開発効率 by using a beautiful フォント designed for プログラミング.",
    "".join(  # powerline
        [
            f"<span style='background-color: {DEEP_SKY_BLUE_3}; color: white;'> root </span>",
            f"<span style='background-color: {GREY_19};'>",
            f"<span style='color: {DEEP_SKY_BLUE_3};'></span>",
            f"<span style='color: {GREY_74};'>  main </span>",
            "</span>",
            f"<span style='background-color: {GREY_35};'>",
            f"<span style='color: {GREY_19};'></span>",
            f"<span style='color: {GREY_74};'> ~  </span>",
            f"<span style='color: {GREY_82};'>Powerline Ready </span>",
            "</span>",
            f"<span style='color: {GREY_35};'></span>",
        ]
    ),
]

style_template = "\n".join(
    [
        "{indent}<style>",
        "{indent}  @font-face {{",
        "{indent}    font-family: '{font_family}';",
        "{indent}    src: url('{font_path}');",
        "{indent}  }}",
        "{indent}  body {{",
        "{indent}    font-family: '{font_family}';",
        "{indent}  }}",
        "{indent}  h1, h2 {{",
        "{indent}    margin: 0;",
        "{indent}  }}",
        "{indent}  table {{",
        "{indent}    width: 100%;",
        "{indent}    border-spacing: 0;",
        "{indent}  }}",
        "{indent}  tr {{",
        "{indent}    display: flex;",
        "{indent}    justify-content: space-between;",
        "{indent}    padding-bottom: 8px;",
        "{indent}  }}",
        "{indent}  td {{",
        "{indent}    padding-left: 0;",
        "{indent}    padding-right: 0;",
        "{indent}  }}",
        "{indent}  .p-4 {{",
        "{indent}    padding: 1rem;",
        "{indent}  }}",
        "{indent}  .sample-container {{",
        "{indent}    color: {sample_foreground_color};",
        "{indent}    background-color: {sample_background_color};",
        "{indent}    margin: 1rem;",
        "{indent}    padding: 0.5rem;",
        "{indent}  }}",
        "{indent}  .glyph-container {{",
        "{indent}    position: relative;",
        "{indent}    width: {font_size};",
        "{indent}    height: {font_size};",
        "{indent}    border-left: 1px solid gray;",
        "{indent}    border-right: 1px solid gray;",
        "{indent}  }}",
        "{indent}  .glyph {{",
        "{indent}    margin: 0 auto;",
        "{indent}    line-height: {font_size};",
        "{indent}    font-size: {font_size};",
        "{indent}    text-align: center;",
        "{indent}  }}",
        "{indent}  .glyph-metrics {{",
        "{indent}    position: absolute;",
        "{indent}    inset: 0;",
        "{indent}    width: {font_size};",
        "{indent}    z-index: -1;",
        "{indent}  }}",
        "{indent}  .baseline {{",
        "{indent}    top: {baseline};",
        "{indent}    border-top: 1px solid gray;",
        "{indent}  }}",
        "{indent}  .ascent {{",
        "{indent}    top: 0;",
        "{indent}    border-top: 1px solid green;",
        "{indent}  }}",
        "{indent}  .descent {{",
        "{indent}    top: {font_size};",
        "{indent}    border-top: 1px solid red;",
        "{indent}  }}",
        "{indent}  .width {{",
        "{indent}    margin: 0 auto;",
        "{indent}    height: {font_size};",
        "{indent}    border-left: solid blue;",
        "{indent}    border-right: solid blue;",
        "{indent}  }}",
        "{indent}</style>",
    ]
)

td_template = "\n".join(
    [
        "{indent}<td>",
        "{indent}  <div>{label}</div>",
        "{indent}  <div class='glyph-container'>",
        "{indent}    <div class='glyph-metrics baseline'></div>",
        "{indent}    <div class='glyph-metrics ascent'></div>",
        "{indent}    <div class='glyph-metrics descent'></div>",
        "{indent}    <div class='glyph-metrics width' style='width: {width}; border-width: {border_width};'></div>",
        "{indent}    <div class='glyph'>{text}</div>",
        "{indent}  </div>",
        "{indent}</td>",
    ]
)


def create_glyph_table(font: Font, indent: str = "") -> str:
    glyphs = sorted(
        [
            glyph
            for glyph in font.glyphs()
            if glyph.isWorthOutputting and glyph.unicode >= 0
        ],
        key=lambda glyph: glyph.unicode,
    )

    table_lines = [f"{indent}<table>"]
    i = 0
    prev_unicode = None
    for glyph in glyphs:
        col_index = glyph.unicode % NUM_COLUMNS
        row_start = glyph.unicode - col_index

        # tail blank
        if prev_unicode and glyph.unicode - prev_unicode != 1:
            j = 1
            while i < NUM_COLUMNS and i != col_index:
                table_lines.append(
                    td_template.format(
                        indent=f"{indent}    ",
                        label=hex(prev_unicode + j),
                        text="&nbsp;",
                        width=0,
                        border_width=0,
                    )
                )
                i += 1
                j += 1

        # row end
        if i >= NUM_COLUMNS:
            table_lines.append(f"{indent}  </tr>")
            i = 0

        # row start
        if i == 0:
            table_lines.append(f"{indent}  <tr>")

        # head blank
        while i < col_index:
            table_lines.append(
                td_template.format(
                    indent=f"{indent}    ",
                    label=hex(row_start + i),
                    text="&nbsp;",
                    width=0,
                    border_width=0,
                )
            )
            i += 1

        # cuurent glyph
        table_lines.append(
            td_template.format(
                indent=f"{indent}    ",
                label=hex(glyph.unicode),
                text=f"&#{glyph.encoding};",
                width=f"{glyph.width / font.em * 100}%",
                border_width="1px",
            )
        )

        prev_unicode = glyph.unicode
        i += 1

    table_lines += [
        f"{indent}  </tr>",
        f"{indent}</table>",
    ]

    return "\n".join(table_lines)


def export_html(font_path: str) -> None:
    font = fontforge.open(font_path)

    print(
        "\n".join(
            [
                "<!DOCTYPE html>",
                "<html lang='en'>",
                "<head>",
                "  <meta charset='UTF-8' />",
                style_template.format(
                    indent="  ",
                    font_family=font.fontname,
                    font_path=font_path,
                    font_size=f"{CELL_SIZE}px",
                    baseline=f"{font.ascent / font.em * 100}%",
                    sample_foreground_color=SAMPLE_FG_COLOR,
                    sample_background_color=SAMPLE_BG_COLOR,
                ),
                "  <body>",
                "    <h1>{title}</h1>".format(title=font.fullname),
                "    <div class='p-4'>",
                "    <div class='p-4'>",
                "      <h2>Samples</h2>",
                "      <div class='sample-container'>",
                *[f"        <div>{sentense}</div>" for sentense in sample_sentences],
                "      </div>",
                "    </div>",
                "    <div class='p-4'>",
                "      <h2>All Glyphs</h2>",
                "      <div class='p-4'>",
                create_glyph_table(font, indent="        "),
                "      </div>",
                "    </div>",
                "    </div>",
                "  </body>",
                "</html>",
            ]
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export font preview as html.",
        usage="python export_html.py /path/to/font/file",
    )
    parser.add_argument("font_file", type=str, help="Path to font.ttf.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_html(args.font_file)
