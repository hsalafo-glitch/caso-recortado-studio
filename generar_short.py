#!/usr/bin/env python3
"""
Genera el short vertical "¿Por qué confesaron un crimen que no cometieron?"
Animación cut-out (recortes de papel) dibujada 100 % con código (pycairo).

Uso:
    python generar_short.py              # vídeo final con voz ElevenLabs (audio en caché)
    python generar_short.py --prueba     # sin voz, duraciones aproximadas + fotogramas clave
    python generar_short.py --voz VOICE_ID

Configuración en .env:
    ELEVENLABS_API_KEY=...
    ELEVENLABS_VOICE_ID=...      (opcional; por defecto «Salva», grave, acento de España)
    ELEVENLABS_MODEL_ID=eleven_v4   (opcional)
    ELEVENLABS_SPEED=1.0         (opcional, 0.7-1.2)

Requisitos: pip install pycairo numpy  ·  ffmpeg en el PATH
"""
import argparse
import base64
import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
import urllib.error
import wave

import cairo
import numpy as np

# ─────────────────────────────── constantes ───────────────────────────────
W, H = 1080, 1920


def TOP_Y():
    """Altura del rótulo superior (vertical: 300 · horizontal: 120)."""
    return 300 if H > W else 118


def SUB_Y():
    """Línea base de los subtítulos (vertical: 1505 · horizontal: abajo)."""
    return 1505 if H > W else H - 95
FPS = 30
POSES = 12                      # poses por segundo (cut-out "a saltos")
MAX_DUR = 59.0
ESTILO = "recortes"   # estilo visual: recortes · palitos · 3d · plano · neon (ver estilos.py)
GAP = 0.30                      # silencio entre bloques
TAIL = 0.8                      # cola final
SR = 44100
MUSIC_DB = -20.0                # música respecto a la voz
SALIDA = "confesiones-falsas"   # nombre base de los archivos de salida

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "salida")
CACHE_DIR = os.path.join(BASE, "cache_audio")
FONT = "Inter Display Black"

INK = (0.07, 0.06, 0.09)        # contorno negro

# ─────────────────────────────── guion ───────────────────────────────
# Cada cue es una frase del texto de VOZ: el cambio ocurre cuando se dice.
BLOQUES = [
    dict(
        id="gancho",
        voz="¿Por qué cinco adolescentes confesaron un crimen que no habían cometido?",
        escenas=[(None, "gancho")],
        pantalla=[(None, "¿POR QUÉ CONFESARON?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Nueva York, 1989. Una mujer es atacada mientras corría por Central Park. "
             "Esa misma noche, la policía detiene a cinco chicos de entre 14 y 16 años. "
             "Tras horas de interrogatorio, algunos sin abogado, los cinco confiesan en vídeo. "
             "Pero sus versiones no coinciden y ningún ADN los relaciona con el crimen. "
             "Aun así, los condenan. En 2002, el verdadero culpable confiesa y el ADN lo confirma. "
             "Para entonces habían pasado entre 6 y 13 años en prisión."),
        escenas=[(None, "parque"), ("Esa misma noche", "patrulla"), ("Tras horas", "interrogatorio"),
                 ("Aun así", "mazo"), ("En 2002", "celda")],
        pantalla=[(None, "NUEVA YORK, 1989"), ("cinco chicos", "5 CHICOS, 14-16 AÑOS"),
                  ("ningún ADN", "SIN ADN"), ("los condenan", "CONDENADOS"),
                  ("y el ADN", "2002: ERAN INOCENTES")],
        eventos={"confiesan": "los cinco confiesan", "versiones": "sus versiones",
                 "adn": "y el ADN", "puertas": "Para entonces"},
    ),
    dict(
        id="explicacion",
        voz=("Se llama confesión falsa por presión. Tras horas de cansancio y miedo, "
             "el cerebro solo quiere que aquello termine. Si te dicen \"confiesa y te vas a casa\", "
             "confesar parece la salida."),
        escenas=[(None, "chico")],
        pantalla=[("cansancio", "CANSANCIO +"), ("miedo", "MIEDO +"),
                  ("Si te dicen", "PROMESA ="), ("confesar parece", "CONFESIÓN")],
        modo_pantalla="pila",
        eventos={"poli": "Si te dicen", "habla": "confiesa y te", "salida": "confesar parece"},
        habla=("confiesa y te", "casa"),
    ),
    dict(
        id="cierre",
        voz=("Por eso muchos países graban los interrogatorios completos. "
             "¿Tú aguantarías diez horas diciendo la verdad?"),
        escenas=[(None, "camara")],
        pantalla=[("Tú aguantarías", "¿AGUANTARÍAS 10 HORAS?")],
        eventos={"pregunta": "Tú aguantarías"},
    ),
]

RECORTES_SUGERIDOS = [
    "Bloque 2: «algunos sin abogado» (≈1,2 s)",
    "Bloque 2: «entre sí» en «sus versiones no coinciden entre sí» (≈0,5 s)",
    "Bloque 2: «que estaban en el parque» (≈1,3 s)",
    "Bloque 3: «La psicología lo llama confesión falsa por presión» → «Se llama confesión falsa por presión» (≈1 s)",
    "Bloque 4: «ya» y «completos» en «graban los interrogatorios completos» (≈0,8 s)",
]


# ─────────────────────────────── utilidades ───────────────────────────────
def hexc(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)


def set_col(ctx, c):
    if len(c) == 4:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgb(*c)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(x):
    c1, c3 = 1.9, 2.9
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_io(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^\w\-]", "", s)


def hnoise(*k):
    """Ruido determinista en [0,1) a partir de una clave."""
    h = hashlib.md5(repr(k).encode()).digest()
    return int.from_bytes(h[:4], "little") / 2 ** 32


def load_env():
    p = os.path.join(BASE, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ─────────────────────────────── primitivas de papel ───────────────────────────────
def P_rect(x, y, w, h):
    return lambda c: c.rectangle(x, y, w, h)


def P_rrect(x, y, w, h, r):
    def f(c):
        c.new_sub_path()
        c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        c.close_path()
    return f


def P_ell(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry

    def f(c):
        c.save()
        c.translate(cx, cy)
        c.scale(rx, ry)
        c.new_sub_path()
        c.arc(0, 0, 1, 0, 2 * math.pi)
        c.restore()
    return f


def P_poly(pts):
    def f(c):
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.close_path()
    return f


def piece(ctx, path, fill, lw=4.0, shadow=True, sh=(5, 7), outline=True):
    """Dibuja una pieza en el estilo visual activo (por defecto, recorte de papel)."""
    if ESTILO != "recortes":
        import estilos
        return estilos.piece(ctx, path, fill, lw, shadow, sh, outline)
    _piece_recortes(ctx, path, fill, lw, shadow, sh, outline)


def _piece_recortes(ctx, path, fill, lw=4.0, shadow=True, sh=(5, 7), outline=True):
    """Recorte de papel: sombra mínima + color plano + contorno negro fino."""
    if shadow:
        ctx.save()
        ctx.translate(*sh)
        path(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.22)
        ctx.fill()
        ctx.restore()
    path(ctx)
    set_col(ctx, fill)
    if outline:
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.fill()


def line(ctx, pts, lw=4, col=INK, cap=cairo.LINE_CAP_ROUND):
    if ESTILO != "recortes":
        import estilos
        return estilos.line(ctx, pts, lw, col, cap)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    set_col(ctx, col)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.stroke()


class rot:
    """Rota las piezas dibujadas dentro del bloque alrededor de un pivote."""
    def __init__(self, ctx, px, py, ang):
        self.c, self.p, self.a = ctx, (px, py), ang

    def __enter__(self):
        self.c.save()
        self.c.translate(*self.p)
        self.c.rotate(self.a)
        self.c.translate(-self.p[0], -self.p[1])

    def __exit__(self, *a):
        self.c.restore()


def text_size(ctx, txt, size):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    return ctx.text_extents(txt)


def draw_text(ctx, txt, cx, cy, size, fill=(1, 1, 1), stroke=INK, sw=10, anchor="center"):
    """Texto con borde: (cx, cy) es el centro visual."""
    e = text_size(ctx, txt, size)
    x = cx - e.width / 2 - e.x_bearing if anchor == "center" else cx - e.x_bearing
    y = cy - e.height / 2 - e.y_bearing
    ctx.move_to(x, y)
    ctx.text_path(txt)
    if sw:
        set_col(ctx, stroke)
        ctx.set_line_width(sw * 2)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    set_col(ctx, fill)
    ctx.fill()
    return e


_KEEP = []


def make_paper_texture(seed=7):
    rng = np.random.default_rng(seed)
    small = rng.normal(0, 1, (H // 24 + 2, W // 24 + 2))
    big = np.kron(small, np.ones((24, 24)))[:H, :W]
    k = np.ones(25) / 25
    big = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, big)
    big = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 0, big)
    fine = rng.normal(0, 1, (H, W))
    fib = (np.sin(np.arange(W) * 0.9)[None, :] * rng.normal(0, 0.3, (H, 1)))
    g = 128 + 9 * big / (big.std() + 1e-6) + 10 * fine + 6 * fib
    g = np.clip(g, 0, 255).astype(np.uint8)
    arr = np.empty((H, W, 4), np.uint8)
    arr[..., 0] = g
    arr[..., 1] = g
    arr[..., 2] = g
    arr[..., 3] = 255
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W, H, W * 4)
    _KEEP.append(arr)
    return surf


# ─────────────────────────────── elementos comunes ───────────────────────────────
def stars(ctx, n, seed, ymax, pose):
    for i in range(n):
        x = hnoise(seed, i, "x") * W
        y = hnoise(seed, i, "y") * ymax
        r = 3 + hnoise(seed, i, "r") * 5
        tw = 1.0 if (pose + i) % 7 else 0.55
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(r * tw, r * tw)
        ctx.move_to(0, -1.6)
        for k in range(1, 8):
            a = -math.pi / 2 + k * math.pi / 4
            rr = 1.6 if k % 2 == 0 else 0.45
            ctx.line_to(rr * math.cos(a), rr * math.sin(a))
        ctx.close_path()
        ctx.restore()
        ctx.set_source_rgb(*hexc("#fff4c2"))
        ctx.fill()


def skyline(ctx, base_y, col, win_col, seed, pose, scale=1.0):
    x = -20
    i = 0
    while x < W + 20:
        w = (90 + hnoise(seed, i, "w") * 110) * scale
        h = (180 + hnoise(seed, i, "h") * 420) * scale
        piece(ctx, P_rect(x, base_y - h, w, h + 5), col, lw=3, shadow=False)
        if hnoise(seed, i, "ant") > 0.75:
            line(ctx, [(x + w / 2, base_y - h), (x + w / 2, base_y - h - 50 * scale)], 4, col)
        # ventanas
        for wy in range(int(base_y - h + 22 * scale), int(base_y - 20), int(42 * scale)):
            for wx in range(int(x + 14 * scale), int(x + w - 20 * scale), int(34 * scale)):
                on = hnoise(seed, i, wx, wy) > 0.55
                if on and hnoise(seed, i, wx, wy, pose // 18) > 0.08:
                    ctx.rectangle(wx, wy, 16 * scale, 22 * scale)
                    set_col(ctx, win_col)
                    ctx.fill()
        x += w + 6
        i += 1


def lamp_post(ctx, x, base_y, pose, h=520):
    flick = 0.85 if (pose % 23 == 5) else 1.0
    # cono de luz
    ctx.move_to(x - 30, base_y - h + 40)
    ctx.line_to(x + 30, base_y - h + 40)
    ctx.line_to(x + 190, base_y)
    ctx.line_to(x - 190, base_y)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.92, 0.55, 0.16 * flick)
    ctx.fill()
    piece(ctx, P_ell(x, base_y, 190, 34), (1, 0.92, 0.55, 0.20 * flick), shadow=False, outline=False)
    piece(ctx, P_rect(x - 10, base_y - h + 30, 20, h - 30), hexc("#2d2f3a"), lw=3)
    piece(ctx, P_rect(x - 28, base_y - 30, 56, 30), hexc("#2d2f3a"), lw=3)
    piece(ctx, P_poly([(x - 38, base_y - h + 40), (x + 38, base_y - h + 40), (x + 24, base_y - h - 30),
                       (x - 24, base_y - h - 30)]), hexc("#ffe58a"), lw=4)
    piece(ctx, P_poly([(x - 46, base_y - h + 44), (x + 46, base_y - h + 44), (x + 40, base_y - h + 30),
                       (x - 40, base_y - h + 30)]), hexc("#2d2f3a"), lw=3)
    piece(ctx, P_poly([(x - 30, base_y - h - 28), (x + 30, base_y - h - 28), (x, base_y - h - 60)]),
          hexc("#2d2f3a"), lw=3)


def tree(ctx, x, base_y, s, col, seed):
    piece(ctx, P_rect(x - 16 * s, base_y - 150 * s, 32 * s, 150 * s), hexc("#4a3226"), lw=3)
    blobs = [(0, -240, 110), (-80, -190, 80), (80, -190, 85), (-40, -300, 80), (45, -300, 75)]
    for i, (dx, dy, r) in enumerate(blobs):
        piece(ctx, P_ell(x + dx * s, base_y + dy * s, r * s, r * s * 0.9), col, lw=3,
              shadow=(i == 0))


def police_tape(ctx, y0, y1, pose, txt="POLICÍA · NO PASAR · "):
    ang = math.atan2(y1 - y0, W + 200)
    sway = math.radians(1.2) * (1 if (pose // 4) % 2 else -1)
    with rot(ctx, W / 2, (y0 + y1) / 2, sway):
        ctx.save()
        ctx.translate(-100, y0)
        ctx.rotate(ang)
        L = math.hypot(W + 200, y1 - y0)
        piece(ctx, P_rect(0, -34, L, 68), hexc("#ffd400"), lw=4)
        ctx.select_font_face(FONT, 0, 0)
        ctx.set_font_size(40)
        e = ctx.text_extents(txt)
        x = -((pose * 6) % int(e.x_advance))
        while x < L:
            ctx.move_to(x, 15)
            ctx.set_source_rgb(*INK)
            ctx.show_text(txt)
            x += e.x_advance
        ctx.restore()


def wall_clock(ctx, cx, cy, r, minutes):
    piece(ctx, P_ell(cx, cy, r + 14), hexc("#3b3b46"), lw=4)
    piece(ctx, P_ell(cx, cy, r), hexc("#f6f1e2"), lw=3, shadow=False)
    for k in range(12):
        a = k * math.pi / 6
        r0 = r * (0.78 if k % 3 == 0 else 0.86)
        line(ctx, [(cx + r0 * math.sin(a), cy - r0 * math.cos(a)),
                   (cx + r * 0.94 * math.sin(a), cy - r * 0.94 * math.cos(a))], 7 if k % 3 == 0 else 4)
    am = minutes / 60 * 2 * math.pi
    ah = minutes / 720 * 2 * math.pi
    line(ctx, [(cx, cy), (cx + r * 0.5 * math.sin(ah), cy - r * 0.5 * math.cos(ah))], 12)
    line(ctx, [(cx, cy), (cx + r * 0.78 * math.sin(am), cy - r * 0.78 * math.cos(am))], 7,
         hexc("#c62828"))
    piece(ctx, P_ell(cx, cy, 10), INK, shadow=False)


# ─────────────────────────────── personajes (originales) ───────────────────────────────
def silhouette(ctx, x, feet, s, tilt, col, rim):
    """Chico en silueta, sin rasgos."""
    head_r = 72 * s
    neck = (x, feet - 230 * s)
    piece(ctx, P_poly([(x - 70 * s, feet), (x + 70 * s, feet), (x + 52 * s, feet - 235 * s),
                       (x - 52 * s, feet - 235 * s)]), col, lw=4, shadow=False)
    with rot(ctx, neck[0], neck[1], tilt):
        piece(ctx, P_ell(x, feet - 230 * s - head_r * 0.9, head_r), col, lw=4, shadow=False)
        ctx.new_sub_path()
        ctx.arc(x, feet - 230 * s - head_r * 0.9, head_r - 9, math.radians(205), math.radians(300))
        set_col(ctx, rim)
        ctx.set_line_width(7)
        ctx.stroke()


BOY_SKIN = hexc("#d79a6c")
COP_SKIN = hexc("#f0c7a0")


def boy(ctx, x, y, tired, droop, talk, look, pose):
    """Chico original: cabeza redonda grande, flequillo en punta, sudadera naranja."""
    r = 128
    neck = (x, y + r * 0.92)
    # cuerpo (sudadera)
    piece(ctx, P_poly([(x - 92, y + 108), (x + 92, y + 108), (x + 150, y + 330), (x - 150, y + 330)]),
          hexc("#ef7d2d"), lw=4)
    piece(ctx, P_poly([(x - 40, y + 108), (x + 40, y + 108), (x, y + 165)]), hexc("#f6efe0"), lw=3,
          shadow=False)
    line(ctx, [(x - 18, y + 140), (x - 22, y + 215)], 4)
    line(ctx, [(x + 18, y + 140), (x + 22, y + 215)], 4)
    with rot(ctx, neck[0], neck[1], droop):
        # orejas
        piece(ctx, P_ell(x - r + 4, y + 10, 26, 34), BOY_SKIN, lw=4)
        piece(ctx, P_ell(x + r - 4, y + 10, 26, 34), BOY_SKIN, lw=4)
        piece(ctx, P_ell(x, y, r, r * 0.96), BOY_SKIN, lw=4.5)
        # pelo: casquete con puntas
        pts = []
        n = 15
        for i in range(n + 1):
            a = math.pi + 0.18 + (math.pi - 0.36) * i / n
            rr = r + (30 if i % 2 else 8)
            pts.append((x + rr * math.cos(a), y - 6 + rr * math.sin(a)))
        for i in range(9):
            fx = x + r * 0.86 - i * (r * 1.72 / 8)
            fy = y - r * 0.38 + (26 if i % 2 else 0)
            pts.append((fx, fy))
        piece(ctx, P_poly(pts), hexc("#3a2418"), lw=4, shadow=False)
        # ojos
        lid = clamp(0.15 + 0.55 * tired)
        for side in (-1, 1):
            ex, ey = x + side * 46, y + 8
            piece(ctx, P_ell(ex, ey, 33, 40), (1, 1, 1), lw=3.5, shadow=False)
            ctx.save()
            P_ell(ex, ey, 33, 40)(ctx)
            ctx.clip()
            P_ell(ex + look * 13, ey + 8, 12, 13)(ctx)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.rectangle(ex - 40, ey - 45, 80, 85 * lid)
            set_col(ctx, BOY_SKIN)
            ctx.fill()
            ctx.restore()
            line(ctx, [(ex - 32, ey - 40 + 85 * lid), (ex + 32, ey - 40 + 85 * lid)], 4)
            P_ell(ex, ey, 33, 40)(ctx)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(3.5)
            ctx.stroke()
            # ojeras
            ctx.new_sub_path()
            ctx.arc(ex, ey + 30, 26, math.radians(30), math.radians(150))
            ctx.set_source_rgba(0.42, 0.2, 0.42, 0.25 + 0.45 * tired)
            ctx.set_line_width(5)
            ctx.stroke()
            # cejas preocupadas
            line(ctx, [(ex - side * 30, ey - 50 - 4 * tired), (ex + side * 22, ey - 62 + 6 * tired)], 6)
        # boca
        if talk:
            piece(ctx, P_ell(x, y + 78, 22, 16 if talk == 1 else 10), hexc("#5a1620"), lw=4, shadow=False)
        else:
            ctx.new_sub_path()
            ctx.arc(x, y + 98, 22, math.radians(220), math.radians(320))
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(5)
            ctx.stroke()
        # gota de sudor
        if tired > 0.45:
            dy = (pose % 6) * 4
            sx, sy = x + 108, y - 58 + dy
            piece(ctx, P_poly([(sx, sy - 26), (sx + 13, sy), (sx, sy + 10), (sx - 13, sy)]),
                  hexc("#8fd3ff"), lw=3, shadow=False)


def cop(ctx, x, floor_y, arm, talk, pose):
    """Policía original: gorra de plato, bigote frondoso, uniforme azul."""
    hy = floor_y - 520
    r = 112
    # piernas
    piece(ctx, P_rect(x - 70, floor_y - 170, 58, 170), hexc("#1b2747"), lw=4)
    piece(ctx, P_rect(x + 12, floor_y - 170, 58, 170), hexc("#1b2747"), lw=4)
    piece(ctx, P_rrect(x - 82, floor_y - 22, 82, 26, 10), INK, lw=3, shadow=False)
    piece(ctx, P_rrect(x + 4, floor_y - 22, 82, 26, 10), INK, lw=3, shadow=False)
    # brazo trasero
    with rot(ctx, x - 92, hy + 150, math.radians(8)):
        piece(ctx, P_rrect(x - 116, hy + 140, 46, 190, 20), hexc("#2c4479"), lw=4)
        piece(ctx, P_ell(x - 93, hy + 338, 26), COP_SKIN, lw=4)
    # cuerpo
    piece(ctx, P_rrect(x - 100, hy + 98, 200, 260, 30), hexc("#2c4479"), lw=4.5)
    piece(ctx, P_rect(x - 100, hy + 300, 200, 30), INK, lw=3, shadow=False)
    piece(ctx, P_rect(x - 18, hy + 302, 36, 26), hexc("#d8b43a"), lw=3, shadow=False)
    # placa
    bx, by = x + 48, hy + 170
    piece(ctx, P_poly([(bx, by - 26), (bx + 22, by - 14), (bx + 18, by + 16), (bx, by + 28),
                       (bx - 18, by + 16), (bx - 22, by - 14)]), hexc("#f2c94c"), lw=3, shadow=False)
    line(ctx, [(x, hy + 110), (x, hy + 295)], 3)
    # cabeza
    piece(ctx, P_ell(x, hy, r, r * 0.97), COP_SKIN, lw=4.5)
    for side in (-1, 1):
        ex, ey = x + side * 40, hy - 4
        piece(ctx, P_ell(ex, ey, 22, 28), (1, 1, 1), lw=3.5, shadow=False)
        P_ell(ex + 7, ey + 4, 9)(ctx)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        line(ctx, [(ex - side * 28, ey - 46), (ex + side * 24, ey - 30)], 10)
    # nariz
    piece(ctx, P_ell(x + 6, hy + 34, 20, 15), hexc("#e3a982"), lw=3.5, shadow=False)
    # boca bajo el bigote
    if talk:
        piece(ctx, P_ell(x + 4, hy + 74, 26, 22 if talk == 1 else 13), hexc("#5a1620"), lw=4, shadow=False)
    # bigote
    must = []
    for i in range(9):
        a = math.pi * i / 8
        must.append((x + 4 - 66 * math.cos(a), hy + 56 - (16 + (8 if i % 2 else 0)) * math.sin(a) * -1))
    must += [(x + 70, hy + 66), (x + 4, hy + 58), (x - 62, hy + 66)]
    piece(ctx, P_poly(must), hexc("#6b4a2b"), lw=3.5, shadow=False)
    # gorra
    piece(ctx, P_poly([(x - 100, hy - 66), (x + 100, hy - 66), (x + 124, hy - 132), (x - 124, hy - 132)]),
          hexc("#1b2747"), lw=4, shadow=False)
    piece(ctx, P_rrect(x - 104, hy - 74, 208, 24, 8), INK, lw=3, shadow=False)
    piece(ctx, P_poly([(x - 86, hy - 52), (x + 106, hy - 52), (x + 128, hy - 34), (x - 70, hy - 40)]),
          INK, lw=3, shadow=False)
    piece(ctx, P_ell(x, hy - 104, 18, 20), hexc("#f2c94c"), lw=3, shadow=False)
    # brazo que señala (pivota en el hombro)
    sx, sy = x + 88, hy + 150
    with rot(ctx, sx, sy, arm):
        piece(ctx, P_rrect(sx - 22, sy - 10, 46, 190, 20), hexc("#2c4479"), lw=4)
        piece(ctx, P_ell(sx + 1, sy + 196, 26), COP_SKIN, lw=4)
        piece(ctx, P_rrect(sx - 7, sy + 200, 14, 44, 7), COP_SKIN, lw=3.5, shadow=False)


# ─────────────────────────────── fondos y escenas ───────────────────────────────
def bg_night_park(ctx, pose, lt):
    ctx.set_source_rgb(*hexc("#1c2552"))
    ctx.paint()
    stars(ctx, 26, "parque", 820, pose)
    piece(ctx, P_ell(830, 330, 74), hexc("#f6eab0"), lw=4)
    piece(ctx, P_ell(806, 312, 13), hexc("#e5d58f"), shadow=False, lw=2)
    piece(ctx, P_ell(850, 352, 9), hexc("#e5d58f"), shadow=False, lw=2)
    skyline(ctx, 1060, hexc("#121838"), hexc("#ffd86b"), "nyc", pose)
    piece(ctx, P_poly([(-10, 1000), (300, 960), (700, 985), (1090, 950), (1090, 1930), (-10, 1930)]),
          hexc("#2f6b45"), lw=4, shadow=False)
    for i, (tx, ty, s) in enumerate([(120, 1040, 1.0), (980, 1030, 1.1), (560, 1000, 0.75)]):
        tree(ctx, tx, ty, s, hexc("#1f4a35") if i != 1 else hexc("#24553c"), i)
    # camino
    piece(ctx, P_poly([(470, 1000), (610, 1000), (900, 1930), (180, 1930)]), hexc("#9b8b6c"), lw=4,
          shadow=False)
    lamp_post(ctx, 250, 1380, pose)
    lamp_post(ctx, 860, 1330, pose + 9, h=480)
    # banco
    piece(ctx, P_rect(640, 1230, 170, 18), hexc("#7a4b2a"), lw=3)
    piece(ctx, P_rect(640, 1195, 170, 16), hexc("#7a4b2a"), lw=3)
    piece(ctx, P_rect(652, 1248, 12, 48), INK, lw=2, shadow=False)
    piece(ctx, P_rect(786, 1248, 12, 48), INK, lw=2, shadow=False)
    # conos + cinta (sin mostrar la agresión)
    for cx in (130, 950):
        piece(ctx, P_poly([(cx - 38, 1470), (cx + 38, 1470), (cx + 10, 1350), (cx - 10, 1350)]),
              hexc("#ff7a1a"), lw=4)
        piece(ctx, P_rect(cx - 25, 1405, 50, 16), (1, 1, 1), lw=2, shadow=False)
    police_tape(ctx, 1300, 1240, pose)
    police_tape(ctx, 1385, 1445, pose + 2, "NO PASAR · POLICÍA · ")


def bg_street(ctx, pose, lt):
    ctx.set_source_rgb(*hexc("#1a2048"))
    ctx.paint()
    stars(ctx, 14, "calle", 600, pose)
    skyline(ctx, 1150, hexc("#2a2f5e"), hexc("#ffd86b"), "calle1", pose, 1.25)
    piece(ctx, P_rect(-10, 1150, W + 20, 90), hexc("#6d6a75"), lw=4, shadow=False)
    piece(ctx, P_rect(-10, 1240, W + 20, 700), hexc("#2b2c38"), lw=4, shadow=False)
    for i in range(6):
        piece(ctx, P_rect(-60 + i * 230 - (pose * 0) % 230, 1560, 130, 18), hexc("#f2e7b0"), lw=2,
              shadow=False)
    lamp_post(ctx, 120, 1180, pose, h=560)


def patrol_car(ctx, x, y, pose, flash):
    """Coche patrulla original (x = centro, y = suelo)."""
    bounce = 3 if pose % 2 else 0
    y = y - bounce
    # carrocería
    piece(ctx, P_poly([(x - 420, y - 70), (x - 410, y - 190), (x - 250, y - 205), (x - 170, y - 320),
                       (x + 170, y - 320), (x + 270, y - 205), (x + 410, y - 185), (x + 420, y - 70)]),
          hexc("#f4f4f0"), lw=5)
    piece(ctx, P_rect(x - 418, y - 160, 836, 60), hexc("#1f3f8f"), lw=4, shadow=False)
    # ventanas con siluetas
    for wx0, wx1 in ((-235, -10), (10, 235)):
        piece(ctx, P_poly([(x + wx0, y - 215), (x + wx0 + 50, y - 302), (x + wx1 - 30, y - 302),
                           (x + wx1, y - 215)]), hexc("#5f7fb0"), lw=4, shadow=False)
    ctx.save()
    P_poly([(x - 235, y - 215), (x - 185, y - 302), (x - 40, y - 302), (x - 10, y - 215)])(ctx)
    ctx.clip()
    for k, hx in enumerate((-190, -120, -55)):
        piece(ctx, P_ell(x + hx, y - 225, 34), hexc("#1a1530"), lw=3, shadow=False)
    ctx.restore()
    ctx.save()
    P_poly([(x + 10, y - 215), (x + 60, y - 302), (x + 205, y - 302), (x + 235, y - 215)])(ctx)
    ctx.clip()
    piece(ctx, P_ell(x + 120, y - 228, 36), hexc("#1a1530"), lw=3, shadow=False)
    piece(ctx, P_rect(x + 78, y - 290, 84, 28), hexc("#1a1530"), lw=3, shadow=False)
    ctx.restore()
    # rótulo
    draw_text(ctx, "POLICÍA", x, y - 130, 46, (1, 1, 1), INK, 4)
    # sirena
    piece(ctx, P_rect(x - 90, y - 350, 180, 32), INK, lw=3, shadow=False)
    piece(ctx, P_rrect(x - 84, y - 346, 80, 24, 8), hexc("#ff3040") if flash else hexc("#6a1a20"), lw=3,
          shadow=False)
    piece(ctx, P_rrect(x + 4, y - 346, 80, 24, 8), hexc("#2f6dff") if not flash else hexc("#1a2a55"), lw=3,
          shadow=False)
    # ruedas
    for wx in (-260, 260):
        piece(ctx, P_ell(x + wx, y - 60, 76), INK, lw=3)
        piece(ctx, P_ell(x + wx, y - 60, 38), hexc("#9a9aa6"), lw=3, shadow=False)
        a = pose * 0.9
        for k in range(3):
            line(ctx, [(x + wx, y - 60), (x + wx + 30 * math.cos(a + k * 2.09), y - 60 + 30 * math.sin(a + k * 2.09))],
                 5)
    piece(ctx, P_rect(x + 385, y - 150, 30, 26), hexc("#ffe58a"), lw=3, shadow=False)


def sc_patrulla(ctx, pose, lt, ev):
    bg_street(ctx, pose, lt)
    flash = (pose // 3) % 2 == 0
    k = clamp(lt / 1.0)
    x = lerp(1600, 560, 1 - (1 - k) ** 2)
    # reflejos de la sirena
    ctx.set_source_rgba(*(hexc("#ff3040") if flash else hexc("#2f6dff")), 0.10)
    ctx.paint()
    patrol_car(ctx, x, 1430, pose if k < 1 else 0, flash)


def bg_room(ctx, pose, door=False, door_open=0.0):
    ctx.set_source_rgb(*hexc("#7c8c7c"))
    ctx.paint()
    # paneles de pared
    for i in range(7):
        line(ctx, [(i * 170 + 40, 0), (i * 170 + 40, 1200)], 3, (0, 0, 0, 0.12))
    piece(ctx, P_rect(-10, 1180, W + 20, 30), hexc("#4c5a4c"), lw=4, shadow=False)
    piece(ctx, P_rect(-10, 1205, W + 20, 730), hexc("#4a4d5a"), lw=4, shadow=False)
    for i in range(9):
        line(ctx, [(i * 140 - 80, 1210), (i * 200 - 260, 1930)], 3, (0, 0, 0, 0.18))
    # espejo unidireccional
    piece(ctx, P_rect(70, 640, 330, 300), hexc("#2c3446"), lw=6)
    line(ctx, [(110, 900), (210, 680)], 10, (1, 1, 1, 0.12))
    line(ctx, [(170, 910), (270, 690)], 6, (1, 1, 1, 0.10))
    if door:
        dx, dy, dw, dh = 850, 760, 200, 440
        # luz cálida al abrirse
        piece(ctx, P_rect(dx, dy, dw, dh), hexc("#ffd36b"), lw=5, shadow=False)
        if door_open > 0:
            ctx.move_to(dx, dy + dh)
            ctx.line_to(dx + dw, dy + dh)
            ctx.line_to(dx + dw + 120 * door_open, 1930)
            ctx.line_to(dx - 260 * door_open, 1930)
            ctx.close_path()
            ctx.set_source_rgba(1, 0.85, 0.4, 0.28)
            ctx.fill()
        w = dw * (1 - 0.75 * door_open)
        piece(ctx, P_rect(dx, dy, w, dh), hexc("#8a5a34"), lw=5)
        piece(ctx, P_ell(dx + w - 26, dy + dh / 2, 12), hexc("#f2c94c"), lw=3, shadow=False)
        # letrero CASA
        piece(ctx, P_rect(dx - 10, dy - 110, dw + 20, 88), hexc("#fff3c4"), lw=5)
        draw_text(ctx, "CASA", dx + dw / 2, dy - 66, 62, hexc("#c62828"), INK, 0)


def lamp_hanging(ctx, x, pose, sway=True):
    a = math.radians(2.5) * (1 if (pose // 6) % 2 else -1) if sway else 0
    with rot(ctx, x, 0, a):
        line(ctx, [(x, 0), (x, 470)], 6)
        ctx.move_to(x - 70, 520)
        ctx.line_to(x + 70, 520)
        ctx.line_to(x + 330, 1300)
        ctx.line_to(x - 330, 1300)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.95, 0.65, 0.13)
        ctx.fill()
        piece(ctx, P_poly([(x - 30, 465), (x + 30, 465), (x + 80, 525), (x - 80, 525)]), hexc("#3a3d48"), lw=4)
        piece(ctx, P_ell(x, 528, 30, 14), hexc("#fff3b0"), lw=3, shadow=False)


def table_and_chairs(ctx, chair_back=True, chair_front=True):
    if chair_back:
        piece(ctx, P_rrect(440, 960, 200, 260, 16), hexc("#5d3a22"), lw=4)
    # mesa
    piece(ctx, P_poly([(170, 1200), (910, 1200), (990, 1290), (90, 1290)]), hexc("#9b6a3f"), lw=5)
    piece(ctx, P_rect(90, 1290, 900, 46), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(120, 1336, 34, 250), hexc("#5d3a22"), lw=4)
    piece(ctx, P_rect(926, 1336, 34, 250), hexc("#5d3a22"), lw=4)
    if chair_front:
        piece(ctx, P_rrect(420, 1440, 240, 60, 14), hexc("#5d3a22"), lw=4)
        piece(ctx, P_rect(440, 1500, 26, 200), hexc("#4a2e1a"), lw=4)
        piece(ctx, P_rect(614, 1500, 26, 200), hexc("#4a2e1a"), lw=4)


def sc_interrogatorio(ctx, pose, lt, ev):
    bg_room(ctx, pose)
    wall_clock(ctx, 800, 820, 112, lt * 95 * 2)          # reloj a toda velocidad
    lamp_hanging(ctx, 540, pose)
    table_and_chairs(ctx)
    # confesiones que aparecen una a una
    if ev.get("confiesan") is not None:
        tl = ev["confiesan_lt"]
        n = int(clamp((lt - tl) / 0.25 + 1, 0, 5)) if lt >= tl else 0
        for i in range(n):
            px = 210 + i * 140
            a = math.radians(-8 + 16 * hnoise("hoja", i))
            with rot(ctx, px + 55, 1240, a):
                piece(ctx, P_poly([(px + 10, 1215), (px + 110, 1215), (px + 118, 1268), (px + 2, 1268)]),
                      (1, 1, 1), lw=3)
                for k in range(3):
                    wob = 8 * hnoise("lin", i, k)
                    line(ctx, [(px + 22, 1228 + k * 12), (px + 95 - wob * 3, 1228 + k * 12)], 3,
                         hexc("#c62828") if (ev.get("versiones_lt") is not None and lt >= ev["versiones_lt"]
                                             and k == i % 3) else INK)


def sc_gancho(ctx, pose, lt, ev):
    ctx.set_source_rgb(*hexc("#100d1f"))
    ctx.paint()
    # foco
    ctx.move_to(470, -20)
    ctx.line_to(610, -20)
    ctx.line_to(1010, 1460)
    ctx.line_to(70, 1460)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.93, 0.7, 0.13)
    ctx.fill()
    piece(ctx, P_ell(540, 1452, 470, 95), (1, 0.93, 0.7, 0.20), shadow=False, outline=False)
    piece(ctx, P_rect(-10, 1452, W + 20, 500), hexc("#0b0916"), shadow=False, lw=3)
    piece(ctx, P_ell(540, 1452, 470, 60), hexc("#2b2540"), shadow=False, lw=3)
    xs = [180, 360, 540, 720, 900]
    hs = [0.98, 1.06, 1.12, 1.0, 0.94]
    for i, (x, s) in enumerate(zip(xs, hs)):
        tilt = math.radians(4) * (1 if (pose // 5 + i) % 2 else -1) * (0.6 + 0.4 * hnoise("t", i))
        silhouette(ctx, x, 1452, s * 1.25, tilt, hexc("#272040"), hexc("#5a4e8a"))
    # interrogante gigante de papel
    k = clamp((lt - 0.25) / 0.35)
    if k > 0:
        sc = ease_out_back(k)
        wob = math.radians(6) * (1 if (pose // 4) % 2 else -1)
        ctx.save()
        ctx.translate(540, 760)
        ctx.rotate(wob)
        ctx.scale(sc, sc)
        ctx.translate(8, 12)
        draw_text(ctx, "?", 0, 0, 470, (0, 0, 0, 0.35), INK, 0)
        ctx.translate(-8, -12)
        draw_text(ctx, "?", 0, 0, 470, hexc("#ffd23f"), INK, 7)
        ctx.restore()


def sc_parque(ctx, pose, lt, ev):
    bg_night_park(ctx, pose, lt)


def scales_icon(ctx, cx, cy, s):
    piece(ctx, P_ell(cx, cy, 120 * s), hexc("#d9b54a"), lw=5)
    piece(ctx, P_ell(cx, cy, 100 * s), hexc("#5a3018"), lw=3, shadow=False)
    line(ctx, [(cx, cy - 70 * s), (cx, cy + 60 * s)], 8, hexc("#d9b54a"))
    line(ctx, [(cx - 65 * s, cy - 45 * s), (cx + 65 * s, cy - 45 * s)], 8, hexc("#d9b54a"))
    for sx in (-1, 1):
        px = cx + sx * 60 * s
        line(ctx, [(px, cy - 45 * s), (px - 22 * s, cy + 5 * s)], 3, hexc("#d9b54a"))
        line(ctx, [(px, cy - 45 * s), (px + 22 * s, cy + 5 * s)], 3, hexc("#d9b54a"))
        ctx.new_sub_path()
        ctx.arc(px, cy + 5 * s, 24 * s, 0, math.pi)
        ctx.close_path()
        set_col(ctx, hexc("#d9b54a"))
        ctx.fill()
    line(ctx, [(cx - 40 * s, cy + 62 * s), (cx + 40 * s, cy + 62 * s)], 10, hexc("#d9b54a"))


def sc_mazo(ctx, pose, lt, ev):
    ctx.set_source_rgb(*hexc("#6e4127"))
    ctx.paint()
    for i in range(8):
        piece(ctx, P_rect(i * 150 - 20, 0, 140, 1000), hexc("#7d4b2d"), lw=3, shadow=False)
    scales_icon(ctx, 540, 790, 1.15)
    # estrado
    piece(ctx, P_rect(-20, 1000, W + 40, 950), hexc("#4f2c18"), lw=5, shadow=False)
    piece(ctx, P_rect(-20, 1000, W + 40, 70), hexc("#8a5532"), lw=5)
    for i in range(4):
        piece(ctx, P_rect(70 + i * 250, 1130, 190, 700), hexc("#5c341d"), lw=4, shadow=False)
    # bloque de sonido
    piece(ctx, P_ell(450, 1170, 170, 46), hexc("#3d2010"), lw=4)
    piece(ctx, P_rect(280, 1120, 340, 50), hexc("#8a5532"), lw=4, shadow=False)
    piece(ctx, P_ell(450, 1120, 170, 46), hexc("#a8693d"), lw=4, shadow=False)
    # golpes en 0,35 s y 1,0 s
    strikes = (0.33, 1.0)
    ang = math.radians(-38)
    hit = False
    for s in strikes:
        d = lt - s
        if -0.25 <= d < 0:
            ang = math.radians(-38) * (-d / 0.25)
        elif 0 <= d < 0.17:
            ang, hit = 0.0, True
        elif 0.17 <= d < 0.5:
            ang = math.radians(-38) * ((d - 0.17) / 0.33)
    if lt > strikes[-1] + 0.17:
        ang = math.radians(-12)
    shake = (6 if hit and pose % 2 else -6 if hit else 0)
    ctx.save()
    ctx.translate(shake, 0)
    px, py = 900, 1000
    with rot(ctx, px, py, ang):
        piece(ctx, P_rrect(500, 975, 420, 44, 20), hexc("#a8693d"), lw=4.5)
        piece(ctx, P_rrect(360, 880, 160, 230, 26), hexc("#6b3a1f"), lw=5)
        piece(ctx, P_rect(360, 920, 160, 26), hexc("#d9b54a"), lw=3, shadow=False)
        piece(ctx, P_rect(360, 1046, 160, 26), hexc("#d9b54a"), lw=3, shadow=False)
    ctx.restore()
    if hit:
        for k in range(8):
            a = math.pi + k * math.pi / 7
            line(ctx, [(450 + 200 * math.cos(a), 1120 + 90 * math.sin(a)),
                       (450 + 290 * math.cos(a), 1120 + 150 * math.sin(a))], 9, hexc("#ffe14d"))


def check_sign(ctx, cx, cy, s):
    with rot(ctx, cx, cy, math.radians(-4)):
        piece(ctx, P_rrect(cx - 280 * s, cy - 110 * s, 560 * s, 220 * s, 26 * s), hexc("#2fb35a"), lw=7,
              sh=(9, 12))
        draw_text(ctx, "ADN", cx - 80 * s, cy, 150 * s, (1, 1, 1), INK, 8)
        ctx.move_to(cx + 110 * s, cy + 5 * s)
        ctx.line_to(cx + 160 * s, cy + 60 * s)
        ctx.line_to(cx + 250 * s, cy - 70 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(48 * s)
        ctx.stroke_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(28 * s)
        ctx.stroke()


def sc_celda(ctx, pose, lt, ev):
    """Vista desde dentro de la celda: puerta de barrotes a la izquierda, calendario a la derecha."""
    ctx.set_source_rgb(*hexc("#9d978b"))
    ctx.paint()
    for row in range(0, 30):
        y = row * 46
        off = 0 if row % 2 else 60
        for col in range(-1, 10):
            x = col * 120 + off
            ctx.rectangle(x + 3, y + 3, 114, 40)
            ctx.set_source_rgba(0, 0, 0, 0.05 + 0.05 * hnoise("lad", row, col))
            ctx.fill()
    piece(ctx, P_rect(-10, 1290, W + 20, 700), hexc("#5d5952"), lw=4, shadow=False)
    # hueco de la puerta: pasillo iluminado detrás
    piece(ctx, P_rect(30, 430, 470, 870), hexc("#f3d98b"), lw=6, shadow=False)
    piece(ctx, P_rect(30, 1080, 470, 220), hexc("#d9bd6e"), lw=4, shadow=False)
    # ventanuco con luna
    piece(ctx, P_rect(640, 470, 250, 150), hexc("#1c2552"), lw=6)
    piece(ctx, P_ell(830, 520, 28), hexc("#f6eab0"), lw=3, shadow=False)
    for k in range(4):
        line(ctx, [(640 + 50 * (k + 1), 470), (640 + 50 * (k + 1), 620)], 9, hexc("#3b3b46"))
    # catre
    piece(ctx, P_rect(560, 1200, 470, 60), hexc("#8a8f99"), lw=4)
    piece(ctx, P_rrect(570, 1155, 450, 55, 20), hexc("#e7e2d3"), lw=4)
    piece(ctx, P_rrect(880, 1130, 130, 50, 20), (1, 1, 1), lw=4, shadow=False)
    piece(ctx, P_rect(575, 1260, 20, 90), INK, lw=2, shadow=False)
    piece(ctx, P_rect(995, 1260, 20, 90), INK, lw=2, shadow=False)
    # calendario que pierde hojas
    t_adn = ev.get("adn_lt", 3.0)
    span = max(0.8, t_adn - 0.2)
    k = clamp(lt / span)
    year = 1990 + int(round(k * 12))
    cx, cy = 790, 860
    piece(ctx, P_rect(cx - 150, cy - 160, 300, 330), (1, 1, 1), lw=5)
    piece(ctx, P_rect(cx - 150, cy - 160, 300, 82), hexc("#d93636"), lw=5, shadow=False)
    for i in range(5):
        piece(ctx, P_ell(cx - 100 + i * 50, cy - 160, 10), INK, shadow=False, lw=2)
    draw_text(ctx, "AÑO", cx, cy - 118, 46, (1, 1, 1), INK, 0)
    draw_text(ctx, str(year), cx, cy + 25, 116, INK, INK, 0)
    for i in range(3):
        line(ctx, [(cx - 105, cy + 110 + i * 18), (cx + 105, cy + 110 + i * 18)], 3, (0, 0, 0, 0.25))
    if k < 1:
        ph = (lt * 12 / span) % 1.0
        for j in range(2):
            p = (ph + j * 0.5) % 1.0
            ctx.save()
            ctx.translate(cx + 40 - p * 200, cy - 60 + p * p * 700)
            ctx.rotate(-p * 4 - j)
            piece(ctx, P_rect(-90, -110, 180, 220), (1, 1, 1), lw=4)
            piece(ctx, P_rect(-90, -110, 180, 50), hexc("#d93636"), lw=3, shadow=False)
            ctx.restore()
    # puerta de barrotes que se desliza a la izquierda
    tp = ev.get("puertas_lt")
    slide = 0.0
    if tp is not None and lt >= tp:
        slide = ease_io((lt - tp) / 0.9) * 520
    ctx.save()
    ctx.rectangle(0, 0, 520, H)
    ctx.clip()
    ctx.translate(-slide, 0)
    for i in range(6):
        x = 44 + i * 88
        piece(ctx, P_rect(x, 430, 24, 870), hexc("#3d3f4a"), lw=4, sh=(8, 0))
        line(ctx, [(x + 6, 432), (x + 6, 1296)], 4, (1, 1, 1, 0.18))
    piece(ctx, P_rect(30, 600, 480, 30), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rect(30, 1150, 480, 30), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rrect(440, 820, 70, 130, 12), hexc("#2a2b33"), lw=4)
    piece(ctx, P_ell(475, 880, 14), INK, lw=2, shadow=False)
    ctx.restore()
    # marco de la puerta
    piece(ctx, P_rect(14, 414, 502, 22), hexc("#2a2b33"), lw=4, shadow=False)
    piece(ctx, P_rect(500, 414, 22, 890), hexc("#2a2b33"), lw=4, shadow=False)
    piece(ctx, P_rect(14, 414, 22, 890), hexc("#2a2b33"), lw=4, shadow=False)
    ta = ev.get("adn_lt")
    if ta is not None and lt >= ta:
        kk = clamp((lt - ta) / 0.3)
        check_sign(ctx, 540, 1160, ease_out_back(kk) if kk < 1 else 1.0)


def battery(ctx, cx, cy, level, pose):
    w, h = 300, 112
    piece(ctx, P_rrect(cx - w / 2, cy - h / 2, w, h, 18), hexc("#f6f1e2"), lw=7)
    piece(ctx, P_rrect(cx + w / 2 - 2, cy - 24, 26, 48, 8), INK, lw=3, shadow=False)
    col = hexc("#2fb35a") if level > 0.5 else hexc("#f2b632") if level > 0.22 else hexc("#e23b3b")
    segs = 5
    on = math.ceil(level * segs - 1e-6)
    if level <= 0.22 and pose % 6 < 3:
        on = 0 if level < 0.12 else on
    for i in range(segs):
        if i < on:
            piece(ctx, P_rrect(cx - w / 2 + 14 + i * 55, cy - h / 2 + 14, 46, h - 28, 6), col, lw=3,
                  shadow=False)


def sc_chico(ctx, pose, lt, ev):
    t_cop = ev.get("poli_lt", 99)
    t_out = ev.get("salida_lt", 99)
    door_open = clamp((lt - (t_cop + 0.6)) / 0.6)
    bg_room(ctx, pose, door=True, door_open=door_open)
    lamp_hanging(ctx, 520, pose)
    dur = ev.get("dur", 12)
    tired = clamp(0.25 + 0.75 * lt / max(1, t_cop))
    droop = math.radians(-3 - 9 * tired) * (1 if (pose // 6) % 2 else 0.6)
    if lt > t_out:
        droop = math.radians(6)
    look = 1.0 if lt > t_cop + 0.4 else 0.0
    # chico: cuerpo, mesa delante, brazos sobre la mesa
    piece(ctx, P_rrect(380, 860, 220, 280, 16), hexc("#5d3a22"), lw=4)
    boy(ctx, 490, 1010, tired, droop, 0, look, pose)
    table_and_chairs(ctx, chair_back=False, chair_front=False)
    for side in (-1, 1):
        piece(ctx, P_rrect(490 + side * 120 - 45, 1195, 90, 70, 30), hexc("#ef7d2d"), lw=4)
        piece(ctx, P_ell(490 + side * 70, 1240, 34, 26), BOY_SKIN, lw=4)
    # batería que se vacía
    level = clamp(1 - lt / max(1.0, t_cop + 0.3))
    battery(ctx, 490, 742, max(0.04, level), pose)
    # policía
    if lt >= t_cop:
        k = clamp((lt - t_cop) / 0.4)
        x = lerp(1350, 735, ease_io(k))
        arm = math.radians(-12) if k < 1 else math.radians(-104 if pose % 6 < 3 or lt > t_out else -98)
        talking = ev.get("habla_ini_lt", 99) <= lt <= ev.get("habla_fin_lt", -1)
        talk = (1 if pose % 3 == 0 else 2 if pose % 3 == 1 else 0) if talking else 0
        cop(ctx, x, 1600, arm, talk, pose)


def video_camera(ctx, x, y, pose):
    # trípode
    for dx in (-110, 0, 110):
        line(ctx, [(x, y + 90), (x + dx, y + 560)], 12, hexc("#2d2f3a"))
    piece(ctx, P_rect(x - 30, y + 60, 60, 40), hexc("#2d2f3a"), lw=4)
    # cuerpo
    piece(ctx, P_rrect(x - 160, y - 90, 300, 160, 22), hexc("#3a3d48"), lw=5)
    piece(ctx, P_poly([(x + 140, y - 60), (x + 230, y - 100), (x + 230, y + 80), (x + 140, y + 40)]),
          hexc("#2d2f3a"), lw=5)
    piece(ctx, P_ell(x + 232, y - 10, 22, 90), hexc("#6f8fc8"), lw=4)
    piece(ctx, P_rrect(x - 130, y - 140, 150, 56, 12), hexc("#2d2f3a"), lw=4)
    piece(ctx, P_rrect(x - 140, y - 60, 120, 90, 10), hexc("#1d2433"), lw=4, shadow=False)
    on = (pose // 6) % 2 == 0
    piece(ctx, P_ell(x + 70, y - 50, 20), hexc("#ff2a2a") if on else hexc("#5a1414"), lw=3, shadow=False)
    if on:
        ctx.new_sub_path()
        ctx.arc(x + 70, y - 50, 36, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.2, 0.2, 0.3)
        ctx.fill()
    draw_text(ctx, "REC", x - 80, y - 15, 40, hexc("#ff4040") if on else hexc("#ffb0b0"), INK, 0)


def sc_camara(ctx, pose, lt, ev):
    dur = ev.get("dur", 6)
    e = ease_io(lt / max(1.0, dur))
    s = 1 + 1.25 * e
    clock = (800, 820)
    fx, fy = lerp(540, clock[0], e), lerp(960, clock[1] + 20, e)
    ctx.save()
    ctx.translate(540, 960)
    ctx.scale(s, s)
    ctx.translate(-fx, -fy)
    bg_room(ctx, pose)
    wall_clock(ctx, clock[0], clock[1], 112, lt * 60 * 3)
    lamp_hanging(ctx, 540, pose)
    table_and_chairs(ctx)
    ctx.restore()
    # la cámara está delante (menos zoom, paralaje)
    s2 = 1 + 0.2 * e
    ctx.save()
    ctx.translate(540, 960)
    ctx.scale(s2, s2)
    ctx.translate(-540 - 60 * e, -960 + 60 * e)
    video_camera(ctx, 250, 1260, pose)
    ctx.restore()
    # marco de visor REC
    on = (pose // 6) % 2 == 0
    for (x, y, dx, dy) in ((60, 680, 1, 1), (1020, 680, -1, 1), (60, 1420, 1, -1), (1020, 1420, -1, -1)):
        line(ctx, [(x, y + dy * 70), (x, y), (x + dx * 70, y)], 8, (1, 1, 1, 0.85), cairo.LINE_CAP_SQUARE)
    if on:
        piece(ctx, P_ell(110, 735, 15), hexc("#ff2a2a"), lw=3, shadow=False)
    draw_text(ctx, "REC", 140, 735, 40, (1, 1, 1), INK, 4, anchor="left")
    secs = int(lt * 60 * 6)
    tc = f"{secs // 3600:02d}:{secs // 60 % 60:02d}:{secs % 60:02d}"
    draw_text(ctx, tc, 990 - text_size(ctx, tc, 36).width, 735, 36, (1, 1, 1), INK, 4, anchor="left")


SCENES = dict(gancho=sc_gancho, parque=sc_parque, patrulla=sc_patrulla, interrogatorio=sc_interrogatorio,
              mazo=sc_mazo, celda=sc_celda, chico=sc_chico, camara=sc_camara)


# ─────────────────────────────── texto en pantalla ───────────────────────────────
CARD_COLS = [hexc("#e63946"), hexc("#1d4ed8"), hexc("#f59e0b"), hexc("#16a34a"), hexc("#7c3aed")]


def fit_size(ctx, txt, size, maxw):
    while size > 30 and text_size(ctx, txt, size).width > maxw:
        size -= 2
    return size


def card_text(ctx, txt, cx, cy, size, card_col, txt_col, tilt, k):
    """Rótulo de papel con animación 'pop' (k: 0→1 tiempo desde la entrada)."""
    if k <= 0:
        return
    sc = ease_out_back(clamp(k / 0.32)) if k < 0.32 else 1.0
    size = fit_size(ctx, txt, size, 900 if H > W else 1300)
    e = text_size(ctx, txt, size)
    pad_x, pad_y = 34, 26
    w, h = e.width + 2 * pad_x, size * 0.78 + 2 * pad_y
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(tilt + (1 - min(1, k / 0.32)) * math.radians(-8))
    ctx.scale(sc, sc)
    piece(ctx, P_poly([(-w / 2 - 6, -h / 2 + 4), (w / 2 + 4, -h / 2 - 3), (w / 2 + 8, h / 2 + 2),
                       (-w / 2 + 2, h / 2 + 5)]), card_col, lw=6, sh=(8, 10))
    draw_text(ctx, txt, 0, 0, size, txt_col, INK, 0 if txt_col == INK else 7)
    ctx.restore()


def draw_pantalla(ctx, t, tl):
    for blk in tl["bloques"]:
        if not (blk["t0"] <= t < blk["t1"]):
            continue
        items = blk["pantalla_t"]
        bi = blk["idx"]
        if blk.get("modo_pantalla") == "pila":
            n = len(items)
            y0 = TOP_Y() - 70
            for i, (ts, txt) in enumerate(items):
                col = hexc("#ffe14d") if i == n - 1 else (1, 1, 1)
                card = hexc("#e63946") if i == n - 1 else CARD_COLS[(i + 1) % len(CARD_COLS)]
                tilt = math.radians(-3 if i % 2 else 2.5)
                card_text(ctx, txt, W / 2 + (-40 if i % 2 else 40) * (i < n - 1), y0 + i * 118, 86, card,
                          col, tilt, t - ts)
        else:
            cur = None
            for i, (ts, txt) in enumerate(items):
                if t >= ts:
                    cur = (i, ts, txt)
            if cur:
                i, ts, txt = cur
                card = CARD_COLS[(bi + i) % len(CARD_COLS)]
                tilt = math.radians(-2.5 if (i + bi) % 2 else 2)
                big = 104 if len(txt) < 16 else 92
                card_text(ctx, txt, W / 2, TOP_Y(), big, card, (1, 1, 1), tilt, t - ts)


# ─────────────────────────────── subtítulos ───────────────────────────────
def build_chunks(words):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["text"] for x in cur)
        if len(cur) >= 3 or len(txt) > 16 or re.search(r"[.,?!;:\"]$", w["text"]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        t0 = c[0]["start"]
        t1 = c[-1]["end"]
        if i + 1 < len(chunks):
            nxt = chunks[i + 1][0]["start"]
            if nxt - t1 < 0.6:
                t1 = nxt
        out.append(dict(words=c, t0=t0, t1=t1))
    return out


def draw_subs(ctx, t, chunks):
    ch = None
    for c in chunks:
        if c["t0"] <= t < c["t1"] + 0.05:
            ch = c
            break
    if not ch:
        return
    words = [w["text"].upper().replace('"', "").replace("«", "").replace("»", "") for w in ch["words"]]
    size = 82
    ctx.select_font_face(FONT, 0, 0)
    while True:
        ctx.set_font_size(size)
        space = size * 0.36
        widths = [ctx.text_extents(w).x_advance for w in words]
        total = sum(widths) + space * (len(words) - 1)
        if total <= (960 if H > W else 1500) or size <= 44:
            break
        size -= 2
    x = W / 2 - total / 2
    y = SUB_Y()
    cur_i = 0
    for i, w in enumerate(ch["words"]):
        if t >= w["start"]:
            cur_i = i
    for i, (wtxt, wd) in enumerate(zip(words, widths)):
        col = hexc("#ffe14d") if i == cur_i else (1, 1, 1)
        ctx.save()
        if i == cur_i:
            ctx.translate(x + wd / 2, y)
            ctx.scale(1.08, 1.08)
            ctx.translate(-(x + wd / 2), -y)
        ctx.move_to(x, y)
        ctx.text_path(wtxt)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(14)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
        set_col(ctx, col)
        ctx.fill()
        ctx.restore()
        x += wd + space


# ─────────────────────────────── voz (ElevenLabs) ───────────────────────────────
def eleven_request(path, payload=None, method="GET"):
    key = os.environ.get("ELEVENLABS_API_KEY")
    req = urllib.request.Request("https://api.elevenlabs.io" + path, method=method,
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    data = json.dumps(payload).encode() if payload is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs {e.code}: {e.read().decode(errors='ignore')[:500]}")


VOZ_POR_DEFECTO = "hyKxCTlAqtnW188CgltM"   # «Salva – The Spanish Voice» (preferencia del usuario)


def pick_voice():
    v = os.environ.get("ELEVENLABS_VOICE_ID", VOZ_POR_DEFECTO)
    if v:
        return v
    voices = eleven_request("/v1/voices").get("voices", [])
    if not voices:
        raise SystemExit("No hay voces en la cuenta: define ELEVENLABS_VOICE_ID en .env")
    def score(vc):
        lab = json.dumps(vc.get("labels", {})).lower() + vc.get("name", "").lower()
        return ("spanish" in lab or "español" in lab or "es" == vc.get("labels", {}).get("language", "")) * 2 + \
               ("narrat" in lab) * 1
    voices.sort(key=score, reverse=True)
    print(f"  · Voz elegida automáticamente: {voices[0]['name']} ({voices[0]['voice_id']}). "
          f"Cámbiala con ELEVENLABS_VOICE_ID.")
    return voices[0]["voice_id"]


def tts_block(i, voice_id):
    """Devuelve (ruta_wav, palabras[{text,start,end}], duración). Usa caché en disco."""
    blk = BLOQUES[i]
    model = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_v4")
    speed = float(os.environ.get("ELEVENLABS_SPEED", "1.0"))
    payload = dict(text=blk["voz"], model_id=model,
                   voice_settings=dict(stability=0.45, similarity_boost=0.8, style=0.25,
                                       use_speaker_boost=True, speed=speed),
                   previous_text=BLOQUES[i - 1]["voz"] if i > 0 else None,
                   next_text=BLOQUES[i + 1]["voz"] if i + 1 < len(BLOQUES) else None)
    payload = {k: v for k, v in payload.items() if v is not None}
    key = hashlib.sha1(json.dumps([voice_id, payload], sort_keys=True).encode()).hexdigest()[:16]
    os.makedirs(CACHE_DIR, exist_ok=True)
    jpath = os.path.join(CACHE_DIR, f"{blk['id']}_{key}.json")
    mpath = os.path.join(CACHE_DIR, f"{blk['id']}_{key}.mp3")
    wpath = os.path.join(CACHE_DIR, f"{blk['id']}_{key}.wav")
    if not os.path.exists(jpath):
        print(f"  · ElevenLabs: generando bloque «{blk['id']}» …")
        res = eleven_request(f"/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128",
                             payload, "POST")
        with open(mpath, "wb") as f:
            f.write(base64.b64decode(res["audio_base64"]))
        json.dump(dict(alignment=res.get("alignment"), normalized=res.get("normalized_alignment")),
                  open(jpath, "w"), ensure_ascii=False)
    else:
        print(f"  · Bloque «{blk['id']}» en caché")
    if not os.path.exists(wpath):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mpath, "-ac", "1", "-ar", str(SR), wpath],
                       check=True)
    al = json.load(open(jpath))["alignment"]
    words = chars_to_words(al["characters"], al["character_start_times_seconds"],
                           al["character_end_times_seconds"])
    audio = read_wav(wpath)
    return audio, words, len(audio) / SR


def chars_to_words(chars, st, en):
    words, cur, s, e = [], "", None, None
    for ch, a, b in zip(chars, st, en):
        if ch.isspace():
            if cur:
                words.append(dict(text=cur, start=s, end=e))
            cur, s = "", None
            continue
        if s is None:
            s = a
        cur += ch
        e = b
    if cur:
        words.append(dict(text=cur, start=s, end=e))
    return words


def approx_words(text):
    """Tiempos aproximados (modo prueba): ~2,8 palabras/s con pausas en la puntuación."""
    nums = {"1989": 1.35, "2002": 0.95, "14": 0.4, "16": 0.4, "6": 0.3, "13": 0.4}
    t, out = 0.05, []
    for w in text.split():
        core = re.sub(r"[^\w]", "", w)
        d = nums.get(core, 0.07 + 0.052 * len(core))
        out.append(dict(text=w, start=t, end=t + d))
        t += d + 0.03
        if re.search(r"[.?!]\"?$", w):
            t += 0.38
        elif re.search(r"[,;:]\"?$", w):
            t += 0.18
    return out, t + 0.1


def read_wav(p):
    with wave.open(p) as wf:
        n = wf.getnframes()
        data = np.frombuffer(wf.readframes(n), np.int16).astype(np.float32) / 32768
        if wf.getnchannels() > 1:
            data = data.reshape(-1, wf.getnchannels()).mean(1)
    return data


def write_wav(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, "wb") as wf:
        wf.setnchannels(2 if x.ndim == 2 else 1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((x * 32767).astype(np.int16).tobytes())


# ─────────────────────────────── música (procedural, sin copyright) ───────────────────────────────
def make_music(dur, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    R = np.zeros(n)
    # dron grave (La menor) con batido lento
    for f, a in ((55.0, 0.5), (82.41, 0.28), (110.0, 0.18), (130.81, 0.08)):
        L += a * np.sin(2 * np.pi * f * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t))
        R += a * np.sin(2 * np.pi * f * 1.003 * t + 0.4) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * t + 1))
    # tensión aguda (segunda menor) que respira
    sw = 0.5 - 0.5 * np.cos(2 * np.pi * t / 11)
    L += 0.035 * sw * np.sin(2 * np.pi * 880 * t)
    R += 0.035 * sw * np.sin(2 * np.pi * 932.33 * t)
    # latido suave
    beat = 60 / 76
    k = 0
    while k * beat < dur:
        for off, amp in ((0, 0.55), (0.24, 0.35)):
            st = int((k * beat + off) * SR)
            m = int(0.35 * SR)
            if st + m < n:
                tt = np.arange(m) / SR
                thump = amp * np.sin(2 * np.pi * (52 + 30 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)
                L[st:st + m] += thump
                R[st:st + m] += thump
        k += 1
    # pizzicato ocasional
    notes = [220.0, 261.63, 293.66, 329.63, 392.0, 440.0]
    tpos = 2.0
    while tpos < dur - 1:
        f = notes[rng.integers(len(notes))]
        st = int(tpos * SR)
        m = int(1.2 * SR)
        if st + m < n:
            tt = np.arange(m) / SR
            p = 0.10 * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 4.5)
            pan = rng.uniform(0.3, 0.7)
            L[st:st + m] += p * (1 - pan)
            R[st:st + m] += p * pan
        tpos += beat * rng.choice([2, 3, 4])
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    out = np.stack([L, R], 1) * fade[:, None]
    return out / (np.abs(out).max() + 1e-9)


def rms(x):
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


# ─────────────────────────────── línea de tiempo ───────────────────────────────
def find_phrase(words, phrase, start=0):
    toks = [norm(x) for x in phrase.split()]
    nw = [norm(w["text"]) for w in words]
    for i in range(start, len(words) - len(toks) + 1):
        if nw[i:i + len(toks)] == toks:
            return i
    for i in range(0, len(words) - len(toks) + 1):
        if nw[i:i + len(toks)] == toks:
            return i
    raise SystemExit(f"No encuentro la frase «{phrase}» en el texto alineado")


NARR_JSON = os.path.join(CACHE_DIR, "narracion_palabras.json")
NARR_MP3 = os.path.join(CACHE_DIR, "narracion.mp3")
LEAD = 0.25
TEMPO_MAX = 1.07


def narracion_cacheada():
    """Narración completa ya generada (un solo mp3 + tiempos por palabra), si existe."""
    if not os.path.exists(NARR_JSON):
        return None
    d = json.load(open(NARR_JSON, encoding="utf-8"))
    words = d["palabras"]
    script = [w for b in BLOQUES for w in b["voz"].split()]
    if [norm(w) for w in script] != [norm(w["text"]) for w in words]:
        print("  · narracion_palabras.json no coincide con el guion actual: se ignora")
        return None
    audio = None
    if os.path.exists(NARR_MP3):
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "csv=p=0", NARR_MP3], capture_output=True, text=True).stdout)
        # si no cabe en el short, se acelera un poco sin cambiar el tono (atempo)
        tempo = max(1.0, (dur + LEAD + TAIL) / (MAX_DUR - 0.5))
        if tempo > TEMPO_MAX:
            print(f"  ⚠  Haría falta acelerar ×{tempo:.2f}; se limita a ×{TEMPO_MAX}. Considera recortar texto.")
            tempo = TEMPO_MAX
        wav = NARR_MP3[:-4] + f"_x{tempo:.3f}.wav"
        # se rehace si la voz es más nueva que la copia (si no, se montaría una voz antigua con tiempos nuevos)
        if not os.path.exists(wav) or os.path.getmtime(wav) < os.path.getmtime(NARR_MP3):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", NARR_MP3, "-af", f"atempo={tempo:.4f}",
                            "-ac", "1", "-ar", str(SR), wav], check=True)
        if tempo > 1.0:
            print(f"  · Voz acelerada ×{tempo:.3f} ({dur:.1f}s → {dur / tempo:.1f}s), mismo tono")
        words = [dict(w, start=w["start"] / tempo, end=w["end"] / tempo) for w in words]
        audio = read_wav(wav)
    return words, audio


def build_timeline_narracion(words, audio):
    bloques, all_words = [], []
    k = 0
    groups = []
    for b in BLOQUES:
        n = len(b["voz"].split())
        groups.append(words[k:k + n])
        k += n
    last_end = (len(audio) / SR if audio is not None else words[-1]["end"]) + LEAD
    total = max(last_end, words[-1]["end"] + LEAD) + TAIL
    starts = [0.0] + [g[0]["start"] + LEAD - 0.2 for g in groups[1:]]
    for i, (b, g) in enumerate(zip(BLOQUES, groups)):
        gw = [dict(w, start=w["start"] + LEAD, end=w["end"] + LEAD, block=i) for w in g]
        t0 = starts[i]
        t1 = starts[i + 1] if i + 1 < len(BLOQUES) else total
        blk = make_block(i, b, gw, t0, t1, LEAD, g[-1]["end"] - g[0]["start"])
        bloques.append(blk)
        all_words += gw
    return finish_timeline(bloques, all_words, [audio], total)


def make_block(i, b, gw, t0, t1, audio_at, d):
    cue = lambda ph: gw[find_phrase(gw, ph)]["start"] - 0.05 if ph else t0
    blk = dict(idx=i, id=b["id"], t0=t0, t1=t1, audio_at=audio_at, dur=d,
               modo_pantalla=b.get("modo_pantalla"),
               pantalla_t=[(cue(ph), txt) for ph, txt in b["pantalla"]],
               escenas_t=[(cue(ph), name) for ph, name in b["escenas"]],
               eventos_t={k: cue(ph) for k, ph in b["eventos"].items()})
    if b.get("habla"):
        a, z = b["habla"]
        ia = find_phrase(gw, a)
        iz = find_phrase(gw, z, ia)
        blk["eventos_t"]["habla_ini"] = gw[ia]["start"]
        blk["eventos_t"]["habla_fin"] = gw[iz]["end"]
    return blk


def finish_timeline(bloques, all_words, audios, total):
    segs = []
    for blk in bloques:
        es = blk["escenas_t"]
        for j, (ts, name) in enumerate(es):
            te = es[j + 1][0] if j + 1 < len(es) else blk["t1"]
            ts = blk["t0"] if j == 0 else ts
            segs.append(dict(name=name, t0=ts, t1=te, blk=blk))
    for s in segs:
        ev = {"dur": s["t1"] - s["t0"]}
        for k, v in s["blk"]["eventos_t"].items():
            ev[k] = v
            ev[k + "_lt"] = v - s["t0"]
        s["ev"] = ev
    return dict(bloques=bloques, words=all_words, segs=segs, total=total, audios=audios)


def build_timeline(prueba, voice_id=None):
    bloques, all_words, audios = [], [], []
    t = 0.25
    for i, b in enumerate(BLOQUES):
        if prueba:
            words, d = approx_words(b["voz"])
            audio = None
        else:
            audio, words, d = tts_block(i, voice_id)
        gw = [dict(w, start=w["start"] + t, end=w["end"] + t, block=i) for w in words]
        t0 = t if i > 0 else 0.0
        t1 = t + d + (GAP if i + 1 < len(BLOQUES) else TAIL)
        cue = lambda ph: gw[find_phrase(gw, ph)]["start"] - 0.05 if ph else t0
        blk = dict(idx=i, id=b["id"], t0=t0, t1=t1, audio_at=t, dur=d,
                   modo_pantalla=b.get("modo_pantalla"),
                   pantalla_t=[(cue(ph), txt) for ph, txt in b["pantalla"]],
                   escenas_t=[(cue(ph), name) for ph, name in b["escenas"]],
                   eventos_t={k: cue(ph) for k, ph in b["eventos"].items()})
        if b.get("habla"):
            a, z = b["habla"]
            ia = find_phrase(gw, a)
            iz = find_phrase(gw, z, ia)
            blk["eventos_t"]["habla_ini"] = gw[ia]["start"]
            blk["eventos_t"]["habla_fin"] = gw[iz]["end"]
        bloques.append(blk)
        all_words += gw
        audios.append(audio)
        t = t1
    total = bloques[-1]["t1"]
    # segmentos de escena
    segs = []
    for blk in bloques:
        es = blk["escenas_t"]
        for j, (ts, name) in enumerate(es):
            te = es[j + 1][0] if j + 1 < len(es) else blk["t1"]
            ts = blk["t0"] if j == 0 else ts
            segs.append(dict(name=name, t0=ts, t1=te, blk=blk))
    for s in segs:
        ev = {"dur": s["t1"] - s["t0"]}
        for k, v in s["blk"]["eventos_t"].items():
            ev[k] = v
            ev[k + "_lt"] = v - s["t0"]
        s["ev"] = ev
    return dict(bloques=bloques, words=all_words, segs=segs, total=total, audios=audios)


# ─────────────────────────────── render ───────────────────────────────
class Renderer:
    def __init__(self, tl):
        self.tl = tl
        self.tex = make_paper_texture()
        self.scene = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.frame = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.key = None
        self.chunks = build_chunks(tl["words"])

    def seg_at(self, t):
        for s in self.tl["segs"]:
            if s["t0"] <= t < s["t1"]:
                return s
        return self.tl["segs"][-1]

    def render_scene(self, t):
        pose = int(math.floor(t * POSES + 1e-6))
        tq = pose / POSES                       # tiempo cuantizado: 12 poses/s
        seg = self.seg_at(t)
        key = (id(seg), pose)
        if key == self.key:
            return
        self.key = key
        ctx = cairo.Context(self.scene)
        ctx.set_antialias(cairo.ANTIALIAS_GOOD)
        lt = max(0.0, tq - seg["t0"])
        SCENES[seg["name"]](ctx, pose, lt, seg["ev"])
        if ESTILO != "recortes":
            import estilos
            estilos.post(self.scene, ctx, pose)
        tex = 0.42 if ESTILO == "recortes" else __import__("estilos").TEXTURA.get(ESTILO, 0)
        if tex:
            ctx.set_operator(cairo.OPERATOR_OVERLAY)
            ctx.set_source_surface(self.tex)
            ctx.paint_with_alpha(tex)
            ctx.set_operator(cairo.OPERATOR_OVER)
        # viñeta suave
        rr = max(W, H) / 1920
        g = cairo.RadialGradient(W / 2, H / 2, 600 * rr, W / 2, H / 2, 1250 * rr)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.35)
        ctx.set_source(g)
        ctx.paint()

    def render(self, t):
        self.render_scene(t)
        ctx = cairo.Context(self.frame)
        ctx.set_source_surface(self.scene)
        ctx.paint()
        draw_pantalla(ctx, t, self.tl)
        draw_subs(ctx, t, self.chunks)
        self.frame.flush()
        return self.frame


def mix_audio(tl, prueba, path):
    total = tl["total"]
    n = int(math.ceil(total * SR)) + SR
    voice = np.zeros(n)
    if tl.get("narracion"):
        a = tl["audios"][0]
        if a is not None:
            st = int(LEAD * SR)
            voice[st:st + len(a)] += a[: n - st]
        else:
            prueba = True
    elif not prueba:
        for blk, a in zip(tl["bloques"], tl["audios"]):
            st = int(blk["audio_at"] * SR)
            voice[st:st + len(a)] += a[: n - st]
    music = make_music(n / SR)
    if prueba:
        v_rms = 10 ** (-18 / 20)                       # voz nominal de referencia
    else:
        act = voice[np.abs(voice) > 0.02]
        v_rms = rms(act) if len(act) else 0.1
    music *= v_rms * 10 ** (MUSIC_DB / 20) / rms(music)
    m = min(len(music), len(voice))           # make_music puede devolver un sample de menos
    mix = music[:m] + voice[:m, None]
    mix *= 0.89 / (np.abs(mix).max() + 1e-9)      # normaliza a -1 dBFS de pico
    write_wav(path, mix)
    return 20 * math.log10(rms(music) / v_rms)


PROCESOS = int(os.environ.get("CR_RENDER_PROCESOS", "0")) or (os.cpu_count() or 1)
CALENTAR = 1.5          # s que cada trozo pinta antes de empezar (sin guardar) para que las transiciones salgan igual


def _trozo(args):
    """Pinta los fotogramas [i0, i1) en su propio mp4 (solo vídeo). Se ejecuta en un proceso aparte."""
    tl, i0, i1, ruta, kf, keydir = args
    r = Renderer(tl)
    for i in range(max(0, i0 - int(CALENTAR * FPS)), i0):
        r.render(i / FPS)                               # calentar: deja el estado (transiciones) como en un render seguido
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-threads", "2", ruta]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(i0, i1):
        surf = r.render(i / FPS)
        p.stdin.write(bytes(surf.get_data()))
        if i in kf:
            surf.write_to_png(os.path.join(keydir, kf[i]))
    p.stdin.close()
    p.wait()
    return p.returncode


def encode(tl, out_mp4, wav, keyframes=None, keydir=None):
    nframes = int(math.ceil(tl["total"] * FPS))
    kf = {int(round(k * FPS)): name for name, k in (keyframes or {}).items()}
    n = min(PROCESOS, max(1, nframes // 120))
    if n > 1 and sys.platform != "win32":
        return encode_paralelo(tl, out_mp4, wav, kf, keydir, nframes, n)
    r = Renderer(tl)
    nframes = int(math.ceil(tl["total"] * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-ar", str(SR), "-shortest", "-movflags", "+faststart", out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        t = i / FPS
        surf = r.render(t)
        p.stdin.write(bytes(surf.get_data()))
        if i in kf:
            surf.write_to_png(os.path.join(keydir, kf[i]))
        if i % 150 == 0:
            print(f"\r  · Render {i}/{nframes}", end="", flush=True)
    p.stdin.close()
    p.wait()
    print(f"\r  · Render {nframes}/{nframes} ✔")
    if p.returncode:
        raise SystemExit("ffmpeg falló")


def encode_paralelo(tl, out_mp4, wav, kf, keydir, nframes, n):
    """Igual que encode(), pero repartiendo los fotogramas entre n procesos (uno por núcleo) y uniendo los trozos."""
    import multiprocessing as mp
    import tempfile
    tmp = tempfile.mkdtemp(prefix="render-", dir=OUT_DIR)
    cortes = [round(k * nframes / n) for k in range(n + 1)]
    trabajos = [(tl, cortes[k], cortes[k + 1], os.path.join(tmp, f"t{k:02d}.mp4"), kf, keydir) for k in range(n)]
    print(f"  · Render en {n} procesos a la vez ({nframes} fotogramas)", flush=True)
    with mp.get_context("fork").Pool(n) as pool:
        codigos = pool.map(_trozo, trabajos)
    if any(codigos):
        raise SystemExit("ffmpeg falló en un trozo del render")
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.writelines(f"file '{t[3]}'\n" for t in trabajos)
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", wav,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
                        "-shortest", "-movflags", "+faststart", out_mp4])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  · Render {nframes}/{nframes} ✔")
    if r.returncode:
        raise SystemExit("ffmpeg falló al unir los trozos")


def thumbnail(path):
    tl = dict(bloques=[], segs=[], words=[], total=1)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    sc_gancho(ctx, 3, 0.0, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(make_paper_texture(11))
    ctx.paint_with_alpha(0.55)
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.paint()
    lines = [("¿POR QUÉ", hexc("#e63946"), (1, 1, 1)), ("CONFESARON", hexc("#ffe14d"), INK),
             ("UN CRIMEN QUE", hexc("#1d4ed8"), (1, 1, 1)), ("NO COMETIERON?", hexc("#e63946"), (1, 1, 1))]
    for i, (txt, cc, tc) in enumerate(lines):
        card_text(ctx, txt, 540, 250 + i * 150, 116, cc, tc, math.radians(-3 if i % 2 else 2.5), 1.0)
    # sello
    with rot(ctx, 540, 1690, math.radians(-6)):
        piece(ctx, P_rrect(240, 1615, 600, 150, 20), hexc("#16a34a"), lw=7, sh=(8, 10))
        draw_text(ctx, "ERAN INOCENTES", 540, 1690, 64, (1, 1, 1), INK, 6)
    surf.write_to_png(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true", help="sin voz, duraciones aproximadas")
    ap.add_argument("--voz", help="voice_id de ElevenLabs")
    args = ap.parse_args()
    load_env()
    if args.voz:
        os.environ["ELEVENLABS_VOICE_ID"] = args.voz
    os.makedirs(OUT_DIR, exist_ok=True)

    prueba = args.prueba
    narr = None if prueba else narracion_cacheada()
    if narr:
        print("1/4 Voz y tiempos (narración en caché: cache_audio/)")
        if narr[1] is None:
            print("  ⚠  Falta cache_audio/narracion.mp3: se usan los tiempos reales pero el vídeo saldrá sin voz")
        tl = build_timeline_narracion(*narr)
        tl["narracion"] = True
        prueba = narr[1] is None
    else:
        if not prueba and not os.environ.get("ELEVENLABS_API_KEY"):
            raise SystemExit("Falta ELEVENLABS_API_KEY en .env (o usa --prueba)")
        print("1/4 Voz y tiempos" + (" (aproximados, sin voz)" if prueba else ""))
        voice_id = None if prueba else pick_voice()
        tl = build_timeline(prueba, voice_id)
    total = tl["total"]
    for b in tl["bloques"]:
        print(f"  · {b['id']:<12} {b['t0']:6.2f}s → {b['t1']:6.2f}s  ({b['t1'] - b['t0']:.2f}s)")
    print(f"  · Duración total: {total:.2f}s")
    if total > MAX_DUR:
        print(f"\n⚠  El vídeo dura {total:.1f}s y supera {MAX_DUR:.0f}s. Recortes propuestos:")
        for r in RECORTES_SUGERIDOS:
            print("     -", r)
        print("   (o sube ELEVENLABS_SPEED a 1.05-1.1 en .env)\n")

    print("2/4 Audio (voz + música a -20 dB)")
    suffix = "-prueba" if prueba else ""
    wav = os.path.join(OUT_DIR, f"audio-{SALIDA}{suffix}.wav")
    rel = mix_audio(tl, prueba, wav)
    print(f"  · Música a {rel:.1f} dB respecto a la voz")

    print("3/4 Animación")
    out = os.path.join(OUT_DIR, f"{SALIDA}{suffix}.mp4")
    keydir = os.path.join(OUT_DIR, f"fotogramas-{SALIDA}" + suffix)
    os.makedirs(keydir, exist_ok=True)
    segs = tl["segs"]
    kf = {}
    for s in ([] if os.environ.get("CR_RAPIDO") == "1" else segs):     # la web no necesita fotogramas de revisión
        mid = s["t0"] + (s["t1"] - s["t0"]) * (0.75 if s["name"] in ("celda", "chico", "camara") else 0.5)
        kf[f"{s['t0']:05.1f}s_{s['name']}.png"] = mid
    encode(tl, out, wav, kf, keydir)

    print("4/4 Miniatura")
    mini = os.path.join(OUT_DIR, f"miniatura-{SALIDA}.png")
    thumbnail(mini)
    print(f"\n✔ {out}\n✔ {mini}\n✔ fotogramas clave en {keydir}")
    if total > MAX_DUR:
        print(f"⚠  Recuerda: dura {total:.1f}s (> {MAX_DUR:.0f}s)")


if __name__ == "__main__":
    main()
