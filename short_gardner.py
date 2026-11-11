#!/usr/bin/env python3
"""
Short 15 · «Los falsos policías del museo» — Isabella Stewart Gardner Museum (Boston, 1990)
Voz gratuita (python voz_gratis.py short_gardner.py).

Uso:
    python short_gardner.py            # vídeo final (usa cache_audio/museo-boston/)
    python short_gardner.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import bubble, since, stamp, txt
from generar_marca import magnifier
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, fondo, gorra_poli, marco, noche, silueta

SLUG = "museo-boston"
PRONUNCIA = {"Boston": "Bóston", "Vermeer": "Vermér", "Rembrandt": "Rémbrand", "FBI": "efe be i"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que el mayor robo de arte de la historia empezó con un vigilante "
             "abriendo la puerta… a dos policías falsos?"),
        escenas=[(None, "puerta")],
        pantalla=[("mayor robo", "EL MAYOR ROBO DE ARTE"), ("dos policías", "¿POLICÍAS FALSOS?")],
        eventos={"abriendo": "abriendo la", "falsos": "policías falsos"},
    ),
    dict(
        id="caso",
        voz=("Boston, 1990, noche de San Patricio. Dos hombres vestidos de agentes llaman al museo y dicen que "
             "vienen por un aviso. El vigilante les abre. Dentro, inmovilizan a los guardias y empiezan a "
             "descolgar cuadros."),
        escenas=[(None, "llamada"), ("Dentro", "sala")],
        pantalla=[(None, "BOSTON, 1990"), ("dicen que", "«VENIMOS POR UN AVISO»"), ("Dentro", "¡DESCUELGAN CUADROS!")],
        eventos={"llaman": "llaman al", "abre": "les abre", "descolgar": "a descolgar"},
    ),
    dict(
        id="botin",
        voz="Se llevan 13 obras, entre ellas un Vermeer y varios Rembrandt. Hoy valen más de 500 millones de dólares.",
        escenas=[(None, "botin")],
        pantalla=[(None, "13 OBRAS"), ("Hoy valen", "+500 MILLONES $")],
        eventos={"vermeer": "un Vermeer", "valen": "Hoy valen"},
    ),
    dict(
        id="marcos",
        voz=("Nunca se ha recuperado ninguna. El museo ofrece 10 millones de dólares de recompensa… y en las "
             "paredes siguen colgados los marcos vacíos."),
        escenas=[(None, "marcos")],
        pantalla=[(None, "NINGUNA RECUPERADA"), ("El museo", "10 MILLONES DE RECOMPENSA"), ("y en", "MARCOS VACÍOS")],
        eventos={"recompensa": "de recompensa", "marcos": "marcos vacíos"},
    ),
    dict(
        id="cierre",
        voz="El FBI cree que los ladrones ya han muerto, pero los cuadros siguen sin aparecer. ¿Dónde crees que están?",
        escenas=[(None, "misterio")],
        pantalla=[(None, "¿LADRONES MUERTOS?"), ("Dónde", "¿DÓNDE ESTÁN?")],
        eventos={"pero": "pero los", "pregunta": "Dónde crees"},
    ),
]


# ─────────────────────────── «cuadros» esquemáticos ───────────────────────────
def tormenta(ctx, x, y, w, h):
    set_col(ctx, hexc("#2b3a3a"))
    ctx.paint()
    piece(ctx, P_rect(x, y + h * 0.6, w, h), hexc("#1f4a4a"), lw=0, shadow=False, outline=False)
    piece(ctx, P_poly([(x + w * 0.2, y + h * 0.7), (x + w * 0.8, y + h * 0.55), (x + w * 0.7, y + h * 0.75),
                       (x + w * 0.3, y + h * 0.85)]), hexc("#6b4428"), lw=2, shadow=False)
    line(ctx, [(x + w * 0.5, y + h * 0.65), (x + w * 0.45, y + h * 0.15)], max(3, w * 0.03), hexc("#3d2614"))
    piece(ctx, P_poly([(x + w * 0.46, y + h * 0.18), (x + w * 0.8, y + h * 0.3), (x + w * 0.5, y + h * 0.5)]),
          hexc("#d9c7a3"), lw=2, shadow=False)
    piece(ctx, P_ell(x + w * 0.85, y + h * 0.15, w * 0.2, h * 0.12), hexc("#e8d9a0"), lw=0, shadow=False, outline=False)


def concierto(ctx, x, y, w, h):
    set_col(ctx, hexc("#4a4033"))
    ctx.paint()
    piece(ctx, P_rect(x, y + h * 0.7, w, h), hexc("#2b2418"), lw=0, shadow=False, outline=False)
    for i in range(6):
        for j in range(2):
            piece(ctx, P_rect(x + i * w / 6, y + h * 0.7 + j * h * 0.15, w / 12, h * 0.15),
                  hexc("#e8e2d0") if (i + j) % 2 else hexc("#1a1712"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(x + w * 0.1, y + h * 0.45, w * 0.45, h * 0.12), hexc("#6b4a33"), lw=2, shadow=False)
    for k, px in enumerate((0.3, 0.7)):
        piece(ctx, P_ell(x + w * px, y + h * 0.35, w * 0.07, h * 0.06), hexc("#d6a86a"), lw=2, shadow=False)
        piece(ctx, P_poly([(x + w * (px - 0.1), y + h * 0.7), (x + w * (px + 0.1), y + h * 0.7),
                           (x + w * (px + 0.05), y + h * 0.4), (x + w * (px - 0.05), y + h * 0.4)]),
              hexc("#e8d9a0") if k == 0 else hexc("#8a3a3a"), lw=2, shadow=False)


def retrato_oscuro(ctx, x, y, w, h):
    set_col(ctx, hexc("#1f1a14"))
    ctx.paint()
    piece(ctx, P_ell(x + w / 2, y + h * 0.4, w * 0.22, h * 0.18), hexc("#c99a6a"), lw=2, shadow=False)
    piece(ctx, P_poly([(x + w * 0.15, y + h), (x + w * 0.85, y + h), (x + w * 0.7, y + h * 0.6), (x + w * 0.3, y + h * 0.6)]),
          hexc("#3a2a1a"), lw=2, shadow=False)
    piece(ctx, P_ell(x + w / 2, y + h * 0.24, w * 0.26, h * 0.08), hexc("#14100c"), lw=0, shadow=False, outline=False)


def caballo(ctx, x, y, w, h):
    set_col(ctx, hexc("#e8dcc0"))
    ctx.paint()
    piece(ctx, P_ell(x + w * 0.5, y + h * 0.55, w * 0.3, h * 0.15), hexc("#7a4e2c"), lw=2, shadow=False)
    for dx in (0.3, 0.4, 0.6, 0.7):
        line(ctx, [(x + w * dx, y + h * 0.62), (x + w * dx, y + h * 0.85)], max(3, w * 0.03), hexc("#7a4e2c"))
    piece(ctx, P_ell(x + w * 0.82, y + h * 0.4, w * 0.1, h * 0.07), hexc("#7a4e2c"), lw=2, shadow=False)


CUADROS = [tormenta, concierto, retrato_oscuro, caballo]


def pared_museo(ctx, col="#3d5a4a"):
    fondo(ctx, col, 1330, "#5a4030")
    piece(ctx, P_rect(-10, 520, 1100, 30), hexc("#c9a46a"), lw=3, shadow=False)
    for i in range(8):
        piece(ctx, P_rect(-10 + i * 140, 1330, 135, 630), hexc("#6b4a33") if i % 2 else hexc("#5a3a2a"), lw=2,
              shadow=False)


def puerta_museo(ctx, x, y, w, h, abierta=0.0):
    piece(ctx, P_rect(x - 40, y - 60, w + 80, h + 60), hexc("#cfc3a8"), lw=5)
    piece(ctx, P_rect(x, y, w, h), hexc("#1a120c"), lw=4, shadow=False)
    ancho = w / 2 * (1 - 0.8 * abierta)
    for side in (0, 1):
        x0 = x if side == 0 else x + w - ancho
        piece(ctx, P_rect(x0, y, ancho, h), hexc("#5a3820"), lw=4)
        piece(ctx, P_rect(x0 + ancho * 0.15, y + h * 0.1, ancho * 0.7, h * 0.35), hexc("#6b4428"), lw=3, shadow=False)
    piece(ctx, P_ell(x + w / 2 - 20, y + h * 0.55, 9), ORO, lw=2, shadow=False)


def falso_poli(ctx, x, feet, s, pose, k=0):
    silueta(ctx, x, feet, s, pose, k)
    gorra_poli(ctx, x, feet, s)
    piece(ctx, P_poly([(x + 20 * s, feet - 190 * s), (x + 40 * s, feet - 170 * s), (x + 20 * s, feet - 150 * s),
                       (x, feet - 170 * s)]), ORO, lw=2, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_puerta(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1320)
    ta = since(ev, "abriendo", lt)
    puerta_museo(ctx, 340, 760, 400, 560, abierta=clamp(ta / 0.8) if ta >= 0 else 0.0)
    if ta >= 0:
        ctx.move_to(440, 1320)
        ctx.line_to(640, 1320)
        ctx.line_to(800, 1600)
        ctx.line_to(280, 1600)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.9, 0.5, 0.25 * clamp(ta / 0.8))
        ctx.fill()
    falso_poli(ctx, 190, 1330, 0.95, pose)
    falso_poli(ctx, 890, 1330, 0.95, pose, 3)
    tf = since(ev, "falsos", lt)
    if tf >= 0:
        stamp(ctx, 190, 1060, "FALSO", tf, 46, col=ROJO, ang=-10)
        stamp(ctx, 890, 1060, "FALSO", tf - 0.2, 46, col=ROJO, ang=8)


def sc_llamada(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1320)
    tab = since(ev, "abre", lt)
    puerta_museo(ctx, 340, 760, 400, 560, abierta=clamp(tab / 0.8) if tab >= 0 else 0.0)
    falso_poli(ctx, 190, 1330, 0.95, pose)
    falso_poli(ctx, 890, 1330, 0.95, pose, 3)
    tl = since(ev, "llaman", lt)
    if tl >= 0 and tab < 0:
        bubble(ctx, 360, 620, 420, 130, (220, 1010), ["¡POLICÍA!", "¡ABRA!"], 46)
        if (pose // 2) % 2 == 0:
            txt(ctx, "TOC TOC", 540, 1180, 44, hexc("#ffe14d"), anchor="center")
    if tab >= 0:
        stamp(ctx, 540, 1180, "LES ABRE", tab, 60, col=hexc("#2fb35a"), ang=-6)


def sc_sala(ctx, pose, lt, ev):
    pared_museo(ctx)
    td = since(ev, "descolgar", lt)
    n = int(clamp(td / 1.8) * 4) if td >= 0 else 0
    pos = [(90, 620, 260, 330), (410, 600, 260, 360), (730, 620, 260, 330)]
    for i, (x, y, w, h) in enumerate(pos):
        if i < n:
            marco(ctx, x, y, w, h, vacio=True, borde=26)
        else:
            marco(ctx, x, y, w, h, CUADROS[i], borde=26)
    falso_poli(ctx, 300, 1320, 0.95, pose)
    falso_poli(ctx, 780, 1320, 0.95, pose, 3)
    if td >= 0:
        with rot(ctx, 800, 1150, math.radians(-10)):
            marco(ctx, 700, 1040, 180, 220, CUADROS[3], borde=18)


def sc_botin(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    n = min(13, int(clamp(lt / 1.6) * 13) + 1)
    for i in range(n):
        r, c = divmod(i, 4)
        x, y = 110 + c * 225, 580 + r * 175
        marco(ctx, x, y, 190, 150, CUADROS[i % 4], borde=16)
    tv = since(ev, "vermeer", lt)
    if tv >= 0:
        stamp(ctx, 540, 1215, "VERMEER · REMBRANDT", tv, 44, col=hexc("#7b4dff"), ang=-4)
    tval = since(ev, "valen", lt)
    if tval >= 0:
        piece(ctx, P_rrect(220, 1290, 640, 110, 16), hexc("#1d2433"), lw=4)
        v = int(500 * ease_io(clamp(tval / 1.0)))
        txt(ctx, f"{v} MILLONES $", 540, 1365, 60, hexc("#9fd6a0"), anchor="center")


def sc_marcos(ctx, pose, lt, ev):
    pared_museo(ctx, "#3a4a5a")
    for i, (x, y, w, h) in enumerate([(100, 600, 380, 300), (600, 590, 380, 320), (100, 960, 380, 300)]):
        marco(ctx, x, y, w, h, vacio=True, borde=30)
    tr = since(ev, "recompensa", lt)
    if tr >= 0:
        k = ease_out_back(clamp(tr / 0.3)) if tr < 0.3 else 1.0
        with rot(ctx, 790, 1110, math.radians(5)):
            ctx.save()
            ctx.translate(790, 1110)
            ctx.scale(max(0.05, k), max(0.05, k))
            ctx.translate(-790, -1110)
            piece(ctx, P_rect(580, 970, 420, 280), hexc("#f3e6c9"), lw=6)
            txt(ctx, "RECOMPENSA", 790, 1050, 48, ROJO, anchor="center")
            txt(ctx, "10.000.000 $", 790, 1150, 60, INK, anchor="center")
            ctx.restore()
    tm = since(ev, "marcos", lt)
    if tm >= 0:
        stamp(ctx, 290, 1310, "SIGUEN VACÍOS", tm, 50, col=ROJO, ang=-6)


def sc_misterio(ctx, pose, lt, ev):
    fondo(ctx, "#1d1a2e", None)
    for i in range(4):
        x = 160 + i * 250
        y = 760 + 120 * math.sin(lt * 1.5 + i) * 0.5 + (i % 2) * 160
        with rot(ctx, x, y, math.radians(-12 + i * 8)):
            marco(ctx, x - 90, y - 80, 180, 160, CUADROS[i], borde=16)
    bob = (pose // 4) % 2 * 10
    draw_text(ctx, "?", 540, 1180 - bob, 240, hexc("#ffe14d"), INK, 9)
    tp = since(ev, "pero", lt)
    if tp >= 0:
        stamp(ctx, 540, 600, "SIN APARECER", tp, 52, col=ROJO, ang=-5)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        k = ease_io(clamp(tq / 0.6))
        magnifier(ctx, lerp(1000, 760, k), lerp(1400, 1150, k), 110, math.radians(-30))


SCENES = dict(puerta=sc_puerta, llamada=sc_llamada, sala=sc_sala, botin=sc_botin, marcos=sc_marcos,
              misterio=sc_misterio)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_puerta(ctx, 0, 2.0, {"abriendo_lt": 0.2, "falsos_lt": 0.8})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(53))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "LES ABRIÓ LA PUERTA", 540, 220, 94, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "A 2 POLICÍAS FALSOS", 540, 380, 94, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡500 MILLONES!", 540, 1690, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
