#!/usr/bin/env python3
"""
Short 2 · «La palabra favorita de un estafador: "YA"»
Mismo motor y estilo cut-out que generar_short.py (voz Salva · eleven_v4).

Uso:
    python generar_short_estafas.py            # vídeo final (usa cache_audio/estafas/)
    python generar_short_estafas.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os
import sys

import cairo

import generar_short as g
from generar_short import (INK, BOY_SKIN, P_ell, P_poly, P_rect, P_rrect, boy, card_text, check_sign, clamp,
                           draw_text, ease_io, ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col)

# ─────────────────────────────── guion ───────────────────────────────
BLOQUES = [
    dict(
        id="gancho",
        voz="\"Tu cuenta ha sido bloqueada. Tienes diez minutos.\" Si oyes esto, cuelga.",
        escenas=[(None, "alerta")],
        pantalla=[("Si oyes", "SI OYES ESTO: CUELGA")],
        eventos={"cuelga": "cuelga"},
    ),
    dict(
        id="patron",
        voz=("Casi todas las estafas tienen algo en común: no te dejan tiempo para pensar. "
             "Un SMS del banco, un falso técnico, un \"hijo\" que necesita dinero urgente."),
        escenas=[(None, "mensajes")],
        pantalla=[("no te dejan", "NO TE DEJAN PENSAR")],
        eventos={"m1": "Un SMS", "m2": "un falso técnico", "m3": "un hijo"},
    ),
    dict(
        id="cerebro",
        voz=("Y no es casualidad. Cuando sientes urgencia y miedo, tu cerebro pasa al modo rápido: "
             "decides por instinto, no por lógica. El estafador solo necesita que no te pares diez segundos "
             "a preguntarte: \"¿esto tiene sentido?\". Por eso añaden autoridad, como \"soy del banco\", "
             "y escasez, como \"última oportunidad\"."),
        escenas=[(None, "cerebro")],
        pantalla=[("urgencia y miedo", "URGENCIA +"), ("añaden autoridad", "AUTORIDAD +"),
                  ("y escasez", "ESCASEZ")],
        modo_pantalla="pila",
        eventos={"urgencia": "urgencia y miedo", "rapido": "modo rápido", "sentido": "esto tiene sentido",
                 "autoridad": "soy del banco", "escasez": "última oportunidad"},
    ),
    dict(
        id="regla",
        voz=("La regla de oro: un banco de verdad nunca te pide claves por teléfono ni te obliga a decidir "
             "en minutos. Cuelga y llama tú al número oficial."),
        escenas=[(None, "regla")],
        pantalla=[(None, "LA REGLA DE ORO"), ("Cuelga y llama", "CUELGA Y LLAMA TÚ")],
        eventos={"claves": "nunca te pide", "cuelga": "Cuelga y llama", "oficial": "número oficial"},
    ),
    dict(
        id="cierre",
        voz="Compártelo con alguien que conteste a todo.",
        escenas=[(None, "compartir")],
        pantalla=[(None, "ENVÍASELO")],
        eventos={"alguien": "con alguien"},
    ),
]

RECORTES = [
    "Bloque 3: «Y no es casualidad.» (≈1 s)",
    "Bloque 3: «diez segundos» → quitar (≈0,8 s)",
    "Bloque 4: «ni te obliga a decidir en minutos» (≈1,8 s)",
]


# ─────────────────────────────── utilidades ───────────────────────────────
def txt(ctx, s, x, y, size, col, font=g.FONT, anchor="left"):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL if font == g.FONT else cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    if anchor == "center":
        x = x - e.width / 2 - e.x_bearing
    elif anchor == "right":
        x = x - e.width - e.x_bearing
    ctx.move_to(x, y)
    if g.ESTILO in ("palitos", "acuarela") and sum(col[:3]) > 1.9:   # en la pizarra blanca, los textos claros pasan a tinta
        col = (0.08, 0.08, 0.1)
    set_col(ctx, col)
    ctx.show_text(s)
    return e


def wrap(ctx, s, size, maxw, font="Inter"):
    ctx.select_font_face(font, 0, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if ctx.text_extents(t).x_advance > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def burst(ctx, cx, cy, n, c1, c2, phase=0.0):
    ctx.set_source_rgb(*c1)
    ctx.paint()
    R = 3000
    for i in range(n):
        if i % 2:
            continue
        a0 = phase + i * 2 * math.pi / n
        a1 = phase + (i + 1) * 2 * math.pi / n
        ctx.move_to(cx, cy)
        ctx.line_to(cx + R * math.cos(a0), cy + R * math.sin(a0))
        ctx.line_to(cx + R * math.cos(a1), cy + R * math.sin(a1))
        ctx.close_path()
        set_col(ctx, c2)
        ctx.fill()


def phone(ctx, cx, cy, w, h, screen_col, draw_screen, ang=0.0):
    with rot(ctx, cx, cy, ang):
        x0, y0 = cx - w / 2, cy - h / 2
        piece(ctx, P_rrect(x0, y0, w, h, 58), hexc("#23242c"), lw=6, sh=(12, 16))
        sx, sy, sw, sh = x0 + 22, y0 + 22, w - 44, h - 44
        piece(ctx, P_rrect(sx, sy, sw, sh, 40), screen_col, lw=3, shadow=False)
        ctx.save()
        P_rrect(sx, sy, sw, sh, 40)(ctx)
        ctx.clip()
        draw_screen(ctx, sx, sy, sw, sh)
        ctx.restore()
        piece(ctx, P_rrect(cx - 60, y0 + 34, 120, 26, 13), hexc("#23242c"), lw=2, shadow=False)


def handset(ctx, cx, cy, r, col=(1, 1, 1), up=False):
    ctx.save()
    ctx.translate(cx, cy)
    if not up:
        ctx.rotate(math.radians(135))
    else:
        ctx.rotate(math.radians(0))
    ctx.new_sub_path()
    ctx.arc(0, r * 0.15, r * 0.5, math.radians(200), math.radians(340))
    set_col(ctx, col)
    ctx.set_line_width(r * 0.3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def call_button(ctx, cx, cy, r, red, pressed=False):
    rr = r * (0.88 if pressed else 1.0)
    piece(ctx, P_ell(cx, cy, rr), hexc("#e23b3b") if red else hexc("#2fb35a"), lw=5, shadow=not pressed)
    if red:
        handset(ctx, cx, cy - rr * 0.05, rr * 0.9, (1, 1, 1), up=False)
    else:
        handset(ctx, cx, cy + rr * 0.08, rr * 0.9, (1, 1, 1), up=True)


def stamp(ctx, cx, cy, word, k, size=64, col=hexc("#e23b3b"), ang=-12):
    if k <= 0:
        return
    sc = ease_out_back(clamp(k / 0.25)) if k < 0.25 else 1.0
    e = g.text_size(ctx, word, size)
    w, h = e.width + 50, size + 34
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(math.radians(ang))
    ctx.scale(sc, sc)
    P_rrect(-w / 2, -h / 2, w, h, 14)(ctx)
    ctx.set_source_rgba(1, 1, 1, 0.75)
    ctx.fill_preserve()
    set_col(ctx, col)
    ctx.set_line_width(9)
    ctx.stroke()
    draw_text(ctx, word, 0, 0, size, col, INK, 0)
    ctx.restore()


def since(ev, key, lt):
    v = ev.get(key + "_lt")
    return -1.0 if v is None else lt - v


# ─────────────────────────────── escenas ───────────────────────────────
def screen_alerta(lt, dim=0.0):
    def f(ctx, sx, sy, sw, sh):
        set_col(ctx, hexc("#121a33"))
        ctx.paint()
        txt(ctx, "9:41", sx + 46, sy + 62, 30, (1, 1, 1), "Inter")
        # notificación roja
        cx = sx + sw / 2
        piece(ctx, P_rrect(sx + 26, sy + 110, sw - 52, 270, 26), hexc("#e23b3b"), lw=4)
        piece(ctx, P_poly([(sx + 76, sy + 150), (sx + 106, sy + 200), (sx + 46, sy + 200)]), hexc("#ffd23f"),
              lw=3, shadow=False)
        txt(ctx, "!", sx + 70, sy + 194, 34, INK)
        txt(ctx, "AVISO URGENTE", sx + 124, sy + 192, 36, (1, 1, 1))
        for i, l in enumerate(["Tu cuenta ha sido", "bloqueada."]):
            txt(ctx, l, sx + 56, sy + 262 + i * 46, 38, (1, 1, 1), "Inter")
        # cuenta atrás
        rest = max(0, 600 - int(lt * 9))
        txt(ctx, "TIENES", cx, sy + 470, 36, hexc("#a9b4d6"), anchor="center")
        txt(ctx, f"{rest // 60:02d}:{rest % 60:02d}", cx, sy + 610, 132, hexc("#ff4d4d"), anchor="center")
        # botón trampa
        pulse = 1.0 + (0.05 if (int(lt * 12) // 3) % 2 else 0)
        bw, bh = (sw - 120) * pulse, 104 * pulse
        piece(ctx, P_rrect(cx - bw / 2, sy + 690, bw, bh, 52), hexc("#ffd23f"), lw=5)
        txt(ctx, "VERIFICAR YA", cx, sy + 690 + bh / 2 + 15, 42, INK, anchor="center")
        if dim > 0:
            ctx.set_source_rgba(0, 0, 0, 0.55 * dim)
            ctx.paint()
    return f


def sc_alerta(ctx, pose, lt, ev):
    burst(ctx, 540, 900, 24, hexc("#3a1530"), hexc("#4a1a3a"), phase=(pose // 3) * 0.06)
    hung = since(ev, "cuelga", lt)
    vib = hung < 0
    ang = math.radians(1.6) * (1 if pose % 2 else -1) if vib else 0.0
    phone(ctx, 540, 940, 540, 1000, hexc("#121a33"), screen_alerta(lt, clamp(hung / 0.3) if hung >= 0 else 0),
          ang)
    if vib:
        for side in (-1, 1):
            for k in range(2):
                r = 60 + k * 40 + (pose % 2) * 8
                ctx.new_sub_path()
                ctx.arc(540 + side * 300, 760, r, math.radians(-40 if side > 0 else 140),
                        math.radians(40 if side > 0 else 220))
                ctx.set_source_rgb(1, 1, 1)
                ctx.set_line_width(10)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
    if hung >= 0:
        k = clamp(hung / 0.3)
        sc = ease_out_back(k) if k < 1 else 1.0
        ctx.save()
        ctx.translate(540, 1000)
        ctx.scale(sc, sc)
        call_button(ctx, 0, 0, 150, True)
        ctx.restore()


def msg_card(ctx, x, y, w, head, body, icon_col, icon, t_in, t_stamp):
    if t_in < 0:
        return 0
    k = clamp(t_in / 0.35)
    x = x + (1 - ease_io(k)) * (w + 120)
    lines = wrap(ctx, body, 30, w - 48)
    hgt = 92 + 40 * len(lines) + 12
    piece(ctx, P_rrect(x, y, w, hgt, 24), (1, 1, 1), lw=4)
    piece(ctx, P_ell(x + 46, y + 46, 24), icon_col, lw=3, shadow=False)
    txt(ctx, icon, x + 46, y + 58, 30, (1, 1, 1), anchor="center")
    txt(ctx, head, x + 84, y + 58, 30, INK)
    for i, l in enumerate(lines):
        txt(ctx, l, x + 26, y + 116 + i * 40, 30, hexc("#33364a"), "Inter")
    if t_stamp >= 0:
        stamp(ctx, x + w - 92, y + 44, "FALSO", t_stamp, 40, ang=8)
    return hgt


def sc_mensajes(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3b2f6b"))
    ctx.paint()
    for i in range(-10, 30):
        ctx.move_to(i * 90, 0)
        ctx.line_to(i * 90 - 800, 1920)
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.set_line_width(30)
        ctx.stroke()
    cards = [("SMS · BANCO", "Pago bloqueado. Verifica tus datos YA en este enlace.", hexc("#1d4ed8"), "€", "m1"),
             ("SOPORTE TÉCNICO", "Su ordenador tiene un virus. Instale esto YA.", hexc("#7c3aed"), "!", "m2"),
             ("Nº DESCONOCIDO", "Mamá, se me rompió el móvil. Necesito 500 € YA.", hexc("#16a34a"), "?", "m3")]

    def screen(c, sx, sy, sw, sh):
        set_col(c, hexc("#e9ecf4"))
        c.paint()
        piece(c, P_rect(sx, sy, sw, 96), hexc("#ffffff"), lw=0, shadow=False, outline=False)
        txt(c, "Mensajes", sx + sw / 2, sy + 72, 36, INK, anchor="center")
        y = sy + 120
        for head, body, col, ic, key in cards:
            d = since(ev, key, lt)
            h = msg_card(c, sx + 18, y, sw - 36, head, body, col, ic, d, d - 0.8)
            y += h + 18

    phone(ctx, 540, 930, 600, 1000, hexc("#e9ecf4"), screen, math.radians(-2))


def gauge(ctx, cx, cy, r, v, pose):
    piece(ctx, P_poly([(cx - r - 26, cy + 20), (cx + r + 26, cy + 20), (cx + r + 26, cy + 30),
                       (cx - r - 26, cy + 30)]), hexc("#3d3f4a"), lw=3)
    for a0, a1, col in ((math.pi, 1.5 * math.pi, "#2fb35a"), (1.5 * math.pi, 2 * math.pi, "#e23b3b")):
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, r, a0, a1)
        ctx.close_path()
        set_col(ctx, hexc(col))
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
    piece(ctx, P_ell(cx, cy, r * 0.42), hexc("#f6f1e2"), lw=4, shadow=False)
    a = math.pi + v * math.pi
    line(ctx, [(cx, cy), (cx + r * 0.92 * math.cos(a), cy + r * 0.92 * math.sin(a))], 14)
    piece(ctx, P_ell(cx, cy, 18), INK, shadow=False)
    draw_text(ctx, "LÓGICA", cx - r * 1.0, cy + 72, 40, hexc("#2fb35a"), INK, 5)
    draw_text(ctx, "INSTINTO", cx + r * 1.0, cy + 72, 40, hexc("#ff5a5a"), INK, 5)


def bolt(ctx, x, y, s):
    pts = [(0, -60), (30, -60), (12, -10), (38, -10), (-18, 70), (-2, 8), (-26, 8)]
    piece(ctx, P_poly([(x + px * s, y + py * s) for px, py in pts]), hexc("#ffe14d"), lw=4, shadow=False)


def bubble(ctx, cx, cy, w, h, tail, lines_, size, col=(1, 1, 1), think=False):
    if think:
        blobs = [(-w * 0.32, 0, h * 0.45), (0, -h * 0.12, h * 0.55), (w * 0.32, 0, h * 0.45),
                 (-w * 0.12, h * 0.18, h * 0.42), (w * 0.14, h * 0.18, h * 0.42)]
        for dx, dy, r in blobs:
            piece(ctx, P_ell(cx + dx, cy + dy, r * 1.25, r), col, lw=4, shadow=False)
        for dx, dy, r in blobs:
            P_ell(cx + dx, cy + dy, r * 1.25 - 4, r - 4)(ctx)
            set_col(ctx, col)
            ctx.fill()
        for i, f in enumerate((0.35, 0.65)):
            px = lerp(cx, tail[0], f)
            py = lerp(cy + h * 0.5, tail[1], f)
            piece(ctx, P_ell(px, py, 18 - i * 6), col, lw=4, shadow=False)
    else:
        x0, y0 = cx - w / 2, cy - h / 2
        bx = clamp(tail[0], x0 + 40, x0 + w - 40)
        piece(ctx, P_poly([(bx - 30, y0 + h - 4), (bx + 30, y0 + h - 4), tail]), col, lw=5)
        piece(ctx, P_rrect(x0, y0, w, h, 30), col, lw=5)
        P_rect(bx - 26, y0 + h - 8, 52, 10)(ctx)
        set_col(ctx, col)
        ctx.fill()
    n = len(lines_)
    for i, l in enumerate(lines_):
        draw_text(ctx, l, cx, cy + (i - (n - 1) / 2) * size * 1.1, size, INK, INK, 0)


def bank_icon(ctx, cx, cy, s):
    piece(ctx, P_poly([(cx - 60 * s, cy - 20 * s), (cx + 60 * s, cy - 20 * s), (cx, cy - 60 * s)]),
          hexc("#1d4ed8"), lw=3, shadow=False)
    for k in range(4):
        piece(ctx, P_rect(cx - 50 * s + k * 30 * s, cy - 14 * s, 14 * s, 50 * s), hexc("#1d4ed8"), lw=2,
              shadow=False)
    piece(ctx, P_rect(cx - 62 * s, cy + 36 * s, 124 * s, 14 * s), hexc("#1d4ed8"), lw=3, shadow=False)


def hourglass(ctx, cx, cy, s, pose):
    piece(ctx, P_poly([(cx - 30 * s, cy - 44 * s), (cx + 30 * s, cy - 44 * s), (cx, cy), (cx + 30 * s, cy + 44 * s),
                       (cx - 30 * s, cy + 44 * s), (cx, cy)]), hexc("#f6d38a"), lw=3, shadow=False)
    lvl = (pose % 12) / 12
    piece(ctx, P_poly([(cx - 30 * s * (1 - lvl), cy + 44 * s - 40 * s * lvl), (cx + 30 * s * (1 - lvl),
                                                                               cy + 44 * s - 40 * s * lvl),
                       (cx + 30 * s, cy + 44 * s), (cx - 30 * s, cy + 44 * s)]), hexc("#c27a1a"), lw=2,
          shadow=False)
    line(ctx, [(cx - 36 * s, cy - 46 * s), (cx + 36 * s, cy - 46 * s)], 8)
    line(ctx, [(cx - 36 * s, cy + 46 * s), (cx + 36 * s, cy + 46 * s)], 8)


def sc_cerebro(ctx, pose, lt, ev):
    set_col(ctx, hexc("#5f8f86"))
    ctx.paint()
    for i in range(8):
        line(ctx, [(i * 150 + 40, 0), (i * 150 + 40, 1300)], 3, (0, 0, 0, 0.08))
    piece(ctx, P_rect(-10, 1300, 1100, 640), hexc("#8b5e3c"), lw=4, shadow=False)
    # cuadro en la pared
    piece(ctx, P_rect(860, 830, 150, 115), hexc("#f6eab0"), lw=6)
    piece(ctx, P_poly([(872, 932), (920, 875), (955, 910), (998, 865), (998, 932)]), hexc("#2f6b45"), lw=3,
          shadow=False)
    # sofá
    piece(ctx, P_rrect(170, 1040, 740, 330, 40), hexc("#b5473a"), lw=5)
    tu = since(ev, "urgencia", lt)
    tr = since(ev, "rapido", lt)
    tired = clamp(0.2 + 0.5 * clamp(lt / max(1.0, ev.get("dur", 20) * 0.6)))
    droop = math.radians(3) * (1 if (pose // 5) % 2 else -1) * (1.6 if tr >= 0 else 0.6)
    boy(ctx, 540, 1080, tired, droop, 0, 1.0, pose)
    # mano con el móvil en la oreja
    piece(ctx, P_rrect(668, 960, 64, 128, 14), hexc("#23242c"), lw=4)
    piece(ctx, P_ell(700, 1080, 40, 44), BOY_SKIN, lw=4)
    piece(ctx, P_rrect(660, 1110, 80, 210, 30), hexc("#ef7d2d"), lw=4)
    # asiento y brazos del sofá delante
    piece(ctx, P_rrect(150, 1330, 780, 150, 30), hexc("#c75446"), lw=5)
    piece(ctx, P_rrect(110, 1150, 120, 330, 40), hexc("#a63f33"), lw=5)
    piece(ctx, P_rrect(850, 1150, 120, 330, 40), hexc("#a63f33"), lw=5)
    # medidor lógica / instinto
    if tu < 0:
        v = 0.22
    elif tr < 0:
        v = lerp(0.22, 0.5, clamp(tu / 1.2))
    else:
        v = lerp(0.5, 0.88, ease_io(tr / 0.4)) + (0.04 if pose % 2 else -0.02)
    gauge(ctx, 540, 700, 150, v, pose)
    if tr >= 0 and (pose // 2) % 2 == 0:
        bolt(ctx, 300, 660, 0.9)
        bolt(ctx, 790, 660, 0.9)
    ts, ta, te = since(ev, "sentido", lt), since(ev, "autoridad", lt), since(ev, "escasez", lt)
    if ts >= 0 and ta < 0:
        bubble(ctx, 280, 920, 330, 150, (430, 1010), ["¿ESTO TIENE", "SENTIDO?"], 38, think=True)
    if ta >= 0 and te < 0:
        bubble(ctx, 850, 905, 360, 140, (720, 1000), ["SOY DEL", "BANCO"], 50)
        bank_icon(ctx, 990, 815, 0.6)
    if te >= 0:
        bubble(ctx, 820, 905, 420, 140, (720, 1000), ["¡ÚLTIMA", "OPORTUNIDAD!"], 48, col=hexc("#ffe14d"))
        hourglass(ctx, 1000, 800, 0.8, pose)


def sc_regla(ctx, pose, lt, ev):
    burst(ctx, 540, 960, 20, hexc("#1e5a4c"), hexc("#226452"), phase=0.0)
    tc, tk, to = since(ev, "claves", lt), since(ev, "cuelga", lt), since(ev, "oficial", lt)

    def screen(c, sx, sy, sw, sh):
        cx = sx + sw / 2
        if to >= 0:
            set_col(c, hexc("#1f8a4c"))
            c.paint()
            txt(c, "Llamando…", cx, sy + 200, 46, (1, 1, 1), "Inter", anchor="center")
            txt(c, "NÚMERO", cx, sy + 300, 70, (1, 1, 1), anchor="center")
            txt(c, "OFICIAL", cx, sy + 380, 70, (1, 1, 1), anchor="center")
            kk = clamp(to / 0.3)
            c.save()
            c.translate(cx, sy + 590)
            s = ease_out_back(kk) if kk < 1 else 1.0
            c.scale(s, s)
            c.move_to(-90, 0)
            c.line_to(-25, 70)
            c.line_to(100, -80)
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.set_source_rgb(*INK)
            c.set_line_width(64)
            c.stroke_preserve()
            c.set_source_rgb(1, 1, 1)
            c.set_line_width(40)
            c.stroke()
            c.restore()
            return
        set_col(c, hexc("#20304f"))
        c.paint()
        if tk >= 0.15:
            txt(c, "Llamada", cx, sy + 420, 60, hexc("#ff6b6b"), anchor="center")
            txt(c, "finalizada", cx, sy + 500, 60, hexc("#ff6b6b"), anchor="center")
            return
        piece(c, P_ell(cx, sy + 230, 92), hexc("#8a93ad"), lw=4, shadow=False)
        txt(c, "?", cx, sy + 268, 110, (1, 1, 1), anchor="center")
        txt(c, "BANCO (?)", cx, sy + 400, 58, (1, 1, 1), anchor="center")
        txt(c, "Llamada entrante…", cx, sy + 456, 32, hexc("#a9b4d6"), "Inter", anchor="center")
        call_button(c, sx + sw * 0.27, sy + sh - 150, 72, True, pressed=(0 <= tk < 0.15))
        call_button(c, sx + sw * 0.73, sy + sh - 150, 72, False)
        if tc >= 0:
            piece(c, P_rrect(sx + 40, sy + 520, sw - 80, 150, 22), (1, 1, 1), lw=4)
            txt(c, "CLAVE: ● ● ● ●", cx, sy + 612, 44, INK, "Inter", anchor="center")
            k = clamp(tc / 0.25)
            line(c, [(sx + 70, sy + 540), (sx + 70 + (sw - 140) * k, sy + 540 + 110 * k)], 16, hexc("#e23b3b"))
            if k >= 1:
                line(c, [(sx + sw - 70, sy + 540), (sx + 70, sy + 650)], 16, hexc("#e23b3b"))
            stamp(c, cx, sy + 690, "NUNCA", tc - 0.3, 44, ang=-6)

    phone(ctx, 540, 930, 560, 1000, hexc("#20304f"), screen)
    # mano que cuelga
    if -0.6 <= tk < 0.9 and to < 0:
        bx, by = 540 - 280 + 22 + 516 * 0.27, 930 - 500 + 22 + 956 - 150
        k = clamp((tk + 0.6) / 0.5) if tk < 0.15 else 1 - clamp((tk - 0.35) / 0.5)
        tx, ty = lerp(820, bx, ease_io(k)), lerp(1900, by + 10, ease_io(k))
        piece(ctx, P_rrect(tx + 30, ty + 210, 170, 420, 50), hexc("#ef7d2d"), lw=5)
        piece(ctx, P_ell(tx + 70, ty + 220, 100, 120), BOY_SKIN, lw=5)
        piece(ctx, P_rrect(tx - 28, ty - 10, 58, 230, 29), BOY_SKIN, lw=5)
        line(ctx, [(tx - 10, ty + 20), (tx + 12, ty + 20)], 4, (0, 0, 0, 0.4))


def plane(ctx, x, y, ang, s):
    with rot(ctx, x, y, ang):
        piece(ctx, P_poly([(x + 90 * s, y), (x - 70 * s, y - 50 * s), (x - 40 * s, y + 4 * s)]), (1, 1, 1),
              lw=4)
        piece(ctx, P_poly([(x + 90 * s, y), (x - 40 * s, y + 4 * s), (x - 60 * s, y + 46 * s)]),
              hexc("#d6dcef"), lw=4, shadow=False)


def sc_compartir(ctx, pose, lt, ev):
    burst(ctx, 540, 1000, 22, hexc("#1d4ed8"), hexc("#2458e6"), phase=(pose // 4) * 0.05)

    def left(c, sx, sy, sw, sh):
        set_col(c, hexc("#eef1fa"))
        c.paint()
        cx, cy = sx + sw / 2, sy + sh / 2
        pts = [(cx + 70, cy - 90), (cx - 70, cy), (cx + 70, cy + 90)]
        line(c, [pts[0], pts[1], pts[2]], 14, hexc("#1d4ed8"))
        for p in pts:
            piece(c, P_ell(p[0], p[1], 38), hexc("#1d4ed8"), lw=4, shadow=False)
        txt(c, "COMPARTIR", cx, sy + sh - 90, 40, INK, anchor="center")

    arrive = clamp(lt / 1.3)

    def right(c, sx, sy, sw, sh):
        set_col(c, hexc("#eef1fa"))
        c.paint()
        for i in range(6):
            piece(c, P_rrect(sx + 24, sy + 90 + i * 86, sw - 48, 66, 16), (1, 1, 1), lw=3, shadow=False)
            line(c, [(sx + 50, sy + 123 + i * 86), (sx + sw - 90 - 30 * (i % 3), sy + 123 + i * 86)], 8,
                 hexc("#c3c9dc"))

    shake = math.radians(3) * (1 if pose % 2 else -1) if arrive >= 1 else 0
    phone(ctx, 280, 1020, 360, 660, hexc("#eef1fa"), left, math.radians(-7))
    phone(ctx, 800, 1000, 360, 660, hexc("#eef1fa"), right, math.radians(6) + shake)
    badge_k = clamp((lt - 1.3) / 0.3)
    piece(ctx, P_ell(950, 690, 62 * (ease_out_back(badge_k) if 0 < badge_k < 1 else 1)), hexc("#e23b3b"), lw=5)
    txt(ctx, "99+", 950, 706, 44, (1, 1, 1), anchor="center")
    # avión de papel con estela
    p = ease_io(arrive)
    x0, y0, x1, y1 = 330, 860, 760, 860
    for i in range(1, 9):
        q = p * i / 9
        px, py = lerp(x0, x1, q), lerp(y0, y1, q) - math.sin(q * math.pi) * 300
        piece(ctx, P_ell(px, py, 7), (1, 1, 1), shadow=False, lw=2)
    if arrive < 1:
        px, py = lerp(x0, x1, p), lerp(y0, y1, p) - math.sin(p * math.pi) * 300
        ang = math.atan2(-math.cos(p * math.pi) * 300 * math.pi, x1 - x0)
        plane(ctx, px, py, ang, 1.2)


SCENES = dict(alerta=sc_alerta, mensajes=sc_mensajes, cerebro=sc_cerebro, regla=sc_regla, compartir=sc_compartir)


def miniatura(path):
    W, H = g.W, g.H
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    sc_alerta(ctx, 1, 0.1, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(5))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "LA PALABRA FAVORITA", 540, 210, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "DE UN ESTAFADOR:", 540, 350, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "«YA»", 540, 1560, 300, hexc("#ffe14d"), INK, math.radians(-4), 1.0)
    surf.write_to_png(path)


def configurar():
    g.BLOQUES[:] = BLOQUES
    g.SCENES.clear()
    g.SCENES.update(SCENES)
    g.RECORTES_SUGERIDOS[:] = RECORTES
    g.SALIDA = "estafas-ya"
    d = os.path.join(g.CACHE_DIR, "estafas")
    os.makedirs(d, exist_ok=True)
    g.CACHE_DIR = d
    g.NARR_JSON = os.path.join(d, "narracion_palabras.json")
    g.NARR_MP3 = os.path.join(d, "narracion.mp3")
    g.thumbnail = miniatura


if __name__ == "__main__":
    configurar()
    g.main()
