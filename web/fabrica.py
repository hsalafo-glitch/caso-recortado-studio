"""La fábrica: guion (JSON) → short_w_<slug>.py → voz gratuita → render. Reutiliza lote14 y el motor."""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # /home/user
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from entorno import datos  # noqa: E402
CASOS = datos("casos")
SCRIPTS = datos("generados")

PLANTILLA = '''import json, os, sys
sys.path.insert(0, {raiz!r})
os.chdir({raiz!r})
import lote14
lote14.registrar({slug!r}, json.load(open({json!r}, encoding="utf-8")))
globals().update(lote14.cargar({slug!r}))

if __name__ == "__main__":
    import generar_short as g
    configurar()
    g.main()
'''


def preparar(slug, caso: dict):
    """Guarda el caso y escribe el script del short. Devuelve la ruta del script."""
    os.makedirs(CASOS, exist_ok=True)
    os.makedirs(SCRIPTS, exist_ok=True)
    pj = os.path.join(CASOS, f"{slug}.json")
    with open(pj, "w", encoding="utf-8") as f:
        json.dump(caso, f, ensure_ascii=False, indent=1)
    ps = os.path.join(SCRIPTS, f"short_w_{slug.replace('-', '_')}.py")
    with open(ps, "w", encoding="utf-8") as f:
        f.write(PLANTILLA.format(raiz=RAIZ, slug=slug, json=pj))
    return ps


def fabricar(script, log, paso=lambda texto: None, voz="narrador"):
    """Voz + render. Escribe la salida en log y llama a paso() al empezar cada fase.
    voz: una de voces.VOCES (la del dueño del canal nunca se usa para clientes)."""
    import voces
    entorno = dict(os.environ, VOZ_MOTOR="qwen", VOZ_QWEN=voces.valida(voz), CR_RAPIDO="1")
    fases = [("Grabando la voz", [sys.executable, "voz_gratis.py", script]),
             ("Animando el vídeo", [sys.executable, script])]
    with open(log, "a", encoding="utf-8") as f:
        for nombre, cmd in fases:
            paso(nombre)
            f.write(f"\n== {nombre}: {' '.join(cmd)}\n")
            f.flush()
            r = subprocess.run(cmd, cwd=RAIZ, stdout=f, stderr=subprocess.STDOUT, env=entorno)
            if r.returncode:
                raise RuntimeError(f"Falló «{nombre}» (mira {log})")
