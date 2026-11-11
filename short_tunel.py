#!/usr/bin/env python3
"""
Short 9 · «Robaron 3 toneladas de billetes… por un túnel» — crimen real + dato impactante
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_tunel.py            # vídeo final (usa cache_audio/tunel-fortaleza/)
    python short_tunel.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier

SLUG = "tunel-fortaleza"

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que unos ladrones sacaron más de tres toneladas de billetes "
             "de un banco… por un túnel?"),
        escenas=[(None, "bascula")],
        pantalla=[("tres toneladas", "¡3 TONELADAS!")],
        eventos={"ton": "tres toneladas", "tunel": "por un túnel"},
    ),
    dict(
        id="caso",
        voz=("Fortaleza, Brasil, 2005. Una banda alquila una casa frente al Banco Central. "
             "Por fuera, es una empresa de césped artificial. Por dentro, una obra secreta."),
        escenas=[(None, "calle"), ("Por dentro", "corte")],
        pantalla=[(None, "FORTALEZA, 2005"), ("Por fuera", "«CÉSPED ARTIFICIAL»"), ("Por dentro", "UNA OBRA SECRETA")],
        eventos={"alquila": "alquila una", "fuera": "Por fuera"},
    ),
    dict(
        id="tunel",
        voz=("Durante meses cavan un túnel de casi 80 metros hasta llegar justo debajo de la cámara acorazada. "
             "Un fin de semana de agosto, la atraviesan."),
        escenas=[(None, "tunel")],
        pantalla=[("casi 80", "CASI 80 METROS"), ("la atraviesan", "¡DENTRO!")],
        eventos={"debajo": "justo debajo", "atraviesan": "la atraviesan"},
    ),
    dict(
        id="botin",
        voz=("Se llevan unos 160 millones de reales en billetes usados, difíciles de rastrear. "
             "Decenas de personas acabaron detenidas, pero la mayor parte del dinero nunca apareció."),
        escenas=[(None, "sacos"), ("Decenas de", "detenidos"), ("pero la mayor", "vacio")],
        pantalla=[(None, "160 MILLONES DE REALES"), ("pero la mayor", "¿Y EL DINERO?")],
        eventos={"rastrear": "difíciles de", "detenidas": "acabaron detenidas"},
    ),
    dict(
        id="cierre",
        voz="Nadie sospecha de un negocio aburrido. ¿Te habrías fijado en la tienda de césped?",
        escenas=[(None, "tienda")],
        pantalla=[("Te habrías", "¿TE HABRÍAS FIJADO?")],
        eventos={"pregunta": "Te habrías"},
    ),
]

RECORTES = ["Bloque 4: «difíciles de rastrear» (≈1 s)"]

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")
TIERRA, TIERRA2 = hexc("#8a5a34"), hexc("#6b4428")
SUELO_Y = 900


# ─────────────────────────────── piezas ───────────────────────────────
def billetes(ctx, x, y, w, h, n, seed=0):
    for i in range(n):
        bx = x + hnoise(seed, i, "x") * (w - 120)
        by = y + h - 30 - (i // 4) * 22 - hnoise(seed, i, "y") * 10
        with rot(ctx, bx + 60, by, math.radians((hnoise(seed, i, "a") - 0.5) * 20)):
            piece(ctx, P_rect(bx, by - 18, 130, 40), hexc("#9fd6a0"), lw=3, shadow=False)
            piece(ctx, P_ell(bx + 65, by + 2, 12), hexc("#5fa35a"), lw=2, shadow=False)


def saco(ctx, x, y, s=1.0, label="R$"):
    piece(ctx, P_poly([(x - 70 * s, y + 80 * s), (x + 70 * s, y + 80 * s), (x + 85 * s, y - 20 * s), (x + 40 * s, y - 70 * s),
                       (x - 40 * s, y - 70 * s), (x - 85 * s, y - 20 * s)]), hexc("#c9a46a"), lw=4)
    line(ctx, [(x - 40 * s, y - 62 * s), (x + 40 * s, y - 62 * s)], 7, hexc("#6b4428"))
    draw_text(ctx, label, x, y + 15 * s, 48 * s, hexc("#2f6b45"), INK, 0)


def excavador(ctx, x, feet, s, pose, k=0):
    silhouette(ctx, x, feet, s, math.radians(6) * (1 if (pose + k) % 4 < 2 else -1), SOMBRA, BORDE)
    a = math.radians(-35 if (pose + k) % 4 < 2 else 10)
    with rot(ctx, x + 50 * s, feet - 170 * s, a):
        line(ctx, [(x + 50 * s, feet - 170 * s), (x + 150 * s, feet - 60 * s)], 9, hexc("#8a5a34"))
        piece(ctx, P_poly([(x + 140 * s, feet - 70 * s), (x + 185 * s, feet - 40 * s), (x + 160 * s, feet - 10 * s),
                           (x + 125 * s, feet - 45 * s)]), hexc("#9aa0ab"), lw=3, shadow=False)


def tienda(ctx, x, y, w, h, abierta=True):
    piece(ctx, P_rect(x, y, w, h), hexc("#f3e6c9"), lw=5)
    piece(ctx, P_rect(x - 10, y - 90, w + 20, 100), hexc("#2f9e4f"), lw=5)
    draw_text(ctx, "CÉSPED", x + w / 2, y - 58, 52, (1, 1, 1), INK, 0)
    draw_text(ctx, "ARTIFICIAL", x + w / 2, y - 14, 30, (1, 1, 1), INK, 0)
    for k in range(5):
        piece(ctx, P_poly([(x + k * w / 5, y + 10), (x + (k + 1) * w / 5, y + 10), (x + (k + 0.5) * w / 5, y + 60)]),
              hexc("#2f9e4f") if k % 2 == 0 else (1, 1, 1), lw=2, shadow=False)
    piece(ctx, P_rect(x + 30, y + 90, w * 0.45, h * 0.45), hexc("#bfe3f2"), lw=4)
    for k in range(3):
        piece(ctx, P_ell(x + 70 + k * 40, y + 90 + h * 0.4, 22, 22), hexc("#5fbf5a"), lw=3, shadow=False)
    piece(ctx, P_rect(x + w - 120, y + h - 200, 90, 200), hexc("#7a4e2c"), lw=4)
    if abierta:
        piece(ctx, P_rrect(x + w - 140, y + 90, 130, 50, 8), (1, 1, 1), lw=3, shadow=False)
        txt(ctx, "ABIERTO", x + w - 75, y + 125, 26, hexc("#2f9e4f"), anchor="center")


def banco(ctx, x, y, w, h):
    piece(ctx, P_rect(x, y, w, h), hexc("#e3e6ec"), lw=5)
    piece(ctx, P_poly([(x - 20, y), (x + w + 20, y), (x + w / 2, y - 110)]), hexc("#cfd5df"), lw=5)
    for k in range(4):
        piece(ctx, P_rect(x + 30 + k * (w - 80) / 3, y + 60, 30, h - 80), (1, 1, 1), lw=3, shadow=False)
    piece(ctx, P_rrect(x + 20, y + 10, w - 40, 44, 8), hexc("#1d4ed8"), lw=3, shadow=False)
    txt(ctx, "BANCO CENTRAL", x + w / 2, y + 42, 26, (1, 1, 1), anchor="center")


def corte_base(ctx, pose):
    """Vista en corte: cielo, calle y subsuelo."""
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_rect(-10, SUELO_Y, 1100, 1100), TIERRA, lw=4, shadow=False)
    for i in range(40):
        x = hnoise("pied", i) * 1080
        y = SUELO_Y + 40 + hnoise("pied", i, "y") * 520
        piece(ctx, P_ell(x, y, 10 + hnoise("pied", i, "r") * 14, 8 + hnoise("pied", i, "r") * 10), TIERRA2, lw=2,
              shadow=False)
    piece(ctx, P_rect(-10, SUELO_Y - 16, 1100, 24), hexc("#6b6f78"), lw=4, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_bascula(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#1d2440"), lw=4, shadow=False)
    tt = since(ev, "ton", lt)
    kg = int(3000 * ease_io(clamp(tt / 1.0))) if tt >= 0 else 0
    # báscula
    piece(ctx, P_rect(200, 1180, 680, 60), hexc("#9aa0ab"), lw=5)
    piece(ctx, P_rect(500, 1240, 80, 70), hexc("#6b6f78"), lw=4)
    piece(ctx, P_rrect(380, 1230, 320, 90, 12), hexc("#1d2433"), lw=4)
    txt(ctx, f"{kg:,} kg".replace(",", "."), 540, 1293, 56, hexc("#ff5a5a"), anchor="center")
    n = int(60 * clamp(tt / 1.0)) if tt >= 0 else 6
    billetes(ctx, 230, 700, 620, 480, n, 1)
    tu = since(ev, "tunel", lt)
    if tu >= 0:
        k = ease_out_back(clamp(tu / 0.3)) if tu < 0.3 else 1.0
        piece(ctx, P_ell(880, 1350, 150 * k, 40 * k), INK, lw=4, shadow=False)
        piece(ctx, P_poly([(880, 1320), (930, 1230), (905, 1230), (905, 1110), (855, 1110), (855, 1230), (830, 1230)]),
              hexc("#ffe14d"), lw=4)


def sc_calle(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_ell(900, 380, 70), hexc("#ffe58a"), lw=4)
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#6b6f78"), lw=4, shadow=False)
    for i in range(6):
        piece(ctx, P_rect(i * 200 - 40, 1520, 120, 16), hexc("#f2e7b0"), lw=2, shadow=False)
    banco(ctx, 600, 770, 420, 480)
    tf = since(ev, "fuera", lt)
    tienda(ctx, 60, 860, 460, 390)
    if tf >= 0:
        stamp(ctx, 290, 700, "¿INOCENTE?", tf, 44, col=hexc("#e23b3b"), ang=-6)
    ta = since(ev, "alquila", lt)
    if ta >= 0 and tf < 0:
        piece(ctx, P_rrect(150, 690, 280, 90, 12), hexc("#e63946"), lw=5)
        draw_text(ctx, "SE ALQUILA", 290, 735, 44, (1, 1, 1), INK, 0)


def sc_corte(ctx, pose, lt, ev):
    corte_base(ctx, pose)
    tienda(ctx, 60, SUELO_Y - 390, 460, 390)
    banco(ctx, 600, SUELO_Y - 480, 420, 480)
    # sótano de la tienda con excavadores
    piece(ctx, P_rect(80, SUELO_Y + 10, 420, 330), hexc("#4a2f1c"), lw=4, shadow=False)
    line(ctx, [(120, SUELO_Y + 10), (120, SUELO_Y + 340)], 5, hexc("#ffe58a", 0.6))
    for k, x in enumerate((180, 330)):
        excavador(ctx, x, SUELO_Y + 330, 0.75, pose, k * 2)
    piece(ctx, P_ell(140, SUELO_Y + 60, 18), hexc("#fff3b0"), lw=3, shadow=False)


def sc_tunel(ctx, pose, lt, ev):
    corte_base(ctx, pose)
    tienda(ctx, 40, SUELO_Y - 390, 380, 390, abierta=False)
    banco(ctx, 640, SUELO_Y - 480, 400, 480)
    # cámara acorazada bajo el banco
    vx, vy = 680, SUELO_Y + 60
    piece(ctx, P_rect(vx, vy, 320, 240), hexc("#5b6475"), lw=6)
    for k in range(3):
        saco(ctx, vx + 70 + k * 90, vy + 150, 0.6)
    ta = since(ev, "atraviesan", lt)
    td = since(ev, "debajo", lt)
    dur = max(1.0, (ev.get("atraviesan_lt", ev.get("dur", 6)) or 6))
    p = clamp(lt / max(0.8, ev.get("debajo_lt", dur) or dur))
    # túnel que avanza desde el sótano de la tienda hasta debajo de la cámara
    x0, x1 = 160, 840
    yt = SUELO_Y + 420
    xe = lerp(x0, x1, ease_io(p))
    piece(ctx, P_rect(x0 - 40, SUELO_Y + 10, 120, yt - SUELO_Y + 50), hexc("#2a1a10"), lw=3, shadow=False)
    piece(ctx, P_rect(x0, yt, xe - x0, 90), hexc("#2a1a10"), lw=3, shadow=False)
    for xx in range(int(x0) + 60, int(xe), 110):
        line(ctx, [(xx, yt), (xx, yt + 90)], 6, hexc("#8a5a34"))
        piece(ctx, P_ell(xx, yt + 12, 8), hexc("#fff3b0"), lw=0, shadow=False, outline=False)
    excavador(ctx, xe - 40, yt + 90, 0.32, pose)
    # medidor de metros
    piece(ctx, P_rrect(300, 1100, 300, 80, 12), hexc("#1d2433"), lw=4)
    txt(ctx, f"{int(78 * ease_io(p))} m", 450, 1155, 50, hexc("#ffe14d"), anchor="center")
    if td >= 0:
        piece(ctx, P_rect(x1 - 40, vy + 240, 80, yt - vy - 240), hexc("#2a1a10"), lw=3, shadow=False)
    if ta >= 0:
        k = clamp(ta / 0.3)
        for i in range(6):
            a = math.pi + i * math.pi / 5
            line(ctx, [(840 + 40 * math.cos(a), vy + 240 + 20 * math.sin(a)),
                       (840 + (90 + 40 * k) * math.cos(a), vy + 240 + (60 + 30 * k) * math.sin(a))], 7, hexc("#ffe14d"))
        draw_text(ctx, "¡CRAC!", 840, vy - 40, 64, hexc("#ffe14d"), INK, 6) if (pose // 3) % 2 == 0 else None


def sc_sacos(ctx, pose, lt, ev):
    corte_base(ctx, pose)
    yt = SUELO_Y + 300
    piece(ctx, P_rect(-10, yt, 1100, 220), hexc("#2a1a10"), lw=3, shadow=False)
    for xx in range(40, 1080, 140):
        line(ctx, [(xx, yt), (xx, yt + 220)], 7, hexc("#8a5a34"))
        piece(ctx, P_ell(xx, yt + 16, 9), hexc("#fff3b0"), lw=0, shadow=False, outline=False)
    for i in range(4):
        x = 1200 - ((lt * 260 + i * 300) % 1500)
        saco(ctx, x, yt + 130, 0.9)
    tr = since(ev, "rastrear", lt)
    if tr >= 0:
        stamp(ctx, 540, 720, "BILLETES USADOS", tr, 50, col=hexc("#2f6b45"), ang=-5)


def sc_detenidos(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#1d2440"), lw=4, shadow=False)
    td = since(ev, "detenidas", lt)
    for i in range(10):
        r, c = divmod(i, 5)
        x, feet = 140 + c * 200, 960 + r * 330
        silhouette(ctx, x, feet, 0.62, 0.0, SOMBRA, BORDE)
        if td >= 0:
            stamp(ctx, x, feet - 120, "DETENIDO", td - i * 0.08, 34, col=hexc("#e23b3b"), ang=-8 + (i % 3) * 6)


def sc_vacio(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#1d2440"), lw=4, shadow=False)
    # saco abierto y vacío
    piece(ctx, P_poly([(380, 1300), (700, 1300), (760, 1060), (640, 960), (440, 960), (320, 1060)]), hexc("#c9a46a"), lw=6)
    piece(ctx, P_ell(540, 970, 110, 30), hexc("#3a2418"), lw=4, shadow=False)
    bob = (pose // 4) % 2 * 12
    draw_text(ctx, "?", 540, 740 - bob, 300, hexc("#ffe14d"), INK, 9)
    piece(ctx, P_rrect(320, 1180, 440, 80, 12), hexc("#1d2433"), lw=4)
    txt(ctx, "RECUPERADO: POCO", 540, 1232, 36, hexc("#ff6b6b"), anchor="center")


def sc_tienda(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#6b6f78"), lw=4, shadow=False)
    tienda(ctx, 210, 820, 660, 480)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        k = ease_io(clamp(tq / 0.6))
        magnifier(ctx, lerp(950, 620, k), 1050, 120, math.radians(-30))


SCENES = dict(bascula=sc_bascula, calle=sc_calle, corte=sc_corte, tunel=sc_tunel, sacos=sc_sacos,
              detenidos=sc_detenidos, vacio=sc_vacio, tienda=sc_tienda)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_tunel(ctx, 0, 6.0, {"debajo_lt": 3.0, "atraviesan_lt": 5.0, "dur": 7})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(31))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "3 TONELADAS", 540, 220, 120, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "DE BILLETES…", 540, 380, 120, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡POR UN TÚNEL!", 540, 1680, 120, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
