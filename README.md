# OM Sans (Arbeitsname)

Prototyp einer eigenen Hausschrift, abgeleitet von Montserrat (SIL Open Font License 1.1, siehe OFL.txt).

## Änderungen gegenüber Montserrat (Probe 6)
1. l mit kleinem Bogen am Fuß als Standard (aus Montserrats ss01, Bogen verkleinert, rechts mehr Luft). I bleibt schlicht.
2. Ziffer 1 mit schrägem Aufstrich (deutsche Form), auch bei den Mediävalziffern.
3. Ligaturen (Feature `liga`, standardmäßig an): `t_t`, `t_z`.
4. Stilsets (optional):
   - `ss02` Schluss-z: z, tz, rz am Wortende mit Unterlänge (ʒ); rz wird nur hier verbunden
   - `ss03` rz auch im Wortinneren verbinden
   - `ss04` ß-Variante B; `cv01` wählt zwischen den ß-Varianten A, B, C (Wert 1, 2, 3)
   - `ss05` ck- und ch-Ligatur (unten verbunden, experimentell)
5. Anführungszeichen und Apostroph als schräge Keile.

## Verwendung im CSS

```css
@font-face { font-family: "OM Sans"; font-weight: 400; src: url(/fonts/OMSans-Regular.woff2) format("woff2"); }
@font-face { font-family: "OM Sans"; font-weight: 600; src: url(/fonts/OMSans-SemiBold.woff2) format("woff2"); }

body { font-family: "OM Sans", sans-serif; }

/* Mediävalziffern im Fließtext, normale Ziffern in Tabellen, Preisen, Überschriften */
p, li { font-variant-numeric: oldstyle-nums; }
table, .preis, h1, h2, h3 { font-variant-numeric: lining-nums tabular-nums; }

/* Browser schalten Ligaturen ab, sobald letter-spacing gesetzt ist: dann ausdrücklich einschalten */
h1, h2, h3 { letter-spacing: -0.01em; font-feature-settings: "liga" 1; }

/* Stilsets gezielt einsetzen, z. B. Schluss-z nur in Überschriften */
h1, h2 { font-feature-settings: "liga" 1, "ss02" 1; }
```

### Ligaturen gezielt aufbrechen
Wie `\/` in LaTeX: In HTML trennt der Zero Width Non-Joiner jede Ligatur, z. B. `Auf&zwnj;trag` oder `er&zwnj;zählen`.

## Bauen
    pip install fonttools skia-pathops brotli
    python3 tools/build.py src/Montserrat-Regular.ttf fonts/OMSans-Regular.ttf Regular
    python3 tools/build.py src/Montserrat-SemiBold.ttf fonts/OMSans-SemiBold.ttf SemiBold

Der Prototyp verändert die fertigen TTF-Dateien. Für alle Gewichte und die Kursive wird der nächste Schritt auf die Glyphs-Quellen von Montserrat umgestellt.
