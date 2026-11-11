#!/usr/bin/env python3
"""
Short 3 · «El 65 % de la gente te electrocutaría si se lo ordenan»
Motor: generar_short.py · utilidades: generar_short_estafas.py · voz Salva (eleven_v4)

Uso:
    python short_obediencia.py            # vídeo final (usa cache_audio/obediencia-65/)
    python short_obediencia.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, burst, since, stamp, txt

SLUG = "obediencia-65"

# ─────────────────────────────── guion ───────────────────────────────
BLOQUES = [
    dict(
        id="gancho",
        voz="¿Darías una descarga mortal a un desconocido solo porque alguien con bata te lo pide?",
        escenas=[(None, "interruptor"), ("alguien con bata", "bata")],
        pantalla=[("alguien con bata", "¿LO HARÍAS?")],
        eventos={},
    ),
    dict(
        id="yale",
        voz=("Yale, 1961. A voluntarios normales les dicen que es un estudio sobre memoria. "
             "Cada vez que otro participante falla, deben darle una descarga más fuerte. "
             "Él grita, suplica, golpea la pared."),
        escenas=[(None, "universidad"), ("A voluntarios", "cartel"), ("Cada vez", "salas")],
        pantalla=[(None, "YALE, 1961"), ("Cada vez", "+15 V POR CADA FALLO")],
        eventos={"grita": "Él grita", "golpea": "golpea la pared"},
    ),
    dict(
        id="truco",
        voz=("Lo que no saben: las descargas son falsas y el que grita es un actor. "
             "Cuando dudan, el investigador solo dice: \"el experimento requiere que continúe\"."),
        escenas=[(None, "truco"), ("Cuando dudan", "investigador")],
        pantalla=[("es un actor", "ERA UN ACTOR")],
        eventos={"falsas": "descargas son falsas", "actor": "es un actor"},
        habla=("el experimento", "continúe"),
    ),
    dict(
        id="resultado",
        voz=("Resultado: el 65% llegó hasta 450 voltios. No eran monstruos. "
             "Sufrían, pero obedecían, porque la responsabilidad ya no parecía suya."),
        escenas=[(None, "siluetas"), ("No eran", "mano"), ("porque la responsabilidad", "flecha")],
        pantalla=[("Resultado", "65 %")],
        eventos={"porc": "el 65%"},
    ),
    dict(
        id="cierre",
        voz=("La obediencia bajaba mucho cuando alguien se negaba primero. "
             "A veces basta una persona que diga \"no\". ¿Tú habrías parado?"),
        escenas=[(None, "rebeldia")],
        pantalla=[("habrías parado", "¿HABRÍAS PARADO?")],
        eventos={"negaba": "se negaba", "basta": "A veces basta", "parado": "habrías parado"},
    ),
]

RECORTES = [
    "Bloque 2: «normales» (≈0,5 s)",
    "Bloque 4: «No eran monstruos.» (≈1,2 s)",
    "Bloque 5: «mucho» (≈0,4 s)",
]

SKIN = hexc("#e8b896")
SKIN2 = hexc("#c98b5e")


# ─────────────────────────────── personajes ───────────────────────────────
def face(ctx, x, y, r, expr="neutro", talk=0, look=0.0, gafas=False):
    """Rasgos de la cara (sin cabeza). expr: neutro | preocupado | grito | sonrisa."""
    for side in (-1, 1):
        ex, ey = x + side * r * 0.36, y - r * 0.02
        piece(ctx, P_ell(ex, ey, r * 0.2, r * 0.26), (1, 1, 1), lw=3.5, shadow=False)
        P_ell(ex + look * r * 0.07, ey + r * 0.04, r * 0.08)(ctx)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        if gafas:
            ctx.new_sub_path()
            ctx.arc(ex, ey, r * 0.3, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        # cejas
        by = ey - r * 0.38
        if expr in ("preocupado", "grito"):
            line(ctx, [(ex - side * r * 0.24, by + r * 0.06), (ex + side * r * 0.14, by - r * 0.1)], 7)
        elif expr == "sonrisa":
            ctx.new_sub_path()
            ctx.arc(ex, by + r * 0.06, r * 0.18, math.radians(200), math.radians(340))
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
        else:
            line(ctx, [(ex - r * 0.18, by), (ex + r * 0.18, by)], 7)
    if gafas:
        line(ctx, [(x - r * 0.06, y - r * 0.02), (x + r * 0.06, y - r * 0.02)], 6)
    my = y + r * 0.52
    if expr == "grito" or talk:
        h = r * (0.3 if expr == "grito" else (0.2 if talk == 1 else 0.11))
        piece(ctx, P_ell(x, my, r * (0.26 if expr == "grito" else 0.18), h), hexc("#5a1620"), lw=4,
              shadow=False)
    elif expr == "sonrisa":
        ctx.new_sub_path()
        ctx.arc(x, my - r * 0.18, r * 0.34, math.radians(25), math.radians(155))
        ctx.close_path()
        set_col(ctx, hexc("#5a1620"))
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
    elif expr == "preocupado":
        ctx.new_sub_path()
        ctx.arc(x, my + r * 0.16, r * 0.2, math.radians(215), math.radians(325))
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
    else:
        line(ctx, [(x - r * 0.16, my), (x + r * 0.16, my)], 5)


def adulto(ctx, x, y, r=100, traje="#5b6475", pelo="#3a2a1e", expr="neutro", talk=0, look=0.0,
           gafas=False, skin=SKIN, droop=0.0, bata=False, sudor=False, pose=0, cuerpo=True):
    """Adulto original: cabeza redonda, raya al lado, traje de los 60 (o bata blanca)."""
    if cuerpo:
        w0, w1 = r * (1.0 if bata else 0.85), r * (1.55 if bata else 1.35)
        piece(ctx, P_poly([(x - w0, y + r * 0.85), (x + w0, y + r * 0.85), (x + w1, y + r * 3.0),
                           (x - w1, y + r * 3.0)]), hexc("#f4f4f0") if bata else hexc(traje), lw=4.5)
        piece(ctx, P_poly([(x - r * 0.38, y + r * 0.85), (x + r * 0.38, y + r * 0.85), (x, y + r * 1.5)]),
              (1, 1, 1), lw=3, shadow=False)
        piece(ctx, P_poly([(x - r * 0.1, y + r * 0.95), (x + r * 0.1, y + r * 0.95), (x + r * 0.13, y + r * 1.75),
                           (x, y + r * 1.95), (x - r * 0.13, y + r * 1.75)]), hexc("#b5473a"), lw=3,
              shadow=False)
        if bata:
            line(ctx, [(x - r * 0.38, y + r * 0.85), (x - r * 0.1, y + r * 2.2)], 4)
            line(ctx, [(x + r * 0.38, y + r * 0.85), (x + r * 0.1, y + r * 2.2)], 4)
            piece(ctx, P_rect(x + r * 0.5, y + r * 1.45, r * 0.4, r * 0.3), hexc("#dfe3ea"), lw=3, shadow=False)
    with rot(ctx, x, y + r * 0.9, droop):
        piece(ctx, P_ell(x - r * 0.97, y + r * 0.05, r * 0.2, r * 0.27), skin, lw=4)
        piece(ctx, P_ell(x + r * 0.97, y + r * 0.05, r * 0.2, r * 0.27), skin, lw=4)
        piece(ctx, P_ell(x, y, r, r * 0.98), skin, lw=4.5)
        # pelo: casquete liso con raya
        pts = []
        for i in range(17):
            a = math.pi + 0.22 + (math.pi - 0.44) * i / 16
            pts.append((x + (r + 6) * math.cos(a), y - 4 + (r + 6) * math.sin(a)))
        pts += [(x + r * 0.9, y - r * 0.32), (x - r * 0.25, y - r * 0.5), (x - r * 0.9, y - r * 0.3)]
        piece(ctx, P_poly(pts), hexc(pelo), lw=4, shadow=False)
        line(ctx, [(x - r * 0.25, y - r * 0.5), (x - r * 0.32, y - r * 0.98)], 3, (1, 1, 1, 0.35))
        face(ctx, x, y + r * 0.08, r * 0.92, expr, talk, look, gafas)
        if sudor:
            dy = (pose % 6) * 4
            sx, sy = x + r * 0.85, y - r * 0.4 + dy
            piece(ctx, P_poly([(sx, sy - 24), (sx + 12, sy), (sx, sy + 9), (sx - 12, sy)]), hexc("#8fd3ff"),
                  lw=3, shadow=False)


def clipboard(ctx, x, y, s=1.0):
    piece(ctx, P_rrect(x - 60 * s, y - 80 * s, 120 * s, 160 * s, 10), hexc("#8a5a34"), lw=4)
    piece(ctx, P_rect(x - 48 * s, y - 62 * s, 96 * s, 132 * s), (1, 1, 1), lw=3, shadow=False)
    piece(ctx, P_rrect(x - 26 * s, y - 92 * s, 52 * s, 24 * s, 6), hexc("#9aa0ab"), lw=3, shadow=False)
    for k in range(5):
        line(ctx, [(x - 36 * s, y - 36 * s + k * 22 * s), (x + 34 * s, y - 36 * s + k * 22 * s)], 3,
             (0, 0, 0, 0.35))


def investigador(ctx, x, floor_y, talk=0, look=-1.0, pose=0):
    hy = floor_y - 470
    piece(ctx, P_rect(x - 60, hy + 300, 50, floor_y - hy - 300), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rect(x + 10, hy + 300, 50, floor_y - hy - 300), hexc("#3d3f4a"), lw=4)
    piece(ctx, P_rrect(x - 74, floor_y - 18, 70, 24, 10), INK, lw=3, shadow=False)
    piece(ctx, P_rrect(x + 6, floor_y - 18, 70, 24, 10), INK, lw=3, shadow=False)
    adulto(ctx, x, hy, 105, pelo="#9a9a9a", expr="neutro", talk=talk, look=look, gafas=True, bata=True)
    clipboard(ctx, x - 70, hy + 230, 1.0)
    piece(ctx, P_ell(x - 10, hy + 250, 30), SKIN, lw=4, shadow=False)


def silla(ctx, x, y, s=1.0):
    piece(ctx, P_rrect(x - 110 * s, y - 250 * s, 220 * s, 260 * s, 18), hexc("#5d3a22"), lw=4)


# ─────────────────────────────── objetos ───────────────────────────────
def hazard(ctx, x, y, w, h):
    ctx.save()
    P_rect(x, y, w, h)(ctx)
    ctx.clip()
    set_col(ctx, hexc("#ffd23f"))
    ctx.paint()
    for i in range(-2, int(w / 40) + 3):
        ctx.move_to(x + i * 40, y + h)
        ctx.line_to(x + i * 40 + 20, y + h)
        ctx.line_to(x + i * 40 + 20 + h, y)
        ctx.line_to(x + i * 40 + h, y)
        ctx.close_path()
        ctx.set_source_rgb(*INK)
        ctx.fill()
    ctx.restore()
    P_rect(x, y, w, h)(ctx)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()


def big_switch(ctx, cx, cy, s, on, label="450 V", lab_col="#e23b3b"):
    piece(ctx, P_rrect(cx - 150 * s, cy - 170 * s, 300 * s, 300 * s, 20 * s), hexc("#3d3f4a"), lw=5)
    piece(ctx, P_rrect(cx - 26 * s, cy - 120 * s, 52 * s, 200 * s, 26 * s), INK, lw=3, shadow=False)
    ang = math.radians(28 if on else -28)
    with rot(ctx, cx, cy + 40 * s, ang):
        piece(ctx, P_rrect(cx - 16 * s, cy - 150 * s, 32 * s, 190 * s, 14 * s), hexc("#c9ced8"), lw=4)
        piece(ctx, P_ell(cx, cy - 150 * s, 40 * s), hexc("#e23b3b"), lw=4)
    piece(ctx, P_rrect(cx - 130 * s, cy + 150 * s, 260 * s, 90 * s, 12 * s), hexc(lab_col), lw=4)
    draw_text(ctx, label, cx, cy + 195 * s, 64 * s, (1, 1, 1), INK, 4)


def hand_down(ctx, x, tip_y, sleeve="#5b6475"):
    """Mano que baja desde arriba con el índice extendido hacia abajo (gesto neutro)."""
    piece(ctx, P_rrect(x - 70, -40, 140, tip_y - 200 + 40, 40), hexc(sleeve), lw=5)
    piece(ctx, P_ell(x, tip_y - 170, 95, 85), SKIN, lw=5)
    piece(ctx, P_rrect(x - 26, tip_y - 140, 52, 140, 26), SKIN, lw=5)
    for k in (-1, 1):
        piece(ctx, P_ell(x + k * 62, tip_y - 120, 30, 38), SKIN, lw=4, shadow=False)
    line(ctx, [(x - 14, tip_y - 30), (x + 14, tip_y - 30)], 4, (0, 0, 0, 0.35))


def panel(ctx, x, y, w, h, volts):
    piece(ctx, P_rrect(x, y, w, h, 16), hexc("#7d838f"), lw=5)
    n = 10
    on = int(volts // 45)
    sw = (w - 40) / n
    for i in range(n):
        cx = x + 20 + sw * (i + 0.5)
        lit = i < on
        piece(ctx, P_ell(cx, y + 40, 13), hexc("#ff4040") if lit else hexc("#5a1414"), lw=3, shadow=False)
        piece(ctx, P_rrect(cx - 12, y + 66, 24, 70, 8), INK, lw=2, shadow=False)
        piece(ctx, P_rrect(cx - 9, y + (70 if lit else 100), 18, 32, 6), hexc("#c9ced8"), lw=2, shadow=False)
        txt(ctx, str(45 * (i + 1)), cx, y + 168, 20, INK, "Inter", anchor="center")
    hazard(ctx, x + w - 2 * sw - 14, y + h - 34, 2 * sw + 4, 22)
    piece(ctx, P_rrect(x + 16, y + h + 14, 220, 70, 12), hexc("#1d2433"), lw=4)
    txt(ctx, f"{int(volts)} V", x + 126, y + h + 66, 46, hexc("#ff5a5a"), anchor="center")


# ─────────────────────────────── escenas ───────────────────────────────
def sc_interruptor(ctx, pose, lt, ev):
    set_col(ctx, hexc("#17151f"))
    ctx.paint()
    piece(ctx, P_rrect(60, 560, 960, 880, 30), hexc("#7d838f"), lw=6)
    for cx in (200, 880):
        piece(ctx, P_ell(cx, 680, 70), hexc("#f6f1e2"), lw=5)
        a = math.radians(-60 + 25 * ((pose // 3) % 3))
        line(ctx, [(cx, 680), (cx + 55 * math.sin(a), 680 - 55 * math.cos(a))], 7, hexc("#e23b3b"))
    hazard(ctx, 240, 600, 600, 50)
    big_switch(ctx, 540, 1060, 1.5, False)
    trem = 6 if pose % 2 else -6
    hand_down(ctx, 540 - 110 + trem, 770 + (pose % 3) * 4)


def sc_bata(ctx, pose, lt, ev):
    set_col(ctx, hexc("#cfe3d6"))
    ctx.paint()
    for i in range(14):
        line(ctx, [(0, i * 100), (1080, i * 100)], 2, (0, 0, 0, 0.07))
        line(ctx, [(i * 100, 0), (i * 100, 1300)], 2, (0, 0, 0, 0.07))
    piece(ctx, P_rect(-10, 1300, 1100, 640), hexc("#9aa3ad"), lw=4, shadow=False)
    # investigador de espaldas
    x, hy = 540, 760
    sway = math.radians(1.5) * (1 if (pose // 6) % 2 else -1)
    with rot(ctx, x, 1500, sway):
        piece(ctx, P_poly([(x - 170, 880), (x + 170, 880), (x + 260, 1520), (x - 260, 1520)]), hexc("#f4f4f0"),
              lw=5)
        line(ctx, [(x, 900), (x, 1520)], 4)
        piece(ctx, P_rrect(x - 290, 920, 90, 420, 40), hexc("#f4f4f0"), lw=5)
        piece(ctx, P_rrect(x + 200, 920, 90, 420, 40), hexc("#f4f4f0"), lw=5)
        piece(ctx, P_ell(x - 245, 1360, 42), SKIN, lw=4)
        piece(ctx, P_rrect(x + 210, 1220, 40, 190, 8), hexc("#8a5a34"), lw=4)
        piece(ctx, P_ell(x + 245, 1360, 42), SKIN, lw=4)
        piece(ctx, P_ell(x - 128, hy + 10, 26, 36), SKIN, lw=4)
        piece(ctx, P_ell(x + 128, hy + 10, 26, 36), SKIN, lw=4)
        piece(ctx, P_ell(x, hy, 130), hexc("#9a9a9a"), lw=5)
        piece(ctx, P_rect(x - 80, hy + 112, 160, 30), SKIN, lw=3, shadow=False)
        piece(ctx, P_poly([(x - 90, 880), (x + 90, 880), (x + 60, 930), (x - 60, 930)]), hexc("#f4f4f0"),
              lw=4, shadow=False)


def sc_universidad(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_ell(880, 600, 70), hexc("#ffe58a"), lw=4)
    for cx, cy in ((200, 640), (640, 560)):
        dx = (pose // 6) * 2
        for dxx, r in ((-50, 45), (0, 60), (50, 45)):
            piece(ctx, P_ell(cx + dxx + dx, cy, r, r * 0.8), (1, 1, 1), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1260, 1100, 700), hexc("#5fa35a"), lw=4, shadow=False)
    g.tree(ctx, 90, 1280, 1.1, hexc("#2f6b45"), 1)
    g.tree(ctx, 990, 1280, 1.2, hexc("#2f6b45"), 2)
    # edificio clásico genérico
    piece(ctx, P_rect(170, 900, 740, 380), hexc("#efe2c4"), lw=5)
    piece(ctx, P_poly([(140, 905), (940, 905), (540, 720)]), hexc("#e3d2ad"), lw=5)
    piece(ctx, P_rect(140, 890, 800, 30), hexc("#d8c59c"), lw=4, shadow=False)
    for i in range(6):
        piece(ctx, P_rect(210 + i * 128, 930, 44, 330), hexc("#fbf3e0"), lw=4)
    for k in range(3):
        piece(ctx, P_rect(150 - k * 20, 1260 + k * 30, 780 + k * 40, 30), hexc("#d8c59c"), lw=3, shadow=False)
    piece(ctx, P_rrect(440, 1100, 200, 160, 10), hexc("#6b4a2b"), lw=4)
    piece(ctx, P_rrect(420, 790, 240, 90, 10), hexc("#1d4ed8"), lw=5)
    draw_text(ctx, "1961", 540, 835, 70, (1, 1, 1), INK, 5)


def sc_cartel(ctx, pose, lt, ev):
    set_col(ctx, hexc("#b07a4a"))
    ctx.paint()
    for i in range(140):
        P_ell(hnoise("c", i, 0) * 1080, hnoise("c", i, 1) * 1920, 4)(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.12)
        ctx.fill()
    for i, (x, y, a) in enumerate(((150, 700, -8), (900, 820, 6), (180, 1330, 5), (880, 1350, -6))):
        with rot(ctx, x, y, math.radians(a)):
            piece(ctx, P_rect(x - 120, y - 90, 240, 180), hexc("#f6eab0") if i % 2 else (1, 1, 1), lw=4)
            for k in range(4):
                line(ctx, [(x - 90, y - 50 + k * 30), (x + 90 - 30 * (k % 2), y - 50 + k * 30)], 4,
                     (0, 0, 0, 0.25))
    k = clamp(lt / 0.3)
    y0 = lerp(-700, 0, ease_out_back(k) if k < 1 else 1.0)
    with rot(ctx, 540, 1000 + y0, math.radians(-3)):
        x0, yy = 230, 620 + y0
        piece(ctx, P_rect(x0, yy, 620, 760), (1, 1, 1), lw=6, sh=(12, 16))
        piece(ctx, P_rect(x0, yy, 620, 200), hexc("#e63946"), lw=6, shadow=False)
        draw_text(ctx, "SE BUSCAN", 540, yy + 62, 70, (1, 1, 1), INK, 0)
        draw_text(ctx, "VOLUNTARIOS", 540, yy + 145, 70, (1, 1, 1), INK, 0)
        draw_text(ctx, "ESTUDIO", 540, yy + 290, 84, INK, INK, 0)
        draw_text(ctx, "DE MEMORIA", 540, yy + 380, 84, INK, INK, 0)
        for j in range(4):
            line(ctx, [(x0 + 70, yy + 480 + j * 50), (x0 + 550 - 60 * (j % 2), yy + 480 + j * 50)], 6,
                 (0, 0, 0, 0.25))
        for j in range(7):
            line(ctx, [(x0 + 30 + j * 85, yy + 700), (x0 + 30 + j * 85, yy + 760)], 3, (0, 0, 0, 0.4))
        piece(ctx, P_ell(540, yy + 22, 22), hexc("#e23b3b"), lw=4, shadow=False)


def salas(ctx, pose, lt, ev, volts, alumno_expr, golpes, cable_suelto=-1.0, mascara=-1.0):
    piece(ctx, P_rect(-10, 0, 560, 1300), hexc("#c9d6c2"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(540, 0, 560, 1300), hexc("#d7c9b0"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rect(-10, 1300, 1100, 640), hexc("#8b7d6b"), lw=4, shadow=False)
    # alumno (derecha), atado a la silla con correas
    silla(ctx, 810, 1240, 1.05)
    talk = (1 if pose % 2 else 2) if alumno_expr == "grito" else 0
    adulto(ctx, 810, 920, 92, traje="#4b7bb5", pelo="#6b4a2b", expr=alumno_expr, talk=talk, look=-0.6,
           skin=SKIN2, pose=pose)
    for yy in (1080, 1160):
        piece(ctx, P_rect(700, yy, 220, 26), hexc("#6b3a1f"), lw=3, shadow=False)
    if mascara >= 0:
        k = clamp(mascara / 0.5)
        mx, my = 810 + 40 * k, 930 - 330 * ease_io(k)
        with rot(ctx, mx, my, math.radians(25 * k)):
            piece(ctx, P_ell(mx, my, 84, 82), SKIN2, lw=4, sh=(10, 12))
            face(ctx, mx, my + 6, 76, "grito", 1)
            line(ctx, [(mx - 84, my), (mx - 130, my - 30)], 3)
            line(ctx, [(mx + 84, my), (mx + 130, my - 30)], 3)
    # voluntario (izquierda) en el panel
    adulto(ctx, 270, 930, 92, expr="preocupado", look=0.8, sudor=True, pose=pose)
    panel(ctx, 30, 1110, 480, 200, volts)
    # cable que atraviesa la pared
    cab = hexc("#e23b3b")
    line(ctx, [(760, 1200), (600, 1230), (565, 1230)], 8, cab)
    if cable_suelto < 0:
        line(ctx, [(515, 1230), (505, 1240)], 8, cab)
    else:
        line(ctx, [(515, 1230), (470, 1330), (430, 1420)], 8, cab)
        piece(ctx, P_rrect(405, 1410, 50, 70, 8), hexc("#3d3f4a"), lw=3)
        stamp(ctx, 400, 1380, "FALSO", cable_suelto, 40, ang=-10)
    # pared (tiembla con los golpes)
    sh = (7 if pose % 2 else -7) if golpes >= 0 else 0
    piece(ctx, P_rect(515 + sh, -10, 50, 1320), hexc("#6b6f78"), lw=4)
    if golpes >= 0 and (pose // 2) % 2 == 0:
        draw_text(ctx, "¡PUM!", 700, 720, 80, hexc("#ffe14d"), INK, 7)
        for k in range(6):
            a = math.radians(160 + k * 10)
            line(ctx, [(575 + 30 * math.cos(a + math.pi), 820 + 30 * math.sin(a)),
                       (575 + 110 * math.cos(a + math.pi), 820 + 110 * math.sin(a))], 6, hexc("#ffe14d"))


def sc_salas(ctx, pose, lt, ev):
    volts = min(450, 30 + 15 * int(lt / 0.45))
    expr = "grito" if since(ev, "grita", lt) >= 0 else "neutro"
    salas(ctx, pose, lt, ev, volts, expr, since(ev, "golpea", lt))


def sc_truco(ctx, pose, lt, ev):
    volts = min(450, 300 + 15 * int(lt / 0.6))
    ta = since(ev, "actor", lt)
    salas(ctx, pose, lt, ev, volts, "sonrisa" if ta >= 0 else "grito", -1, since(ev, "falsas", lt), ta)


def sc_investigador(ctx, pose, lt, ev):
    set_col(ctx, hexc("#c9d6c2"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 640), hexc("#8b7d6b"), lw=4, shadow=False)
    adulto(ctx, 280, 980, 92, expr="preocupado", look=1.0, sudor=True, pose=pose)
    panel(ctx, 40, 1160, 470, 200, 375)
    t0 = ev.get("habla_ini_lt", 99)
    t1 = ev.get("habla_fin_lt", -1)
    talk = (1 if pose % 3 == 0 else 2 if pose % 3 == 1 else 0) if t0 <= lt <= t1 else 0
    investigador(ctx, 790, 1420, talk, -1.0, pose)
    if lt >= t0 - 0.1:
        bubble(ctx, 560, 640, 820, 220, (760, 790), ["«EL EXPERIMENTO REQUIERE", "QUE CONTINÚE»"], 50)


def sc_siluetas(ctx, pose, lt, ev):
    set_col(ctx, hexc("#141a33"))
    ctx.paint()
    tp = since(ev, "porc", lt)
    n_lit = int(26 * clamp(tp / 1.6)) if tp >= 0 else 0
    order = sorted(range(40), key=lambda i: hnoise("orden", i))
    lit = set(order[:n_lit])
    for i in range(40):
        r, c = divmod(i, 8)
        x, feet = 120 + c * 120, 690 + r * 140
        on = i in lit
        silhouette(ctx, x, feet, 0.36, 0.0, hexc("#e23b3b") if on else hexc("#3a3f66"),
                   hexc("#ff9a9a") if on else hexc("#5c6399"))
    draw_text(ctx, f"{n_lit} DE 40", 540, 1345, 74, hexc("#ff6b6b") if n_lit else (1, 1, 1), INK, 7)


def sc_mano(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2a2730"))
    ctx.paint()
    piece(ctx, P_rrect(40, 600, 1000, 840, 26), hexc("#7d838f"), lw=6)
    labels = ["375 V", "405 V", "435 V", "450 V"]
    for i, lab in enumerate(labels):
        cx = 175 + i * 243
        on = i < 3
        piece(ctx, P_ell(cx, 690, 22), hexc("#ff4040") if on else hexc("#5a1414"), lw=3, shadow=False)
        piece(ctx, P_rrect(cx - 34, 740, 68, 220, 20), INK, lw=3, shadow=False)
        piece(ctx, P_rrect(cx - 26, 750 if on else 860, 52, 90, 14), hexc("#c9ced8"), lw=3, shadow=False)
        piece(ctx, P_rrect(cx - 100, 1000, 200, 80, 10), hexc("#e23b3b") if i == 3 else hexc("#3d3f4a"), lw=4)
        draw_text(ctx, lab, cx, 1040, 46, (1, 1, 1), INK, 0)
    hazard(ctx, 70, 1120, 940, 50)
    trem = (10 if pose % 2 else -10)
    tip = 760 + (pose % 3) * 5
    hand_down(ctx, 904 + trem, tip)
    dy = (pose % 8) * 22
    piece(ctx, P_poly([(960 + trem, tip - 220 + dy), (976 + trem, tip - 190 + dy), (960 + trem, tip - 176 + dy),
                       (944 + trem, tip - 190 + dy)]), hexc("#8fd3ff"), lw=3, shadow=False)


def sc_flecha(ctx, pose, lt, ev):
    set_col(ctx, hexc("#f1e3c8"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#b89c74"), lw=4, shadow=False)
    adulto(ctx, 270, 930, 95, expr="preocupado", look=1.0, sudor=True, pose=pose)
    panel(ctx, 50, 1140, 440, 180, 450)
    investigador(ctx, 800, 1420, 0, -1.0, pose)
    k = ease_io(clamp(lt / 0.9))
    cx = lerp(270, 760, k)
    y = 620
    w = 560
    with rot(ctx, cx, y, math.radians(-3)):
        piece(ctx, P_poly([(cx - w / 2, y - 55), (cx + w / 2 - 80, y - 55), (cx + w / 2 - 80, y - 100),
                           (cx + w / 2, y), (cx + w / 2 - 80, y + 100), (cx + w / 2 - 80, y + 55),
                           (cx - w / 2, y + 55)]), hexc("#ffd23f"), lw=6, sh=(10, 12))
        draw_text(ctx, "RESPONSABILIDAD", cx - 40, y, 52, INK, INK, 0)


def crossed_arms(ctx, x, y, s, col):
    for a in (-22, 22):
        with rot(ctx, x, y, math.radians(a)):
            piece(ctx, P_rrect(x - 70 * s, y - 16 * s, 140 * s, 32 * s, 14 * s), col, lw=3, shadow=False)


def sc_rebeldia(ctx, pose, lt, ev):
    set_col(ctx, hexc("#23304f"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1450, 1100, 500), hexc("#1a2440"), lw=4, shadow=False)
    # voltímetro que vuelve a cero
    tp = since(ev, "parado", lt)
    v = 1.0 if tp < 0 else 1 - ease_io(tp / 0.7)
    cx, cy, r = 540, 640, 120
    ctx.move_to(cx, cy)
    ctx.arc(cx, cy, r, math.pi, 2 * math.pi)
    ctx.close_path()
    set_col(ctx, hexc("#f6f1e2"))
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5)
    ctx.stroke()
    a = math.pi + v * math.pi
    line(ctx, [(cx, cy), (cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))], 9, hexc("#e23b3b"))
    piece(ctx, P_ell(cx, cy, 14), INK, shadow=False)
    draw_text(ctx, "0", cx - r - 34, cy - 10, 40, (1, 1, 1), INK, 5)
    draw_text(ctx, "450", cx + r + 54, cy - 10, 40, (1, 1, 1), INK, 5)
    tn, tb = since(ev, "negaba", lt), since(ev, "basta", lt)
    seats = [(220, 1080), (540, 1080), (860, 1080), (220, 1440), (540, 1440), (860, 1440)]
    order = [1, 0, 2, 4, 3, 5]          # el primero en negarse es el del centro arriba
    for idx, (x, feet) in enumerate(seats):
        rank = order.index(idx)
        if rank == 0:
            up = tn >= 0
        else:
            up = tb >= 0 and tb >= (rank - 1) * 0.35
        silla(ctx, x, feet - 60, 0.8)
        if up:
            col, rim = (hexc("#2fb3a5"), hexc("#9ff0e6")) if rank == 0 else (hexc("#4a7fd6"), hexc("#a9c6ff"))
            silhouette(ctx, x, feet, 0.82, 0.0, col, rim)
            crossed_arms(ctx, x, feet - 120, 0.9, rim)
        else:
            silhouette(ctx, x, feet, 0.6, 0.0, hexc("#3a3f66"), hexc("#5c6399"))


SCENES = dict(interruptor=sc_interruptor, bata=sc_bata, universidad=sc_universidad, cartel=sc_cartel,
              salas=sc_salas, truco=sc_truco, investigador=sc_investigador, siluetas=sc_siluetas,
              mano=sc_mano, flecha=sc_flecha, rebeldia=sc_rebeldia)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_interruptor(ctx, 1, 0.5, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(9))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "EL 65 % DE LA GENTE", 540, 210, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "TE ELECTROCUTARÍA", 540, 350, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "SI SE LO ORDENAN", 540, 1640, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
