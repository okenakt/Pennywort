import argparse

import fontforge
from fontforge import font as Font

CELL_SIZE = 48
NUM_COLUMNS = 16

sample_sentences = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "あいうえおぱぴぷぺぽ",
    "アイウエオパピプペポ",
    "[]{}()<>=+-*/\|!?@#$%^&_,.:;'\"",
    "　 全角スペース",
    "Boost your 開発効率 by using a beautiful フォント designed for プログラミング.",
]

head_template = "\n".join(
    [
        "{indent}<head>",
        "{indent}  <meta charset='UTF-8' />",
        "{indent}  <style>",
        "{indent}    @font-face {{",
        "{indent}      font-family: '{font_family}';",
        "{indent}      src: url('{font_path}');",
        "{indent}    }}",
        "{indent}    body {{",
        "{indent}      font-family: '{font_family}';",
        "{indent}    }}",
        "{indent}    h1, h2 {{",
        "{indent}      margin: 0px;",
        "{indent}    }}",
        "{indent}    .p-4 {{",
        "{indent}      padding: 1rem;",
        "{indent}    }}",
        "{indent}  </style>",
        "{indent}</head>",
    ]
)

table_style_template = "\n".join(
    [
        "{indent}<style>",
        "{indent}  td {{",
        "{indent}    padding-top: 4px;",
        "{indent}    padding-bottom: 4px;",
        "{indent}  }}",
        "{indent}  .glyph-container {{",
        "{indent}    position: relative;",
        "{indent}    width: {font_size}px;",
        "{indent}    height: {font_size}px;",
        "{indent}    border-left: 1px solid gray;",
        "{indent}    border-right: 1px solid gray;",
        "{indent}  }}",
        "{indent}  .glyph {{",
        "{indent}    margin: 0px auto;",
        "{indent}    line-height: {font_size}px;",
        "{indent}    font-size: {font_size}px;",
        "{indent}    text-align: center;",
        "{indent}  }}",
        "{indent}  .font-metrics {{",
        "{indent}    position: absolute;",
        "{indent}    inset: 0px;",
        "{indent}    width: {font_size}px;",
        "{indent}    z-index: -1;",
        "{indent}  }}",
        "{indent}  .baseline {{",
        "{indent}    top: {baseline}px;",
        "{indent}    border-top: 1px solid gray;",
        "{indent}  }}",
        "{indent}  .ascent {{",
        "{indent}    top: 0px;",
        "{indent}    border-top: 1px solid green;",
        "{indent}  }}",
        "{indent}  .descent {{",
        "{indent}    top: {font_size}px;",
        "{indent}    border-top: 1px solid red;",
        "{indent}  }}",
        "{indent}  .width {{",
        "{indent}    margin: 0px auto;",
        "{indent}    height: {font_size}px;",
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
        "{indent}    <div class='font-metrics baseline'></div>",
        "{indent}    <div class='font-metrics ascent'></div>",
        "{indent}    <div class='font-metrics descent'></div>",
        "{indent}    <div class='font-metrics width' style='width: {width}px; border-width: {border_width}px;'></div>",
        "{indent}    <div class='glyph'>{text}</div>",
        "{indent}  </div>",
        "{indent}</td>",
    ]
)


def create_glyph_table(font: Font, font_size: float, indent: str = "") -> str:
    scale = font_size / font.em
    table_lines = [
        f"{indent}<table>",
        table_style_template.format(
            indent=f"{indent}  ",
            font_size=font_size,
            baseline=font.ascent * scale,
        ),
    ]

    glyphs = sorted(
        [
            glyph
            for glyph in font.glyphs()
            if glyph.isWorthOutputting and glyph.unicode >= 0
        ],
        key=lambda glyph: glyph.unicode,
    )

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
                indent="        ",
                label=hex(glyph.unicode),
                text=f"&#{glyph.encoding};",
                width=glyph.width * scale,
                border_width=1,
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
                head_template.format(
                    indent="  ",
                    font_family=font.fontname,
                    font_path=font_path,
                ),
                "  <body>",
                "    <h1>{title}</h1>".format(title=font.fullname),
                "    <div class='p-4'>",
                "    <div class='p-4'>",
                "      <h2>Samples</h2>",
                "      <div class='p-4'>",
                *[f"        <div>{sentense}</div>" for sentense in sample_sentences],
                "      </div>",
                "    </div>",
                "    <div class='p-4'>",
                "      <h2>All Glyphs</h2>",
                "      <div class='p-4'>",
                create_glyph_table(font, CELL_SIZE, indent="        "),
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
