#!/usr/bin/env python3
"""
Short 16 · «Escaparon de Alcatraz gracias a unas cabezas de papel» — EE. UU., 1962
Voz gratuita (python voz_gratis.py short_alcatraz.py).
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
from short_museo import guardia
from short_robo_siglo import olas

SLUG = "alcatraz"
PRONUNCIA = {}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pensarías si te dijera que tres presos escaparon de Alcatraz… gracias a unas cabezas de papel?",
        escenas=[(None, "isla"), ("gracias a", "cabeza")],
        pantalla=[("tres presos", "ESCAPE DE ALCATRAZ"), ("gracias a", "¿CABEZAS DE PAPEL?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("San Francisco, 1962. Alcatraz es una isla rodeada de agua helada. Durante meses, tres presos agrandan "
             "los respiraderos de sus celdas y fabrican cabezas falsas con jabón, papel y pelo de verdad."),
        escenas=[(None, "isla"), ("Durante meses", "celda")],
        pantalla=[(None, "SAN FRANCISCO, 1962"), ("agua helada", "AGUA HELADA"), ("Durante meses", "MESES CAVANDO"),
                  ("fabrican", "JABÓN + PAPEL + PELO")],
        eventos={"helada": "agua helada", "cabezas": "fabrican cabezas", "pelo": "pelo de"},
    ),
    dict(
        id="ronda",
        voz=("La noche del escape, dejan las cabezas en sus camas. Los guardias pasan, ven a tres hombres "
             "dormidos… y siguen la ronda."),
        escenas=[(None, "ronda")],
        pantalla=[(None, "LA NOCHE DEL ESCAPE"), ("siguen la", "«TODO EN ORDEN»")],
        eventos={"guardias": "Los guardias", "siguen": "siguen la"},
    ),
    dict(
        id="balsa",
        voz=("Ellos ya están en el agua, en una balsa hecha con más de cincuenta impermeables. A la mañana "
             "siguiente salta la alarma, y solo encuentran restos de la balsa."),
        escenas=[(None, "balsa"), ("A la mañana", "alarma"), ("y solo", "restos")],
        pantalla=[(None, "+50 IMPERMEABLES"), ("A la mañana", "¡ALARMA!"), ("y solo", "SOLO RESTOS")],
        eventos={"impermeables": "cincuenta impermeables"},
    ),
    dict(
        id="cierre",
        voz="Nunca se encontraron sus cuerpos. ¿Crees que llegaron a la orilla?",
        escenas=[(None, "sebuscan")],
        pantalla=[(None, "NUNCA APARECIERON"), ("Crees", "¿LLEGARON A LA ORILLA?")],
        eventos={"pregunta": "Crees que"},
    ),
]

AGUA = hexc("#2f5f88")


def isla_prision(ctx, pose, cx=540, cy=1080, s=1.0):
    piece(ctx, P_poly([(cx - 380 * s, cy + 60 * s), (cx - 300 * s, cy - 40 * s), (cx + 280 * s, cy - 60 * s),
                       (cx + 400 * s, cy + 60 * s)]), hexc("#6b5a4a"), lw=5)
    piece(ctx, P_rect(cx - 250 * s, cy - 230 * s, 420 * s, 190 * s), hexc("#d9d2c0"), lw=5)
    for i in range(7):
        for j in range(2):
            piece(ctx, P_rect(cx - 225 * s + i * 56 * s, cy - 205 * s + j * 75 * s, 30 * s, 45 * s),
                  hexc("#ffe58a") if (i + j + pose // 6) % 3 == 0 else hexc("#3d3f4a"), lw=2, shadow=False)
    piece(ctx, P_rect(cx + 200 * s, cy - 330 * s, 60 * s, 290 * s), hexc("#e3e6ec"), lw=4)
    piece(ctx, P_rect(cx + 185 * s, cy - 360 * s, 90 * s, 40 * s), hexc("#9aa0ab"), lw=4)
    a = lt_faro = (pose % 24) / 24 * 2 * math.pi
    ctx.move_to(cx + 230 * s, cy - 340 * s)
    ctx.line_to(cx + 230 * s + 600 * math.cos(a - 0.1), cy - 340 * s + 140 * math.sin(a - 0.1))
    ctx.line_to(cx + 230 * s + 600 * math.cos(a + 0.1), cy - 340 * s + 140 * math.sin(a + 0.1))
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.6, 0.22)
    ctx.fill()


def cabeza_falsa(ctx, x, y, r):
    piece(ctx, P_ell(x, y, r, r * 1.1), hexc("#e8c4a0"), lw=5)
    piece(ctx, P_poly([(x - r, y - r * 0.2), (x - r * 0.8, y - r * 1.05), (x, y - r * 1.25), (x + r * 0.8, y - r * 1.05),
                       (x + r, y - r * 0.2), (x + r * 0.6, y - r * 0.7), (x - r * 0.6, y - r * 0.7)]), hexc("#4a3020"), lw=4,
          shadow=False)
    # ojos cerrados y boca pintados (cara de muñeco)
    for dx in (-0.35, 0.35):
        ctx.new_sub_path()
        ctx.arc(x + dx * r, y + 0.05 * r, r * 0.16, 0, math.pi)
        set_col(ctx, INK)
        ctx.set_line_width(4)
        ctx.stroke()
    line(ctx, [(x - r * 0.2, y + r * 0.5), (x + r * 0.2, y + r * 0.5)], 4, hexc("#9a4a3a"))


def cama(ctx, x, y, w, cabeza=True, r=55):
    piece(ctx, P_rect(x, y, w, 50), hexc("#7a7f8a"), lw=4)
    piece(ctx, P_rect(x + 10, y + 50, 14, 90), hexc("#5b6475"), lw=3, shadow=False)
    piece(ctx, P_rect(x + w - 24, y + 50, 14, 90), hexc("#5b6475"), lw=3, shadow=False)
    piece(ctx, P_rrect(x + 10, y - 40, 120, 50, 18), (1, 1, 1), lw=3, shadow=False)
    if cabeza:
        cabeza_falsa(ctx, x + 75, y - 55, r)
    piece(ctx, P_poly([(x + 120, y + 5), (x + w, y + 5), (x + w, y - 50), (x + w * 0.7, y - 75), (x + 140, y - 60)]),
          hexc("#5a7a9a"), lw=4)


def barrotes(ctx, x0, x1, y0, y1, n=9):
    for i in range(n):
        x = lerp(x0, x1, i / (n - 1))
        line(ctx, [(x, y0), (x, y1)], 10, hexc("#3d3f4a"))
    line(ctx, [(x0, y0 + 40), (x1, y0 + 40)], 12, hexc("#3d3f4a"))
    line(ctx, [(x0, y1 - 40), (x1, y1 - 40)], 12, hexc("#3d3f4a"))


# ─────────────────────────────── escenas ───────────────────────────────
def sc_isla(ctx, pose, lt, ev):
    noche(ctx, pose)
    piece(ctx, P_rect(-10, 1080, 1100, 900), AGUA, lw=0, shadow=False, outline=False)
    isla_prision(ctx, pose, 540, 1120, 1.1)
    olas(ctx, 1200, pose, AGUA)
    th = since(ev, "helada", lt)
    if th >= 0:
        stamp(ctx, 540, 1330, "CORRIENTES FUERTES", th, 48, col=hexc("#4fb3ff"), ang=-5)


def sc_cabeza(ctx, pose, lt, ev):
    fondo(ctx, "#5b6475", 1330, "#3d3f4a")
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    cabeza_falsa(ctx, 540, 940, 220 * max(0.05, k))
    if lt > 0.6:
        stamp(ctx, 540, 1260, "¡FALSA!", lt - 0.6, 64, col=ROJO, ang=-8)


def sc_celda(ctx, pose, lt, ev):
    fondo(ctx, "#8a8f9a", 1330, "#5b6475")
    piece(ctx, P_rect(80, 560, 920, 770), hexc("#a8adb6"), lw=5)
    # respiradero en la pared del fondo, que se va agrandando
    tc = since(ev, "cabezas", lt)
    k = clamp(lt / 2.0)
    w = 110 + 70 * k
    piece(ctx, P_rect(880 - w / 2, 1060, w, 120 + 40 * k), hexc("#1a1d24"), lw=4)
    for i in range(4):
        line(ctx, [(880 - w / 2 + 15, 1080 + i * 28), (880 + w / 2 - 15, 1080 + i * 28)], 4, hexc("#5b6475"))
    for i in range(int(8 * k)):
        piece(ctx, P_ell(780 + hnoise("pol", i) * 200, 1300 + hnoise("pol", i, "y") * 20, 10), hexc("#c9ccd6"), lw=2,
              shadow=False)
    if tc < 0:
        silueta(ctx, 500, 1320, 0.95, pose)
    else:
        # mesa con los materiales de la cabeza falsa
        piece(ctx, P_rect(200, 1150, 640, 40), hexc("#6b4428"), lw=4)
        piece(ctx, P_rect(220, 1190, 30, 140), hexc("#5a3820"), lw=3, shadow=False)
        piece(ctx, P_rect(790, 1190, 30, 140), hexc("#5a3820"), lw=3, shadow=False)
        piece(ctx, P_rrect(240, 1090, 120, 60, 14), hexc("#f3f1ea"), lw=4)
        txt(ctx, "JABÓN", 300, 1130, 26, INK, anchor="center")
        piece(ctx, P_ell(460, 1110, 50, 40), (1, 1, 1), lw=4)
        piece(ctx, P_ell(460, 1110, 16), hexc("#c9ccd6"), lw=2, shadow=False)
        tp = since(ev, "pelo", lt)
        if tp >= 0:
            for i in range(8):
                line(ctx, [(560 + i * 8, 1145), (575 + i * 9, 1095 + (i % 3) * 6)], 4, hexc("#4a3020"))
        r = 70 * clamp(tc / 1.5)
        if r > 5:
            cabeza_falsa(ctx, 640, 1070, r)


def sc_ronda(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1330, "#2f333d")
    for i in range(3):
        x = 40 + i * 340
        piece(ctx, P_rect(x, 600, 320, 700), hexc("#6b707c"), lw=5)
        cama(ctx, x + 20, 1150, 280, cabeza=True, r=48)
        barrotes(ctx, x + 10, x + 310, 600, 1300, 7)
    tg = since(ev, "guardias", lt)
    if tg >= 0:
        gx = lerp(-150, 760, clamp(tg / 3.0))
        guardia(ctx, gx, 1010, r=60, pose=pose, linterna=True)
    if (pose // 4) % 2 == 0:
        for i in range(3):
            txt(ctx, "z", 140 + i * 340, 1040, 50, hexc("#ffe14d"), anchor="center")


def balsa(ctx, x, y, s, pose):
    for i in range(3):
        silueta(ctx, x - 110 * s + i * 110 * s, y - 10 * s, 0.42 * s, pose, i)
    piece(ctx, P_rrect(x - 230 * s, y - 40 * s, 460 * s, 90 * s, 40 * s), hexc("#e8c21f"), lw=5)
    for i in range(5):
        line(ctx, [(x - 190 * s + i * 95 * s, y - 35 * s), (x - 170 * s + i * 95 * s, y + 45 * s)], 3, hexc("#b5940f"))
    with rot(ctx, x + 60 * s, y - 40 * s, math.radians(-25 if pose % 4 < 2 else 15)):
        line(ctx, [(x + 60 * s, y - 70 * s), (x, y + 70 * s)], 9 * s, hexc("#7a4e2c"))


def sc_balsa(ctx, pose, lt, ev):
    noche(ctx, pose)
    piece(ctx, P_rect(-10, 1080, 1100, 900), AGUA, lw=0, shadow=False, outline=False)
    isla_prision(ctx, pose, 900, 1010, 0.45)
    x = lerp(800, 420, ease_io(clamp(lt / 3.0)))
    balsa(ctx, x, 1210, 1.2, pose)
    olas(ctx, 1240, pose, AGUA)
    ti = since(ev, "impermeables", lt)
    if ti >= 0:
        for i in range(6):
            with rot(ctx, 160 + i * 150, 680, math.radians(-15 + i * 6)):
                piece(ctx, P_poly([(130 + i * 150, 620), (190 + i * 150, 620), (210 + i * 150, 740), (110 + i * 150, 740)]),
                      hexc("#e8c21f"), lw=4)
        stamp(ctx, 540, 860, "+50", ti, 70, col=ROJO, ang=-6)


def sc_alarma(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1330, "#2f333d")
    piece(ctx, P_rect(280, 600, 520, 700), hexc("#6b707c"), lw=5)
    cama(ctx, 330, 1150, 420, cabeza=True, r=60)
    guardia(ctx, 880, 950, r=70, pose=pose, expr="grito")
    on = pose % 6 < 3
    piece(ctx, P_ell(540, 560, 50), ROJO if on else hexc("#6b1d24"), lw=4)
    if on:
        ctx.save()
        ctx.set_source_rgba(1, 0.2, 0.2, 0.18)
        ctx.paint()
        ctx.restore()
    stamp(ctx, 400, 920, "¡ES DE PAPEL!", lt - 0.4, 54, col=ROJO, ang=-8)


def sc_restos(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fc8e0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 900, 1100, 300), AGUA, lw=0, shadow=False, outline=False)
    olas(ctx, 940, pose, AGUA)
    piece(ctx, P_rect(-10, 1150, 1100, 900), hexc("#d9c08a"), lw=4, shadow=False)
    for i, (x, y, a) in enumerate(((250, 1250, -20), (520, 1300, 15), (780, 1240, -5))):
        with rot(ctx, x, y, math.radians(a)):
            piece(ctx, P_poly([(x - 90, y - 30), (x + 80, y - 40), (x + 100, y + 20), (x - 70, y + 40)]), hexc("#e8c21f"), lw=4)
    with rot(ctx, 880, 1330, math.radians(10)):
        line(ctx, [(820, 1330), (960, 1300)], 9, hexc("#7a4e2c"))


def sc_sebuscan(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1360, "#262a3a")
    with rot(ctx, 540, 940, math.radians(-2)):
        piece(ctx, P_rect(120, 560, 840, 760), hexc("#f3e6c9"), lw=6, sh=(12, 16))
        draw_text(ctx, "SE BUSCAN", 540, 650, 90, ROJO, INK, 0)
        for i in range(3):
            x = 260 + i * 280
            piece(ctx, P_rect(x - 110, 720, 220, 300), hexc("#d9c7a3"), lw=4, shadow=False)
            silueta(ctx, x, 1020, 0.85, 0, tilt=0.0)
            bob = ((pose + i * 2) // 4) % 2 * 8
            draw_text(ctx, "?", x, 820 - bob, 90, hexc("#ffe14d"), INK, 6)
        txt(ctx, "DESDE 1962", 540, 1160, 54, INK, anchor="center")
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        stamp(ctx, 540, 1280, "¿VIVOS?", tq, 64, col=hexc("#1d4ed8"), ang=-6)


SCENES = dict(isla=sc_isla, cabeza=sc_cabeza, celda=sc_celda, ronda=sc_ronda, balsa=sc_balsa, alarma=sc_alarma,
              restos=sc_restos, sebuscan=sc_sebuscan)
SCENES = con_mapa(SCENES, BLOQUES, pais="USA", ciudad="SAN FRANCISCO", lon=-122.42, lat=37.77)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_balsa(ctx, 0, 1.5, {"impermeables_lt": None})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(59))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    cabeza_falsa(ctx, 820, 760, 120)
    card_text(ctx, "ESCAPARON DE ALCATRAZ", 540, 220, 88, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "CON CABEZAS DE PAPEL", 540, 380, 88, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y NUNCA APARECIERON!", 540, 1690, 90, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
