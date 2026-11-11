#!/usr/bin/env python3
"""
Short 12 · «Buscaron 16 años a una asesina… que nunca existió» — el fantasma de Heilbronn
Guion escrito con la skill (references/guiones.md). Voz gratuita (Chatterbox) por falta de créditos.

Uso:
    python short_fantasma.py            # vídeo final (usa cache_audio/fantasma-heilbronn/)
    python short_fantasma.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier
from short_obediencia import adulto

SLUG = "fantasma-heilbronn"

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pensarías si te dijera que la policía buscó durante 16 años a una asesina… que nunca existió?",
        escenas=[(None, "sebusca")],
        pantalla=[("16 años", "16 AÑOS BUSCÁNDOLA"), ("que nunca", "¿NUNCA EXISTIÓ?")],
        eventos={"anios": "16 años", "existio": "que nunca"},
    ),
    dict(
        id="caso",
        voz=("Alemania, Austria y Francia. Desde 1993, el mismo ADN de mujer aparece en unas 40 escenas de "
             "crímenes: robos, asaltos… y hasta seis asesinatos."),
        escenas=[(None, "mapa")],
        pantalla=[(None, "1993"), ("el mismo", "MISMO ADN"), ("unas 40", "40 ESCENAS"), ("hasta seis", "6 ASESINATOS")],
        eventos={"adn": "el mismo", "escenas": "unas 40", "robos": "robos", "asesinatos": "hasta seis"},
    ),
    dict(
        id="misterio",
        voz=("La prensa la llama \"el fantasma de Heilbronn\". Nadie la ve, nadie la graba. "
             "Solo deja su ADN, una y otra vez."),
        escenas=[(None, "tablon"), ("Nadie la ve", "camara"), ("Solo deja", "tablon")],
        pantalla=[(None, "«EL FANTASMA»"), ("Nadie la ve", "NADIE LA VE"), ("Solo deja", "SOLO SU ADN")],
        eventos={"fantasma": "el fantasma", "graba": "nadie la graba", "deja": "Solo deja"},
    ),
    dict(
        id="giro",
        voz=("En 2009, su ADN aparece en una prueba que no tenía nada que ver. Entonces lo entienden: estaba en "
             "los bastoncillos con los que la policía recogía las muestras. Era de una trabajadora de la fábrica "
             "que los hacía."),
        escenas=[(None, "prueba"), ("estaba en", "bastoncillo"), ("Era de", "fabrica")],
        pantalla=[(None, "2009"), ("estaba en", "¡EN LOS BASTONCILLOS!"), ("Era de", "DE LA FÁBRICA")],
        eventos={"nada": "nada que ver", "entienden": "Entonces lo", "muestras": "las muestras"},
    ),
    dict(
        id="cierre",
        voz="16 años persiguiendo a alguien que solo estaba en el algodón. ¿Tú te habrías fiado del ADN?",
        escenas=[(None, "algodon")],
        pantalla=[(None, "16 AÑOS…"), ("Tú te", "¿TE HABRÍAS FIADO?")],
        eventos={"algodon": "el algodón", "pregunta": "Tú te"},
    ),
]

PRONUNCIA = {"Heilbronn": "Jáilbron"}

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")
PAPEL = hexc("#f3e6c9")
CORCHO = hexc("#c79a5b")
ROJO = hexc("#e23b3b")


# ─────────────────────────────── piezas ───────────────────────────────
def fondo(ctx, col="#2d3557", suelo=1320, col_suelo="#1d2440"):
    set_col(ctx, hexc(col))
    ctx.paint()
    piece(ctx, P_rect(-10, suelo, 1100, 1960 - suelo), hexc(col_suelo), lw=4, shadow=False)


def mujer_silueta(ctx, x, feet, s):
    """Silueta femenina sin rasgos (busto con hombros y melena), para el cartel de «se busca»."""
    hr = 80 * s
    hy = feet - 250 * s
    # melena por detrás
    piece(ctx, P_rrect(x - hr * 1.15, hy - hr * 0.9, hr * 2.3, hr * 2.4, hr * 0.9), SOMBRA, lw=4, shadow=False)
    # hombros
    piece(ctx, P_poly([(x - 190 * s, feet), (x + 190 * s, feet), (x + 160 * s, feet - 110 * s), (x + 60 * s, feet - 150 * s),
                       (x - 60 * s, feet - 150 * s), (x - 160 * s, feet - 110 * s)]), SOMBRA, lw=4, shadow=False)
    piece(ctx, P_rect(x - 30 * s, hy + hr * 0.6, 60 * s, 90 * s), SOMBRA, lw=0, shadow=False, outline=False)
    piece(ctx, P_ell(x, hy, hr * 0.92, hr), SOMBRA, lw=4, shadow=False)
    ctx.new_sub_path()
    ctx.arc(x, hy, hr * 0.8, math.radians(205), math.radians(300))
    set_col(ctx, BORDE)
    ctx.set_line_width(6)
    ctx.stroke()


def helice(ctx, cx, y0, y1, amp, fase, cols=("#ff5a8a", "#4fb3ff")):
    n = 16
    pts_a, pts_b = [], []
    for i in range(n + 1):
        y = lerp(y0, y1, i / n)
        a = fase + i * 0.7
        pts_a.append((cx + amp * math.sin(a), y))
        pts_b.append((cx - amp * math.sin(a), y))
        if i % 1 == 0:
            line(ctx, [pts_a[-1], pts_b[-1]], 5, hexc("#f3f3f3"))
    line(ctx, pts_a, 12, hexc(cols[0]))
    line(ctx, pts_b, 12, hexc(cols[1]))


def bastoncillo(ctx, x, y, s, ang=0.0):
    with rot(ctx, x, y, ang):
        piece(ctx, P_rrect(x - 330 * s, y - 14 * s, 560 * s, 28 * s, 12 * s), hexc("#f4f4f0"), lw=4)
        piece(ctx, P_ell(x + 270 * s, y, 95 * s, 60 * s), (1, 1, 1), lw=5)
        for k in range(5):
            piece(ctx, P_ell(x + 230 * s + hnoise("alg", k) * 80 * s, y - 30 * s + hnoise("alg", k, "y") * 60 * s,
                             16 * s), hexc("#ececec"), lw=0, shadow=False, outline=False)


def caja_bastoncillos(ctx, x, y, w=170, h=120):
    piece(ctx, P_rect(x, y, w, h), hexc("#8ec5e8"), lw=4)
    piece(ctx, P_rect(x, y, w, 30), hexc("#1d4ed8"), lw=3, shadow=False)
    txt(ctx, "ESTÉRIL", x + w / 2, y + 23, 20, (1, 1, 1), anchor="center")
    for k in range(3):
        line(ctx, [(x + 30, y + 55 + k * 20), (x + w - 50, y + 55 + k * 20)], 6, (1, 1, 1))
        piece(ctx, P_ell(x + w - 42, y + 55 + k * 20, 12, 9), (1, 1, 1), lw=2, shadow=False)


def mesa(ctx, y, x0=-10, x1=1090, col="#7a4e2c"):
    piece(ctx, P_rect(x0, y, x1 - x0, 60), hexc(col), lw=5)
    piece(ctx, P_rect(x0, y + 60, x1 - x0, 1960 - y), hexc("#5a3820"), lw=4, shadow=False)


def chincheta(ctx, x, y, col, k=1.0):
    r = 16 * k
    if r <= 1:
        return
    piece(ctx, P_ell(x, y - r * 1.6, r), col, lw=3, shadow=False)
    line(ctx, [(x, y - r * 0.7), (x, y)], 4, INK)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_sebusca(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", 1360, "#262a3a")
    with rot(ctx, 540, 900, math.radians(-2)):
        piece(ctx, P_rect(230, 520, 620, 800), PAPEL, lw=6, sh=(12, 16))
        draw_text(ctx, "SE BUSCA", 540, 610, 92, ROJO, INK, 0)
        piece(ctx, P_rect(300, 690, 480, 470), hexc("#d9c7a3"), lw=4, shadow=False)
        mujer_silueta(ctx, 540, 1158, 1.0)
        te = since(ev, "existio", lt)
        if te >= 0:
            k = ease_io(clamp(te / 0.9))
            # la goma borra la silueta de arriba abajo
            piece(ctx, P_rect(302, 692, 476, 466 * k), hexc("#d9c7a3"), lw=0, shadow=False, outline=False)
            ex, ey = 540 + 150 * math.sin(pose * 1.3), 692 + 466 * k
            with rot(ctx, ex, ey, math.radians(-30)):
                piece(ctx, P_rrect(ex - 70, ey - 40, 140, 80, 14), hexc("#ff8fa3"), lw=4)
                piece(ctx, P_rect(ex - 70, ey - 40, 50, 80), hexc("#4f7cff"), lw=3, shadow=False)
            if k >= 1:
                bob = (pose // 4) % 2 * 10
                draw_text(ctx, "?", 540, 930 - bob, 260, hexc("#ffe14d"), INK, 9)
        txt(ctx, "RECOMPENSA", 540, 1240, 44, INK, anchor="center")
    ta = since(ev, "anios", lt)
    if ta >= 0:
        stamp(ctx, 820, 1290, "16 AÑOS", ta, 52, col=ROJO, ang=-10)


MAPA = {
    "FRANCIA": [(80, 760), (330, 690), (420, 820), (400, 1060), (300, 1230), (120, 1200), (60, 1000)],
    "ALEMANIA": [(420, 600), (700, 560), (760, 720), (720, 900), (560, 960), (420, 880), (400, 720)],
    "AUSTRIA": [(560, 980), (760, 930), (980, 960), (960, 1060), (700, 1090), (560, 1060)],
}


def pin_pos(i):
    zonas = [("ALEMANIA", 0.5), ("AUSTRIA", 0.3), ("FRANCIA", 0.2)]
    z = zonas[0][0] if hnoise("z", i) < 0.5 else (zonas[1][0] if hnoise("z", i) < 0.8 else zonas[2][0])
    pts = MAPA[z]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    return cx + (hnoise("px", i) - 0.5) * (max(xs) - min(xs)) * 0.6, cy + (hnoise("py", i) - 0.5) * (max(ys) - min(ys)) * 0.6


def sc_mapa(ctx, pose, lt, ev):
    set_col(ctx, hexc("#7fb7d9"))
    ctx.paint()
    cols = {"FRANCIA": "#8fd18a", "ALEMANIA": "#f2d36b", "AUSTRIA": "#f2a46b"}
    for nombre, pts in MAPA.items():
        piece(ctx, P_poly(pts), hexc(cols[nombre]), lw=5)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        txt(ctx, nombre, sum(xs) / len(xs), sum(ys) / len(ys) + 14, 34, INK, anchor="center")
    te = since(ev, "escenas", lt)
    ta = since(ev, "asesinatos", lt)
    n = 3 if te < 0 else 3 + int(37 * clamp(te / 2.0))
    for i in range(n):
        x, y = pin_pos(i)
        rojo = ta >= 0 and i < 6
        chincheta(ctx, x, y, ROJO if rojo else hexc("#1d4ed8"), 1.4 if rojo else 1.0)
    # contador
    piece(ctx, P_rrect(300, 1250, 480, 110, 16), hexc("#1d2433"), lw=4)
    txt(ctx, f"ESCENAS: {n}", 540, 1325, 56, hexc("#ffe14d"), anchor="center")
    tadn = since(ev, "adn", lt)
    if tadn >= 0:
        k = ease_out_back(clamp(tadn / 0.3)) if tadn < 0.3 else 1.0
        piece(ctx, P_rrect(880, 560, 170, 520 * k, 20), (1, 1, 1, 0.9), lw=4)
        if k > 0.8:
            helice(ctx, 965, 600, 1040, 50, pose * 0.5)


def tablon(ctx, pose, lt, ev, hilos=1.0):
    fondo(ctx, "#3a3150", 1320, "#241e33")
    piece(ctx, P_rect(80, 520, 920, 640), CORCHO, lw=6)
    for i in range(30):
        piece(ctx, P_ell(100 + hnoise("c", i) * 880, 540 + hnoise("c", i, "y") * 600, 4), hexc("#a77c44"),
              lw=0, shadow=False, outline=False)
    centro = (540, 830)
    fotos = [(200, 610), (400, 580), (720, 590), (880, 640), (180, 900), (330, 1020), (760, 1010), (900, 920)]
    m = int(len(fotos) * clamp(hilos))
    for (x, y) in fotos[:m]:
        line(ctx, [(x, y + 40), centro], 5, ROJO)
    for (x, y) in fotos:
        with rot(ctx, x, y, math.radians((hnoise("f", x) - 0.5) * 14)):
            piece(ctx, P_rect(x - 60, y - 10, 120, 100), (1, 1, 1), lw=4)
            draw_text(ctx, "?", x, y + 40, 60, hexc("#9aa0ab"), INK, 0)
            chincheta(ctx, x, y + 2, ROJO, 0.7)
    piece(ctx, P_rrect(centro[0] - 120, centro[1] - 70, 240, 140, 14), hexc("#ffe14d"), lw=5)
    helice(ctx, centro[0] - 60, centro[1] - 50, centro[1] + 50, 22, pose * 0.4)
    txt(ctx, "ADN", centro[0] + 45, centro[1] + 18, 48, INK, anchor="center")


def sc_tablon(ctx, pose, lt, ev):
    td = since(ev, "deja", lt)
    tablon(ctx, pose, lt, ev, hilos=clamp(lt / 1.5) if td < 0 else 1.0)
    # investigadores detrás de la mesa, mirando el tablón
    adulto(ctx, 240, 1140, 90, traje="#5b6475", expr="preocupado", look=1.0, pose=pose)
    adulto(ctx, 840, 1150, 85, traje="#6b3a3a", pelo="#7a5a2e", expr="neutro", look=-1.0, pose=pose + 2, gafas=True)
    mesa(ctx, 1330)
    tf = since(ev, "fantasma", lt)
    if tf >= 0 and td < 0:
        stamp(ctx, 540, 1060, "«FANTASMA»", tf, 52, col=hexc("#7b4dff"), ang=-6)
    if td >= 0:
        for i in range(3):
            stamp(ctx, 220 + i * 320, 1240, "ADN", td - i * 0.25, 46, col=ROJO, ang=-8 + i * 7)


def monitor(ctx, x, y, w, h, pose, sin_senal=True):
    piece(ctx, P_rrect(x, y, w, h, 18), hexc("#23242c"), lw=6)
    sx, sy, sw, sh = x + 20, y + 20, w - 40, h - 40
    piece(ctx, P_rect(sx, sy, sw, sh), hexc("#3a3f4a"), lw=3, shadow=False)
    if sin_senal:
        for i in range(70):
            px = sx + hnoise("n", i, pose % 3) * (sw - 20)
            py = sy + hnoise("m", i, pose % 3) * (sh - 12)
            piece(ctx, P_rect(px, py, 18, 8), (0.8, 0.8, 0.8) if i % 2 else (0.45, 0.45, 0.5), lw=0,
                  shadow=False, outline=False)
        piece(ctx, P_rrect(sx + sw / 2 - 170, sy + sh / 2 - 40, 340, 80, 10), INK, lw=0, shadow=False)
        txt(ctx, "SIN IMAGEN", sx + sw / 2, sy + sh / 2 + 16, 44, (1, 1, 1), anchor="center")


def sc_camara(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557")
    # cámara de vigilancia en la pared
    with rot(ctx, 880, 560, math.radians(12 + (6 if pose % 8 < 4 else -6))):
        piece(ctx, P_rrect(760, 520, 200, 80, 14), hexc("#e3e6ec"), lw=4)
        piece(ctx, P_ell(760, 560, 30), INK, lw=3, shadow=False)
        piece(ctx, P_ell(930, 540, 8), ROJO if pose % 6 < 3 else hexc("#6b1d24"), lw=0, shadow=False, outline=False)
    line(ctx, [(960, 560), (1080, 560)], 10, hexc("#9aa0ab"))
    monitor(ctx, 120, 680, 840, 520, pose)
    tg = since(ev, "graba", lt)
    if tg >= 0:
        stamp(ctx, 540, 1270, "NADIE LA GRABA", tg, 50, col=ROJO, ang=-5)


def sc_prueba(ctx, pose, lt, ev):
    fondo(ctx, "#2f3c5a", 1300, "#e3e6ec")
    # pantalla de laboratorio comparando dos ADN
    piece(ctx, P_rrect(130, 560, 820, 600, 22), hexc("#23242c"), lw=6)
    piece(ctx, P_rect(160, 590, 760, 540), hexc("#0f1a2e"), lw=3, shadow=False)
    txt(ctx, "PRUEBA Nº 41", 540, 650, 40, hexc("#8fd3ff"), anchor="center")
    for j, x in enumerate((340, 740)):
        for i in range(12):
            w = 40 + hnoise("b", i) * 110
            piece(ctx, P_rect(x - w / 2, 690 + i * 30, w, 18), hexc("#ff5a8a") if j == 0 else hexc("#4fb3ff"),
                  lw=0, shadow=False, outline=False)
    tn = since(ev, "nada", lt)
    if tn >= 0:
        k = clamp(tn / 0.5)
        piece(ctx, P_rrect(300, 1060, 480 * max(0.05, k), 50, 10), hexc("#2fb35a"), lw=3, shadow=False)
        txt(ctx, "COINCIDE", 540, 1100, 40, (1, 1, 1), anchor="center") if k >= 1 else None
    te = since(ev, "entienden", lt)
    if te >= 0:
        stamp(ctx, 540, 900, "¿OTRA VEZ ELLA?", te, 58, col=hexc("#ffe14d"), ang=-6)
    # tubos de ensayo sobre la mesa
    for i in range(5):
        x = 260 + i * 140
        piece(ctx, P_rrect(x - 22, 1190, 44, 110, 20), hexc("#bfe3f2"), lw=4)
        piece(ctx, P_rect(x - 20, 1250, 40, 48), hexc("#ff8a8a") if i % 2 else hexc("#ffe14d"), lw=0,
              shadow=False, outline=False)


def sc_bastoncillo(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557")
    bastoncillo(ctx, 480, 940, 1.35, math.radians(-12))
    k = ease_io(clamp(lt / 0.6))
    mx, my = lerp(1000, 760, k), lerp(1250, 830, k)
    magnifier(ctx, mx, my, 150, math.radians(-30))
    if k >= 1:
        ctx.save()
        ctx.arc(mx, my, 135, 0, 2 * math.pi)
        ctx.clip()
        set_col(ctx, (1, 1, 1))
        ctx.paint()
        for i in range(14):
            piece(ctx, P_ell(mx - 120 + hnoise("lf", i) * 240, my - 120 + hnoise("lf", i, "y") * 240, 30),
                  hexc("#e6e6e6"), lw=0, shadow=False, outline=False)
        helice(ctx, mx, my - 110, my + 110, 45, pose * 0.6)
        ctx.restore()
    tm = since(ev, "muestras", lt)
    if tm >= 0:
        stamp(ctx, 380, 1220, "¡YA VENÍA DE FÁBRICA!", tm, 46, col=ROJO, ang=-6)


def sc_fabrica(ctx, pose, lt, ev):
    fondo(ctx, "#4a4f5c", 1320, "#2f333d")
    # ventanas de fábrica
    for i in range(4):
        piece(ctx, P_rect(80 + i * 250, 540, 180, 140), hexc("#bfe3f2"), lw=4, shadow=False)
    # trabajadora (silueta sin rasgos) detrás de la cinta
    silhouette(ctx, 540, 1150, 1.0, math.radians(3 if pose % 6 < 3 else -3), SOMBRA, BORDE)
    # cinta transportadora (tapa la mitad inferior)
    piece(ctx, P_rect(-10, 1080, 1100, 70), hexc("#3d3f4a"), lw=5)
    for i in range(12):
        piece(ctx, P_ell(i * 100 + (pose * 8) % 100, 1115, 22), hexc("#9aa0ab"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1150, 1100, 170), hexc("#5b6475"), lw=4, shadow=False)
    for i in range(5):
        x = (i * 260 + lt * 160) % 1300 - 200
        caja_bastoncillos(ctx, x, 960)
    stamp(ctx, 540, 1240, "ADN DE FÁBRICA", lt - 0.6, 50, col=ROJO, ang=-4)


def sc_algodon(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557")
    # calendario que pasa los años
    year = 1993 + int(16 * ease_io(clamp(lt / 2.0)))
    piece(ctx, P_rect(330, 540, 420, 300), (1, 1, 1), lw=5)
    piece(ctx, P_rect(330, 540, 420, 80), ROJO, lw=4, shadow=False)
    draw_text(ctx, str(year), 540, 740, 120, INK, INK, 0)
    bastoncillo(ctx, 470, 1060, 1.0, math.radians(-8))
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        k = ease_io(clamp(tq / 0.6))
        magnifier(ctx, lerp(980, 740, k), lerp(1300, 1050, k), 110, math.radians(-30))
    ta = since(ev, "algodon", lt)
    if ta >= 0 and tq < 0:
        stamp(ctx, 540, 1250, "SOLO ALGODÓN", ta, 52, col=hexc("#7b4dff"), ang=-5)


SCENES = dict(sebusca=sc_sebusca, mapa=sc_mapa, tablon=sc_tablon, camara=sc_camara, prueba=sc_prueba,
              bastoncillo=sc_bastoncillo, fabrica=sc_fabrica, algodon=sc_algodon)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_sebusca(ctx, 0, 3.0, {"existio_lt": 1.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(41))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "16 AÑOS BUSCANDO", 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "A UNA ASESINA…", 540, 380, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡QUE NO EXISTÍA!", 540, 1680, 110, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
