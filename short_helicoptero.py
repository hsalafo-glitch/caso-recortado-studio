#!/usr/bin/env python3
"""
Short 26 · «Robaron un depósito de dinero aterrizando en el tejado» — Västberga, Estocolmo, 2009
Voz gratuita (python voz_gratis.py short_helicoptero.py).
"""
import math
import os

import cairo

import generar_short as g
from mapa_mundo import con_mapa
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ROJO, SOMBRA, VERDE_BILLETE, fondo, noche, silueta
from short_robo_siglo import saco

SLUG = "robo-helicoptero"
PRONUNCIA = {"Estocolmo": "Estocolmo"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pasaría si unos ladrones asaltaran un depósito de dinero… aterrizando en el tejado con un "
             "helicóptero?"),
        escenas=[(None, "deposito"), ("aterrizando", "llegada")],
        pantalla=[("un depósito", "UN DEPÓSITO DE DINERO"), ("aterrizando", "¿EN HELICÓPTERO?")],
        eventos={},
    ),
    dict(
        id="caso",
        voz=("Estocolmo, septiembre de 2009. Antes del amanecer, un helicóptero robado aterriza en el tejado de un "
             "depósito de dinero de una empresa de seguridad."),
        escenas=[(None, "llegada")],
        pantalla=[(None, "ESTOCOLMO, 2009"), ("un helicóptero", "UN HELICÓPTERO ROBADO"), ("aterriza", "¡EN EL TEJADO!")],
        eventos={"robado": "helicóptero robado"},
    ),
    dict(
        id="dentro",
        voz=("Los ladrones rompen una ventana del techo, se abren paso con explosivos y bajan a por el dinero. En "
             "pocos minutos vuelven a subir con sacos llenos."),
        escenas=[(None, "corte"), ("En pocos", "sacos")],
        pantalla=[(None, "POR EL TECHO"), ("se abren", "¡EXPLOSIVOS!"), ("En pocos", "SACOS LLENOS")],
        eventos={"rompen": "rompen una", "explosivos": "con explosivos", "bajan": "y bajan"},
    ),
    dict(
        id="policia",
        voz=("La policía no puede usar sus helicópteros: alguien había dejado un paquete sospechoso en su base. Se "
             "llevan unos 39 millones de coronas."),
        escenas=[(None, "base"), ("Se llevan", "botin")],
        pantalla=[(None, "LA POLICÍA, EN TIERRA"), ("un paquete", "¿UNA BOMBA?"), ("Se llevan", "≈ 39 MILLONES DE CORONAS")],
        eventos={"paquete": "un paquete"},
    ),
    dict(
        id="cierre",
        voz="Varios acabaron condenados, pero el dinero nunca apareció. ¿Te lo esperabas?",
        escenas=[(None, "final")],
        pantalla=[(None, "CONDENADOS"), ("pero el", "¿Y EL DINERO?"), ("Te lo", "¿TE LO ESPERABAS?")],
        eventos={"dinero": "pero el", "pregunta": "Te lo"},
    ),
]


def helicoptero(ctx, x, y, s, pose, col="#2b2d33"):
    piece(ctx, P_rect(x + 60 * s, y - 20 * s, 260 * s, 30 * s), hexc(col), lw=4)
    piece(ctx, P_poly([(x + 300 * s, y - 20 * s), (x + 340 * s, y - 90 * s), (x + 360 * s, y - 90 * s), (x + 340 * s, y + 10 * s)]),
          hexc(col), lw=4)
    piece(ctx, P_ell(x, y, 140 * s, 90 * s), hexc(col), lw=5)
    piece(ctx, P_ell(x - 60 * s, y - 20 * s, 60 * s, 50 * s), hexc("#8ec5e8"), lw=4, shadow=False)
    line(ctx, [(x - 90 * s, y + 110 * s), (x + 110 * s, y + 110 * s)], 8 * s, INK)
    for dx in (-50, 60):
        line(ctx, [(x + dx * s, y + 80 * s), (x + dx * s, y + 110 * s)], 6 * s, INK)
    line(ctx, [(x, y - 90 * s), (x, y - 120 * s)], 8 * s, INK)
    w = 300 * s if pose % 2 == 0 else 90 * s
    line(ctx, [(x - w, y - 120 * s), (x + w, y - 120 * s)], 8 * s, hexc("#5b6475"))


def edificio(ctx, x, y, w, h, roto=False):
    piece(ctx, P_rect(x, y, w, h), hexc("#9aa0ab"), lw=5)
    for r in range(3):
        for c in range(5):
            piece(ctx, P_rect(x + 40 + c * (w - 80) / 5, y + 60 + r * (h - 100) / 3, (w - 80) / 5 - 30, (h - 100) / 3 - 50),
                  hexc("#3d4a5a"), lw=3, shadow=False)
    piece(ctx, P_rect(x - 20, y - 30, w + 40, 30), hexc("#6b707c"), lw=4)
    piece(ctx, P_rect(x + w / 2 - 80, y - 60, 160, 30), hexc("#ffe58a") if roto else hexc("#8ec5e8"), lw=4)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_deposito(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    edificio(ctx, 160, 820, 760, 510)
    piece(ctx, P_rrect(330, 900, 420, 70, 12), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "DEPÓSITO DE DINERO", 540, 948, 32, INK, anchor="center")
    for i in range(3):
        saco(ctx, 380 + i * 160, 1230, 0.55)


def sc_llegada(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    edificio(ctx, 160, 900, 760, 430)
    k = ease_io(clamp(lt / 1.8))
    x, y = lerp(1300, 560, k), lerp(560, 760, k)
    helicoptero(ctx, x, y, 0.9, pose)
    ctx.move_to(x - 40, y + 100)
    ctx.line_to(x - 200, y + 400)
    ctx.line_to(x + 120, y + 400)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.6, 0.15)
    ctx.fill()
    tr = since(ev, "robado", lt)
    if tr >= 0:
        stamp(ctx, 360, 1200, "ROBADO", tr, 58, col=ROJO, ang=-8)


def sc_corte(ctx, pose, lt, ev):
    fondo(ctx, "#141a33", None)
    piece(ctx, P_rect(80, 760, 920, 30), hexc("#6b707c"), lw=4)
    piece(ctx, P_rect(80, 790, 920, 640), hexc("#c9ccd6"), lw=5)
    piece(ctx, P_rect(80, 1100, 920, 20), hexc("#6b707c"), lw=3, shadow=False)
    helicoptero(ctx, 300, 640, 0.6, pose)
    tr = since(ev, "rompen", lt)
    if tr >= 0:
        piece(ctx, P_rect(500, 760, 160, 30), hexc("#1a1d24"), lw=3, shadow=False)
    te = since(ev, "explosivos", lt)
    if te >= 0 and te < 0.8 and (pose // 2) % 2 == 0:
        draw_text(ctx, "¡BUM!", 580, 1110, 90, hexc("#ffe14d"), INK, 7)
        for a in range(8):
            ang = a * math.pi / 4
            line(ctx, [(580 + 60 * math.cos(ang), 1110 + 60 * math.sin(ang)), (580 + 140 * math.cos(ang), 1110 + 140 * math.sin(ang))],
                 6, hexc("#ff8a1f"))
    tb = since(ev, "bajan", lt)
    if tb >= 0:
        piece(ctx, P_rect(520, 1100, 120, 20), hexc("#1a1d24"), lw=3, shadow=False)
        line(ctx, [(560, 790), (560, 1400)], 5, hexc("#d9c08a"))
        for i in range(2):
            y = lerp(900, 1380, clamp((tb - i * 0.4) / 1.4))
            silueta(ctx, 600 + i * 90, y, 0.5, pose, i)
        for i in range(4):
            piece(ctx, P_rect(760 + (i % 2) * 90, 1280 - (i // 2) * 60, 80, 50), VERDE_BILLETE, lw=3, shadow=False)


def sc_sacos(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1330)
    edificio(ctx, 160, 900, 760, 430, roto=True)
    helicoptero(ctx, 560, 760, 0.9, pose)
    for i in range(int(clamp(lt / 1.2) * 4)):
        saco(ctx, 300 + i * 140, 840, 0.4)
    if lt > 1.4:
        k = clamp((lt - 1.4) / 1.0)
        ctx.save()
        ctx.translate(0, -400 * k)
        ctx.restore()


def sc_base(ctx, pose, lt, ev):
    set_col(ctx, hexc("#6b7a8a"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1200, 1100, 760), hexc("#4a4f5c"), lw=4, shadow=False)
    ctx.new_sub_path()
    ctx.arc(540, 1280, 160, 0, 2 * math.pi)
    set_col(ctx, hexc("#ffe14d"))
    ctx.set_line_width(10)
    ctx.stroke()
    draw_text(ctx, "H", 540, 1280, 120, hexc("#ffe14d"), INK, 0)
    helicoptero(ctx, 540, 1060, 0.85, 0, col="#1d4ed8")
    txt(ctx, "POLICÍA", 520, 1070, 30, (1, 1, 1), anchor="center")
    tp = since(ev, "paquete", lt)
    if tp >= 0:
        piece(ctx, P_rrect(840, 1240, 140, 100, 12), hexc("#7a4e2c"), lw=4)
        line(ctx, [(840, 1290), (980, 1290)], 5, hexc("#3d2614"))
        stamp(ctx, 540, 760, "NO PUEDEN DESPEGAR", tp, 48, col=ROJO, ang=-6)


def sc_botin(ctx, pose, lt, ev):
    noche(ctx, pose)
    k = ease_io(clamp(lt / 2.0))
    helicoptero(ctx, lerp(540, -300, k), lerp(900, 640, k), 0.9, pose)
    piece(ctx, P_rrect(230, 1150, 620, 110, 16), hexc("#1d2433"), lw=4)
    v = int(39 * ease_io(clamp(lt / 1.0)))
    txt(ctx, f"{v} MILLONES DE CORONAS", 540, 1222, 44, hexc("#9fd6a0"), anchor="center")


def sc_final(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    for i in range(4):
        x = 180 + i * 240
        silueta(ctx, x, 1330, 0.85, pose, i)
        stamp(ctx, x, 1000, "CONDENADO", lt - 0.3 - i * 0.15, 30, col=ROJO, ang=-8 + i * 5)
    td = since(ev, "dinero", lt)
    if td >= 0:
        for i in range(3):
            saco(ctx, 380 + i * 160, 760, 0.45)
        bob = (pose // 4) % 2 * 8
        draw_text(ctx, "?", 540, 640 - bob, 130, hexc("#ffe14d"), INK, 7)


SCENES = dict(deposito=sc_deposito, llegada=sc_llegada, corte=sc_corte, sacos=sc_sacos, base=sc_base, botin=sc_botin,
              final=sc_final)
SCENES = con_mapa(SCENES, BLOQUES, pais="SWE", ciudad="ESTOCOLMO", lon=18.07, lat=59.33)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_sacos(ctx, 0, 1.2, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(103))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ATERRIZARON", 540, 220, 110, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "EN EL TEJADO", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y SE LLEVARON EL DINERO!", 540, 1690, 78, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
