#!/usr/bin/env python3
"""
Short 25 · «Cuatro estudiantes robaron la Piedra del Destino» — Westminster, Navidad de 1950
Voz gratuita (python voz_gratis.py short_piedra.py).
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
from short_dioni import coche
from short_codice import catedral

SLUG = "piedra-destino"
PRONUNCIA = {"Westminster": "Güéstminster"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("Imagina que cuatro estudiantes roban una piedra de 150 kilos… de la abadía donde se coronan los reyes "
             "de Inglaterra."),
        escenas=[(None, "piedra"), ("de la", "abadia")],
        pantalla=[("cuatro", "4 ESTUDIANTES"), ("una piedra", "UNA PIEDRA DE 150 KG"), ("de la", "¿EN LA ABADÍA REAL?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Londres, Navidad de 1950. La Piedra del Destino, un símbolo de Escocia, lleva siglos bajo el trono de "
             "la coronación, en la abadía de Westminster. Cuatro estudiantes escoceses deciden llevársela a casa."),
        escenas=[(None, "trono"), ("Cuatro estudiantes", "estudiantes")],
        pantalla=[(None, "LONDRES, NAVIDAD DE 1950"), ("un símbolo", "SÍMBOLO DE ESCOCIA"), ("Cuatro estudiantes", "¡A CASA!")],
        eventos={"siglos": "lleva siglos"},
    ),
    dict(
        id="rotura",
        voz="Entran de noche, la sacan del trono… y se les cae al suelo. La piedra se parte en dos.",
        escenas=[(None, "caida")],
        pantalla=[(None, "DE NOCHE"), ("y se", "¡SE LES CAE!"), ("La piedra", "PARTIDA EN DOS")],
        eventos={"cae": "y se", "parte": "se parte"},
    ),
    dict(
        id="huida",
        voz="Aun así, cruzan el país con los trozos escondidos en sus coches. En Escocia la reparan en secreto.",
        escenas=[(None, "carretera"), ("En Escocia", "taller")],
        pantalla=[(None, "RUMBO A ESCOCIA"), ("En Escocia", "REPARADA EN SECRETO")],
        eventos={},
    ),
    dict(
        id="cierre",
        voz=("Meses después aparece en una abadía escocesa, envuelta en una bandera de Escocia. ¿Fue un robo… o "
             "una devolución?"),
        escenas=[(None, "bandera")],
        pantalla=[(None, "MESES DESPUÉS…"), ("Fue un", "¿ROBO O DEVOLUCIÓN?")],
        eventos={"bandera": "envuelta en", "pregunta": "Fue un"},
    ),
]

PIEDRA = hexc("#b0946a")


def piedra(ctx, x, y, s=1.0, partida=0.0, ang=0.0):
    w, h = 300 * s, 150 * s
    if partida <= 0:
        with rot(ctx, x, y, ang):
            piece(ctx, P_rrect(x - w / 2, y - h / 2, w, h, 14 * s), PIEDRA, lw=5)
            for i in range(10):
                piece(ctx, P_ell(x - w / 2 + 20 * s + hnoise("pd", i) * (w - 40 * s), y - h / 2 + 20 * s + hnoise("pd", i, "y") * (h - 40 * s),
                                 7 * s), hexc("#957a54"), lw=0, shadow=False, outline=False)
            for dx in (-w / 2 + 30 * s, w / 2 - 30 * s):
                piece(ctx, P_ell(x + dx, y - h / 2 + 10 * s, 18 * s, 10 * s), hexc("#5b6475"), lw=3, shadow=False)
        return
    g_ = 40 * s * partida
    for side in (-1, 1):
        cx = x + side * (w / 4 + g_)
        with rot(ctx, cx, y, ang + side * math.radians(6) * partida):
            piece(ctx, P_poly([(cx - w / 4, y - h / 2), (cx + w / 4 - (12 * s if side < 0 else 0), y - h / 2),
                               (cx + w / 4 + (side * 10 * s), y), (cx + w / 4 - (8 * s if side < 0 else 0), y + h / 2),
                               (cx - w / 4, y + h / 2)]), PIEDRA, lw=5)


def trono(ctx, x, y, s=1.0, con_piedra=True):
    piece(ctx, P_poly([(x - 170 * s, y), (x + 170 * s, y), (x + 150 * s, y - 640 * s), (x, y - 760 * s),
                       (x - 150 * s, y - 640 * s)]), hexc("#8a5a2c"), lw=6)
    piece(ctx, P_rect(x - 140 * s, y - 360 * s, 280 * s, 40 * s), hexc("#a8743a"), lw=4)
    piece(ctx, P_rect(x - 140 * s, y - 200 * s, 280 * s, 200 * s), hexc("#5a3820"), lw=4)
    if con_piedra:
        piedra(ctx, x, y - 95 * s, 0.85 * s)
    for dx in (-170, 170):
        piece(ctx, P_ell(x + dx * s, y + 10 * s, 40 * s, 24 * s), ORO, lw=4)


def bandera_escocia(ctx, x, y, w, h):
    piece(ctx, P_rect(x, y, w, h), hexc("#1d5fc9"), lw=4)
    ctx.save()
    P_rect(x, y, w, h)(ctx)
    ctx.clip()
    line(ctx, [(x, y), (x + w, y + h)], h * 0.2, (1, 1, 1))
    line(ctx, [(x + w, y), (x, y + h)], h * 0.2, (1, 1, 1))
    ctx.restore()


# ─────────────────────────────── escenas ───────────────────────────────
def sc_piedra(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    piedra(ctx, 540, 960, 1.7 * max(0.05, k))
    for i in range(4):
        silueta(ctx, 160 + i * 250 + (0 if i < 2 else 0), 1330, 0.6, pose, i) if lt > 0.6 else None
    piece(ctx, P_rrect(380, 1120, 320, 90, 14), hexc("#1d2433"), lw=4)
    txt(ctx, "150 KG", 540, 1185, 60, hexc("#ffe14d"), anchor="center")


def sc_abadia(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fb0c4"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 660), hexc("#6b6f78"), lw=4, shadow=False)
    catedral(ctx, 540, 1300, 0.85)
    # corona
    piece(ctx, P_poly([(440, 560), (470, 500), (505, 540), (540, 480), (575, 540), (610, 500), (640, 560)]), ORO, lw=4)
    piece(ctx, P_rect(440, 560, 200, 34), ORO, lw=4)


def sc_trono(ctx, pose, lt, ev):
    fondo(ctx, "#4a3a5a", 1330, "#2e2238")
    for i in range(3):
        piece(ctx, P_rrect(100 + i * 330, 560, 200, 360, 100), hexc("#6a8ac9") if i == 1 else hexc("#5a7ab0"), lw=4, shadow=False)
    trono(ctx, 540, 1320, 1.0)
    ts = since(ev, "siglos", lt)
    if ts >= 0:
        stamp(ctx, 540, 1060, "SIGLOS AQUÍ", ts, 48, col=hexc("#1d5fc9"), ang=-6)


def sc_estudiantes(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    for i in range(4):
        x = 180 + i * 240
        silueta(ctx, x, 1330, 0.95, pose, i)
        # bufanda universitaria
        piece(ctx, P_rect(x - 60, 1330 - 225 * 0.95, 120, 26), hexc("#c8202f") if i % 2 else hexc("#1d5fc9"), lw=3, shadow=False)
    bandera_escocia(ctx, 840, 600, 180, 120)
    line(ctx, [(840, 600), (840, 900)], 8, hexc("#7a4e2c"))


def sc_caida(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", 1330, "#1a1428")
    trono(ctx, 760, 1320, 0.8, con_piedra=False)
    tc = since(ev, "cae", lt)
    tp = since(ev, "parte", lt)
    if tc < 0:
        x = lerp(760, 470, ease_io(clamp(lt / 1.2)))
        piedra(ctx, x, 1180, 1.0)
        for i in range(2):
            silueta(ctx, x - 230 + i * 460, 1330, 0.85, pose, i)
    else:
        k = clamp(tc / 0.4)
        y = lerp(1180, 1250, k)
        piedra(ctx, 470, y, 1.0, partida=clamp(tp / 0.4) if tp >= 0 else 0.0)
        if k >= 1 and (pose // 2) % 2 == 0:
            draw_text(ctx, "¡CRAC!", 470, 1050, 90, hexc("#ffe14d"), INK, 7)
        for i in range(2):
            silueta(ctx, 240 + i * 460, 1330, 0.85, pose, i)


def sc_carretera(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1250)
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#3d3f4a"), lw=4, shadow=False)
    for i in range(6):
        piece(ctx, P_rect(i * 200 - (pose * 10) % 200, 1360, 110, 14), hexc("#f2e7b0"), lw=0, shadow=False, outline=False)
    x = lerp(150, 760, ease_io(clamp(lt / 2.5)))
    coche(ctx, x, 1340, 1.1, "#2f5f88")
    piece(ctx, P_rrect(60, 600, 300, 70, 12), hexc("#2f9e4f"), lw=4)
    txt(ctx, "← LONDRES", 210, 648, 34, (1, 1, 1), anchor="center")
    piece(ctx, P_rrect(720, 600, 300, 70, 12), hexc("#1d5fc9"), lw=4)
    txt(ctx, "ESCOCIA →", 870, 648, 34, (1, 1, 1), anchor="center")
    piedra(ctx, x - 80, 1110, 0.35, partida=0.6)


def sc_taller(ctx, pose, lt, ev):
    fondo(ctx, "#6b5a4a", 1330, "#4a3a2a")
    piece(ctx, P_rect(160, 1150, 760, 50), hexc("#7a4e2c"), lw=5)
    for x in (190, 860):
        piece(ctx, P_rect(x, 1200, 30, 130), hexc("#5a3820"), lw=3, shadow=False)
    k = clamp(lt / 1.4)
    piedra(ctx, 540, 1070, 0.9, partida=1 - k)
    silueta(ctx, 900, 1330, 0.85, pose)
    with rot(ctx, 820, 1000, math.radians(-30 if (pose // 2) % 2 else 0)):
        piece(ctx, P_rect(760, 990, 100, 26), hexc("#9aa0ab"), lw=3)
        line(ctx, [(810, 1016), (840, 1080)], 10, hexc("#7a4e2c"))
    if k >= 1:
        stamp(ctx, 540, 860, "REPARADA", lt - 1.4, 56, col=hexc("#2fb35a"), ang=-6)


def sc_bandera(ctx, pose, lt, ev):
    fondo(ctx, "#5a5a6a", 1330, "#3a3a4a")
    # ruinas de abadía
    for x in (160, 920):
        piece(ctx, P_rect(x - 60, 560, 120, 770), hexc("#9a7a6a"), lw=5)
    piece(ctx, P_poly([(100, 560), (980, 560), (540, 470)]), hexc("#9a7a6a"), lw=5)
    ctx.new_sub_path()
    ctx.arc(540, 760, 250, math.pi, 2 * math.pi)
    set_col(ctx, hexc("#2b2340"))
    ctx.fill()
    piece(ctx, P_rect(340, 1130, 400, 200), hexc("#b5a888"), lw=5)
    tb = since(ev, "bandera", lt)
    if tb >= 0:
        k = ease_out_back(clamp(tb / 0.4)) if tb < 0.4 else 1.0
        piedra(ctx, 540, 1060, 0.9)
        bandera_escocia(ctx, 540 - 170 * k, 960, 340 * max(0.05, k), 160)
    else:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 900 - bob, 160, hexc("#ffe14d"), INK, 7)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        stamp(ctx, 540, 780, "¿ROBO?", tq, 60, col=ROJO, ang=-8)


SCENES = dict(piedra=sc_piedra, abadia=sc_abadia, trono=sc_trono, estudiantes=sc_estudiantes, caida=sc_caida,
              carretera=sc_carretera, taller=sc_taller, bandera=sc_bandera)
SCENES = con_mapa(SCENES, BLOQUES, pais="GBR", ciudad="LONDRES", lon=-0.13, lat=51.5)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_caida(ctx, 0, 2.0, {"cae_lt": 0.2, "parte_lt": 0.6})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(101))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "4 ESTUDIANTES", 540, 220, 108, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "ROBARON UNA PIEDRA", 540, 380, 92, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y SE LES ROMPIÓ!", 540, 1690, 100, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
