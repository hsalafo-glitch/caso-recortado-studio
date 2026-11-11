#!/usr/bin/env python3
"""
Short 5 · «Recuerdas algo que nunca te pasó» (recuerdos falsos)
Motor: generar_short.py · utilidades de los shorts anteriores · voz Salva (eleven_v4)

Uso:
    python short_recuerdos.py            # vídeo final (usa cache_audio/recuerdos-falsos/)
    python short_recuerdos.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, BOY_SKIN, P_ell, P_poly, P_rect, P_rrect, boy, card_text, clamp, draw_text,
                           ease_io, ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, since, stamp, txt
from short_obediencia import SKIN, adulto
from short_mentiras import persona_a

SLUG = "recuerdos-falsos"

# ─────────────────────────────── guion (versión recortada aprobada) ───────────────────────────────
BLOQUES = [
    dict(
        id="gancho",
        voz="Imagina que recuerdas perfectamente algo de tu infancia… que nunca te pasó.",
        escenas=[(None, "centro")],
        pantalla=[("nunca te pasó", "¿Y SI NUNCA PASÓ?")],
        eventos={"grieta": "nunca te pasó"},
    ),
    dict(
        id="estudio",
        voz=("1995. La psicóloga Elizabeth Loftus da a 24 personas cuatro historias de su infancia, "
             "contadas por sus familiares. Tres son reales. La cuarta, inventada: de niños se perdieron "
             "en un centro comercial y un anciano los ayudó."),
        escenas=[(None, "laboratorio"), ("cuatro historias", "cuadernillo"), ("de niños", "anciano")],
        pantalla=[("24 personas", "24 PERSONAS"), ("Tres son reales", "3 REALES + 1 FALSA")],
        eventos={"tres": "Tres son reales", "cuarta": "La cuarta"},
    ),
    dict(
        id="resultado",
        voz=("Al recordarlas, una de cada cuatro empieza a recordar la falsa. "
             "Y algunas añaden detalles que nadie les contó: cómo era el anciano, si lloraron…"),
        escenas=[(None, "siluetas24"), ("Y algunas", "detalles")],
        pantalla=[("una de cada", "1 DE CADA 4")],
        eventos={"una": "una de cada", "anciano": "cómo era", "lloraron": "si lloraron"},
    ),
    dict(
        id="memoria",
        voz=("La memoria no es un vídeo: cada vez que recuerdas, tu cerebro lo reconstruye. "
             "Y si alguien de confianza te da una pieza falsa, encaja sin que lo notes."),
        escenas=[(None, "cinta"), ("cada vez que", "puzle")],
        pantalla=[("cada vez que", "RECORDAR = RECONSTRUIR")],
        eventos={"tacha": "no es un", "falsa": "pieza falsa", "encaja": "encaja sin"},
    ),
    dict(
        id="testigos",
        voz=("Por eso, en casi 7 de cada 10 condenas anuladas por ADN en Estados Unidos, "
             "un testigo señaló al inocente. ¿Seguro que todo lo que recuerdas pasó de verdad?"),
        escenas=[(None, "rueda")],
        pantalla=[("casi 7", "7 DE CADA 10"), ("Seguro que", "¿SEGURO QUE PASÓ?")],
        eventos={"senala": "un testigo", "inocente": "al inocente"},
    ),
]

RECORTES = ["Bloque 3: «si lloraron» (≈0,8 s)", "Bloque 5: «en Estados Unidos» (≈1 s)"]


# ─────────────────────────────── piezas ───────────────────────────────
def nino(ctx, x, y, s=0.62, look=0.0, expr_tired=0.0, pose=0):
    """El chico de siempre, más pequeño, de pie (con piernas)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    piece(ctx, P_rect(-60, 310, 50, 130), hexc("#2c4479"), lw=5)
    piece(ctx, P_rect(10, 310, 50, 130), hexc("#2c4479"), lw=5)
    piece(ctx, P_rrect(-74, 430, 70, 26, 10), INK, lw=3, shadow=False)
    piece(ctx, P_rrect(4, 430, 70, 26, 10), INK, lw=3, shadow=False)
    boy(ctx, 0, 0, expr_tired, math.radians(2) * (1 if (pose // 6) % 2 else -1), 0, look, pose)
    ctx.restore()


def anciano(ctx, x, y, r=95, pose=0, look=0.0):
    piece(ctx, P_rect(x - 55, y + r * 2.9, 46, 160), hexc("#5a4a3a"), lw=4)
    piece(ctx, P_rect(x + 9, y + r * 2.9, 46, 160), hexc("#5a4a3a"), lw=4)
    adulto(ctx, x, y, r, traje="#b58b5a", pelo="#e8e8e8", expr="sonrisa", look=look, gafas=True, pose=pose)
    line(ctx, [(x + r * 1.5, y + r * 1.6), (x + r * 1.7, y + r * 4.5)], 10, hexc("#6b3a1f"))


def tiendas(ctx, pose):
    set_col(ctx, hexc("#f3e6c9"))
    ctx.paint()
    cols = ["#e63946", "#1d4ed8", "#16a34a", "#f59e0b", "#7c3aed"]
    for row, y0 in enumerate((180, 640)):
        for i in range(4):
            x0 = -60 + i * 300 + row * 140
            c = hexc(cols[(i + row * 2) % 5])
            piece(ctx, P_rect(x0, y0, 260, 380), hexc("#fbf6ea"), lw=4)
            piece(ctx, P_rect(x0 + 20, y0 + 120, 220, 220), hexc("#bfe3f2"), lw=4, shadow=False)
            for k in range(5):
                piece(ctx, P_poly([(x0 + k * 52, y0 + 60), (x0 + (k + 1) * 52, y0 + 60), (x0 + (k + 0.5) * 52, y0 + 110)]),
                      c if k % 2 == 0 else (1, 1, 1), lw=3, shadow=False)
            piece(ctx, P_rect(x0, y0, 260, 60), c, lw=4, shadow=False)
    piece(ctx, P_rect(-10, 1080, 1100, 900), hexc("#d9cfbd"), lw=4, shadow=False)
    for i in range(12):
        line(ctx, [(i * 110 - 200, 1080), (i * 160 - 500, 1940)], 3, (0, 0, 0, 0.12))
    for j in range(6):
        line(ctx, [(0, 1080 + j * 70 + j * j * 8), (1080, 1080 + j * 70 + j * j * 8)], 3, (0, 0, 0, 0.1))


def grietas(ctx, cx, cy, k, seed=3):
    if k <= 0:
        return
    for i in range(11):
        a = i * 2 * math.pi / 11 + hnoise(seed, i) * 0.4
        L = (500 + 700 * hnoise(seed, i, "l")) * k
        pts = [(cx, cy)]
        x, y = cx, cy
        n = 6
        for j in range(1, n + 1):
            d = L / n
            aa = a + (hnoise(seed, i, j) - 0.5) * 0.7
            x, y = x + d * math.cos(aa), y + d * math.sin(aa)
            pts.append((x, y))
        line(ctx, pts, 9, INK)
        line(ctx, pts, 4, (1, 1, 1, 0.9))
    ctx.new_sub_path()
    ctx.arc(cx, cy, 160 * k, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.set_line_width(5)
    ctx.stroke()


def foto(ctx, x, y, w, h, dibujo, borde=None, ang=0.0):
    with rot(ctx, x, y, ang):
        piece(ctx, P_rect(x - w / 2, y - h / 2, w, h), (1, 1, 1), lw=5 if borde is None else 0,
              outline=borde is None)
        if borde is not None:
            P_rect(x - w / 2, y - h / 2, w, h)(ctx)
            set_col(ctx, borde)
            ctx.set_line_width(14)
            ctx.stroke()
        ctx.save()
        P_rect(x - w / 2 + 16, y - h / 2 + 16, w - 32, h - 70)(ctx)
        ctx.clip()
        dibujo(x, y - 20, w - 32, h - 70)
        ctx.restore()


def make_dibujos(ctx):
    def tarta(x, y, w, h):
        set_col(ctx, hexc("#ffd6e0"))
        ctx.paint()
        piece(ctx, P_rect(x - 70, y, 140, 70), hexc("#a0522d"), lw=3, shadow=False)
        piece(ctx, P_rect(x - 70, y - 14, 140, 20), hexc("#fff5f8"), lw=3, shadow=False)
        for k in (-40, 0, 40):
            piece(ctx, P_rect(x + k - 5, y - 54, 10, 40), hexc("#ffe14d"), lw=2, shadow=False)
            piece(ctx, P_ell(x + k, y - 62, 6, 10), hexc("#ff7a1a"), lw=2, shadow=False)

    def playa(x, y, w, h):
        set_col(ctx, hexc("#8ec5e8"))
        ctx.paint()
        piece(ctx, P_rect(x - w / 2, y + 20, w, h), hexc("#f2d38b"), lw=0, shadow=False, outline=False)
        piece(ctx, P_rect(x - w / 2, y - 10, w, 30), hexc("#2f7fc1"), lw=0, shadow=False, outline=False)
        piece(ctx, P_ell(x + 60, y - 70, 26), hexc("#ffe14d"), lw=3, shadow=False)

    def bici(x, y, w, h):
        set_col(ctx, hexc("#cfe9c9"))
        ctx.paint()
        for dx in (-50, 50):
            ctx.new_sub_path()
            ctx.arc(x + dx, y + 30, 34, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        line(ctx, [(x - 50, y + 30), (x, y - 10), (x + 50, y + 30), (x - 10, y + 30), (x - 50, y + 30)], 6,
             hexc("#e63946"))

    def centro(x, y, w, h):
        set_col(ctx, hexc("#f3e6c9"))
        ctx.paint()
        for i in range(3):
            piece(ctx, P_rect(x - 110 + i * 75, y - 60, 65, 90), hexc(["#e63946", "#1d4ed8", "#16a34a"][i]), lw=2,
                  shadow=False)
        txt(ctx, "?", x, y + 75, 60, hexc("#e23b3b"), anchor="center")

    return [tarta, playa, bici, centro]


# ─────────────────────────────── escenas ───────────────────────────────
def sc_centro(ctx, pose, lt, ev):
    tiendas(ctx, pose)
    nino(ctx, 540, 1000, 0.62, look=-0.6 if (pose // 12) % 2 else 0.6, pose=pose)
    tg = since(ev, "grieta", lt)
    if tg >= 0:
        k = clamp(tg / 0.35)
        grietas(ctx, 560, 820, k)


def sc_laboratorio(ctx, pose, lt, ev):
    set_col(ctx, hexc("#d6e6ee"))
    ctx.paint()
    for y in (560, 760):
        piece(ctx, P_rect(80, y, 380, 18), hexc("#8a5a34"), lw=3)
        for i in range(4):
            c = hexc(["#16a34a", "#e63946", "#1d4ed8", "#f59e0b"][i])
            x = 120 + i * 90
            piece(ctx, P_poly([(x, y), (x + 50, y), (x + 40, y - 70), (x + 10, y - 70)]), c, lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1260, 1100, 700), hexc("#9aa3ad"), lw=4, shadow=False)
    piece(ctx, P_rect(120, 1060, 840, 50), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_rect(160, 1110, 40, 160), hexc("#5d3a22"), lw=4)
    piece(ctx, P_rect(880, 1110, 40, 160), hexc("#5d3a22"), lw=4)
    # montón de 24 cuadernillos
    for i in range(8):
        piece(ctx, P_rect(560 + (i % 2) * 6, 1030 - i * 22, 260, 24), hexc("#f6eab0") if i % 2 else (1, 1, 1),
              lw=3, sh=(3, 3))
    piece(ctx, P_rrect(600, 800, 180, 70, 12), hexc("#1d4ed8"), lw=4)
    draw_text(ctx, "× 24", 690, 836, 46, (1, 1, 1), INK, 0)
    # cartel 1995
    piece(ctx, P_rrect(600, 520, 330, 160, 18), hexc("#e63946"), lw=6)
    draw_text(ctx, "1995", 765, 600, 100, (1, 1, 1), INK, 6)
    # silueta de la investigadora (sin rasgos)
    silhouette(ctx, 330, 1070, 1.05, math.radians(2) * (1 if (pose // 6) % 2 else -1), hexc("#3a3f66"),
               hexc("#6b72a8"))


def sc_cuadernillo(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    k = clamp(lt / 0.4)
    # cuadernillo abierto
    w = lerp(80, 920, ease_io(k))
    piece(ctx, P_rrect(540 - w / 2, 560, w, 860, 20), hexc("#8a5a34"), lw=6)
    piece(ctx, P_rect(540 - w / 2 + 20, 580, w - 40, 820), hexc("#fbf6ea"), lw=4, shadow=False)
    line(ctx, [(540, 580), (540, 1400)], 4, (0, 0, 0, 0.3))
    if k < 1:
        return
    dib = make_dibujos(ctx)
    tt, tc = since(ev, "tres", lt), since(ev, "cuarta", lt)
    pos = [(320, 790), (760, 790), (320, 1180), (760, 1180)]
    for i, ((x, y), d) in enumerate(zip(pos, dib)):
        borde = None
        if i < 3 and tt >= 0 and tt >= i * 0.25:
            borde = hexc("#2fb35a")
        if i == 3 and tc >= 0:
            borde = hexc("#e23b3b")
        foto(ctx, x, y, 330, 330, d, borde, math.radians([-3, 2, 3, -2][i]))
        if borde is not None:
            piece(ctx, P_ell(x + 140, y - 140, 40), borde, lw=4, shadow=False)
            if i < 3:
                line(ctx, [(x + 118, y - 140), (x + 136, y - 120), (x + 162, y - 158)], 9, (1, 1, 1))
            else:
                line(ctx, [(x + 124, y - 156), (x + 156, y - 124)], 9, (1, 1, 1))
                line(ctx, [(x + 156, y - 156), (x + 124, y - 124)], 9, (1, 1, 1))


def sc_anciano(ctx, pose, lt, ev):
    tiendas(ctx, pose)
    anciano(ctx, 690, 760, 100, pose, look=-1.0)
    nino(ctx, 390, 950, 0.55, look=1.0, pose=pose)
    # manos unidas
    line(ctx, [(560, 1080), (515, 1110)], 26, hexc("#b58b5a"))
    line(ctx, [(460, 1110), (505, 1115)], 22, hexc("#ef7d2d"))
    piece(ctx, P_ell(512, 1112, 28), BOY_SKIN, lw=4)
    piece(ctx, P_rrect(170, 620, 250, 90, 14), hexc("#e63946"), lw=5)
    draw_text(ctx, "¿Y MAMÁ?", 295, 665, 44, (1, 1, 1), INK, 0)


def sc_siluetas24(ctx, pose, lt, ev):
    set_col(ctx, hexc("#141a33"))
    ctx.paint()
    tu = since(ev, "una", lt)
    n = int(6 * clamp(tu / 1.2)) if tu >= 0 else 0
    lit = set(sorted(range(24), key=lambda i: hnoise("r24", i))[:n])
    for i in range(24):
        r, c = divmod(i, 6)
        x, feet = 140 + c * 160, 760 + r * 175
        on = i in lit
        silhouette(ctx, x, feet, 0.44, 0.0, hexc("#f2b632") if on else hexc("#3a3f66"),
                   hexc("#fff0a8") if on else hexc("#5c6399"))
    draw_text(ctx, f"{n} DE 24", 540, 1350, 74, hexc("#f2b632") if n else (1, 1, 1), INK, 7)


def sc_detalles(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1330, 1100, 600), hexc("#1d2440"), lw=4, shadow=False)
    persona_a(ctx, 540, 1060, 110, "preocupado", -0.6, pose=pose)
    # nube de pensamiento que se llena
    cx, cy = 540, 700
    bubble(ctx, cx, cy, 700, 300, (560, 920), [""], 40, think=True)
    ta, tl_ = since(ev, "anciano", lt), since(ev, "lloraron", lt)
    # recuerdo base: el anciano dando la mano
    piece(ctx, P_ell(cx - 90, cy - 10, 85), SKIN, lw=4, shadow=False)
    piece(ctx, P_ell(cx - 90, cy - 80, 86, 38), hexc("#e8e8e8"), lw=3, shadow=False)
    piece(ctx, P_ell(cx + 80, cy + 30, 58), BOY_SKIN, lw=4, shadow=False)
    piece(ctx, P_ell(cx + 80, cy - 10, 60, 26), hexc("#3a2418"), lw=3, shadow=False)
    if ta >= 0:   # gafas del anciano
        k = ease_out_back(clamp(ta / 0.3)) if ta < 0.3 else 1
        for dx in (-32, 32):
            ctx.new_sub_path()
            ctx.arc(cx - 90 + dx, cy - 10, 26 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
    if tl_ >= 0:  # lágrima del niño
        piece(ctx, P_poly([(cx + 100, cy + 20), (cx + 116, cy + 52), (cx + 100, cy + 66), (cx + 84, cy + 52)]),
              hexc("#8fd3ff"), lw=3, shadow=False)
    if tl_ >= 0.7:  # escaparate
        piece(ctx, P_rect(cx + 170, cy - 100, 130, 150), hexc("#bfe3f2"), lw=4, shadow=False)
        piece(ctx, P_rect(cx + 170, cy - 124, 130, 30), hexc("#e63946"), lw=3, shadow=False)
    for i, (t, lab) in enumerate(((ta, "GAFAS"), (tl_, "LÁGRIMA"), (tl_ - 0.7, "ESCAPARATE"))):
        if t >= 0:
            px, py = [(200, 1100), (870, 1100), (860, 1260)][i]
            stamp(ctx, px, py, "+ " + lab, t, 46, col=hexc("#f59e0b"), ang=-4)


def cassette(ctx, cx, cy, s, pose, label="RECUERDO"):
    piece(ctx, P_rrect(cx - 380 * s, cy - 230 * s, 760 * s, 460 * s, 30 * s), hexc("#23242c"), lw=6, sh=(12, 16))
    piece(ctx, P_rrect(cx - 310 * s, cy - 190 * s, 620 * s, 110 * s, 12), (1, 1, 1), lw=4, shadow=False)
    draw_text(ctx, label, cx, cy - 135 * s, 60 * s, INK, INK, 0)
    piece(ctx, P_rrect(cx - 280 * s, cy - 40 * s, 560 * s, 190 * s, 60 * s), hexc("#3d3f4a"), lw=4, shadow=False)
    for rx in (cx - 160 * s, cx + 160 * s):
        piece(ctx, P_ell(rx, cy + 55 * s, 72 * s), hexc("#f6f1e2"), lw=4, shadow=False)
        a = pose * 0.6
        for k in range(6):
            aa = a + k * math.pi / 3
            line(ctx, [(rx + 20 * s * math.cos(aa), cy + 55 * s + 20 * s * math.sin(aa)),
                       (rx + 55 * s * math.cos(aa), cy + 55 * s + 55 * s * math.sin(aa))], 7, INK)


def sc_cinta(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3b2f6b"))
    ctx.paint()
    cassette(ctx, 540, 940, 1.1, pose)
    tt = since(ev, "tacha", lt)
    if tt >= 0:
        k = clamp(tt / 0.3)
        line(ctx, [(140, 600), (140 + 800 * k, 600 + 680 * k)], 34, hexc("#e23b3b"))
        if tt >= 0.3:
            k2 = clamp((tt - 0.3) / 0.3)
            line(ctx, [(940, 600), (940 - 800 * k2, 600 + 680 * k2)], 34, hexc("#e23b3b"))


def pieza(ctx, x, y, w, h, col, knobs, ang=0.0):
    """Pieza de puzle: rectángulo con salientes (knobs = (der, abajo)) redondos."""
    def path(c):
        c.move_to(x, y)
        c.line_to(x + w, y)
        if knobs[0]:
            c.line_to(x + w, y + h * 0.35)
            c.arc(x + w + 20, y + h * 0.5, 26, math.radians(220), math.radians(140))
            c.line_to(x + w, y + h)
        else:
            c.line_to(x + w, y + h)
        if knobs[1]:
            c.line_to(x + w * 0.65, y + h)
            c.arc(x + w * 0.5, y + h + 20, 26, math.radians(-50), math.radians(230))
        c.line_to(x, y + h)
        c.close_path()
    with rot(ctx, x + w / 2, y + h / 2, ang):
        piece(ctx, path, col, lw=5)


def sc_puzle(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    tf, te = since(ev, "falsa", lt), since(ev, "encaja", lt)
    w, h = 270, 260
    x0, y0 = 135, 620
    cols = ["#f2d38b", "#8ec5e8", "#cfe9c9", "#f6eab0", "#ffd6e0", "#d6e6ee"]
    n = min(5, 1 + int(lt / 0.5))
    falsa = 4      # la pieza que se sustituye
    for i in range(6):
        r, c = divmod(i, 3)
        x, y = x0 + c * w, y0 + r * h
        if i == falsa:
            if tf < 0:
                P_rect(x + 6, y + 6, w - 12, h - 12)(ctx)
                ctx.set_source_rgba(1, 1, 1, 0.12)
                ctx.fill()
                continue
            k = 1.0 if te >= 0 else clamp(tf / 0.8)
            xx, yy = lerp(x + 120, x, ease_io(k)), lerp(y + 520, y, ease_io(k))
            pieza(ctx, xx, yy, w, h, hexc("#e23b3b"), (c < 2, r < 1), math.radians(12 * (1 - k)))
            if te >= 0 and (pose // 3) % 2 == 0:
                draw_text(ctx, "¡ENCAJA!", x + w / 2, y + h / 2, 44, (1, 1, 1), INK, 5)
            continue
        if i < n or i == 5 and n >= 5:
            pieza(ctx, x, y, w, h, hexc(cols[i]), (c < 2, r < 1))
    # dibujo del recuerdo (niño + anciano) encima del puzle
    piece(ctx, P_ell(380, 820, 44), SKIN, lw=4, shadow=False)
    piece(ctx, P_ell(380, 785, 46, 22), hexc("#e8e8e8"), lw=3, shadow=False)
    piece(ctx, P_ell(700, 860, 34), BOY_SKIN, lw=4, shadow=False)


def sc_rueda(ctx, pose, lt, ev):
    set_col(ctx, hexc("#e6e1d3"))
    ctx.paint()
    for i in range(10):
        y = 560 + i * 70
        line(ctx, [(0, y), (1080, y)], 3 if i % 2 else 5, (0, 0, 0, 0.35))
        txt(ctx, f"{220 - i * 10}", 20, y - 8, 26, (0, 0, 0, 0.5), "Inter")
    piece(ctx, P_rect(-10, 1260, 1100, 700), hexc("#4a4d5a"), lw=4, shadow=False)
    ts, ti = since(ev, "senala", lt), since(ev, "inocente", lt)
    for i, x in enumerate((160, 350, 540, 730, 920)):
        on = i == 2 and ts >= 0
        silhouette(ctx, x, 1250, 1.0, 0.0, hexc("#e8574a") if on else hexc("#3a3f66"),
                   hexc("#ffb0a8") if on else hexc("#5c6399"))
        piece(ctx, P_rrect(x - 40, 1120, 80, 60, 8), (1, 1, 1), lw=3, shadow=False)
        draw_text(ctx, str(i + 1), x, 1150, 40, INK, INK, 0)
    if ts >= 0:
        k = clamp(ts / 0.4)
        tx, ty = lerp(-60, 515, ease_io(k)), lerp(1720, 1185, ease_io(k))
        ang = math.atan2(1185 - 1720, 515 + 60)
        with rot(ctx, tx, ty, ang):
            piece(ctx, P_rrect(tx - 520, ty - 46, 380, 92, 40), hexc("#5b6475"), lw=5)
            piece(ctx, P_ell(tx - 110, ty, 70, 60), SKIN, lw=5)
            piece(ctx, P_rrect(tx - 60, ty - 20, 70, 40, 20), SKIN, lw=5)
    if ti >= 0:
        stamp(ctx, 540, 870, "INOCENTE", ti, 70, col=hexc("#2fb35a"), ang=-10)


SCENES = dict(centro=sc_centro, laboratorio=sc_laboratorio, cuadernillo=sc_cuadernillo, anciano=sc_anciano,
              siluetas24=sc_siluetas24, detalles=sc_detalles, cinta=sc_cinta, puzle=sc_puzle, rueda=sc_rueda)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_centro(ctx, 0, 1.0, {"grieta_lt": 0.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(17))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "RECUERDAS ALGO", 540, 220, 110, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "QUE NUNCA", 540, 380, 130, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "TE PASÓ", 540, 1620, 150, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
