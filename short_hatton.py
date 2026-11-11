#!/usr/bin/env python3
"""
Short 21 · «La banda de abuelos que vació una cámara acorazada» — Hatton Garden, Londres, 2015
Voz gratuita (python voz_gratis.py short_hatton.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, fondo, noche, silueta
from short_robo_siglo import pared_cajas, saco

SLUG = "hatton-garden"
PRONUNCIA = {"Hatton Garden": "Játon Gárden"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que uno de los mayores robos de Inglaterra lo hizo una banda… cuyo líder "
             "tenía 76 años?"),
        escenas=[(None, "abuelos")],
        pantalla=[("uno de", "UNO DE LOS MAYORES ROBOS"), ("cuyo líder", "¿CON 76 AÑOS?")],
        eventos={"lider": "cuyo líder"},
    ),
    dict(
        id="caso",
        voz=("Londres, Semana Santa de 2015. Aprovechando el puente, la banda entra en un edificio de cajas de "
             "seguridad en Hatton Garden, baja por el hueco del ascensor y llega hasta la cámara."),
        escenas=[(None, "fachada"), ("baja por", "ascensor")],
        pantalla=[(None, "LONDRES, 2015"), ("Aprovechando", "PUENTE DE SEMANA SANTA"), ("baja por", "POR EL HUECO DEL ASCENSOR")],
        eventos={"entra": "la banda", "camara": "hasta la"},
    ),
    dict(
        id="muro",
        voz=("Allí, con una perforadora de diamante, abren tres agujeros en un muro de hormigón de medio metro. "
             "Durante dos noches, vacían decenas de cajas."),
        escenas=[(None, "taladro"), ("Durante dos", "cajas")],
        pantalla=[(None, "PERFORADORA DE DIAMANTE"), ("en un", "MURO DE 50 CM"), ("Durante dos", "2 NOCHES")],
        eventos={"agujeros": "tres agujeros"},
    ),
    dict(
        id="botin",
        voz=("Se llevan unos 14 millones de libras en joyas, oro y dinero. Pero las cámaras de la calle los "
             "delatan, y en mayo la policía los detiene."),
        escenas=[(None, "botin"), ("Pero las", "camaras")],
        pantalla=[(None, "≈ 14 MILLONES DE £"), ("Pero las", "LAS CÁMARAS LOS DELATAN"), ("en mayo", "¡DETENIDOS!")],
        eventos={"detiene": "la policía"},
    ),
    dict(
        id="cierre",
        voz="Los abuelos del robo acabaron en prisión, y parte del botín nunca apareció. ¿Te lo habrías imaginado?",
        escenas=[(None, "carcel")],
        pantalla=[(None, "EN PRISIÓN"), ("y parte", "PARTE DEL BOTÍN, SIN APARECER"), ("Te lo", "¿TE LO IMAGINABAS?")],
        eventos={"parte": "y parte", "pregunta": "Te lo"},
    ),
]


def abuelo(ctx, x, feet, s, pose, k=0, gorra=False):
    """Silueta sin rasgos con bastón y pelo cano: los autores son personas reales."""
    silueta(ctx, x, feet, s, pose, k)
    hy = feet - (230 + 65) * s
    ctx.new_sub_path()
    ctx.arc(x, hy, 66 * s, math.radians(200), math.radians(340))
    set_col(ctx, hexc("#d9d9d9"))
    ctx.set_line_width(10 * s)
    ctx.stroke()
    if gorra:
        piece(ctx, P_poly([(x - 70 * s, hy - 30 * s), (x + 90 * s, hy - 30 * s), (x + 60 * s, hy - 70 * s), (x - 60 * s, hy - 70 * s)]),
              hexc("#5b6475"), lw=3, shadow=False)
    line(ctx, [(x + 80 * s, feet - 120 * s), (x + 95 * s, feet)], 8 * s, hexc("#7a4e2c"))
    ctx.new_sub_path()
    ctx.arc(x + 65 * s, feet - 120 * s, 16 * s, math.pi, 2 * math.pi)
    ctx.stroke()


def taladro(ctx, x, y, s, pose):
    piece(ctx, P_rect(x - 40 * s, y - 260 * s, 80 * s, 300 * s), hexc("#e63946"), lw=4)
    piece(ctx, P_rect(x - 120 * s, y + 30 * s, 240 * s, 30 * s), hexc("#3d3f4a"), lw=3)
    piece(ctx, P_rrect(x - 30 * s, y - 120 * s, 200 * s, 70 * s, 16 * s), hexc("#c8202f"), lw=4)
    piece(ctx, P_rect(x + 170 * s, y - 100 * s, 120 * s, 30 * s), hexc("#c9ccd6"), lw=3)
    if pose % 2 == 0:
        for i in range(5):
            a = math.radians(-60 + i * 30)
            line(ctx, [(x + 300 * s, y - 85 * s), (x + 300 * s + 50 * s * math.cos(a), y - 85 * s + 50 * s * math.sin(a))],
                 5, hexc("#d9d2c0"))


# ─────────────────────────────── escenas ───────────────────────────────
def sc_abuelos(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i in range(4):
        abuelo(ctx, 180 + i * 240, 1330, 1.0, pose, i, gorra=i % 2 == 0)
    tl = since(ev, "lider", lt)
    if tl >= 0:
        stamp(ctx, 180, 900, "76 AÑOS", tl, 54, col=ROJO, ang=-8)


def sc_fachada(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    piece(ctx, P_rect(200, 560, 680, 770), hexc("#8a6a5a"), lw=5)
    for r in range(4):
        for c in range(4):
            piece(ctx, P_rect(250 + c * 160, 610 + r * 150, 100, 100), hexc("#ffe58a") if (r + c) % 5 == 0 else hexc("#2b2d40"),
                  lw=3, shadow=False)
    piece(ctx, P_rect(470, 1150, 140, 180), hexc("#3d2614"), lw=4)
    piece(ctx, P_rrect(380, 1080, 320, 50, 10), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "CAJAS DE SEGURIDAD", 540, 1115, 26, INK, anchor="center")
    te = since(ev, "entra", lt)
    if te >= 0:
        for i in range(3):
            k = clamp((te - i * 0.3) / 1.2)
            if k < 1:
                abuelo(ctx, lerp(100 - i * 80, 540, k), 1330, 0.6, pose, i)
    piece(ctx, P_rect(-10, 1300, 1100, 40), hexc("#6b6f78"), lw=0, shadow=False, outline=False)


def sc_ascensor(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", None)
    piece(ctx, P_rect(340, 520, 400, 1440), hexc("#1a1d24"), lw=5)
    for y in range(560, 1500, 120):
        line(ctx, [(340, y), (740, y)], 4, hexc("#3d3f4a"))
    line(ctx, [(520, 520), (520, 1500)], 6, hexc("#9aa0ab"))
    line(ctx, [(560, 520), (560, 1500)], 6, hexc("#9aa0ab"))
    for i in range(2):
        y = lerp(560, 1150, clamp((lt - i * 0.4) / 2.0))
        silueta(ctx, 470 + i * 140, y + 250, 0.7, pose, i)
    tc = since(ev, "camara", lt)
    if tc >= 0:
        stamp(ctx, 540, 1330, "LA CÁMARA", tc, 56, col=hexc("#ffe14d"), ang=-6)


def sc_taladro(ctx, pose, lt, ev):
    fondo(ctx, "#5b6475", 1330, "#3d3f4a")
    piece(ctx, P_rect(600, 540, 480, 790), hexc("#9aa0ab"), lw=5)
    for i in range(30):
        piece(ctx, P_ell(620 + hnoise("hm", i) * 440, 560 + hnoise("hm", i, "y") * 760, 8), hexc("#7a7f8a"), lw=0,
              shadow=False, outline=False)
    ta = since(ev, "agujeros", lt)
    n = 0 if ta < 0 else min(3, 1 + int(ta / 0.5))
    for i in range(n):
        piece(ctx, P_ell(700 + i * 60, 900 + (i % 2) * 50, 70), hexc("#1a1d24"), lw=4)
    for lx in (230, 420):
        piece(ctx, P_rect(lx, 1020, 24, 310), hexc("#3d3f4a"), lw=3, shadow=False)
    taladro(ctx, 330, 960, 1.0, pose)
    abuelo(ctx, 160, 1330, 0.9, pose)
    piece(ctx, P_rrect(620, 1180, 300, 90, 14), hexc("#1d2433"), lw=4)
    txt(ctx, "50 CM", 770, 1245, 60, hexc("#ffe14d"), anchor="center")


def sc_cajas(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1330, "#262a3a")
    n = int(clamp(lt / 2.0) * 50)
    pared_cajas(ctx, 90, 560, 10, 6, 92, 92, n)
    for i in range(3):
        saco(ctx, 250 + i * 290, 1250, 0.6)


def sc_botin(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i in range(int(clamp(lt / 1.0) * 9)):
        r, c = divmod(i, 3)
        x, y = 300 + c * 240, 700 + r * 170
        kind = (r + c) % 3
        if kind == 0:
            piece(ctx, P_poly([(x, y - 60), (x + 60, y), (x, y + 60), (x - 60, y)]), hexc("#bfe8ff"), lw=4)
        elif kind == 1:
            piece(ctx, P_rrect(x - 70, y - 30, 140, 60, 8), ORO, lw=4)
        else:
            piece(ctx, P_ell(x, y, 55), hexc("#e8b830"), lw=4)
            piece(ctx, P_ell(x, y, 30), hexc("#2d3557"), lw=3, shadow=False)
    piece(ctx, P_rrect(260, 1220, 560, 90, 14), hexc("#1d2433"), lw=4)
    v = int(14 * ease_io(clamp(lt / 1.0)))
    txt(ctx, f"{v} MILLONES £", 540, 1285, 54, hexc("#9fd6a0"), anchor="center")


def sc_camaras(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fb0c4"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 660), hexc("#6b6f78"), lw=4, shadow=False)
    for i, x in enumerate((180, 540, 900)):
        line(ctx, [(x, 1300), (x, 700)], 12, hexc("#3d3f4a"))
        with rot(ctx, x, 700, math.radians(15 * (1 if (pose // 6 + i) % 2 else -1))):
            piece(ctx, P_rrect(x - 30, 650, 150, 60, 12), hexc("#e3e6ec"), lw=4)
            piece(ctx, P_ell(x + 120, 680, 20), INK, lw=2, shadow=False)
            piece(ctx, P_ell(x - 10, 665, 7), ROJO if pose % 6 < 3 else hexc("#6b1d24"), lw=0, shadow=False, outline=False)
    for i in range(3):
        abuelo(ctx, 300 + i * 220, 1330, 0.75, pose, i)
    td = since(ev, "detiene", lt)
    if td >= 0:
        stamp(ctx, 540, 960, "¡DETENIDOS!", td, 64, col=ROJO, ang=-8)


def sc_carcel(ctx, pose, lt, ev):
    fondo(ctx, "#5b6475", 1330, "#3d3f4a")
    for i in range(3):
        abuelo(ctx, 300 + i * 240, 1320, 0.85, pose, i)
    for i in range(9):
        line(ctx, [(140 + i * 100, 560), (140 + i * 100, 1330)], 14, hexc("#2b2d33"))
    line(ctx, [(120, 620), (960, 620)], 16, hexc("#2b2d33"))
    tp = since(ev, "parte", lt)
    if tp >= 0:
        saco(ctx, 540, 1180, 0.8)
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 1000 - bob, 150, hexc("#ffe14d"), INK, 7)


SCENES = dict(abuelos=sc_abuelos, fachada=sc_fachada, ascensor=sc_ascensor, taladro=sc_taladro, cajas=sc_cajas,
              botin=sc_botin, camaras=sc_camaras, carcel=sc_carcel)
SCENES = con_mapa(SCENES, BLOQUES, pais="GBR", ciudad="LONDRES", lon=-0.12, lat=51.51)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_taladro(ctx, 0, 2.0, {"agujeros_lt": 0.2})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(79))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UNA BANDA DE ABUELOS", 540, 220, 90, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "VACIÓ UNA CÁMARA", 540, 380, 96, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡14 MILLONES £!", 540, 1690, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
    surf.write_to_png(path)


def configurar():
    g.BLOQUES[:] = BLOQUES
    g.SCENES.clear()
    g.SCENES.update(SCENES)
    g.RECORTES_SUGERIDOS[:] = []
    g.SALIDA = SLUG
    d = os.path.join(g.CACHE_DIR, SLUG)
    os.makedirs(d, exist_ok=True)
    g.CACHE_DIR = d
    g.NARR_JSON = os.path.join(d, "narracion_palabras.json")
    g.NARR_MP3 = os.path.join(d, "narracion.mp3")
    g.thumbnail = miniatura


if __name__ == "__main__":
    configurar()
    g.main()
