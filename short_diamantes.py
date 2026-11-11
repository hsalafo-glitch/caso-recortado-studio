#!/usr/bin/env python3
"""
Short 8 · «El robo de 100 millones que arruinó un sándwich» — caso real de crimen + dato impactante
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_diamantes.py            # vídeo final (usa cache_audio/diamantes-sandwich/)
    python short_diamantes.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, since, stamp, txt
from generar_marca import magnifier
from short_mentiras import persona_a
from short_obediencia import SKIN

SLUG = "diamantes-sandwich"

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pasaría si el robo perfecto se arruinara por un sándwich a medio comer?",
        escenas=[(None, "brillo")],
        pantalla=[("el robo perfecto", "¿EL ROBO PERFECTO?")],
        eventos={"sandwich": "un sándwich"},
    ),
    dict(
        id="caso",
        voz=("Amberes, 2003. Unos ladrones vacían la cámara acorazada del Centro del Diamante, una de las más "
             "seguras del mundo. Su jefe llevaba tiempo alquilando allí una oficina como falso comerciante. "
             "Botín: más de 100 millones de dólares."),
        escenas=[(None, "camara"), ("Su jefe", "oficina"), ("Botín", "botin")],
        pantalla=[(None, "AMBERES, 2003"), ("Su jefe", "EL «COMERCIANTE»"), ("Botín", "+100 MILLONES $")],
        eventos={"vacian": "vacían la"},
    ),
    dict(
        id="bolsa",
        voz=("Pero después, uno de ellos tira una bolsa de basura en un bosque. Dentro hay sobres del Centro, "
             "diamantes sueltos… y un sándwich de salami mordido."),
        escenas=[(None, "bosque")],
        pantalla=[("tira una", "LA BOLSA")],
        eventos={"tira": "tira una", "sobres": "sobres del", "diam": "diamantes sueltos", "sand": "un sándwich"},
    ),
    dict(
        id="caida",
        voz=("Las pruebas de esa bolsa llevan a la policía hasta el jefe, que cae a los pocos días. "
             "Diez años de cárcel. Casi todos los diamantes siguen sin aparecer."),
        escenas=[(None, "lupa"), ("Casi todos", "vacia")],
        pantalla=[("Diez años", "10 AÑOS DE CÁRCEL"), ("Casi todos", "¿Y LOS DIAMANTES?")],
        eventos={"cae": "que cae", "diez": "Diez años"},
    ),
    dict(
        id="cierre",
        voz="Cuando creemos que lo difícil ya pasó, bajamos la guardia. ¿Cuál ha sido tu sándwich de salami?",
        escenas=[(None, "guardia")],
        pantalla=[("Cuál ha sido", "¿CUÁL FUE TU SÁNDWICH?")],
        eventos={"guardia": "bajamos la guardia", "pregunta": "Cuál ha sido"},
    ),
]

RECORTES = ["Bloque 2: «una de las más seguras del mundo» (≈1,5 s)"]

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")


# ─────────────────────────────── piezas ───────────────────────────────
def diamante(ctx, x, y, s, pose=0, seed=0):
    tw = 1.0 if (pose + seed) % 6 else 1.15
    c = [hexc("#9fe7ff"), hexc("#6fd0f2"), hexc("#c9f3ff")][seed % 3]
    pts = [(x - 40 * s, y - 14 * s), (x - 22 * s, y - 34 * s), (x + 22 * s, y - 34 * s), (x + 40 * s, y - 14 * s),
           (x, y + 40 * s)]
    piece(ctx, P_poly(pts), c, lw=4, shadow=False)
    line(ctx, [(x - 40 * s, y - 14 * s), (x + 40 * s, y - 14 * s)], 3)
    line(ctx, [(x - 14 * s, y - 14 * s), (x, y + 40 * s), (x + 14 * s, y - 14 * s)], 2, (0, 0, 0, 0.5))
    if tw > 1:
        for a in range(4):
            aa = a * math.pi / 2
            line(ctx, [(x + 30 * s * math.cos(aa), y - 50 * s + 30 * s * math.sin(aa)),
                       (x + 52 * s * math.cos(aa), y - 50 * s + 52 * s * math.sin(aa))], 5, (1, 1, 1))


def sandwich(ctx, cx, cy, s=1.0, mordido=True):
    def pan(c, y0):
        c.save()
        c.translate(cx, cy + y0 * s)
        c.scale(s, s)
        c.new_sub_path()
        c.move_to(-220, 0)
        c.curve_to(-230, -70, 230, -70, 220, 0)
        c.line_to(220, 30)
        c.line_to(-220, 30)
        c.close_path()
        c.restore()
    piece(ctx, lambda c: pan(c, 40), hexc("#e0a85a"), lw=5)
    for k in range(6):
        piece(ctx, P_ell(cx + (-170 + k * 68) * s, cy + 20 * s, 36 * s, 16 * s), hexc("#c0392b"), lw=3, shadow=False)
    pts = [(-230 + k * 23, -6 + (10 if k % 2 else -4)) for k in range(21)]
    piece(ctx, P_poly([(cx + x * s, cy + y * s) for x, y in pts] + [(cx + 230 * s, cy + 14 * s), (cx - 230 * s, cy + 14 * s)]),
          hexc("#6cc24a"), lw=3, shadow=False)
    piece(ctx, lambda c: pan(c, -20), hexc("#f0c070"), lw=5)
    for k in range(5):
        piece(ctx, P_ell(cx + (-120 + k * 60) * s, cy - 60 * s, 6 * s, 4 * s), hexc("#fff3c4"), lw=0, shadow=False,
              outline=False)
    # el mordisco lo pinta mordisco() con el color del fondo de cada escena


def mordisco(ctx, cx, cy, s, fondo):
    for k in range(3):
        piece(ctx, P_ell(cx + 225 * s, cy + (-32 + k * 34) * s, 34 * s), fondo, lw=0, shadow=False, outline=False)


def jefe(ctx, x, feet, s=1.0, maletin=True, tilt=0.0):
    silhouette(ctx, x, feet, s, tilt, SOMBRA, BORDE)
    if maletin:
        piece(ctx, P_rrect(x + 60 * s, feet - 130 * s, 110 * s, 80 * s, 10), hexc("#3a2418"), lw=4)
        line(ctx, [(x + 95 * s, feet - 130 * s), (x + 100 * s, feet - 150 * s), (x + 130 * s, feet - 150 * s),
                   (x + 135 * s, feet - 130 * s)], 5)


def puerta_cámara(ctx, cx, cy, r, abierta, pose):
    """Puerta circular de cámara acorazada. abierta 0..1 (se abre girando sobre la bisagra)."""
    w = max(0.06, 1 - abierta)
    hx = cx + r
    ctx.save()
    ctx.translate(hx, cy)
    ctx.scale(w, 1)
    ctx.translate(-hx, -cy)
    piece(ctx, P_ell(cx, cy, r), hexc("#8a93a6"), lw=6, sh=(12, 14))
    piece(ctx, P_ell(cx, cy, r * 0.82), hexc("#a9b1c2"), lw=4, shadow=False)
    a = pose * 0.15 * (1 - abierta)
    for k in range(6):
        aa = a + k * math.pi / 3
        line(ctx, [(cx, cy), (cx + r * 0.6 * math.cos(aa), cy + r * 0.6 * math.sin(aa))], 14, hexc("#5b6475"))
        piece(ctx, P_ell(cx + r * 0.6 * math.cos(aa), cy + r * 0.6 * math.sin(aa), 22), hexc("#d6dce6"), lw=3,
              shadow=False)
    piece(ctx, P_ell(cx, cy, 50), hexc("#5b6475"), lw=4, shadow=False)
    ctx.restore()


def cajitas(ctx, x0, y0, cols, rows, abiertas=1.0):
    for i in range(cols):
        for j in range(rows):
            x, y = x0 + i * 120, y0 + j * 95
            piece(ctx, P_rect(x, y, 110, 85), hexc("#c9a54a"), lw=3, shadow=False)
            if hnoise("caja", i, j) < abiertas:
                piece(ctx, P_rect(x + 10, y + 10, 90, 65), hexc("#2d2f3a"), lw=2, shadow=False)
            else:
                piece(ctx, P_ell(x + 55, y + 42, 8), INK, lw=0, shadow=False, outline=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_brillo(ctx, pose, lt, ev):
    fondo = hexc("#1b1534")
    set_col(ctx, fondo)
    ctx.paint()
    for i in range(14):
        x = 120 + hnoise("dx", i) * 840
        y = 600 + hnoise("dy", i) * 800
        diamante(ctx, x, y, 0.6 + hnoise("ds", i) * 0.8, pose, i)
    ts = since(ev, "sandwich", lt)
    if ts >= 0:
        k = ease_out_back(clamp(ts / 0.35)) if ts < 0.35 else 1.0
        y = lerp(-300, 1040, min(1.0, k))
        sandwich(ctx, 540, y, 1.35)
        mordisco(ctx, 540, y, 1.35, fondo)
        if ts > 0.35:
            draw_text(ctx, "¡ÑAM!", 820, 840, 70, hexc("#ffe14d"), INK, 6)


def sc_camara(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3d3f4a"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#2d2f3a"), lw=4, shadow=False)
    # interior: cajas de seguridad vacías
    piece(ctx, P_rect(150, 560, 780, 720), hexc("#5b6475"), lw=5)
    tv = since(ev, "vacian", lt)
    cajitas(ctx, 180, 590, 6, 7, 1.0 if tv >= 0 else 0.0)
    ab = ease_io(clamp(lt / 0.8))
    puerta_cámara(ctx, 540, 920, 360, ab, pose)


def sc_oficina(ctx, pose, lt, ev):
    set_col(ctx, hexc("#d6dce6"))
    ctx.paint()
    for i in range(10):
        line(ctx, [(0, 200 + i * 120), (1080, 200 + i * 120)], 2, (0, 0, 0, 0.05))
    piece(ctx, P_rect(-10, 1330, 1100, 620), hexc("#8a93a6"), lw=4, shadow=False)
    piece(ctx, P_rect(560, 640, 340, 700), hexc("#7a4e2c"), lw=5)
    piece(ctx, P_ell(860, 1000, 16), hexc("#f2c94c"), lw=3, shadow=False)
    piece(ctx, P_rrect(590, 690, 280, 110, 10), hexc("#f6f1e2"), lw=4)
    draw_text(ctx, "OFICINA", 730, 725, 40, INK, INK, 0)
    draw_text(ctx, "DIAMANTES", 730, 770, 32, hexc("#1d4ed8"), INK, 0)
    jefe(ctx, 330, 1340, 1.15, True, math.radians(2) * (1 if (pose // 6) % 2 else -1))
    piece(ctx, P_rrect(280, 1170, 100, 56, 8), (1, 1, 1), lw=3, shadow=False)
    txt(ctx, "VIP", 330, 1210, 30, hexc("#e23b3b"), anchor="center")


def sc_botin(ctx, pose, lt, ev):
    set_col(ctx, hexc("#1b1534"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1360, 1100, 600), hexc("#120f22"), lw=4, shadow=False)
    # saco
    piece(ctx, P_poly([(340, 1360), (740, 1360), (800, 1020), (700, 940), (380, 940), (280, 1020)]), hexc("#8a6a3a"),
          lw=6)
    line(ctx, [(380, 950), (700, 950)], 10, hexc("#5d3a22"))
    draw_text(ctx, "$", 540, 1180, 180, hexc("#5d3a22"), INK, 0)
    for i in range(10):
        p = (lt * 1.6 + i / 10) % 1.0
        x = 380 + hnoise("bx", i) * 320
        y = lerp(450, 960, p)
        diamante(ctx, x, y, 0.55, pose, i)


def sc_bosque(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fc9a8"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#4f7a3f"), lw=4, shadow=False)
    for i, (x, sc) in enumerate(((90, 1.3), (300, 1.0), (800, 1.15), (1000, 1.4))):
        g.tree(ctx, x, 1270, sc, hexc("#2f6b45") if i % 2 else hexc("#24553c"), i)
    tt, ts, td, tsa = (since(ev, k, lt) for k in ("tira", "sobres", "diam", "sand"))
    if tt < 0:
        return
    k = clamp(tt / 0.5)
    y = lerp(380, 1180, ease_io(k))
    abierta = ts >= 0
    # bolsa
    piece(ctx, P_poly([(400, y + 120), (680, y + 120), (720, y - 60), (640, y - 140), (440, y - 140), (360, y - 60)]),
          hexc("#2a2b33"), lw=5)
    if not abierta:
        piece(ctx, P_poly([(500, y - 140), (580, y - 140), (560, y - 190), (520, y - 190)]), hexc("#2a2b33"), lw=4)
    items = []
    if ts >= 0:
        items.append(("sobre", ts, (240, 900)))
    if td >= 0:
        items.append(("diam", td, (540, 880)))
    if tsa >= 0:
        items.append(("sand", tsa, (810, 930)))
    for kind, t, (x, yy) in items:
        q = ease_out_back(clamp(t / 0.35)) if t < 0.35 else 1.0
        px, py = lerp(540, x, min(1, q)), lerp(y - 120, yy, min(1, q))
        if kind == "sobre":
            with rot(ctx, px, py, math.radians(-10)):
                piece(ctx, P_rect(px - 110, py - 70, 220, 140), hexc("#f6eab0"), lw=4)
                piece(ctx, P_poly([(px - 110, py - 70), (px, py), (px + 110, py - 70)]), hexc("#efe2c4"), lw=3,
                      shadow=False)
                txt(ctx, "CENTRO", px, py + 50, 28, INK, anchor="center")
        elif kind == "diam":
            for j in range(3):
                diamante(ctx, px - 100 + j * 100, py, 1.1, pose, j)
        else:
            sandwich(ctx, px, py, 0.75)
            mordisco(ctx, px, py, 0.75, hexc("#9fc9a8"))
            if t > 0.4:
                stamp(ctx, px, py - 120, "¡SALAMI!", t - 0.4, 40, col=hexc("#e23b3b"), ang=8)


def sc_lupa(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1340, 1100, 600), hexc("#1d2440"), lw=4, shadow=False)
    sandwich(ctx, 330, 1060, 0.85)
    mordisco(ctx, 330, 1060, 0.85, hexc("#2d3557"))
    k = clamp(lt / 0.6)
    magnifier(ctx, lerp(150, 400, ease_io(k)), 900, 120, math.radians(-30))
    tc = since(ev, "cae", lt)
    if tc >= 0:
        jefe(ctx, 800, 1350, 1.1, False)
        stamp(ctx, 800, 820, "¡DETENIDO!", tc, 52, col=hexc("#e23b3b"), ang=-8)
    td = since(ev, "diez", lt)
    if td >= 0:
        stamp(ctx, 800, 1260, "10 AÑOS", td, 60, col=hexc("#ffe14d"), ang=6)


def sc_vacia(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3d3f4a"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#2d2f3a"), lw=4, shadow=False)
    piece(ctx, P_rect(150, 560, 780, 720), hexc("#5b6475"), lw=5)
    cajitas(ctx, 180, 590, 6, 7, 1.0)
    bob = (pose // 4) % 2 * 12
    draw_text(ctx, "?", 540, 900 - bob, 380, hexc("#ffe14d"), INK, 9)


def sc_guardia(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1330, 1100, 620), hexc("#1d2440"), lw=4, shadow=False)
    persona_a(ctx, 290, 980, 110, "sonrisa", 1.0, pose=pose)
    # escudo que baja con «bajamos la guardia»
    tg = since(ev, "guardia", lt)
    a = math.radians(70) * ease_io(clamp(tg / 0.5)) if tg >= 0 else 0.0
    with rot(ctx, 680, 1150, a):
        piece(ctx, P_poly([(560, 760), (800, 760), (800, 1000), (680, 1150), (560, 1000)]), hexc("#1d4ed8"), lw=6)
        piece(ctx, P_poly([(610, 810), (750, 810), (750, 980), (680, 1070), (610, 980)]), hexc("#f2c94c"), lw=4,
              shadow=False)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        sandwich(ctx, 800, 640, 0.6)
        mordisco(ctx, 800, 640, 0.6, hexc("#2d3557"))
        bubble(ctx, 330, 690, 420, 150, (350, 820), ["¿Y EL TUYO?"], 56, col=hexc("#ffe14d"))


SCENES = dict(brillo=sc_brillo, camara=sc_camara, oficina=sc_oficina, botin=sc_botin, bosque=sc_bosque,
              lupa=sc_lupa, vacia=sc_vacia, guardia=sc_guardia)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_brillo(ctx, 0, 1.0, {"sandwich_lt": 0.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(29))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "100 MILLONES", 540, 220, 120, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "EN DIAMANTES…", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "Y UN SÁNDWICH", 540, 1620, 120, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
