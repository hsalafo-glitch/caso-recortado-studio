#!/usr/bin/env python3
"""
Short 30 · «Robó mapas de 500 años en la Biblioteca Nacional» — Madrid, 2007
Voz gratuita (python voz_gratis.py short_ptolomeo.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, avion_lado, fondo, silueta

SLUG = "mapas-ptolomeo"
PRONUNCIA = {"Ptolomeo": "Tolomeo"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("Imagina que un hombre entra en la Biblioteca Nacional de España como investigador… y sale con mapas de "
             "más de 500 años."),
        escenas=[(None, "biblioteca"), ("y sale", "mapa")],
        pantalla=[("la Biblioteca", "BIBLIOTECA NACIONAL"), ("y sale", "MAPAS DE +500 AÑOS")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Madrid, 2007. Un supuesto historiador pide en la sala de lectura una joya de 1482: la Cosmografía de "
             "Ptolomeo, con mapas del mundo impresos hace siglos."),
        escenas=[(None, "sala")],
        pantalla=[(None, "MADRID, 2007"), ("una joya", "UNA JOYA DE 1482")],
        eventos={"libro": "una joya"},
    ),
    dict(
        id="faltan",
        voz="Tiempo después, al revisar el libro, descubren que faltan páginas: le habían arrancado varios mapas.",
        escenas=[(None, "faltan")],
        pantalla=[(None, "TIEMPO DESPUÉS…"), ("descubren", "¡FALTAN PÁGINAS!")],
        eventos={"faltan": "faltan páginas"},
    ),
    dict(
        id="rastro",
        voz=("La policía sigue su rastro por medio mundo. Aparecen mapas en Argentina, en Estados Unidos… y dos en "
             "Australia, en casa de un anticuario que los había comprado en una subasta en Londres."),
        escenas=[(None, "mundo")],
        pantalla=[(None, "POR MEDIO MUNDO"), ("Aparecen", "ARGENTINA · EE. UU."), ("y dos", "¡Y AUSTRALIA!")],
        eventos={"argentina": "en Argentina", "eeuu": "en Estados", "australia": "y dos", "subasta": "una subasta"},
    ),
    dict(
        id="cierre",
        voz="El escándalo hizo dimitir a la directora de la biblioteca. ¿Cuántos tesoros crees que se pierden así?",
        escenas=[(None, "final")],
        pantalla=[(None, "DIMITE LA DIRECTORA"), ("Cuántos", "¿CUÁNTOS TESOROS MÁS?")],
        eventos={"pregunta": "Cuántos tesoros"},
    ),
]

PERGAMINO = hexc("#e8d9b0")


def mapa_antiguo(ctx, x, y, w, h, ang=0.0):
    with rot(ctx, x + w / 2, y + h / 2, ang):
        piece(ctx, P_rect(x, y, w, h), PERGAMINO, lw=4)
        piece(ctx, P_ell(x + w / 2, y + h * 0.55, w * 0.42, h * 0.32), hexc("#c9b48a"), lw=3, shadow=False)
        piece(ctx, P_poly([(x + w * 0.3, y + h * 0.45), (x + w * 0.5, y + h * 0.35), (x + w * 0.7, y + h * 0.45),
                           (x + w * 0.62, y + h * 0.7), (x + w * 0.38, y + h * 0.68)]), hexc("#a8946a"), lw=2, shadow=False)
        for i in range(5):
            line(ctx, [(x + w * 0.1, y + h * (0.3 + i * 0.1)), (x + w * 0.9, y + h * (0.3 + i * 0.1))], 1.5, (0.4, 0.3, 0.2, 0.5))
        piece(ctx, P_ell(x + w * 0.12, y + h * 0.15, w * 0.06), hexc("#c9b48a"), lw=2, shadow=False)
        piece(ctx, P_ell(x + w * 0.88, y + h * 0.15, w * 0.06), hexc("#c9b48a"), lw=2, shadow=False)


def libro_abierto(ctx, x, y, s, falta=0.0):
    piece(ctx, P_poly([(x - 380 * s, y - 220 * s), (x, y - 190 * s), (x + 380 * s, y - 220 * s), (x + 380 * s, y + 220 * s),
                       (x, y + 250 * s), (x - 380 * s, y + 220 * s)]), hexc("#7a3a1f"), lw=5)
    piece(ctx, P_poly([(x - 350 * s, y - 200 * s), (x - 10 * s, y - 175 * s), (x - 10 * s, y + 225 * s), (x - 350 * s, y + 200 * s)]),
          PERGAMINO, lw=3)
    piece(ctx, P_poly([(x + 10 * s, y - 175 * s), (x + 350 * s, y - 200 * s), (x + 350 * s, y + 200 * s), (x + 10 * s, y + 225 * s)]),
          PERGAMINO, lw=3)
    mapa_antiguo(ctx, x - 320 * s, y - 150 * s, 280 * s, 320 * s)
    if falta > 0:
        ctx.save()
        ctx.set_source_rgba(0.1, 0.06, 0.03, 1)
        pts = [(x + 20 * s, y - 170 * s), (x + 60 * s, y - 120 * s), (x + 30 * s, y - 60 * s), (x + 70 * s, y), (x + 25 * s, y + 70 * s),
               (x + 60 * s, y + 140 * s), (x + 20 * s, y + 220 * s)]
        line(ctx, pts, 8 * s, hexc("#5a3820"))
        ctx.restore()
    else:
        mapa_antiguo(ctx, x + 40 * s, y - 150 * s, 280 * s, 320 * s)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_biblioteca(ctx, pose, lt, ev):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 660), hexc("#b5a888"), lw=4, shadow=False)
    piece(ctx, P_rect(100, 760, 880, 540), hexc("#e8dcc0"), lw=5)
    piece(ctx, P_poly([(80, 760), (1000, 760), (540, 580)]), hexc("#d9c7a3"), lw=5)
    for i in range(6):
        piece(ctx, P_rect(150 + i * 140, 800, 60, 460), hexc("#f3f1ea"), lw=3)
    piece(ctx, P_rrect(300, 700, 480, 50, 10), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "BIBLIOTECA NACIONAL", 540, 735, 30, INK, anchor="center")
    x = lerp(-150, 540, ease_io(clamp(lt / 1.6)))
    silueta(ctx, x, 1330, 0.95, pose)
    piece(ctx, P_rrect(x + 60, 1180, 90, 70, 10), hexc("#5a3820"), lw=3, shadow=False)


def sc_mapa(ctx, pose, lt, ev):
    fondo(ctx, "#3a3150", 1330, "#241e33")
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    mapa_antiguo(ctx, 540 - 300 * k, 920 - 260 * k, 600 * max(0.05, k), 520 * max(0.05, k), math.radians(-4))
    piece(ctx, P_rrect(400, 1250, 280, 70, 12), hexc("#1d2433"), lw=4)
    txt(ctx, "1482", 540, 1300, 48, hexc("#ffe14d"), anchor="center")


def sc_sala(ctx, pose, lt, ev):
    fondo(ctx, "#6b4a33", 1330, "#4a3020")
    for i in range(6):
        piece(ctx, P_rect(40 + i * 175, 560, 150, 420), hexc("#5a3820"), lw=4)
        for j in range(4):
            for b in range(5):
                piece(ctx, P_rect(50 + i * 175 + b * 28, 580 + j * 100, 22, 80),
                      hexc(["#c94a4a", "#4a7ac9", "#d9c7a3", "#5fa35a", "#a77c44"][(b + j + i) % 5]), lw=1, shadow=False)
    silueta(ctx, 540, 1150, 1.0, pose)
    piece(ctx, P_rect(120, 1130, 840, 40), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(160, 1170, 30, 160), hexc("#5a3820"), lw=3, shadow=False)
    piece(ctx, P_rect(890, 1170, 30, 160), hexc("#5a3820"), lw=3, shadow=False)
    tl = since(ev, "libro", lt)
    if tl >= 0:
        libro_abierto(ctx, 540, 1060, 0.4)
        piece(ctx, P_ell(860, 900, 40), hexc("#ffe58a"), lw=3)
        line(ctx, [(860, 940), (860, 1130)], 6, hexc("#3d3f4a"))


def sc_faltan(ctx, pose, lt, ev):
    fondo(ctx, "#3a3150", 1330, "#241e33")
    tf = since(ev, "faltan", lt)
    libro_abierto(ctx, 540, 940, 1.1, falta=1.0 if tf >= 0 else 0.0)
    if tf >= 0:
        k = ease_io(clamp(tf / 0.6))
        magnifier(ctx, lerp(1000, 720, k), lerp(1300, 1000, k), 110, math.radians(-30))
        stamp(ctx, 540, 1290, "ARRANCADOS", tf, 60, col=ROJO, ang=-6)


def sc_mundo(ctx, pose, lt, ev):
    set_col(ctx, hexc("#7fb7d9"))
    ctx.paint()
    zonas = {"ESPAÑA": (560, 640, "#f2d36b"), "ARGENTINA": (330, 1200, "#8fd18a"), "EE. UU.": (250, 740, "#f2a46b"),
             "AUSTRALIA": (880, 1180, "#e8b98a"), "LONDRES": (540, 560, "#c9b4e8")}
    for nombre, (x, y, c) in zonas.items():
        piece(ctx, P_ell(x, y, 110 if nombre not in ("LONDRES",) else 60, 80 if nombre != "LONDRES" else 40), hexc(c), lw=4)
        txt(ctx, nombre, x, y + 12, 28 if nombre != "LONDRES" else 22, INK, anchor="center")
    orden = [("argentina", "ARGENTINA"), ("eeuu", "EE. UU."), ("australia", "AUSTRALIA")]
    for key, nombre in orden:
        t = since(ev, key, lt)
        if t >= 0:
            x0, y0 = zonas["ESPAÑA"][:2]
            x1, y1 = zonas[nombre][:2]
            k = ease_io(clamp(t / 0.8))
            ctx.set_dash([14, 10])
            line(ctx, [(x0, y0), (lerp(x0, x1, k), lerp(y0, y1, k))], 5, ROJO)
            ctx.set_dash([])
            if k >= 1:
                mapa_antiguo(ctx, x1 - 40, y1 - 120, 80, 70, math.radians(-8))
    ts = since(ev, "subasta", lt)
    if ts >= 0:
        stamp(ctx, 540, 900, "VENDIDOS EN SUBASTA", ts, 44, col=hexc("#7b4dff"), ang=-6)


def sc_final(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    piece(ctx, P_rect(120, 1100, 840, 40), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(150, 1140, 780, 190), hexc("#5a3820"), lw=4)
    x, feet = 540, 1110
    piece(ctx, P_rrect(x - 75, feet - 330, 150, 160, 60), hexc("#3a2a1e"), lw=4, shadow=False)
    silueta(ctx, x, feet, 0.9, pose)
    piece(ctx, P_rect(700, 1020, 160, 80), (1, 1, 1), lw=3)
    txt(ctx, "DIMISIÓN", 780, 1070, 26, INK, anchor="center")
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        for i in range(3):
            mapa_antiguo(ctx, 150 + i * 280, 600 + (i % 2) * 60, 200, 160, math.radians(-10 + i * 10))
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 880, 920 - bob, 120, hexc("#ffe14d"), INK, 6)


SCENES = dict(biblioteca=sc_biblioteca, mapa=sc_mapa, sala=sc_sala, faltan=sc_faltan, mundo=sc_mundo, final=sc_final)
SCENES = con_mapa(SCENES, BLOQUES, pais="ESP", ciudad="MADRID", lon=-3.7, lat=40.42)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_faltan(ctx, 0, 2.0, {"faltan_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(127))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ARRANCÓ MAPAS", 540, 220, 106, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "DE 500 AÑOS", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡EN LA BIBLIOTECA NACIONAL!", 540, 1690, 74, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
