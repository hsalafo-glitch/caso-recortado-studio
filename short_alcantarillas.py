#!/usr/bin/env python3
"""
Short 28 · «Robaron un banco entrando por las alcantarillas» — Société Générale, Niza, 1976
Voz gratuita (python voz_gratis.py short_alcantarillas.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, fondo, silueta
from short_robo_siglo import olas, pared_cajas, saco, banco
from short_tunel import TIERRA, TIERRA2, excavador

SLUG = "robo-alcantarillas"
PRONUNCIA = {"Niza": "Niza", "Société Générale": "Sosieté Yeneral"}

BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina robar un banco… entrando por las alcantarillas.",
        escenas=[(None, "calle"), ("entrando", "tapa")],
        pantalla=[("robar", "ROBAR UN BANCO…"), ("entrando", "¿POR LAS ALCANTARILLAS?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Niza, julio de 1976. Durante semanas, una banda cava un túnel desde las alcantarillas hasta la cámara "
             "acorazada de un banco, la Société Générale."),
        escenas=[(None, "corte")],
        pantalla=[(None, "NIZA, 1976"), ("Durante semanas", "SEMANAS CAVANDO"), ("hasta la", "HASTA LA CÁMARA")],
        eventos={"camara": "hasta la"},
    ),
    dict(
        id="dentro",
        voz=("Aprovechan un fin de semana largo. Dentro, abren cientos de cajas de seguridad… y, según se cuenta, "
             "hasta se sientan a comer allí mismo."),
        escenas=[(None, "cajas"), ("y, según", "picnic")],
        pantalla=[(None, "FIN DE SEMANA LARGO"), ("abren cientos", "CIENTOS DE CAJAS"), ("y, según", "¿UN PICNIC?")],
        eventos={},
    ),
    dict(
        id="nota",
        voz=("Antes de irse, dejan escrito en la pared: \"sin armas, sin odio y sin violencia\". Se llevan unos 46 "
             "millones de francos que nunca aparecieron."),
        escenas=[(None, "pared"), ("Se llevan", "botin")],
        pantalla=[(None, "UN MENSAJE…"), ("Se llevan", "≈ 46 MILLONES DE FRANCOS"), ("que nunca", "NUNCA APARECIERON")],
        eventos={"odio": "sin odio", "violencia": "sin violencia"},
    ),
    dict(
        id="cierre",
        voz=("Treinta años después, unos ladrones argentinos dejaron una nota muy parecida en un banco de Buenos "
             "Aires. ¿Casualidad?"),
        escenas=[(None, "eco")],
        pantalla=[(None, "30 AÑOS DESPUÉS…"), ("Casualidad", "¿CASUALIDAD?")],
        eventos={"nota": "una nota", "pregunta": "Casualidad"},
    ),
]


def tapa_alcantarilla(ctx, x, y, r, abierta=0.0):
    piece(ctx, P_ell(x, y, r, r * 0.35), hexc("#1a1d24"), lw=4)
    if abierta < 1:
        with rot(ctx, x, y, 0):
            dx = r * 1.2 * abierta
            piece(ctx, P_ell(x + dx, y - 10 * abierta, r, r * 0.35), hexc("#5b6475"), lw=4)
            for i in range(3):
                line(ctx, [(x + dx - r * 0.6, y - r * 0.12 + i * r * 0.12), (x + dx + r * 0.6, y - r * 0.12 + i * r * 0.12)],
                     4, hexc("#3d3f4a"))


def calle_niza(ctx, pose):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    for i, (x, w, h, col) in enumerate(((-20, 340, 600, "#f2c9a0"), (320, 300, 680, "#f2e0b0"), (620, 480, 560, "#e8b98a"))):
        piece(ctx, P_rect(x, 1250 - h, w, h), hexc(col), lw=4)
        for r in range(3):
            for c in range(2):
                piece(ctx, P_rect(x + 50 + c * (w - 150), 1250 - h + 60 + r * 160, 80, 110), hexc("#2f9e4f"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1250, 1100, 710), hexc("#9aa0ab"), lw=4, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_calle(ctx, pose, lt, ev):
    calle_niza(ctx, pose)
    piece(ctx, P_rect(620, 690, 480, 70), hexc("#c8202f"), lw=4)
    txt(ctx, "BANCO", 860, 740, 46, (1, 1, 1), anchor="center")
    tapa_alcantarilla(ctx, 300, 1360, 110)


def sc_tapa(ctx, pose, lt, ev):
    calle_niza(ctx, pose)
    k = clamp(lt / 0.8)
    tapa_alcantarilla(ctx, 540, 1350, 200, abierta=k)
    if k >= 1:
        silueta(ctx, 540, 1340, 0.8, pose)
        piece(ctx, P_rect(300, 1350, 480, 120), hexc("#9aa0ab"), lw=0, shadow=False, outline=False)
        tapa_alcantarilla(ctx, 540, 1350, 200, abierta=1.0)


def sc_corte(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    banco(ctx, 560, 560, 460, 300, pose)
    piece(ctx, P_rect(-10, 860, 1100, 1100), TIERRA, lw=4, shadow=False)
    for i in range(30):
        piece(ctx, P_ell(hnoise("tn", i) * 1080, 900 + hnoise("tn", i, "y") * 560, 10), TIERRA2, lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(-10, 845, 1100, 24), hexc("#6b6f78"), lw=4, shadow=False)
    # cámara acorazada bajo el banco
    piece(ctx, P_rect(640, 900, 340, 220), hexc("#5b6475"), lw=6)
    pared_cajas(ctx, 670, 930, 5, 2, 56, 80, 0)
    # alcantarilla (tubo) abajo a la izquierda
    piece(ctx, P_rect(-10, 1250, 520, 160), hexc("#9aa0ab"), lw=5, shadow=False)
    piece(ctx, P_rect(-10, 1270, 520, 120), hexc("#4a4f5c"), lw=3, shadow=False)
    ctx.save()
    P_rect(-10, 1270, 520, 120)(ctx)
    ctx.clip()
    olas(ctx, 1350, pose, hexc("#5a6a4a"))
    ctx.restore()
    k = ease_io(clamp(lt / 3.0))
    pts = [(500, 1320), (lerp(500, 800, k), lerp(1320, 1150, k))]
    line(ctx, pts, 80, hexc("#2a1a10"))
    excavador(ctx, pts[-1][0] - 30, pts[-1][1] + 40, 0.3, pose)
    tc = since(ev, "camara", lt)
    if tc >= 0:
        stamp(ctx, 810, 820, "CÁMARA", tc, 44, col=hexc("#ffe14d"), ang=-6)


def sc_cajas(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1330, "#262a3a")
    n = int(clamp(lt / 2.0) * 60)
    pared_cajas(ctx, 90, 560, 10, 6, 92, 92, n)
    for i in range(3):
        saco(ctx, 260 + i * 280, 1250, 0.6)


def sc_picnic(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1330, "#262a3a")
    pared_cajas(ctx, 90, 560, 10, 4, 92, 92, 40)
    # mantel con comida
    piece(ctx, P_poly([(220, 1300), (860, 1300), (800, 1160), (280, 1160)]), (1, 1, 1), lw=4)
    for i in range(4):
        for j in range(2):
            if (i + j) % 2 == 0:
                piece(ctx, P_poly([(280 + i * 130 + j * -15, 1160 + j * 70), (410 + i * 130 + j * -15, 1160 + j * 70),
                                   (405 + i * 130 - (j + 1) * 15, 1230 + j * 70), (275 + i * 130 - (j + 1) * 15, 1230 + j * 70)]),
                      hexc("#e63946"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rrect(420, 1060, 40, 120, 12), hexc("#5a2a3a"), lw=4)
    piece(ctx, P_ell(600, 1180, 70, 24), hexc("#d9a050"), lw=4)
    piece(ctx, P_rrect(520, 1150, 160, 40, 18), hexc("#e8c48a"), lw=3, shadow=False)
    for i, x in enumerate((180, 900)):
        silueta(ctx, x, 1330, 0.9, pose, i)


def sc_pared(ctx, pose, lt, ev):
    fondo(ctx, "#5b6475", 1330, "#3d3f4a")
    piece(ctx, P_rect(80, 560, 920, 700), hexc("#c9ccd6"), lw=5)
    lineas = [("SIN ARMAS,", None), ("SIN ODIO", "odio"), ("Y SIN VIOLENCIA", "violencia")]
    for i, (tline, key) in enumerate(lineas):
        if key is None or since(ev, key, lt) >= 0:
            with rot(ctx, 540, 720 + i * 170, math.radians(-3 + i * 2)):
                draw_text(ctx, tline, 540, 720 + i * 170, 92, hexc("#1d2433"), hexc("#1d2433"), 0)
    pared_cajas(ctx, 380, 1180, 4, 1, 80, 60, 4)


def sc_botin(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i in range(4):
        saco(ctx, 240 + i * 200, 1000, 0.8)
    piece(ctx, P_rrect(200, 1170, 680, 110, 16), hexc("#1d2433"), lw=4)
    v = int(46 * ease_io(clamp(lt / 1.0)))
    txt(ctx, f"{v} MILLONES DE FRANCOS", 540, 1242, 46, hexc("#9fd6a0"), anchor="center")


def sc_eco(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", 1330, "#1a1428")
    for i, (x, y, a, t1, t2, col) in enumerate(((300, 850, -6, "NIZA 1976", "«SIN ARMAS, SIN ODIO…»", "#c9ccd6"),
                                                (780, 1050, 5, "BS. AS. 2006", "«SIN ARMAS NI RENCORES…»", "#fbf6e8"))):
        if i == 1 and since(ev, "nota", lt) < 0:
            continue
        with rot(ctx, x, y, math.radians(a)):
            piece(ctx, P_rect(x - 220, y - 150, 440, 300), hexc(col), lw=5)
            txt(ctx, t1, x, y - 70, 44, ROJO, anchor="center")
            txt(ctx, t2, x, y + 20, 30, hexc("#1d2433"), anchor="center")
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 1300 - bob, 140, hexc("#ffe14d"), INK, 7)


SCENES = dict(calle=sc_calle, tapa=sc_tapa, corte=sc_corte, cajas=sc_cajas, picnic=sc_picnic, pared=sc_pared,
              botin=sc_botin, eco=sc_eco)
SCENES = con_mapa(SCENES, BLOQUES, pais="FRA", ciudad="NIZA", lon=7.26, lat=43.7)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_corte(ctx, 0, 2.5, {"camara_lt": 1.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(109))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ROBARON UN BANCO", 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "POR LAS ALCANTARILLAS", 540, 380, 86, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "«SIN ODIO NI VIOLENCIA»", 540, 1690, 86, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
