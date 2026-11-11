#!/usr/bin/env python3
"""
Short 24 · «La falsa heredera que engañó a Nueva York» — Anna Sorokin «Delvey» (2016-2019)
Voz gratuita (python voz_gratis.py short_heredera.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, VERDE_BILLETE, avion_lado, fondo, gafas_oscuras, silueta

SLUG = "falsa-heredera"
PRONUNCIA = {"Delvey": "Délvi", "Sorokin": "Sorókin"}

BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina vivir en hoteles de lujo de Nueva York… haciéndote pasar por una millonaria que no existe.",
        escenas=[(None, "hotel")],
        pantalla=[("hoteles", "HOTELES DE LUJO"), ("haciéndote", "¿MILLONARIA FALSA?")],
        eventos={"falsa": "haciéndote pasar"},
    ),
    dict(
        id="caso",
        voz=("Nueva York, 2016. Una joven dice ser Anna Delvey, una heredera alemana con una fortuna de unos 60 "
             "millones de euros. Viste caro, da propinas de cien dólares… y todos la creen."),
        escenas=[(None, "heredera")],
        pantalla=[(None, "NUEVA YORK, 2016"), ("una heredera", "«HEREDERA ALEMANA»"), ("Viste caro", "PROPINAS DE 100 $")],
        eventos={"fortuna": "una fortuna", "propinas": "da propinas", "creen": "todos la"},
    ),
    dict(
        id="deudas",
        voz=("Pero no hay fortuna. Deja facturas de hotel sin pagar, alquila un jet privado que nunca paga e intenta "
             "conseguir un préstamo de 22 millones de dólares."),
        escenas=[(None, "factura"), ("alquila un", "jet"), ("e intenta", "prestamo")],
        pantalla=[(None, "NO HAY FORTUNA"), ("alquila un", "JET PRIVADO SIN PAGAR"), ("e intenta", "PRÉSTAMO DE 22 MILLONES $")],
        eventos={"sinpagar": "sin pagar"},
    ),
    dict(
        id="juicio",
        voz=("En 2019, un jurado la declara culpable: se había quedado con unos 275.000 dólares de bancos, hoteles "
             "y amigos. Su verdadero nombre era Anna Sorokin."),
        escenas=[(None, "juicio")],
        pantalla=[(None, "2019: CULPABLE"), ("se había", "≈ 275.000 $"), ("Su verdadero", "ANNA SOROKIN")],
        eventos={"culpable": "declara culpable", "nombre": "Su verdadero"},
    ),
    dict(
        id="cierre",
        voz="Hoy su historia es una serie de televisión. ¿Tú te habrías creído que era millonaria?",
        escenas=[(None, "serie")],
        pantalla=[(None, "AHORA ES UNA SERIE"), ("Tú te", "¿TE LO HABRÍAS CREÍDO?")],
        eventos={"pregunta": "Tú te"},
    ),
]


def dama(ctx, x, feet, s, pose, k=0):
    """Silueta sin rasgos con melena, gafas de sol y bolso (persona real)."""
    hr = 72 * s
    hy = feet - 230 * s - hr * 0.9
    piece(ctx, P_rrect(x - hr * 1.15, hy - hr * 0.9, hr * 2.3, hr * 2.5, hr * 0.9), hexc("#3a2a1e"), lw=4, shadow=False)
    silueta(ctx, x, feet, s, pose, k)
    gafas_oscuras(ctx, x, feet, s)
    piece(ctx, P_rrect(x + 60 * s, feet - 140 * s, 90 * s, 70 * s, 12 * s), hexc("#c8202f"), lw=4, shadow=False)
    ctx.new_sub_path()
    ctx.arc(x + 105 * s, feet - 140 * s, 30 * s, math.pi, 2 * math.pi)
    set_col(ctx, INK)
    ctx.set_line_width(4)
    ctx.stroke()


def lobby(ctx, pose):
    fondo(ctx, "#6b3a4a", 1330, "#3a1e28")
    for i in range(5):
        piece(ctx, P_rect(40 + i * 220, 540, 60, 790), hexc("#d9b46a"), lw=4, shadow=False)
    for x in (320, 760):
        line(ctx, [(x, 520), (x, 600)], 4, ORO)
        for i in range(5):
            piece(ctx, P_ell(x - 60 + i * 30, 620 + (i % 2) * 10, 12), hexc("#fff3b0"), lw=2, shadow=False)
    for i in range(8):
        piece(ctx, P_rect(i * 140 - 20, 1330, 130, 630), hexc("#3a2a20") if i % 2 else hexc("#2b2418"), lw=0, shadow=False, outline=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_hotel(ctx, pose, lt, ev):
    lobby(ctx, pose)
    dama(ctx, 540, 1330, 1.25, pose)
    tf = since(ev, "falsa", lt)
    if tf >= 0:
        stamp(ctx, 540, 820, "¿MILLONARIA?", tf, 60, col=ROJO, ang=-8)


def sc_heredera(ctx, pose, lt, ev):
    lobby(ctx, pose)
    dama(ctx, 380, 1330, 1.15, pose)
    tf = since(ev, "fortuna", lt)
    if tf >= 0:
        piece(ctx, P_rrect(560, 600, 460, 120, 16), hexc("#1d2433"), lw=4)
        v = int(60 * ease_io(clamp(tf / 1.0)))
        txt(ctx, f"{v} MILLONES €", 790, 680, 52, hexc("#9fd6a0"), anchor="center")
    tp = since(ev, "propinas", lt)
    if tp >= 0:
        for i in range(6):
            k = clamp((tp - i * 0.15) / 1.0)
            if 0 < k < 1:
                bx, by = lerp(480, 600 + i * 70, k), lerp(1150, 900 + (i % 2) * 120, k)
                with rot(ctx, bx, by, math.radians(k * 200 + i * 30)):
                    piece(ctx, P_rect(bx - 55, by - 22, 110, 44), VERDE_BILLETE, lw=3, shadow=False)
                    txt(ctx, "100", bx, by + 10, 24, hexc("#2f6b45"), anchor="center")
    tc = since(ev, "creen", lt)
    if tc >= 0:
        for i in range(3):
            silueta(ctx, 700 + i * 130, 1330, 0.7, pose, i)
        stamp(ctx, 830, 960, "¡SE LO CREEN!", tc, 46, col=hexc("#2fb35a"), ang=6)


def sc_factura(ctx, pose, lt, ev):
    lobby(ctx, pose)
    with rot(ctx, 540, 900, math.radians(-4)):
        piece(ctx, P_rect(300, 560, 480, 680), (1, 1, 1), lw=5)
        txt(ctx, "FACTURA", 540, 650, 54, INK, anchor="center")
        for i in range(8):
            line(ctx, [(340, 720 + i * 50), (740, 720 + i * 50)], 5, hexc("#c9ccd6"))
        txt(ctx, "TOTAL: $$$", 540, 1180, 44, INK, anchor="center")
    ts = since(ev, "sinpagar", lt)
    if ts >= 0:
        stamp(ctx, 540, 960, "SIN PAGAR", ts, 70, col=ROJO, ang=-12)


def sc_jet(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#6b6f78"), lw=4, shadow=False)
    x = lerp(560, 900, ease_io(clamp(lt / 2.0)))
    with rot(ctx, x, 1000, math.radians(-8 * clamp(lt / 2.0))):
        avion_lado(ctx, x, 1000, 0.75)
    stamp(ctx, 540, 1180, "35.400 $ · SIN PAGAR", lt - 0.6, 46, col=ROJO, ang=-6)


def sc_prestamo(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    piece(ctx, P_rect(260, 560, 560, 700), hexc("#f3f1ea"), lw=5)
    txt(ctx, "SOLICITUD", 540, 640, 50, INK, anchor="center")
    txt(ctx, "PRÉSTAMO", 540, 700, 40, hexc("#5b6475"), anchor="center")
    piece(ctx, P_rect(320, 760, 440, 100), hexc("#e3e6ec"), lw=3, shadow=False)
    v = int(22 * ease_io(clamp(lt / 1.0)))
    txt(ctx, f"{v}.000.000 $", 540, 830, 50, INK, anchor="center")
    for i in range(4):
        line(ctx, [(320, 920 + i * 60), (760, 920 + i * 60)], 4, hexc("#c9ccd6"))
    if lt > 1.2:
        stamp(ctx, 540, 1140, "¿AVAL? NINGUNO", lt - 1.2, 46, col=ROJO, ang=-8)


def sc_juicio(ctx, pose, lt, ev):
    fondo(ctx, "#6b4a33", 1330, "#4a3020")
    piece(ctx, P_rect(-10, 560, 1100, 60), hexc("#5a3820"), lw=4, shadow=False)
    dama(ctx, 540, 1200, 1.0, pose)
    piece(ctx, P_rect(240, 1100, 600, 230), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(240, 1080, 600, 40), hexc("#5a3820"), lw=4)
    with rot(ctx, 860, 760, math.radians(-30 if (pose // 3) % 2 == 0 else -10)):
        piece(ctx, P_rrect(820, 700, 120, 60, 12), hexc("#7a4e2c"), lw=4)
        line(ctx, [(880, 760), (880, 880)], 12, hexc("#7a4e2c"))
    tc = since(ev, "culpable", lt)
    if tc >= 0:
        stamp(ctx, 540, 760, "CULPABLE", tc, 70, col=ROJO, ang=-8)
    tn = since(ev, "nombre", lt)
    if tn >= 0:
        piece(ctx, P_rrect(320, 1150, 440, 80, 12), (1, 1, 1), lw=4)
        txt(ctx, "ANNA SOROKIN", 540, 1205, 44, INK, anchor="center")


def sc_serie(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    piece(ctx, P_rrect(130, 600, 820, 520, 20), hexc("#23242c"), lw=6)
    piece(ctx, P_rect(160, 630, 760, 460), hexc("#6b3a4a"), lw=3, shadow=False)
    ctx.save()
    P_rect(160, 630, 760, 460)(ctx)
    ctx.clip()
    dama(ctx, 540, 1100, 0.9, pose)
    ctx.restore()
    piece(ctx, P_rect(500, 1120, 80, 80), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rect(400, 1200, 280, 30), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_poly([(820, 660), (890, 700), (820, 740)]), hexc("#e63946"), lw=3, shadow=False)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 900, 1250 - bob, 140, hexc("#ffe14d"), INK, 7)


SCENES = dict(hotel=sc_hotel, heredera=sc_heredera, factura=sc_factura, jet=sc_jet, prestamo=sc_prestamo,
              juicio=sc_juicio, serie=sc_serie)
SCENES = con_mapa(SCENES, BLOQUES, pais="USA", ciudad="NUEVA YORK", lon=-74.0, lat=40.71)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_heredera(ctx, 0, 2.0, {"fortuna_lt": 0.0, "propinas_lt": 1.4})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(97))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "SE HIZO PASAR", 540, 220, 108, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "POR MILLONARIA", 540, 380, 104, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y NUEVA YORK SE LO CREYÓ!", 540, 1690, 76, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
