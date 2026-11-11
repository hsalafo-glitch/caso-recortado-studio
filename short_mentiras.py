#!/usr/bin/env python3
"""
Short 4 · «Uno de estos dos miente (y no vas a saber cuál)»
Motor: generar_short.py · utilidades: generar_short_estafas.py y short_obediencia.py · voz Salva (eleven_v4)

Uso:
    python short_mentiras.py            # vídeo final (usa cache_audio/mentiras/)
    python short_mentiras.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)
from generar_short_estafas import bubble, burst, since, stamp, txt
from short_obediencia import SKIN, adulto, face

SLUG = "mentiras"

# ─────────────────────────────── guion (versión recortada aprobada) ───────────────────────────────
BLOQUES = [
    dict(
        id="gancho",
        voz="Uno de estos dos te está mintiendo. Tienes tres segundos para adivinar cuál.",
        escenas=[(None, "duelo")],
        pantalla=[("adivinar cuál", "¿CUÁL MIENTE?")],
        eventos={"cuenta": "Tienes tres segundos"},
    ),
    dict(
        id="moneda",
        voz="¿Ya? Da igual lo que elegiste: era como tirar una moneda.",
        escenas=[(None, "moneda")],
        pantalla=[("tirar una moneda", "50/50")],
        eventos={"igual": "Da igual", "moneda": "tirar una moneda"},
    ),
    dict(
        id="estudios",
        voz=("En 2006 se juntaron más de 200 estudios sobre cazar mentiras. Acierto medio: 54%. "
             "Y policías, jueces y aduaneros apenas lo hacían mejor."),
        escenas=[(None, "papeles"), ("Acierto medio", "barra"), ("Y policías", "profesionales")],
        pantalla=[(None, "+200 ESTUDIOS"), ("Acierto medio", "ACIERTO: 54%"),
                  ("Y policías", "LOS EXPERTOS, IGUAL")],
        eventos={},
    ),
    dict(
        id="mitos",
        voz=("¿Y los trucos de película? Mirar arriba, tocarse la nariz, esquivar tu mirada… "
             "Se ha comprobado que los ojos no delatan nada. "
             "Y los nervios tampoco: un inocente también suda si le acusan."),
        escenas=[(None, "claqueta"), ("Mirar arriba", "mitos"), ("Y los nervios", "foco")],
        pantalla=[(None, "¿FUNCIONAN?"), ("Se ha comprobado", "MITOS"), ("un inocente", "NERVIOS ≠ MENTIRA")],
        eventos={"nariz": "tocarse la nariz", "mirada": "esquivar tu mirada", "comprobado": "Se ha comprobado"},
    ),
    dict(
        id="reves",
        voz=("Lo que funciona es atacar la historia, no el cuerpo: pide que te lo cuente al revés. "
             "Quien dice la verdad lo recuerda; quien miente tiene que inventarlo dos veces, "
             "y ahí se contradice."),
        escenas=[(None, "rebobinar"), ("Quien dice", "historias")],
        pantalla=[("al revés", "PIDE QUE LO CUENTE AL REVÉS")],
        eventos={"recuerda": "lo recuerda", "miente": "quien miente", "dos": "dos veces",
                 "contradice": "se contradice"},
    ),
    dict(
        id="cierre",
        voz="Pruébalo con tu amigo más mentiroso y cuéntame qué pasa.",
        escenas=[(None, "huida")],
        pantalla=[(None, "ETIQUETA AL MÁS MENTIROSO")],
        eventos={},
    ),
]

RECORTES = ["Bloque 4: «esquivar tu mirada» (≈1 s)", "Bloque 3: «apenas» (≈0,4 s)"]

ROJO = hexc("#e8574a")


# ─────────────────────────────── personajes ───────────────────────────────
def persona_a(ctx, x, y, r=110, expr="neutro", look=0.0, sudor=False, pose=0, skin=SKIN, droop=0.0):
    """A: melena corta castaña, jersey verde."""
    with rot(ctx, x, y + r * 0.9, droop):
        piece(ctx, P_rrect(x - r * 1.18, y - r * 0.9, r * 2.36, r * 1.95, r * 0.7), hexc("#7a3b1e"), lw=4.5)
    adulto(ctx, x, y, r, traje="#2f8f5b", pelo="#7a3b1e", expr=expr, look=look, sudor=sudor, pose=pose,
           skin=skin, droop=droop)


def persona_b(ctx, x, y, r=110, expr="neutro", look=0.0, sudor=False, pose=0, skin=None, droop=0.0):
    """B: pelo negro, gafas, chaqueta azul."""
    adulto(ctx, x, y, r, traje="#2c4479", pelo="#1f1a1a", expr=expr, look=look, gafas=True, sudor=sudor,
           pose=pose, skin=skin if skin is not None else hexc("#d9a77c"), droop=droop)


def encoge(ctx, x, y, r, skin=SKIN, col="#2f8f5b"):
    """Brazos encogiéndose de hombros (palmas arriba)."""
    for side in (-1, 1):
        sx, sy = x + side * r * 0.95, y + r * 1.25
        with rot(ctx, sx, sy, math.radians(-side * 125)):
            piece(ctx, P_rrect(sx - r * 0.17, sy, r * 0.34, r * 0.95, r * 0.15), hexc(col), lw=4)
        ex, ey = sx + side * r * 0.78, sy - r * 0.55
        piece(ctx, P_ell(ex, ey, r * 0.22, r * 0.16), skin, lw=4)


def etiqueta(ctx, x, y, letra, col):
    piece(ctx, P_rrect(x - 60, y - 50, 120, 100, 18), col, lw=5)
    draw_text(ctx, letra, x, y, 80, (1, 1, 1), INK, 6)


def coin(ctx, cx, cy, r, phase, label="?"):
    w = abs(math.cos(phase))
    piece(ctx, P_ell(cx, cy, max(10, r * w), r), hexc("#f2c94c"), lw=5)
    if w > 0.35:
        piece(ctx, P_ell(cx, cy, max(6, r * w * 0.78), r * 0.78), hexc("#e0b13a"), lw=3, shadow=False)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(w, 1)
        draw_text(ctx, label, 0, 0, r * 0.9, hexc("#8a6a12"), INK, 0)
        ctx.restore()


def escenario(ctx, pose, color="#211a3a"):
    set_col(ctx, hexc(color))
    ctx.paint()
    for cx in (300, 780):
        ctx.move_to(cx - 40, -10)
        ctx.line_to(cx + 40, -10)
        ctx.line_to(cx + 260, 1300)
        ctx.line_to(cx - 260, 1300)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.93, 0.7, 0.11)
        ctx.fill()
    piece(ctx, P_rect(-10, 1290, 1100, 650), hexc("#151026"), lw=4, shadow=False)
    for cx in (300, 780):
        piece(ctx, P_ell(cx, 1290, 220, 40), (1, 0.93, 0.7, 0.16), shadow=False, outline=False)


def pareja(ctx, pose, ea="neutro", eb="neutro", la=0.0, lb=0.0, xb=780, skin_b=None, sb=False):
    persona_a(ctx, 300, 880, 110, ea, la, pose=pose, droop=math.radians(2) * (1 if (pose // 6) % 2 else -1))
    persona_b(ctx, xb, 880, 110, eb, lb, sudor=sb, pose=pose,
              skin=skin_b if skin_b is not None else hexc("#d9a77c"),
              droop=math.radians(2) * (-1 if (pose // 6) % 2 else 1))


# ─────────────────────────────── escenas ───────────────────────────────
def sc_duelo(ctx, pose, lt, ev):
    escenario(ctx, pose)
    pareja(ctx, pose, la=0.0, lb=0.0)
    etiqueta(ctx, 300, 1360, "A", hexc("#2f8f5b"))
    etiqueta(ctx, 780, 1360, "B", hexc("#2c4479"))
    tc = since(ev, "cuenta", lt)
    if tc >= 0:
        resto = max(0.6, ev.get("dur", 4) - ev.get("cuenta_lt", 0))
        n = 3 - min(2, int(tc / (resto / 3)))
        k = (tc % (resto / 3)) / 0.25
        sc = ease_out_back(clamp(k)) if k < 1 else 1.0
        ctx.save()
        ctx.translate(540, 620)
        ctx.scale(sc, sc)
        piece(ctx, P_ell(0, 0, 120), (1, 1, 1), lw=7, sh=(10, 12))
        draw_text(ctx, str(n), 0, 6, 190, hexc("#e23b3b"), INK, 7)
        ctx.restore()


def sc_moneda(ctx, pose, lt, ev):
    escenario(ctx, pose)
    ti = since(ev, "igual", lt)
    pareja(ctx, pose, "sonrisa" if ti >= 0 else "neutro", "sonrisa" if ti >= 0 else "neutro")
    if ti >= 0:
        encoge(ctx, 300, 880, 110, SKIN, "#2f8f5b")
        encoge(ctx, 780, 880, 110, hexc("#d9a77c"), "#2c4479")
    k = clamp(lt / 0.6)
    cy = lerp(-200, 1040, ease_io(k))
    if k >= 1:
        cy += (6 if pose % 2 else -6)
    coin(ctx, 540, cy, 120, pose * 0.7, "€")
    etiqueta(ctx, 300, 1360, "A", hexc("#2f8f5b"))
    etiqueta(ctx, 780, 1360, "B", hexc("#2c4479"))


def sc_papeles(ctx, pose, lt, ev):
    set_col(ctx, hexc("#e9dcc0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#b89c74"), lw=4, shadow=False)
    n = min(46, 14 + int(lt * 10))
    for i in range(n):
        row = i // 6
        x = 300 + (i % 6) * 90 - row * 6 + (hnoise("p", i) - 0.5) * 40
        y = 1300 - row * 46
        if row > 4:
            x = 420 + (i % 6) * 40 + (hnoise("p2", i) - 0.5) * 30
        with rot(ctx, x, y, math.radians((hnoise("a", i) - 0.5) * 18)):
            piece(ctx, P_rect(x - 80, y - 26, 160, 52), (1, 1, 1) if i % 3 else hexc("#f6eab0"), lw=3,
                  sh=(3, 4))
            line(ctx, [(x - 60, y - 6), (x + 50, y - 6)], 3, (0, 0, 0, 0.25))
            line(ctx, [(x - 60, y + 8), (x + 30, y + 8)], 3, (0, 0, 0, 0.25))
    # hoja que cae
    p = (lt * 1.5) % 1.0
    with rot(ctx, 640, 500 + p * 500, p * 5):
        piece(ctx, P_rect(560, 470 + p * 500, 160, 60), (1, 1, 1), lw=3)
    piece(ctx, P_rect(150, 680, 14, 640), hexc("#6b4a2b"), lw=3)
    with rot(ctx, 157, 700, math.radians(-4)):
        piece(ctx, P_rrect(40, 620, 300, 130, 14), hexc("#e63946"), lw=5)
        draw_text(ctx, "+200", 190, 662, 56, (1, 1, 1), INK, 5)
        draw_text(ctx, "ESTUDIOS", 190, 716, 40, (1, 1, 1), INK, 4)


def sc_barra(ctx, pose, lt, ev):
    set_col(ctx, hexc("#1d2a52"))
    ctx.paint()
    v = 0.54 * ease_io(clamp(lt / 1.4))
    x0, y0, w, h = 110, 820, 860, 140
    piece(ctx, P_rrect(x0, y0, w, h, 40), hexc("#f6f1e2"), lw=7)
    ctx.save()
    P_rrect(x0 + 12, y0 + 12, w - 24, h - 24, 30)(ctx)
    ctx.clip()
    piece(ctx, P_rect(x0 + 12, y0 + 12, (w - 24) * v, h - 24), hexc("#f2b632"), lw=0, shadow=False,
          outline=False)
    for i in range(0, 30):
        line(ctx, [(x0 + i * 40, y0 + 12), (x0 + i * 40 - 40, y0 + h)], 8, (1, 1, 1, 0.2))
    ctx.restore()
    xm = x0 + 12 + (w - 24) * 0.5
    line(ctx, [(xm, y0 - 40), (xm, y0 + h + 40)], 6, (1, 1, 1))
    draw_text(ctx, "MONEDA: 50%", xm, y0 + h + 90, 40, (1, 1, 1), INK, 5)
    draw_text(ctx, f"{int(round(v * 100))} %", 540, 680, 150, hexc("#f2b632"), INK, 9)
    if v >= 0.539:
        coin(ctx, 540, 1250, 90, pose * 0.7, "€")


def gorra(ctx, x, y, r, col, visera=INK):
    piece(ctx, P_poly([(x - r * 0.95, y - r * 0.55), (x + r * 0.95, y - r * 0.55), (x + r * 1.05, y - r * 1.15),
                       (x - r * 1.05, y - r * 1.15)]), hexc(col), lw=4, shadow=False)
    piece(ctx, P_poly([(x - r * 0.8, y - r * 0.5), (x + r * 1.0, y - r * 0.5), (x + r * 1.15, y - r * 0.36),
                       (x - r * 0.6, y - r * 0.4)]), visera, lw=3, shadow=False)
    piece(ctx, P_ell(x, y - r * 0.85, r * 0.16), hexc("#f2c94c"), lw=3, shadow=False)


def sc_profesionales(ctx, pose, lt, ev):
    set_col(ctx, hexc("#e9dcc0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 640), hexc("#b89c74"), lw=4, shadow=False)
    gente = [(190, "#23365e", "POLICÍA", "#23365e"), (540, "#161616", "JUEZA", None),
             (890, "#5d6b2f", "ADUANAS", "#4a5626")]
    for i, (x, traje, rotulo, cap) in enumerate(gente):
        r = 82
        y = 1000
        adulto(ctx, x, y, r, traje=traje, pelo="#4a3226" if i != 1 else "#8a8a8a", expr="preocupado",
               look=0.0, pose=pose, skin=SKIN if i != 2 else hexc("#c98b5e"))
        if i == 1:
            piece(ctx, P_poly([(x - r * 0.5, y + r * 0.85), (x + r * 0.5, y + r * 0.85), (x, y + r * 1.35)]),
                  (1, 1, 1), lw=3, shadow=False)
        if cap:
            gorra(ctx, x, y, r, cap)
        piece(ctx, P_rrect(x - 130, 1310, 260, 70, 12), hexc("#3d3f4a"), lw=4)
        draw_text(ctx, rotulo, x, 1345, 40, (1, 1, 1), INK, 0)
        coin(ctx, x, 760 - (pose % 4) * 10 if (pose + i) % 8 < 4 else 760, 64, pose * 0.8 + i * 1.3, "€")


def claqueta(ctx, cx, cy, s, ang):
    piece(ctx, P_rect(cx - 330 * s, cy - 110 * s, 660 * s, 380 * s), hexc("#2a2a30"), lw=6)
    for k in range(3):
        line(ctx, [(cx - 300 * s, cy + (20 + k * 80) * s), (cx + 300 * s, cy + (20 + k * 80) * s)], 4,
             (1, 1, 1, 0.6))
    draw_text(ctx, "TRUCOS DE", cx, cy + 50 * s, 70 * s, (1, 1, 1), INK, 0)
    draw_text(ctx, "PELÍCULA", cx, cy + 150 * s, 80 * s, hexc("#ffe14d"), INK, 0)
    with rot(ctx, cx - 330 * s, cy - 110 * s, ang):
        ctx.save()
        P_rect(cx - 330 * s, cy - 190 * s, 660 * s, 80 * s)(ctx)
        ctx.clip()
        set_col(ctx, (1, 1, 1))
        ctx.paint()
        for k in range(-1, 9):
            x = cx - 330 * s + k * 90 * s
            ctx.move_to(x, cy - 110 * s)
            ctx.line_to(x + 45 * s, cy - 110 * s)
            ctx.line_to(x + 85 * s, cy - 190 * s)
            ctx.line_to(x + 40 * s, cy - 190 * s)
            ctx.close_path()
            ctx.set_source_rgb(*INK)
            ctx.fill()
        ctx.restore()
        P_rect(cx - 330 * s, cy - 190 * s, 660 * s, 80 * s)(ctx)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()


def sc_claqueta(ctx, pose, lt, ev):
    burst(ctx, 540, 960, 20, hexc("#7c2d3a"), hexc("#8a3444"))
    ang = math.radians(-22) if (pose // 5) % 2 == 0 else 0.0
    claqueta(ctx, 540, 930, 1.2, ang)
    if ang == 0.0:
        draw_text(ctx, "¡CLAC!", 820, 640, 70, hexc("#ffe14d"), INK, 6)


def mito_card(ctx, y, k, dibujo, texto, tm):
    if k < 0:
        return
    x = lerp(1400, 540, ease_io(clamp(k / 0.3)))
    with rot(ctx, x, y, math.radians(-2 if y % 2 else 2)):
        piece(ctx, P_rrect(x - 440, y - 125, 880, 250, 26), (1, 1, 1), lw=5)
        dibujo(x - 250, y)
        draw_text(ctx, texto, x + 150, y, 46, INK, INK, 0)
        if tm >= 0:
            stamp(ctx, x + 300, y - 70, "MITO", tm, 52, ang=-10)


def sc_mitos(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    tn, tmi, tc = since(ev, "nariz", lt), since(ev, "mirada", lt), since(ev, "comprobado", lt)

    def ojo(x, y):
        piece(ctx, P_ell(x, y, 120, 70), (1, 1, 1), lw=5, shadow=False)
        piece(ctx, P_ell(x - 50, y - 28, 32), INK, shadow=False)
        line(ctx, [(x - 120, y - 70), (x - 10, y - 100), (x + 110, y - 80)], 8)
        line(ctx, [(x + 100, y + 40), (x + 40, y - 10)], 10, hexc("#e23b3b"))
        piece(ctx, P_poly([(x + 22, y - 28), (x + 66, y - 18), (x + 40, y + 12)]), hexc("#e23b3b"), lw=3, shadow=False)

    def nariz(x, y):
        piece(ctx, P_ell(x, y, 100, 100), SKIN, lw=5, shadow=False)
        face(ctx, x, y, 92, "preocupado", 0, 0.6)
        piece(ctx, P_ell(x + 40, y + 34, 34, 26), SKIN, lw=4, shadow=False)
        piece(ctx, P_rrect(x + 30, y + 20, 26, 90, 12), SKIN, lw=4, shadow=False)

    def mirada(x, y):
        piece(ctx, P_ell(x, y, 100, 100), hexc("#d9a77c"), lw=5, shadow=False)
        face(ctx, x, y, 92, "neutro", 0, -1.0)
        line(ctx, [(x - 120, y), (x - 180, y)], 10, hexc("#e23b3b"))
        piece(ctx, P_poly([(x - 200, y), (x - 170, y - 22), (x - 170, y + 22)]), hexc("#e23b3b"), lw=3, shadow=False)

    def tm(i):
        return tc - i * 0.3 if tc >= 0 else -1

    mito_card(ctx, 640, lt, ojo, "MIRAR ARRIBA", tm(0))
    mito_card(ctx, 940, tn, nariz, "TOCARSE LA NARIZ", tm(1))
    mito_card(ctx, 1240, tmi, mirada, "NO MIRARTE", tm(2))


def sc_foco(ctx, pose, lt, ev):
    set_col(ctx, hexc("#120f1c"))
    ctx.paint()
    ctx.move_to(470, -10)
    ctx.line_to(610, -10)
    ctx.line_to(900, 1350)
    ctx.line_to(180, 1350)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.7, 0.16)
    ctx.fill()
    piece(ctx, P_poly([(470, 300), (610, 300), (660, 400), (420, 400)]), hexc("#3a3d48"), lw=5)
    line(ctx, [(540, -10), (540, 300)], 6)
    piece(ctx, P_rect(-10, 1340, 1100, 600), hexc("#1d1830"), lw=4, shadow=False)
    persona_a(ctx, 540, 930, 120, "preocupado", 0.0, sudor=True, pose=pose)
    for i in range(4):
        dy = ((pose + i * 3) % 8) * 14
        sx = 540 + (-170 if i % 2 else 170) + (i // 2) * 20
        sy = 800 + i * 40 + dy
        piece(ctx, P_poly([(sx, sy - 26), (sx + 13, sy), (sx, sy + 10), (sx - 13, sy)]), hexc("#8fd3ff"), lw=3,
              shadow=False)
    piece(ctx, P_rrect(300, 1310, 480, 90, 16), hexc("#2f8f5b"), lw=5)
    draw_text(ctx, "INOCENTE", 540, 1355, 54, (1, 1, 1), INK, 0)


def sc_rebobinar(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3b2f6b"))
    ctx.paint()
    cx, cy = 540, 960
    piece(ctx, P_rrect(cx - 400, cy - 240, 800, 480, 30), hexc("#23242c"), lw=6, sh=(12, 16))
    piece(ctx, P_rrect(cx - 330, cy - 200, 660, 120, 12), (1, 1, 1), lw=4, shadow=False)
    draw_text(ctx, "LA HISTORIA", cx, cy - 140, 64, INK, INK, 0)
    piece(ctx, P_rrect(cx - 300, cy - 40, 600, 200, 60), hexc("#3d3f4a"), lw=4, shadow=False)
    for rx in (cx - 170, cx + 170):
        piece(ctx, P_ell(rx, cy + 60, 80), hexc("#f6f1e2"), lw=4, shadow=False)
        a = -pose * 0.9
        for k in range(6):
            aa = a + k * math.pi / 3
            line(ctx, [(rx + 22 * math.cos(aa), cy + 60 + 22 * math.sin(aa)),
                       (rx + 60 * math.cos(aa), cy + 60 + 60 * math.sin(aa))], 8, INK)
        piece(ctx, P_ell(rx, cy + 60, 20), INK, shadow=False)
    if (pose // 3) % 2 == 0:
        for k in range(2):
            x = 360 - k * 100
            piece(ctx, P_poly([(x + 90, 1320), (x + 90, 1440), (x, 1380)]), hexc("#ffe14d"), lw=5)
    secs = max(0, 9000 - int(lt * 1800))
    draw_text(ctx, f"{secs // 3600:02d}:{secs // 60 % 60:02d}:{secs % 60:02d}", 700, 1380, 60, (1, 1, 1),
              INK, 5)


def grieta(ctx, cx, cy, w, h, k):
    pts = [(cx - w * 0.45, cy - h * 0.3)]
    n = 7
    for i in range(1, n + 1):
        pts.append((cx - w * 0.45 + w * 0.9 * i / n * k, cy - h * 0.3 + (h * 0.5 if i % 2 else 0) * k))
    line(ctx, pts, 7, INK)


def sc_historias(ctx, pose, lt, ev):
    escenario(ctx, pose, "#1f3b57")
    tr, tmi, td, tc = (since(ev, k, lt) for k in ("recuerda", "miente", "dos", "contradice"))
    pareja(ctx, pose, "sonrisa" if tr >= 0 else "neutro", "preocupado" if tmi >= 0 else "neutro",
           sb=tmi >= 0)
    etiqueta(ctx, 300, 1360, "A", hexc("#2f8f5b"))
    etiqueta(ctx, 780, 1360, "B", hexc("#2c4479"))
    # bocadillo de A: historia sólida
    bubble(ctx, 270, 560, 420, 170, (300, 720), ["3 · 2 · 1", "¡FÁCIL!"], 46)
    if tr >= 0:
        piece(ctx, P_ell(450, 470, 42), hexc("#2fb35a"), lw=4)
        line(ctx, [(430, 470), (447, 488), (474, 452)], 9, (1, 1, 1))
    # bocadillo de B: se agrieta
    if td < 0:
        bubble(ctx, 810, 560, 420, 170, (780, 720), ["EHHH…", "¿3 · 1 · 2?"], 46)
        if tmi >= 0:
            grieta(ctx, 810, 560, 420, 170, clamp(tmi / 0.4))
    # pila de papeles que crece sobre B y se cae
    if td >= 0:
        n = min(8, 1 + int(td / 0.18))
        fall = clamp(tc / 0.6) if tc >= 0 else 0.0
        for i in range(n):
            y = 740 - i * 34
            dx = fall * (120 + i * 60)
            with rot(ctx, 780 + dx, y, math.radians((hnoise("b", i) - 0.5) * 16 + fall * (40 + i * 12))):
                piece(ctx, P_rect(780 + dx - 90, y - 15, 180, 30), (1, 1, 1), lw=3, sh=(3, 4))
        if tc >= 0:
            stamp(ctx, 800, 470, "¡PILLADO!", tc - 0.3, 58, ang=-8)


def sc_huida(ctx, pose, lt, ev):
    escenario(ctx, pose)
    rojo = clamp((lt - 0.3) / 0.3)
    skin_b = tuple(lerp(a, b, rojo) for a, b in zip(hexc("#d9a77c"), ROJO))
    run = clamp((lt - 1.0) / 1.0)
    xb = lerp(780, 1450, ease_io(run))
    persona_a(ctx, 300, 880, 110, "sonrisa", 1.0, pose=pose)
    encoge(ctx, 300, 880, 110, SKIN, "#2f8f5b")
    if run > 0:
        for k in range(3):
            line(ctx, [(xb - 200 - k * 40, 900 + k * 60), (xb - 330 - k * 40, 900 + k * 60)], 8, (1, 1, 1, 0.7))
        for side, ph in ((-1, 0), (1, 1)):
            a = math.radians(30 if (pose + ph) % 2 else -30)
            with rot(ctx, xb + side * 40, 1210, a):
                piece(ctx, P_rect(xb + side * 40 - 26, 1210, 52, 110), hexc("#1f2a44"), lw=4)
    persona_b(ctx, xb, 880, 110, "preocupado", 1.0, sudor=True, pose=pose, skin=skin_b,
              droop=math.radians(-8) if run > 0 else 0.0)
    etiqueta(ctx, 300, 1360, "A", hexc("#2f8f5b"))
    if run <= 0:
        etiqueta(ctx, 780, 1360, "B", hexc("#2c4479"))


SCENES = dict(duelo=sc_duelo, moneda=sc_moneda, papeles=sc_papeles, barra=sc_barra,
              profesionales=sc_profesionales, claqueta=sc_claqueta, mitos=sc_mitos, foco=sc_foco,
              rebobinar=sc_rebobinar, historias=sc_historias, huida=sc_huida)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    escenario(ctx, 0)
    pareja(ctx, 0, "neutro", "neutro", 0.0, 0.0)
    etiqueta(ctx, 300, 1360, "A", hexc("#2f8f5b"))
    etiqueta(ctx, 780, 1360, "B", hexc("#2c4479"))
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(13))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "UNO DE ESTOS DOS", 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "MIENTE", 540, 400, 170, hexc("#ffe14d"), INK, math.radians(2), 1.0)
    card_text(ctx, "¿CUÁL?", 540, 1620, 130, hexc("#1d4ed8"), (1, 1, 1), math.radians(-3), 1.0)
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
