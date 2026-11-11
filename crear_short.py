"""Guion (JSON con la forma de web/guionista.py → Guion) → short terminado. Sin web y sin API.

    python crear_short.py guion.json --prueba   # revisa el guion + fotogramas sin voz (salida/revision-<slug>/hoja.png)
    python crear_short.py guion.json            # voz gratuita + render → salida/<slug>.mp4 y miniatura
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "web"))
import fabrica  # noqa: E402
import guionista  # noqa: E402


def main():
    ruta = next(a for a in sys.argv[1:] if a.endswith(".json"))
    g = guionista.Guion.model_validate(json.load(open(ruta, encoding="utf-8")))
    err = guionista.revisar(g)
    if err:
        print("✘ El guion tiene problemas:\n  - " + "\n  - ".join(err))
        sys.exit(1)
    palabras = sum(len(b.voz.split()) for b in g.bloques)
    print(f"✔ guion correcto: {palabras} palabras, {sum(len(b.escenas) for b in g.bloques)} escenas")
    script = fabrica.preparar(g.slug, guionista.a_lote14(g))
    py = sys.executable
    if "--prueba" in sys.argv:
        subprocess.run([py, "fotogramas.py", script, "--prueba"], cwd=AQUI, check=True)
        return
    for cmd in ([py, "voz_gratis.py", script], [py, script], [py, "fotogramas.py", script]):
        subprocess.run(cmd, cwd=AQUI, check=True)
    print(f"✔ salida/{g.slug}.mp4\n  Título: {g.titulo_youtube}\n  Descripción: {g.descripcion}")


if __name__ == "__main__":
    main()
