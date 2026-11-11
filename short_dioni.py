#!/usr/bin/env python3
"""
Short 17 · «El vigilante que se llevó el furgón» — El Dioni (Madrid, 1989)
Voz gratuita (python voz_gratis.py short_dioni.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, VERDE_BILLETE, avion_lado, fondo, gorra_poli, noche, silueta
from short_robo_siglo import saco

SLUG = "el-dioni"
PRONUNCIA = {}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pasaría si el vigilante que protege el dinero… decidiera llevárselo?",
        escenas=[(None, "furgon")],
        pantalla=[("el vigilante", "EL VIGILANTE…"), ("decidiera", "¿SE LO LLEVA?")],
        eventos={"decidiera": "decidiera"},
    ),
    dict(
        id="caso",
        voz=("Madrid, julio de 1989. Dionisio, vigilante de seguridad, conduce un furgón blindado con casi 300 "
             "millones de pesetas. Aprovecha que se queda solo con el vehículo… y arranca."),
        escenas=[(None, "calle"), ("y arranca", "huida")],
        pantalla=[(None, "MADRID, 1989"), ("casi 300", "300 MILLONES DE PESETAS"), ("Aprovecha", "SE QUEDA SOLO…"),
                  ("y arranca", "¡ARRANCA!")],
        eventos={"pesetas": "casi 300", "solo": "Aprovecha que"},
    ),
    dict(
        id="huida",
        voz=("Pasa el dinero a su coche, abandona el furgón y desaparece. Días después, vuela a Brasil. España "
             "entera habla de él."),
        escenas=[(None, "trasvase"), ("Días después", "vuelo")],
        pantalla=[(None, "DEL FURGÓN AL COCHE"), ("Días después", "RUMBO A BRASIL"), ("España entera", "TODA ESPAÑA HABLA DE ÉL")],
        eventos={"abandona": "abandona el", "espana": "España entera"},
    ),
    dict(
        id="detencion",
        voz="En septiembre lo detienen en Brasil. Pasa un año en una cárcel brasileña y después cumple condena en España.",
        escenas=[(None, "brasil"), ("y después", "condena")],
        pantalla=[(None, "DETENIDO EN BRASIL"), ("y después", "CONDENA EN ESPAÑA")],
        eventos={"detienen": "lo detienen"},
    ),
    dict(
        id="cierre",
        voz=("¿Y el dinero? Él asegura que casi todo desapareció por el camino, que le traicionaron las personas "
             "en las que confió. ¿Le crees?"),
        escenas=[(None, "dinero")],
        pantalla=[(None, "¿Y EL DINERO?"), ("le traicionaron", "«ME TRAICIONARON»"), ("Le crees", "¿LE CREES?")],
        eventos={"desaparecio": "casi todo", "pregunta": "Le crees"},
    ),
]


def furgon(ctx, x, y, s=1.0, puerta=0.0):
    """Furgón blindado genérico de lado (x,y = centro del suelo)."""
    piece(ctx, P_rrect(x - 330 * s, y - 330 * s, 500 * s, 280 * s, 14 * s), hexc("#c9ccd6"), lw=5)
    piece(ctx, P_poly([(x + 170 * s, y - 50 * s), (x + 170 * s, y - 280 * s), (x + 260 * s, y - 280 * s),
                       (x + 330 * s, y - 170 * s), (x + 330 * s, y - 50 * s)]), hexc("#b5bccb"), lw=5)
    piece(ctx, P_poly([(x + 190 * s, y - 180 * s), (x + 190 * s, y - 260 * s), (x + 250 * s, y - 260 * s),
                       (x + 305 * s, y - 180 * s)]), hexc("#8ec5e8"), lw=4, shadow=False)
    piece(ctx, P_rect(x - 330 * s, y - 200 * s, 500 * s, 40 * s), hexc("#1d4ed8"), lw=0, shadow=False, outline=False)
    txt(ctx, "BLINDADO", x - 80 * s, y - 230 * s, 44 * s, hexc("#1d4ed8"), anchor="center")
    for k in range(3):
        piece(ctx, P_ell(x - 300 * s + k * 20 * s, y - 300 * s, 6 * s), hexc("#5b6475"), lw=0, shadow=False, outline=False)
    if puerta > 0:
        piece(ctx, P_rect(x - 330 * s, y - 320 * s, 40 * s, 270 * s), hexc("#1a1d24"), lw=3, shadow=False)
    for wx in (x - 220 * s, x + 220 * s):
        piece(ctx, P_ell(wx, y - 40 * s, 55 * s), INK, lw=3, shadow=False)
        piece(ctx, P_ell(wx, y - 40 * s, 22 * s), hexc("#9aa0ab"), lw=2, shadow=False)


def coche(ctx, x, y, s=1.0, col="#c8202f"):
    piece(ctx, P_rrect(x - 200 * s, y - 120 * s, 400 * s, 80 * s, 24 * s), hexc(col), lw=5)
    piece(ctx, P_poly([(x - 120 * s, y - 120 * s), (x + 100 * s, y - 120 * s), (x + 60 * s, y - 190 * s),
                       (x - 90 * s, y - 190 * s)]), hexc(col), lw=5)
    piece(ctx, P_poly([(x - 100 * s, y - 125 * s), (x - 10 * s, y - 125 * s), (x - 10 * s, y - 180 * s),
                       (x - 80 * s, y - 180 * s)]), hexc("#bfe3f2"), lw=3, shadow=False)
    piece(ctx, P_poly([(x + 5 * s, y - 125 * s), (x + 85 * s, y - 125 * s), (x + 50 * s, y - 180 * s),
                       (x + 5 * s, y - 180 * s)]), hexc("#bfe3f2"), lw=3, shadow=False)
    for wx in (x - 120 * s, x + 120 * s):
        piece(ctx, P_ell(wx, y - 40 * s, 40 * s), INK, lw=3, shadow=False)
        piece(ctx, P_ell(wx, y - 40 * s, 15 * s), hexc("#9aa0ab"), lw=2, shadow=False)


def calle_madrid(ctx, pose, suelo=1300):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_ell(880, 640, 70), hexc("#ffe58a"), lw=4)
    for i, (x, w, h, col) in enumerate(((-20, 300, 560, "#e8b98a"), (300, 260, 640, "#d98a6a"),
                                        (580, 280, 520, "#e8d2a0"), (880, 260, 600, "#c9a07a"))):
        piece(ctx, P_rect(x, suelo - h, w, h), hexc(col), lw=4)
        for r in range(3):
            for c in range(2):
                piece(ctx, P_rect(x + 50 + c * (w - 140), suelo - h + 60 + r * 140, 60, 80), hexc("#4a6a8a"),
                      lw=3, shadow=False)
                line(ctx, [(x + 45 + c * (w - 140), suelo - h + 140 + r * 140), (x + 115 + c * (w - 140),
                                                                                  suelo - h + 140 + r * 140)], 6, INK)
    piece(ctx, P_rect(-10, suelo, 1100, 660), hexc("#6b6f78"), lw=4, shadow=False)
    piece(ctx, P_rect(-10, suelo, 1100, 30), hexc("#b5bccb"), lw=3, shadow=False)


def vigilante(ctx, x, feet, s, pose, k=0):
    silueta(ctx, x, feet, s, pose, k)
    gorra_poli(ctx, x, feet, s)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_furgon(ctx, pose, lt, ev):
    calle_madrid(ctx, pose)
    furgon(ctx, 560, 1380, 1.2)
    vigilante(ctx, 170, 1420, 0.95, pose)
    td = since(ev, "decidiera", lt)
    if td >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 170, 960 - bob, 160, hexc("#ffe14d"), INK, 7)
        for i in range(3):
            saco(ctx, 420 + i * 150, 1320, 0.55)


def sc_calle(ctx, pose, lt, ev):
    calle_madrid(ctx, pose)
    furgon(ctx, 560, 1380, 1.2)
    tp = since(ev, "pesetas", lt)
    if tp >= 0:
        stamp(ctx, 480, 920, "300 MILLONES", tp, 56, col=hexc("#2f6b45"), ang=-6)
    ts = since(ev, "solo", lt)
    if ts >= 0:
        for i in range(2):
            k = clamp((ts - i * 0.2) / 1.2)
            vigilante(ctx, lerp(150 + i * 90, -150, k), 1420, 0.85, pose, i)
        stamp(ctx, 810, 980, "SOLO", ts, 56, col=ROJO, ang=8)


def sc_huida(ctx, pose, lt, ev):
    calle_madrid(ctx, pose)
    k = ease_io(clamp(lt / 1.4))
    x = lerp(560, 1500, k)
    furgon(ctx, x, 1380, 1.2)
    for i in range(4):
        line(ctx, [(x - 460 - i * 60, 1250 + i * 30), (x - 380 - i * 60, 1250 + i * 30)], 8, (1, 1, 1))


def sc_trasvase(ctx, pose, lt, ev):
    calle_madrid(ctx, pose)
    ta = since(ev, "abandona", lt)
    furgon(ctx, 330, 1380, 0.9, puerta=1.0)
    coche(ctx, 860, 1380, 1.0)
    n = int(clamp(lt / 1.2) * 4)
    for i in range(4):
        if i < n:
            saco(ctx, 760 + (i % 2) * 120, 1180 - (i // 2) * 60, 0.45)
        else:
            saco(ctx, 160 + i * 70, 1210, 0.45)
    if ta >= 0:
        stamp(ctx, 330, 1000, "VACÍO", ta, 60, col=ROJO, ang=-8)


def mapa_vuelo(ctx, pose, lt):
    set_col(ctx, hexc("#7fb7d9"))
    ctx.paint()
    piece(ctx, P_poly([(620, 540), (780, 530), (820, 620), (720, 700), (600, 680)]), hexc("#f2d36b"), lw=5)
    txt(ctx, "ESPAÑA", 710, 625, 30, INK, anchor="center")
    piece(ctx, P_poly([(160, 1000), (380, 960), (440, 1100), (380, 1320), (260, 1380), (180, 1240), (130, 1100)]),
          hexc("#8fd18a"), lw=5)
    txt(ctx, "BRASIL", 290, 1170, 36, INK, anchor="center")
    k = ease_io(clamp(lt / 2.0))
    pts = [(lerp(700, 300, t), lerp(640, 1100, t) - 220 * math.sin(math.pi * t)) for t in [i / 30 * k for i in range(31)]]
    if len(pts) > 1:
        ctx.set_dash([18, 14])
        line(ctx, pts, 6, ROJO)
        ctx.set_dash([])
    px, py = pts[-1]
    piece(ctx, P_poly([(px + 30, py), (px - 30, py - 22), (px - 18, py), (px - 30, py + 22)]), (1, 1, 1), lw=4)


def sc_vuelo(ctx, pose, lt, ev):
    mapa_vuelo(ctx, pose, lt)
    te = since(ev, "espana", lt)
    if te >= 0:
        for i in range(3):
            with rot(ctx, 800, 900 + i * 120, math.radians(-6 + i * 5)):
                piece(ctx, P_rect(650, 840 + i * 120, 320, 110), hexc("#f3f1ea"), lw=4)
                txt(ctx, "¡EL DIONI!", 810, 905 + i * 120, 40, INK, anchor="center")


def sc_brasil(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#e8cf94"), lw=4, shadow=False)
    for x in (140, 940):
        line(ctx, [(x, 1260), (x + 30, 820)], 22, hexc("#7a4e2c"))
        for a in range(5):
            ang = math.radians(-160 + a * 35)
            line(ctx, [(x + 30, 820), (x + 30 + 170 * math.cos(ang), 820 + 90 * math.sin(ang) + 40)], 26, hexc("#2f9e4f"))
    silueta(ctx, 540, 1300, 1.2, pose)
    td = since(ev, "detienen", lt)
    if td >= 0:
        stamp(ctx, 540, 900, "¡DETENIDO!", td, 70, col=ROJO, ang=-8)


def sc_condena(ctx, pose, lt, ev):
    fondo(ctx, "#5b6475", 1330, "#3d3f4a")
    silueta(ctx, 540, 1290, 1.2, pose)
    for i in range(9):
        line(ctx, [(140 + i * 100, 540), (140 + i * 100, 1330)], 14, hexc("#2b2d33"))
    line(ctx, [(120, 600), (960, 600)], 16, hexc("#2b2d33"))
    piece(ctx, P_rrect(380, 1150, 320, 90, 14), (1, 1, 1), lw=4)
    txt(ctx, "ESPAÑA", 540, 1213, 52, INK, anchor="center")


def sc_dinero(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i, x in enumerate((300, 540, 780)):
        piece(ctx, P_poly([(x - 90, 1300), (x + 90, 1300), (x + 105, 1140), (x + 50, 1080), (x - 50, 1080), (x - 105, 1140)]),
              hexc("#c9a46a"), lw=5)
        piece(ctx, P_ell(x, 1090, 55, 16), hexc("#3a2418"), lw=3, shadow=False)
    td = since(ev, "desaparecio", lt)
    if td >= 0:
        for i in range(8):
            k = clamp((td - i * 0.1) / 1.5)
            if k <= 0 or k >= 1:
                continue
            bx = 540 + (hnoise("vb", i) - 0.5) * 700 * k
            by = 1060 - 500 * k
            with rot(ctx, bx, by, math.radians(hnoise("vb", i, "a") * 360 * k)):
                piece(ctx, P_rect(bx - 50, by - 20, 100, 40), VERDE_BILLETE, lw=3, shadow=False)
    bob = (pose // 4) % 2 * 10
    draw_text(ctx, "?", 540, 900 - bob, 220, hexc("#ffe14d"), INK, 9) if td < 0 or td > 1.6 else None


SCENES = dict(furgon=sc_furgon, calle=sc_calle, huida=sc_huida, trasvase=sc_trasvase, vuelo=sc_vuelo,
              brasil=sc_brasil, condena=sc_condena, dinero=sc_dinero)
SCENES = con_mapa(SCENES, BLOQUES, pais="ESP", ciudad="MADRID", lon=-3.7, lat=40.42)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_furgon(ctx, 0, 2.0, {"decidiera_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(61))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "EL VIGILANTE", 540, 220, 110, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "SE LLEVÓ EL FURGÓN", 540, 380, 96, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡300 MILLONES!", 540, 1690, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
