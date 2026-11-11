"""Obrero: hace los vídeos de la cola de uno en uno. Se ejecuta aparte de la web:

    python web/worker.py            (en el servidor lo arranca systemd: ver despliegue/)

Coge el trabajo más antiguo «en cola», lo marca como suyo de forma atómica (así nunca lo hacen dos procesos),
escribe el guion, graba la voz, anima el vídeo y, si es del plan gratis, le pone la marca de agua.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from entorno import cargar_env, datos  # noqa: E402

cargar_env()                     # antes de importar db, para que respete CR_DB de web/.env
import db  # noqa: E402
import fabrica  # noqa: E402
import guionista  # noqa: E402
DEMO = os.environ.get("CR_DEMO") == "1"
SALIDA = datos("salida") if os.environ.get("CR_DATOS") else os.path.join(fabrica.RAIZ, "salida")
LOGS = datos("logs")
MARCA = "Hecho con Caso Recortado Studio"


def fuente():
    """Ruta de la fuente del motor (Inter Display Black), para la marca de agua."""
    for p in (os.path.join(AQUI, "..", "fuentes", "InterDisplay-Black.otf"),
              "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"):
        if os.path.exists(p):
            return os.path.abspath(p)
    r = subprocess.run(["fc-match", "-f", "%{file}", "Inter Display:black"], capture_output=True, text=True)
    return r.stdout.strip()


def poner_marca(mp4):
    """Marca de agua abajo, por debajo de los subtítulos (que van en y≈1505): no tapa nada importante."""
    tmp = mp4 + ".marca.mp4"
    f = fuente().replace(":", r"\:")
    vf = (f"drawbox=x=(iw-560)/2:y=1700:w=560:h=70:color=black@0.55:t=fill,"
          f"drawtext=fontfile='{f}':text='{MARCA}':fontsize=32:fontcolor=white@0.92:x=(w-text_w)/2:y=1722")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", vf, "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, mp4)


def guion_demo(tema):
    """Modo demo (sin IA): elige el ejemplo de web/ejemplos/ que más se parezca al tema."""
    d = os.path.join(AQUI, "ejemplos")
    ejemplos = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    tema = tema.lower()
    elegido = next((f for f in ejemplos if any(w[:6] in tema for w in f[:-5].split("-"))), ejemplos[0])
    return json.load(open(os.path.join(d, elegido), encoding="utf-8"))


def actualizar(tid, **k):
    with db.conectar() as c:
        c.execute(f"UPDATE trabajos SET {', '.join(f'{x}=?' for x in k)} WHERE id=?", (*k.values(), tid))


def coger():
    """Reserva el siguiente trabajo en cola. Devuelve la fila o None."""
    with db.conectar() as c:
        fila = c.execute("SELECT * FROM trabajos WHERE estado='en cola' ORDER BY inicio LIMIT 1").fetchone()
        if not fila:
            return None
        n = c.execute("UPDATE trabajos SET estado='trabajando', paso='Escribiendo el guion' WHERE id=? AND estado='en cola'",
                      (fila["id"],)).rowcount
        return fila if n else None


def escribir_guion(t):
    """Guion nuevo (con IA, o un ejemplo en modo demo) → (caso, slug)."""
    if DEMO:
        caso = guion_demo(t["tema"])
        slug = caso.pop("slug")
    else:
        g = guionista.escribir(t["tema"], t["estilo"])
        caso = guionista.a_lote14(g)
        slug = g.slug
    caso["estilo"] = t["visual"]                          # el estilo visual lo decide el usuario
    slug = re.sub(r"[^a-z0-9-]", "", slug.lower())[:40] + "-" + t["id"][:6]
    return caso, slug


def procesar(t):
    tid = t["id"]
    os.makedirs(LOGS, exist_ok=True)
    log = os.path.join(LOGS, f"{tid}.log")
    try:
        if t["guion"]:                                    # guion ya escrito (y quizá corregido por el usuario)
            caso, slug = json.loads(t["guion"]), t["slug"]
        else:
            caso, slug = escribir_guion(t)
            actualizar(tid, slug=slug, titulo=caso["titulo_youtube"], descripcion=caso["descripcion"],
                       guion=json.dumps(caso, ensure_ascii=False))
            if t["revisar"]:                              # se para aquí: el usuario lo lee, lo corrige y lo confirma
                actualizar(tid, estado="revisar", paso="Revisa el guion")
                return
        actualizar(tid, titulo=caso["titulo_youtube"], descripcion=caso["descripcion"])
        script = fabrica.preparar(slug, caso)
        fabrica.fabricar(script, log, lambda p: actualizar(tid, paso=p), voz=t["voz"])
        motor_salida = os.path.join(fabrica.RAIZ, "salida")
        if os.path.abspath(SALIDA) != os.path.abspath(motor_salida):   # datos en el disco permanente (CR_DATOS)
            os.makedirs(SALIDA, exist_ok=True)
            for nombre in (f"{slug}.mp4", f"miniatura-{slug}.png"):
                if os.path.exists(os.path.join(motor_salida, nombre)):
                    shutil.move(os.path.join(motor_salida, nombre), os.path.join(SALIDA, nombre))
        if t["marca"]:
            actualizar(tid, paso="Animando el vídeo")
            poner_marca(os.path.join(SALIDA, f"{slug}.mp4"))
        actualizar(tid, estado="listo", paso="¡Listo!", fin=db.ahora())
    except ValueError as e:                               # problema del tema o del guion: se le explica
        actualizar(tid, estado="error", paso=str(e)[:300], fin=db.ahora())
    except Exception as e:                                # fallo técnico (el crédito se devuelve solo)
        with open(log, "a", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        actualizar(tid, estado="error", paso="Ha fallado algo técnico. Vuelve a intentarlo.", fin=db.ahora())


def recuperar():
    """Al arrancar: lo que quedó «trabajando» (se apagó a medias) vuelve a la cola."""
    with db.conectar() as c:
        c.execute("UPDATE trabajos SET estado='en cola', paso='Esperando turno' WHERE estado='trabajando'")


def bucle(espera=3):
    db.crear_tablas()
    recuperar()
    while True:
        t = coger()
        if t:
            procesar(t)
        else:
            time.sleep(espera)


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        sys.exit("Falta ffmpeg: instálalo con el script de despliegue/instalar.sh")
    bucle()
