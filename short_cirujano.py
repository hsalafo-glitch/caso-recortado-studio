#!/usr/bin/env python3
"""
Short 7 · «Operó en un barco de guerra… sin ser médico» — caso real + dato impactante
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_cirujano.py            # vídeo final (usa cache_audio/falso-cirujano/)
    python short_cirujano.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, since, stamp, txt
from short_mentiras import persona_a

SLUG = "falso-cirujano"

BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina que el cirujano que te opera nunca ha estudiado Medicina. Y aun así, sales vivo.",
        escenas=[(None, "quirofano")],
        pantalla=[("nunca ha", "¿Y SI NO ES MÉDICO?")],
        eventos={"nunca": "nunca ha", "vivo": "sales vivo"},
    ),
    dict(
        id="caso",
        voz=("1951. Ferdinand Demara consigue los papeles de un médico de verdad y entra en la Marina de "
             "Canadá como cirujano. Le destinan a un buque de guerra en Corea."),
        escenas=[(None, "papeles"), ("Le destinan", "barco")],
        pantalla=[(None, "1951"), ("como cirujano", "«CIRUJANO» FALSO"), ("Le destinan", "RUMBO A COREA")],
        eventos={"papeles": "los papeles", "marina": "la Marina"},
    ),
    dict(
        id="giro",
        voz=("Un día llegan soldados heridos. Demara se encierra con un libro de cirugía, lo lee a toda prisa… "
             "y opera. Según las crónicas, sus pacientes sobreviven."),
        escenas=[(None, "camillas"), ("se encierra", "libro"), ("y opera", "operando")],
        pantalla=[("se encierra", "MANUAL EXPRÉS"), ("pacientes sobreviven", "¡SOBREVIVEN!")],
        eventos={"sobreviven": "pacientes sobreviven"},
    ),
    dict(
        id="pillado",
        voz=("Le pillan por su propia fama: los periódicos cuentan la hazaña y la madre del médico auténtico "
             "la lee. Antes ya había sido monje y profesor con otros nombres."),
        escenas=[(None, "periodico"), ("Antes ya", "disfraces")],
        pantalla=[(None, "PILLADO POR SU FAMA"), ("Antes ya", "MONJE, PROFESOR…")],
        eventos={"madre": "la madre", "monje": "monje", "profesor": "profesor", "nombres": "otros nombres"},
    ),
    dict(
        id="cierre",
        voz="Un título y un uniforme hacen que nadie pregunte. ¿Tú le habrías pedido el diploma?",
        escenas=[(None, "confianza")],
        pantalla=[(None, "TÍTULO +"), ("un uniforme", "UNIFORME ="), ("nadie pregunte", "CONFIANZA")],
        modo_pantalla="pila",
        eventos={"pregunta": "Tú le"},
    ),
]

RECORTES = ["Bloque 4: «Antes ya había sido monje y profesor con otros nombres.» (≈3 s)"]

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")


# ─────────────────────────────── piezas ───────────────────────────────
def impostor(ctx, x, feet, s=1.0, tilt=0.0, gorro=None, bata=None):
    """Silueta sin rasgos (persona real). gorro: 'quirofano' | 'marina' | 'monje' | None."""
    silhouette(ctx, x, feet, s, tilt, SOMBRA, BORDE)
    hy = feet - 230 * s - 72 * s * 0.9
    r = 72 * s
    with rot(ctx, x, feet - 230 * s, tilt):
        if gorro == "quirofano":
            piece(ctx, P_poly([(x - r * 1.05, hy - r * 0.2), (x + r * 1.05, hy - r * 0.2), (x + r * 0.8, hy - r * 1.05),
                               (x - r * 0.8, hy - r * 1.05)]), hexc("#2f9e8f"), lw=4, shadow=False)
            piece(ctx, P_rrect(x - r * 0.75, hy + r * 0.15, r * 1.5, r * 0.6, r * 0.2), hexc("#bfe3dc"), lw=3,
                  shadow=False)
        elif gorro == "marina":
            piece(ctx, P_poly([(x - r * 0.95, hy - r * 0.55), (x + r * 0.95, hy - r * 0.55), (x + r * 1.1, hy - r * 1.15),
                               (x - r * 1.1, hy - r * 1.15)]), (1, 1, 1), lw=4, shadow=False)
            piece(ctx, P_rect(x - r * 0.95, hy - r * 0.62, r * 1.9, r * 0.18), INK, lw=3, shadow=False)
            piece(ctx, P_ell(x, hy - r * 0.85, r * 0.17), hexc("#f2c94c"), lw=3, shadow=False)
    if bata:
        piece(ctx, P_poly([(x - 52 * s, feet - 230 * s), (x + 52 * s, feet - 230 * s), (x + 74 * s, feet - 30 * s),
                           (x - 74 * s, feet - 30 * s)]), hexc(bata), lw=4, shadow=False)


def paciente(ctx, x, y, w=420, ok=-1.0, pose=0):
    """Camilla con paciente tapado hasta el cuello (sin heridas visibles)."""
    piece(ctx, P_rect(x - w / 2, y + 40, w, 26), hexc("#9aa3ad"), lw=4)
    for dx in (-w / 2 + 20, w / 2 - 40):
        piece(ctx, P_rect(x + dx, y + 66, 20, 120), hexc("#6b6f78"), lw=3)
    piece(ctx, P_rrect(x - w / 2 + 10, y - 30, w - 20, 80, 30), hexc("#e8f1f5"), lw=4)
    piece(ctx, P_ell(x - w / 2 + 60, y - 30, 48, 44), hexc("#e8b896"), lw=4)
    for dx in (-14, 14):
        ctx.new_sub_path()
        ctx.arc(x - w / 2 + 60 + dx, y - 34, 9, math.radians(20), math.radians(160))
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
    if ok >= 0:
        k = ease_out_back(clamp(ok / 0.3)) if ok < 0.3 else 1.0
        piece(ctx, P_ell(x + w / 2 - 50, y - 90, 46 * k), hexc("#2fb35a"), lw=4)
        if k >= 1:
            line(ctx, [(x + w / 2 - 72, y - 90), (x + w / 2 - 54, y - 70), (x + w / 2 - 26, y - 108)], 10, (1, 1, 1))


def monitor(ctx, x, y, pose, vivo=True):
    piece(ctx, P_rrect(x - 130, y - 90, 260, 180, 16), hexc("#2d2f3a"), lw=5)
    piece(ctx, P_rect(x - 110, y - 70, 220, 120), hexc("#0f2a1e"), lw=3, shadow=False)
    pts = []
    off = (pose * 18) % 220
    for i in range(23):
        xx = x - 110 + i * 10
        ph = (i * 10 + off) % 110
        yy = y - 10 - (50 if vivo and 46 <= ph < 54 else (-20 if vivo and 54 <= ph < 60 else 0))
        pts.append((xx, yy))
    line(ctx, pts, 5, hexc("#3cff8a"))
    line(ctx, [(x, y + 90), (x, y + 260)], 10, hexc("#6b6f78"))


def barco(ctx, cx, wy, pose):
    bob = 6 if (pose // 4) % 2 else 0
    y = wy + bob
    piece(ctx, P_poly([(cx - 470, y - 120), (cx + 470, y - 160), (cx + 400, y + 20), (cx - 420, y + 20)]),
          hexc("#7d838f"), lw=5)
    piece(ctx, P_rect(cx - 200, y - 260, 300, 140), hexc("#9aa0ab"), lw=5)
    piece(ctx, P_rect(cx - 140, y - 360, 160, 100), hexc("#9aa0ab"), lw=5)
    for k in range(4):
        piece(ctx, P_rect(cx - 180 + k * 70, y - 230, 36, 30), hexc("#bfe3f2"), lw=3, shadow=False)
    line(ctx, [(cx - 60, y - 360), (cx - 60, y - 520)], 8, INK)
    line(ctx, [(cx - 120, y - 470), (cx, y - 470)], 6, INK)
    piece(ctx, P_rrect(cx + 160, y - 220, 140, 70, 10), hexc("#e8f1f5"), lw=4)
    draw_text(ctx, "+", cx + 230, y - 186, 70, hexc("#e23b3b"), INK, 0)
    piece(ctx, P_rect(cx + 330, y - 220, 50, 70), hexc("#9aa0ab"), lw=4)


def olas(ctx, y, pose, col):
    off = (pose * 14) % 160
    ctx.move_to(-20, y)
    for i in range(-1, 9):
        x = i * 160 - off
        ctx.curve_to(x + 40, y - 40, x + 120, y - 40, x + 160, y)
    ctx.line_to(1100, 1940)
    ctx.line_to(-20, 1940)
    ctx.close_path()
    set_col(ctx, col)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()


def quirofano_bg(ctx):
    set_col(ctx, hexc("#9fd3c7"))
    ctx.paint()
    for i in range(12):
        line(ctx, [(0, i * 110), (1080, i * 110)], 2, (0, 0, 0, 0.06))
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#6f8f8a"), lw=4, shadow=False)
    line(ctx, [(540, 0), (540, 420)], 8, hexc("#6b6f78"))
    piece(ctx, P_ell(540, 470, 190, 70), hexc("#d6dce6"), lw=5)
    piece(ctx, P_ell(540, 470, 130, 40), hexc("#fff8d6"), lw=3, shadow=False)
    ctx.move_to(400, 500)
    ctx.line_to(680, 500)
    ctx.line_to(900, 1200)
    ctx.line_to(180, 1200)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 0.9, 0.18)
    ctx.fill()


# ─────────────────────────────── escenas ───────────────────────────────
def sc_quirofano(ctx, pose, lt, ev):
    quirofano_bg(ctx)
    # diploma en la pared: se rompe en «nunca ha estudiado»
    tn = since(ev, "nunca", lt)
    k = ease_io(clamp(tn / 0.4)) if tn >= 0 else 0.0
    for side in (-1, 1):
        dx = side * 40 * k
        with rot(ctx, 850 + side * 60, 700, math.radians(side * 14 * k)):
            ctx.save()
            ctx.rectangle(850 + (0 if side > 0 else -200), 560, 200, 300)
            ctx.clip()
            ctx.translate(dx, 30 * k)
            piece(ctx, P_rect(730, 600, 240, 190), hexc("#f6eab0"), lw=5)
            draw_text(ctx, "DIPLOMA", 850, 640, 34, INK, INK, 0)
            for j in range(3):
                line(ctx, [(760, 680 + j * 28), (940, 680 + j * 28)], 4, (0, 0, 0, 0.3))
            piece(ctx, P_ell(910, 760, 20), hexc("#c62828"), lw=3, shadow=False)
            ctx.restore()
    if k > 0:
        line(ctx, [(850, 590), (838, 650), (858, 700), (842, 800)], 5, INK)
    paciente(ctx, 470, 1130, 520)
    impostor(ctx, 540, 1300, 1.15, math.radians(2) * (1 if (pose // 6) % 2 else -1), "quirofano", "#2f9e8f")
    piece(ctx, P_rect(160, 1180, 760, 30), hexc("#d6dce6"), lw=4)
    tv = since(ev, "vivo", lt)
    monitor(ctx, 190, 760, pose, vivo=True)
    if tv >= 0:
        stamp(ctx, 220, 600, "¡VIVO!", tv, 50, col=hexc("#2fb35a"), ang=-8)


def sc_papeles(ctx, pose, lt, ev):
    set_col(ctx, hexc("#e9dcc0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#b89c74"), lw=4, shadow=False)
    tp, tm = since(ev, "papeles", lt), since(ev, "marina", lt)
    # médico auténtico (silueta clara) y el impostor
    silhouette(ctx, 230, 1330, 1.1, 0.0, hexc("#c9ced8"), hexc("#ffffff"))
    impostor(ctx, 800, 1330, 1.15, math.radians(2) * (1 if (pose // 6) % 2 else -1),
             "marina" if tm >= 0 else None, "#1f2a44" if tm >= 0 else None)
    if tp >= 0:
        k = ease_io(clamp(tp / 0.8))
        x = lerp(330, 640, k)
        y = 1020 - math.sin(k * math.pi) * 160
        with rot(ctx, x, y, math.radians(-8 + 16 * k)):
            piece(ctx, P_rect(x - 120, y - 80, 240, 160), (1, 1, 1), lw=4)
            piece(ctx, P_rect(x - 100, y - 60, 60, 70), hexc("#d6dce6"), lw=3, shadow=False)
            draw_text(ctx, "DR.", x + 40, y - 34, 34, INK, INK, 0)
            line(ctx, [(x - 20, y + 30), (x + 100, y + 30)], 4, (0, 0, 0, 0.35))
            line(ctx, [(x - 100, y + 56), (x + 100, y + 56)], 4, (0, 0, 0, 0.35))


def sc_barco(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    for cx, cy in ((240, 640), (820, 560)):
        for dxx, r in ((-50, 45), (0, 60), (50, 45)):
            piece(ctx, P_ell(cx + dxx + (pose // 6) * 2, cy, r, r * 0.8), (1, 1, 1), lw=3, shadow=False)
    olas(ctx, 1180, pose + 6, hexc("#2f6fb0"))
    barco(ctx, 560, 1170, pose)
    olas(ctx, 1260, pose, hexc("#1d4e8a"))


def sc_camillas(ctx, pose, lt, ev):
    set_col(ctx, hexc("#c9d6c2"))
    ctx.paint()
    for i in range(5):
        piece(ctx, P_ell(140 + i * 200, 400, 40), hexc("#9aa0ab"), lw=4, shadow=False)
        piece(ctx, P_ell(140 + i * 200, 400, 24), hexc("#bfe3f2"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#7d838f"), lw=4, shadow=False)
    sway = math.radians(3) * (1 if (pose // 6) % 2 else -1)
    with rot(ctx, 540, 0, sway):
        line(ctx, [(540, 0), (540, 520)], 6)
        piece(ctx, P_poly([(500, 520), (580, 520), (620, 580), (460, 580)]), hexc("#3a3d48"), lw=4)
    paciente(ctx, 300, 860, 420)
    paciente(ctx, 760, 1160, 420)
    piece(ctx, P_rrect(620, 650, 320, 120, 16), hexc("#e8f1f5"), lw=5)
    draw_text(ctx, "ENFERMERÍA", 780, 710, 40, hexc("#c62828"), INK, 0)


def sc_libro(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1200, 1100, 760), hexc("#5d3a22"), lw=4, shadow=False)
    impostor(ctx, 540, 1260, 1.0, math.radians(-4), "marina", "#1f2a44")
    # libro grande sobre la mesa
    cx, cy = 540, 1150
    piece(ctx, P_rect(cx - 340, cy - 40, 680, 230), hexc("#6b3a1f"), lw=5)
    piece(ctx, P_rect(cx - 320, cy - 30, 300, 200), (1, 1, 1), lw=4, shadow=False)
    piece(ctx, P_rect(cx + 20, cy - 30, 300, 200), (1, 1, 1), lw=4, shadow=False)
    draw_text(ctx, "CIRUGÍA", cx - 170, cy + 20, 46, INK, INK, 0)
    for j in range(3):
        line(ctx, [(cx - 290, cy + 70 + j * 30), (cx - 50, cy + 70 + j * 30)], 4, (0, 0, 0, 0.3))
    # páginas volando
    for k in range(3):
        p = ((lt * 3 + k / 3) % 1.0)
        with rot(ctx, cx + 170, cy + 70, -p * math.pi):
            piece(ctx, P_rect(cx + 20, cy - 30, 300, 200), hexc("#f6f1e2"), lw=3, shadow=False)
    draw_text(ctx, "¡RÁPIDO!", 820, 760, 60, hexc("#ffe14d"), INK, 6) if (pose // 3) % 2 == 0 else None


def sc_operando(ctx, pose, lt, ev):
    quirofano_bg(ctx)
    ts = since(ev, "sobreviven", lt)
    paciente(ctx, 300, 900, 420, ts, pose)
    paciente(ctx, 780, 1150, 420, ts - 0.3 if ts >= 0 else -1, pose)
    impostor(ctx, 560, 1320, 0.95, math.radians(3) * (1 if (pose // 4) % 2 else -1), "quirofano", "#2f9e8f")
    monitor(ctx, 880, 650, pose)


def sc_periodico(ctx, pose, lt, ev):
    set_col(ctx, hexc("#d9cfbd"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1350, 1100, 600), hexc("#8b7d6b"), lw=4, shadow=False)
    tm = since(ev, "madre", lt)
    k = max(0.05, ease_out_back(clamp(lt / 0.35))) if lt < 0.35 else 1.0
    with rot(ctx, 540, 900, math.radians(-4 + 360 * (1 - k) / 6)):
        ctx.save()
        ctx.translate(540, 900)
        ctx.scale(k, k)
        ctx.translate(-540, -900)
        piece(ctx, P_rect(160, 560, 760, 660), hexc("#f6f1e2"), lw=6, sh=(10, 14))
        draw_text(ctx, "EL DIARIO", 540, 620, 50, INK, INK, 0)
        line(ctx, [(190, 660), (890, 660)], 5)
        draw_text(ctx, "¡HÉROE A BORDO!", 540, 730, 64, hexc("#c62828"), INK, 0)
        piece(ctx, P_rect(200, 800, 300, 330), hexc("#d6dce6"), lw=4, shadow=False)
        ctx.save()
        P_rect(200, 800, 300, 330)(ctx)
        ctx.clip()
        impostor(ctx, 350, 1150, 0.95, 0.0, "marina", "#1f2a44")
        ctx.restore()
        for j in range(8):
            line(ctx, [(530, 820 + j * 38), (880 - 40 * (j % 3), 820 + j * 38)], 5, (0, 0, 0, 0.3))
        ctx.restore()
    if tm >= 0:
        # la madre del médico auténtico: silueta con moño, sin rasgos
        x = 860
        silhouette(ctx, x, 1360, 0.9, 0.0, hexc("#4a3f66"), hexc("#a99ad6"))
        piece(ctx, P_ell(x, 1360 - 230 * 0.9 - 72 * 0.9 * 1.9, 30), hexc("#4a3f66"), lw=4, shadow=False)
        draw_text(ctx, "?!", x + 40, 1040 - (6 if pose % 2 else 0), 110, hexc("#ffe14d"), INK, 7)


def percha(ctx, x, y, ropa, etiqueta, k, pose):
    if k < 0:
        return
    sc = max(0.05, ease_out_back(clamp(k / 0.3))) if k < 0.3 else 1.0
    sw = math.radians(3) * (1 if (pose // 5) % 2 else -1)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.rotate(sw)
    line(ctx, [(0, -30), (0, 0)], 5)
    line(ctx, [(-90, 40), (0, 0), (90, 40)], 6)
    ropa(ctx)
    ctx.restore()
    draw_text(ctx, etiqueta, x, y + 470, 40, (1, 1, 1), INK, 5)


def sc_disfraces(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3b2f6b"))
    ctx.paint()
    line(ctx, [(60, 620), (1020, 620)], 14, hexc("#9aa0ab"))
    tm, tp, tn = since(ev, "monje", lt), since(ev, "profesor", lt), since(ev, "nombres", lt)

    def monje(c):
        piece(c, P_poly([(-100, 40), (100, 40), (140, 420), (-140, 420)]), hexc("#7a4e2c"), lw=5)
        piece(c, P_poly([(-70, 40), (70, 40), (40, 110), (-40, 110)]), hexc("#5d3a22"), lw=4, shadow=False)
        line(c, [(-110, 260), (110, 260)], 8, hexc("#f2c94c"))

    def profesor(c):
        piece(c, P_poly([(-110, 40), (110, 40), (130, 400), (-130, 400)]), hexc("#8a6a3a"), lw=5)
        piece(c, P_poly([(-40, 40), (40, 40), (0, 160)]), (1, 1, 1), lw=3, shadow=False)
        piece(c, P_rect(30, 200, 70, 90), hexc("#e63946"), lw=3, shadow=False)

    def cirujano(c):
        piece(c, P_poly([(-110, 40), (110, 40), (130, 410), (-130, 410)]), hexc("#2f9e8f"), lw=5)
        piece(c, P_poly([(-40, 40), (40, 40), (0, 120)]), hexc("#bfe3dc"), lw=3, shadow=False)

    percha(ctx, 200, 640, monje, "MONJE", tm, pose)
    percha(ctx, 540, 640, profesor, "PROFESOR", tp, pose)
    percha(ctx, 880, 640, cirujano, "CIRUJANO", tp - 0.4 if tp >= 0 else -1, pose)
    if tn >= 0:
        for i, (x, nom) in enumerate(((200, "¿?"), (540, "¿?"), (880, "¿?"))):
            stamp(ctx, x, 1230, "¿NOMBRE?", tn - i * 0.2, 44, col=hexc("#e23b3b"), ang=-6 + i * 6)


def sc_confianza(ctx, pose, lt, ev):
    quirofano_bg(ctx)
    impostor(ctx, 760, 1330, 1.15, math.radians(2) * (1 if (pose // 6) % 2 else -1), "marina", "#1f2a44")
    # marco con diploma a su lado
    piece(ctx, P_rect(820, 820, 200, 150), hexc("#f6eab0"), lw=5)
    draw_text(ctx, "DIPLOMA", 920, 860, 30, INK, INK, 0)
    persona_a(ctx, 290, 1000, 100, "preocupado", 1.0, pose=pose)
    piece(ctx, P_rect(160, 1320, 260, 20), hexc("#6f8f8a"), lw=0, shadow=False, outline=False)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bubble(ctx, 400, 800, 520, 160, (320, 900), ["¿ME ENSEÑA", "EL DIPLOMA?"], 48, col=hexc("#ffe14d"))


SCENES = dict(quirofano=sc_quirofano, papeles=sc_papeles, barco=sc_barco, camillas=sc_camillas, libro=sc_libro,
              operando=sc_operando, periodico=sc_periodico, disfraces=sc_disfraces, confianza=sc_confianza)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_quirofano(ctx, 0, 1.0, {"nunca_lt": 0.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(23))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "OPERÓ EN UN", 540, 220, 120, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "BARCO DE GUERRA", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "SIN SER MÉDICO", 540, 1620, 120, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
    surf.write_to_png(path)


def configurar():
    g.BLOQUES[:] = BLOQUES
    g.SCENES.clear()
    g.SCENES.update(SCENES)
    g.RECORTES_SUGERIDOS[:] = RECORTES
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
