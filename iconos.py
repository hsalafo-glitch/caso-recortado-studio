"""Biblioteca de dibujos de papel para shorts de cualquier tema.

    dibujar(ctx, nombre, x, y, s, pose)   # (x, y) = centro; s = escala (1 ≈ 300 px de alto)
    CATEGORIAS                             # {categoría: [nombres]}  → lo usa el guionista

Mismo estilo que el motor: colores planos, contorno negro fino, sombra mínima y movimiento
a saltos con `pose` (12 poses/s). Nada de personas reales ni marcas.
"""
import math

from generar_short import INK, P_ell, P_poly, P_rect, P_rrect, hexc, line, piece, set_col

C = {k: hexc(v) for k, v in dict(
    rojo="#e63946", naranja="#f08a24", amarillo="#ffd23f", verde="#2fb35a", verdeo="#1f7a3e", azul="#2f6fd6",
    celeste="#7fc8f8", morado="#7b4dff", rosa="#ff8fb1", marron="#8a5a35", marronc="#c08a5a", gris="#9aa3b5",
    grisc="#d9dee8", blanco="#f7f4ea", piel="#f2c9a0", oro="#f2b632", negro="#1d1f29", carne="#d9534f").items()}


def _estrella(cx, cy, r1, r2, n=5, giro=-math.pi / 2):
    return [(cx + (r1 if i % 2 == 0 else r2) * math.cos(giro + i * math.pi / n),
             cy + (r1 if i % 2 == 0 else r2) * math.sin(giro + i * math.pi / n)) for i in range(2 * n)]


def _circ(cx, cy, r, n=24, a0=0, a1=2 * math.pi):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + r * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def _ojo(ctx, x, y, s, r=14):
    piece(ctx, P_ell(x, y, r * s * 0.8, r * s), C["blanco"], lw=3, shadow=False)
    piece(ctx, P_ell(x + 2 * s, y + 2 * s, r * s * 0.4, r * s * 0.5), INK, lw=0, shadow=False, outline=False)


def _cara(ctx, x, y, s, feliz=True):
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 35 * s, y - 25 * s, 11 * s, 15 * s), INK, lw=0, shadow=False, outline=False)
    if feliz:
        line(ctx, _circ(x, y + 5 * s, 50 * s, 12, 0.2 * math.pi, 0.8 * math.pi), 8 * s)
    else:
        line(ctx, _circ(x, y + 75 * s, 45 * s, 12, 1.2 * math.pi, 1.8 * math.pi), 8 * s)


# ───────────────────────────── naturaleza ─────────────────────────────
def sol(ctx, x, y, s, p):
    g = math.radians(8 if p % 4 < 2 else 0)
    for i in range(10):
        a = g + i * math.pi / 5
        piece(ctx, P_poly([(x + 105 * s * math.cos(a - 0.15), y + 105 * s * math.sin(a - 0.15)),
                           (x + 165 * s * math.cos(a), y + 165 * s * math.sin(a)),
                           (x + 105 * s * math.cos(a + 0.15), y + 105 * s * math.sin(a + 0.15))]), C["naranja"], lw=3)
    piece(ctx, P_ell(x, y, 105 * s), C["amarillo"], lw=5)
    _cara(ctx, x, y + 5 * s, 0.9 * s)


def luna(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 140 * s), C["grisc"], lw=5)
    for cx, cy, r in ((-50, -50, 28), (55, -20, 20), (-20, 60, 34), (70, 75, 14), (-85, 20, 12)):
        piece(ctx, P_ell(x + cx * s, y + cy * s, r * s), C["gris"], lw=3, shadow=False)
    if p % 6 < 3:
        piece(ctx, P_poly(_estrella(x + 150 * s, y - 130 * s, 26 * s, 10 * s)), C["amarillo"], lw=3, shadow=False)


def estrella(ctx, x, y, s, p):
    r = 1.0 if p % 4 < 2 else 0.93
    piece(ctx, P_poly(_estrella(x, y, 150 * s * r, 62 * s * r)), C["amarillo"], lw=5)


def planeta(ctx, x, y, s, p):
    ctx.save(); ctx.new_path(); ctx.translate(x, y); ctx.rotate(-0.25); ctx.scale(1, 0.3)
    ctx.arc(0, 0, 200 * s, math.pi, 2 * math.pi); set_col(ctx, INK); ctx.set_line_width(36 * s); ctx.stroke()
    ctx.arc(0, 0, 200 * s, math.pi, 2 * math.pi); set_col(ctx, C["oro"]); ctx.set_line_width(26 * s); ctx.stroke()
    ctx.restore()
    piece(ctx, P_ell(x, y, 115 * s), C["morado"], lw=5)
    for k in (-40, 15):
        line(ctx, [(x - 95 * s, y + k * s), (x + 95 * s, y + (k - 25) * s)], 10 * s, hexc("#9b78ff"))
    ctx.save(); ctx.new_path(); ctx.translate(x, y); ctx.rotate(-0.25); ctx.scale(1, 0.3)
    ctx.arc(0, 0, 200 * s, 0, math.pi); set_col(ctx, INK); ctx.set_line_width(36 * s); ctx.stroke()
    ctx.arc(0, 0, 200 * s, 0, math.pi); set_col(ctx, C["oro"]); ctx.set_line_width(26 * s); ctx.stroke()
    ctx.restore()


def tierra(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 140 * s), C["azul"], lw=5)
    d = 12 * s if p % 6 < 3 else 0
    ctx.save(); ctx.new_path(); ctx.arc(x, y, 138 * s, 0, 2 * math.pi); ctx.clip()
    for pts in ([(-90, -80), (-20, -110), (10, -60), (-30, -10), (-80, 10), (-110, -30)],
                [(20, 10), (90, -20), (120, 40), (70, 110), (30, 80)], [(-70, 70), (-30, 60), (-40, 110)]):
        piece(ctx, P_poly([(x + a * s + d, y + b * s) for a, b in pts]), C["verde"], lw=3, shadow=False)
    ctx.restore()


def nube(ctx, x, y, s, p):
    for cx, cy, r in ((-80, 20, 70), (0, -20, 95), (85, 15, 70)):
        piece(ctx, P_ell(x + cx * s, y + cy * s, r * s), C["blanco"], lw=5, shadow=False)
    piece(ctx, P_rrect(x - 150 * s, y + 10 * s, 300 * s, 80 * s, 40 * s), C["blanco"], lw=0, shadow=False, outline=False)
    line(ctx, [(x - 140 * s, y + 90 * s), (x + 140 * s, y + 90 * s)], 5 * s)


def lluvia(ctx, x, y, s, p):
    o = 25 * s if p % 4 < 2 else 0
    for i, dx in enumerate((-90, -30, 30, 90)):
        yy = y + (100 + (o if i % 2 else 25 * s - o) / s) * s
        piece(ctx, P_poly([(x + dx * s, yy), (x + (dx - 12) * s, yy + 35 * s), (x + (dx + 12) * s, yy + 35 * s)]), C["celeste"], lw=3, shadow=False)
    nube(ctx, x, y - 40 * s, s, p)


def rayo(ctx, x, y, s, p):
    piece(ctx, P_poly([(x + 30 * s, y - 170 * s), (x - 80 * s, y + 20 * s), (x - 5 * s, y + 20 * s), (x - 40 * s, y + 170 * s),
                       (x + 90 * s, y - 30 * s), (x + 10 * s, y - 30 * s), (x + 60 * s, y - 170 * s)]),
          C["amarillo"] if p % 4 < 2 else C["blanco"], lw=5)


def fuego(ctx, x, y, s, p):
    k = 1.0 if p % 4 < 2 else 0.9
    piece(ctx, P_poly([(x - 110 * s, y + 80 * s), (x - 100 * s, y - 40 * s), (x - 50 * s, y + 10 * s), (x - 30 * s, y - 160 * s * k),
                       (x + 40 * s, y - 60 * s), (x + 70 * s, y - 120 * s * k), (x + 110 * s, y + 80 * s), (x, y + 140 * s)]), C["naranja"], lw=5)
    piece(ctx, P_poly([(x - 55 * s, y + 90 * s), (x - 30 * s, y - 20 * s), (x, y + 30 * s), (x + 25 * s, y - 50 * s * k),
                       (x + 55 * s, y + 90 * s), (x, y + 120 * s)]), C["amarillo"], lw=3, shadow=False)


def gota(ctx, x, y, s, p):
    pts = [(x, y - 160 * s)] + _circ(x, y + 50 * s, 100 * s, 30, -0.2 * math.pi, 1.2 * math.pi)
    piece(ctx, P_poly(pts), C["celeste"], lw=5)
    piece(ctx, P_ell(x - 40 * s, y + 40 * s, 15 * s, 30 * s), C["blanco"], lw=0, shadow=False, outline=False)


def arbol(ctx, x, y, s, p):
    piece(ctx, P_rect(x - 25 * s, y + 20 * s, 50 * s, 150 * s), C["marron"], lw=4)
    d = 6 * s if p % 6 < 3 else -6 * s
    for cx, cy, r in ((-70, -10, 80), (70, -10, 80), (0, -90, 95), (0, 20, 85)):
        piece(ctx, P_ell(x + cx * s + d, y + cy * s, r * s), C["verde"], lw=4, shadow=False)


def flor(ctx, x, y, s, p):
    line(ctx, [(x, y), (x, y + 170 * s)], 14 * s, C["verdeo"])
    piece(ctx, P_ell(x + 45 * s, y + 110 * s, 45 * s, 20 * s), C["verde"], lw=3, shadow=False)
    g = 0.3 if p % 4 < 2 else 0
    for i in range(6):
        a = g + i * math.pi / 3
        piece(ctx, P_ell(x + 70 * s * math.cos(a), y - 40 * s + 70 * s * math.sin(a), 48 * s), C["rosa"], lw=4, shadow=False)
    piece(ctx, P_ell(x, y - 40 * s, 45 * s), C["amarillo"], lw=4)


def montana(ctx, x, y, s, p):
    piece(ctx, P_poly([(x - 200 * s, y + 140 * s), (x - 60 * s, y - 60 * s), (x + 40 * s, y + 140 * s)]), C["gris"], lw=5)
    piece(ctx, P_poly([(x - 100 * s, y + 140 * s), (x + 50 * s, y - 150 * s), (x + 200 * s, y + 140 * s)]), hexc("#7a8499"), lw=5)
    piece(ctx, P_poly([(x + 50 * s, y - 150 * s), (x + 5 * s, y - 62 * s), (x + 30 * s, y - 75 * s), (x + 55 * s, y - 55 * s),
                       (x + 75 * s, y - 80 * s), (x + 95 * s, y - 62 * s)]), C["blanco"], lw=3, shadow=False)


def volcan(ctx, x, y, s, p):
    k = 1 if p % 4 < 2 else 0.85
    piece(ctx, P_poly([(x - 40 * s, y - 80 * s), (x - 70 * s, y - 180 * s * k), (x - 10 * s, y - 120 * s), (x + 20 * s, y - 200 * s * k),
                       (x + 40 * s, y - 120 * s), (x + 80 * s, y - 170 * s * k), (x + 40 * s, y - 80 * s)]), C["naranja"], lw=4)
    piece(ctx, P_poly([(x - 200 * s, y + 140 * s), (x - 50 * s, y - 90 * s), (x + 50 * s, y - 90 * s), (x + 200 * s, y + 140 * s)]), C["marron"], lw=5)
    piece(ctx, P_poly([(x - 50 * s, y - 90 * s), (x + 50 * s, y - 90 * s), (x + 25 * s, y - 30 * s), (x, y - 60 * s), (x - 30 * s, y - 20 * s)]), C["rojo"], lw=3, shadow=False)


def ola(ctx, x, y, s, p):
    d = 15 * s if p % 6 < 3 else 0
    pts = [(x - 200 * s, y + 140 * s), (x - 200 * s, y + 20 * s)]
    for i in range(41):
        t = i / 40
        pts.append((x - 200 * s + 400 * s * t, y + 20 * s - 50 * s * math.sin(t * 3 * math.pi) - d))
    piece(ctx, P_poly(pts + [(x + 200 * s, y + 140 * s)]), C["azul"], lw=5)
    piece(ctx, P_poly([(x - 30 * s, y - 20 * s - d), (x + 50 * s, y - 120 * s - d), (x + 120 * s, y - 60 * s - d), (x + 60 * s, y - 70 * s - d)]), C["celeste"], lw=4)


# ───────────────────────────── animales ─────────────────────────────
def pez(ctx, x, y, s, p):
    c = 15 * s if p % 4 < 2 else -15 * s
    piece(ctx, P_poly([(x + 90 * s, y), (x + 190 * s, y - 80 * s + c), (x + 190 * s, y + 80 * s + c)]), C["naranja"], lw=4)
    piece(ctx, P_ell(x - 20 * s, y, 130 * s, 85 * s), C["naranja"], lw=5)
    for dx in (-10, 40):
        line(ctx, _circ(x + dx * s, y, 60 * s, 8, -0.4 * math.pi, 0.4 * math.pi), 4 * s, hexc("#c4621a"))
    _ojo(ctx, x - 90 * s, y - 20 * s, s, 18)


def pajaro(ctx, x, y, s, p):
    a = -60 if p % 4 < 2 else 20
    piece(ctx, P_poly([(x - 10 * s, y - 10 * s), (x - 140 * s, y + (a - 20) * s), (x - 60 * s, y + 40 * s)]), hexc("#2456a8"), lw=4)
    piece(ctx, P_ell(x, y + 20 * s, 120 * s, 85 * s), C["azul"], lw=5)
    piece(ctx, P_ell(x + 95 * s, y - 50 * s, 60 * s), C["azul"], lw=5)
    piece(ctx, P_poly([(x + 145 * s, y - 60 * s), (x + 200 * s, y - 40 * s), (x + 145 * s, y - 25 * s)]), C["naranja"], lw=3)
    _ojo(ctx, x + 110 * s, y - 60 * s, s, 13)
    for dx in (-25, 25):
        line(ctx, [(x + dx * s, y + 100 * s), (x + dx * s, y + 150 * s)], 6 * s, C["naranja"])


def zancuda(ctx, x, y, s, p):
    """Ave de patas largas (flamenco, garza...)."""
    col = C["rosa"]
    line(ctx, [(x - 10 * s, y + 20 * s), (x - 10 * s, y + 200 * s)], 8 * s, hexc("#e06a8f"))
    line(ctx, [(x + 20 * s, y + 20 * s), (x + 20 * s, y + 110 * s), (x - 15 * s, y + 90 * s)] if p % 6 < 3 else
         [(x + 20 * s, y + 20 * s), (x + 20 * s, y + 200 * s)], 8 * s, hexc("#e06a8f"))
    piece(ctx, P_ell(x, y, 110 * s, 65 * s), col, lw=5)
    line(ctx, [(x + 80 * s, y - 20 * s), (x + 120 * s, y - 120 * s), (x + 80 * s, y - 190 * s)], 22 * s, INK)
    line(ctx, [(x + 80 * s, y - 20 * s), (x + 120 * s, y - 120 * s), (x + 80 * s, y - 190 * s)], 14 * s, col)
    piece(ctx, P_ell(x + 85 * s, y - 200 * s, 32 * s), col, lw=4)
    piece(ctx, P_poly([(x + 110 * s, y - 210 * s), (x + 150 * s, y - 195 * s), (x + 135 * s, y - 165 * s)]), INK, lw=2)
    _ojo(ctx, x + 85 * s, y - 208 * s, s, 9)


def gato(ctx, x, y, s, p):
    c = -10 if p % 6 < 3 else 10
    line(ctx, [(x + 100 * s, y + 120 * s), (x + 170 * s, y + 60 * s), (x + (180 + c) * s, y - 20 * s)], 24 * s, INK)
    line(ctx, [(x + 100 * s, y + 120 * s), (x + 170 * s, y + 60 * s), (x + (180 + c) * s, y - 20 * s)], 16 * s, C["naranja"])
    piece(ctx, P_ell(x, y + 90 * s, 110 * s, 80 * s), C["naranja"], lw=5)
    for d in (-1, 1):
        piece(ctx, P_poly([(x + d * 90 * s, y - 120 * s), (x + d * 95 * s, y - 210 * s), (x + d * 35 * s, y - 155 * s)]), C["naranja"], lw=4)
    piece(ctx, P_ell(x, y - 90 * s, 100 * s, 85 * s), C["naranja"], lw=5)
    for d in (-1, 1):
        _ojo(ctx, x + d * 38 * s, y - 100 * s, s, 16)
        for k in (-8, 8):
            line(ctx, [(x + d * 50 * s, y - 60 * s + k * s), (x + d * 120 * s, y - 65 * s + k * 2 * s)], 3 * s)
    piece(ctx, P_poly([(x - 12 * s, y - 70 * s), (x + 12 * s, y - 70 * s), (x, y - 58 * s)]), C["rosa"], lw=2, shadow=False)


def perro(ctx, x, y, s, p):
    c = -12 if p % 4 < 2 else 12
    line(ctx, [(x - 100 * s, y + 60 * s), (x - (170 + c) * s, y - 10 * s)], 18 * s, C["marronc"])
    piece(ctx, P_ell(x - 10 * s, y + 80 * s, 120 * s, 75 * s), C["marronc"], lw=5)
    for dx in (-80, -20, 40, 90):
        piece(ctx, P_rect(x + dx * s - 14 * s, y + 120 * s, 28 * s, 60 * s), C["marronc"], lw=3, shadow=False)
    piece(ctx, P_ell(x + 70 * s, y - 70 * s, 95 * s, 85 * s), C["marronc"], lw=5)
    for d in (-1, 1):
        piece(ctx, P_ell(x + 70 * s + d * 85 * s, y - 70 * s, 28 * s, 60 * s), C["marron"], lw=4, shadow=False)
        _ojo(ctx, x + 70 * s + d * 32 * s, y - 90 * s, s, 14)
    piece(ctx, P_ell(x + 70 * s, y - 40 * s, 22 * s, 16 * s), INK, lw=0, shadow=False, outline=False)


def abeja(ctx, x, y, s, p):
    a = 1 if p % 2 == 0 else 0.7
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 45 * s, y - 95 * s, 55 * s, 75 * s * a), hexc("#ddf2ff", 0.9), lw=4, shadow=False)
    piece(ctx, P_ell(x, y, 140 * s, 90 * s), C["amarillo"], lw=5)
    ctx.save(); ctx.new_path(); P_ell(x, y, 138 * s, 88 * s)(ctx); ctx.clip()
    for dx in (-60, 0, 60):
        piece(ctx, P_rect(x + dx * s - 14 * s, y - 100 * s, 28 * s, 200 * s), INK, lw=0, shadow=False, outline=False)
    ctx.restore()
    piece(ctx, P_poly([(x - 140 * s, y), (x - 190 * s, y - 10 * s), (x - 140 * s, y + 20 * s)]), INK, lw=2, shadow=False)
    _ojo(ctx, x + 100 * s, y - 20 * s, s, 15)


def mariposa(ctx, x, y, s, p):
    a = 1 if p % 4 < 2 else 0.6
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 85 * s * a, y - 50 * s, 85 * s * a, 80 * s), C["morado"], lw=4)
        piece(ctx, P_ell(x + d * 70 * s * a, y + 70 * s, 60 * s * a, 55 * s), C["rosa"], lw=4)
        piece(ctx, P_ell(x + d * 90 * s * a, y - 50 * s, 25 * s * a, 25 * s), C["amarillo"], lw=2, shadow=False)
    piece(ctx, P_ell(x, y, 18 * s, 110 * s), INK, lw=0, shadow=False)
    for d in (-1, 1):
        line(ctx, [(x, y - 100 * s), (x + d * 40 * s, y - 160 * s)], 4 * s)


def dinosaurio(ctx, x, y, s, p):
    c = 10 if p % 6 < 3 else -10
    piece(ctx, P_poly([(x - 60 * s, y + 20 * s), (x - 230 * s, y + (60 + c) * s), (x - 60 * s, y + 90 * s)]), C["verde"], lw=4)
    piece(ctx, P_ell(x, y + 40 * s, 130 * s, 85 * s), C["verde"], lw=5)
    for dx in (-50, 50):
        piece(ctx, P_rect(x + dx * s - 22 * s, y + 100 * s, 44 * s, 75 * s), C["verde"], lw=4, shadow=False)
    for i in range(4):
        bx = x - 80 * s + i * 50 * s
        piece(ctx, P_poly([(bx - 20 * s, y - 35 * s), (bx, y - 75 * s), (bx + 20 * s, y - 35 * s)]), C["naranja"], lw=3, shadow=False)
    piece(ctx, P_poly([(x + 80 * s, y), (x + 120 * s, y - 120 * s), (x + 210 * s, y - 130 * s), (x + 220 * s, y - 80 * s), (x + 140 * s, y - 60 * s), (x + 130 * s, y + 20 * s)]), C["verde"], lw=5)
    _ojo(ctx, x + 165 * s, y - 108 * s, s, 13)


def huella(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y + 50 * s, 85 * s, 75 * s), C["marron"], lw=5)
    for dx, dy in ((-95, -50), (-35, -110), (35, -110), (95, -50)):
        piece(ctx, P_ell(x + dx * s, y + dy * s, 32 * s, 40 * s), C["marron"], lw=4)


# ───────────────────────────── ciencia y cuerpo ─────────────────────────────
def atomo(ctx, x, y, s, p):
    g = 0.2 if p % 4 < 2 else 0
    for k in range(3):
        ctx.save(); ctx.new_path(); ctx.translate(x, y); ctx.rotate(g + k * math.pi / 3); ctx.scale(1, 0.38)
        ctx.arc(0, 0, 170 * s, 0, 2 * math.pi); ctx.restore()
        set_col(ctx, INK); ctx.set_line_width(14 * s); ctx.stroke_preserve()
        set_col(ctx, C["celeste"]); ctx.set_line_width(8 * s); ctx.stroke()
    piece(ctx, P_ell(x, y, 38 * s), C["rojo"], lw=4)


def adn(ctx, x, y, s, p):
    f = 0.4 if p % 4 < 2 else 0
    a = [(x + 70 * s * math.sin(t / 10 * 2 * math.pi + f), y - 170 * s + t * 17 * s) for t in range(21)]
    b = [(x - 70 * s * math.sin(t / 10 * 2 * math.pi + f), y - 170 * s + t * 17 * s) for t in range(21)]
    for i in range(1, 20, 2):
        line(ctx, [a[i], b[i]], 8 * s, (C["verde"], C["rojo"], C["amarillo"], C["morado"])[i // 2 % 4])
    for pts, col in ((a, C["azul"]), (b, C["rosa"])):
        line(ctx, pts, 20 * s, INK)
        line(ctx, pts, 12 * s, col)


def matraz(ctx, x, y, s, p):
    piece(ctx, P_poly([(x - 35 * s, y - 170 * s), (x + 35 * s, y - 170 * s), (x + 35 * s, y - 50 * s), (x + 140 * s, y + 140 * s),
                       (x - 140 * s, y + 140 * s), (x - 35 * s, y - 50 * s)]), C["blanco"], lw=5)
    piece(ctx, P_poly([(x - 90 * s, y + 50 * s), (x + 90 * s, y + 50 * s), (x + 136 * s, y + 136 * s), (x - 136 * s, y + 136 * s)]), C["verde"], lw=3, shadow=False)
    b = 0 if p % 4 < 2 else -25
    for dx, dy, r in ((-30, 80, 14), (30, 100, 10), (5, 20, 12)):
        piece(ctx, P_ell(x + dx * s, y + (dy + b) * s - (40 * s if dy < 50 else 0), r * s), C["blanco"], lw=2, shadow=False)


def microscopio(ctx, x, y, s, p):
    piece(ctx, P_rrect(x - 130 * s, y + 120 * s, 260 * s, 40 * s, 10 * s), C["gris"], lw=4)
    piece(ctx, P_poly([(x + 40 * s, y + 120 * s), (x + 90 * s, y + 120 * s), (x + 90 * s, y - 40 * s), (x + 40 * s, y - 20 * s)]), C["gris"], lw=4)
    piece(ctx, P_rect(x - 80 * s, y + 30 * s, 160 * s, 22 * s), C["grisc"], lw=4)
    ctx.save(); ctx.translate(x, y - 60 * s); ctx.rotate(-0.45)
    piece(ctx, P_rrect(-35 * s, -130 * s, 70 * s, 200 * s, 12 * s), C["azul"], lw=5)
    piece(ctx, P_rect(-25 * s, 70 * s, 50 * s, 30 * s), INK, lw=0)
    ctx.restore()


def cohete(ctx, x, y, s, p):
    k = 1 if p % 2 == 0 else 0.75
    piece(ctx, P_poly([(x - 40 * s, y + 110 * s), (x, y + (110 + 110 * k) * s), (x + 40 * s, y + 110 * s)]), C["naranja"], lw=4)
    for d in (-1, 1):
        piece(ctx, P_poly([(x + d * 55 * s, y + 20 * s), (x + d * 120 * s, y + 120 * s), (x + d * 55 * s, y + 110 * s)]), C["rojo"], lw=4)
    piece(ctx, P_poly([(x, y - 190 * s), (x + 60 * s, y - 90 * s), (x + 60 * s, y + 110 * s), (x - 60 * s, y + 110 * s), (x - 60 * s, y - 90 * s)]), C["blanco"], lw=5)
    piece(ctx, P_poly([(x, y - 190 * s), (x + 45 * s, y - 115 * s), (x - 45 * s, y - 115 * s)]), C["rojo"], lw=3, shadow=False)
    piece(ctx, P_ell(x, y - 30 * s, 32 * s), C["celeste"], lw=5, shadow=False)


def satelite(ctx, x, y, s, p):
    for d in (-1, 1):
        piece(ctx, P_rect(x + d * 70 * s - (110 * s if d < 0 else 0), y - 40 * s, 110 * s, 80 * s), C["azul"], lw=4)
        line(ctx, [(x + d * 125 * s, y - 40 * s), (x + d * 125 * s, y + 40 * s)], 3 * s)
    piece(ctx, P_rrect(x - 60 * s, y - 70 * s, 120 * s, 140 * s, 14 * s), C["oro"], lw=5)
    line(ctx, [(x, y - 70 * s), (x, y - 130 * s)], 5 * s)
    piece(ctx, P_ell(x, y - 140 * s, 14 * s), C["rojo"] if p % 4 < 2 else C["blanco"], lw=3, shadow=False)


def cerebro(ctx, x, y, s, p):
    col = C["rosa"]
    for cx, cy, r in ((-70, -40, 75), (0, -70, 80), (75, -40, 75), (-60, 40, 70), (60, 40, 70), (0, 20, 70)):
        piece(ctx, P_ell(x + cx * s, y + cy * s, r * s, r * s * 0.85), col, lw=4, shadow=False)
    line(ctx, [(x, y - 130 * s), (x, y + 90 * s)], 5 * s)
    for pts in (((-110, -40), (-70, -20), (-80, 20)), ((110, -40), (70, -20), (80, 20)), ((-40, -100), (-30, -60)), ((40, -100), (30, -60))):
        line(ctx, [(x + a * s, y + b * s) for a, b in pts], 4 * s)
    if p % 4 < 2:
        for a in (-2.4, -1.6, -0.8):
            line(ctx, [(x + 170 * s * math.cos(a), y - 20 * s + 170 * s * math.sin(a)), (x + 210 * s * math.cos(a), y - 20 * s + 210 * s * math.sin(a))], 7 * s, C["amarillo"])


def corazon(ctx, x, y, s, p):
    k = 1.0 if p % 6 < 2 else 0.9
    pts = [(x + 150 * k * s * (16 * math.sin(t) ** 3) / 16,
            y - 150 * k * s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in
           [i / 40 * 2 * math.pi for i in range(40)]]
    piece(ctx, P_poly(pts), C["rojo"], lw=5)
    piece(ctx, P_ell(x - 60 * k * s, y - 60 * k * s, 18 * s, 28 * s), C["blanco"], lw=0, shadow=False, outline=False)


def bombilla(ctx, x, y, s, p):
    if p % 4 < 2:
        for a in [math.pi + i * math.pi / 6 for i in range(7)]:
            line(ctx, [(x + 150 * s * math.cos(a), y - 40 * s + 150 * s * math.sin(a)), (x + 195 * s * math.cos(a), y - 40 * s + 195 * s * math.sin(a))], 8 * s, C["amarillo"])
    piece(ctx, P_rect(x - 45 * s, y + 70 * s, 90 * s, 70 * s), C["gris"], lw=4)
    for k in (90, 115):
        line(ctx, [(x - 45 * s, y + k * s), (x + 45 * s, y + k * s)], 4 * s)
    piece(ctx, P_poly(_circ(x, y - 40 * s, 110 * s, 30, 0.75 * math.pi, 2.25 * math.pi) + [(x + 45 * s, y + 70 * s), (x - 45 * s, y + 70 * s)]), C["amarillo"], lw=5)
    line(ctx, [(x - 25 * s, y + 60 * s), (x - 25 * s, y), (x, y - 30 * s), (x + 25 * s, y), (x + 25 * s, y + 60 * s)], 4 * s, C["naranja"])


def engranaje(ctx, x, y, s, p):
    g = 0.2 if p % 4 < 2 else 0
    pts = []
    for i in range(10):
        a0 = g + i * 2 * math.pi / 10
        for a, r in ((a0 - 0.2, 130), (a0 - 0.13, 165), (a0 + 0.13, 165), (a0 + 0.2, 130), (a0 + 0.42, 130)):
            pts.append((x + r * s * math.cos(a), y + r * s * math.sin(a)))
    piece(ctx, P_poly(pts), C["gris"], lw=5)
    piece(ctx, P_ell(x, y, 45 * s), hexc("#2d3557"), lw=5, shadow=False)


def iman(ctx, x, y, s, p):
    arco = [(x - 140 * s, y + 140 * s), (x - 140 * s, y - 20 * s)] + _circ(x, y - 20 * s, 140 * s, 30, math.pi, 2 * math.pi) + \
           [(x + 140 * s, y + 140 * s), (x + 60 * s, y + 140 * s), (x + 60 * s, y - 20 * s)] + _circ(x, y - 20 * s, 60 * s, 20, 2 * math.pi, math.pi) + \
           [(x - 60 * s, y + 140 * s)]
    piece(ctx, P_poly(arco), C["rojo"], lw=5)
    for d in (-1, 1):
        piece(ctx, P_rect(x + (d * 100 - 40) * s, y + 100 * s, 80 * s, 40 * s), C["grisc"], lw=4, shadow=False)
    if p % 4 < 2:
        for d in (-1, 1):
            line(ctx, [(x + d * 100 * s, y + 170 * s), (x + d * 100 * s, y + 200 * s)], 6 * s, C["amarillo"])


def termometro(ctx, x, y, s, p):
    piece(ctx, P_rrect(x - 35 * s, y - 180 * s, 70 * s, 280 * s, 35 * s), C["blanco"], lw=5)
    piece(ctx, P_ell(x, y + 120 * s, 60 * s), C["rojo"], lw=5)
    h = 220 if p % 6 < 3 else 180
    piece(ctx, P_rect(x - 14 * s, y + (90 - h) * s, 28 * s, h * s), C["rojo"], lw=0, shadow=False, outline=False)
    for k in range(5):
        line(ctx, [(x + 35 * s, y - 140 * s + k * 50 * s), (x + 60 * s, y - 140 * s + k * 50 * s)], 4 * s)


def pastilla(ctx, x, y, s, p):
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.6 + (0.08 if p % 4 < 2 else 0))
    piece(ctx, P_rrect(-170 * s, -65 * s, 340 * s, 130 * s, 65 * s), C["blanco"], lw=5)
    piece(ctx, P_poly([(0, -65 * s), (105 * s, -65 * s)] + _circ(105 * s, 0, 65 * s, 20, -math.pi / 2, math.pi / 2) + [(0, 65 * s)]), C["rojo"], lw=5, shadow=False)
    ctx.restore()


# ───────────────────────────── tecnología ─────────────────────────────
def movil(ctx, x, y, s, p):
    piece(ctx, P_rrect(x - 95 * s, y - 175 * s, 190 * s, 350 * s, 26 * s), C["negro"], lw=5)
    piece(ctx, P_rect(x - 78 * s, y - 145 * s, 156 * s, 270 * s), C["celeste"], lw=2, shadow=False)
    for k in range(3):
        piece(ctx, P_rrect(x - 60 * s, y - 120 * s + k * 70 * s, 120 * s, 50 * s, 10 * s), C["blanco"], lw=2, shadow=False)
    if p % 4 < 2:
        piece(ctx, P_ell(x + 80 * s, y - 165 * s, 30 * s), C["rojo"], lw=4)


def ordenador(ctx, x, y, s, p):
    piece(ctx, P_rrect(x - 170 * s, y - 150 * s, 340 * s, 220 * s, 14 * s), C["negro"], lw=5)
    piece(ctx, P_rect(x - 150 * s, y - 130 * s, 300 * s, 180 * s), C["azul"], lw=2, shadow=False)
    for k in range(3):
        line(ctx, [(x - 120 * s, y - 95 * s + k * 45 * s), (x + (60 - k * 50 + (30 if p % 4 < 2 else 0)) * s, y - 95 * s + k * 45 * s)], 12 * s, C["verde"])
    piece(ctx, P_poly([(x - 30 * s, y + 70 * s), (x + 30 * s, y + 70 * s), (x + 50 * s, y + 130 * s), (x - 50 * s, y + 130 * s)]), C["gris"], lw=4)
    piece(ctx, P_rrect(x - 110 * s, y + 130 * s, 220 * s, 25 * s, 8 * s), C["gris"], lw=4)


def robot(ctx, x, y, s, p):
    a = 20 if p % 4 < 2 else -20
    for d in (-1, 1):
        line(ctx, [(x + d * 100 * s, y + 40 * s), (x + d * 160 * s, y + (40 + d * a) * s)], 22 * s, INK)
        line(ctx, [(x + d * 100 * s, y + 40 * s), (x + d * 160 * s, y + (40 + d * a) * s)], 14 * s, C["gris"])
    piece(ctx, P_rrect(x - 100 * s, y - 10 * s, 200 * s, 170 * s, 20 * s), C["gris"], lw=5)
    piece(ctx, P_rrect(x - 50 * s, y + 30 * s, 100 * s, 60 * s, 8 * s), C["azul"], lw=3, shadow=False)
    line(ctx, [(x, y - 120 * s), (x, y - 170 * s)], 6 * s)
    piece(ctx, P_ell(x, y - 175 * s, 16 * s), C["rojo"] if p % 4 < 2 else C["amarillo"], lw=3, shadow=False)
    piece(ctx, P_rrect(x - 85 * s, y - 130 * s, 170 * s, 110 * s, 20 * s), C["grisc"], lw=5)
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 38 * s, y - 80 * s, 20 * s), C["celeste"], lw=4, shadow=False)
    line(ctx, [(x - 30 * s, y - 45 * s), (x + 30 * s, y - 45 * s)], 6 * s)


def chip(ctx, x, y, s, p):
    for k in range(5):
        o = -100 + k * 50
        for a, b, c, d in ((o, -130, o, -170), (o, 130, o, 170), (-130, o, -170, o), (130, o, 170, o)):
            line(ctx, [(x + a * s, y + b * s), (x + c * s, y + d * s)], 12 * s, C["oro"])
    piece(ctx, P_rrect(x - 130 * s, y - 130 * s, 260 * s, 260 * s, 16 * s), C["negro"], lw=5)
    piece(ctx, P_rect(x - 60 * s, y - 60 * s, 120 * s, 120 * s), C["verde"] if p % 4 < 2 else C["verdeo"], lw=3, shadow=False)


def senal(ctx, x, y, s, p):
    """Ondas de wifi / señal / internet."""
    n = 3 if p % 6 < 3 else 2
    for k in range(n):
        r = (70 + k * 65) * s
        pts = _circ(x, y + 100 * s, r, 20, 1.25 * math.pi, 1.75 * math.pi)
        line(ctx, pts, 30 * s, INK)
        line(ctx, pts, 20 * s, C["azul"])
    piece(ctx, P_ell(x, y + 100 * s, 28 * s), C["azul"], lw=4)


# ───────────────────────────── historia ─────────────────────────────
def piramide(ctx, x, y, s, p):
    piece(ctx, P_poly([(x - 210 * s, y + 140 * s), (x, y - 150 * s), (x + 210 * s, y + 140 * s)]), C["oro"], lw=5)
    piece(ctx, P_poly([(x, y - 150 * s), (x + 210 * s, y + 140 * s), (x + 60 * s, y + 140 * s)]), hexc("#d49a24"), lw=3, shadow=False)
    for k in range(1, 5):
        yy = y - 150 * s + k * 58 * s
        line(ctx, [(x - k * 42 * s, yy), (x + k * 42 * s, yy)], 3 * s)
    sol_y = y - 170 * s if p % 6 < 3 else y - 160 * s
    piece(ctx, P_ell(x + 170 * s, sol_y, 35 * s), C["naranja"], lw=4)


def castillo(ctx, x, y, s, p):
    for d in (-1, 1):
        piece(ctx, P_rect(x + d * 130 * s - 45 * s, y - 120 * s, 90 * s, 260 * s), C["gris"], lw=5)
        for k in range(3):
            piece(ctx, P_rect(x + d * 130 * s - 45 * s + k * 33 * s, y - 150 * s, 24 * s, 32 * s), C["gris"], lw=3, shadow=False)
    piece(ctx, P_rect(x - 90 * s, y - 50 * s, 180 * s, 190 * s), C["grisc"], lw=5)
    for k in range(4):
        piece(ctx, P_rect(x - 90 * s + k * 50 * s, y - 80 * s, 30 * s, 32 * s), C["grisc"], lw=3, shadow=False)
    piece(ctx, P_poly(_circ(x, y + 70 * s, 45 * s, 16, math.pi, 2 * math.pi) + [(x + 45 * s, y + 140 * s), (x - 45 * s, y + 140 * s)]), C["marron"], lw=4)
    line(ctx, [(x + 130 * s, y - 150 * s), (x + 130 * s, y - 230 * s)], 5 * s)
    f = 20 if p % 4 < 2 else 0
    piece(ctx, P_poly([(x + 130 * s, y - 230 * s), (x + 200 * s, y - (215 - f / 2) * s), (x + 130 * s, y - 195 * s)]), C["rojo"], lw=3)


def columna(ctx, x, y, s, p):
    piece(ctx, P_rect(x - 120 * s, y - 170 * s, 240 * s, 40 * s), C["blanco"], lw=5)
    piece(ctx, P_rect(x - 85 * s, y - 130 * s, 170 * s, 250 * s), C["blanco"], lw=5)
    for k in (-50, -17, 17, 50):
        line(ctx, [(x + k * s, y - 120 * s), (x + k * s, y + 110 * s)], 4 * s, C["gris"])
    piece(ctx, P_rect(x - 120 * s, y + 120 * s, 240 * s, 40 * s), C["blanco"], lw=5)


def barco(ctx, x, y, s, p):
    b = 8 * s if p % 6 < 3 else -8 * s
    line(ctx, [(x, y + 60 * s + b), (x, y - 180 * s + b)], 8 * s)
    piece(ctx, P_poly([(x + 10 * s, y - 170 * s + b), (x + 150 * s, y + 30 * s + b), (x + 10 * s, y + 30 * s + b)]), C["blanco"], lw=4)
    piece(ctx, P_poly([(x - 10 * s, y - 130 * s + b), (x - 120 * s, y + 30 * s + b), (x - 10 * s, y + 30 * s + b)]), C["blanco"], lw=4)
    piece(ctx, P_poly([(x - 200 * s, y + 50 * s + b), (x + 200 * s, y + 50 * s + b), (x + 140 * s, y + 140 * s + b), (x - 140 * s, y + 140 * s + b)]), C["marron"], lw=5)
    piece(ctx, P_rect(x - 220 * s, y + 130 * s, 440 * s, 40 * s), C["azul"], lw=4, shadow=False)


def pergamino(ctx, x, y, s, p):
    piece(ctx, P_rect(x - 130 * s, y - 150 * s, 260 * s, 300 * s), hexc("#f1dca7"), lw=5)
    for d in (-1, 1):
        piece(ctx, P_rrect(x - 160 * s, y + d * 150 * s - 25 * s, 320 * s, 50 * s, 25 * s), hexc("#d9b877"), lw=5)
    for k in range(5):
        line(ctx, [(x - 90 * s, y - 90 * s + k * 40 * s), (x + (90 - (40 if k == 4 else 0)) * s, y - 90 * s + k * 40 * s)], 5 * s, C["marron"])


def reloj_arena(ctx, x, y, s, p):
    for d in (-1, 1):
        piece(ctx, P_rrect(x - 130 * s, y + d * 170 * s - 18 * s, 260 * s, 36 * s, 10 * s), C["marron"], lw=4)
    piece(ctx, P_poly([(x - 100 * s, y - 150 * s), (x + 100 * s, y - 150 * s), (x + 15 * s, y), (x + 100 * s, y + 150 * s),
                       (x - 100 * s, y + 150 * s), (x - 15 * s, y)]), hexc("#e8f4ff"), lw=5)
    k = 0.55 if p % 12 < 6 else 0.45
    piece(ctx, P_poly([(x - 100 * k * s, y - 150 * k * s), (x + 100 * k * s, y - 150 * k * s), (x, y - 10 * s)]), C["oro"], lw=0, shadow=False, outline=False)
    piece(ctx, P_poly([(x - 85 * s, y + 147 * s), (x + 85 * s, y + 147 * s), (x, y + (140 - 220 * (1 - k)) * s)]), C["oro"], lw=0, shadow=False, outline=False)
    line(ctx, [(x, y), (x, y + 140 * s)], 4 * s, C["oro"])


# ───────────────────────────── cotidiano ─────────────────────────────
def casa(ctx, x, y, s, p):
    piece(ctx, P_rect(x - 140 * s, y - 20 * s, 280 * s, 170 * s), C["blanco"], lw=5)
    piece(ctx, P_poly([(x - 180 * s, y - 10 * s), (x, y - 170 * s), (x + 180 * s, y - 10 * s)]), C["rojo"], lw=5)
    piece(ctx, P_rect(x - 30 * s, y + 50 * s, 60 * s, 100 * s), C["marron"], lw=4)
    piece(ctx, P_rect(x + 60 * s, y + 20 * s, 55 * s, 55 * s), C["amarillo"] if p % 6 < 3 else C["celeste"], lw=4)
    piece(ctx, P_rect(x - 115 * s, y + 20 * s, 55 * s, 55 * s), C["celeste"], lw=4)


def coche(ctx, x, y, s, p):
    b = 5 * s if p % 2 == 0 else 0
    piece(ctx, P_poly([(x - 100 * s, y - 20 * s - b), (x - 60 * s, y - 100 * s - b), (x + 70 * s, y - 100 * s - b), (x + 120 * s, y - 20 * s - b)]), C["rojo"], lw=5)
    piece(ctx, P_poly([(x - 75 * s, y - 25 * s - b), (x - 45 * s, y - 85 * s - b), (x + 5 * s, y - 85 * s - b), (x + 5 * s, y - 25 * s - b)]), C["celeste"], lw=3, shadow=False)
    piece(ctx, P_poly([(x + 20 * s, y - 25 * s - b), (x + 20 * s, y - 85 * s - b), (x + 62 * s, y - 85 * s - b), (x + 95 * s, y - 25 * s - b)]), C["celeste"], lw=3, shadow=False)
    piece(ctx, P_rrect(x - 190 * s, y - 30 * s - b, 380 * s, 100 * s, 30 * s), C["rojo"], lw=5)
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 110 * s, y + 70 * s, 45 * s), INK, lw=3)
        piece(ctx, P_ell(x + d * 110 * s, y + 70 * s, 18 * s), C["gris"], lw=2, shadow=False)


def reloj(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["blanco"], lw=8)
    for i in range(12):
        a = i * math.pi / 6
        line(ctx, [(x + 120 * s * math.cos(a), y + 120 * s * math.sin(a)), (x + 135 * s * math.cos(a), y + 135 * s * math.sin(a))], 6 * s)
    a = -math.pi / 2 + (p % 12) * math.pi / 6
    line(ctx, [(x, y), (x + 105 * s * math.cos(a), y + 105 * s * math.sin(a))], 7 * s, C["rojo"])
    line(ctx, [(x, y), (x + 70 * s * math.cos(-0.5), y + 70 * s * math.sin(-0.5))], 12 * s)
    piece(ctx, P_ell(x, y, 14 * s), INK, lw=0, shadow=False)


def libro(ctx, x, y, s, p):
    a = 0 if p % 6 < 3 else 10
    piece(ctx, P_poly([(x, y - 110 * s), (x - 190 * s, y - (140 - a) * s), (x - 190 * s, y + 120 * s), (x, y + 150 * s)]), C["blanco"], lw=5)
    piece(ctx, P_poly([(x, y - 110 * s), (x + 190 * s, y - (140 - a) * s), (x + 190 * s, y + 120 * s), (x, y + 150 * s)]), C["blanco"], lw=5)
    for d in (-1, 1):
        for k in range(4):
            line(ctx, [(x + d * 30 * s, y - 70 * s + k * 50 * s), (x + d * 160 * s, y - 90 * s + k * 50 * s)], 5 * s, C["gris"])
    line(ctx, [(x, y - 110 * s), (x, y + 150 * s)], 6 * s)


def hamburguesa(ctx, x, y, s, p):
    piece(ctx, P_rrect(x - 160 * s, y + 70 * s, 320 * s, 60 * s, 28 * s), C["oro"], lw=5)
    piece(ctx, P_rrect(x - 170 * s, y + 20 * s, 340 * s, 60 * s, 26 * s), C["marron"], lw=5)
    piece(ctx, P_poly([(x - 175 * s, y + 25 * s), (x + 175 * s, y + 25 * s)] + [(x + 175 * s - i * 35 * s, y + (5 if i % 2 else 45) * s) for i in range(11)]), C["amarillo"], lw=4, shadow=False)
    piece(ctx, P_rrect(x - 180 * s, y - 15 * s, 360 * s, 30 * s, 14 * s), C["verde"], lw=4, shadow=False)
    piece(ctx, P_poly(_circ(x, y - 15 * s, 165 * s, 30, math.pi, 2 * math.pi)), C["oro"], lw=5)
    for dx, dy in ((-80, -80), (-20, -120), (50, -90), (100, -50), (-120, -40)):
        piece(ctx, P_ell(x + dx * s, y + dy * s, 9 * s, 5 * s), C["blanco"], lw=1, shadow=False)


def manzana(ctx, x, y, s, p):
    line(ctx, [(x, y - 110 * s), (x + 10 * s, y - 170 * s)], 12 * s, C["marron"])
    piece(ctx, P_ell(x + 55 * s, y - 145 * s, 50 * s, 22 * s), C["verde"], lw=4, shadow=False)
    piece(ctx, P_ell(x, y + 10 * s, 140 * s, 125 * s), C["rojo"], lw=5)
    piece(ctx, P_ell(x - 70 * s, y - 30 * s, 18 * s, 30 * s), C["blanco"], lw=0, shadow=False, outline=False)


def taza(ctx, x, y, s, p):
    for k, dx in enumerate((-40, 0, 40)):
        o = 10 if (p + k) % 4 < 2 else -10
        line(ctx, [(x + dx * s, y - 70 * s), (x + (dx + o) * s, y - 110 * s), (x + dx * s, y - 150 * s)], 7 * s, C["grisc"])
    ctx.new_path(); ctx.arc(x + 130 * s, y + 20 * s, 55 * s, 0, 2 * math.pi)
    set_col(ctx, INK); ctx.set_line_width(32 * s); ctx.stroke_preserve(); set_col(ctx, C["blanco"]); ctx.set_line_width(20 * s); ctx.stroke()
    piece(ctx, P_poly([(x - 130 * s, y - 60 * s), (x + 130 * s, y - 60 * s), (x + 110 * s, y + 130 * s), (x - 110 * s, y + 130 * s)]), C["blanco"], lw=5)
    piece(ctx, P_ell(x, y - 60 * s, 128 * s, 22 * s), C["marron"], lw=4, shadow=False)


def balon(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 145 * s), C["blanco"], lw=6)
    g = 0.3 if p % 4 < 2 else 0
    piece(ctx, P_poly(_estrella(x, y, 50 * s, 50 * s, 5, g)[::2]), INK, lw=0, shadow=False)
    for i in range(5):
        a = g - math.pi / 2 + i * 2 * math.pi / 5
        cx, cy = x + 115 * s * math.cos(a), y + 115 * s * math.sin(a)
        line(ctx, [(x + 50 * s * math.cos(a), y + 50 * s * math.sin(a)), (cx, cy)], 5 * s)
        ctx.save(); ctx.new_path(); ctx.arc(x, y, 143 * s, 0, 2 * math.pi); ctx.clip()
        piece(ctx, P_ell(cx + 25 * s * math.cos(a), cy + 25 * s * math.sin(a), 35 * s), INK, lw=0, shadow=False)
        ctx.restore()


def medalla(ctx, x, y, s, p):
    for d, col in ((-1, C["azul"]), (1, C["rojo"])):
        piece(ctx, P_poly([(x + d * 10 * s, y - 40 * s), (x + d * 90 * s, y - 190 * s), (x + d * 30 * s, y - 190 * s), (x - d * 40 * s, y - 50 * s)]), col, lw=4)
    piece(ctx, P_ell(x, y + 50 * s, 110 * s), C["oro"], lw=6)
    piece(ctx, P_poly(_estrella(x, y + 50 * s, 60 * s, 25 * s)), C["amarillo"] if p % 4 < 2 else C["blanco"], lw=3, shadow=False)


def moneda(ctx, x, y, s, p):
    w = 1 if p % 6 < 3 else 0.75
    piece(ctx, P_ell(x, y, 135 * s * w, 135 * s), C["oro"], lw=6)
    piece(ctx, P_ell(x, y, 100 * s * w, 100 * s), hexc("#f7c948"), lw=3, shadow=False)
    ctx.select_font_face("Sans", 0, 1); ctx.set_font_size(130 * s); set_col(ctx, hexc("#a8791c"))
    e = ctx.text_extents("€"); ctx.move_to(x - e.width / 2 - e.x_bearing, y + e.height / 2); ctx.show_text("€")


def regalo(ctx, x, y, s, p):
    a = 0 if p % 6 < 3 else -15
    piece(ctx, P_rect(x - 140 * s, y - 40 * s, 280 * s, 190 * s), C["morado"], lw=5)
    piece(ctx, P_rect(x - 160 * s, y - (100 - a) * s, 320 * s, 65 * s), hexc("#9b78ff"), lw=5)
    piece(ctx, P_rect(x - 25 * s, y - (100 - a) * s, 50 * s, 250 * s - a * s), C["amarillo"], lw=4, shadow=False)
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 55 * s, y - (130 - a) * s, 55 * s, 32 * s), C["amarillo"], lw=4, shadow=False)


def dinero(ctx, x, y, s, p):
    """Pila de monedas + billete: dinero en general."""
    for k in range(4):
        piece(ctx, P_ell(x - 90 * s, y + (110 - k * 35) * s, 80 * s, 28 * s), C["oro"], lw=4, shadow=False)
    ctx.save(); ctx.translate(x + 60 * s, y - 20 * s); ctx.rotate(-0.15 + (0.06 if p % 4 < 2 else 0))
    piece(ctx, P_rect(-130 * s, -70 * s, 260 * s, 140 * s), hexc("#7cc47f"), lw=5)
    piece(ctx, P_ell(0, 0, 40 * s), hexc("#5aa85d"), lw=3, shadow=False)
    ctx.restore()


# ───────────────────────────── símbolos ─────────────────────────────
def check(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["verde"], lw=6)
    line(ctx, [(x - 70 * s, y), (x - 15 * s, y + 60 * s), (x + 80 * s, y - 60 * s)], 30 * s, C["blanco"])


def cruz(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["rojo"], lw=6)
    for a, b in (((-60, -60), (60, 60)), ((60, -60), (-60, 60))):
        line(ctx, [(x + a[0] * s, y + a[1] * s), (x + b[0] * s, y + b[1] * s)], 30 * s, C["blanco"])


def _flecha(ctx, x, y, s, arriba, col):
    k = -1 if arriba else 1
    piece(ctx, P_poly([(x - 50 * s, y - k * 160 * s), (x + 50 * s, y - k * 160 * s), (x + 50 * s, y), (x + 120 * s, y),
                       (x, y + k * 160 * s), (x - 120 * s, y), (x - 50 * s, y)]), col, lw=5)


def sube(ctx, x, y, s, p):
    _flecha(ctx, x, y - (15 * s if p % 4 < 2 else 0), s, True, C["verde"])


def baja(ctx, x, y, s, p):
    _flecha(ctx, x, y + (15 * s if p % 4 < 2 else 0), s, False, C["rojo"])


def peligro(ctx, x, y, s, p):
    piece(ctx, P_poly([(x, y - 160 * s), (x + 175 * s, y + 140 * s), (x - 175 * s, y + 140 * s)]), C["amarillo"], lw=6)
    piece(ctx, P_rrect(x - 16 * s, y - 70 * s, 32 * s, 130 * s, 12 * s), INK, lw=0, shadow=False)
    piece(ctx, P_ell(x, y + 95 * s, 18 * s), INK, lw=0, shadow=False)


def feliz(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["amarillo"], lw=6)
    _cara(ctx, x, y + (0 if p % 6 < 3 else -6 * s), 1.4 * s, True)


def triste(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["celeste"], lw=6)
    _cara(ctx, x, y, 1.4 * s, False)
    piece(ctx, P_ell(x + 50 * s, y + (10 if p % 6 < 3 else 30) * s, 10 * s, 16 * s), C["azul"], lw=2, shadow=False)


def sorpresa(ctx, x, y, s, p):
    piece(ctx, P_ell(x, y, 150 * s), C["naranja"], lw=6)
    for d in (-1, 1):
        piece(ctx, P_ell(x + d * 50 * s, y - 35 * s, 18 * s, 26 * s), INK, lw=0, shadow=False)
    k = 1 if p % 4 < 2 else 0.8
    piece(ctx, P_ell(x, y + 60 * s, 32 * s * k, 42 * s * k), INK, lw=0, shadow=False)


def idea(ctx, x, y, s, p):
    bombilla(ctx, x, y, s, p)


DIBUJOS = {f.__name__: f for f in (
    sol, luna, estrella, planeta, tierra, nube, lluvia, rayo, fuego, gota, arbol, flor, montana, volcan, ola,
    pez, pajaro, zancuda, gato, perro, abeja, mariposa, dinosaurio, huella,
    atomo, adn, matraz, microscopio, cohete, satelite, cerebro, corazon, bombilla, engranaje, iman, termometro, pastilla,
    movil, ordenador, robot, chip, senal,
    piramide, castillo, columna, barco, pergamino, reloj_arena,
    casa, coche, reloj, libro, hamburguesa, manzana, taza, balon, medalla, moneda, regalo, dinero,
    check, cruz, sube, baja, peligro, feliz, triste, sorpresa)}

CATEGORIAS = {
    "naturaleza y espacio": "sol luna estrella planeta tierra nube lluvia rayo fuego gota arbol flor montana volcan ola",
    "animales": "pez pajaro zancuda gato perro abeja mariposa dinosaurio huella",
    "ciencia y cuerpo": "atomo adn matraz microscopio cohete satelite cerebro corazon bombilla engranaje iman termometro pastilla",
    "tecnología": "movil ordenador robot chip senal",
    "historia": "piramide castillo columna barco pergamino reloj_arena",
    "cotidiano": "casa coche reloj libro hamburguesa manzana taza balon medalla moneda regalo dinero",
    "símbolos y emociones": "check cruz sube baja peligro feliz triste sorpresa",
}


def dibujar(ctx, k, x, y, s=1.0, pose=0):
    DIBUJOS[k](ctx, x, y, s, pose)


if __name__ == "__main__":   # hoja con todos los dibujos: python iconos.py → salida/iconos.png
    import cairo
    n = len(DIBUJOS)
    cols = 8
    filas = (n + cols - 1) // cols
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, cols * 260, filas * 280)
    ctx = cairo.Context(surf)
    set_col(ctx, hexc("#2d3557")); ctx.paint()
    for i, (k, f) in enumerate(DIBUJOS.items()):
        cx, cy = (i % cols) * 260 + 130, (i // cols) * 280 + 125
        f(ctx, cx, cy, 0.48, 0)
        ctx.select_font_face("Sans", 0, 1); ctx.set_font_size(20); set_col(ctx, (1, 1, 1))
        e = ctx.text_extents(k); ctx.move_to(cx - e.width / 2, cy + 140); ctx.show_text(k)
    surf.write_to_png("salida/iconos.png")
    print(n, "dibujos → salida/iconos.png")
