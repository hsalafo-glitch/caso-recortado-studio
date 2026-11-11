#!/usr/bin/env python3
"""Fotogramas de revisión de un short: uno a mitad de cada escena y otro 0,4 s después de cada
evento o rótulo, más una hoja de contactos (hoja.png) para verlos todos de un vistazo.

Uso:
    python fotogramas.py short_<nombre>.py            # con la voz real si ya está en caché
    python fotogramas.py short_<nombre>.py --prueba   # con tiempos aproximados
Salida: salida/revision-<SLUG>/
"""
import importlib.util
import os
import sys

from PIL import Image

try:
    import motor_short as g
except ImportError:          # proyectos antiguos: el motor se llama generar_short.py
    import generar_short as g


def cargar(path):
    spec = importlib.util.spec_from_file_location("short_mod", os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    path = sys.argv[1]
    prueba = "--prueba" in sys.argv
    s = cargar(path)
    s.configurar()
    n = None if prueba else g.narracion_cacheada()
    tl = g.build_timeline_narracion(*n) if n else g.build_timeline(True)
    r = g.Renderer(tl)
    momentos = []
    for seg in tl["segs"]:
        momentos.append((f"escena-{seg['name']}", (seg["t0"] + seg["t1"]) / 2))
    for b in tl["bloques"]:
        for k, v in b["eventos_t"].items():
            momentos.append((f"{b['id']}-{k}", v + 0.4))
        for ts, txt in b["pantalla_t"]:
            momentos.append((f"{b['id']}-rotulo", ts + 0.5))
    momentos.sort(key=lambda x: x[1])
    out = os.path.join(g.OUT_DIR, f"revision-{g.SALIDA}")
    os.makedirs(out, exist_ok=True)
    thumbs = []
    for i, (name, t) in enumerate(momentos):
        t = min(max(0.0, t), tl["total"] - 0.05)
        p = os.path.join(out, f"{i:02d}_{t:05.1f}s_{name}.png")
        r.render(t).write_to_png(p)
        thumbs.append(Image.open(p).resize((270, 480)))
    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (270 * cols, 480 * rows), (20, 20, 20))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    sheet.save(os.path.join(out, "hoja.png"))
    print(f"✔ {len(thumbs)} fotogramas en {out} (hoja de contactos: hoja.png)")


if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    main()
