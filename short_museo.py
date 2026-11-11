#!/usr/bin/env python3
"""
Short 10 · «Robaron el tesoro de México en Nochebuena» — caso real (Museo Nacional de Antropología, 1985)
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_museo.py            # vídeo final (usa cache_audio/museo-nochebuena/)
    python short_museo.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, since, stamp, txt
from short_obediencia import SKIN, adulto
from short_mentiras import gorra

SLUG = "museo-nochebuena"

BLOQUES = [
    dict(
        id="gancho",
        voz=("Imagina que dos estudiantes de 21 años se llevan el mayor tesoro arqueológico de México… "
             "en plena Nochebuena."),
        escenas=[(None, "vitrina")],
        pantalla=[("en plena", "¿EN NOCHEBUENA?")],
        eventos={"llevan": "se llevan", "plena": "en plena"},
    ),
    dict(
        id="caso",
        voz=("Ciudad de México, 1985. Mientras el país celebra la Navidad, Carlos y Ramón, estudiantes de "
             "Veterinaria, se cuelan en el Museo Nacional de Antropología por los conductos del aire "
             "acondicionado."),
        escenas=[(None, "fachada"), ("se cuelan", "conducto")],
        pantalla=[(None, "CDMX, 1985"), ("se cuelan", "POR EL AIRE ACONDICIONADO")],
        eventos={"celebra": "el país celebra"},
    ),
    dict(
        id="golpe",
        voz=("Los vigilantes habían dejado de hacer sus rondas. En unas horas vacían las vitrinas: más de cien "
             "piezas, entre ellas la máscara de jade del rey maya Pakal."),
        escenas=[(None, "garita"), ("En unas horas", "vitrinas"), ("entre ellas", "pakal")],
        pantalla=[(None, "SIN RONDAS"), ("En unas horas", "+100 PIEZAS"), ("entre ellas", "LA MÁSCARA DE PAKAL")],
        eventos={"rondas": "sus rondas"},
    ),
    dict(
        id="misterio",
        voz=("Lo llamaron el robo del siglo. Las piezas no aparecieron hasta 1989, y aún hoy nadie tiene claro "
             "para qué las querían."),
        escenas=[(None, "portada"), ("Las piezas", "calendario")],
        pantalla=[(None, "«EL ROBO DEL SIGLO»"), ("para qué", "¿PARA QUÉ?")],
        eventos={"aparecieron": "hasta 1989", "para": "para qué"},
    ),
    dict(
        id="cierre",
        voz=("El lugar más vigilado se vuelve frágil el día en que todos bajan la guardia. "
             "¿Tú habrías hecho la ronda en Nochebuena?"),
        escenas=[(None, "ronda")],
        pantalla=[("Tú habrías", "¿HARÍAS LA RONDA?")],
        eventos={"guardia": "bajan la guardia", "pregunta": "Tú habrías"},
    ),
]

RECORTES = ["Bloque 2: «estudiantes de Veterinaria» (≈1,2 s)"]

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")
NOCHE = hexc("#141a33")
JADE, JADE2 = hexc("#2f9e6f"), hexc("#1f7a55")


# ─────────────────────────────── piezas ───────────────────────────────
def mascara(ctx, cx, cy, s=1.0, brillo=0):
    """Máscara funeraria de mosaico de jade (estilizada)."""
    if brillo:
        for k in range(8):
            a = k * math.pi / 4 + (brillo % 2) * 0.2
            line(ctx, [(cx + 170 * s * math.cos(a), cy + 200 * s * math.sin(a)),
                       (cx + 220 * s * math.cos(a), cy + 260 * s * math.sin(a))], 6, hexc("#ffe58a"))
    piece(ctx, P_ell(cx, cy, 140 * s, 175 * s), JADE, lw=5, sh=(10, 12))
    for i in range(36):
        a = hnoise("tesela", i) * 2 * math.pi
        r = math.sqrt(hnoise("tesela", i, "r")) * 0.85
        x, y = cx + 140 * s * r * math.cos(a), cy + 175 * s * r * math.sin(a)
        w = 22 * s + hnoise("t", i) * 16 * s
        with rot(ctx, x, y, a):
            piece(ctx, P_rect(x - w / 2, y - w / 3, w, w * 0.66), JADE2 if i % 3 else hexc("#3cb47f"), lw=2,
                  shadow=False)
    for side in (-1, 1):
        ex = cx + side * 55 * s
        piece(ctx, P_ell(ex, cy - 25 * s, 36 * s, 18 * s), hexc("#f6f1e2"), lw=4, shadow=False)
        piece(ctx, P_ell(ex, cy - 25 * s, 13 * s), INK, shadow=False)
    piece(ctx, P_poly([(cx - 20 * s, cy - 10 * s), (cx + 20 * s, cy - 10 * s), (cx + 28 * s, cy + 50 * s),
                       (cx - 28 * s, cy + 50 * s)]), JADE2, lw=3, shadow=False)
    piece(ctx, P_ell(cx, cy + 95 * s, 40 * s, 14 * s), hexc("#c0392b"), lw=3, shadow=False)


def vitrina(ctx, x, y, w, h, contenido=None, vacia=False):
    piece(ctx, P_rect(x - 10, y + h, w + 20, 120), hexc("#3a2e4f"), lw=4)
    piece(ctx, P_rect(x, y, w, h), hexc("#bfe3f2", 0.18), lw=5, shadow=False)
    line(ctx, [(x + 20, y + h - 30), (x + w * 0.4, y + 20)], 6, (1, 1, 1, 0.25))
    if contenido and not vacia:
        contenido()


def vasija(ctx, cx, cy, s, col):
    piece(ctx, P_poly([(cx - 30 * s, cy - 50 * s), (cx + 30 * s, cy - 50 * s), (cx + 50 * s, cy), (cx + 30 * s, cy + 50 * s),
                       (cx - 30 * s, cy + 50 * s), (cx - 50 * s, cy)]), col, lw=3, shadow=False)
    line(ctx, [(cx - 45 * s, cy), (cx + 45 * s, cy)], 4, (0, 0, 0, 0.35))


def luces(ctx, y, pose, x0=0, x1=1080):
    pts = []
    for i in range(14):
        x = lerp(x0, x1, i / 13)
        pts.append((x, y + 30 * math.sin(i / 13 * math.pi * 2)))
    line(ctx, pts, 3, INK)
    cols = ["#e63946", "#ffe14d", "#2fb35a", "#1d4ed8"]
    for i, (x, yy) in enumerate(pts):
        on = (i + pose // 3) % 2 == 0
        piece(ctx, P_ell(x, yy + 14, 10, 14), hexc(cols[i % 4]) if on else hexc("#3a3f66"), lw=2, shadow=False)


def gateando(ctx, x, y, s, pose, k=0):
    """Persona a gatas (silueta sin rasgos, persona real): brazos delante, rodillas en el suelo."""
    st = 1 if (pose + k) % 4 < 2 else -1
    w = 16 * s
    # pierna trasera y brazo trasero (más oscuros, detrás)
    line(ctx, [(x - 60 * s, y), (x - 45 * s - 6 * s * st, y + 72 * s), (x - 140 * s, y + 80 * s)], w, hexc("#100d1c"))
    line(ctx, [(x + 45 * s, y - 6 * s), (x + 75 * s - 10 * s * st, y + 78 * s)], w * 0.9, hexc("#100d1c"))
    # tronco y cabeza
    piece(ctx, P_rrect(x - 85 * s, y - 32 * s, 160 * s, 64 * s, 30 * s), SOMBRA, lw=4, shadow=False)
    piece(ctx, P_ell(x + 108 * s, y - 34 * s, 36 * s), SOMBRA, lw=4, shadow=False)
    ctx.new_sub_path()
    ctx.arc(x + 108 * s, y - 34 * s, 28 * s, math.radians(200), math.radians(300))
    set_col(ctx, BORDE)
    ctx.set_line_width(5)
    ctx.stroke()
    # pierna y brazo delanteros
    line(ctx, [(x - 55 * s, y + 6 * s), (x - 40 * s + 6 * s * st, y + 76 * s), (x - 130 * s, y + 84 * s)], w, SOMBRA)
    line(ctx, [(x + 55 * s, y), (x + 85 * s + 10 * s * st, y + 82 * s)], w * 0.9, SOMBRA)


def guardia(ctx, x, y, r=95, pose=0, linterna=False, expr="neutro"):
    piece(ctx, P_rect(x - 55, y + r * 2.9, 46, 170), hexc("#23365e"), lw=4)
    piece(ctx, P_rect(x + 9, y + r * 2.9, 46, 170), hexc("#23365e"), lw=4)
    adulto(ctx, x, y, r, traje="#2c4479", pelo="#3a2a1e", expr=expr, look=1.0, pose=pose, skin=hexc("#c98b5e"))
    gorra(ctx, x, y, r, "#1b2747")
    if linterna:
        ctx.move_to(x + r * 1.4, y + r * 1.7)
        ctx.line_to(x + r * 6, y + r * 0.6)
        ctx.line_to(x + r * 6, y + r * 3.2)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.95, 0.6, 0.25)
        ctx.fill()
        piece(ctx, P_rrect(x + r * 1.1, y + r * 1.55, r * 0.6, r * 0.3, 8), hexc("#3d3f4a"), lw=3, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sala(ctx):
    set_col(ctx, hexc("#211a3a"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#16112a"), lw=4, shadow=False)
    for i in range(6):
        line(ctx, [(i * 200 + 40, 0), (i * 200 + 40, 1300)], 3, (1, 1, 1, 0.04))


def sc_vitrina(ctx, pose, lt, ev):
    sala(ctx)
    ctx.move_to(470, -10)
    ctx.line_to(610, -10)
    ctx.line_to(820, 1300)
    ctx.line_to(260, 1300)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.95, 0.7, 0.10)
    ctx.fill()
    tp = since(ev, "plena", lt)
    vacia = tp >= 0
    vitrina(ctx, 290, 640, 500, 560, lambda: mascara(ctx, 540, 920, 1.0, pose if lt > 0.3 else 0), vacia)
    if vacia:
        bob = (pose // 4) % 2 * 10
        draw_text(ctx, "?", 540, 930 - bob, 260, hexc("#ffe14d"), INK, 8)
        # bola de Navidad colgando
        line(ctx, [(780, 0), (780, 520)], 3, (1, 1, 1, 0.6))
        piece(ctx, P_ell(780, 560, 44), hexc("#e63946"), lw=4)
        piece(ctx, P_rect(764, 508, 32, 16), hexc("#f2c94c"), lw=2, shadow=False)


def sc_fachada(ctx, pose, lt, ev):
    set_col(ctx, NOCHE)
    ctx.paint()
    g.stars(ctx, 28, "cdmx", 700, pose)
    tc = since(ev, "celebra", lt)
    if tc >= 0:
        for i, (fx, fy, col) in enumerate(((220, 420, "#ff6b6b"), (860, 380, "#ffe14d"), (560, 300, "#6fd0f2"))):
            k = ((lt * 1.4 + i * 0.33) % 1.0)
            for j in range(10):
                a = j * math.pi / 5
                r = 20 + 90 * k
                line(ctx, [(fx + r * 0.6 * math.cos(a), fy + r * 0.6 * math.sin(a)),
                           (fx + r * math.cos(a), fy + r * math.sin(a))], 5, hexc(col, 1 - k * 0.7))
    piece(ctx, P_rect(-10, 1260, 1100, 700), hexc("#3d3f4a"), lw=4, shadow=False)
    # edificio moderno genérico
    piece(ctx, P_rect(90, 760, 900, 500), hexc("#cfc8b8"), lw=5)
    piece(ctx, P_rect(60, 700, 960, 80), hexc("#b8b0a0"), lw=5)
    for k in range(8):
        piece(ctx, P_rect(130 + k * 108, 900, 70, 260), hexc("#1d2433"), lw=3, shadow=False)
        piece(ctx, P_rect(130 + k * 108, 900, 70, 260), hexc("#ffd86b", 0.25 if (k + pose // 12) % 3 else 0.5), lw=0,
              shadow=False, outline=False)
    piece(ctx, P_rrect(200, 790, 680, 90, 10), hexc("#f6f1e2"), lw=4)
    draw_text(ctx, "MUSEO NACIONAL", 540, 822, 40, INK, INK, 0)
    draw_text(ctx, "DE ANTROPOLOGÍA", 540, 860, 30, hexc("#c0392b"), INK, 0)
    luces(ctx, 690, pose, 40, 1040)


def sc_conducto(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2a2440"))
    ctx.paint()
    # conducto en corte
    piece(ctx, P_rect(-10, 760, 1100, 460), hexc("#9aa0ab"), lw=6)
    piece(ctx, P_rect(-10, 790, 1100, 400), hexc("#5b6475"), lw=4, shadow=False)
    for i in range(9):
        line(ctx, [(i * 140 - 20, 760), (i * 140 - 20, 1220)], 4, hexc("#7d838f"))
    x = lerp(-250, 640, clamp(lt / 3.2))
    gateando(ctx, x, 1090, 1.2, pose, 0)
    gateando(ctx, x - 330, 1090, 1.2, pose, 2)
    # rejilla de salida
    piece(ctx, P_rect(900, 800, 150, 380), hexc("#3d3f4a"), lw=5)
    for k in range(9):
        line(ctx, [(910, 825 + k * 40), (1040, 825 + k * 40)], 5, hexc("#9aa0ab"))
    piece(ctx, P_rrect(380, 580, 320, 90, 12), hexc("#6fd0f2"), lw=5)
    draw_text(ctx, "A/C", 540, 625, 60, INK, INK, 0)


def sc_garita(ctx, pose, lt, ev):
    sala(ctx)
    # silla vacía y mesa con café y arbolito
    piece(ctx, P_rrect(320, 900, 220, 300, 18), hexc("#5d3a22"), lw=5)
    piece(ctx, P_rect(300, 1160, 260, 40), hexc("#7a4e2c"), lw=4)
    for dx in (310, 530):
        piece(ctx, P_rect(dx, 1200, 22, 110), hexc("#4a2e1a"), lw=3)
    piece(ctx, P_rect(600, 1060, 380, 30), hexc("#9b6a3f"), lw=4)
    piece(ctx, P_rect(620, 1090, 24, 220), hexc("#7a4e2c"), lw=3)
    piece(ctx, P_rect(936, 1090, 24, 220), hexc("#7a4e2c"), lw=3)
    piece(ctx, P_rrect(660, 990, 70, 70, 10), (1, 1, 1), lw=4)
    if (pose // 6) % 2 == 0:
        for k in range(2):
            line(ctx, [(680 + k * 25, 975), (690 + k * 25, 940), (680 + k * 25, 910)], 4, (1, 1, 1, 0.5))
    piece(ctx, P_poly([(860, 870), (930, 1060), (790, 1060)]), hexc("#2fb35a"), lw=4)
    for k, (bx, by) in enumerate(((850, 950), (880, 1000), (830, 1020))):
        piece(ctx, P_ell(bx, by, 10), hexc(["#e63946", "#ffe14d", "#1d4ed8"][k]), lw=2, shadow=False)
    piece(ctx, P_rrect(740, 1020, 90, 30, 8), hexc("#3d3f4a"), lw=3, shadow=False)
    tr = since(ev, "rondas", lt)
    if tr >= 0:
        stamp(ctx, 440, 780, "SIN RONDA", tr, 56, col=hexc("#e23b3b"), ang=-8)


def sc_vitrinas(ctx, pose, lt, ev):
    sala(ctx)
    cols = ["#c0392b", "#d9a441", "#2f9e6f", "#8a5a34", "#7c3aed", "#1d4ed8"]
    vacias = int(lt / 0.35)
    for i in range(6):
        r, c = divmod(i, 3)
        x, y = 70 + c * 330, 600 + r * 400
        v = i < vacias
        vitrina(ctx, x, y, 280, 260, lambda x=x, y=y, i=i: vasija(ctx, x + 140, y + 140, 1.3, hexc(cols[i])), v)
        if v:
            txt(ctx, "VACÍA", x + 140, y + 150, 34, hexc("#ff6b6b"), anchor="center")
    n = min(124, 20 * vacias)
    piece(ctx, P_rrect(360, 1430, 360, 70, 12), hexc("#1d2433"), lw=4) if False else None


def sc_pakal(ctx, pose, lt, ev):
    sala(ctx)
    k = ease_out_back(clamp(lt / 0.35)) if lt < 0.35 else 1.0
    ctx.save()
    ctx.translate(540, 960)
    ctx.scale(max(0.05, k), max(0.05, k))
    ctx.translate(-540, -960)
    mascara(ctx, 540, 960, 1.9, pose)
    ctx.restore()
    piece(ctx, P_rrect(300, 1300, 480, 90, 14), hexc("#f6f1e2"), lw=4)
    txt(ctx, "JADE · REY PAKAL", 540, 1358, 40, INK, anchor="center")


def sc_portada(ctx, pose, lt, ev):
    set_col(ctx, hexc("#d9cfbd"))
    ctx.paint()
    k = max(0.05, ease_out_back(clamp(lt / 0.35))) if lt < 0.35 else 1.0
    with rot(ctx, 540, 960, math.radians(-4 + 30 * (1 - k))):
        ctx.save()
        ctx.translate(540, 960)
        ctx.scale(k, k)
        ctx.translate(-540, -960)
        piece(ctx, P_rect(140, 560, 800, 820), hexc("#f6f1e2"), lw=6, sh=(10, 14))
        draw_text(ctx, "EL DIARIO · 26 DIC 1985", 540, 620, 40, INK, INK, 0)
        line(ctx, [(170, 660), (910, 660)], 5)
        draw_text(ctx, "¡EL ROBO", 540, 740, 92, hexc("#c0392b"), INK, 0)
        draw_text(ctx, "DEL SIGLO!", 540, 840, 92, hexc("#c0392b"), INK, 0)
        piece(ctx, P_rect(180, 900, 330, 380), hexc("#211a3a"), lw=4, shadow=False)
        mascara(ctx, 345, 1090, 0.75)
        for j in range(8):
            line(ctx, [(540, 920 + j * 42), (900 - 40 * (j % 3), 920 + j * 42)], 6, (0, 0, 0, 0.3))
        ctx.restore()


def sc_calendario(ctx, pose, lt, ev):
    sala(ctx)
    ta, tp = since(ev, "aparecieron", lt), since(ev, "para", lt)
    span = max(0.6, ev.get("aparecieron_lt", 2.0) or 2.0)
    year = 1985 + int(round(4 * clamp(lt / span)))
    cx, cy = 300, 820
    piece(ctx, P_rect(cx - 170, cy - 180, 340, 380), (1, 1, 1), lw=5)
    piece(ctx, P_rect(cx - 170, cy - 180, 340, 90), hexc("#c0392b"), lw=5, shadow=False)
    draw_text(ctx, "AÑO", cx, cy - 135, 46, (1, 1, 1), INK, 0)
    draw_text(ctx, str(year), cx, cy + 40, 120, INK, INK, 0)
    if ta >= 0:
        vitrina(ctx, 600, 640, 380, 500, lambda: mascara(ctx, 790, 880, 0.95))
        piece(ctx, P_ell(940, 680, 46), hexc("#2fb35a"), lw=4)
        line(ctx, [(918, 680), (936, 700), (964, 662)], 10, (1, 1, 1))
    if tp >= 0:
        bob = (pose // 4) % 2 * 10
        draw_text(ctx, "?", 300, 1250 - bob, 200, hexc("#ffe14d"), INK, 8)


def sc_ronda(ctx, pose, lt, ev):
    sala(ctx)
    for i in range(3):
        vitrina(ctx, 470 + i * 200, 820, 170, 230, lambda i=i: vasija(ctx, 555 + i * 200, 935, 0.9,
                                                                          hexc(["#c0392b", "#d9a441", "#2f9e6f"][i])))
    tg = since(ev, "guardia", lt)
    guardia(ctx, 230, 860, 90, pose, linterna=tg < 0, expr="neutro" if tg < 0 else "preocupado")
    luces(ctx, 520, pose, 60, 1020)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bubble(ctx, 560, 640, 520, 150, (300, 780), ["¿Y TÚ?"], 70, col=hexc("#ffe14d"))


SCENES = dict(vitrina=sc_vitrina, fachada=sc_fachada, conducto=sc_conducto, garita=sc_garita,
              vitrinas=sc_vitrinas, pakal=sc_pakal, portada=sc_portada, calendario=sc_calendario, ronda=sc_ronda)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_pakal(ctx, 1, 1.0, {})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(37))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ROBARON EL TESORO", 540, 220, 110, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "DE MÉXICO", 540, 380, 130, hexc("#2f9e6f"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "EN NOCHEBUENA", 540, 1640, 120, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
