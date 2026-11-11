#!/usr/bin/env python3
"""
Short 11 · «Robaron un banco con armas de juguete… y huyeron en bote» — Banco Río de Acassuso (2006)
Guion escrito con la skill (references/guiones.md). Voz Salva (eleven_v4).

Uso:
    python short_robo_siglo.py            # vídeo final (usa cache_audio/robo-del-siglo/)
    python short_robo_siglo.py --prueba   # sin voz, tiempos aproximados
"""
import math
import os

import cairo

import generar_short as g
from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io,
                           ease_out_back, hexc, hnoise, lerp, line, piece, rot, set_col, silhouette)
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier
from short_museo import guardia

SLUG = "robo-del-siglo"

BLOQUES = [
    dict(
        id="gancho",
        voz="¿Qué pasaría si unos ladrones asaltaran un banco con armas de juguete… y escaparan en bote?",
        escenas=[(None, "juguete"), ("y escaparan", "bote")],
        pantalla=[("armas de", "¿ARMAS DE JUGUETE?"), ("en bote", "¿Y EN BOTE?")],
        eventos={"armas": "armas de", "bote": "en bote"},
    ),
    dict(
        id="caso",
        voz=("Buenos Aires, enero de 2006. Una banda entra en el Banco Río de Acassuso con pistolas de juguete "
             "y retiene a 23 personas. Nadie sale herido."),
        escenas=[(None, "banco")],
        pantalla=[(None, "BUENOS AIRES, 2006"), ("retiene a", "23 REHENES"), ("Nadie sale", "0 HERIDOS")],
        eventos={"entra": "Una banda", "juguete": "pistolas de", "retiene": "retiene a", "nadie": "Nadie sale"},
    ),
    dict(
        id="truco",
        voz=("Uno de ellos negocia por teléfono con la policía durante horas. Mientras tanto, los demás vacían "
             "más de 140 cajas de seguridad y bajan a un túnel que habían cavado hasta el desagüe."),
        escenas=[(None, "partida"), ("y bajan", "tunel")],
        pantalla=[(None, "HORAS AL TELÉFONO"), ("vacían más", "+140 CAJAS"), ("y bajan", "UN TÚNEL…")],
        eventos={"mientras": "Mientras tanto", "vacian": "vacían más", "desague": "hasta el desagüe"},
    ),
    dict(
        id="nota",
        voz=("Cuando la policía entra, solo encuentra una nota: \"En barrio de ricachones, sin armas ni rencores, "
             "es solo plata y no amores\". Botín: unos 19 millones de dólares."),
        escenas=[(None, "camara"), ("una nota", "nota"), ("Botín", "huida")],
        pantalla=[(None, "LA POLICÍA ENTRA…"), ("una nota", "LA NOTA"), ("Botín", "19 MILLONES DE DÓLARES")],
        eventos={"nota": "una nota", "rencores": "sin armas", "amores": "no amores", "botin": "Botín"},
    ),
    dict(
        id="cierre",
        voz=("Acabaron detenidos, pero casi todo el dinero sigue sin aparecer. Mientras todos miraban la "
             "negociación, nadie miraba el suelo. ¿Tú lo habrías visto?"),
        escenas=[(None, "detenidos"), ("pero casi", "vacio"), ("Mientras todos", "suelo")],
        pantalla=[(None, "DETENIDOS"), ("pero casi", "¿Y EL DINERO?"), ("Tú lo", "¿LO HABRÍAS VISTO?")],
        eventos={"detenidos": "Acabaron", "suelo": "nadie miraba", "pregunta": "Tú lo"},
    ),
]

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")
TIERRA, TIERRA2 = hexc("#8a5a34"), hexc("#6b4428")
AGUA = hexc("#3f7fa8")


# ─────────────────────────────── piezas ───────────────────────────────
def fondo_noche(ctx, suelo=1300):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, suelo, 1100, 1960 - suelo), hexc("#1d2440"), lw=4, shadow=False)


def pistola_juguete(ctx, x, y, s=1.0, bang=0.0):
    """Pistola de juguete de colores con banderín «BANG!» (nada realista)."""
    if bang > 0:
        k = ease_out_back(clamp(bang / 0.3)) if bang < 0.3 else 1.0
        line(ctx, [(x + 250 * s, y - 40 * s), (x + (250 + 140 * k) * s, y - 40 * s)], 6 * s, INK)
        fw, fh = 260 * s * k, 110 * s * k
        if k > 0.05:
            piece(ctx, P_rect(x + (390 * s if k >= 1 else (250 + 140 * k) * s), y - 40 * s - fh / 2, fw, fh),
                  (1, 1, 1), lw=4)
            if k > 0.6:
                draw_text(ctx, "BANG!", x + (390 * s) + fw / 2, y - 40 * s, 62 * s * k, hexc("#e63946"), INK, 0)
    # cañón y cuerpo
    piece(ctx, P_rrect(x - 40 * s, y - 80 * s, 300 * s, 80 * s, 20 * s), hexc("#ff8a1f"), lw=5)
    piece(ctx, P_rect(x + 240 * s, y - 70 * s, 26 * s, 60 * s), hexc("#ffe14d"), lw=4, shadow=False)
    piece(ctx, P_poly([(x - 30 * s, y - 10 * s), (x + 70 * s, y - 10 * s), (x + 40 * s, y + 150 * s),
                       (x - 70 * s, y + 150 * s)]), hexc("#2fb35a"), lw=5)
    ctx.new_sub_path()
    ctx.arc(x + 95 * s, y + 15 * s, 34 * s, 0, math.pi)
    set_col(ctx, INK)
    ctx.set_line_width(7 * s)
    ctx.stroke()
    for k in range(3):
        piece(ctx, P_ell(x + 20 * s + k * 70 * s, y - 40 * s, 14 * s), hexc("#ffe14d"), lw=3, shadow=False)


def bote(ctx, x, y, s, pose, sacos=3, gente=2):
    """Bote hinchable con siluetas y sacos."""
    for i in range(gente):
        silhouette(ctx, x - 70 * s + i * 120 * s, y - 10 * s, 0.45 * s, math.radians(4 if (pose + i) % 4 < 2 else -4),
                   SOMBRA, BORDE)
    for i in range(sacos):
        saco(ctx, x + 150 * s + i * 60 * s, y - 40 * s, 0.38 * s)
    piece(ctx, P_rrect(x - 200 * s, y - 40 * s, 460 * s, 90 * s, 45 * s), hexc("#ff8a1f"), lw=5)
    line(ctx, [(x - 160 * s, y + 5 * s), (x + 220 * s, y + 5 * s)], 5 * s, hexc("#c75f0f"))
    a = math.radians(-25 if pose % 4 < 2 else 15)
    with rot(ctx, x + 20 * s, y - 40 * s, a):
        line(ctx, [(x + 20 * s, y - 70 * s), (x - 40 * s, y + 70 * s)], 9 * s, hexc("#7a4e2c"))
        piece(ctx, P_ell(x - 45 * s, y + 80 * s, 16 * s, 30 * s), hexc("#7a4e2c"), lw=3, shadow=False)


def saco(ctx, x, y, s=1.0, label="$"):
    piece(ctx, P_poly([(x - 70 * s, y + 80 * s), (x + 70 * s, y + 80 * s), (x + 85 * s, y - 20 * s), (x + 40 * s, y - 70 * s),
                       (x - 40 * s, y - 70 * s), (x - 85 * s, y - 20 * s)]), hexc("#c9a46a"), lw=4)
    line(ctx, [(x - 40 * s, y - 62 * s), (x + 40 * s, y - 62 * s)], 7 * s, hexc("#6b4428"))
    draw_text(ctx, label, x, y + 15 * s, 60 * s, hexc("#2f6b45"), INK, 0)


def olas(ctx, y, pose, col=AGUA, x0=-20, x1=1100):
    off = (pose % 6) * 12
    ctx.move_to(x0, y)
    x = x0 - off
    while x < x1:
        ctx.curve_to(x + 30, y - 18, x + 60, y - 18, x + 90, y)
        x += 90
    ctx.line_to(x1, y + 400)
    ctx.line_to(x0, y + 400)
    ctx.close_path()
    set_col(ctx, col)
    ctx.fill_preserve()
    set_col(ctx, INK)
    ctx.set_line_width(4)
    ctx.stroke()


def banco(ctx, x, y, w, h, pose=0, cartel="BANCO"):
    piece(ctx, P_rect(x, y, w, h), hexc("#e3e6ec"), lw=5)
    piece(ctx, P_rect(x - 20, y - 60, w + 40, 70), hexc("#c8202f"), lw=5)
    draw_text(ctx, cartel, x + w / 2, y - 25, 50, (1, 1, 1), INK, 0)
    for k in range(3):
        piece(ctx, P_rect(x + 40 + k * (w - 80) / 3, y + 50, (w - 80) / 3 - 30, 150), hexc("#bfe3f2"), lw=4,
              shadow=False)
        # persianas bajadas
        for j in range(5):
            line(ctx, [(x + 42 + k * (w - 80) / 3, y + 60 + j * 26), (x + 40 + (k + 1) * (w - 80) / 3 - 32,
                                                                       y + 60 + j * 26)], 4, hexc("#8ea4b8"))
    piece(ctx, P_rect(x + w / 2 - 70, y + h - 220, 140, 220), hexc("#5b6475"), lw=5)


def patrulla(ctx, x, y, pose, flip=False):
    """Coche de policía genérico con sirena que parpadea."""
    s = -1 if flip else 1
    piece(ctx, P_rrect(x - 170, y - 70, 340, 90, 24), (1, 1, 1), lw=5)
    piece(ctx, P_poly([(x - 100, y - 70), (x + 90, y - 70), (x + 60, y - 140), (x - 70, y - 140)]), (1, 1, 1), lw=5)
    piece(ctx, P_rect(x - 170, y - 40, 340, 26), hexc("#1d4ed8"), lw=3, shadow=False)
    piece(ctx, P_poly([(x - 85, y - 76), (x - 8, y - 76), (x - 8, y - 132), (x - 60, y - 132)]), hexc("#bfe3f2"), lw=3,
          shadow=False)
    piece(ctx, P_poly([(x + 8, y - 76), (x + 78, y - 76), (x + 52, y - 132), (x + 8, y - 132)]), hexc("#bfe3f2"), lw=3,
          shadow=False)
    on = (pose // 3) % 2 == 0
    piece(ctx, P_rrect(x - 50, y - 166, 50, 28, 6), hexc("#e63946") if on else hexc("#6b1d24"), lw=3, shadow=False)
    piece(ctx, P_rrect(x, y - 166, 50, 28, 6), hexc("#1d4ed8") if not on else hexc("#16255e"), lw=3, shadow=False)
    if on:
        burst_light(ctx, x - 25 + 0 * s, y - 152, hexc("#e63946"))
    else:
        burst_light(ctx, x + 25, y - 152, hexc("#4f7cff"))
    for wx in (x - 105, x + 105):
        piece(ctx, P_ell(wx, y + 22, 40), INK, lw=3, shadow=False)
        piece(ctx, P_ell(wx, y + 22, 16), hexc("#9aa0ab"), lw=2, shadow=False)


def burst_light(ctx, x, y, col):
    ctx.save()
    ctx.set_source_rgba(col[0], col[1], col[2], 0.28)
    ctx.arc(x, y, 90, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def caja_seg(ctx, x, y, w, h, abierta=0.0):
    piece(ctx, P_rect(x, y, w, h), hexc("#b9bfca"), lw=3, shadow=False)
    if abierta <= 0:
        piece(ctx, P_ell(x + w / 2, y + h / 2, 7), hexc("#5b6475"), lw=2, shadow=False)
        return
    piece(ctx, P_rect(x + 4, y + 4, w - 8, h - 8), hexc("#22252e"), lw=2, shadow=False)
    # puerta abierta hacia la izquierda
    piece(ctx, P_poly([(x, y), (x - w * 0.35, y + 8), (x - w * 0.35, y + h - 8), (x, y + h)]), hexc("#d7dce4"),
          lw=2, shadow=False)


def pared_cajas(ctx, x, y, cols, rows, w, h, n_abiertas):
    piece(ctx, P_rect(x - 14, y - 14, cols * w + 28, rows * h + 28), hexc("#5b6475"), lw=5)
    orden = sorted(range(cols * rows), key=lambda i: hnoise("cajas", i))
    abiertas = set(orden[:n_abiertas])
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        caja_seg(ctx, x + c * w, y + r * h, w - 6, h - 6, 1.0 if i in abiertas else 0.0)


def reloj(ctx, cx, cy, r, horas):
    piece(ctx, P_ell(cx, cy, r), (1, 1, 1), lw=6)
    for k in range(12):
        a = k * math.pi / 6
        line(ctx, [(cx + (r - 18) * math.sin(a), cy - (r - 18) * math.cos(a)),
                   (cx + (r - 6) * math.sin(a), cy - (r - 6) * math.cos(a))], 4, INK)
    a_h = horas * math.pi / 6
    a_m = horas * 2 * math.pi
    line(ctx, [(cx, cy), (cx + r * 0.5 * math.sin(a_h), cy - r * 0.5 * math.cos(a_h))], 9, INK)
    line(ctx, [(cx, cy), (cx + r * 0.78 * math.sin(a_m), cy - r * 0.78 * math.cos(a_m))], 6, hexc("#e63946"))
    piece(ctx, P_ell(cx, cy, 9), INK, lw=0, shadow=False, outline=False)


def negociador(ctx, x, feet, s, pose):
    """Silueta sin rasgos con un teléfono pegado a la oreja; el brazo va doblado, no levantado."""
    silhouette(ctx, x, feet, s, math.radians(5 if pose % 6 < 3 else -3), SOMBRA, BORDE)
    hy = feet - 230 * s - 72 * s * 0.9
    line(ctx, [(x + 50 * s, feet - 200 * s), (x + 110 * s, feet - 120 * s), (x + 70 * s, hy + 20 * s)], 18 * s, SOMBRA)
    piece(ctx, P_rrect(x + 40 * s, hy - 40 * s, 40 * s, 90 * s, 14 * s), hexc("#e63946"), lw=4, shadow=False)
    if (pose // 2) % 2 == 0:
        for k in range(3):
            ctx.new_sub_path()
            ctx.arc(x + 70 * s, hy, (70 + k * 26) * s, math.radians(-40), math.radians(20))
            set_col(ctx, hexc("#ffe14d"))
            ctx.set_line_width(6)
            ctx.stroke()


def corte_base(ctx, suelo):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, suelo, 1100, 1960 - suelo), TIERRA, lw=4, shadow=False)
    for i in range(40):
        x = hnoise("pied", i) * 1080
        y = suelo + 40 + hnoise("pied", i, "y") * (1500 - suelo)
        piece(ctx, P_ell(x, y, 10 + hnoise("pied", i, "r") * 14, 8 + hnoise("pied", i, "r") * 10), TIERRA2, lw=2,
              shadow=False)
    piece(ctx, P_rect(-10, suelo - 16, 1100, 24), hexc("#6b6f78"), lw=4, shadow=False)


# ─────────────────────────────── escenas ───────────────────────────────
def sc_juguete(ctx, pose, lt, ev):
    fondo_noche(ctx)
    ta = since(ev, "armas", lt)
    k = 1.0 if ta < 0 else 1.0
    wob = math.radians(-6 if pose % 4 < 2 else -2)
    with rot(ctx, 420, 920, wob):
        pistola_juguete(ctx, 170, 900, 1.15 * k, bang=ta if ta >= 0 else 0.0)
    if ta >= 0:
        stamp(ctx, 540, 1250, "DE JUGUETE", ta - 0.5, 60, col=hexc("#2fb35a"), ang=-6)


def sc_bote(ctx, pose, lt, ev):
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    olas(ctx, 1150, pose)
    x = lerp(-250, 560, ease_io(clamp(lt / 1.2)))
    bote(ctx, x, 1150 - 10, 1.1, pose)


def sc_banco(ctx, pose, lt, ev):
    fondo_noche(ctx, 1250)
    banco(ctx, 190, 700, 700, 560, pose)
    for i in range(3):
        patrulla(ctx, 180 + i * 360, 1350 + (i % 2) * 25, pose + i)
    tj = since(ev, "juguete", lt)
    if tj >= 0:
        with rot(ctx, 540, 640, 0):
            pass
        stamp(ctx, 540, 770, "¡DE JUGUETE!", tj, 54, col=hexc("#2fb35a"), ang=-4)
    tr = since(ev, "retiene", lt)
    if tr >= 0:
        stamp(ctx, 540, 940, "23 DENTRO", tr, 58, col=hexc("#e23b3b"), ang=-8)
    tn = since(ev, "nadie", lt)
    if tn >= 0:
        stamp(ctx, 540, 1090, "0 HERIDOS", tn, 58, col=hexc("#2f6b45"), ang=6)


def sc_partida(ctx, pose, lt, ev):
    # arriba: negociador al teléfono + reloj
    set_col(ctx, hexc("#2d3557"))
    ctx.paint()
    piece(ctx, P_rect(-10, 500, 1100, 470), hexc("#3a4170"), lw=4, shadow=False)
    negociador(ctx, 300, 960, 1.05, pose)
    horas = 10 + lt * 0.9
    reloj(ctx, 780, 720, 140, horas)
    # separador
    piece(ctx, P_rect(-10, 970, 1100, 18), hexc("#ffe14d"), lw=4, shadow=False)
    # abajo: pared de cajas de seguridad
    piece(ctx, P_rect(-10, 988, 1100, 500), hexc("#262b45"), lw=0, shadow=False, outline=False)
    tv = since(ev, "vacian", lt)
    tm = since(ev, "mientras", lt)
    n = 0
    if tm >= 0:
        n = 3
    if tv >= 0:
        n = 3 + int(37 * clamp(tv / 2.2))
    pared_cajas(ctx, 70, 1020, 10, 4, 94, 100, n)


def sc_tunel(ctx, pose, lt, ev):
    suelo = 860
    corte_base(ctx, suelo)
    banco(ctx, 80, suelo - 330, 440, 330, cartel="BANCO")
    # bóveda bajo el banco
    piece(ctx, P_rect(100, suelo + 20, 400, 220), hexc("#5b6475"), lw=6)
    pared_cajas(ctx, 130, suelo + 50, 6, 2, 60, 70, 12)
    # desagüe pluvial (gran tubo en corte)
    ty = 1300
    piece(ctx, P_rect(-10, ty - 90, 1100, 180), hexc("#9aa0ab"), lw=5, shadow=False)
    piece(ctx, P_rect(-10, ty - 70, 1100, 140), hexc("#4a4f5c"), lw=3, shadow=False)
    ctx.save()
    P_rect(-10, ty - 70, 1100, 140)(ctx)
    ctx.clip()
    olas(ctx, ty + 30, pose, AGUA)
    ctx.restore()
    txt(ctx, "DESAGÜE", 820, ty - 110, 40, (1, 1, 1), anchor="center")
    # túnel que baja de la bóveda al desagüe
    p = ease_io(clamp(lt / 1.4))
    yb = lerp(suelo + 240, ty - 70, p)
    piece(ctx, P_rect(400, suelo + 240, 90, yb - suelo - 240 + 2), hexc("#2a1a10"), lw=3, shadow=False)
    for yy in range(int(suelo + 270), int(yb), 70):
        line(ctx, [(400, yy), (490, yy)], 6, hexc("#c9a46a"))
    # figura bajando con un saco
    fy = lerp(suelo + 300, ty - 80, ease_io(clamp((lt - 0.4) / 1.6)))
    silhouette(ctx, 445, fy + 50, 0.32, 0.0, SOMBRA, BORDE)
    td = since(ev, "desague", lt)
    if td >= 0:
        x = lerp(560, 760, ease_io(clamp(td / 1.0)))
        bote(ctx, x, ty + 20, 0.5, pose, sacos=2, gente=1)


def sc_camara(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3a3f55"))
    ctx.paint()
    piece(ctx, P_rect(-10, 1320, 1100, 640), hexc("#262a3a"), lw=4, shadow=False)
    pared_cajas(ctx, 90, 560, 10, 6, 92, 92, 60)
    # papeles por el suelo
    for i in range(8):
        x = 120 + hnoise("pap", i) * 840
        with rot(ctx, x, 1330, math.radians((hnoise("pap", i, "a") - 0.5) * 60)):
            piece(ctx, P_rect(x - 30, 1320, 60, 40), (1, 1, 1), lw=2, shadow=False)
    # policías entran desde la izquierda
    x = lerp(-200, 250, ease_io(clamp(lt / 0.8)))
    guardia(ctx, x, 1010, r=70, pose=pose, linterna=True, expr="preocupado" if lt > 0.9 else "neutro")
    x2 = lerp(-400, 100, ease_io(clamp((lt - 0.3) / 0.8)))
    if x2 > -300:
        guardia(ctx, x2, 1050, r=62, pose=pose + 2, expr="preocupado" if lt > 1.2 else "neutro")
    if lt > 1.0:
        stamp(ctx, 700, 1240, "¡VACÍA!", lt - 1.0, 60, col=hexc("#e23b3b"), ang=-6)


def sc_nota(ctx, pose, lt, ev):
    set_col(ctx, hexc("#3a3f55"))
    ctx.paint()
    k = ease_out_back(clamp(lt / 0.35)) if lt < 0.35 else 1.0
    ang = math.radians(-3 + (1 if pose % 6 < 3 else 0))
    with rot(ctx, 540, 960, ang):
        ctx.save()
        ctx.translate(540, 960)
        ctx.scale(max(0.05, k), max(0.05, k))
        ctx.translate(-540, -960)
        piece(ctx, P_rect(150, 560, 780, 780), hexc("#fbf6e8"), lw=6, sh=(14, 18))
        for j in range(9):
            line(ctx, [(190, 650 + j * 75), (890, 650 + j * 75)], 2, hexc("#9cc3e0"))
        lineas = ["En barrio de", "ricachones,", "sin armas ni", "rencores,", "es solo plata", "y no amores"]
        tr = since(ev, "rencores", lt)
        ta = since(ev, "amores", lt)
        vis = 2 + (2 if tr >= 0 else 0) + (2 if ta >= 0 else 0)
        for i, s in enumerate(lineas[:vis]):
            txt(ctx, s, 540, 690 + i * 105, 64, hexc("#1d3a8a"), font="Caveat" if False else g.FONT, anchor="center")
        ctx.restore()


def sc_huida(ctx, pose, lt, ev):
    set_col(ctx, hexc("#4a4f5c"))
    ctx.paint()
    # interior del túnel pluvial
    piece(ctx, P_rect(-10, 500, 1100, 70), hexc("#9aa0ab"), lw=4, shadow=False)
    for i in range(7):
        x = (i * 180 - (pose * 10) % 180)
        line(ctx, [(x, 570), (x, 1180)], 4, hexc("#3a3f4a"))
    olas(ctx, 1180, pose)
    x = lerp(-100, 560, ease_io(clamp(lt / 1.0)))
    bote(ctx, x, 1170, 1.0, pose, sacos=4, gente=2)
    # billetes volando
    for i in range(6):
        bx = (hnoise("bil", i) * 1080 + lt * 120) % 1100
        by = 700 + hnoise("bil", i, "y") * 300 + (pose % 4) * 6
        with rot(ctx, bx, by, math.radians((hnoise("bil", i, "a") - 0.5) * 60)):
            piece(ctx, P_rect(bx - 50, by - 20, 100, 40), hexc("#9fd6a0"), lw=3, shadow=False)


def sc_detenidos(ctx, pose, lt, ev):
    fondo_noche(ctx)
    for i in range(6):
        r, c = divmod(i, 3)
        x, feet = 220 + c * 320, 1010 + r * 330
        silhouette(ctx, x, feet, 0.72, 0.0, SOMBRA, BORDE)
        stamp(ctx, x, feet - 120, "DETENIDO", lt - i * 0.12, 36, col=hexc("#e23b3b"), ang=-8 + (i % 3) * 6)


def sc_vacio(ctx, pose, lt, ev):
    fondo_noche(ctx)
    piece(ctx, P_poly([(380, 1300), (700, 1300), (760, 1060), (640, 960), (440, 960), (320, 1060)]), hexc("#c9a46a"), lw=6)
    piece(ctx, P_ell(540, 970, 110, 30), hexc("#3a2418"), lw=4, shadow=False)
    bob = (pose // 4) % 2 * 12
    draw_text(ctx, "?", 540, 740 - bob, 300, hexc("#ffe14d"), INK, 9)
    piece(ctx, P_rrect(200, 1170, 680, 100, 14), hexc("#1d2433"), lw=4)
    txt(ctx, "RECUPERADO: ~1 MILLÓN", 540, 1238, 50, hexc("#ff6b6b"), anchor="center")


def sc_suelo(ctx, pose, lt, ev):
    suelo = 1080
    corte_base(ctx, suelo)
    banco(ctx, 300, suelo - 420, 480, 420)
    patrulla(ctx, 140, suelo - 30, pose)
    patrulla(ctx, 940, suelo - 30, pose + 1)
    # túnel oculto bajo el suelo
    piece(ctx, P_rect(500, suelo + 10, 80, 260), hexc("#2a1a10"), lw=3, shadow=False)
    piece(ctx, P_rect(500, suelo + 220, 600, 70), hexc("#2a1a10"), lw=3, shadow=False)
    ts = since(ev, "suelo", lt)
    if ts >= 0:
        k = ease_io(clamp(ts / 0.7))
        magnifier(ctx, lerp(980, 640, k), lerp(1500, 1250, k), 120, math.radians(-30))


SCENES = dict(juguete=sc_juguete, bote=sc_bote, banco=sc_banco, partida=sc_partida, tunel=sc_tunel,
              camara=sc_camara, nota=sc_nota, huida=sc_huida, detenidos=sc_detenidos, vacio=sc_vacio,
              suelo=sc_suelo)


def miniatura(path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
    ctx = cairo.Context(surf)
    sc_huida(ctx, 0, 3.0, {})
    with rot(ctx, 420, 1420, math.radians(-8)):
        pistola_juguete(ctx, 180, 1400, 0.8, bang=1.0)
    ctx.set_operator(cairo.OPERATOR_OVERLAY)
    ctx.set_source_surface(g.make_paper_texture(37))
    ctx.paint_with_alpha(0.42)
    ctx.set_operator(cairo.OPERATOR_OVER)
    card_text(ctx, "ARMAS DE JUGUETE", 540, 220, 104, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
    card_text(ctx, "Y HUIDA EN BOTE", 540, 380, 104, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
    card_text(ctx, "¡19 MILLONES!", 540, 1720, 120, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
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
