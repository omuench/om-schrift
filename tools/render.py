"""Glyphen per Name aus einer TTF als PNG rendern (zur Sichtprüfung).
Aufruf: python3 render.py font.ttf out.png glyph1 glyph2 ...  (Gruppen mit '|' trennen = neue Zeile)
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch


class MplPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.v, self.c = [], []
    def _moveTo(self, p): self.v.append(p); self.c.append(Path.MOVETO)
    def _lineTo(self, p): self.v.append(p); self.c.append(Path.LINETO)
    def _curveToOne(self, a, b, p):
        self.v += [a, b, p]; self.c += [Path.CURVE4] * 3
    def _qCurveToOne(self, a, p):
        self.v += [a, p]; self.c += [Path.CURVE3] * 2
    def _closePath(self): self.v.append((0, 0)); self.c.append(Path.CLOSEPOLY)


def render(fontpath, out, names):
    f = TTFont(fontpath)
    gs = f.getGlyphSet()
    rows, row = [], []
    for n in names:
        if n == "|":
            rows.append(row); row = []
        else:
            row.append(n)
    rows.append(row)
    fig, ax = plt.subplots(figsize=(14, 2.2 * len(rows)))
    y = 0; maxx = 0
    for r in rows:
        x = 0
        for n in r:
            pen = MplPen(gs)
            gs[n].draw(pen)
            if pen.v:
                verts = [(vx + x, vy + y) for vx, vy in pen.v]
                ax.add_patch(PathPatch(Path(verts, pen.c), fc="black", ec="none"))
            ax.text(x, y - 330, n, fontsize=7, color="gray")
            x += gs[n].width + 60
        maxx = max(maxx, x)
        y -= 1400
    ax.axhline(0, color="#ccc", lw=0.5)
    ax.set_xlim(-50, max(maxx, 2500)); ax.set_ylim(y + 1400 - 450, 1050)
    ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(out, dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3:])
