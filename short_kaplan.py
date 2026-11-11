#!/usr/bin/env python3
"""
Short 27 · «La fuga de 10 segundos en helicóptero» — Santa Martha Acatitla, CDMX, 1971
Voz gratuita (python voz_gratis.py short_kaplan.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import bubble, since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, fondo, gorra_poli, silueta
from short_helicoptero import helicoptero
from short_altiplano import carcel_exterior

SLUG = "fuga-helicoptero-mexico"
PRONUNCIA = {"Kaplan": "Káplan", "Acatitla": "Acatitla"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que un preso escapó de una cárcel de Ciudad de México… en unos segundos, "
             "y en helicóptero?"),
        escenas=[(None, "patio")],
        pantalla=[("un preso", "UNA FUGA EN SEGUNDOS"), ("y en", "¿EN HELICÓPTERO?")],
        eventos={"heli": "y en"},
    ),
    dict(
        id="caso",
        voz=("Agosto de 1971, penal de Santa Martha Acatitla. Joel Kaplan, un empresario estadounidense, cumple "
             "condena por un asesinato que siempre negó. Su hermana empieza a planear la fuga."),
        escenas=[(None, "penal"), ("Joel Kaplan", "preso"), ("Su hermana", "plan")],
        pantalla=[(None, "CDMX, 1971"), ("Joel Kaplan", "UN PRESO ESTADOUNIDENSE"), ("Su hermana", "EL PLAN")],
        eventos={"nego": "siempre negó"},
    ),
    dict(
        id="aterriza",
        voz=("Una tarde, un helicóptero aterriza en el patio de la prisión. Los guardias creen que es una visita "
             "oficial… y no hacen nada."),
        escenas=[(None, "aterriza")],
        pantalla=[(None, "UNA TARDE…"), ("Los guardias", "«VISITA OFICIAL»")],
        eventos={"guardias": "Los guardias", "nada": "no hacen"},
    ),
    dict(
        id="despega",
        voz=("Kaplan y otro preso suben de un salto, y el helicóptero despega. Unos segundos después, ya están en el "
             "aire, rumbo a Estados Unidos."),
        escenas=[(None, "despega")],
        pantalla=[(None, "¡SUBEN DE UN SALTO!"), ("Unos segundos", "UNOS SEGUNDOS"), ("rumbo a", "RUMBO A EE. UU.")],
        eventos={"despega": "el helicóptero", "rumbo": "rumbo a"},
    ),
    dict(
        id="cierre",
        voz=("La fuga inspiró una película de Hollywood. ¿Te imaginas ver aterrizar un helicóptero en el patio de una "
             "cárcel?"),
        escenas=[(None, "cine")],
        pantalla=[(None, "INSPIRÓ UNA PELÍCULA"), ("Te imaginas", "¿TE LO IMAGINAS?")],
        eventos={"pregunta": "Te imaginas"},
    ),
]


def patio(ctx, pose):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    piece(ctx, P_rect(-10, 560, 1100, 360), hexc("#d9d2c0"), lw=5)
    for i in range(9):
        piece(ctx, P_rect(40 + i * 115, 620, 50, 90), hexc("#3d3f4a"), lw=3, shadow=False)
        piece(ctx, P_rect(40 + i * 115, 760, 50, 90), hexc("#3d3f4a"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 920, 1100, 1040), hexc("#b5a888"), lw=4, shadow=False)
    for i in range(14):
        line(ctx, [(i * 80, 920), (i * 80 - 120, 1960)], 2, hexc("#a8946a"))


def guardia_sil(ctx, x, feet, s, pose, k=0):
    silueta(ctx, x, feet, s, pose, k)
    gorra_poli(ctx, x, feet, s)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_patio(ctx, pose, lt, ev):
    patio(ctx, pose)
    for i in range(4):
        silueta(ctx, 160 + i * 250, 1330, 0.8, pose, i)
    th = since(ev, "heli", lt)
    if th >= 0:
        k = ease_io(clamp(th / 1.0))
        helicoptero(ctx, lerp(1300, 700, k), lerp(500, 700, k), 0.8, pose)


def sc_penal(ctx, pose, lt, ev):
    carcel_exterior(ctx, pose)
    piece(ctx, P_rrect(320, 1080, 440, 70, 12), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "SANTA MARTHA ACATITLA", 540, 1127, 30, INK, anchor="center")


def sc_preso(ctx, pose, lt, ev):
    fondo(ctx, "#8a8f9a", 1330, "#5b6475")
    silueta(ctx, 540, 1320, 1.3, pose)
    for i in range(9):
        line(ctx, [(140 + i * 100, 560), (140 + i * 100, 1330)], 14, hexc("#2b2d33"))
    line(ctx, [(120, 620), (960, 620)], 16, hexc("#2b2d33"))
    tn = since(ev, "nego", lt)
    if tn >= 0:
        bubble(ctx, 760, 760, 300, 110, (620, 900), ["¡INOCENTE!"], 44)


def sc_plan(ctx, pose, lt, ev):
    fondo(ctx, "#6b5a4a", 1330, "#4a3a2a")
    piece(ctx, P_rect(140, 1080, 800, 50), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(160, 1130, 30, 200), hexc("#5a3820"), lw=3, shadow=False)
    piece(ctx, P_rect(890, 1130, 30, 200), hexc("#5a3820"), lw=3, shadow=False)
    piece(ctx, P_rect(260, 860, 560, 220), hexc("#f3e6c9"), lw=4)
    line(ctx, [(300, 1040), (480, 940), (640, 1000), (780, 900)], 6, ROJO)
    piece(ctx, P_rect(320, 900, 120, 90), hexc("#9aa0ab"), lw=3, shadow=False)
    txt(ctx, "X", 780, 915, 50, ROJO, anchor="center")
    # hermana: silueta con melena
    x, feet, s = 900, 1330, 1.0
    piece(ctx, P_rrect(x - 75, feet - 330, 150, 160, 60), hexc("#3a2a1e"), lw=4, shadow=False)
    silueta(ctx, x, feet, s, pose)


def sc_aterriza(ctx, pose, lt, ev):
    patio(ctx, pose)
    k = ease_io(clamp(lt / 1.6))
    helicoptero(ctx, lerp(1300, 560, k), lerp(500, 1080, k), 1.0, pose)
    tg = since(ev, "guardias", lt)
    if tg >= 0:
        for i in range(2):
            guardia_sil(ctx, 120 + i * 840, 1330, 0.85, pose, i)
        bubble(ctx, 220, 760, 360, 110, (140, 960), ["¿UNA VISITA?"], 42)
    tn = since(ev, "nada", lt)
    if tn >= 0:
        stamp(ctx, 540, 1400, "NO HACEN NADA", tn, 52, col=ROJO, ang=-6)


def sc_despega(ctx, pose, lt, ev):
    patio(ctx, pose)
    td = since(ev, "despega", lt)
    if td < 0:
        helicoptero(ctx, 560, 1080, 1.0, pose)
        for i in range(2):
            silueta(ctx, lerp(150 + i * 120, 470, clamp(lt / 0.8)), 1330, 0.8, pose, i)
    else:
        k = ease_io(clamp(td / 3.5))
        helicoptero(ctx, lerp(560, -250, k), lerp(1080, 700, k), 1.0, pose)
    secs = min(10, int(lt * 3))
    piece(ctx, P_rrect(780, 1180, 240, 100, 14), hexc("#1d2433"), lw=4)
    txt(ctx, f"{secs} s", 900, 1250, 60, hexc("#ffe14d"), anchor="center")


def sc_cine(ctx, pose, lt, ev):
    fondo(ctx, "#1d1a2e", 1330, "#141223")
    piece(ctx, P_rect(120, 560, 840, 500), (1, 1, 1), lw=5)
    ctx.save()
    P_rect(130, 570, 820, 480)(ctx)
    ctx.clip()
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    helicoptero(ctx, 540 + 60 * math.sin(lt), 800, 0.8, pose)
    ctx.restore()
    for i in range(6):
        piece(ctx, P_ell(150 + i * 155, 1300, 60, 70), hexc("#2b2340"), lw=3, shadow=False)
    for i in range(10):
        piece(ctx, P_rect(80 + i * 96, 1080, 50, 40), hexc("#ffe58a") if (i + pose // 3) % 2 else hexc("#c9a46a"), lw=0,
              shadow=False, outline=False)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 960, 1200 - bob, 120, hexc("#ffe14d"), INK, 6)


SCENES = dict(patio=sc_patio, penal=sc_penal, preso=sc_preso, plan=sc_plan, aterriza=sc_aterriza, despega=sc_despega,
              cine=sc_cine)
SCENES = con_mapa(SCENES, BLOQUES, pais="MEX", ciudad="CIUDAD DE MÉXICO", lon=-99.13, lat=19.43)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_aterriza(ctx, 0, 2.0, {"guardias_lt": 0.5})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(107))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UN HELICÓPTERO", 540, 220, 104, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "EN EL PATIO DEL PENAL", 540, 380, 84, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡FUGA EN 10 SEGUNDOS!", 540, 1690, 88, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
