#!/usr/bin/env python3
"""
Short 14 · «El robo que hizo famosa a la Mona Lisa» — Louvre, 1911
Voz gratuita (python voz_gratis.py short_mona_lisa.py).

Uso:
    python short_mona_lisa.py            # vídeo final (usa cache_audio/mona-lisa/)
    python short_mona_lisa.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import since, stamp, txt
from piezas_casos import BORDE, ORO, ROJO, SOMBRA, fondo, marco, retrato, silueta
from short_museo import guardia

SLUG = "mona-lisa"
PRONUNCIA = {"Louvre": "Luvre"}

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que el cuadro más famoso del mundo… se lo llevó bajo el brazo un hombre "
             "que había trabajado en el museo?"),
        escenas=[(None, "cuadro"), ("se lo", "brazo")],
        pantalla=[("cuadro más", "EL CUADRO MÁS FAMOSO"), ("bajo el", "¿BAJO EL BRAZO?")],
        eventos={"trabajado": "había trabajado"},
    ),
    dict(
        id="caso",
        voz=("París, agosto de 1911. Un hombre pasa la noche escondido en un armario del Louvre. Por la mañana, "
             "con el museo cerrado, descuelga la Mona Lisa y sale tan tranquilo."),
        escenas=[(None, "armario"), ("Por la", "descuelga")],
        pantalla=[(None, "PARÍS, 1911"), ("escondido", "ESCONDIDO TODA LA NOCHE"), ("descuelga", "¡LA DESCUELGA!")],
        eventos={"armario": "un armario", "cerrado": "museo cerrado", "descuelga": "descuelga la",
                 "sale": "sale tan"},
    ),
    dict(
        id="pistas",
        voz=("Nadie se da cuenta hasta el día siguiente. Interrogan incluso a Picasso. Durante dos años, el cuadro "
             "descansa en un baúl con doble fondo en su piso."),
        escenas=[(None, "hueco"), ("Interrogan", "interrogatorio"), ("Durante dos", "baul")],
        pantalla=[(None, "NADIE SE DA CUENTA"), ("Interrogan", "¿PICASSO?"), ("Durante dos", "2 AÑOS ESCONDIDA")],
        eventos={"siguiente": "día siguiente", "picasso": "a Picasso", "doble": "doble fondo"},
    ),
    dict(
        id="venta",
        voz="En 1913 intenta venderlo a un marchante de Florencia, que avisa a la policía.",
        escenas=[(None, "venta")],
        pantalla=[(None, "FLORENCIA, 1913"), ("que avisa", "¡AVISA A LA POLICÍA!")],
        eventos={"avisa": "que avisa"},
    ),
    dict(
        id="cierre",
        voz=("Antes del robo, la Mona Lisa no era tan famosa. El robo la convirtió en el cuadro más famoso del "
             "mundo. ¿Lo sabías?"),
        escenas=[(None, "fama")],
        pantalla=[(None, "ANTES: POCO CONOCIDA"), ("El robo", "¡FAMOSA EN TODO EL MUNDO!"), ("Lo sabías", "¿LO SABÍAS?")],
        eventos={"robo": "El robo", "pregunta": "Lo sabías"},
    ),
]

PARED = "#8a4b3c"


def sala(ctx, col=PARED):
    fondo(ctx, col, 1330, "#5a3a2a")
    piece(ctx, P_rect(-10, 1300, 1100, 40), hexc("#d9c7a3"), lw=4, shadow=False)
    for i in range(7):
        piece(ctx, P_rect(i * 170 - 20, 1330, 120, 630), hexc("#6b4a33"), lw=2, shadow=False)


def clavos(ctx, x, y, w):
    for dx in (0.2, 0.8):
        piece(ctx, P_ell(x + w * dx, y, 9), hexc("#3d3f4a"), lw=2, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_cuadro(ctx, pose, lt, ev):
    sala(ctx)
    k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
    with rot(ctx, 540, 900, 0):
        ctx.save()
        ctx.translate(540, 920)
        ctx.scale(max(0.05, k), max(0.05, k))
        ctx.translate(-540, -920)
        marco(ctx, 300, 580, 480, 680, retrato, borde=46)
        ctx.restore()
    # cordón de museo
    for x in (150, 930):
        piece(ctx, P_rect(x - 10, 1150, 20, 160), hexc("#d9a520"), lw=3)
    ctx.move_to(150, 1170)
    ctx.curve_to(400, 1260, 680, 1260, 930, 1170)
    set_col(ctx, ROJO)
    ctx.set_line_width(10)
    ctx.stroke()


def sc_brazo(ctx, pose, lt, ev):
    sala(ctx)
    clavos(ctx, 300, 600, 480)
    piece(ctx, P_rect(320, 620, 440, 600), hexc("#7a4034"), lw=0, shadow=False, outline=False)
    x = lerp(300, 860, ease_io(clamp(lt / 2.2)))
    silueta(ctx, x, 1320, 1.25, pose)
    with rot(ctx, x + 40, 1120, math.radians(-8)):
        marco(ctx, x - 40, 1000, 200, 270, retrato, borde=22)
    tt = since(ev, "trabajado", lt)
    if tt >= 0:
        stamp(ctx, 300, 1150, "EXEMPLEADO", tt, 50, col=ROJO, ang=-8)


def sc_armario(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", 1330, "#1a1428")
    # armario en corte
    piece(ctx, P_rect(260, 600, 560, 720), hexc("#6b4428"), lw=6)
    piece(ctx, P_rect(290, 630, 500, 660), hexc("#1a120c"), lw=3, shadow=False)
    silueta(ctx, 540, 1290, 1.15, pose)
    # puerta entreabierta
    piece(ctx, P_poly([(790, 630), (900, 650), (900, 1270), (790, 1290)]), hexc("#8a5a34"), lw=5)
    piece(ctx, P_ell(820, 960, 12), ORO, lw=2, shadow=False)
    # reloj de la noche
    horas = 21 + lt * 2.5
    piece(ctx, P_ell(150, 700, 80), (1, 1, 1), lw=5)
    a1, a2 = horas * math.pi / 6, horas * 2 * math.pi
    line(ctx, [(150, 700), (150 + 40 * math.sin(a1), 700 - 40 * math.cos(a1))], 7, INK)
    line(ctx, [(150, 700), (150 + 62 * math.sin(a2), 700 - 62 * math.cos(a2))], 4, ROJO)
    if since(ev, "armario", lt) >= 0:
        bob = (pose // 4) % 2 * 6
        txt(ctx, "Z", 700, 760 - bob, 60, hexc("#ffe14d"), anchor="center")
        txt(ctx, "z", 740, 710 - bob, 44, hexc("#ffe14d"), anchor="center")


def sc_descuelga(ctx, pose, lt, ev):
    sala(ctx)
    tdes = since(ev, "descuelga", lt)
    ts = since(ev, "sale", lt)
    clavos(ctx, 360, 600, 360)
    if tdes < 0:
        marco(ctx, 360, 600, 360, 500, retrato, borde=36)
        silueta(ctx, 260, 1320, 1.2, pose)
    elif ts < 0:
        k = ease_io(clamp(tdes / 0.6))
        marco(ctx, 360 - 120 * k, 600 + 340 * k, 360, 500, retrato, borde=36)
        silueta(ctx, 260, 1320, 1.2, pose)
    else:
        piece(ctx, P_rect(380, 620, 320, 460), hexc("#7a4034"), lw=0, shadow=False, outline=False)
        k = ease_io(clamp(ts / 1.4))
        x = lerp(260, 960, k)
        silueta(ctx, x, 1320, 1.2, pose)
        with rot(ctx, x + 30, 1120, math.radians(-8)):
            marco(ctx, x - 50, 990, 190, 260, retrato, borde=20)
        txt(ctx, "SALIDA", 980, 760, 40, hexc("#2fb35a"), anchor="center")
    tc = since(ev, "cerrado", lt)
    if tc >= 0 and ts < 0:
        piece(ctx, P_rrect(760, 640, 260, 90, 12), hexc("#1d2433"), lw=4)
        txt(ctx, "CERRADO", 890, 700, 40, ROJO, anchor="center")


def sc_hueco(ctx, pose, lt, ev):
    sala(ctx)
    clavos(ctx, 360, 600, 360)
    piece(ctx, P_rect(380, 620, 320, 460), hexc("#7a4034"), lw=0, shadow=False, outline=False)
    guardia(ctx, 780, 880, r=85, pose=pose, expr="preocupado")
    tsig = since(ev, "siguiente", lt)
    if tsig >= 0:
        stamp(ctx, 540, 850, "¡NO ESTÁ!", tsig, 70, col=ROJO, ang=-8)


def sc_interrogatorio(ctx, pose, lt, ev):
    fondo(ctx, "#1d1a2e", 1330, "#141223")
    ctx.move_to(540, 520)
    ctx.line_to(260, 1240)
    ctx.line_to(820, 1240)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.6, 0.18)
    ctx.fill()
    line(ctx, [(540, 380), (540, 520)], 5, hexc("#9aa0ab"))
    piece(ctx, P_poly([(470, 560), (610, 560), (580, 510), (500, 510)]), hexc("#3d3f4a"), lw=4)
    silueta(ctx, 540, 1250, 1.2, pose)
    piece(ctx, P_rect(150, 1180, 780, 60), hexc("#5a3820"), lw=5)
    piece(ctx, P_rect(150, 1240, 780, 100), hexc("#3d2614"), lw=4, shadow=False)
    piece(ctx, P_rrect(380, 1190, 320, 50, 10), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "PICASSO", 540, 1228, 40, INK, anchor="center")
    tp = since(ev, "picasso", lt)
    if tp >= 0:
        stamp(ctx, 540, 820, "SIN PRUEBAS", tp + 0.0 - 0.6, 52, col=hexc("#2f6b45"), ang=-6)


def sc_baul(ctx, pose, lt, ev):
    fondo(ctx, "#4a3a5a", 1330, "#2e2238")
    # baúl en corte, con doble fondo
    piece(ctx, P_rect(180, 760, 720, 520), hexc("#8a5a34"), lw=6)
    for x in (180, 880):
        piece(ctx, P_rect(x, 760, 20, 520), hexc("#3d3f4a"), lw=3, shadow=False)
    piece(ctx, P_rect(210, 790, 660, 300), hexc("#5a3820"), lw=3, shadow=False)
    for i in range(5):
        piece(ctx, P_rrect(240 + i * 125, 860 + (i % 2) * 30, 110, 180, 12),
              hexc(["#c94a4a", "#4a7ac9", "#d9c7a3", "#5fa35a", "#a77c44"][i]), lw=3, shadow=False)
    td = since(ev, "doble", lt)
    k = ease_io(clamp(td / 0.6)) if td >= 0 else 0
    piece(ctx, P_rect(210, 1100 + 0, 660, 20), hexc("#6b4428"), lw=4)
    piece(ctx, P_rect(210, 1120, 660, 140), hexc("#1a120c"), lw=3, shadow=False)
    if k > 0:
        marco(ctx, lerp(560, 300, k), 1125, 300, 130, lambda c, x, y, w, h: retrato(c, x, y, w, h * 3), borde=14)
        stamp(ctx, 420, 660, "DOBLE FONDO", td, 52, col=hexc("#ffe14d"), ang=-5)
    yrs = 1911 + int(2 * clamp(lt / 1.8))
    piece(ctx, P_rrect(790, 600, 240, 90, 14), (1, 1, 1), lw=4)
    txt(ctx, str(yrs), 910, 665, 60, INK, anchor="center")


def sc_venta(ctx, pose, lt, ev):
    fondo(ctx, "#c9a46a", 1330, "#7a5a34")
    for i in range(3):
        piece(ctx, P_rect(100 + i * 320, 560, 200, 260), hexc("#8ec5e8"), lw=4, shadow=False)
    silueta(ctx, 250, 1230, 1.05, pose)
    silueta(ctx, 830, 1230, 1.05, pose, 3)
    piece(ctx, P_rect(120, 1160, 840, 60), hexc("#5a3820"), lw=5)
    piece(ctx, P_rect(120, 1220, 840, 110), hexc("#3d2614"), lw=4, shadow=False)
    marco(ctx, 440, 900, 200, 260, retrato, borde=22)
    piece(ctx, P_rrect(150, 830, 200, 70, 12), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "VENDEDOR", 250, 878, 30, INK, anchor="center")
    piece(ctx, P_rrect(720, 830, 220, 70, 12), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "MARCHANTE", 830, 878, 30, INK, anchor="center")
    ta = since(ev, "avisa", lt)
    if ta >= 0:
        stamp(ctx, 540, 700, "¡DETENIDO!", ta - 0.4, 64, col=ROJO, ang=-8)


def sc_fama(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", 1330, "#1d2440")
    marco(ctx, 380, 620, 320, 440, retrato, borde=32)
    tr = since(ev, "robo", lt)
    if tr < 0:
        stamp(ctx, 540, 1180, "POCO CONOCIDA", lt - 0.4, 50, col=hexc("#9aa0ab"), ang=-4)
    else:
        n = int(clamp(tr / 1.6) * 6)
        pos = [(180, 700), (900, 720), (170, 1040), (910, 1060), (300, 1250), (780, 1250)]
        for i in range(n):
            x, y = pos[i]
            with rot(ctx, x, y, math.radians(-10 + i * 5)):
                piece(ctx, P_rect(x - 130, y - 85, 260, 170), hexc("#f3f1ea"), lw=4)
                txt(ctx, "¡ROBADA!", x, y - 30, 40, INK, anchor="center")
                for j in range(3):
                    line(ctx, [(x - 100, y + 10 + j * 22), (x + 100, y + 10 + j * 22)], 5, hexc("#9aa0ab"))
        if (pose // 2) % 3 == 0:
            for (fx, fy) in ((260, 600), (820, 620)):
                piece(ctx, P_poly([(fx, fy - 50), (fx + 15, fy - 15), (fx + 50, fy), (fx + 15, fy + 15), (fx, fy + 50),
                                   (fx - 15, fy + 15), (fx - 50, fy), (fx - 15, fy - 15)]), (1, 1, 1), lw=2,
                      shadow=False)


SCENES = dict(cuadro=sc_cuadro, brazo=sc_brazo, armario=sc_armario, descuelga=sc_descuelga, hueco=sc_hueco,
              interrogatorio=sc_interrogatorio, baul=sc_baul, venta=sc_venta, fama=sc_fama)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_brazo(ctx, 0, 1.2, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(47))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ROBÓ LA MONA LISA", 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "BAJO EL BRAZO", 540, 380, 104, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y LA HIZO FAMOSA!", 540, 1690, 100, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
