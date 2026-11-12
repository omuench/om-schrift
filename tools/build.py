"""Baut den Prototyp "OM Sans" aus Montserrat (OFL) per Code.

Änderungen:
  1. I und l: die Alternativformen aus Montserrats Stilset ss01 (I mit Querstrichen,
     l mit Bogen) werden zur Standardform (cmap zeigt direkt auf die .ss01-Glyphen).
  2. tt-Ligatur (t_t): zwei t mit durchgehendem Querbalken, Feature 'liga' (standardmäßig an).
  3. Schluss-z (z.fina, Form des ʒ): nur am Wortende, im Stilset ss02 (optional).
  4. Umbenennung in "OM Sans" (Arbeitsname).

Aufruf: python3 build.py <quelle.ttf> <ziel.ttf> <Stilname>
"""
import copy
import sys

from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib.tables import otTables
import pathops

FAMILY = "OM Sans"


def outline(gs, name, dx=0):
    """Glyph als pathops.Path, optional horizontal verschoben."""
    path = pathops.Path()
    pen = path.getPen(glyphSet=gs)
    gs[name].draw(TransformPen(pen, (1, 0, 0, 1, dx, 0)))
    return path


def to_glyph(path, gs):
    tt = TTGlyphPen(gs)
    # pathops liefert kubische Kurven; in Quadratik umwandeln für glyf
    from fontTools.pens.cu2quPen import Cu2QuPen
    path.draw(Cu2QuPen(tt, max_err=1.0, reverse_direction=False))
    return tt.glyph()


def add_glyph(font, name, glyph, width, lsb):
    font["glyf"][name] = glyph
    font["hmtx"][name] = (width, lsb)
    order = font.getGlyphOrder()
    if name not in order:
        font.setGlyphOrder(order + [name])
        font["maxp"].numGlyphs = len(font.getGlyphOrder())


def crossbar(gs):
    """Querbalken des t aus der Kontur bestimmen: linkes Ende = Punkte mit minimalem x."""
    rec = RecordingPen()
    gs["t"].draw(rec)
    pts = [p for op, args in rec.value for p in args]
    xmin = min(x for x, _ in pts)
    ys = sorted({y for x, y in pts if x == xmin})
    y0, y1 = ys[0], ys[-1]
    xr = max(x for x, y in pts if y in (y0, y1))
    return xmin, xr, y0, y1


def make_tt(font):
    gs = font.getGlyphSet()
    w = gs["t"].width
    xl, xr, y0, y1 = crossbar(gs)
    p = outline(gs, "t")
    p2 = outline(gs, "t", dx=w)
    bridge = pathops.Path()
    bridge.moveTo(xr - 5, y0); bridge.lineTo(w + xl + 5, y0)
    bridge.lineTo(w + xl + 5, y1); bridge.lineTo(xr - 5, y1); bridge.close()
    merged = pathops.op(pathops.op(p, p2, pathops.PathOp.UNION), bridge, pathops.PathOp.UNION)
    g = to_glyph(merged, gs)
    g.recalcBounds(font["glyf"])
    add_glyph(font, "t_t", g, 2 * w, g.xMin)


def make_lig(font, left, right, name, tighten=20):
    """Ligatur aus zwei Glyphen, verbunden auf Höhe des t-Querbalkens (= Oberkante z)."""
    gs = font.getGlyphSet()
    _, _, y0, y1 = crossbar(gs)
    w = gs[left].width - tighten
    a = outline(gs, left)
    b = outline(gs, right, dx=w)
    # rechtes Ende des linken Glyphen auf Balkenhöhe, linkes Ende des rechten
    def ends(name, dx):
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        rec = DecomposingRecordingPen(gs); gs[name].draw(rec)
        pts = [(x + dx, y) for op, args in rec.value for (x, y) in args]
        band = [x for x, y in pts if y0 - 10 <= y <= y1 + 10]
        return min(band), max(band)
    _, ar = ends(left, 0)
    bl, _ = ends(right, w)
    bridge = pathops.Path()
    bridge.moveTo(ar - 8, y0); bridge.lineTo(bl + 8, y0)
    bridge.lineTo(bl + 8, y1); bridge.lineTo(ar - 8, y1); bridge.close()
    merged = pathops.op(pathops.op(a, b, pathops.PathOp.UNION), bridge, pathops.PathOp.UNION)
    g = to_glyph(merged, gs)
    g.recalcBounds(font["glyf"])
    add_glyph(font, name, g, w + gs[right].width, g.xMin)


def german_one(font):
    """Ziffer 1 mit schrägem Aufstrich statt waagerechter Fahne."""
    gs = font.getGlyphSet()
    rec = RecordingPen(); gs["one"].draw(rec)
    pts = [p for op, args in rec.value for p in args]
    xs = sorted({x for x, y in pts}); top = max(y for x, y in pts)
    flag_low = sorted({y for x, y in pts})[1]          # Unterkante der alten Fahne
    thick = top - flag_low
    sl, sr = xs[-2], xs[-1]                            # Stamm links/rechts
    stem = pathops.Path()
    stem.moveTo(sl, 0); stem.lineTo(sr, 0); stem.lineTo(sr, top); stem.lineTo(sl, top); stem.close()
    # Aufstrich: Band von der Stammspitze schräg nach links unten
    import math
    tip = (xs[0] - 70, top - 0.42 * top)   # länger und flacher als Probe 2
    p0 = (sr, top)
    dx, dy = tip[0] - p0[0], tip[1] - p0[1]
    L = math.hypot(dx, dy); nx, ny = dy / L, -dx / L
    if ny > 0: nx, ny = -nx, -ny                       # Normale nach rechts unten
    t = thick * 1.05
    flag = pathops.Path()
    flag.moveTo(*p0); flag.lineTo(*tip)
    flag.lineTo(tip[0] + nx * t, tip[1] + ny * t); flag.lineTo(p0[0] + nx * t, p0[1] + ny * t); flag.close()
    # Beschnitt: unterhalb der Oberkante des Aufstrichs und links vom rechten Stammrand
    far = (p0[0] + 3 * dx, p0[1] + 3 * dy)
    clip = pathops.Path()
    clip.moveTo(*p0); clip.lineTo(*far); clip.lineTo(far[0], -10); clip.lineTo(sr, -10); clip.close()
    merged = pathops.op(pathops.op(stem, flag, pathops.PathOp.UNION), clip, pathops.PathOp.INTERSECTION)
    # nach rechts verschieben, damit links wieder der ursprüngliche Vorbreitenabstand steht
    adv, lsb0 = font["hmtx"]["one"]
    bounds = merged.bounds
    shift = lsb0 - bounds[0]
    from fontTools.pens.cu2quPen import Cu2QuPen
    tt = TTGlyphPen(gs)
    merged.draw(TransformPen(Cu2QuPen(tt, max_err=1.0, reverse_direction=False), (1, 0, 0, 1, shift, 0)))
    g = tt.glyph(); g.recalcBounds(font["glyf"])
    font["glyf"]["one"] = g
    font["hmtx"]["one"] = (int(round(adv + shift)), g.xMin)


def smaller_l_tail(font, factor=0.7, rsb=50):
    """Bogen am Fuß des l verkleinern und rechts mehr Luft geben."""
    from fontTools.pens.recordingPen import RecordingPen
    gs = font.getGlyphSet()
    rec = RecordingPen(); gs["l.ss01"].draw(rec)
    pts = [p for op, args in rec.value for p in args]
    stem_r = sorted({x for x, y in pts if y > 600})[-1]
    tt = TTGlyphPen(gs)
    for op, args in rec.value:
        new = [((stem_r + (x - stem_r) * factor) if x > stem_r else x, y) for x, y in args]
        getattr(tt, op)(*new)
    g = tt.glyph(); g.recalcBounds(font["glyf"])
    font["glyf"]["l.ss01"] = g
    font["hmtx"]["l.ss01"] = (g.xMax + rsb, g.xMin)


def make_zfina(font):
    gs = font.getGlyphSet()
    src = font.getBestCmap()[0x0292]  # ʒ
    g = copy.deepcopy(font["glyf"][src])
    add_glyph(font, "z.fina", g, *font["hmtx"][src])


def default_alternates(font):
    cmap_tables = [t for t in font["cmap"].tables if t.isUnicode()]
    order = set(font.getGlyphOrder())
    for t in cmap_tables:
        for cp, name in list(t.cmap.items()):
            if name[:1] == "l" and not name.startswith("longs") and name + ".ss01" in order:
                t.cmap[cp] = name + ".ss01"


def merge_gsub(font, fea):
    """Neue Features in einer Kopie kompilieren und ihre Lookups ins bestehende GSUB übernehmen,
    damit Montserrats eigene Features erhalten bleiben."""
    tmp = copy.deepcopy(font)
    del tmp["GSUB"]
    addOpenTypeFeaturesFromString(tmp, fea, tables=["GSUB"])
    src, dst = tmp["GSUB"].table, font["GSUB"].table
    off = len(dst.LookupList.Lookup)
    for lk in src.LookupList.Lookup:
        for st in lk.SubTable:
            for rec in getattr(st, "SubstLookupRecord", []) or []:
                rec.LookupListIndex += off
            for cr in getattr(st, "ChainSubRuleSet", []) or []:
                pass
        dst.LookupList.Lookup.append(lk)
    dst.LookupList.LookupCount = len(dst.LookupList.Lookup)
    for fr in src.FeatureList.FeatureRecord:
        idx = [i + off for i in fr.Feature.LookupListIndex]
        existing = [r for r in dst.FeatureList.FeatureRecord if r.FeatureTag == fr.FeatureTag]
        if existing:
            for r in existing:
                r.Feature.LookupListIndex += idx
                r.Feature.LookupCount = len(r.Feature.LookupListIndex)
        else:
            nr = otTables.FeatureRecord()
            nr.FeatureTag = fr.FeatureTag
            nr.Feature = otTables.Feature()
            nr.Feature.FeatureParams = None
            nr.Feature.LookupListIndex = idx
            nr.Feature.LookupCount = len(idx)
            dst.FeatureList.FeatureRecord.append(nr)
            new_i = len(dst.FeatureList.FeatureRecord) - 1
            for sr in dst.ScriptList.ScriptRecord:
                langs = [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]
                for ls in langs:
                    if ls is not None:
                        ls.FeatureIndex.append(new_i)
                        ls.FeatureCount = len(ls.FeatureIndex)
    dst.FeatureList.FeatureCount = len(dst.FeatureList.FeatureRecord)
    # FeatureList muss nach Tag sortiert sein: neu sortieren und Indizes umschreiben
    recs = dst.FeatureList.FeatureRecord
    order = sorted(range(len(recs)), key=lambda i: recs[i].FeatureTag)
    remap = {old: new for new, old in enumerate(order)}
    dst.FeatureList.FeatureRecord = [recs[i] for i in order]
    for sr in dst.ScriptList.ScriptRecord:
        langs = [sr.Script.DefaultLangSys] + [l.LangSys for l in sr.Script.LangSysRecord]
        for ls in langs:
            if ls is not None:
                ls.FeatureIndex = sorted(remap[i] for i in ls.FeatureIndex)
                if ls.ReqFeatureIndex != 0xFFFF:
                    ls.ReqFeatureIndex = remap[ls.ReqFeatureIndex]


FEA = """
@BUCHSTABE = [a-z A-Z adieresis odieresis udieresis Adieresis Odieresis Udieresis germandbls
              I.ss01 l.ss01 t_t t_z r_z z.fina t_z.fina r_z.fina];
lookup TT { sub t t by t_t; sub t z by t_z; sub r z by r_z; } TT;
feature liga { lookup TT; } liga;
lookup ZFINA_SUB { sub z by z.fina; sub t_z by t_z.fina; sub r_z by r_z.fina; } ZFINA_SUB;
feature ss02 {
    featureNames { name "Schluss-z"; };
    ignore sub [z t_z r_z]' @BUCHSTABE;
    sub [z t_z r_z]' lookup ZFINA_SUB;
} ss02;
"""


def rename(font, style):
    name = font["name"]
    ps = FAMILY.replace(" ", "") + "-" + style.replace(" ", "")
    vals = {1: FAMILY, 2: "Regular", 3: f"0.1;OM;{ps}", 4: f"{FAMILY} {style}",
            6: ps, 16: FAMILY, 17: style}
    if style != "Regular":
        vals[1] = f"{FAMILY} {style}"
        vals[2] = "Regular"
    for rec in list(name.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    for nid, v in vals.items():
        name.setName(v, nid, 3, 1, 0x409)
        name.setName(v, nid, 1, 0, 0)
    name.setName("Prototyp, abgeleitet von Montserrat (SIL OFL 1.1). Arbeitsname.", 10, 3, 1, 0x409)


def main(src, dst, style):
    font = TTFont(src)
    default_alternates(font)
    smaller_l_tail(font)
    german_one(font)
    make_tt(font)
    make_lig(font, "t", "z", "t_z", tighten=0)
    make_lig(font, "r", "z", "r_z")
    make_zfina(font)
    make_lig(font, "t", "z.fina", "t_z.fina", tighten=-30)
    make_lig(font, "r", "z.fina", "r_z.fina", tighten=-30)
    merge_gsub(font, FEA)
    rename(font, style)
    font.save(dst)
    w = TTFont(dst)
    w.flavor = "woff2"
    w.save(dst.replace(".ttf", ".woff2"))
    print("ok", dst)


if __name__ == "__main__":
    main(*sys.argv[1:4])
