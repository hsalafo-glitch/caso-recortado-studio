#!/usr/bin/env python3
"""
Short 19 · «El falso policía de los 300 millones de yenes» — Tokio, 1968
Voz gratuita (python voz_gratis.py short_yenes.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import bubble, since, stamp, txt
from generar_marca import magnifier
from piezas_casos import BORDE, ROJO, SOMBRA, VERDE_BILLETE, fondo, silueta
from short_dioni import coche

SLUG = "yenes-tokio"
PRONUNCIA = {"Tokio": "Tokio"}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pasaría si un ladrón robara casi 300 millones de yenes… sin tocar a nadie, y nunca lo atraparan?",
        escenas=[(None, "yenes")],
        pantalla=[("casi 300", "300 MILLONES DE YENES"), ("sin tocar", "SIN TOCAR A NADIE")],
        eventos={"sin": "sin tocar", "nunca": "nunca lo"},
    ),
    dict(
        id="caso",
        voz=("Tokio, diciembre de 1968. Un coche del banco lleva las pagas extra de los trabajadores de una fábrica. "
             "De repente, un policía en moto le hace parar."),
        escenas=[(None, "carretera")],
        pantalla=[(None, "TOKIO, 1968"), ("las pagas", "PAGAS EXTRA"), ("De repente", "¡ALTO!")],
        eventos={"pagas": "las pagas", "moto": "un policía"},
    ),
    dict(
        id="truco",
        voz=("Les dice que puede haber una bomba bajo el coche. Se mete debajo, sale humo y fuego, y los empleados "
             "huyen. Entonces el \"policía\" sube al coche… y se lo lleva."),
        escenas=[(None, "bomba"), ("Entonces el", "robo")],
        pantalla=[(None, "«¡HAY UNA BOMBA!»"), ("sale humo", "¡HUMO Y FUEGO!"), ("Entonces el", "SE LLEVA EL COCHE")],
        eventos={"debajo": "Se mete", "humo": "sale humo", "huyen": "empleados huyen"},
    ),
    dict(
        id="pistas",
        voz=("El humo era una bengala, y la moto, una moto robada y pintada como las de la policía. Dejó más de cien "
             "pistas, pero nunca le encontraron."),
        escenas=[(None, "bengala"), ("Dejó más", "pistas")],
        pantalla=[(None, "SOLO UNA BENGALA"), ("y la moto", "MOTO PINTADA"), ("Dejó más", "+100 PISTAS")],
        eventos={"moto": "y la moto", "nunca": "pero nunca"},
    ),
    dict(
        id="cierre",
        voz="En 1975, el delito prescribió. Aunque hoy confesara, no podrían juzgarle. ¿Quién crees que era?",
        escenas=[(None, "prescrito")],
        pantalla=[(None, "1975: PRESCRITO"), ("Quién", "¿QUIÉN ERA?")],
        eventos={"prescribio": "el delito", "pregunta": "Quién crees"},
    ),
]


def moto_policia(ctx, x, y, s, pose, piloto=True, pintada=True):
    for wx in (x - 120 * s, x + 120 * s):
        piece(ctx, P_ell(wx, y, 60 * s), INK, lw=3, shadow=False)
        piece(ctx, P_ell(wx, y, 24 * s), hexc("#9aa0ab"), lw=2, shadow=False)
    piece(ctx, P_poly([(x - 130 * s, y - 40 * s), (x + 60 * s, y - 70 * s), (x + 150 * s, y - 40 * s),
                       (x + 110 * s, y - 10 * s), (x - 90 * s, y - 10 * s)]), (1, 1, 1) if pintada else hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rect(x - 60 * s, y - 70 * s, 120 * s, 22 * s), hexc("#1d4ed8") if pintada else hexc("#3d3f4a"), lw=3,
          shadow=False)
    line(ctx, [(x + 110 * s, y - 50 * s), (x + 130 * s, y - 130 * s)], 8 * s, INK)
    piece(ctx, P_ell(x + 160 * s, y - 60 * s, 18 * s), hexc("#ffe58a"), lw=3, shadow=False)
    if pintada:
        on = pose % 6 < 3
        piece(ctx, P_ell(x - 110 * s, y - 70 * s, 14 * s), ROJO if on else hexc("#6b1d24"), lw=2, shadow=False)
    if piloto:
        silueta(ctx, x - 10 * s, y - 50 * s, 0.75 * s, pose)
        hy = y - 50 * s - 230 * 0.75 * s - 72 * 0.75 * s * 0.9
        piece(ctx, P_ell(x - 10 * s, hy - 8 * s, 60 * s, 52 * s), (1, 1, 1), lw=4, shadow=False)
        piece(ctx, P_rect(x - 60 * s, hy + 6 * s, 100 * s, 18 * s), hexc("#2b2d33"), lw=2, shadow=False)


def carretera(ctx, pose, suelo=1250):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    for i, (x, w, h) in enumerate(((-20, 220, 420), (210, 180, 520), (400, 260, 380), (670, 200, 560), (880, 220, 440))):
        piece(ctx, P_rect(x, suelo - h, w, h), hexc(["#9aa0ab", "#b5bccb", "#8a8f9a", "#a8adb6", "#9aa0ab"][i]), lw=4)
        for r in range(int(h / 110)):
            piece(ctx, P_rect(x + 30, suelo - h + 30 + r * 110, w - 60, 50), hexc("#5b6475"), lw=2, shadow=False)
    piece(ctx, P_rect(-10, suelo, 1100, 700), hexc("#4a4f5c"), lw=4, shadow=False)
    for i in range(6):
        piece(ctx, P_rect(i * 200 - (pose * 4) % 200, suelo + 110, 110, 16), hexc("#f2e7b0"), lw=0, shadow=False, outline=False)


def humo(ctx, x, y, k, pose):
    for i in range(7):
        r = (40 + 25 * i) * k
        piece(ctx, P_ell(x + (hnoise("hm", i) - 0.5) * 300 * k, y - i * 50 * k, r), hexc("#d9d9d9") if i % 2 else hexc("#bfbfbf"),
              lw=0, shadow=False, outline=False)
    if (pose // 2) % 2 == 0:
        piece(ctx, P_poly([(x - 40, y + 20), (x, y - 70 * k), (x + 40, y + 20)]), hexc("#ff8a1f"), lw=3, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_yenes(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    n = int(clamp(lt / 1.2) * 12)
    for i in range(n):
        r, c = divmod(i, 4)
        x, y = 240 + c * 200, 640 + r * 170
        for j in range(4):
            piece(ctx, P_rect(x - 80, y - j * 12, 160, 70), hexc("#d9c7a3"), lw=3, shadow=False)
        piece(ctx, P_ell(x, y - 36 + 35, 22), hexc("#c8202f"), lw=2, shadow=False)
        txt(ctx, "¥", x, y + 12, 34, (1, 1, 1), anchor="center")
    ts = since(ev, "sin", lt)
    if ts >= 0:
        stamp(ctx, 540, 1200, "0 HERIDOS", ts, 60, col=hexc("#2fb35a"), ang=-6)


def sc_carretera(ctx, pose, lt, ev):
    carretera(ctx, pose)
    coche(ctx, 640, 1330, 1.3, "#2b2d33")
    tp = since(ev, "pagas", lt)
    if tp >= 0:
        stamp(ctx, 640, 990, "¥ PAGAS EXTRA", tp, 46, col=hexc("#c8202f"), ang=-5)
    tm = since(ev, "moto", lt)
    if tm >= 0:
        x = lerp(-250, 180, ease_io(clamp(tm / 1.0)))
        moto_policia(ctx, x, 1300, 0.9, pose)
        if tm > 1.0:
            bubble(ctx, 220, 800, 260, 110, (190, 1000), ["¡ALTO!"], 56)


def sc_bomba(ctx, pose, lt, ev):
    carretera(ctx, pose)
    coche(ctx, 600, 1330, 1.3, "#2b2d33")
    moto_policia(ctx, 120, 1300, 0.7, pose, piloto=False)
    td = since(ev, "debajo", lt)
    th = since(ev, "humo", lt)
    tu = since(ev, "huyen", lt)
    if td < 0:
        silueta(ctx, 900, 1330, 0.9, pose)
        hy = 1330 - (230 + 72 * 0.9) * 0.9
        piece(ctx, P_ell(900, hy - 8, 72, 62), (1, 1, 1), lw=4, shadow=False)
        piece(ctx, P_rect(842, hy + 6, 116, 20), hexc("#2b2d33"), lw=2, shadow=False)
        bubble(ctx, 760, 820, 380, 120, (880, 1020), ["¡UNA BOMBA!"], 50)
    else:
        # sólo asoman las piernas bajo el coche
        line(ctx, [(820, 1320), (930, 1325)], 26, SOMBRA)
        line(ctx, [(820, 1300), (930, 1300)], 26, SOMBRA)
    if th >= 0:
        humo(ctx, 600, 1260, clamp(th / 0.8) * 1.1, pose)
    if tu >= 0:
        for i in range(2):
            k = clamp((tu - i * 0.2) / 1.0)
            silueta(ctx, lerp(500 + i * 100, -200 - i * 100, k), 1330, 0.85, pose, i)


def sc_robo(ctx, pose, lt, ev):
    carretera(ctx, pose)
    moto_policia(ctx, 120, 1300, 0.7, pose, piloto=False)
    k = ease_io(clamp(lt / 1.6))
    x = lerp(600, 1500, k)
    coche(ctx, x, 1330, 1.3, "#2b2d33")
    humo(ctx, 600, 1260, 0.8 * (1 - k * 0.6), pose)
    for i in range(3):
        line(ctx, [(x - 330 - i * 60, 1220 + i * 30), (x - 260 - i * 60, 1220 + i * 30)], 8, (1, 1, 1))


def sc_bengala(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1330, "#262a3a")
    tm = since(ev, "moto", lt)
    if tm < 0:
        with rot(ctx, 540, 950, math.radians(-30)):
            piece(ctx, P_rrect(380, 920, 320, 60, 20), ROJO, lw=5)
            piece(ctx, P_rect(400, 920, 60, 60), (1, 1, 1), lw=3, shadow=False)
            if (pose // 2) % 2 == 0:
                piece(ctx, P_poly([(700, 920), (800, 950), (700, 980)]), hexc("#ffe14d"), lw=3, shadow=False)
        stamp(ctx, 540, 1200, "NO ERA UNA BOMBA", lt - 0.4, 52, col=ROJO, ang=-6)
    else:
        moto_policia(ctx, 540, 1200, 1.4, pose, piloto=False, pintada=clamp(tm / 0.8) > 0.5)
        stamp(ctx, 540, 800, "ROBADA", tm - 0.3, 60, col=ROJO, ang=-8)


def sc_pistas(ctx, pose, lt, ev):
    fondo(ctx, "#3a3150", 1330, "#241e33")
    n = 3 + int(clamp(lt / 1.6) * 117)
    for i in range(min(n, 60)):
        x = 120 + (i % 10) * 92
        y = 600 + (i // 10) * 95
        piece(ctx, P_rect(x - 30, y - 30, 60, 60), (1, 1, 1), lw=3, shadow=False)
        txt(ctx, str(i + 1), x, y + 10, 24, INK, anchor="center")
    piece(ctx, P_rrect(320, 1190, 440, 100, 14), hexc("#1d2433"), lw=4)
    txt(ctx, f"PISTAS: {min(n, 120)}", 540, 1262, 54, hexc("#ffe14d"), anchor="center")
    tn = since(ev, "nunca", lt)
    if tn >= 0:
        stamp(ctx, 540, 900, "NI UN NOMBRE", tn, 64, col=ROJO, ang=-8)


def sc_prescrito(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    year = 1968 + int(7 * ease_io(clamp(lt / 1.4)))
    piece(ctx, P_rect(330, 560, 420, 300), (1, 1, 1), lw=5)
    piece(ctx, P_rect(330, 560, 420, 80), ROJO, lw=4, shadow=False)
    draw_text(ctx, str(year), 540, 760, 120, INK, INK, 0)
    silueta(ctx, 540, 1320, 1.0, pose)
    hy = 1320 - 230 - 65
    piece(ctx, P_ell(540, hy - 8, 80, 70), (1, 1, 1), lw=4, shadow=False)
    piece(ctx, P_rect(475, hy + 10, 130, 22), hexc("#2b2d33"), lw=2, shadow=False)
    tp = since(ev, "prescribio", lt)
    if tp >= 0:
        stamp(ctx, 540, 900, "PRESCRITO", tp, 66, col=ROJO, ang=-10)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 760, 1080 - bob, 160, hexc("#ffe14d"), INK, 7)


SCENES = dict(yenes=sc_yenes, carretera=sc_carretera, bomba=sc_bomba, robo=sc_robo, bengala=sc_bengala,
              pistas=sc_pistas, prescrito=sc_prescrito)
SCENES = con_mapa(SCENES, BLOQUES, pais="JPN", ciudad="TOKIO", lon=139.69, lat=35.69)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_bomba(ctx, 0, 2.0, {"debajo_lt": 0.2, "humo_lt": 0.6})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(71))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UN FALSO POLICÍA", 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "300 MILLONES DE ¥", 540, 380, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡NUNCA LO PILLARON!", 540, 1690, 96, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
