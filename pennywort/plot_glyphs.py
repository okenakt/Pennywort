import matplotlib.pyplot as plt
from fontforge import glyph as Glyph
from fontTools.pens.basePen import BasePen
from matplotlib.patches import PathPatch as MplPathPatch
from matplotlib.patches import Rectangle
from matplotlib.path import Path as MplPath

Point = tuple[float, float]


class MplPathPen(BasePen):
    def __init__(self) -> None:
        self.__currentPoint = None
        self._path: list = []

    def _moveTo(self, pt: Point) -> None:
        self._path.append((MplPath.MOVETO, pt))

    def _lineTo(self, pt: Point) -> None:
        self._path.append((MplPath.LINETO, pt))

    def _curveToOne(self, p1: Point, p2: Point, p3: Point) -> None:
        self._path.append((MplPath.CURVE4, p1))
        self._path.append((MplPath.CURVE4, p2))
        self._path.append((MplPath.CURVE4, p3))

    def _closePath(self) -> None:
        self._path.append((MplPath.CLOSEPOLY, (0, 0)))

    def getPath(self) -> MplPath | None:
        if len(self._path) == 0:
            return None

        codes, vertices = zip(*self._path)
        return MplPath(vertices, codes)


def plot_glyphs(glyph_matrix: list[list[Glyph | None]]) -> None:
    nrows = len(glyph_matrix)
    ncols = max([len(row) for row in glyph_matrix])
    fig, axes = plt.subplots(nrows, ncols)

    max_width = 0
    max_ascent = 0
    max_descent = 0
    for i in range(nrows):
        for j in range(ncols):
            if j >= len(glyph_matrix[i]) or glyph_matrix[i][j] is None:
                continue

            ax = axes if ncols == 1 else axes[j] if nrows == 1 else axes[i, j]

            glyph: Glyph = glyph_matrix[i][j]
            width = glyph.width
            ascent = glyph.font.ascent
            descent = glyph.font.descent

            pen = MplPathPen()
            glyph.draw(pen)
            glyph_path = pen.getPath()

            if glyph_path is not None:
                patch = MplPathPatch(glyph_path, facecolor="black", lw=1)
                ax.add_patch(patch)

            ax.add_patch(
                Rectangle(
                    (0, -descent),
                    width,
                    ascent + descent,
                    edgecolor="blue",
                    facecolor="none",
                    linewidth=1,
                )
            )

            ax.axvline(
                x=width / 2,
                color="black",
                alpha=0.2,
                linestyle=":",
            )  # Vertical half
            ax.axhline(
                y=ascent / 2,
                color="black",
                alpha=0.2,
                linestyle=":",
            )  # Horizontal half

            ax.axhline(y=0, color="black", linestyle="--")  # Baseline
            ax.axhline(y=ascent, color="green", linestyle="--")  # Ascent
            ax.axhline(y=-descent, color="red", linestyle="--")  # Descent

            max_width = max(width, max_width)
            max_ascent = max(ascent, max_ascent)
            max_descent = max(descent, max_descent)

    for i in range(nrows):
        for j in range(ncols):
            ax = axes if ncols == 1 else axes[j] if nrows == 1 else axes[i, j]

            if i != nrows - 1:
                ax.xaxis.set_ticklabels([])
            if j != 0:
                ax.yaxis.set_ticklabels([])

            ax.set_xlim(0, max_width)
            ax.set_ylim(-max_descent, max_ascent)
            ax.set_aspect("equal")

    plt.show()
