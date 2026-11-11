"""Base de datos de la web (SQLite): usuarios, trabajos y pagos. Un archivo: web/datos.sqlite3."""
import os
import sqlite3
import time
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
from entorno import datos as _datos  # noqa: E402
RUTA = os.environ.get("CR_DB") or _datos("datos.sqlite3")

# Planes: vídeos al mes y si llevan marca de agua. Los precios se cobran en Stripe (ver .env.example).
PLANES = {
    "gratis":  dict(nombre="Gratis",  videos=2,   marca=True,  precio="0 €"),
    "creador": dict(nombre="Creador", videos=25,  marca=False, precio="9,99 €/mes"),
    "pro":     dict(nombre="Pro",     videos=80,  marca=False, precio="29,99 €/mes"),
}

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    clave_hash TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'gratis',
    periodo_inicio REAL,                 -- inicio del periodo pagado actual (para los planes de pago)
    stripe_cliente TEXT,
    stripe_suscripcion TEXT,
    creado REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS trabajos (
    id TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    tema TEXT NOT NULL,
    estilo TEXT NOT NULL,
    visual TEXT NOT NULL,
    marca INTEGER NOT NULL DEFAULT 1,    -- 1 = el vídeo lleva marca de agua (plan gratis al pedirlo)
    estado TEXT NOT NULL,                -- en cola · trabajando · revisar · listo · error · cancelado
    paso TEXT,
    slug TEXT,
    titulo TEXT,
    descripcion TEXT,
    inicio REAL NOT NULL,
    fin REAL
);
CREATE INDEX IF NOT EXISTS trabajos_usuario ON trabajos(usuario_id, inicio);
CREATE INDEX IF NOT EXISTS trabajos_estado ON trabajos(estado, inicio);
CREATE TABLE IF NOT EXISTS lista_espera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    canal TEXT,                          -- su canal o red (opcional)
    pagaria TEXT,                        -- «sí», «quizá», «no»: ¿pagaría unos 10 €/mes?
    creado REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS recuperar (
    token_hash TEXT PRIMARY KEY,         -- solo se guarda el hash: el enlace del email no se puede reconstruir
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    caduca REAL NOT NULL,
    usado INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS pagos (
    evento_id TEXT PRIMARY KEY,          -- id del evento de Stripe: así no se procesa dos veces
    tipo TEXT NOT NULL,
    usuario_id INTEGER,
    recibido REAL NOT NULL
);
"""


def conectar():
    c = sqlite3.connect(RUTA, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


# Columnas añadidas después de la primera versión (se añaden solas a las bases de datos que ya existían)
COLUMNAS_NUEVAS = {
    "trabajos": {"voz": "TEXT NOT NULL DEFAULT 'narrador'",   # voz de la web elegida (nunca la del dueño del canal)
                 "revisar": "INTEGER NOT NULL DEFAULT 0",       # 1 = enseñar el guion antes de hacer el vídeo
                 "guion": "TEXT",                              # guion (JSON) ya escrito: el obrero no lo vuelve a escribir
                 "personaje": "TEXT"},                         # aspecto del narrador elegido (JSON)
}


def crear_tablas():
    with conectar() as c:
        c.executescript(ESQUEMA)
        for tabla, cols in COLUMNAS_NUEVAS.items():
            hay = {r[1] for r in c.execute(f"PRAGMA table_info({tabla})")}
            for nombre, tipo in cols.items():
                if nombre not in hay:
                    c.execute(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}")


def inicio_mes():
    ahora = datetime.now(timezone.utc)
    return datetime(ahora.year, ahora.month, 1, tzinfo=timezone.utc).timestamp()


def uso(c, usuario):
    """(usados, límite) del periodo actual. Los vídeos que fallan no cuentan: se devuelve el crédito."""
    plan = PLANES.get(usuario["plan"], PLANES["gratis"])
    desde = inicio_mes() if usuario["plan"] == "gratis" else (usuario["periodo_inicio"] or inicio_mes())
    n = c.execute("SELECT COUNT(*) FROM trabajos WHERE usuario_id=? AND inicio>=? AND estado NOT IN ('error','cancelado')",
                  (usuario["id"], desde)).fetchone()[0]
    return n, plan["videos"]


def ahora():
    return time.time()
