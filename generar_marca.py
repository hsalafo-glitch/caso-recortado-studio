#!/usr/bin/env python3
"""Identidad del canal «Caso Recortado»: foto de perfil (800x800) y banner (2560x1440).
Mismo estilo cut-out que el short. Uso: python generar_marca.py"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, draw_text, hexc, line, piece,
                           rot, silhouette, boy, cop)

NOMBRE = "CASO RECORTADO"
LEMA = "Crímenes reales y la psicología que hay detrás"
OUT = os.path.join(g.BASE, "salida", "canal")


def texture(ctx, w, h, seed, alpha=0.4):
    g.W, g.H = w, h
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(seed))
    ctx.paint_with_alpha(alpha)
    ctx.set_operator(cairo.OPERATOR_OVER)


def magnifier(ctx, cx, cy, r, ang):
    with rot(ctx, cx, cy, ang):
        piece(ctx, P_rrect(cx - 34, cy + r - 6, 68, r * 1.25, 30), hexc("#6b3a1f"), lw=8, sh=(12, 14))
        piece(ctx, P_rect(cx - 40, cy + r - 16, 80, 40), hexc("#3d3f4a"), lw=7, shadow=False)
        piece(ctx, P_ell(cx, cy, r + 30), hexc("#3d3f4a"), lw=9, sh=(12, 14))
        piece(ctx, P_ell(cx, cy, r), hexc("#cfe9ff"), lw=7, shadow=False)
        ctx.new_sub_path()
        ctx.arc(cx, cy, r * 0.72, math.radians(200), math.radians(250))
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.set_line_width(16)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def avatar(path, S=800):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(*hexc("#1b1534"))
    ctx.paint()
    # foco
    ctx.move_to(S * 0.42, -10)
    ctx.line_to(S * 0.58, -10)
    ctx.line_to(S * 0.95, S)
    ctx.line_to(S * 0.05, S)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.93, 0.7, 0.12)
    ctx.fill()
    # "?" de papel
    ctx.save()
    ctx.translate(S * 0.40, S * 0.47)
    ctx.rotate(math.radians(-8))
    ctx.translate(12, 16)
    draw_text(ctx, "?", 0, 0, 520, (0, 0, 0, 0.35), INK, 0)
    ctx.translate(-12, -16)
    draw_text(ctx, "?", 0, 0, 520, hexc("#ffd23f"), INK, 9)
    ctx.restore()
    # lupa
    magnifier(ctx, S * 0.60, S * 0.50, 125, math.radians(-38))
    # tira de cinta policial abajo
    ctx.save()
    ctx.translate(-40, S * 0.86)
    ctx.rotate(math.radians(-6))
    piece(ctx, P_rect(0, -40, S + 120, 80), hexc("#ffd400"), lw=6)
    ctx.select_font_face(g.FONT, 0, 0)
    ctx.set_font_size(44)
    ctx.move_to(20, 16)
    ctx.set_source_rgb(*INK)
    ctx.show_text("CASO · RECORTADO · CASO · RECORTADO")
    ctx.restore()
    texture(ctx, S, S, 21, 0.4)
    surf.write_to_png(path)


def banner(path, Wb=2560, Hb=1440):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, Wb, Hb)
    ctx = cairo.Context(surf)
    g.W, g.H = Wb, Hb
    ctx.set_source_rgb(*hexc("#1c2552"))
    ctx.paint()
    g.stars(ctx, 70, "banner", 520, 0)
    piece(ctx, P_ell(1790, 250, 80), hexc("#f6eab0"), lw=5)
    g.skyline(ctx, 1000, hexc("#121838"), hexc("#ffd86b"), "banner", 0, 1.1)
    piece(ctx, P_rect(-10, 990, Wb + 20, 460), hexc("#2b2c38"), lw=5, shadow=False)
    # personajes en los laterales (visibles en TV/escritorio)
    for i, x in enumerate((180, 330, 480)):
        silhouette(ctx, x, 990, 1.0 + 0.08 * (i == 1), math.radians(4 * (-1) ** i), hexc("#272040"),
                   hexc("#5a4e8a"))
    ctx.save()
    ctx.translate(2190, 390)
    ctx.scale(0.95, 0.95)
    cop(ctx, 0, 620, math.radians(-30), 0, 0)
    ctx.restore()
    ctx.save()
    ctx.translate(2430, 690)
    ctx.scale(0.8, 0.8)
    piece(ctx, P_poly([(-150, 330), (150, 330), (150, 480), (-150, 480)]), hexc("#ef7d2d"), lw=4)
    boy(ctx, 0, 200, 0.6, math.radians(-6), 0, -1.0, 0)
    ctx.restore()
    # cinta policial a lo ancho (fuera de la zona segura de texto)
    for y0, y1, txt in ((1120, 1060, "POLICÍA · NO PASAR · "), (1250, 1300, "CASO RECORTADO · ")):
        ang = math.atan2(y1 - y0, Wb + 200)
        ctx.save()
        ctx.translate(-100, y0)
        ctx.rotate(ang)
        L = math.hypot(Wb + 200, y1 - y0)
        piece(ctx, P_rect(0, -40, L, 80), hexc("#ffd400"), lw=5)
        ctx.select_font_face(g.FONT, 0, 0)
        ctx.set_font_size(46)
        adv = ctx.text_extents(txt).x_advance
        x = 0
        while x < L:
            ctx.move_to(x, 17)
            ctx.set_source_rgb(*INK)
            ctx.show_text(txt)
            x += adv
        ctx.restore()
    # zona segura (1546x423 centrada): nombre + lema
    cx, cy = Wb / 2, Hb / 2
    card_text(ctx, "CASO", cx - 545, cy - 70, 150, hexc("#e63946"), (1, 1, 1), math.radians(-3), 1.0)
    card_text(ctx, "RECORTADO", cx + 215, cy - 70, 150, hexc("#ffe14d"), INK, math.radians(2.5), 1.0)
    card_text(ctx, LEMA.upper(), cx, cy + 105, 52, hexc("#1d4ed8"), (1, 1, 1), math.radians(-1.5), 1.0)
    texture(ctx, Wb, Hb, 33, 0.4)
    surf.write_to_png(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    avatar(os.path.join(OUT, "foto-perfil-800.png"))
    banner(os.path.join(OUT, "banner-2560x1440.png"))
    print("✔", OUT)
