"""Probeseite aus Vorlage bauen: Fonts als base64 einbetten. Aufruf: python3 make_proof.py out/probe1.html"""
import base64
import sys

b = lambda p: base64.b64encode(open(p, "rb").read()).decode()
TEXT = '''<h2>Befähigung statt Abhängigkeit, kurz und klar erklärt</h2>
<p class="body">Ich begleite Teams in mittelständischen Unternehmen, bis neue Software im Alltag wirklich genutzt wird. Oft ist das Werkzeug längst da, aber es fehlt die Brücke zwischen Einführung und Gewohnheit.</p>
<p class="body">Im Mittelpunkt steht nicht die Technik, sondern das Netz aus Menschen, Rollen und Routinen. Dort entscheidet sich, ob aus „eingeführt“ irgendwann „gelebt“ wird. Ein kurzer Blick zurück zeigt meist, woran es hakt.</p>
<p class="body">Seit 2022 begleite ich Unternehmen mit 50 bis 500 Mitarbeitenden. Ist das realistisch? Meistens schon, wenn alle mitziehen und der Nutzen spürbar ist. Mit freundlichem Gruß aus Dresden.</p>'''

t = open("tools/proof_template.html", encoding="utf-8").read()
for key, path in {"__REG__": "out/OMSans-Regular.woff2", "__SEMI__": "out/OMSans-SemiBold.woff2",
                  "__MREG__": "out/Montserrat-Regular.woff2", "__MSEMI__": "out/Montserrat-SemiBold.woff2"}.items():
    t = t.replace(key, b(path))
t = t.replace("__TEXT__", TEXT)
open(sys.argv[1], "w", encoding="utf-8").write(t)
print("ok", sys.argv[1])
