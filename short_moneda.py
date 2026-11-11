#!/usr/bin/env python3
"""
Short 20 · «Robaron una moneda de oro de 100 kilos con una carretilla» — Museo Bode, Berlín, 2017
Voz gratuita (python voz_gratis.py short_moneda.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, tree)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, fondo, noche, silueta
from short_dioni import coche

SLUG = "moneda-oro"
PRONUNCIA = {"Bode": "Bóde"}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pensarías si te dijera que robaron una moneda de oro de 100 kilos… con una escalera y una carretilla?",
        escenas=[(None, "moneda")],
        pantalla=[("una moneda", "UNA MONEDA DE 100 KG"), ("con una", "¿CON UNA CARRETILLA?")],
        eventos={"carretilla": "con una"},
    ),
    dict(
        id="caso",
        voz=("Berlín, marzo de 2017. En el Museo Bode se expone una moneda gigante: tan grande como la rueda de un "
             "coche y de oro puro. Vale unos 4 millones de dólares."),
        escenas=[(None, "museo"), ("Vale unos", "valor")],
        pantalla=[(None, "BERLÍN, 2017"), ("tan grande", "COMO UNA RUEDA"), ("Vale unos", "≈ 4 MILLONES $")],
        eventos={"rueda": "tan grande"},
    ),
    dict(
        id="entrada",
        voz=("De madrugada, los ladrones suben a las vías del tren que pasan junto al museo, apoyan una escalera y "
             "entran por una ventana. Según la acusación, tenían un cómplice dentro: un vigilante del museo."),
        escenas=[(None, "vias"), ("Según la", "complice")],
        pantalla=[(None, "DE MADRUGADA"), ("apoyan una", "UNA ESCALERA"), ("Según la", "UN CÓMPLICE DENTRO")],
        eventos={"escalera": "apoyan una", "ventana": "entran por"},
    ),
    dict(
        id="huida",
        voz=("Se llevan la moneda en una carretilla, la cruzan por un parque y la cargan en un coche. Años después "
             "condenan a tres jóvenes… pero la moneda nunca aparece."),
        escenas=[(None, "parque"), ("Años después", "condena")],
        pantalla=[(None, "EN CARRETILLA"), ("Años después", "3 CONDENADOS"), ("pero la", "¿Y LA MONEDA?")],
        eventos={"coche": "en un coche", "nunca": "nunca aparece"},
    ),
    dict(
        id="cierre",
        voz="La policía cree que la fundieron y la vendieron en trozos. ¿Crees que algún día aparecerá?",
        escenas=[(None, "fundida")],
        pantalla=[(None, "¿FUNDIDA?"), ("Crees", "¿APARECERÁ?")],
        eventos={"trozos": "en trozos", "pregunta": "Crees que"},
    ),
]


def moneda(ctx, x, y, r, ang=0.0, canto=False):
    with rot(ctx, x, y, ang):
        if canto:
            piece(ctx, P_rrect(x - 26, y - r, 52, 2 * r, 20), hexc("#c99a1a"), lw=5)
            return
        piece(ctx, P_ell(x, y, r), ORO, lw=6)
        piece(ctx, P_ell(x, y, r * 0.88), hexc("#e8b830"), lw=3, shadow=False)
        # hoja de arce esquemática
        s = r / 200
        pts = [(0, -120), (25, -70), (70, -90), (55, -35), (110, -30), (80, 10), (100, 40), (30, 30), (15, 90),
               (0, 70), (-15, 90), (-30, 30), (-100, 40), (-80, 10), (-110, -30), (-55, -35), (-70, -90), (-25, -70)]
        piece(ctx, P_poly([(x + px * s, y + py * s) for px, py in pts]), hexc("#c99a1a"), lw=3, shadow=False)
        line(ctx, [(x, y + 70 * s), (x, y + 130 * s)], 8 * s, hexc("#c99a1a"))
        ctx.save()
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.arc(x - r * 0.4, y - r * 0.4, r * 0.18, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()


def carretilla(ctx, x, y, s, pose, carga=True):
    piece(ctx, P_ell(x + 110 * s, y - 30 * s, 34 * s), INK, lw=3, shadow=False)
    if carga:
        moneda(ctx, x, y - 160 * s, 110 * s, math.radians(pose * 3))
    piece(ctx, P_poly([(x - 110 * s, y - 120 * s), (x + 140 * s, y - 120 * s), (x + 100 * s, y - 40 * s),
                       (x - 70 * s, y - 40 * s)]), hexc("#2f9e4f"), lw=5)
    line(ctx, [(x - 100 * s, y - 100 * s), (x - 220 * s, y - 60 * s)], 10 * s, hexc("#7a4e2c"))
    line(ctx, [(x - 40 * s, y - 40 * s), (x - 60 * s, y)], 8 * s, hexc("#3d3f4a"))


def escalera(ctx, x0, y0, x1, y1, w=60):
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
    line(ctx, [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny)], 9, hexc("#c9ccd6"))
    line(ctx, [(x0 - nx, y0 - ny), (x1 - nx, y1 - ny)], 9, hexc("#c9ccd6"))
    for i in range(1, 9):
        t = i / 9
        px, py = lerp(x0, x1, t), lerp(y0, y1, t)
        line(ctx, [(px + nx, py + ny), (px - nx, py - ny)], 6, hexc("#c9ccd6"))


def fachada_museo(ctx, x, y, w, h):
    piece(ctx, P_rect(x, y, w, h), hexc("#b5a888"), lw=5)
    for r in range(3):
        for c in range(4):
            piece(ctx, P_rrect(x + 40 + c * (w - 80) / 4, y + 60 + r * (h - 120) / 3, (w - 80) / 4 - 40, (h - 120) / 3 - 50, 30),
                  hexc("#2b2d40"), lw=3, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_moneda(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    moneda(ctx, 540, 900, 300 * max(0.05, k), math.radians(-4 + (pose % 8 < 4) * 3))
    tc = since(ev, "carretilla", lt)
    if tc >= 0:
        stamp(ctx, 540, 1260, "100 KG", tc, 70, col=ROJO, ang=-8)


def sc_museo(ctx, pose, lt, ev):
    fondo(ctx, "#5a4a6a", 1330, "#3a2e44")
    piece(ctx, P_rect(240, 1180, 600, 150), hexc("#e3e6ec"), lw=5)
    piece(ctx, P_rect(260, 600, 560, 580), hexc("#bfe3f2"), lw=5)
    moneda(ctx, 540, 890, 230)
    piece(ctx, P_rect(260, 600, 560, 580), (1, 1, 1, 0.12), lw=0, shadow=False, outline=False)
    tr = since(ev, "rueda", lt)
    if tr >= 0:
        k = ease_io(clamp(tr / 0.8))
        x = lerp(1250, 940, k)
        piece(ctx, P_ell(x, 1210, 120), INK, lw=4)
        piece(ctx, P_ell(x, 1210, 55), hexc("#9aa0ab"), lw=3, shadow=False)


def sc_valor(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    moneda(ctx, 540, 860, 220)
    piece(ctx, P_rrect(240, 1150, 600, 110, 16), hexc("#1d2433"), lw=4)
    v = 4.0 * ease_io(clamp(lt / 1.0))
    txt(ctx, f"{v:.1f} MILLONES $".replace(".", ","), 540, 1225, 60, hexc("#9fd6a0"), anchor="center")


def sc_vias(ctx, pose, lt, ev):
    noche(ctx, pose)
    fachada_museo(ctx, 480, 560, 640, 770)
    # vías elevadas en primer plano
    piece(ctx, P_rect(-10, 1180, 560, 50), hexc("#5b6475"), lw=4)
    for i in range(5):
        piece(ctx, P_rect(20 + i * 110, 1230, 30, 100), hexc("#3d3f4a"), lw=3, shadow=False)
    line(ctx, [(-10, 1170), (540, 1170)], 8, hexc("#9aa0ab"))
    piece(ctx, P_rect(-10, 1330, 1100, 630), hexc("#0c1024"), lw=4, shadow=False)
    te = since(ev, "escalera", lt)
    tv = since(ev, "ventana", lt)
    if te >= 0:
        k = clamp(te / 0.6)
        escalera(ctx, 420, 1170, lerp(420, 640, k), lerp(1170, 900, k))
    for i in range(2):
        if tv >= 0:
            k = clamp((tv - i * 0.4) / 1.0)
            x, y = lerp(300, 600, k), lerp(1170, 900, k)
            if k < 1:
                silueta(ctx, x, y, 0.7, pose, i)
        else:
            silueta(ctx, 200 + i * 120, 1170, 0.7, pose, i)
    if tv >= 0:
        piece(ctx, P_rrect(560, 700, 130, 190, 30), hexc("#ffe58a"), lw=3, shadow=False)


def sc_complice(ctx, pose, lt, ev):
    fondo(ctx, "#5a4a6a", 1330, "#3a2e44")
    silueta(ctx, 540, 1320, 1.3, pose)
    hy = 1320 - (230 + 65) * 1.3
    piece(ctx, P_poly([(540 - 90, hy - 50), (540 + 90, hy - 50), (540 + 75, hy - 115), (540 - 75, hy - 115)]),
          hexc("#1b2747"), lw=4, shadow=False)
    piece(ctx, P_rrect(540 - 110, hy - 60, 220, 24, 8), hexc("#0e1630"), lw=3, shadow=False)
    piece(ctx, P_rrect(380, 1000, 280, 70, 12), (1, 1, 1), lw=4)
    txt(ctx, "VIGILANTE", 520, 1048, 40, INK, anchor="center")
    stamp(ctx, 540, 760, "¿CÓMPLICE?", lt - 0.6, 64, col=ROJO, ang=-8)


def sc_parque(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1260)
    for i in range(6):
        tree(ctx, 60 + i * 200, 1270 - (i % 2) * 30, 1.0, hexc("#1f4a3a"), i)
    tc = since(ev, "coche", lt)
    if tc < 0:
        x = lerp(-200, 700, ease_io(clamp(lt / 2.2)))
        carretilla(ctx, x, 1350, 1.0, pose)
        silueta(ctx, x - 260, 1360, 0.75, pose)
    else:
        coche(ctx, 760, 1400, 1.1, "#2b2d33")
        moneda(ctx, 600, 1180, 70, canto=True)
        stamp(ctx, 760, 1050, "AL MALETERO", tc, 50, col=hexc("#ffe14d"), ang=-6)


def sc_condena(ctx, pose, lt, ev):
    fondo(ctx, "#6b4a33", 1330, "#4a3020")
    piece(ctx, P_rect(120, 1100, 840, 230), hexc("#7a4e2c"), lw=5)
    for i in range(3):
        silueta(ctx, 270 + i * 270, 1120, 0.9, pose, i)
    piece(ctx, P_rect(120, 1080, 840, 40), hexc("#5a3820"), lw=4)
    for i in range(3):
        stamp(ctx, 270 + i * 270, 880, "CONDENADO", lt - 0.3 - i * 0.2, 34, col=ROJO, ang=-8 + i * 6)
    tn = since(ev, "nunca", lt)
    if tn >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 680 - bob, 150, hexc("#ffe14d"), INK, 7)


def sc_fundida(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    k = clamp(lt / 1.5)
    if k < 1:
        moneda(ctx, 540, 820, 200 * (1 - 0.5 * k))
    # crisol
    piece(ctx, P_poly([(380, 1000), (700, 1000), (660, 1230), (420, 1230)]), hexc("#5b6475"), lw=5)
    piece(ctx, P_ell(540, 1005, 160, 30), hexc("#ff8a1f") if (pose // 2) % 2 else hexc("#ffb02e"), lw=3, shadow=False)
    for i in range(3):
        piece(ctx, P_poly([(480 + i * 40, 1240), (500 + i * 40, 1290), (460 + i * 40, 1290)]), hexc("#ff5a1f"), lw=0,
              shadow=False, outline=False)
    tt = since(ev, "trozos", lt)
    if tt >= 0:
        for i in range(6):
            kk = clamp((tt - i * 0.1) / 0.8)
            x = lerp(540, 150 + i * 160, kk)
            piece(ctx, P_rrect(x - 45, 1280 + 0 * kk, 90, 40, 8), ORO, lw=3)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 820, 760 - bob, 170, hexc("#ffe14d"), INK, 7)


SCENES = dict(moneda=sc_moneda, museo=sc_museo, valor=sc_valor, vias=sc_vias, complice=sc_complice, parque=sc_parque,
              condena=sc_condena, fundida=sc_fundida)
SCENES = con_mapa(SCENES, BLOQUES, pais="DEU", ciudad="BERLÍN", lon=13.4, lat=52.52)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_parque(ctx, 0, 1.4, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(73))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "100 KILOS DE ORO", 540, 220, 104, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "EN UNA CARRETILLA", 540, 380, 96, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡NUNCA APARECIÓ!", 540, 1690, 104, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
