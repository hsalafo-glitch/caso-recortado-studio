#!/usr/bin/env python3
"""
Short 18 · «El electricista que robó el Códice Calixtino» — Santiago de Compostela, 2011
Voz gratuita (python voz_gratis.py short_codice.py).
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
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, VERDE_BILLETE, billetes_fajo, fondo, silueta

SLUG = "codice-calixtino"
PRONUNCIA = {"XII": "doce"}

BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina que roban un libro de más de 800 años… y que el ladrón es el electricista de la catedral.",
        escenas=[(None, "libro"), ("y que", "electricista")],
        pantalla=[("un libro", "UN LIBRO DE +800 AÑOS"), ("y que", "¿EL ELECTRICISTA?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Santiago de Compostela, julio de 2011. El Códice Calixtino, una joya del siglo XII, desaparece de una "
             "cámara de seguridad de la catedral."),
        escenas=[(None, "catedral"), ("desaparece", "camara")],
        pantalla=[(None, "SANTIAGO, 2011"), ("una joya", "UNA JOYA DEL SIGLO XII"), ("desaparece", "¡DESAPARECE!")],
        eventos={},
    ),
    dict(
        id="busqueda",
        voz=("Durante un año, la policía lo busca por todas partes. Hasta que se fijan en un antiguo electricista "
             "que había trabajado décadas en la catedral."),
        escenas=[(None, "busqueda"), ("Hasta que", "sospechoso")],
        pantalla=[(None, "UN AÑO BUSCANDO"), ("Hasta que", "EL SOSPECHOSO")],
        eventos={"decadas": "trabajado décadas"},
    ),
    dict(
        id="garaje",
        voz="En julio de 2012 lo encuentran en su garaje, metido en bolsas, junto a más de un millón de euros en efectivo.",
        escenas=[(None, "garaje")],
        pantalla=[(None, "JULIO DE 2012"), ("en su garaje", "¡EN SU GARAJE!"), ("junto a", "+1 MILLÓN DE €")],
        eventos={"garaje": "en su garaje", "euros": "junto a"},
    ),
    dict(
        id="cierre",
        voz="Hoy ha vuelto a la catedral. Un tesoro de más de 800 años… escondido en un garaje. ¿Te lo imaginabas?",
        escenas=[(None, "vuelta"), ("Un tesoro", "trastos")],
        pantalla=[(None, "DE VUELTA A LA CATEDRAL"), ("Un tesoro", "ESCONDIDO EN UN GARAJE"), ("Te lo", "¿TE LO IMAGINABAS?")],
        eventos={"pregunta": "Te lo"},
    ),
]


def codice(ctx, x, y, s=1.0, ang=0.0, brillo=False):
    with rot(ctx, x, y, ang):
        if brillo:
            ctx.save()
            ctx.set_source_rgba(1, 0.9, 0.4, 0.25)
            ctx.arc(x, y, 260 * s, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        piece(ctx, P_rrect(x - 160 * s, y - 210 * s, 320 * s, 420 * s, 16 * s), hexc("#7a1f1f"), lw=5)
        piece(ctx, P_rect(x - 150 * s, y + 190 * s, 300 * s, 16 * s), hexc("#f3e6c9"), lw=2, shadow=False)
        piece(ctx, P_rrect(x - 125 * s, y - 175 * s, 250 * s, 350 * s, 10 * s), (0, 0, 0, 0), lw=0, shadow=False)
        ctx.rectangle(x - 125 * s, y - 175 * s, 250 * s, 350 * s)
        set_col(ctx, ORO)
        ctx.set_line_width(7 * s)
        ctx.stroke()
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            piece(ctx, P_ell(x + dx * 125 * s, y + dy * 175 * s, 22 * s), ORO, lw=3, shadow=False)
        # cruz de Santiago esquemática
        piece(ctx, P_rect(x - 14 * s, y - 100 * s, 28 * s, 200 * s), ORO, lw=3, shadow=False)
        piece(ctx, P_rect(x - 70 * s, y - 40 * s, 140 * s, 28 * s), ORO, lw=3, shadow=False)
        piece(ctx, P_ell(x, y - 26 * s, 26 * s), hexc("#c8202f"), lw=3, shadow=False)


def catedral(ctx, x, y, s=1.0):
    col = hexc("#c9b48a")
    for dx in (-260, 260):
        piece(ctx, P_rect(x + dx * s - 90 * s, y - 760 * s, 180 * s, 760 * s), col, lw=5)
        piece(ctx, P_poly([(x + dx * s - 100 * s, y - 760 * s), (x + dx * s + 100 * s, y - 760 * s),
                           (x + dx * s, y - 920 * s)]), hexc("#a8946a"), lw=5)
        for k in range(3):
            piece(ctx, P_rrect(x + dx * s - 30 * s, y - 680 * s + k * 170 * s, 60 * s, 100 * s, 28 * s),
                  hexc("#3a2f4a"), lw=3, shadow=False)
    piece(ctx, P_rect(x - 170 * s, y - 560 * s, 340 * s, 560 * s), col, lw=5)
    piece(ctx, P_poly([(x - 180 * s, y - 560 * s), (x + 180 * s, y - 560 * s), (x, y - 700 * s)]), hexc("#a8946a"), lw=5)
    piece(ctx, P_rrect(x - 90 * s, y - 300 * s, 180 * s, 300 * s, 80 * s), hexc("#3a2f4a"), lw=4)
    piece(ctx, P_ell(x, y - 450 * s, 60 * s), hexc("#4a6a9a"), lw=4)


def electricista(ctx, x, feet, s, pose, k=0):
    silueta(ctx, x, feet, s, pose, k)
    # cinturón de herramientas y rollo de cable
    piece(ctx, P_rect(x - 70 * s, feet - 110 * s, 140 * s, 26 * s), hexc("#a77c44"), lw=3, shadow=False)
    piece(ctx, P_ell(x + 95 * s, feet - 120 * s, 40 * s), hexc("#e8c21f"), lw=4, shadow=False)
    piece(ctx, P_ell(x + 95 * s, feet - 120 * s, 16 * s), hexc("#1d1a2e"), lw=2, shadow=False)


def bombilla(ctx, x, y, s, on=True):
    piece(ctx, P_ell(x, y, 50 * s, 58 * s), hexc("#ffe58a") if on else hexc("#d9d2c0"), lw=4)
    piece(ctx, P_rect(x - 24 * s, y + 50 * s, 48 * s, 36 * s), hexc("#9aa0ab"), lw=3, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_libro(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", 1330, "#1a1428")
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    codice(ctx, 540, 930, 1.05 * max(0.05, k), math.radians(-3), brillo=True)


def sc_electricista(ctx, pose, lt, ev):
    fondo(ctx, "#3a3150", 1330, "#241e33")
    electricista(ctx, 420, 1330, 1.35, pose)
    codice(ctx, 760, 1080, 0.55, math.radians(12))
    bombilla(ctx, 420, 640, 1.0, on=(pose // 3) % 2 == 0)
    line(ctx, [(420, 540), (420, 582)], 5, INK)


def sc_catedral(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fc8e0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 660), hexc("#b5a888"), lw=4, shadow=False)
    for i in range(10):
        line(ctx, [(i * 120, 1300), (i * 120 - 60, 1960)], 3, hexc("#9a8e70"))
    catedral(ctx, 540, 1300, 0.85)


def sc_camara(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1330, "#2f333d")
    # cámara de seguridad: puerta acorazada abierta y atril vacío
    piece(ctx, P_ell(300, 900, 230), hexc("#9aa0ab"), lw=6)
    piece(ctx, P_ell(300, 900, 180), hexc("#1a1d24"), lw=4, shadow=False)
    with rot(ctx, 120, 900, math.radians(-20)):
        piece(ctx, P_ell(80, 900, 70, 220), hexc("#b5bccb"), lw=5)
    piece(ctx, P_poly([(620, 1000), (900, 1000), (860, 1080), (660, 1080)]), hexc("#6b4428"), lw=5)
    piece(ctx, P_rect(735, 1080, 50, 230), hexc("#5a3820"), lw=4)
    piece(ctx, P_rect(680, 1300, 160, 30), hexc("#5a3820"), lw=4)
    k = clamp(lt / 0.6)
    if k < 1:
        ctx.save()
        ctx.push_group()
        codice(ctx, 760, 900, 0.4)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - k)
        ctx.restore()
    else:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 760, 860 - bob, 180, hexc("#ffe14d"), INK, 8)


def sc_busqueda(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1340, "#5a3820")
    piece(ctx, P_rect(80, 560, 920, 700), hexc("#c79a5b"), lw=6)
    for i in range(6):
        x, y = 200 + (i % 3) * 300, 680 + (i // 3) * 300
        with rot(ctx, x, y, math.radians((hnoise("bp", i) - 0.5) * 14)):
            piece(ctx, P_rect(x - 100, y - 80, 200, 160), (1, 1, 1), lw=4)
            draw_text(ctx, "?", x, y, 80, hexc("#9aa0ab"), INK, 0)
    k = (lt * 0.6) % 1
    magnifier(ctx, lerp(200, 880, k), 860 + 120 * math.sin(k * 6.28), 120, math.radians(-30))
    meses = min(12, 1 + int(lt * 2))
    piece(ctx, P_rrect(330, 1170, 420, 90, 14), hexc("#1d2433"), lw=4)
    txt(ctx, f"MES {meses}", 540, 1235, 54, hexc("#ffe14d"), anchor="center")


def sc_sospechoso(ctx, pose, lt, ev):
    fondo(ctx, "#3a3150", 1330, "#241e33")
    catedral(ctx, 760, 1330, 0.55)
    electricista(ctx, 330, 1330, 1.25, pose)
    td = since(ev, "decadas", lt)
    if td >= 0:
        stamp(ctx, 330, 860, "DÉCADAS DENTRO", td, 48, col=ROJO, ang=-8)


def garaje_fondo(ctx):
    fondo(ctx, "#8a8f9a", 1330, "#5b6475")
    piece(ctx, P_rect(-10, 540, 1100, 60), hexc("#6b707c"), lw=4, shadow=False)
    for i in range(4):
        piece(ctx, P_rect(60 + i * 250, 620, 200, 40), hexc("#7a4e2c"), lw=3)
        for j in range(3):
            piece(ctx, P_rect(70 + i * 250 + j * 60, 560 + 0, 50, 60), hexc(["#c94a4a", "#4a7ac9", "#d9c7a3"][j]), lw=2,
                  shadow=False)
    # trastos
    piece(ctx, P_rect(60, 1100, 260, 230), hexc("#c9a46a"), lw=4)
    piece(ctx, P_rect(80, 980, 220, 120), hexc("#b5945a"), lw=4)
    piece(ctx, P_ell(900, 1250, 80), INK, lw=4)
    piece(ctx, P_ell(900, 1250, 34), hexc("#9aa0ab"), lw=3, shadow=False)
    piece(ctx, P_rect(760, 1100, 60, 230), hexc("#e07a2d"), lw=4)


def sc_garaje(ctx, pose, lt, ev):
    garaje_fondo(ctx)
    tg = since(ev, "garaje", lt)
    # bolsas
    piece(ctx, P_poly([(380, 1330), (620, 1330), (650, 1170), (580, 1080), (420, 1080), (350, 1170)]), hexc("#2b2d33"), lw=5)
    if tg >= 0:
        k = ease_out_back(clamp(tg / 0.4)) if tg < 0.4 else 1.0
        codice(ctx, 500, 980, 0.5 * max(0.05, k), math.radians(-10), brillo=True)
    te = since(ev, "euros", lt)
    if te >= 0:
        n = int(clamp(te / 1.0) * 6)
        for i in range(n):
            billetes_fajo(ctx, 640 + (i % 2) * 120, 1240 - (i // 2) * 70, 0.9)
        stamp(ctx, 760, 900, "+1.000.000 €", te, 50, col=hexc("#2f6b45"), ang=6)


def sc_vuelta(ctx, pose, lt, ev):
    fondo(ctx, "#3a2f4a", 1330, "#241e33")
    ctx.move_to(540, 480)
    ctx.line_to(300, 1300)
    ctx.line_to(780, 1300)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.6, 0.2)
    ctx.fill()
    piece(ctx, P_rect(360, 1180, 360, 150), hexc("#6b4428"), lw=5)
    codice(ctx, 540, 950, 0.65, 0, brillo=True)


def sc_trastos(ctx, pose, lt, ev):
    garaje_fondo(ctx)
    codice(ctx, 540, 1080, 0.55, math.radians(-8), brillo=True)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        k = ease_io(clamp(tq / 0.6))
        magnifier(ctx, lerp(1000, 700, k), lerp(1400, 1150, k), 110, math.radians(-30))


SCENES = dict(libro=sc_libro, electricista=sc_electricista, catedral=sc_catedral, camara=sc_camara,
              busqueda=sc_busqueda, sospechoso=sc_sospechoso, garaje=sc_garaje, vuelta=sc_vuelta, trastos=sc_trastos)
SCENES = con_mapa(SCENES, BLOQUES, pais="ESP", ciudad="SANTIAGO", lon=-8.54, lat=42.88)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_garaje(ctx, 0, 2.0, {"garaje_lt": 0.2, "euros_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(67))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UN LIBRO DE 800 AÑOS", 540, 220, 92, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "EN UN GARAJE", 540, 380, 104, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡LO ROBÓ EL ELECTRICISTA!", 540, 1690, 80, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
