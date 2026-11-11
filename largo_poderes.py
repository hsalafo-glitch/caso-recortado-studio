#!/usr/bin/env python3
"""
Vídeo largo 16:9 · «¿Qué pasaría si los superpoderes se consiguieran con experimentos?»
Voz: creada para este vídeo (grave, cálida, acento de España) con el motor gratuito → python voz_gratis.py largo_poderes.py

Uso:
    python largo_poderes.py            # vídeo final (cache_audio/poderes-experimentos/)
    python largo_poderes.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, stars)
from generar_short_estafas import bubble, since, stamp, txt
from generar_marca import magnifier
from largo_poderes_texto import BLOQUES_VOZ
from short_obediencia import adulto

SLUG = "poderes-experimentos"
VOZ_REF = "voz_ref.wav"
VOZ_AJUSTES = {"EXAGERACION": 0.5, "CFG": 0.45, "TEMPERATURA": 0.75, "ECO": False}
PRONUNCIA = {"biohackers": "báiojákers"}
W, H = 1920, 1080
CX = W / 2
SUELO = 900

ROJO, VERDE, AMAR, AZUL, MORADO = hexc("#e23b3b"), hexc("#2fb35a"), hexc("#ffe14d"), hexc("#1d4ed8"), hexc("#7b4dff")
SUJETO = "#2fa3a3"


def B(i, escenas, pantalla, eventos):
    return dict(id=f"b{i}", voz=BLOQUES_VOZ[i], escenas=escenas, pantalla=pantalla, eventos=eventos)


BLOQUES = [
    B(0, [(None, "intro"), ("Imagina que", "cola")],
      [("superpoderes", "SUPERPODERES REALES"), ("presentarte", "…CON EXPERIMENTOS"), ("Algunos salen", "UNOS SALEN MUY BIEN"),
       ("Otros", "…Y OTROS MUY MAL"), ("Imagina que", "EL PRIMER LABORATORIO DE PODERES")],
      {"experimento": "un experimento", "bien": "Algunos salen", "mal": "Otros", "cola": "Y que"}),
    B(1, [(None, "cuna"), ("Todo sale", "tresvias"), ("Cada voluntario", "contrato")],
      [(None, "LAS REGLAS"), ("Nadie nace", "NADIE NACE CON PODERES"), ("Todo sale", "TODO SALE DE UN LABORATORIO"),
       ("Cada voluntario", "UN CONTRATO DE 40 PÁGINAS"), ("letra pequeña", "LA LETRA PEQUEÑA…")],
      {"genes": "genes editados", "implantes": "implantes y", "farmacos": "fármacos", "letra": "letra pequeña",
       "garantiza": "no garantiza", "importante": "va a"}),
    B(2, [(None, "t1"), ("Existe un", "freno"), ("Hay razas", "vaca"), ("Así que", "levanta"), ("Pero el", "comida")],
      [(None, "EXPERIMENTO 1 · SUPERFUERZA"), ("Existe un", "EL GEN DE LA MIOSTATINA"), ("Hay razas", "VACAS SIN FRENO"),
       ("Incluso se", "TAMBIÉN EN PERSONAS"), ("Así que", "QUITAN EL FRENO"), ("Pero el", "+6.000 CALORÍAS AL DÍA"),
       ("Superfuerza, sí", "…Y HAMBRE PARA SIEMPRE")],
      {"freno": "como un", "persona": "Incluso se", "funciona": "Y funciona", "moto": "levanta una", "consumir": "empieza a"}),
    B(3, [(None, "t2"), ("En el", "gotas"), ("Resultado", "noche"), ("Su único", "gafas")],
      [(None, "EXPERIMENTO 2 · VISIÓN NOCTURNA"), ("En el", "2015: UNOS BIOHACKERS"), ("y aseguraron", "¿SILUETAS A 50 M?"),
       ("Nunca se", "NUNCA SE DEMOSTRÓ"), ("Resultado", "¡ÉXITO TOTAL!"), ("Su único", "SU PROBLEMA: EL SOL"),
       ("Probablemente", "EL MEJOR PODER DE LA LISTA")],
      {"peces": "algunos peces", "siluetas": "y aseguraron", "sol": "el sol", "gafas": "con gafas"}),
    B(4, [(None, "t3"), ("El laboratorio", "cristal"), ("Hasta que", "ojo"), ("El sujeto tres es", "ciego")],
      [(None, "EXPERIMENTO 3 · INVISIBILIDAD"), ("Y aquí", "AQUÍ EMPIEZA LO MALO"), ("Desaparece", "¡DESAPARECE!"),
       ("para ver", "PARA VER HAY QUE ATRAPAR LUZ"), ("El sujeto tres es", "INVISIBLE… Y CIEGO")],
      {"desaparece": "Desaparece delante", "aplausos": "Aplausos", "atraviesa": "Si la", "ciego": "completamente ciego"}),
    B(5, [(None, "t4"), ("La inspiración", "ajolote"), ("Al principio", "herida"), ("Pero regenerar", "celulas")],
      [(None, "EXPERIMENTO 4 · REGENERACIÓN"), ("La inspiración", "EL AJOLOTE (MÉXICO)"), ("Al principio", "¡UN MILAGRO!"),
       ("Pero regenerar", "CÉLULAS SIN FRENO…"), ("eso tiene", "…TUMOR"), ("El poder", "FUNCIONA DEMASIADO BIEN")],
      {"patas": "sus patas", "hueso": "un hueso", "sincontrol": "sin control", "bulto": "le aparece"}),
    B(6, [(None, "t5"), ("Hoy ya", "implante"), ("El laboratorio va", "dos"), ("En la calle", "calle"), ("A los tres", "boton")],
      [(None, "EXPERIMENTO 5 · TELEPATÍA"), ("Hoy ya", "IMPLANTES CEREBRALES REALES"), ("El laboratorio va", "CEREBRO A CEREBRO"),
       ("En la calle", "CIENTOS DE VOCES A LA VEZ"), ("A los tres", "UN BOTÓN PARA APAGARLO")],
      {"escribir": "escribir solo", "escucha": "puede escuchar", "vacia": "una habitación", "apagarlo": "para apagarlo"}),
    B(7, [(None, "t6"), ("Así que", "huesos"), ("Y el sujeto", "vuela"), ("Pero unos", "caida")],
      [(None, "EXPERIMENTO 6 · VOLAR"), ("Para levantar", "ALAS ENORMES + CUERPO LIGERO"), ("Así que", "HUESOS HUECOS"),
       ("Y el sujeto", "¡VUELA!"), ("Pero unos", "HUESOS FRÁGILES"), ("Puede volar", "VUELA… PERO NO PUEDE TROPEZAR")],
      {"vacia": "vacía los", "cae": "Un mal", "rompe": "se rompe"}),
    B(8, [(None, "t7"), ("La máquina", "maquina"), ("Pero los científicos", "copia")],
      [(None, "EXPERIMENTO 7 · TELETRANSPORTE"), ("La máquina", "ÁTOMO A ÁTOMO"), ("El sujeto siete", "10 METROS"),
       ("Pero los científicos", "SILENCIO…"), ("Porque la", "¿ORIGINAL… O COPIA?")],
      {"desmonta": "lo desmonta", "construir": "vuelve a", "entra": "El sujeto", "aparece": "y aparece",
       "destruido": "ha destruido", "pregunta": "quién ha"}),
    B(9, [(None, "dinero"), ("Los gobiernos", "soldados"), ("Aparecerían", "ilegal"), ("Y habría", "registro")],
      [(None, "UN MUNDO CON PODERES"), ("Probablemente", "LOS RICOS, PRIMERO"), ("Los gobiernos", "SOLDADOS CON SUPERFUERZA"),
       ("Las aseguradoras", "SEGUROS MÁS CAROS"), ("Aparecerían", "LABORATORIOS ILEGALES"), ("Y habría", "UN REGISTRO DE PODERES")],
      {"seguros": "Las aseguradoras", "peligrosos": "mucho más", "coche": "un coche"}),
    B(10, [(None, "balanza"), ("Así que", "eleccion")],
      [(None, "CADA AVANCE TIENE UN PRECIO"), ("Así que", "¿TE APUNTARÍAS?"), ("Y qué", "¿QUÉ PODER ELEGIRÍAS?"),
       ("Te leo", "TE LEO EN COMENTARIOS")],
      {"precio": "un precio", "bien": "muy bien", "mal": "muy mal", "elegirias": "Y qué"}),
]


# ─────────────────────────────── fondos y piezas ───────────────────────────────
def fondo(ctx, col="#2d3557", suelo=SUELO, col_suelo="#1d2440"):
    set_col(ctx, hexc(col))
    ctx.paint()
    if suelo is not None:
        piece(ctx, P_rect(-10, suelo, W + 20, H - suelo + 10), hexc(col_suelo), lw=4, shadow=False)


def laboratorio(ctx, col="#dfe8ee"):
    fondo(ctx, col, SUELO, "#9aa6b0")
    for i in range(0, W, 160):
        line(ctx, [(i, SUELO), (i - 80, H)], 2, hexc("#8a96a0"))
    for x in (120, 1640):
        piece(ctx, P_rect(x, 260, 200, 330), hexc("#bfe3f2"), lw=5)
        line(ctx, [(x + 100, 260), (x + 100, 590)], 4, INK)
    piece(ctx, P_rect(-10, 640, W + 20, 30), hexc("#c9ccd6"), lw=3, shadow=False)


def mesa(ctx, x0, x1, y, col="#e3e6ec"):
    piece(ctx, P_rect(x0, y, x1 - x0, 40), hexc(col), lw=5)
    piece(ctx, P_rect(x0 + 20, y + 40, x1 - x0 - 40, SUELO - y - 40 + 60), hexc("#b5bccb"), lw=4, shadow=False)


def piernas(ctx, x, y, r, col="#2b2d40"):
    for dx in (-0.55, 0.1):
        piece(ctx, P_rect(x + dx * r, y + r * 2.85, r * 0.45, r * 1.9), hexc(col), lw=4)
        piece(ctx, P_rrect(x + dx * r - r * 0.08, y + r * 4.65, r * 0.62, r * 0.25, r * 0.1), INK, lw=3, shadow=False)


def sujeto(ctx, x, y, r=80, expr="neutro", pose=0, talk=0, look=0.0, col=SUJETO, gafas=False):
    piernas(ctx, x, y, r)
    adulto(ctx, x, y, r, traje=col, pelo="#3a2a1e", expr=expr, talk=talk, look=look, pose=pose, gafas=gafas)


def cientifico(ctx, x, y, r=75, expr="neutro", pose=0, look=0.0, pelo="#7a5a2e"):
    piernas(ctx, x, y, r, "#3d3f4a")
    adulto(ctx, x, y, r, bata=True, pelo=pelo, expr=expr, look=look, pose=pose, gafas=True)


def matraz(ctx, x, y, s, col, pose=0):
    piece(ctx, P_rect(x - 22 * s, y - 150 * s, 44 * s, 70 * s), hexc("#dff2fb"), lw=4)
    piece(ctx, P_poly([(x - 22 * s, y - 80 * s), (x + 22 * s, y - 80 * s), (x + 90 * s, y + 60 * s), (x - 90 * s, y + 60 * s)]),
          hexc("#dff2fb"), lw=5)
    piece(ctx, P_poly([(x - 55 * s, y - 10 * s), (x + 55 * s, y - 10 * s), (x + 90 * s, y + 60 * s), (x - 90 * s, y + 60 * s)]),
          hexc(col), lw=0, shadow=False, outline=False)
    for i in range(3):
        yy = y - 30 * s - ((pose * 6 + i * 25) % 70) * s
        piece(ctx, P_ell(x + (i - 1) * 18 * s, yy, 8 * s), (1, 1, 1, 0.8), lw=2, shadow=False)


def helice(ctx, cx, y0, y1, amp, fase, cols=("#ff5a8a", "#4fb3ff")):
    n = 16
    pa, pb = [], []
    for i in range(n + 1):
        y = lerp(y0, y1, i / n)
        a = fase + i * 0.7
        pa.append((cx + amp * math.sin(a), y))
        pb.append((cx - amp * math.sin(a), y))
        line(ctx, [pa[-1], pb[-1]], 5, hexc("#f3f3f3"))
    line(ctx, pa, 12, hexc(cols[0]))
    line(ctx, pb, 12, hexc(cols[1]))


def chip(ctx, x, y, s=1.0):
    piece(ctx, P_rrect(x - 60 * s, y - 60 * s, 120 * s, 120 * s, 12 * s), hexc("#2b2d33"), lw=4)
    piece(ctx, P_rect(x - 30 * s, y - 30 * s, 60 * s, 60 * s), hexc("#c9a46a"), lw=3, shadow=False)
    for k in range(4):
        for d in (-1, 1):
            line(ctx, [(x - 45 * s + k * 30 * s, y + d * 60 * s), (x - 45 * s + k * 30 * s, y + d * 85 * s)], 6 * s, hexc("#9aa0ab"))
            line(ctx, [(x + d * 60 * s, y - 45 * s + k * 30 * s), (x + d * 85 * s, y - 45 * s + k * 30 * s)], 6 * s, hexc("#9aa0ab"))


def pastilla(ctx, x, y, s=1.0, ang=-0.5):
    with rot(ctx, x, y, ang):
        piece(ctx, P_rrect(x - 90 * s, y - 40 * s, 180 * s, 80 * s, 40 * s), (1, 1, 1), lw=5)
        piece(ctx, P_rrect(x, y - 40 * s, 90 * s, 80 * s, 40 * s), hexc("#e63946"), lw=0, shadow=False, outline=False)
        P_rrect(x - 90 * s, y - 40 * s, 180 * s, 80 * s, 40 * s)(ctx)
        set_col(ctx, INK)
        ctx.set_line_width(5)
        ctx.stroke()


def puno(ctx, x, y, s, col="#f59e0b"):
    piece(ctx, P_rrect(x - 70 * s, y - 60 * s, 140 * s, 120 * s, 30 * s), hexc(col), lw=5)
    for k in range(3):
        line(ctx, [(x - 40 * s + k * 40 * s, y - 60 * s), (x - 40 * s + k * 40 * s, y - 10 * s)], 4, INK)
    piece(ctx, P_rect(x - 50 * s, y + 60 * s, 100 * s, 70 * s), hexc(col), lw=5)


def ojo(ctx, x, y, s, iris="#2fb35a", pupila=1.0):
    piece(ctx, P_ell(x, y, 120 * s, 70 * s), (1, 1, 1), lw=5)
    piece(ctx, P_ell(x, y, 50 * s), hexc(iris), lw=4, shadow=False)
    piece(ctx, P_ell(x, y, 22 * s * pupila), INK, lw=0, shadow=False, outline=False)
    piece(ctx, P_ell(x - 14 * s, y - 14 * s, 8 * s), (1, 1, 1), lw=0, shadow=False, outline=False)


def fantasma_silueta(ctx, x, y, s, alpha=1.0):
    ctx.save()
    ctx.set_dash([14, 10])
    P_ell(x, y, 70 * s)(ctx)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.set_line_width(5)
    ctx.stroke()
    P_poly([(x - 110 * s, y + 70 * s), (x + 110 * s, y + 70 * s), (x + 150 * s, y + 300 * s), (x - 150 * s, y + 300 * s)])(ctx)
    ctx.stroke()
    ctx.restore()


def ajolote(ctx, x, y, s, pata=1.0, pose=0):
    rosa = hexc("#f6a6c1")
    piece(ctx, P_poly([(x + 160 * s, y), (x + 330 * s, y - 30 * s + 10 * math.sin(pose)), (x + 330 * s, y + 30 * s), (x + 160 * s, y + 40 * s)]),
          rosa, lw=4)
    piece(ctx, P_ell(x + 60 * s, y + 10 * s, 150 * s, 60 * s), rosa, lw=5)
    for k, (dx, dy) in enumerate(((-20, 60), (120, 60))):
        lp = 60 * s * (pata if k == 1 else 1.0)
        if lp > 3:
            line(ctx, [(x + dx * s, y + dy * s), (x + dx * s - 20 * s, y + dy * s + lp)], 16 * s, rosa)
    piece(ctx, P_ell(x - 110 * s, y - 10 * s, 90 * s, 75 * s), rosa, lw=5)
    for k in range(3):
        for d in (-1, 1):
            a = math.radians(-150 + k * 25) if d < 0 else math.radians(-30 - k * 25)
            line(ctx, [(x - 110 * s + d * 60 * s, y - 50 * s), (x - 110 * s + d * 60 * s + 70 * s * math.cos(a) * -d * -1,
                                                                 y - 50 * s + 70 * s * math.sin(a))], 12 * s, hexc("#e0507a"))
    for dx in (-140, -80):
        piece(ctx, P_ell(x + dx * s, y - 20 * s, 10 * s), INK, lw=0, shadow=False, outline=False)
    ctx.new_sub_path()
    ctx.arc(x - 110 * s, y + 10 * s, 30 * s, 0.2, math.pi - 0.2)
    set_col(ctx, INK)
    ctx.set_line_width(4)
    ctx.stroke()


def ala(ctx, x, y, s, lado=1, batir=0.0):
    with rot(ctx, x, y, math.radians(-25 * lado + batir * 20 * lado)):
        pts = [(x, y)]
        for k in range(6):
            pts.append((x + lado * (60 + k * 55) * s, y - (120 - k * 12) * s + k * 8 * s))
        pts += [(x + lado * 360 * s, y + 40 * s), (x + lado * 120 * s, y + 60 * s)]
        piece(ctx, P_poly(pts), (1, 1, 1), lw=5)
        for k in range(4):
            line(ctx, [(x + lado * 40 * s, y + 10 * s), (x + lado * (120 + k * 60) * s, y - (80 - k * 25) * s)], 3, hexc("#c9ccd6"))


def cabina(ctx, x, y, s, col="#4fb3ff", luz=0.0):
    piece(ctx, P_rect(x - 130 * s, y - 360 * s, 260 * s, 380 * s), hexc("#c9ccd6"), lw=5)
    piece(ctx, P_rect(x - 100 * s, y - 330 * s, 200 * s, 340 * s), hexc("#1d2433"), lw=4, shadow=False)
    if luz > 0:
        ctx.save()
        ctx.set_source_rgba(0.3, 0.8, 1, 0.35 * luz)
        ctx.rectangle(x - 100 * s, y - 330 * s, 200 * s, 340 * s)
        ctx.fill()
        ctx.restore()
    piece(ctx, P_rect(x - 140 * s, y - 380 * s, 280 * s, 40 * s), hexc(col), lw=4)
    piece(ctx, P_rect(x - 140 * s, y + 10 * s, 280 * s, 30 * s), hexc(col), lw=4)


def cerebro(ctx, x, y, s, col="#f6a6c1"):
    piece(ctx, P_ell(x, y, 110 * s, 80 * s), hexc(col), lw=5)
    for k in range(4):
        ctx.new_sub_path()
        ctx.arc(x - 60 * s + k * 40 * s, y - 10 * s, 26 * s, math.pi * 1.1, math.pi * 1.9)
        set_col(ctx, INK)
        ctx.set_line_width(3)
        ctx.stroke()
    line(ctx, [(x, y - 75 * s), (x, y + 75 * s)], 3, INK)


def icono(ctx, nombre, x, y, s, pose=0):
    if nombre == "fuerza":
        puno(ctx, x, y, s)
    elif nombre == "vision":
        ojo(ctx, x, y, s)
    elif nombre == "invisible":
        fantasma_silueta(ctx, x, y - 100 * s, s * 0.6)
    elif nombre == "regenera":
        ajolote(ctx, x + 20 * s, y, s * 0.5, pose=pose)
    elif nombre == "telepatia":
        cerebro(ctx, x, y, s)
    elif nombre == "volar":
        ala(ctx, x - 10 * s, y + 20 * s, s * 0.55, 1)
        ala(ctx, x + 10 * s, y + 20 * s, s * 0.55, -1)
    elif nombre == "teleporte":
        for k in range(3):
            P_ell(x, y, (110 - k * 30) * s, (60 - k * 15) * s)(ctx)
            set_col(ctx, hexc(["#7b4dff", "#4fb3ff", "#ffe14d"][k]))
            ctx.set_line_width(10 * s)
            ctx.stroke()


ICONOS = ["fuerza", "vision", "invisible", "regenera", "telepatia", "volar", "teleporte"]
NOMBRES = ["SUPERFUERZA", "VISIÓN NOCTURNA", "INVISIBILIDAD", "REGENERACIÓN", "TELEPATÍA", "VOLAR", "TELETRANSPORTE"]
COLS = ["#f59e0b", "#2fb35a", "#9aa0ab", "#f6a6c1", "#7b4dff", "#4fb3ff", "#e63946"]
VEREDICTO = ["BIEN… CON TRUCO", "¡GENIAL!", "FATAL", "DEMASIADO BIEN", "BIEN… HASTA SALIR", "MAL", "INQUIETANTE"]


# ─────────────────────────────── bloque 1 · gancho ───────────────────────────────
def sc_intro(ctx, pose, lt, ev):
    fondo(ctx, "#1d1a2e", None)
    stars(ctx, 50, 3, H, pose)
    for i, nom in enumerate(ICONOS):
        a = -math.pi / 2 + i * 2 * math.pi / 7 + lt * 0.15
        x, y = CX + 560 * math.cos(a), 540 + 300 * math.sin(a)
        k = clamp((lt - i * 0.18) / 0.3)
        if k > 0:
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(k, k)
            ctx.translate(-x, -y)
            piece(ctx, P_ell(x, y, 120), hexc("#2d3557"), lw=4)
            icono(ctx, nom, x, y, 0.75, pose)
            ctx.restore()
    te = since(ev, "experimento", lt)
    if te >= 0:
        matraz(ctx, CX, 600, 1.4 * clamp(te / 0.3 + 0.05), "#7b4dff", pose)
    tb, tm = since(ev, "bien", lt), since(ev, "mal", lt)
    if tb >= 0:
        stamp(ctx, CX - 330, 820, "¡GENIAL!", tb, 60, col=VERDE, ang=-8)
    if tm >= 0:
        stamp(ctx, CX + 330, 820, "¡DESASTRE!", tm, 60, col=ROJO, ang=8)


def sc_cola(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, SUELO - 40, W + 20, H), hexc("#9aa0ab"), lw=4, shadow=False)
    piece(ctx, P_rect(1080, 260, 760, 620), hexc("#f3f1ea"), lw=6)
    piece(ctx, P_rect(1060, 230, 800, 70), hexc("#7b4dff"), lw=5)
    txt(ctx, "LABORATORIO DE PODERES", 1460, 280, 42, (1, 1, 1), anchor="center")
    for r in range(2):
        for c in range(4):
            piece(ctx, P_rect(1120 + c * 180, 340 + r * 170, 120, 110), hexc("#bfe3f2"), lw=4, shadow=False)
    piece(ctx, P_rect(1400, 690, 130, 190), hexc("#5b6475"), lw=5)
    for i in range(6):
        x = 1300 - i * 190
        sujeto(ctx, x, 560 + (i % 2) * 10, 62, pose=pose + i, col=["#c94a4a", "#4a7ac9", "#d9a520", "#5fa35a", "#a77c44", "#2fa3a3"][i],
               look=1.0)
    tc = since(ev, "cola", lt)
    if tc >= 0:
        x = 1300 - 5 * 190
        k = ease_out_back(clamp(tc / 0.4)) if tc < 0.4 else 1.0
        piece(ctx, P_poly([(x, 470), (x - 40, 400), (x - 15, 400), (x - 15, 330), (x + 15, 330), (x + 15, 400), (x + 40, 400)]),
              AMAR, lw=5)
        draw_text(ctx, "TÚ", x, 290, 70 * k + 1, AMAR, INK, 7)


# ─────────────────────────────── bloque 2 · reglas ───────────────────────────────
def sc_cuna(ctx, pose, lt, ev):
    fondo(ctx, "#f2d9e6", SUELO, "#c9a0b5")
    piece(ctx, P_rrect(660, 560, 600, 260, 40), hexc("#ffffff"), lw=6)
    for k in range(9):
        line(ctx, [(690 + k * 65, 480), (690 + k * 65, 560)], 8, hexc("#c9a0b5"))
    line(ctx, [(660, 480), (1260, 480)], 10, hexc("#c9a0b5"))
    piece(ctx, P_ell(860, 560, 70), hexc("#f0c7a0"), lw=4)
    for dx in (-25, 25):
        piece(ctx, P_ell(860 + dx, 555, 7, 10), INK, lw=0, shadow=False, outline=False)
    piece(ctx, P_rrect(900, 520, 300, 110, 50), hexc("#9fd0ea"), lw=4)
    stamp(ctx, CX, 330, "SIN PODERES", lt - 1.2, 66, col=ROJO, ang=-6)


def sc_tresvias(ctx, pose, lt, ev):
    laboratorio(ctx)
    for i, (key, nombre) in enumerate((("genes", "GENES"), ("implantes", "IMPLANTES"), ("farmacos", "FÁRMACOS"))):
        x = 480 + i * 480
        t = since(ev, key, lt)
        piece(ctx, P_rrect(x - 190, 230, 380, 520, 30), (1, 1, 1), lw=5)
        txt(ctx, nombre, x, 710, 48, INK, anchor="center")
        if t >= 0:
            k = ease_out_back(clamp(t / 0.35)) if t < 0.35 else 1.0
            ctx.save()
            ctx.translate(x, 440)
            ctx.scale(max(0.05, k), max(0.05, k))
            ctx.translate(-x, -440)
            if i == 0:
                helice(ctx, x, 300, 600, 70, pose * 0.4)
            elif i == 1:
                chip(ctx, x, 450, 1.3)
            else:
                pastilla(ctx, x, 450, 1.2)
            ctx.restore()


def sc_contrato(ctx, pose, lt, ev):
    fondo(ctx, "#3a3f55", SUELO, "#5a3820")
    piece(ctx, P_rect(560, 200, 800, 700), (1, 1, 1), lw=6, sh=(12, 16))
    txt(ctx, "CONTRATO DEL VOLUNTARIO", CX, 270, 44, INK, anchor="center")
    for k in range(10):
        line(ctx, [(620, 330 + k * 45), (1300, 330 + k * 45)], 6, hexc("#c9ccd6"))
    pag = min(40, 1 + int(lt * 12))
    piece(ctx, P_rrect(1400, 220, 260, 90, 14), hexc("#1d2433"), lw=4)
    txt(ctx, f"PÁG. {pag}/40", 1530, 282, 44, AMAR, anchor="center")
    txt(ctx, "el laboratorio no garantiza el resultado", 960, 840, 18, hexc("#5b6475"), anchor="center")
    line(ctx, [(1100, 870), (1300, 860)], 4, hexc("#1d4ed8"))
    tl = since(ev, "letra", lt)
    if tl >= 0:
        k = ease_io(clamp(tl / 0.6))
        mx, my = lerp(1700, 960, k), lerp(900, 790, k)
        magnifier(ctx, mx, my, 150, math.radians(-25))
    tg = since(ev, "garantiza", lt)
    if tg >= 0:
        piece(ctx, P_rrect(420, 560, 1080, 140, 20), (1, 1, 1), lw=6)
        txt(ctx, "«NO GARANTIZA EL RESULTADO»", CX, 650, 58, ROJO, anchor="center")
    ti = since(ev, "importante", lt)
    if ti >= 0:
        stamp(ctx, 1500, 480, "¡OJO!", ti, 70, col=ROJO, ang=10)


# ─────────────────────────────── títulos de experimento ───────────────────────────────
def hacer_titulo(n):
    def sc(ctx, pose, lt, ev):
        fondo(ctx, "#1d2433", None)
        for i in range(12):
            line(ctx, [(i * 180 - (lt * 80) % 180, 0), (i * 180 - 300 - (lt * 80) % 180, H)], 40, (1, 1, 1, 0.03))
        k = ease_out_back(clamp(lt / 0.4)) if lt < 0.4 else 1.0
        piece(ctx, P_rrect(560, 230, 800, 560, 40), hexc(COLS[n]), lw=7, sh=(14, 18))
        ctx.save()
        ctx.translate(CX, 500)
        ctx.scale(max(0.05, k), max(0.05, k))
        ctx.translate(-CX, -500)
        piece(ctx, P_ell(CX, 470, 170), (1, 1, 1), lw=6)
        icono(ctx, ICONOS[n], CX, 470, 1.1, pose)
        ctx.restore()
        draw_text(ctx, f"Nº {n + 1}", CX, 720, 90, (1, 1, 1), INK, 8)
        if lt > 1.2:
            col = VERDE if n in (1,) else (ROJO if n in (2, 5) else hexc("#f59e0b"))
            stamp(ctx, 1580, 780, VEREDICTO[n], lt - 1.2, 44, col=col, ang=-8) if lt > 99 else None
    return sc


# ─────────────────────────────── bloque 3 · superfuerza ───────────────────────────────
def sc_freno(ctx, pose, lt, ev):
    laboratorio(ctx)
    piece(ctx, P_rrect(300, 220, 420, 620, 30), (1, 1, 1), lw=5)
    helice(ctx, 510, 270, 780, 90, pose * 0.4)
    txt(ctx, "MIOSTATINA", 510, 830, 40, INK, anchor="center")
    tf = since(ev, "freno", lt)
    if tf >= 0:
        k = ease_out_back(clamp(tf / 0.35)) if tf < 0.35 else 1.0
        piece(ctx, P_rrect(1000, 420, 500 * k, 220 * k, 30), ROJO, lw=6)
        if k > 0.9:
            draw_text(ctx, "FRENO", 1250, 530, 110, (1, 1, 1), INK, 8)
        puno(ctx, 1250, 760, 0.8)


def vaca(ctx, x, y, s, pose):
    piece(ctx, P_ell(x, y, 300 * s, 170 * s), (1, 1, 1), lw=6)
    for (dx, dy, r) in ((-120, -40, 60), (80, 40, 70), (150, -60, 40)):
        piece(ctx, P_ell(x + dx * s, y + dy * s, r * s, r * 0.8 * s), INK, lw=0, shadow=False, outline=False)
    for dx in (-220, -110, 120, 230):
        piece(ctx, P_rrect(x + dx * s - 35 * s, y + 110 * s, 70 * s, 190 * s, 20 * s), (1, 1, 1), lw=5)
    for dx in (-140, 0, 140):
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y - 40 * s, 70 * s, math.pi * 1.15, math.pi * 1.85)
        set_col(ctx, INK)
        ctx.set_line_width(4)
        ctx.stroke()
    hx = x + 330 * s
    piece(ctx, P_rrect(hx - 70 * s, y - 170 * s, 160 * s, 190 * s, 50 * s), (1, 1, 1), lw=6)
    piece(ctx, P_rrect(hx - 60 * s, y - 40 * s, 150 * s, 70 * s, 30 * s), hexc("#f6a6c1"), lw=4)
    for dx in (-30, 50):
        piece(ctx, P_ell(hx + dx * s, y - 110 * s, 12 * s), INK, lw=0, shadow=False, outline=False)
        piece(ctx, P_poly([(hx + dx * s, y - 170 * s), (hx + dx * s + 20 * s, y - 230 * s), (hx + dx * s + 40 * s, y - 165 * s)]),
              hexc("#f3e6c9"), lw=3)


def sc_vaca(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, 760, W + 20, 400), hexc("#7cc46a"), lw=4, shadow=False)
    vaca(ctx, 700, 560, 1.15, pose)
    stamp(ctx, 700, 260, "SIN FRENO", lt - 0.8, 60, col=ROJO, ang=-6)
    tp = since(ev, "persona", lt)
    if tp >= 0:
        sujeto(ctx, 1500, 430, 80, expr="sonrisa", pose=pose, col="#f59e0b")
        stamp(ctx, 1500, 300, "MUTACIÓN REAL", tp, 44, col=AZUL, ang=6)


def moto(ctx, x, y, s):
    for wx in (x - 120 * s, x + 120 * s):
        piece(ctx, P_ell(wx, y, 60 * s), INK, lw=3, shadow=False)
        piece(ctx, P_ell(wx, y, 24 * s), hexc("#9aa0ab"), lw=2, shadow=False)
    piece(ctx, P_poly([(x - 130 * s, y - 40 * s), (x + 60 * s, y - 70 * s), (x + 150 * s, y - 40 * s), (x + 110 * s, y - 10 * s),
                       (x - 90 * s, y - 10 * s)]), hexc("#e63946"), lw=4)
    line(ctx, [(x + 110 * s, y - 50 * s), (x + 130 * s, y - 130 * s)], 8 * s, INK)


def sc_levanta(ctx, pose, lt, ev):
    laboratorio(ctx)
    tm = since(ev, "moto", lt)
    k = ease_io(clamp(tm / 0.6)) if tm >= 0 else 0
    sujeto(ctx, CX, 470, 95, expr="sonrisa" if k > 0.5 else "neutro", pose=pose)
    # brazos levantados en diagonal (sin dedos)
    for d in (-1, 1):
        line(ctx, [(CX + d * 90, 600), (CX + d * 170, lerp(620, 380, k))], 34, hexc(SUJETO))
        piece(ctx, P_ell(CX + d * 170, lerp(620, 380, k), 30), hexc("#f0c7a0"), lw=4)
    moto(ctx, CX, lerp(820, 300, k), 1.0)
    mesa(ctx, CX - 300, CX + 300, 760) if k < 0.05 else None
    tf = since(ev, "funciona", lt)
    if tf >= 0:
        stamp(ctx, 1500, 450, "¡FUNCIONA!", tf, 70, col=VERDE, ang=-8)


def sc_comida(ctx, pose, lt, ev):
    fondo(ctx, "#f2e0b0", SUELO, "#a77c44")
    sujeto(ctx, 600, 400, 85, expr="sonrisa", talk=pose % 2 + 1, pose=pose)
    mesa(ctx, 250, 1700, 640, "#c9a46a")
    n = int(clamp(lt / 3.0) * 10)
    for i in range(n):
        x = 900 + (i % 5) * 150
        y = 620 - (i // 5) * 40
        piece(ctx, P_ell(x, y, 70, 22), (1, 1, 1), lw=4)
        piece(ctx, P_ell(x, y - 10, 45, 18), hexc(["#c94a4a", "#d9a520", "#5fa35a"][i % 3]), lw=3, shadow=False)
    piece(ctx, P_rrect(1300, 220, 460, 110, 16), hexc("#1d2433"), lw=4)
    v = int(6000 * ease_io(clamp(lt / 3.0)))
    txt(ctx, f"{v:,} kcal".replace(",", "."), 1530, 295, 60, AMAR, anchor="center")
    tc = since(ev, "consumir", lt)
    if tc >= 0:
        bubble(ctx, 300, 260, 300, 110, (520, 380), ["¡GRRR!"], 56)


# ─────────────────────────────── bloque 4 · visión nocturna ───────────────────────────────
def pez_abisal(ctx, x, y, s, pose):
    piece(ctx, P_ell(x, y, 130 * s, 70 * s), hexc("#3a2f5a"), lw=4)
    piece(ctx, P_poly([(x + 120 * s, y), (x + 210 * s, y - 60 * s), (x + 210 * s, y + 60 * s)]), hexc("#3a2f5a"), lw=4)
    for k in range(5):
        piece(ctx, P_poly([(x - 120 * s + k * 18 * s, y + 10 * s), (x - 110 * s + k * 18 * s, y + 40 * s), (x - 100 * s + k * 18 * s, y + 10 * s)]),
              (1, 1, 1), lw=1, shadow=False)
    line(ctx, [(x - 60 * s, y - 60 * s), (x - 130 * s, y - 150 * s), (x - 180 * s, y - 120 * s)], 4, hexc("#9aa0ab"))
    on = (pose // 3) % 2 == 0
    ctx.save()
    ctx.set_source_rgba(0.4, 1, 0.8, 0.35 if on else 0.2)
    ctx.arc(x - 180 * s, y - 120 * s, 50 * s, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    piece(ctx, P_ell(x - 180 * s, y - 120 * s, 14 * s), hexc("#9fffd9"), lw=2, shadow=False)
    piece(ctx, P_ell(x - 70 * s, y - 15 * s, 14 * s), (1, 1, 1), lw=2, shadow=False)


def sc_gotas(ctx, pose, lt, ev):
    fondo(ctx, "#141a33", None)
    tp = since(ev, "peces", lt)
    ts = since(ev, "siluetas", lt)
    if ts >= 0:
        for i in range(5):
            x = 300 + i * 330
            ctx.save()
            ctx.set_source_rgba(0.5, 1, 0.6, 0.18 + 0.1 * (i % 2))
            P_ell(x, 520, 50)(ctx)
            ctx.fill()
            P_rect(x - 60, 570, 120, 260)(ctx)
            ctx.fill()
            ctx.restore()
        piece(ctx, P_rrect(780, 860, 360, 80, 14), hexc("#1d2433"), lw=4)
        txt(ctx, "50 METROS", CX, 915, 48, hexc("#9fffd9"), anchor="center")
        return
    ojo(ctx, CX, 640, 2.0, iris="#4a7ac9")
    # cuentagotas
    piece(ctx, P_rrect(CX - 30, 160, 60, 220, 20), hexc("#dff2fb"), lw=5)
    piece(ctx, P_rrect(CX - 40, 120, 80, 70, 24), hexc("#e63946"), lw=5)
    yd = 380 + ((lt * 300) % 160)
    piece(ctx, P_poly([(CX, yd - 20), (CX + 14, yd + 6), (CX, yd + 20), (CX - 14, yd + 6)]), hexc("#9fffd9"), lw=3)
    if tp >= 0:
        pez_abisal(ctx, lerp(2200, 1550, ease_io(clamp(tp / 1.2))), 330, 1.0, pose)


def sc_noche(ctx, pose, lt, ev):
    set_col(ctx, hexc("#06080f"))
    ctx.paint()
    stars(ctx, 30, 9, 500, pose)
    k = ease_io(clamp(lt / 1.0))
    xm = lerp(W, CX, k)
    ctx.save()
    ctx.rectangle(xm, 0, W, H)
    ctx.clip()
    set_col(ctx, hexc("#163a22"))
    ctx.paint()
    for i in range(4):
        x = 1100 + i * 220
        piece(ctx, P_ell(x, 520, 45), hexc("#6fe08f"), lw=3, shadow=False)
        piece(ctx, P_rect(x - 55, 565, 110, 240), hexc("#4fc06f"), lw=3, shadow=False)
    piece(ctx, P_rect(-10, 805, W + 20, 300), hexc("#0f2a18"), lw=0, shadow=False, outline=False)
    ctx.restore()
    line(ctx, [(xm, 0), (xm, H)], 8, (1, 1, 1))
    txt(ctx, "SIN PODER", 480, 300, 48, hexc("#5b6475"), anchor="center")
    if k > 0.9:
        txt(ctx, "CON PODER", 1440, 300, 48, hexc("#9fffd9"), anchor="center")


def sc_gafas(ctx, pose, lt, ev):
    set_col(ctx, hexc("#9fd0ea"))
    ctx.paint()
    piece(ctx, P_rect(-10, 780, W + 20, 400), hexc("#e8cf94"), lw=4, shadow=False)
    ts = since(ev, "sol", lt)
    piece(ctx, P_ell(1600, 230, 110), hexc("#ffe14d"), lw=5)
    if ts >= 0:
        for a in range(12):
            ang = a * math.pi / 6 + lt * 0.5
            line(ctx, [(1600 + 140 * math.cos(ang), 230 + 140 * math.sin(ang)), (1600 + 210 * math.cos(ang), 230 + 210 * math.sin(ang))],
                 10, hexc("#ffb02e"))
    tg = since(ev, "gafas", lt)
    sujeto(ctx, 800, 420, 100, expr="sonrisa" if tg >= 0 else "preocupado", pose=pose, col="#7b4dff")
    if tg >= 0:
        for dx in (-38, 38):
            piece(ctx, P_rrect(800 + dx - 36, 405, 72, 44, 14), INK, lw=3, shadow=False)
        line(ctx, [(780, 425), (820, 425)], 6, INK)


# ─────────────────────────────── bloque 5 · invisibilidad ───────────────────────────────
def sc_cristal(ctx, pose, lt, ev):
    laboratorio(ctx)
    td = since(ev, "desaparece", lt)
    a = 1.0 - clamp(td / 1.0) if td >= 0 else 1.0
    if a > 0:
        ctx.push_group()
        sujeto(ctx, CX, 420, 95, pose=pose)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
    if a < 1:
        fantasma_silueta(ctx, CX, 390, 1.0, alpha=0.5 * (1 - a))
    ta = since(ev, "aplausos", lt)
    if ta >= 0:
        for i in range(4):
            x = 260 + i * 130 if i < 2 else 1400 + (i - 2) * 160
            cientifico(ctx, x, 560, 60, expr="sonrisa", pose=pose + i)
        if (pose // 2) % 2 == 0:
            txt(ctx, "¡CLAP! ¡CLAP!", 1500, 380, 50, AMAR, anchor="center")


def sc_ojo(ctx, pose, lt, ev):
    fondo(ctx, "#1d2433", None)
    ta = since(ev, "atraviesa", lt)
    # ojo en corte
    piece(ctx, P_ell(CX, 540, 300), (1, 1, 1, 0.92) if ta < 0 else (1, 1, 1, 0.15), lw=6)
    piece(ctx, P_ell(CX - 290, 540, 40, 110), hexc("#bfe3f2"), lw=4, shadow=False)
    ret = AMAR if ta < 0 else hexc("#3d3f4a")
    ctx.new_sub_path()
    ctx.arc(CX, 540, 290, -0.9, 0.9)
    set_col(ctx, ret)
    ctx.set_line_width(28)
    ctx.stroke()
    txt(ctx, "RETINA", CX + 340, 360, 40, ret, anchor="center")
    for k in range(3):
        y = 470 + k * 70
        x1 = CX + 270 if ta < 0 else W + 50
        line(ctx, [(0, y), (CX - 290, y), (x1, 540 + (y - 540) * (0.3 if ta < 0 else 1.0))], 8, hexc("#ffe14d"))
    if ta >= 0:
        stamp(ctx, CX, 870, "LA LUZ NO SE QUEDA", ta, 54, col=ROJO, ang=-5)


def sc_ciego(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", SUELO, "#1d2440")
    fantasma_silueta(ctx, CX, 390, 1.1, alpha=0.8)
    bob = (pose // 4) % 2 * 10
    for i, (x, y) in enumerate(((CX - 300, 300), (CX + 300, 320))):
        draw_text(ctx, "?", x, y - bob, 120, AMAR, INK, 7)
    tc = since(ev, "ciego", lt)
    if tc >= 0:
        stamp(ctx, CX, 820, "INVISIBLE Y CIEGO", tc, 62, col=ROJO, ang=-6)


# ─────────────────────────────── bloque 6 · regeneración ───────────────────────────────
def sc_ajolote(ctx, pose, lt, ev):
    set_col(ctx, hexc("#6fb6c9"))
    ctx.paint()
    piece(ctx, P_rect(-10, 820, W + 20, 300), hexc("#c9b48a"), lw=4, shadow=False)
    for i in range(8):
        x = 100 + i * 250
        line(ctx, [(x, 830), (x + 20 * math.sin(lt + i), 620)], 10, hexc("#2f9e4f"))
    tp = since(ev, "patas", lt)
    pata = clamp(tp / 1.5) if tp >= 0 else 0.2
    ajolote(ctx, CX - 100, 520, 1.6, pata=pata, pose=pose)
    if tp >= 0:
        stamp(ctx, 1550, 300, "SE REGENERA", tp, 52, col=VERDE, ang=-6)


def sc_herida(ctx, pose, lt, ev):
    fondo(ctx, "#f2e0d0", None)
    piece(ctx, P_rrect(300, 380, 1300, 220, 100), hexc("#f0c7a0"), lw=6)
    k = clamp(lt / 2.0)
    if k < 1:
        line(ctx, [(800, 490 - 50 * (1 - k)), (1100, 490 + 50 * (1 - k))], 14 * (1 - k) + 1, hexc("#c92a2a"))
    piece(ctx, P_rrect(1450, 160, 300, 110, 16), hexc("#1d2433"), lw=4)
    txt(ctx, f"{int(k * 3)} MIN", 1600, 235, 60, AMAR, anchor="center")
    th = since(ev, "hueso", lt)
    if th >= 0:
        kk = clamp(th / 1.0)
        piece(ctx, P_rrect(500, 720, 900, 90, 45), (1, 1, 1), lw=5)
        if kk < 1:
            line(ctx, [(930, 715), (960, 765), (940, 815)], 8, ROJO)
        stamp(ctx, 1600, 760, "SOLDADO", th - 1.0, 44, col=VERDE, ang=-6)


def sc_celulas(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", None)
    tsc = since(ev, "sincontrol", lt)
    n = min(64, 2 ** int(1 + lt * 1.5)) if tsc < 0 else 64
    cols = 8
    for i in range(n):
        r, c = divmod(i, cols)
        x, y = 600 + c * 95 + (r % 2) * 40, 260 + r * 75
        piece(ctx, P_ell(x, y, 40, 34), hexc("#f6a6c1") if tsc < 0 else hexc("#e05050"), lw=3, shadow=False)
        piece(ctx, P_ell(x, y, 12), hexc("#7b4dff"), lw=0, shadow=False, outline=False)
    piece(ctx, P_rrect(200, 220, 300, 110, 16), hexc("#1d2433"), lw=4)
    txt(ctx, f"×{n}", 350, 295, 64, AMAR, anchor="center")
    tb = since(ev, "bulto", lt)
    if tb >= 0:
        stamp(ctx, CX, 860, "UN BULTO", tb, 64, col=ROJO, ang=-6)


# ─────────────────────────────── bloque 7 · telepatía ───────────────────────────────
def pantalla_escribe(ctx, x, y, w, h, texto, k):
    piece(ctx, P_rrect(x, y, w, h, 20), hexc("#23242c"), lw=6)
    piece(ctx, P_rect(x + 20, y + 20, w - 40, h - 40), hexc("#0f1a2e"), lw=3, shadow=False)
    n = int(len(texto) * k)
    txt(ctx, texto[:n] + ("|" if int(k * 20) % 2 else ""), x + 50, y + h / 2 + 15, 44, hexc("#9fffd9"))


def sc_implante(ctx, pose, lt, ev):
    laboratorio(ctx)
    sujeto(ctx, 520, 420, 95, pose=pose, look=1.0)
    chip(ctx, 520, 330, 0.35)
    te = since(ev, "escribir", lt)
    k = clamp(lt / 3.0) if te < 0 else 1.0
    pantalla_escribe(ctx, 900, 260, 820, 400, "HOLA, MUNDO", k)
    for i in range(3):
        a = (lt * 3 + i) % 3 / 3
        ctx.new_sub_path()
        ctx.arc(520, 330, 120 + a * 200, -0.6, 0.6)
        ctx.set_source_rgba(0.6, 1, 0.85, 1 - a)
        ctx.set_line_width(6)
        ctx.stroke()


def sc_dos(ctx, pose, lt, ev):
    laboratorio(ctx)
    sujeto(ctx, 560, 420, 90, pose=pose, look=1.0)
    sujeto(ctx, 1360, 420, 90, pose=pose + 3, look=-1.0, col="#c94a4a")
    ctx.move_to(560, 330)
    ctx.curve_to(760, 150, 1160, 150, 1360, 330)
    set_col(ctx, hexc("#7b4dff"))
    ctx.set_line_width(10)
    ctx.stroke()
    for x in (560, 1360):
        chip(ctx, x, 330, 0.3)
    te = since(ev, "escucha", lt)
    if te >= 0:
        bubble(ctx, 1360, 140, 380, 110, (1300, 300), ["TENGO HAMBRE"], 40)
        bubble(ctx, 560, 140, 380, 110, (620, 300), ["…TIENE HAMBRE"], 40)
    tv = since(ev, "vacia", lt)
    if tv >= 0:
        stamp(ctx, CX, 820, "PERFECTO", tv, 56, col=VERDE, ang=-6)


def sc_calle(ctx, pose, lt, ev):
    set_col(ctx, hexc("#c9d6e3"))
    ctx.paint()
    for i in range(7):
        x = i * 290 - 40
        h = 380 + (i % 3) * 90
        piece(ctx, P_rect(x, SUELO - h, 250, h), hexc(["#9aa0ab", "#b5bccb", "#8a8f9a"][i % 3]), lw=4)
    piece(ctx, P_rect(-10, SUELO - 120, W + 20, H), hexc("#6b6f78"), lw=4, shadow=False)
    for i in range(7):
        x = 150 + i * 270
        if i == 3:
            continue
        sujeto(ctx, x, 560 + (i % 2) * 20, 55, pose=pose + i, col=["#c94a4a", "#4a7ac9", "#d9a520", "#5fa35a", "#a77c44", "#2f6b45", "#e07a2d"][i])
    sujeto(ctx, 960, 520, 75, expr="grito", pose=pose)
    frases = ["¡LLEGO TARDE!", "¿Y SI ME DESPIDEN?", "ODIO LOS LUNES", "NO SE LO DIGAS A NADIE", "¡QUÉ HAMBRE!",
              "¿HE CERRADO LA PUERTA?", "ME DEBE DINERO", "¡ESTE TRÁFICO!"]
    n = min(len(frases), int(lt * 2.5))
    for i in range(n):
        x = 220 + (i % 4) * 480 + (hnoise("cf", i) - 0.5) * 60
        y = 280 + (i // 4) * 150
        bubble(ctx, x, y, 400, 100, (x + (60 if x < CX else -60), y + 120), [frases[i]], 30, think=True)


def sc_boton(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", None)
    ta = since(ev, "apagarlo", lt)
    pulsado = ta >= 0.4
    piece(ctx, P_ell(CX, 640, 260, 110), hexc("#3d3f4a"), lw=6)
    piece(ctx, P_ell(CX, 600 if not pulsado else 625, 220, 95), hexc("#c92a2a") if not pulsado else hexc("#8a1d1d"), lw=6)
    txt(ctx, "OFF", CX, 620 if not pulsado else 645, 90, (1, 1, 1), anchor="center")
    if ta >= 0:
        stamp(ctx, CX, 320, "¡SILENCIO!", ta - 0.4, 70, col=VERDE, ang=-6)


# ─────────────────────────────── bloque 8 · volar ───────────────────────────────
def hueso_corte(ctx, x, y, s, hueco=False, rotura=False):
    piece(ctx, P_ell(x, y, 180 * s), hexc("#f3e6c9"), lw=6)
    if hueco:
        piece(ctx, P_ell(x, y, 140 * s), hexc("#2d3557"), lw=4, shadow=False)
        for k in range(4):
            a = k * math.pi / 4
            line(ctx, [(x + 140 * s * math.cos(a), y + 140 * s * math.sin(a)), (x - 140 * s * math.cos(a), y - 140 * s * math.sin(a))],
                 6 * s, hexc("#f3e6c9"))
    else:
        piece(ctx, P_ell(x, y, 60 * s), hexc("#e0b080"), lw=3, shadow=False)
    if rotura:
        line(ctx, [(x - 30 * s, y - 190 * s), (x + 20 * s, y - 60 * s), (x - 20 * s, y + 40 * s), (x + 30 * s, y + 190 * s)], 10, ROJO)


def sc_huesos(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", None)
    hueso_corte(ctx, 600, 520, 1.3)
    txt(ctx, "NORMAL", 600, 840, 50, (1, 1, 1), anchor="center")
    tv = since(ev, "vacia", lt)
    hueso_corte(ctx, 1320, 520, 1.3, hueco=tv >= 0)
    txt(ctx, "HUECO" if tv >= 0 else "…", 1320, 840, 50, AMAR, anchor="center")


def sc_vuela(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    for i in range(5):
        x = (i * 470 - lt * 120) % (W + 400) - 200
        for dx, dy, r in ((-60, 10, 50), (0, -15, 70), (60, 10, 50)):
            piece(ctx, P_ell(x + dx, 200 + (i % 2) * 300 + dy, r), (1, 1, 1), lw=0, shadow=False, outline=False)
    g.skyline(ctx, H, hexc("#5b6475"), hexc("#ffe58a"), 4, pose, 0.9) if hasattr(g, "skyline") else None
    y = 480 + 30 * math.sin(lt * 2)
    bat = 1.0 if pose % 6 < 3 else -0.6
    ala(ctx, CX - 40, y + 120, 1.0, -1, bat)
    ala(ctx, CX + 40, y + 120, 1.0, 1, bat)
    sujeto(ctx, CX, y, 80, expr="sonrisa", pose=pose, col="#4fb3ff")


def sc_caida(ctx, pose, lt, ev):
    set_col(ctx, hexc("#8ec5e8"))
    ctx.paint()
    piece(ctx, P_rect(-10, SUELO, W + 20, H), hexc("#7cc46a"), lw=4, shadow=False)
    tc = since(ev, "cae", lt)
    tr = since(ev, "rompe", lt)
    if tc < 0:
        ala(ctx, 760, 520, 0.8, -1, 0)
        ala(ctx, 840, 520, 0.8, 1, 0)
        sujeto(ctx, 800, 420, 70, pose=pose, col="#4fb3ff")
    else:
        y = lerp(420, 760, clamp(tc / 0.6))
        with rot(ctx, 800, y + 100, math.radians(70 * clamp(tc / 0.6))):
            ala(ctx, 760, y + 100, 0.8, -1, 0)
            ala(ctx, 840, y + 100, 0.8, 1, 0)
            sujeto(ctx, 800, y, 70, expr="grito", pose=pose, col="#4fb3ff")
    hueso_corte(ctx, 1450, 420, 0.8, hueco=True, rotura=tr >= 0)
    if tr >= 0:
        stamp(ctx, 1450, 750, "¡CRAC!", tr, 70, col=ROJO, ang=-8)


# ─────────────────────────────── bloque 9 · teletransporte ───────────────────────────────
def particulas(ctx, x, y, k, seed, col=(0.6, 0.9, 1)):
    for i in range(40):
        a = hnoise(seed, i) * 2 * math.pi
        r = 30 + hnoise(seed, i, "r") * 200 * k
        ctx.save()
        ctx.set_source_rgba(col[0], col[1], col[2], 1 - k * 0.7)
        ctx.arc(x + r * math.cos(a), y - 150 + r * math.sin(a) * 1.4, 6, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()


def sc_maquina(ctx, pose, lt, ev):
    laboratorio(ctx, "#cfd8e3")
    cabina(ctx, 560, 860, 1.2, luz=1.0 if since(ev, "desmonta", lt) >= 0 else 0.0)
    cabina(ctx, 1360, 860, 1.2, col="#7b4dff", luz=1.0 if since(ev, "construir", lt) >= 0 else 0.0)
    line(ctx, [(720, 470), (1200, 470)], 10, hexc("#4fb3ff"))
    piece(ctx, P_rrect(870, 400, 180, 70, 14), hexc("#1d2433"), lw=4)
    txt(ctx, "10 m", CX, 450, 44, AMAR, anchor="center")
    td = since(ev, "desmonta", lt)
    tc = since(ev, "construir", lt)
    te = since(ev, "entra", lt)
    ta = since(ev, "aparece", lt)
    estado = "dentro"
    if ta >= 0 or (tc >= 0 and te < 0):
        estado = "otro"
    if te >= 0 and ta < 0:
        estado = "desaparece"
    if estado == "dentro":
        sujeto(ctx, 560, 600, 70, pose=pose)
        if td >= 0:
            yy = 860 - ((lt * 400) % 380)
            line(ctx, [(460, yy), (660, yy)], 8, hexc("#9fffd9"))
    elif estado == "desaparece":
        particulas(ctx, 560, 750, clamp(te / 0.8), "tp1")
    else:
        sujeto(ctx, 1360, 600, 70, expr="sonrisa", pose=pose)
        if ta >= 0 and ta < 0.8:
            particulas(ctx, 1360, 750, 1 - clamp(ta / 0.8), "tp2", (0.8, 0.6, 1))


def sc_copia(ctx, pose, lt, ev):
    laboratorio(ctx, "#cfd8e3")
    cabina(ctx, 460, 860, 1.1)
    cabina(ctx, 1460, 860, 1.1, col="#7b4dff")
    td = since(ev, "destruido", lt)
    if td >= 0:
        fantasma_silueta(ctx, 460, 510, 0.75, alpha=max(0.1, 1 - td / 1.5))
        stamp(ctx, 460, 300, "ORIGINAL", td, 40, col=ROJO, ang=-6)
        stamp(ctx, 1460, 300, "COPIA", td - 0.4, 40, col=MORADO, ang=6)
    sujeto(ctx, 1460, 560, 70, expr="sonrisa", pose=pose)
    cientifico(ctx, 860, 500, 70, expr="preocupado", pose=pose, look=1.0)
    cientifico(ctx, 1060, 500, 70, expr="preocupado", pose=pose + 2, look=-1.0, pelo="#3a2a1e")
    mesa(ctx, 740, 1180, 690)
    tq = since(ev, "pregunta", lt)
    if tq >= 0:
        bob = (pose // 4) % 2 * 10
        draw_text(ctx, "?", CX, 300 - bob, 180, AMAR, INK, 9)


# ─────────────────────────────── bloque 10 · sociedad ───────────────────────────────
def sc_dinero(ctx, pose, lt, ev):
    fondo(ctx, "#2b2340", SUELO, "#1a1428")
    piece(ctx, P_poly([(1080, 300), (1600, 300), (1700, 420), (1600, 540), (1080, 540)]), AMAR, lw=6)
    piece(ctx, P_ell(1630, 420, 18), (1, 1, 1), lw=3)
    txt(ctx, "1.000.000 $", 1360, 440, 70, INK, anchor="center")
    sujeto(ctx, 560, 420, 95, expr="sonrisa", pose=pose, col="#1d1a2e")
    piece(ctx, P_rect(500, 250, 120, 80), INK, lw=3)
    piece(ctx, P_rect(470, 320, 180, 20), INK, lw=3)
    ts = since(ev, "seguros", lt)
    if ts >= 0:
        stamp(ctx, 1360, 700, "SEGURO ×10", ts, 56, col=ROJO, ang=-6)


def sc_soldados(ctx, pose, lt, ev):
    fondo(ctx, "#6b7a5a", SUELO, "#4a5a3a")
    for i in range(6):
        x = 260 + i * 280
        sujeto(ctx, x, 450, 70, expr="neutro", pose=pose if i % 2 else 0, col="#3d5a2f")
        piece(ctx, P_ell(x, 395, 78, 40), hexc("#3d5a2f"), lw=4, shadow=False)
    stamp(ctx, CX, 820, "SUPERFUERZA", lt - 0.6, 56, col=ROJO, ang=-5)


def sc_ilegal(ctx, pose, lt, ev):
    fondo(ctx, "#141223", SUELO, "#0c0a18")
    for x in (0, 1500):
        piece(ctx, P_rect(x, 100, 420, 800), hexc("#2b2340"), lw=4)
    on = (pose // 2) % 3 != 0
    piece(ctx, P_rrect(700, 220, 520, 140, 24), hexc("#ff3cac") if on else hexc("#5a1a40"), lw=6)
    txt(ctx, "LAB 24H", CX, 315, 80, (1, 1, 1) if on else hexc("#c9a0b5"), anchor="center")
    matraz(ctx, 760, 760, 1.0, "#9fff3c", pose)
    matraz(ctx, 1160, 760, 1.0, "#ff8a1f", pose + 3)
    piece(ctx, P_rrect(860, 470, 200, 100, 14), AMAR, lw=4)
    txt(ctx, "-90%", CX, 540, 54, ROJO, anchor="center")
    tp = since(ev, "peligrosos", lt)
    if tp >= 0:
        stamp(ctx, CX, 860, "PELIGRO", tp, 64, col=ROJO, ang=-6)


def sc_registro(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", None)
    piece(ctx, P_rrect(460, 220, 1000, 600, 36), hexc("#f3f1ea"), lw=6, sh=(14, 18))
    piece(ctx, P_rect(460, 220, 1000, 110, ), hexc("#1d4ed8"), lw=0, shadow=False, outline=False)
    txt(ctx, "REGISTRO DE PODERES", CX, 295, 54, (1, 1, 1), anchor="center")
    piece(ctx, P_rect(520, 380, 300, 360), hexc("#bfe3f2"), lw=4, shadow=False)
    ctx.save()
    P_rect(520, 380, 300, 360)(ctx)
    ctx.clip()
    sujeto(ctx, 670, 520, 85, pose=0)
    ctx.restore()
    for i, (a, b) in enumerate((("NOMBRE:", "SUJETO 1"), ("PODER:", "SUPERFUERZA"), ("RIESGO:", "ALTO"))):
        txt(ctx, a, 880, 440 + i * 100, 40, hexc("#5b6475"))
        txt(ctx, b, 1100, 440 + i * 100, 40, INK)
    tc = since(ev, "coche", lt)
    if tc >= 0:
        stamp(ctx, 1250, 720, "REGISTRADO", tc, 52, col=ROJO, ang=-10)


# ─────────────────────────────── bloque 11 · final ───────────────────────────────
def sc_balanza(ctx, pose, lt, ev):
    fondo(ctx, "#2d3557", SUELO, "#1d2440")
    tb, tm = since(ev, "bien", lt), since(ev, "mal", lt)
    ang = 0.0
    if tb >= 0:
        ang = -0.18
    if tm >= 0:
        ang = 0.18 * math.sin(lt * 3)
    piece(ctx, P_rect(CX - 20, 380, 40, 500), hexc("#c9a46a"), lw=5)
    piece(ctx, P_poly([(CX - 160, SUELO), (CX + 160, SUELO), (CX, 820)]), hexc("#c9a46a"), lw=5)
    with rot(ctx, CX, 380, ang):
        line(ctx, [(CX - 500, 380), (CX + 500, 380)], 16, hexc("#c9a46a"))
        for d, lab, col in ((-1, "BIEN", VERDE), (1, "MAL", ROJO)):
            x = CX + d * 500
            line(ctx, [(x, 380), (x - 120, 600)], 4, INK)
            line(ctx, [(x, 380), (x + 120, 600)], 4, INK)
            piece(ctx, P_ell(x, 610, 150, 34), col, lw=5)
            txt(ctx, lab, x, 700, 54, col, anchor="center")
    tp = since(ev, "precio", lt)
    if tp >= 0:
        piece(ctx, P_poly([(CX - 140, 200), (CX + 120, 200), (CX + 180, 260), (CX + 120, 320), (CX - 140, 320)]), AMAR, lw=5)
        txt(ctx, "PRECIO", CX - 10, 280, 48, INK, anchor="center")


def sc_eleccion(ctx, pose, lt, ev):
    fondo(ctx, "#1d1a2e", None)
    for i, nom in enumerate(ICONOS):
        r, c = divmod(i, 4)
        x = 330 + c * 420 + (210 if r == 1 else 0)
        y = 360 + r * 360
        piece(ctx, P_rrect(x - 170, y - 150, 340, 300, 30), hexc(COLS[i]), lw=5)
        icono(ctx, nom, x, y - 30, 0.65, pose)
        txt(ctx, NOMBRES[i], x, y + 120, 30, (1, 1, 1), anchor="center")
    te = since(ev, "elegirias", lt)
    if te >= 0:
        i = int(te * 3) % 7
        r, c = divmod(i, 4)
        x = 330 + c * 420 + (210 if r == 1 else 0)
        y = 360 + r * 360
        P_rrect(x - 180, y - 160, 360, 320, 34)(ctx)
        set_col(ctx, AMAR)
        ctx.set_line_width(14)
        ctx.stroke()


SCENES = dict(intro=sc_intro, cola=sc_cola, cuna=sc_cuna, tresvias=sc_tresvias, contrato=sc_contrato,
              freno=sc_freno, vaca=sc_vaca, levanta=sc_levanta, comida=sc_comida, gotas=sc_gotas, noche=sc_noche,
              gafas=sc_gafas, cristal=sc_cristal, ojo=sc_ojo, ciego=sc_ciego, ajolote=sc_ajolote, herida=sc_herida,
              celulas=sc_celulas, implante=sc_implante, dos=sc_dos, calle=sc_calle, boton=sc_boton, huesos=sc_huesos,
              vuela=sc_vuela, caida=sc_caida, maquina=sc_maquina, copia=sc_copia, dinero=sc_dinero,
              soldados=sc_soldados, ilegal=sc_ilegal, registro=sc_registro, balanza=sc_balanza, eleccion=sc_eleccion)
for _n in range(7):
    SCENES[f"t{_n + 1}"] = hacer_titulo(_n)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    sc_intro(ctx, 0, 3.0, {"experimento_lt": 0.5, "bien_lt": 1.0, "mal_lt": 1.2})
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(131))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "¿SUPERPODERES", CX, 170, 130, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "CON EXPERIMENTOS?", CX, 340, 120, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "UNOS SALEN BIEN… OTROS FATAL", CX, 930, 84, hexc("#ffe14d"), INK, math.radians(-2), 1.0)
    surf.write_to_png(path)


def configurar():
    g.W, g.H = W, H
    g.MAX_DUR = 600.0
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
