"""Lee web/.env (claves y ajustes) sin depender de paquetes extra. Nunca se sube a ningún sitio."""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))


def cargar_env(ruta=None):
    ruta = ruta or os.path.join(AQUI, ".env")
    if not os.path.exists(ruta):
        return
    for linea in open(ruta, encoding="utf-8"):
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def datos(*partes):
    """Ruta de los datos que deben sobrevivir a las actualizaciones (base de datos, vídeos, registros, clave).
    En la nube, CR_DATOS apunta al disco permanente (p. ej. /datos en Railway). Sin CR_DATOS, la carpeta web/."""
    base = os.environ.get("CR_DATOS") or AQUI
    return os.path.join(base, *partes)
