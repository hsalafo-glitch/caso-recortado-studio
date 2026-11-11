#!/usr/bin/env python3
"""
Short 29 · «El robo que obligó a cambiar los billetes» — Banco de la República, Valledupar (Colombia), 1994
Voz gratuita (python voz_gratis.py short_valledupar.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, VERDE_BILLETE, fondo, noche, silueta
from short_robo_siglo import saco
from short_hatton import taladro

SLUG = "robo-valledupar"
PRONUNCIA = {"Valledupar": "Valledupar"}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pensarías si te dijera que un robo obligó a todo un país… a cambiar sus billetes?",
        escenas=[(None, "billetes")],
        pantalla=[("un robo", "UN ROBO…"), ("a cambiar", "¿NUEVOS BILLETES?")],
        eventos={"cambiar": "a cambiar"},
    ),
    dict(
        id="caso",
        voz=("Valledupar, Colombia, octubre de 1994. Durante un puente festivo, una banda entra en la sede del Banco "
             "de la República, el banco central del país, sin disparar un solo tiro."),
        escenas=[(None, "banco")],
        pantalla=[(None, "COLOMBIA, 1994"), ("Durante un", "PUENTE FESTIVO"), ("sin disparar", "SIN UN SOLO DISPARO")],
        eventos={"entra": "una banda", "tiro": "sin disparar"},
    ),
    dict(
        id="boveda",
        voz=("Perforan la bóveda y sacan más de 24.000 millones de pesos. Desde un hotel justo enfrente, dos de ellos "
             "lo coordinaban todo."),
        escenas=[(None, "boveda"), ("Desde un", "hotel")],
        pantalla=[(None, "LA BÓVEDA"), ("más de", "+24.000 MILLONES DE PESOS"), ("Desde un", "UN HOTEL ENFRENTE")],
        eventos={"sacan": "y sacan"},
    ),
    dict(
        id="billetes",
        voz=("El golpe fue tan grande que el banco tuvo que cambiar el diseño de los billetes de 2.000, 5.000 y "
             "10.000 pesos."),
        escenas=[(None, "rediseno")],
        pantalla=[(None, "TAN GRANDE QUE…"), ("cambiar el", "BILLETES NUEVOS")],
        eventos={"cambiar": "cambiar el", "dosmil": "de 2.000", "cincomil": "5.000 y", "diezmil": "10.000 pesos"},
    ),
    dict(
        id="cierre",
        voz="Años después, su historia llegó a la televisión. ¿Tú habrías aceptado uno de esos billetes?",
        escenas=[(None, "tele")],
        pantalla=[(None, "AHORA ES UNA SERIE"), ("Tú habrías", "¿LO HABRÍAS ACEPTADO?")],
        eventos={"pregunta": "Tú habrías"},
    ),
]


def billete(ctx, x, y, w, h, valor, col, nuevo=False, ang=0.0):
    with rot(ctx, x, y, ang):
        piece(ctx, P_rect(x - w / 2, y - h / 2, w, h), hexc(col), lw=4)
        piece(ctx, P_rect(x - w / 2 + 12, y - h / 2 + 12, w - 24, h - 24), (0, 0, 0, 0), lw=2, shadow=False)
        piece(ctx, P_ell(x - w * 0.22, y, h * 0.28), hexc("#f3f1ea"), lw=3, shadow=False)
        if nuevo:
            piece(ctx, P_poly([(x - w * 0.22, y - h * 0.2), (x - w * 0.12, y + h * 0.15), (x - w * 0.32, y + h * 0.15)]),
                  hexc(col), lw=2, shadow=False)
        else:
            piece(ctx, P_ell(x - w * 0.22, y - h * 0.04, h * 0.12), hexc(col), lw=2, shadow=False)
        txt(ctx, valor, x + w * 0.2, y + h * 0.12, h * 0.32, INK, anchor="center")


def sede(ctx, x, y, w, h):
    piece(ctx, P_rect(x, y, w, h), hexc("#e8dcc0"), lw=5)
    for c in range(5):
        piece(ctx, P_rect(x + 30 + c * (w - 60) / 5, y + 40, (w - 60) / 5 - 30, h - 80), hexc("#c9b48a"), lw=3, shadow=False)
    piece(ctx, P_rect(x - 20, y - 70, w + 40, 70), hexc("#a8946a"), lw=5)
    txt(ctx, "BANCO DE LA REPÚBLICA", x + w / 2, y - 25, 34, INK, anchor="center")


# ─────────────────────────────── escenas ───────────────────────────────
def sc_billetes(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i, (v, c) in enumerate((("2.000", "#c9a46a"), ("5.000", "#8fbf8a"), ("10.000", "#c98a8a"))):
        billete(ctx, 540, 700 + i * 200, 560, 170, v, c, ang=math.radians(-4 + i * 4))
    tc = since(ev, "cambiar", lt)
    if tc >= 0:
        stamp(ctx, 540, 1200, "¿CAMBIARLOS?", tc, 60, col=ROJO, ang=-8)


def sc_banco(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    sede(ctx, 160, 820, 760, 510)
    te = since(ev, "entra", lt)
    if te >= 0:
        for i in range(4):
            k = clamp((te - i * 0.2) / 1.2)
            if k < 1:
                silueta(ctx, lerp(-80 - i * 90, 540, k), 1330, 0.6, pose, i)
    tt = since(ev, "tiro", lt)
    if tt >= 0:
        stamp(ctx, 540, 1150, "0 DISPAROS", tt, 60, col=hexc("#2fb35a"), ang=-6)


def sc_boveda(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1330, "#2f333d")
    piece(ctx, P_ell(700, 920, 260), hexc("#9aa0ab"), lw=6)
    piece(ctx, P_ell(700, 920, 210), hexc("#7a7f8a"), lw=4, shadow=False)
    for a in range(8):
        ang = a * math.pi / 4
        line(ctx, [(700, 920), (700 + 180 * math.cos(ang), 920 + 180 * math.sin(ang))], 8, hexc("#5b6475"))
    k = clamp(lt / 1.2)
    piece(ctx, P_ell(600, 860, 70 * k), hexc("#1a1d24"), lw=3, shadow=False) if k > 0.05 else None
    taladro(ctx, 260, 900, 0.8, pose)
    for lx in (180, 340):
        piece(ctx, P_rect(lx, 940, 20, 390), hexc("#3d3f4a"), lw=3, shadow=False)
    ts = since(ev, "sacan", lt)
    if ts >= 0:
        for i in range(int(clamp(ts / 1.2) * 5)):
            saco(ctx, 160 + i * 180, 1260, 0.5)


def sc_hotel(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    sede(ctx, 600, 900, 440, 430)
    piece(ctx, P_rect(40, 600, 440, 730), hexc("#c96a4a"), lw=5)
    piece(ctx, P_rrect(120, 560, 280, 60, 10), hexc("#ffe14d"), lw=4)
    txt(ctx, "HOTEL", 260, 603, 40, INK, anchor="center")
    for r in range(4):
        for c in range(3):
            lit = (r == 1 and c == 2)
            piece(ctx, P_rect(80 + c * 130, 660 + r * 160, 90, 110), hexc("#ffe58a") if lit else hexc("#3a3150"), lw=3, shadow=False)
    # dos siluetas en la ventana iluminada
    ctx.save()
    P_rect(340, 820, 90, 110)(ctx)
    ctx.clip()
    silueta(ctx, 370, 940, 0.3, pose)
    silueta(ctx, 405, 940, 0.3, pose, 2)
    ctx.restore()
    ctx.set_dash([16, 12])
    line(ctx, [(430, 870), (620, 1000)], 5, hexc("#ffe14d"))
    ctx.set_dash([])


def sc_rediseno(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    marcas = [("dosmil", "2.000", "#c9a46a"), ("cincomil", "5.000", "#8fbf8a"), ("diezmil", "10.000", "#c98a8a")]
    tc = since(ev, "cambiar", lt)
    for i, (key, v, c) in enumerate(marcas):
        y = 680 + i * 220
        nuevo = since(ev, key, lt) >= 0
        billete(ctx, 540, y, 520, 160, v, c if not nuevo else c, nuevo=nuevo, ang=math.radians(-3 + i * 3))
        if nuevo:
            stamp(ctx, 860, y - 40, "NUEVO", since(ev, key, lt), 34, col=hexc("#1d4ed8"), ang=10)
        elif tc >= 0:
            line(ctx, [(300, y - 60), (780, y + 60)], 10, ROJO)


def sc_tele(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    piece(ctx, P_rrect(130, 600, 820, 520, 20), hexc("#23242c"), lw=6)
    piece(ctx, P_rect(160, 630, 760, 460), hexc("#e8dcc0"), lw=3, shadow=False)
    ctx.save()
    P_rect(160, 630, 760, 460)(ctx)
    ctx.clip()
    sede(ctx, 260, 780, 560, 400)
    ctx.restore()
    piece(ctx, P_rect(500, 1120, 80, 80), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rect(400, 1200, 280, 30), hexc("#3d3f4a"), lw=4)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        billete(ctx, 820, 1250, 300, 100, "2.000", "#c9a46a", ang=math.radians(-12))
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 220, 1250 - bob, 130, hexc("#ffe14d"), INK, 7)


SCENES = dict(billetes=sc_billetes, banco=sc_banco, boveda=sc_boveda, hotel=sc_hotel, rediseno=sc_rediseno, tele=sc_tele)
SCENES = con_mapa(SCENES, BLOQUES, pais="COL", ciudad="VALLEDUPAR", lon=-73.25, lat=10.46)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_billetes(ctx, 0, 2.0, {"cambiar_lt": 0.6})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(113))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UN ROBO TAN GRANDE", 540, 220, 96, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "QUE CAMBIARON", 540, 380, 104, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡LOS BILLETES!", 540, 1690, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
