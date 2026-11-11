#!/usr/bin/env python3
"""
Short 23 · «Escapó por la regadera de su celda» — fuga del Altiplano (México, 2015)
Voz gratuita (python voz_gratis.py short_altiplano.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, fondo, noche, silueta
from short_tunel import TIERRA, TIERRA2

SLUG = "tunel-altiplano"
PRONUNCIA = {}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que un preso escapó de una cárcel de máxima seguridad… por un agujero en "
             "la regadera de su celda?"),
        escenas=[(None, "carcel"), ("por un", "regadera")],
        pantalla=[("máxima", "MÁXIMA SEGURIDAD"), ("por un", "¿POR LA REGADERA?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("México, julio de 2015. El Altiplano es una de las prisiones más vigiladas del país. Pero bajo la "
             "regadera de una celda, alguien había cavado un agujero."),
        escenas=[(None, "carcel"), ("Pero bajo", "agujero")],
        pantalla=[(None, "MÉXICO, 2015"), ("El Altiplano", "EL ALTIPLANO"), ("Pero bajo", "UN AGUJERO")],
        eventos={"agujero": "un agujero"},
    ),
    dict(
        id="tunel",
        voz="Al otro lado esperaba un túnel de un kilómetro y medio, con luz, ventilación… y una moto montada sobre rieles.",
        escenas=[(None, "tunel")],
        pantalla=[(None, "1,5 KM DE TÚNEL"), ("con luz", "LUZ + AIRE"), ("y una", "¡UNA MOTO SOBRE RIELES!")],
        eventos={"luz": "con luz", "moto": "y una"},
    ),
    dict(
        id="casa",
        voz=("En pocos minutos llegó a una casa en obras fuera del penal. Las cámaras lo habían visto entrar en la "
             "regadera… y nunca salir."),
        escenas=[(None, "obra"), ("Las cámaras", "monitor")],
        pantalla=[(None, "UNA CASA EN OBRAS"), ("Las cámaras", "LAS CÁMARAS…"), ("y nunca", "…NUNCA LO VIERON SALIR")],
        eventos={"nunca": "y nunca"},
    ),
    dict(
        id="cierre",
        voz=("Era El Chapo Guzmán. Lo recapturaron seis meses después, en Sinaloa. ¿Cómo crees que nadie oyó cavar "
             "un túnel así?"),
        escenas=[(None, "recaptura")],
        pantalla=[(None, "RECAPTURADO EN 2016"), ("Cómo", "¿NADIE OYÓ NADA?")],
        eventos={"recaptura": "Lo recapturaron", "pregunta": "Cómo crees"},
    ),
]


def carcel_exterior(ctx, pose):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#a8946a"), lw=4, shadow=False)
    piece(ctx, P_rect(80, 760, 920, 500), hexc("#d9d2c0"), lw=5)
    for i in range(8):
        for j in range(2):
            piece(ctx, P_rect(130 + i * 110, 820 + j * 170, 50, 90), hexc("#3d3f4a"), lw=3, shadow=False)
    for x in (60, 1020):
        piece(ctx, P_rect(x - 50, 560, 100, 700), hexc("#b5bccb"), lw=5)
        piece(ctx, P_rect(x - 70, 520, 140, 60), hexc("#8a8f9a"), lw=4)
    for i in range(22):
        x = 40 + i * 48
        line(ctx, [(x, 740), (x + 20, 715)], 3, INK)
    line(ctx, [(0, 740), (1080, 740)], 4, INK)
    a = (pose % 24) / 24 * math.pi - math.pi / 2
    ctx.move_to(1020, 560)
    ctx.line_to(1020 + 900 * math.cos(a + math.pi - 0.1), 560 + 500 * math.sin(a + math.pi - 0.1) * 0.3 + 300)
    ctx.line_to(1020 + 900 * math.cos(a + math.pi + 0.1), 560 + 500 * math.sin(a + math.pi + 0.1) * 0.3 + 300)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.6, 0.18)
    ctx.fill()


def regadera(ctx, x, y, s=1.0, agujero=0.0, pose=0, agua=True):
    piece(ctx, P_rect(x - 220 * s, y - 520 * s, 440 * s, 560 * s), hexc("#e3e6ec"), lw=5)
    for i in range(5):
        for j in range(6):
            piece(ctx, P_rect(x - 210 * s + i * 86 * s, y - 510 * s + j * 90 * s, 80 * s, 84 * s), hexc("#cfd8e3"), lw=1,
                  shadow=False)
    line(ctx, [(x + 120 * s, y - 520 * s), (x + 120 * s, y - 440 * s), (x + 40 * s, y - 440 * s)], 10 * s, hexc("#9aa0ab"))
    piece(ctx, P_ell(x + 30 * s, y - 440 * s, 30 * s, 16 * s), hexc("#9aa0ab"), lw=3, shadow=False)
    if agua and pose % 2 == 0:
        for i in range(6):
            line(ctx, [(x + 10 * s + i * 8 * s, y - 420 * s), (x + i * 14 * s - 10 * s, y - 300 * s)], 3, hexc("#8ec5e8"))
    piece(ctx, P_rect(x - 220 * s, y + 40 * s, 440 * s, 60 * s), hexc("#cfd8e3"), lw=4)
    if agujero > 0:
        piece(ctx, P_rect(x - 60 * s * agujero, y + 40 * s, 120 * s * agujero, 60 * s), hexc("#1a120c"), lw=3, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_carcel(ctx, pose, lt, ev):
    carcel_exterior(ctx, pose)


def sc_regadera(ctx, pose, lt, ev):
    fondo(ctx, "#8a8f9a", 1330, "#5b6475")
    regadera(ctx, 540, 1230, 1.3, agujero=clamp(lt / 0.8), pose=pose)
    bob = (pose // 4) % 2 * 8
    if lt > 0.8:
        draw_text(ctx, "?", 540, 860 - bob, 160, hexc("#ffe14d"), INK, 7)


def sc_agujero(ctx, pose, lt, ev):
    fondo(ctx, "#8a8f9a", 1330, "#5b6475")
    regadera(ctx, 540, 1100, 1.0, agujero=1.0, pose=pose, agua=False)
    # corte del suelo: el pozo bajo la regadera
    piece(ctx, P_rect(-10, 1200, 1100, 760), TIERRA, lw=4, shadow=False)
    for i in range(20):
        piece(ctx, P_ell(hnoise("ta", i) * 1080, 1220 + hnoise("ta", i, "y") * 260, 12), TIERRA2, lw=0, shadow=False, outline=False)
    k = clamp(lt / 1.0)
    piece(ctx, P_rect(480, 1140, 120, 360 * k), hexc("#1a120c"), lw=3, shadow=False)
    if k > 0.5:
        line(ctx, [(500, 1150), (500, 1150 + 340 * k)], 5, hexc("#c9a46a"))
        for yy in range(1170, int(1150 + 340 * k), 50):
            line(ctx, [(500, yy), (580, yy)], 4, hexc("#c9a46a"))


def moto_rieles(ctx, x, y, s, pose):
    line(ctx, [(x - 200 * s, y + 40 * s), (x + 200 * s, y + 40 * s)], 6, hexc("#9aa0ab"))
    for wx in (x - 70 * s, x + 70 * s):
        piece(ctx, P_ell(wx, y + 20 * s, 26 * s), INK, lw=3, shadow=False)
    piece(ctx, P_poly([(x - 100 * s, y), (x + 90 * s, y - 20 * s), (x + 110 * s, y + 10 * s), (x - 90 * s, y + 20 * s)]),
          hexc("#e63946"), lw=4)
    piece(ctx, P_rect(x - 110 * s, y - 10 * s, 120 * s, 20 * s), hexc("#5b6475"), lw=3, shadow=False)


def sc_tunel(ctx, pose, lt, ev):
    set_col(ctx, TIERRA)
    ctx.paint()
    for i in range(40):
        piece(ctx, P_ell(hnoise("tt", i) * 1080, 540 + hnoise("tt", i, "y") * 900, 14), TIERRA2, lw=0, shadow=False, outline=False)
    # boca del túnel en perspectiva
    piece(ctx, P_ell(540, 1000, 420, 380), hexc("#2a1a10"), lw=6)
    piece(ctx, P_ell(540, 1000, 200, 180), hexc("#1a120c"), lw=3, shadow=False)
    piece(ctx, P_ell(540, 1000, 70, 60), hexc("#0c0805"), lw=2, shadow=False)
    # rieles
    for dx in (-60, 60):
        line(ctx, [(540 + dx * 0.4, 1040), (540 + dx * 5, 1400)], 8, hexc("#9aa0ab"))
    for i in range(6):
        t = i / 6
        y = lerp(1060, 1380, t * t)
        line(ctx, [(540 - 30 - 260 * t * t, y), (540 + 30 + 260 * t * t, y)], 6, hexc("#7a4e2c"))
    tl = since(ev, "luz", lt)
    if tl >= 0:
        for i, (x, y) in enumerate(((380, 760), (700, 760), (460, 880), (620, 880))):
            piece(ctx, P_ell(x, y, 18 - i * 3), hexc("#fff3b0"), lw=2, shadow=False)
    tm = since(ev, "moto", lt)
    if tm >= 0:
        k = ease_out_back(clamp(tm / 0.5)) if tm < 0.5 else 1.0
        moto_rieles(ctx, 540, 1250, 1.5 * max(0.05, k), pose)
    piece(ctx, P_rrect(360, 560, 360, 90, 14), hexc("#1d2433"), lw=4)
    m = int(1500 * ease_io(clamp(lt / 2.0)))
    txt(ctx, f"{m} m", 540, 625, 56, hexc("#ffe14d"), anchor="center")


def sc_obra(ctx, pose, lt, ev):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1180, 1100, 780), hexc("#a8946a"), lw=4, shadow=False)
    # casa sin terminar, con ladrillos a la vista
    piece(ctx, P_rect(300, 700, 520, 480), hexc("#c96a4a"), lw=5)
    for r in range(10):
        for c in range(8):
            piece(ctx, P_rect(305 + c * 65 + (r % 2) * 30, 705 + r * 47, 60, 42), hexc("#b5583a"), lw=1, shadow=False)
    for x in (300, 560, 820):
        line(ctx, [(x, 700), (x, 600)], 10, hexc("#9aa0ab"))
    piece(ctx, P_rect(500, 1000, 120, 180), hexc("#1a120c"), lw=4)
    x = lerp(560, 900, ease_io(clamp((lt - 0.4) / 1.4)))
    if lt > 0.4:
        silueta(ctx, x, 1250, 0.9, pose)
    carcel_mini = 0.3
    piece(ctx, P_rect(0, 980, 180, 200), hexc("#d9d2c0"), lw=4)
    txt(ctx, "PENAL", 90, 1090, 34, INK, anchor="center")


def sc_monitor(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    piece(ctx, P_rrect(140, 600, 800, 600, 20), hexc("#23242c"), lw=6)
    piece(ctx, P_rect(170, 630, 740, 540), hexc("#3a4a3a"), lw=3, shadow=False)
    ctx.save()
    P_rect(170, 630, 740, 540)(ctx)
    ctx.clip()
    piece(ctx, P_rect(420, 700, 260, 400), hexc("#7a8a7a"), lw=3, shadow=False)
    piece(ctx, P_rect(400, 680, 40, 440), hexc("#5a6a5a"), lw=3, shadow=False)
    for i in range(0, 540, 6):
        line(ctx, [(170, 630 + i), (910, 630 + i)], 1, (0, 0, 0, 0.15))
    ctx.restore()
    txt(ctx, "CAM 07", 230, 680, 32, hexc("#9fd6a0"))
    on = pose % 6 < 3
    piece(ctx, P_ell(860, 670, 12), ROJO if on else hexc("#6b1d24"), lw=0, shadow=False, outline=False)
    t = 21 + lt * 0.05
    txt(ctx, f"20:{52 + int(lt * 6) % 8:02d}", 840, 1150, 32, hexc("#9fd6a0"), anchor="center")
    tn = since(ev, "nunca", lt)
    if tn >= 0:
        stamp(ctx, 540, 900, "NO SALE", tn, 64, col=ROJO, ang=-8)


def sc_recaptura(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1330, "#262a3a")
    silueta(ctx, 540, 1320, 1.25, pose)
    tr = since(ev, "recaptura", lt)
    if tr >= 0:
        stamp(ctx, 540, 860, "RECAPTURADO", tr, 62, col=ROJO, ang=-8)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        for i in range(3):
            k = clamp((tq - i * 0.2) / 0.4)
            if k > 0:
                txt(ctx, "¿?", 200 + i * 340, 700 + (i % 2) * 60, 70 * k, hexc("#ffe14d"), anchor="center")


SCENES = dict(carcel=sc_carcel, regadera=sc_regadera, agujero=sc_agujero, tunel=sc_tunel, obra=sc_obra,
              monitor=sc_monitor, recaptura=sc_recaptura)
SCENES = con_mapa(SCENES, BLOQUES, pais="MEX", ciudad="ALTIPLANO", lon=-99.75, lat=19.29)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_tunel(ctx, 0, 2.0, {"luz_lt": 0.1, "moto_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(89))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ESCAPÓ POR", 540, 220, 110, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "LA REGADERA", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡1,5 KM DE TÚNEL!", 540, 1690, 104, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
