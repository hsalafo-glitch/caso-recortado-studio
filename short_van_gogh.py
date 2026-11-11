#!/usr/bin/env python3
"""
Short 22 · «Dos Van Gogh robados… que aparecieron en casa de la mafia» — Ámsterdam 2002 / Nápoles 2016
Voz gratuita (python voz_gratis.py short_van_gogh.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, fondo, marco, noche, silueta
from short_gardner import pared_museo
from short_moneda import escalera

SLUG = "van-gogh-camorra"
PRONUNCIA = {"Van Gogh": "Van Gog", "Camorra": "Camorra", "Ámsterdam": "Ámsterdam"}

BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina robar dos cuadros de Van Gogh… y que aparezcan catorce años después en una casa de la mafia.",
        escenas=[(None, "cuadros"), ("y que", "mafia")],
        pantalla=[("dos cuadros", "2 VAN GOGH ROBADOS"), ("catorce años", "14 AÑOS DESPUÉS…"), ("de la", "¿EN CASA DE LA MAFIA?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Ámsterdam, diciembre de 2002. De noche, dos ladrones apoyan una escalera en el Museo Van Gogh, suben "
             "al tejado, rompen una ventana y se llevan dos cuadros."),
        escenas=[(None, "museo")],
        pantalla=[(None, "ÁMSTERDAM, 2002"), ("apoyan una", "UNA ESCALERA"), ("rompen una", "¡CRAC!")],
        eventos={"escalera": "apoyan una", "tejado": "suben al", "ventana": "rompen una", "cuadros": "se llevan"},
    ),
    dict(
        id="adn",
        voz=("Huyen deslizándose por una cuerda. Gracias a restos de ADN, la policía detiene a los dos ladrones… "
             "pero los cuadros no aparecen."),
        escenas=[(None, "cuerda"), ("Gracias a", "adn")],
        pantalla=[(None, "POR UNA CUERDA"), ("Gracias a", "ADN"), ("pero los", "¿Y LOS CUADROS?")],
        eventos={"detiene": "la policía", "cuadros": "pero los"},
    ),
    dict(
        id="napoles",
        voz=("En 2016, en una operación contra el narcotráfico en Italia, la policía entra en una casa cerca de "
             "Nápoles. Dentro de una caja fuerte, envueltos en tela, están los dos Van Gogh."),
        escenas=[(None, "redada"), ("Dentro de", "caja")],
        pantalla=[(None, "ITALIA, 2016"), ("la policía", "CERCA DE NÁPOLES"), ("Dentro de", "¡EN UNA CAJA FUERTE!")],
        eventos={"entra": "entra en", "envueltos": "envueltos en"},
    ),
    dict(
        id="cierre",
        voz="Estaban en manos de la Camorra. Hoy han vuelto al museo. ¿Cómo crees que llegaron hasta allí?",
        escenas=[(None, "vuelta")],
        pantalla=[(None, "EN MANOS DE LA CAMORRA"), ("Hoy han", "DE VUELTA AL MUSEO"), ("Cómo", "¿CÓMO LLEGARON ALLÍ?")],
        eventos={"vuelta": "Hoy han", "pregunta": "Cómo crees"},
    ),
]


def marina(ctx, x, y, w, h):
    """Marina esquemática con cielo tormentoso y barca (estilo pincelada)."""
    set_col(ctx, hexc("#8a9aa0"))
    ctx.paint()
    for i in range(6):
        line(ctx, [(x, y + h * (0.1 + i * 0.07)), (x + w, y + h * (0.12 + i * 0.07))], max(3, h * 0.03),
             hexc("#a8b4b8") if i % 2 else hexc("#6b7a80"))
    piece(ctx, P_rect(x, y + h * 0.55, w, h), hexc("#4a6a5a"), lw=0, shadow=False, outline=False)
    for i in range(5):
        line(ctx, [(x, y + h * (0.6 + i * 0.07)), (x + w, y + h * (0.58 + i * 0.07))], max(3, h * 0.025), hexc("#d9d2c0"))
    piece(ctx, P_poly([(x + w * 0.35, y + h * 0.55), (x + w * 0.65, y + h * 0.55), (x + w * 0.6, y + h * 0.62),
                       (x + w * 0.4, y + h * 0.62)]), hexc("#5a3820"), lw=2, shadow=False)
    line(ctx, [(x + w * 0.5, y + h * 0.55), (x + w * 0.5, y + h * 0.25)], max(2, w * 0.02), hexc("#3d2614"))


def iglesia(ctx, x, y, w, h):
    set_col(ctx, hexc("#c9b48a"))
    ctx.paint()
    piece(ctx, P_rect(x, y + h * 0.7, w, h), hexc("#8a7a4a"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(x + w * 0.35, y + h * 0.3, w * 0.3, h * 0.42), hexc("#7a6a5a"), lw=2, shadow=False)
    piece(ctx, P_poly([(x + w * 0.32, y + h * 0.3), (x + w * 0.68, y + h * 0.3), (x + w * 0.5, y + h * 0.1)]),
          hexc("#5a4a3a"), lw=2, shadow=False)
    for i in range(5):
        piece(ctx, P_ell(x + w * (0.15 + i * 0.17), y + h * 0.82, w * 0.03, h * 0.06), hexc("#2b2418"), lw=0,
              shadow=False, outline=False)


def tela(ctx, x, y, w, h):
    piece(ctx, P_rrect(x, y, w, h, 18), hexc("#e8dcc0"), lw=4)
    for i in range(4):
        line(ctx, [(x + 20, y + 20 + i * h / 4), (x + w - 20, y + 30 + i * h / 4)], 3, hexc("#b5a888"))


# ─────────────────────────────── escenas ───────────────────────────────
def sc_cuadros(ctx, pose, lt, ev):
    pared_museo(ctx, "#3d5a6a")
    marco(ctx, 90, 640, 420, 330, marina, borde=30)
    marco(ctx, 570, 600, 400, 420, iglesia, borde=30)
    if lt > 1.2:
        stamp(ctx, 540, 1180, "ROBADOS", lt - 1.2, 64, col=ROJO, ang=-6)


def sc_mafia(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", 1330, "#1a1428")
    # casa en la costa, de noche
    piece(ctx, P_rect(250, 760, 580, 570), hexc("#e8d2a0"), lw=5)
    piece(ctx, P_poly([(220, 760), (860, 760), (540, 560)]), hexc("#c94a4a"), lw=5)
    for c in range(3):
        piece(ctx, P_rect(300 + c * 180, 860, 110, 140), hexc("#ffe58a") if c == 1 else hexc("#3a3150"), lw=3, shadow=False)
    piece(ctx, P_rect(480, 1130, 120, 200), hexc("#5a3820"), lw=4)
    with rot(ctx, 900, 1100, math.radians(8)):
        marco(ctx, 820, 1000, 160, 130, marina, borde=14)
    bob = (pose // 4) % 2 * 8
    draw_text(ctx, "?", 540, 660 - bob, 120, hexc("#ffe14d"), INK, 6)


def sc_museo(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    piece(ctx, P_rect(300, 700, 700, 630), hexc("#d9d2c0"), lw=5)
    piece(ctx, P_rect(280, 680, 740, 40), hexc("#9aa0ab"), lw=4)
    tv = since(ev, "ventana", lt)
    for c in range(3):
        rota = tv >= 0 and c == 0
        piece(ctx, P_rect(360 + c * 210, 760, 150, 200), hexc("#ffe58a") if rota else hexc("#2b2d40"), lw=4, shadow=False)
        if rota:
            for a in range(5):
                ang = math.radians(a * 72)
                line(ctx, [(435, 860), (435 + 70 * math.cos(ang), 860 + 90 * math.sin(ang))], 4, INK)
    te = since(ev, "escalera", lt)
    if te >= 0:
        k = clamp(te / 0.6)
        escalera(ctx, 180, 1330, lerp(180, 300, k), lerp(1330, 690, k))
    tt = since(ev, "tejado", lt)
    for i in range(2):
        if tt >= 0:
            k = clamp((tt - i * 0.4) / 1.0)
            silueta(ctx, lerp(200, 380 + i * 120, k), lerp(1330, 680, k), 0.55, pose, i)
        else:
            silueta(ctx, 100 + i * 100, 1330, 0.55, pose, i)
    tc = since(ev, "cuadros", lt)
    if tc >= 0:
        with rot(ctx, 560, 640, math.radians(-8)):
            marco(ctx, 500, 580, 120, 100, marina, borde=10)


def sc_cuerda(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    piece(ctx, P_rect(500, 560, 580, 770), hexc("#d9d2c0"), lw=5)
    line(ctx, [(560, 560), (560, 1330)], 6, hexc("#d9c08a"))
    y = lerp(620, 1100, ease_io(clamp(lt / 1.6)))
    silueta(ctx, 520, y + 200, 0.75, pose)
    with rot(ctx, 640, y + 80, math.radians(-10)):
        marco(ctx, 590, y + 20, 130, 110, iglesia, borde=12)


def sc_adn(ctx, pose, lt, ev):
    fondo(ctx, "#2f3c5a", 1330, "#1f2a40")
    from short_fantasma import helice
    piece(ctx, P_rrect(380, 560, 320, 560, 30), (1, 1, 1, 0.9), lw=5)
    helice(ctx, 540, 610, 1070, 80, pose * 0.5)
    td = since(ev, "detiene", lt)
    if td >= 0:
        for i in range(2):
            silueta(ctx, 200 + i * 680, 1330, 0.9, pose, i)
            from generar_short_estafas import stamp as st
            st(ctx, 200 + i * 680, 960, "DETENIDO", td - i * 0.2, 40, col=ROJO, ang=-8 + i * 12)
    tc = since(ev, "cuadros", lt)
    if tc >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 1230 - bob, 120, hexc("#ffe14d"), INK, 6)


def sc_redada(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    piece(ctx, P_rect(-10, 1180, 1100, 160), hexc("#2f5f88"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(280, 700, 520, 630), hexc("#e8d2a0"), lw=5)
    piece(ctx, P_poly([(250, 700), (830, 700), (540, 540)]), hexc("#c94a4a"), lw=5)
    piece(ctx, P_rect(480, 1130, 120, 200), hexc("#1a120c"), lw=4)
    te = since(ev, "entra", lt)
    if te >= 0:
        on = pose % 6 < 3
        for x in (120, 960):
            piece(ctx, P_ell(x, 1100, 40), ROJO if on else hexc("#1d4ed8"), lw=3)
            ctx.save()
            c = (1, 0.2, 0.2) if on else (0.3, 0.5, 1)
            ctx.set_source_rgba(c[0], c[1], c[2], 0.2)
            ctx.arc(x, 1100, 160, 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        stamp(ctx, 540, 900, "ANTINARCÓTICOS", te, 46, col=hexc("#1d4ed8"), ang=-6)


def sc_caja(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1330, "#2f333d")
    piece(ctx, P_rrect(200, 580, 680, 700, 20), hexc("#5b6475"), lw=6)
    piece(ctx, P_rect(240, 620, 600, 620), hexc("#1a1d24"), lw=4, shadow=False)
    k = ease_io(clamp(lt / 0.8))
    dw = 600 * (1 - k) + 140 * k
    piece(ctx, P_poly([(880 - 600 * (1 - k), 600), (880 - 600 * (1 - k) + dw, 600 - 60 * k),
                       (880 - 600 * (1 - k) + dw, 1260 + 60 * k), (880 - 600 * (1 - k), 1260)]), hexc("#7a7f8a"), lw=5)
    te = since(ev, "envueltos", lt)
    tela(ctx, 280, 700, 260, 220)
    tela(ctx, 560, 680, 240, 260)
    if te >= 0:
        kk = clamp(te / 0.8)
        if kk > 0.5:
            marco(ctx, 290, 960, 240, 190, marina, borde=18)
            marco(ctx, 570, 960, 220, 260, iglesia, borde=18)


def sc_vuelta(ctx, pose, lt, ev):
    tv = since(ev, "vuelta", lt)
    if tv < 0:
        fondo(ctx, "#2b2340", 1330, "#1a1428")
        piece(ctx, P_rrect(340, 760, 400, 160, 20), hexc("#1d1a2e"), lw=5)
        txt(ctx, "CAMORRA", 540, 860, 64, ROJO, anchor="center")
        for i, x in enumerate((260, 820)):
            silueta(ctx, x, 1330, 0.9, pose, i)
    else:
        pared_museo(ctx, "#3d5a6a")
        marco(ctx, 90, 640, 420, 330, marina, borde=30)
        marco(ctx, 570, 600, 400, 420, iglesia, borde=30)
        stamp(ctx, 540, 1180, "DE VUELTA", tv, 60, col=hexc("#2fb35a"), ang=-6)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 920, 1150 - bob, 140, hexc("#ffe14d"), INK, 7)


SCENES = dict(cuadros=sc_cuadros, mafia=sc_mafia, museo=sc_museo, cuerda=sc_cuerda, adn=sc_adn, redada=sc_redada,
              caja=sc_caja, vuelta=sc_vuelta)
SCENES = con_mapa(SCENES, BLOQUES, pais="NLD", ciudad="ÁMSTERDAM", lon=4.9, lat=52.37)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_caja(ctx, 0, 2.0, {"envueltos_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(83))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "2 VAN GOGH ROBADOS", 540, 220, 96, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "14 AÑOS DESPUÉS…", 540, 380, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡EN CASA DE LA MAFIA!", 540, 1690, 92, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
