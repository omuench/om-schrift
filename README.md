# OM Sans (Arbeitsname)

Prototyp einer eigenen Hausschrift, abgeleitet von Montserrat (SIL Open Font License 1.1, siehe OFL.txt).

## Änderungen gegenüber Montserrat (Probe 2)
1. l mit kleinem Bogen am Fuß als Standard (aus Montserrats ss01, Bogen verkleinert, rechts mehr Luft). I bleibt schlicht.
2. Ziffer 1 mit schrägem Aufstrich (deutsche Form).
3. Ligaturen `t_t`, `t_z`, `r_z`, Feature `liga` (standardmäßig aktiv).
4. Schluss-z (`z.fina`, Form des ʒ) nur am Wortende, Stilset `ss02` (optional).

Hinweis für CSS: Browser schalten Ligaturen ab, sobald `letter-spacing` gesetzt ist. Dann zusätzlich
`font-feature-settings: "liga" 1;` setzen.

## Bauen
    pip install fonttools skia-pathops brotli
    python3 tools/build.py src/Montserrat-Regular.ttf fonts/OMSans-Regular.ttf Regular
    python3 tools/build.py src/Montserrat-SemiBold.ttf fonts/OMSans-SemiBold.ttf SemiBold

Der Prototyp verändert die fertigen TTF-Dateien. Für alle Gewichte und die Kursive wird der nächste Schritt auf die Glyphs-Quellen von Montserrat umgestellt.
