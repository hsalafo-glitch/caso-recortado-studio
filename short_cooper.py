#!/usr/bin/env python3
"""
Short 13 · «Secuestró un avión… y desapareció en el aire» — D. B. Cooper (EE. UU., 1971)
Voz gratuita (python voz_gratis.py short_cooper.py).

Uso:
    python short_cooper.py            # vídeo final (usa cache_audio/db-cooper/)
    python short_cooper.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, tree)
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier
from piezas_casos import (BORDE, ROJO, SOMBRA, VERDE_BILLETE, avion_lado, avion_noche, billetes_fajo,
                          expediente, fondo, gafas_oscuras, mochila_paracaidas, noche, nube, paracaidas, silueta)

SLUG = "db-cooper"
PRONUNCIA = {"Seattle": "Siátel", "FBI": "efe be i"}

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pasaría si un hombre secuestrara un avión… y después desapareciera en el aire para siempre?",
        escenas=[(None, "cielo")],
        pantalla=[("secuestrara", "¿SECUESTRA UN AVIÓN…"), ("desapareciera", "…Y DESAPARECE?")],
        eventos={"desap": "desapareciera"},
    ),
    dict(
        id="caso",
        voz=("Estados Unidos, 1971. Un pasajero de traje y gafas oscuras le pasa una nota a la azafata: dice que "
             "lleva una bomba. Pide 200.000 dólares y cuatro paracaídas."),
        escenas=[(None, "cabina"), ("Pide", "pedido")],
        pantalla=[(None, "EE. UU., 1971"), ("una nota", "UNA NOTA…"), ("Pide", "200.000 $ + 4 PARACAÍDAS")],
        eventos={"nota": "una nota", "bomba": "una bomba", "paracaidas": "cuatro paracaídas"},
    ),
    dict(
        id="salto",
        voz=("En Seattle le entregan el dinero, deja bajar a los pasajeros y ordena despegar otra vez. En plena "
             "noche, abre la puerta trasera… y salta con el dinero."),
        escenas=[(None, "pista"), ("En plena", "salto")],
        pantalla=[(None, "SEATTLE"), ("ordena despegar", "¡OTRA VEZ AL AIRE!"), ("y salta", "¡SALTA!")],
        eventos={"dinero": "entregan el", "bajar": "deja bajar", "despegar": "ordena despegar",
                 "puerta": "abre la", "salta": "y salta"},
    ),
    dict(
        id="rastro",
        voz=("Nunca encontraron su cuerpo. En 1980, un niño que jugaba junto a un río encontró casi 6.000 dólares "
             "enterrados en la arena: eran billetes del rescate."),
        escenas=[(None, "bosque"), ("En 1980", "rio")],
        pantalla=[(None, "NI RASTRO"), ("En 1980", "1980"), ("casi 6.000", "≈ 6.000 $ EN LA ARENA")],
        eventos={"encontro": "encontró casi", "billetes": "eran billetes"},
    ),
    dict(
        id="cierre",
        voz="El FBI cerró el caso en 2016 sin saber quién era. ¿Crees que sobrevivió al salto?",
        escenas=[(None, "expediente")],
        pantalla=[(None, "CASO CERRADO · 2016"), ("Crees", "¿SOBREVIVIÓ?")],
        eventos={"sin": "sin saber", "pregunta": "Crees que"},
    ),
]


# ─────────────────────────────── escenas ───────────────────────────────
def sc_cielo(ctx, pose, lt, ev):
    noche(ctx, pose)
    nube(ctx, 200, 1250, 1.3)
    nube(ctx, 850, 1330, 1.1)
    x = lerp(1250, 420, ease_io(clamp(lt / 2.2)))
    avion_noche(ctx, x, 780, 1.05, pose)
    td = since(ev, "desap", lt)
    if td >= 0:
        k = clamp(td / 1.4)
        px, py = x - 300 + 80 * k, 1200 + 180 * k
        if k < 0.85:
            paracaidas(ctx, px, py, 0.85, abierto=clamp(k * 3))
        else:
            nube(ctx, px, py - 120, 1.0, "#4a528a")
            bob = (pose // 4) % 2 * 10
            draw_text(ctx, "?", px, py - 330 - bob, 200, hexc("#ffe14d"), INK, 8)


def cabina_fondo(ctx):
    set_col(ctx, hexc("#d9d2c0"))
    ctx.paint()
    piece(ctx, P_rect(-10, 520, 1100, 90), hexc("#efe9da"), lw=4, shadow=False)
    for i in range(4):
        piece(ctx, P_rrect(60 + i * 260, 560, 120, 70, 30), hexc("#8ec5e8"), lw=4, shadow=False)
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#6b5a4a"), lw=4, shadow=False)


def asiento(ctx, x, y, col="#2f5d8a"):
    piece(ctx, P_rrect(x - 110, y - 260, 220, 300, 30), hexc(col), lw=5)
    piece(ctx, P_rrect(x - 95, y - 250, 190, 60, 20), hexc("#f3f1ea"), lw=3, shadow=False)


def sc_cabina(ctx, pose, lt, ev):
    cabina_fondo(ctx)
    asiento(ctx, 300, 1120)
    silueta(ctx, 300, 1180, 1.0, pose)
    gafas_oscuras(ctx, 300, 1180, 1.0)
    # corbata para «de traje»
    piece(ctx, P_poly([(300, 975), (285, 1010), (300, 1080), (315, 1010)]), hexc("#e23b3b"), lw=3, shadow=False)
    asiento(ctx, 300, 1400, "#24496e")   # respaldo de delante: tapa la mitad inferior
    piece(ctx, P_rrect(560, 1130, 230, 160, 14), hexc("#3d2b1f"), lw=5)  # maletín
    piece(ctx, P_rrect(640, 1105, 70, 34, 10), hexc("#3d2b1f"), lw=4, shadow=False)
    tn = since(ev, "nota", lt)
    if tn >= 0:
        k = ease_io(clamp(tn / 0.8))
        nx, ny = lerp(420, 850, k), lerp(980, 900, k)
        with rot(ctx, nx, ny, math.radians(-8 + 10 * k)):
            piece(ctx, P_rect(nx - 90, ny - 60, 180, 120), (1, 1, 1), lw=4)
            for j in range(3):
                line(ctx, [(nx - 65, ny - 25 + j * 25), (nx + 65, ny - 25 + j * 25)], 4, hexc("#5b6475"))
    tb = since(ev, "bomba", lt)
    if tb >= 0:
        stamp(ctx, 675, 1260, "¿UNA BOMBA?", tb, 46, col=ROJO, ang=-8)


def sc_pedido(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    n = int(clamp(lt / 1.0) * 6)
    for i in range(n):
        r, c = divmod(i, 3)
        billetes_fajo(ctx, 270 + c * 270, 860 + r * 130, 1.3)
    tp = since(ev, "paracaidas", lt)
    if tp >= 0:
        for i in range(4):
            if tp > i * 0.18:
                mochila_paracaidas(ctx, 210 + i * 220, 1210, 1.3, ["#e07a2d", "#2fb35a", "#e07a2d", "#2fb35a"][i])
    piece(ctx, P_rrect(300, 590, 480, 100, 16), hexc("#1d2433"), lw=4)
    val = int(200000 * ease_io(clamp(lt / 1.0)))
    txt(ctx, f"{val:,} $".replace(",", "."), 540, 660, 60, hexc("#9fd6a0"), anchor="center")


def sc_pista(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1180)
    for i in range(8):
        piece(ctx, P_rect(i * 150 + 20, 1260, 80, 14), hexc("#f2e7b0"), lw=0, shadow=False, outline=False)
    tdes = since(ev, "despegar", lt)
    x = 600
    y = 1000
    if tdes >= 0:
        k = ease_io(clamp(tdes / 1.6))
        x, y = lerp(600, 1600, k), lerp(1000, 650, k * k)
    with rot(ctx, x, y, math.radians(-12) * (clamp(tdes / 0.5) if tdes >= 0 else 0)):
        avion_lado(ctx, x, y, 1.15, escalera=1.0 if tdes < 0 else 0.0, luces=1)
    td = since(ev, "dinero", lt)
    tb = since(ev, "bajar", lt)
    if tdes < 0:
        if td >= 0:
            k = clamp(td / 1.0)
            # bolsa de dinero subiendo la escalera
            bx, by = lerp(60, 200, k), lerp(1180, 1090, k)
            piece(ctx, P_poly([(bx - 40, by + 40), (bx + 40, by + 40), (bx + 50, by - 10), (bx + 20, by - 40),
                               (bx - 20, by - 40), (bx - 50, by - 10)]), hexc("#c9a46a"), lw=4)
            draw_text(ctx, "$", bx, by + 5, 40, hexc("#2f6b45"), INK, 0)
        if tb >= 0:
            for i in range(4):
                k = clamp((tb - i * 0.3) / 1.2)
                if k > 0:
                    silueta(ctx, lerp(170, -80, k) - i * 10, 1180, 0.5, pose, i)


def sc_salto(ctx, pose, lt, ev):
    noche(ctx, pose)
    # lluvia
    for i in range(40):
        x = hnoise("ll", i) * 1080
        y = (hnoise("ll", i, "y") * 1400 + pose * 40) % 1400 + 500
        line(ctx, [(x, y), (x - 10, y + 40)], 3, (0.7, 0.8, 1, 0.4))
    tp = since(ev, "puerta", lt)
    esc = clamp(tp / 0.6) if tp >= 0 else 0.0
    avion_noche(ctx, 640, 760, 0.9, pose)
    if esc > 0:
        piece(ctx, P_poly([(320, 790), (370, 790), (370 - 150 * esc, 790 + 170 * esc), (320 - 150 * esc, 790 + 170 * esc)]),
              hexc("#6b6f78"), lw=4)
    ts = since(ev, "salta", lt)
    if ts >= 0:
        k = clamp(ts / 1.6)
        paracaidas(ctx, lerp(260, 420, k), lerp(1050, 1400, k), 1.0, abierto=clamp((ts - 0.5) / 0.4))
    nube(ctx, 540, 1380, 1.6, "#252c52")


def sc_bosque(ctx, pose, lt, ev):
    noche(ctx, pose, suelo=1250)
    for i in range(9):
        tree(ctx, 30 + i * 130, 1290 + (i % 2) * 40, 1.1 + (i % 3) * 0.2, hexc("#1f4a3a"), i)
    # haces de linterna buscando
    for k, x0 in enumerate((180, 860)):
        a = math.radians(-60 + 25 * math.sin(lt * 1.3 + k * 2))
        ctx.move_to(x0, 1300)
        ctx.line_to(x0 + 700 * math.cos(a - 0.12), 1300 + 700 * math.sin(a - 0.12))
        ctx.line_to(x0 + 700 * math.cos(a + 0.12), 1300 + 700 * math.sin(a + 0.12))
        ctx.close_path()
        ctx.set_source_rgba(1, 0.95, 0.6, 0.22)
        ctx.fill()
    stamp(ctx, 540, 1150, "NI CUERPO NI DINERO", lt - 0.6, 60, col=ROJO, ang=-6)


def sc_rio(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, 700, 1100, 260), hexc("#3f7fa8"), lw=4, shadow=False)
    for i in range(6):
        line(ctx, [(i * 190 + (pose * 6) % 190, 780), (i * 190 + 80 + (pose * 6) % 190, 780)], 5, hexc("#cfe9f7"))
    piece(ctx, P_rect(-10, 950, 1100, 1010), hexc("#e8cf94"), lw=4, shadow=False)
    for i in range(30):
        piece(ctx, P_ell(hnoise("ar", i) * 1080, 980 + hnoise("ar", i, "y") * 420, 6), hexc("#d4b877"), lw=0,
              shadow=False, outline=False)
    # niño (persona real: silueta pequeña, sin rasgos) cavando
    silueta(ctx, 300, 1260, 0.8, pose)
    te = since(ev, "encontro", lt)
    k = clamp(te / 0.8) if te >= 0 else 0
    piece(ctx, P_ell(640, 1240, 190, 60), hexc("#c9a96a"), lw=4, shadow=False)
    for i in range(int(6 * k)):
        with rot(ctx, 560 + i * 35, 1220, math.radians(-15 + i * 7)):
            piece(ctx, P_rect(500 + i * 35, 1200 - i * 6, 130, 50), VERDE_BILLETE, lw=3, shadow=False)
    tb = since(ev, "billetes", lt)
    if tb >= 0:
        stamp(ctx, 640, 1080, "¡DEL RESCATE!", tb, 54, col=hexc("#2f6b45"), ang=-6)


def sc_expediente(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3a3f55"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1340, 1100, 620), hexc("#5a3820"), lw=4, shadow=False)
    expediente(ctx, 190, 640, 700, 660, "EXPEDIENTE", pose)
    stamp(ctx, 540, 1200, "CASO CERRADO", lt - 0.5, 62, col=ROJO, ang=-10)
    ts = since(ev, "sin", lt)
    if ts >= 0:
        stamp(ctx, 740, 760, "SIN NOMBRE", ts, 40, col=hexc("#1d4ed8"), ang=8)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        k = ease_io(clamp(tq / 0.6))
        magnifier(ctx, lerp(1000, 720, k), lerp(1380, 1000, k), 110, math.radians(-30))


SCENES = dict(cielo=sc_cielo, cabina=sc_cabina, pedido=sc_pedido, pista=sc_pista, salto=sc_salto,
              bosque=sc_bosque, rio=sc_rio, expediente=sc_expediente)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_salto(ctx, 0, 3.0, {"puerta_lt": 0.5, "salta_lt": 1.6})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(43))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "SECUESTRÓ UN AVIÓN", 540, 220, 96, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "Y SALTÓ…", 540, 380, 110, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡NUNCA LO HALLARON!", 540, 1690, 96, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
