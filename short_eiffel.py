#!/usr/bin/env python3
"""
Short 6 · «Vendió la Torre Eiffel (y lo intentó otra vez)» — caso real + dato impactante
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_eiffel.py            # vídeo final (usa cache_audio/torre-eiffel/)
    python short_eiffel.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import bubble, since, stamp, txt
from short_obediencia import SKIN, adulto

SLUG = "torre-eiffel"

BLOQUES = [
    dict(
        id="gancho",
        voz=("¿Qué pensarías si te dijera que un hombre vendió la Torre Eiffel… "
             "y que luego intentó venderla otra vez?"),
        escenas=[(None, "torre")],
        pantalla=[("vendió la", "VENDIÓ LA TORRE EIFFEL"), ("intentó venderla", "¡Y OTRA VEZ!")],
        eventos={"vende": "vendió la", "otra": "intentó venderla"},
    ),
    dict(
        id="caso",
        voz=("París, 1925. Victor Lustig se hace pasar por un alto cargo del Gobierno. "
             "Reúne en un hotel de lujo a varios chatarreros y les cuenta un secreto: "
             "la torre cuesta demasiado y van a desmontarla. El hierro, para quien más pague."),
        escenas=[(None, "despacho"), ("Reúne en", "hotel"), ("la torre cuesta", "desmonte")],
        pantalla=[(None, "PARÍS, 1925"), ("un secreto", "ES UN SECRETO"), ("El hierro", "EL HIERRO, A SUBASTA")],
        eventos={"cargo": "alto cargo", "secreto": "un secreto", "pague": "quien más pague"},
    ),
    dict(
        id="soborno",
        voz=("Un comprador duda. Entonces Lustig le pide un soborno… y eso le convence. "
             "Un funcionario corrupto le parecía más real que uno honrado."),
        escenas=[(None, "soborno")],
        pantalla=[("le pide", "UN SOBORNO"), ("Un funcionario", "CORRUPTO = CREÍBLE")],
        eventos={"pide": "le pide", "convence": "le convence"},
    ),
    dict(
        id="verguenza",
        voz=("Lustig cobra y desaparece. Y el comprador no lo denuncia: le da demasiada vergüenza. "
             "Así que Lustig vuelve y lo intenta otra vez. El segundo sí va a la policía."),
        escenas=[(None, "verguenza"), ("Así que", "comisaria")],
        pantalla=[("demasiada vergüenza", "VERGÜENZA"), ("El segundo", "ESTA VEZ, SÍ")],
        eventos={"desaparece": "cobra y", "segundo": "El segundo"},
    ),
    dict(
        id="cierre",
        voz="Autoridad, secreto y vergüenza: la estafa perfecta se protege sola. ¿Tú lo habrías denunciado?",
        escenas=[(None, "formula")],
        pantalla=[(None, "AUTORIDAD +"), ("secreto y", "SECRETO +"), ("y vergüenza", "VERGÜENZA ="),
                  ("la estafa", "ESTAFA PERFECTA")],
        modo_pantalla="pila",
        eventos={"pregunta": "Tú lo"},
    ),
]

RECORTES = ["Bloque 2: «El hierro, para quien más pague.» (≈1,5 s)",
            "Bloque 3: «Un funcionario corrupto le parecía más real que uno honrado.» (≈3 s)"]


# ─────────────────────────────── piezas ───────────────────────────────
def torre(ctx, cx, base, s=1.0, piezas=0.0, col="#7b5a3c"):
    """Torre de hierro de papel (genérica). piezas>0 separa los tramos."""
    c = hexc(col)
    o1, o2, o3 = piezas * 60, piezas * 130, piezas * 200
    # base con arco
    with rot(ctx, cx, base - 160 * s, math.radians(-6 * piezas)):
        ctx.save()
        ctx.translate(-o1, o1 * 0.5)
        piece(ctx, P_poly([(cx - 300 * s, base), (cx - 150 * s, base - 300 * s), (cx + 150 * s, base - 300 * s),
                           (cx + 300 * s, base), (cx + 170 * s, base), (cx, base - 170 * s), (cx - 170 * s, base)]),
              c, lw=5)
        for k in range(5):
            y = base - k * 60 * s
            w = 300 * s - k * 30 * s
            line(ctx, [(cx - w + 30 * s, y - 20 * s), (cx - w + 70 * s, y - 50 * s)], 3, (0, 0, 0, 0.35))
            line(ctx, [(cx + w - 30 * s, y - 20 * s), (cx + w - 70 * s, y - 50 * s)], 3, (0, 0, 0, 0.35))
        piece(ctx, P_rect(cx - 175 * s, base - 320 * s, 350 * s, 30 * s), c, lw=4)
        ctx.restore()
    ctx.save()
    ctx.translate(o2 * 0.4, -o2 * 0.3)
    with rot(ctx, cx, base - 450 * s, math.radians(8 * piezas)):
        piece(ctx, P_poly([(cx - 140 * s, base - 320 * s), (cx + 140 * s, base - 320 * s), (cx + 70 * s, base - 600 * s),
                           (cx - 70 * s, base - 600 * s)]), c, lw=5)
        for k in range(4):
            y = base - 350 * s - k * 65 * s
            line(ctx, [(cx - 100 * s + k * 16 * s, y), (cx + 100 * s - k * 16 * s, y - 40 * s)], 3, (0, 0, 0, 0.35))
        piece(ctx, P_rect(cx - 90 * s, base - 615 * s, 180 * s, 26 * s), c, lw=4)
    ctx.restore()
    ctx.save()
    ctx.translate(-o3 * 0.3, -o3 * 0.6)
    with rot(ctx, cx, base - 800 * s, math.radians(-12 * piezas)):
        piece(ctx, P_poly([(cx - 66 * s, base - 600 * s), (cx + 66 * s, base - 600 * s), (cx + 14 * s, base - 960 * s),
                           (cx - 14 * s, base - 960 * s)]), c, lw=5)
        piece(ctx, P_rect(cx - 5 * s, base - 1040 * s, 10 * s, 80 * s), c, lw=3)
    ctx.restore()


def estafador(ctx, x, feet, s=1.0, tilt=0.0, maleta=False):
    """Silueta sin rasgos con sombrero de copa (persona real → sin cara)."""
    col, rim = hexc("#1d1a2e"), hexc("#6b72a8")
    silhouette(ctx, x, feet, s, tilt, col, rim)
    hy = feet - 230 * s - 72 * s * 0.9
    with rot(ctx, x, feet - 230 * s, tilt):
        piece(ctx, P_rect(x - 95 * s, hy - 62 * s, 190 * s, 18 * s), col, lw=4, shadow=False)
        piece(ctx, P_rect(x - 58 * s, hy - 170 * s, 116 * s, 112 * s), col, lw=4, shadow=False)
        piece(ctx, P_rect(x - 58 * s, hy - 90 * s, 116 * s, 16 * s), hexc("#e63946"), lw=3, shadow=False)
    line(ctx, [(x + 70 * s, feet - 140 * s), (x + 95 * s, feet)], 8, col)
    if maleta:
        piece(ctx, P_rrect(x - 140 * s, feet - 120 * s, 90 * s, 70 * s, 8), hexc("#8a5a34"), lw=4)


def comprador(ctx, x, y, r=95, expr="neutro", skin=SKIN, pose=0, look=0.0, traje="#5d6b2f"):
    adulto(ctx, x, y, r, traje=traje, pelo="#6b4a2b", expr=expr, look=look, pose=pose, skin=skin)


def noche(ctx, pose):
    set_col(ctx, hexc("#1c2552"))
    ctx.paint()
    g.stars(ctx, 30, "paris", 700, pose)
    piece(ctx, P_ell(950, 720, 50), hexc("#f6eab0"), lw=4)
    g.skyline(ctx, 1350, hexc("#151b3e"), hexc("#ffd86b"), "paris", pose, 0.8)
    piece(ctx, P_rect(-10, 1340, 1100, 600), hexc("#22284a"), lw=4, shadow=False)


def cartel(ctx, x, y, texto, k, col="#e63946", ang=-6):
    if k < 0:
        return
    sc = ease_out_back(clamp(k / 0.3)) if k < 0.3 else 1.0
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang + (2 if (int(k * 12) // 4) % 2 else -2)))
    ctx.scale(sc, sc)
    line(ctx, [(-80, -110), (0, -170), (80, -110)], 5)
    piece(ctx, P_rrect(-170, -110, 340, 120, 14), hexc(col), lw=5)
    draw_text(ctx, texto, 0, -50, 62, (1, 1, 1), INK, 5)
    ctx.restore()


# ─────────────────────────────── escenas ───────────────────────────────
def sc_torre(ctx, pose, lt, ev):
    noche(ctx, pose)
    torre(ctx, 540, 1360, 0.85)
    cartel(ctx, 540, 1030, "SE VENDE", since(ev, "vende", lt))
    to = since(ev, "otra", lt)
    if to >= 0:
        stamp(ctx, 760, 1210, "¡OTRA VEZ!", to, 62, col=hexc("#e23b3b"), ang=8)


def sc_despacho(ctx, pose, lt, ev):
    set_col(ctx, hexc("#6e4127"))
    ctx.paint()
    for i in range(8):
        piece(ctx, P_rect(i * 150 - 20, 0, 140, 1300), hexc("#7d4b2d"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#4f2c18"), lw=4, shadow=False)
    estafador(ctx, 300, 1320, 1.25, math.radians(2) * (1 if (pose // 6) % 2 else -1))
    tc = since(ev, "cargo", lt)
    k = clamp(tc / 0.3) if tc >= 0 else 0
    if k > 0:
        x, y = lerp(1300, 720, ease_io(k)), 930
        with rot(ctx, x, y, math.radians(-4)):
            piece(ctx, P_rect(x - 210, y - 290, 420, 560), hexc("#fbf6ea"), lw=5, sh=(10, 12))
            draw_text(ctx, "MINISTERIO", x, y - 220, 44, INK, INK, 0)
            for j in range(6):
                line(ctx, [(x - 160, y - 140 + j * 50), (x + 160 - 40 * (j % 3), y - 140 + j * 50)], 5, (0, 0, 0, 0.3))
            piece(ctx, P_ell(x + 110, y + 190, 60), hexc("#c62828"), lw=4, shadow=False)
            draw_text(ctx, "OFICIAL", x + 110, y + 190, 22, (1, 1, 1), INK, 0)


def sc_hotel(ctx, pose, lt, ev):
    set_col(ctx, hexc("#7a2333"))
    ctx.paint()
    for i in range(9):
        line(ctx, [(i * 130, 0), (i * 130, 1250)], 4, hexc("#f2c94c", 0.25))
    # lámpara de araña
    line(ctx, [(540, 0), (540, 520)], 5, hexc("#f2c94c"))
    for k in range(-3, 4):
        piece(ctx, P_ell(540 + k * 55, 560 - abs(k) * 12, 14, 26), hexc("#fff3b0"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 1250, 1100, 700), hexc("#3d1520"), lw=4, shadow=False)
    # chatarreros sentados a la mesa
    for i, (x, sk, tr) in enumerate(((210, SKIN, "#5d6b2f"), (540, hexc("#c98b5e"), "#4b5563"),
                                     (870, hexc("#d9a77c"), "#6b4a2b"))):
        comprador(ctx, x, 950, 85, "neutro", sk, pose, look=0.0, traje=tr)
    piece(ctx, P_rect(60, 1150, 960, 60), hexc("#9b6a3f"), lw=5)
    piece(ctx, P_rect(80, 1210, 920, 180), hexc("#f6f1e2"), lw=4)
    ts = since(ev, "secreto", lt)
    if ts >= 0:
        bubble(ctx, 540, 640, 520, 150, (540, 760), ["SHHH… ES", "UN SECRETO"], 50)


def sc_desmonte(ctx, pose, lt, ev):
    noche(ctx, pose)
    k = ease_io(clamp(lt / 0.8))
    torre(ctx, 540, 1360, 0.85, piezas=k)
    tp = since(ev, "pague", lt)
    if tp >= 0:
        for i, (x, y) in enumerate(((330, 1150), (660, 900), (450, 640))):
            stamp(ctx, x, y, "¿CUÁNTO?", tp - i * 0.25, 40, col=hexc("#2fb35a"), ang=-8 + i * 7)


def billete(ctx, x, y, ang):
    with rot(ctx, x, y, ang):
        piece(ctx, P_rect(x - 70, y - 34, 140, 68), hexc("#9fd6a0"), lw=3, shadow=False)
        piece(ctx, P_ell(x, y, 18), hexc("#5fa35a"), lw=2, shadow=False)


def sc_soborno(ctx, pose, lt, ev):
    set_col(ctx, hexc("#7a2333"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#3d1520"), lw=4, shadow=False)
    tp, tc = since(ev, "pide", lt), since(ev, "convence", lt)
    estafador(ctx, 260, 1320, 1.2, math.radians(3) * (1 if (pose // 6) % 2 else -1))
    comprador(ctx, 780, 960, 100, "sonrisa" if tc >= 0 else "preocupado", SKIN, pose, look=-1.0)
    # duda → confianza
    if tc < 0:
        draw_text(ctx, "?", 900 + (4 if pose % 2 else -4), 760, 150, hexc("#ffe14d"), INK, 7)
    else:
        piece(ctx, P_ell(900, 760, 70), hexc("#2fb35a"), lw=5)
        line(ctx, [(870, 760), (895, 790), (935, 730)], 14, (1, 1, 1))
    if tp >= 0:
        k = ease_io(clamp(tp / 0.6))
        x = lerp(380, 680, k)
        y = 1160 - math.sin(k * math.pi) * 120
        piece(ctx, P_rect(x - 90, y - 55, 180, 110), hexc("#f6eab0"), lw=4)
        piece(ctx, P_poly([(x - 90, y - 55), (x, y + 5), (x + 90, y - 55)]), hexc("#efe2c4"), lw=3, shadow=False)
        billete(ctx, x - 20, y - 70, math.radians(-12))
        billete(ctx, x + 25, y - 76, math.radians(10))


def sc_verguenza(ctx, pose, lt, ev):
    set_col(ctx, hexc("#d9cfbd"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#8b7d6b"), lw=4, shadow=False)
    # comprador rojo escondido tras el periódico
    rojo = hexc("#e8574a")
    comprador(ctx, 360, 930, 100, "preocupado", rojo, pose)
    with rot(ctx, 360, 1150, math.radians(-3)):
        piece(ctx, P_rect(150, 990, 420, 300), hexc("#f6f1e2"), lw=5)
        draw_text(ctx, "DIARIO", 360, 1040, 50, INK, INK, 0)
        for j in range(4):
            line(ctx, [(180, 1100 + j * 40), (540 - 40 * (j % 2), 1100 + j * 40)], 6, (0, 0, 0, 0.3))
    # el estafador se va con la maleta
    td = since(ev, "desaparece", lt)
    k = ease_io(clamp(td / 1.2)) if td >= 0 else 0
    if k < 1:
        estafador(ctx, lerp(820, 1300, k), 1320, 1.0, math.radians(-6 if k > 0 else 0), maleta=True)


def sc_comisaria(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1300, 1100, 650), hexc("#9aa3ad"), lw=4, shadow=False)
    piece(ctx, P_rect(500, 620, 520, 690), hexc("#e3d2ad"), lw=5)
    piece(ctx, P_rrect(560, 650, 400, 100, 12), hexc("#1d4ed8"), lw=5)
    draw_text(ctx, "POLICÍA", 760, 700, 64, (1, 1, 1), INK, 0)
    piece(ctx, P_rect(680, 1000, 160, 300), hexc("#6b4a2b"), lw=5)
    for wx in (560, 880):
        piece(ctx, P_rect(wx, 820, 100, 120), hexc("#bfe3f2"), lw=4)
    ts = since(ev, "segundo", lt)
    k = ease_io(clamp(ts / 0.8)) if ts >= 0 else 0
    xc = lerp(380, 600, k)
    for dx in (-48, 8):
        piece(ctx, P_rect(xc + dx, 1220, 40, 82), hexc("#2d2f3a"), lw=4)
    comprador(ctx, xc, 960, 90, "preocupado" if k < 1 else "neutro", hexc("#c98b5e"), pose,
              look=1.0, traje="#4b5563")
    if ts < 0:
        estafador(ctx, 130 + (pose % 2) * 6, 1320, 0.9, maleta=True)
    elif ts > 0.4:
        stamp(ctx, 330, 760, "¡DENUNCIA!", ts - 0.4, 54, col=hexc("#e23b3b"), ang=-8)


def sc_formula(ctx, pose, lt, ev):
    noche(ctx, pose)
    torre(ctx, 760, 1340, 0.5)
    estafador(ctx, 330, 1330, 1.0, math.radians(4) * (1 if (pose // 6) % 2 else -1), maleta=True)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bubble(ctx, 540, 900, 760, 150, (420, 1010), ["¿LO HABRÍAS DENUNCIADO?"], 52, col=hexc("#ffe14d"))


SCENES = dict(torre=sc_torre, despacho=sc_despacho, hotel=sc_hotel, desmonte=sc_desmonte, soborno=sc_soborno,
              verguenza=sc_verguenza, comisaria=sc_comisaria, formula=sc_formula)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_torre(ctx, 0, 1.0, {"vende_lt": 0.0})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(19))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "VENDIÓ LA", 540, 220, 120, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "TORRE EIFFEL", 540, 380, 130, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡Y OTRA VEZ!", 540, 1620, 140, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
