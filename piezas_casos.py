"""Piezas compartidas por los shorts de Cooper, Mona Lisa y el museo de Boston."""
import math

from generar_short import (INK, P_ell, P_poly, P_rect, P_rrect, clamp, draw_text, ease_io, hexc, hnoise, lerp,
                           line, piece, rot, set_col, silhouette, stars)
from generar_short_estafas import txt
import generar_short as _g

SOMBRA, BORDE = hexc("#1d1a2e"), hexc("#6b72a8")
ROJO = hexc("#e23b3b")
ORO = hexc("#d9a520")
VERDE_BILLETE = hexc("#9fd6a0")


def fondo(ctx, col="#2d3557", suelo=1320, col_suelo="#1d2440"):
    if _g.ESTILO != "recortes":
        import estilos
        return estilos.fondo(ctx, col, suelo, col_suelo)
    import escenario                      # fondo de estudio: degradado, luz, profundidad y suelo sin raya
    escenario.estudio(ctx, hexc(col), suelo)


def noche(ctx, pose, suelo=None):
    if _g.ESTILO != "recortes":
        import estilos
        return estilos.fondo(ctx, "#141a33", suelo, "#0c1024", noche=True, pose=pose)
    import escenario
    escenario.estudio(ctx, hexc("#1b2346"), suelo, pose, noche=True, intensidad=0.8)
    piece(ctx, P_ell(860, 620, 70), hexc("#f3e6b0"), lw=4)
    piece(ctx, P_ell(888, 600, 60), hexc("#1d2549"), lw=0, shadow=False, outline=False)


def silueta(ctx, x, feet, s, pose=0, k=0, tilt=None):
    if _g.ESTILO in ("palitos", "neon", "holograma"):
        import estilos
        return estilos.palito(ctx, x, feet, s, pose, k)
    t = math.radians(4 if (pose + k) % 6 < 3 else -3) if tilt is None else tilt
    silhouette(ctx, x, feet, s, t, SOMBRA, BORDE)


def gafas_oscuras(ctx, x, feet, s):
    hy = feet - 230 * s - 72 * s * 0.9
    for dx in (-26, 26):
        piece(ctx, P_rrect(x + dx * s - 22 * s, hy - 8 * s, 44 * s, 26 * s, 8 * s), hexc("#05060a"), lw=3,
              shadow=False)
    line(ctx, [(x - 4 * s, hy), (x + 4 * s, hy)], 4 * s, hexc("#05060a"))


def gorra_poli(ctx, x, feet, s):
    hy = feet - 230 * s - 72 * s * 0.9
    piece(ctx, P_poly([(x - 70 * s, hy - 40 * s), (x + 70 * s, hy - 40 * s), (x + 60 * s, hy - 95 * s),
                       (x - 60 * s, hy - 95 * s)]), hexc("#1b2747"), lw=4, shadow=False)
    piece(ctx, P_rrect(x - 85 * s, hy - 48 * s, 170 * s, 20 * s, 8 * s), hexc("#0e1630"), lw=3, shadow=False)
    piece(ctx, P_ell(x, hy - 70 * s, 12 * s), ORO, lw=2, shadow=False)


def marco(ctx, x, y, w, h, contenido=None, vacio=False, borde=None):
    b = borde or max(18, w * 0.09)
    piece(ctx, P_rect(x, y, w, h), ORO, lw=5)
    piece(ctx, P_rect(x + b * 0.35, y + b * 0.35, w - b * 0.7, h - b * 0.7), hexc("#b5841a"), lw=2, shadow=False)
    ix, iy, iw, ih = x + b, y + b, w - 2 * b, h - 2 * b
    if vacio:
        piece(ctx, P_rect(ix, iy, iw, ih), hexc("#6b5a7a"), lw=3, shadow=False)
        txt(ctx, "VACÍO", ix + iw / 2, iy + ih / 2 + 12, max(18, iw * 0.16), hexc("#cfc3da"), anchor="center")
        return
    ctx.save()
    P_rect(ix, iy, iw, ih)(ctx)
    ctx.clip()
    if contenido:
        contenido(ctx, ix, iy, iw, ih)
    ctx.restore()
    piece(ctx, P_rect(ix, iy, iw, ih), (0, 0, 0, 0), lw=3, shadow=False)


def retrato(ctx, x, y, w, h):
    """Retrato renacentista esquemático (paisaje, figura sin rasgos, manos cruzadas)."""
    set_col(ctx, hexc("#5f6b45"))
    ctx.paint()
    piece(ctx, P_rect(x, y + h * 0.42, w, h), hexc("#3d4a35"), lw=0, shadow=False, outline=False)
    piece(ctx, P_poly([(x, y + h * 0.35), (x + w * 0.3, y + h * 0.28), (x + w * 0.2, y + h * 0.45), (x, y + h * 0.5)]),
          hexc("#8aa39a"), lw=0, shadow=False, outline=False)
    piece(ctx, P_poly([(x + w, y + h * 0.3), (x + w * 0.72, y + h * 0.36), (x + w * 0.8, y + h * 0.5), (x + w, y + h * 0.52)]),
          hexc("#8aa39a"), lw=0, shadow=False, outline=False)
    cx = x + w / 2
    piece(ctx, P_poly([(cx - w * 0.42, y + h), (cx + w * 0.42, y + h), (cx + w * 0.3, y + h * 0.55),
                       (cx - w * 0.3, y + h * 0.55)]), hexc("#2b2418"), lw=2, shadow=False)
    piece(ctx, P_ell(cx, y + h * 0.37, w * 0.24, h * 0.2), hexc("#1f1a12"), lw=2, shadow=False)
    piece(ctx, P_ell(cx, y + h * 0.38, w * 0.17, h * 0.155), hexc("#d6a86a"), lw=2, shadow=False)
    piece(ctx, P_ell(cx, y + h * 0.88, w * 0.2, h * 0.05), hexc("#d6a86a"), lw=2, shadow=False)


def billetes_fajo(ctx, x, y, s=1.0):
    for i in range(4):
        piece(ctx, P_rect(x - 70 * s, y - i * 14 * s, 140 * s, 60 * s), VERDE_BILLETE, lw=3, shadow=False)
    piece(ctx, P_ell(x, y - 3 * 14 * s + 30 * s, 16 * s), hexc("#5fa35a"), lw=2, shadow=False)
    piece(ctx, P_rect(x - 12 * s, y - 3 * 14 * s, 24 * s, 60 * s), hexc("#e6d9a8"), lw=2, shadow=False)


def mochila_paracaidas(ctx, x, y, s=1.0, col="#e07a2d"):
    piece(ctx, P_rrect(x - 60 * s, y - 80 * s, 120 * s, 160 * s, 24 * s), hexc(col), lw=4)
    line(ctx, [(x - 40 * s, y - 80 * s), (x - 40 * s, y + 80 * s)], 6 * s, hexc("#3d3f4a"))
    line(ctx, [(x + 40 * s, y - 80 * s), (x + 40 * s, y + 80 * s)], 6 * s, hexc("#3d3f4a"))
    piece(ctx, P_ell(x, y, 16 * s), hexc("#c9ccd6"), lw=3, shadow=False)


def paracaidas(ctx, x, y, s, abierto=1.0, col="#f2f2f2"):
    """Persona en silueta colgando de un paracaídas (x,y = pies)."""
    if abierto > 0.05:
        r = 170 * s * abierto
        cy = y - 420 * s
        ctx.new_sub_path()
        ctx.arc(x, cy, r, math.pi, 2 * math.pi)
        ctx.close_path()
        set_col(ctx, hexc(col))
        ctx.fill_preserve()
        set_col(ctx, INK)
        ctx.set_line_width(4)
        ctx.stroke()
        for k in range(-2, 3):
            line(ctx, [(x + k * r / 2.2, cy), (x, y - 220 * s)], 2.5, INK)
            if k < 2:
                piece(ctx, P_poly([(x + k * r / 2, cy), (x + (k + 1) * r / 2, cy), (x + (k + 0.5) * r / 2, cy - r * 0.5)]),
                      hexc("#e07a2d") if k % 2 == 0 else hexc(col), lw=0, shadow=False, outline=False)
    silhouette(ctx, x, y, 0.5 * s, 0.0, SOMBRA, BORDE)


def avion_lado(ctx, x, y, s=1.0, escalera=0.0, luces=0):
    """Avión trirreactor de pasajeros visto de lado, genérico (x,y = centro del fuselaje)."""
    L = 760 * s
    piece(ctx, P_poly([(x - L * 0.32, y - 30 * s), (x - L * 0.5, y - 210 * s), (x - L * 0.42, y - 210 * s),
                       (x - L * 0.2, y - 40 * s)]), hexc("#cfd5df"), lw=4)
    piece(ctx, P_rrect(x - L * 0.5, y - 55 * s, L, 110 * s, 55 * s), (1, 1, 1), lw=5)
    piece(ctx, P_poly([(x + L * 0.5 - 10 * s, y - 50 * s), (x + L * 0.58, y), (x + L * 0.5 - 10 * s, y + 50 * s)]),
          (1, 1, 1), lw=4)
    piece(ctx, P_rect(x - L * 0.46, y - 6 * s, L * 0.98, 18 * s), hexc("#c8202f"), lw=0, shadow=False, outline=False)
    for i in range(12):
        piece(ctx, P_ell(x - L * 0.3 + i * L * 0.062, y - 22 * s, 9 * s, 11 * s),
              hexc("#ffe58a") if luces else hexc("#8ec5e8"), lw=2, shadow=False)
    piece(ctx, P_poly([(x - L * 0.05, y + 20 * s), (x + L * 0.16, y + 20 * s), (x - L * 0.12, y + 110 * s),
                       (x - L * 0.2, y + 110 * s)]), hexc("#b5bccb"), lw=4)
    piece(ctx, P_rrect(x - L * 0.42, y - 80 * s, L * 0.16, 44 * s, 20 * s), hexc("#9aa0ab"), lw=4)
    if escalera > 0:
        a = escalera
        piece(ctx, P_poly([(x - L * 0.47, y + 40 * s), (x - L * 0.41, y + 40 * s),
                           (x - L * 0.47 - 140 * s * a, y + (40 + 150 * a) * s),
                           (x - L * 0.53 - 140 * s * a, y + (40 + 150 * a) * s)]), hexc("#6b6f78"), lw=4)


def avion_noche(ctx, x, y, s, pose):
    avion_lado(ctx, x, y, s, luces=1)
    on = pose % 6 < 3
    piece(ctx, P_ell(x - 360 * s, y - 200 * s, 9 * s), ROJO if on else hexc("#6b1d24"), lw=0, shadow=False,
          outline=False)


def nube(ctx, x, y, s, col="#3a4170"):
    for dx, dy, r in ((-90, 10, 70), (0, -20, 95), (95, 10, 72), (40, 30, 70), (-40, 30, 70)):
        piece(ctx, P_ell(x + dx * s, y + dy * s, r * s), hexc(col), lw=0, shadow=False, outline=False)


def expediente(ctx, x, y, w, h, titulo, pose=0):
    piece(ctx, P_rect(x + 40, y - 40, w * 0.35, 60), hexc("#d9b46a"), lw=4)
    piece(ctx, P_rect(x, y, w, h), hexc("#e8c57e"), lw=5)
    txt(ctx, titulo, x + w / 2, y + 80, 52, hexc("#5a3a14"), anchor="center")
    piece(ctx, P_rect(x + w / 2 - 150, y + 130, 300, 340), hexc("#f3f1ea"), lw=4)
    silhouette(ctx, x + w / 2, y + 470, 0.9, 0.0, SOMBRA, BORDE)
    bob = (pose // 4) % 2 * 8
    draw_text(ctx, "?", x + w / 2, y + 270 - bob, 150, hexc("#ffe14d"), INK, 7)
