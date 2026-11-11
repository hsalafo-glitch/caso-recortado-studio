"""El narrador: un personaje articulado original (cabeza grande, cuerpo pequeño) que entra andando y gesticula.

    dibujar(ctx, x, pies, s, gesto, lt, pose, mira=0)

Gestos: neutro · saluda · senala · piensa · sorpresa · celebra · triste · explica · corre
Brazos y piernas tienen dos tramos (hombro→codo→mano, cadera→rodilla→pie); cada gesto es un juego de ángulos y
el personaje pasa del andar al gesto mezclando ángulos. Se dibuja con piece()/line(), así que respeta el estilo
visual activo (papel, palitos, 3D, neón...).
"""
import math

from generar_short import INK, P_ell, P_rrect, clamp, hexc, line, piece

GESTOS = ["neutro", "saluda", "senala", "piensa", "sorpresa", "celebra", "triste", "explica", "corre"]

PIEL, CAMISETA, PANTALON, ZAPATO = hexc("#f2c9a0"), hexc("#e63946"), hexc("#2b3a67"), hexc("#1d1f29")

# ángulos en grados desde «colgando hacia abajo»; positivo = hacia fuera del cuerpo y hacia arriba
#            brazo izq (hombro, codo)  brazo der (hombro, codo)   boca        cejas  cabeza  salto
POSES = {
    "neutro":   ((12, 8),              (12, 8),                   "sonrisa",  0,     0,      0),
    "saluda":   ((12, 8),              (150, 20),                 "sonrisa",  1,     4,      0),
    "senala":   ((14, 10),             (92, 0),                   "sonrisa",  1,     3,      0),
    "piensa":   ((10, 10),             (38, 150),                 "linea",    2,     -7,     0),
    "sorpresa": ((118, 20),            (118, 20),                 "o",        3,     0,      1),
    "celebra":  ((138, 14),            (138, 14),                 "abierta",  1,     0,      2),
    "triste":   ((4, 4),               (4, 4),                    "triste",   -2,    9,      0),
    "explica":  ((55, 95),             (55, 95),                  "abierta",  1,     0,      0),
    "corre":    ((40, 80),             (-30, 80),                 "abierta",  1,     6,      0),
}
ENTRA = 0.7      # segundos andando hasta su sitio
MEZCLA = 0.3     # segundos para pasar del andar al gesto


def _punta(o, largo, ang, lado):
    a = math.radians(ang)
    return (o[0] + lado * largo * math.sin(a), o[1] + largo * math.cos(a))


def _miembro(ctx, o, l1, l2, a1, a2, lado, grosor, col, fin=None):
    """Dos tramos: o → articulación → extremo. a2 se suma a a1 (cuánto se dobla). Devuelve el extremo."""
    codo = _punta(o, l1, a1, lado)
    mano = _punta(codo, l2, a1 + a2, lado)
    line(ctx, [o, codo, mano], grosor + 8, INK)
    line(ctx, [o, codo, mano], grosor, col)
    if fin:
        piece(ctx, P_ell(mano[0], mano[1], fin[0], fin[1]), fin[2], lw=4, shadow=False)
    return mano


def dibujar(ctx, x, pies, s, gesto="neutro", lt=9.0, pose=0, mira=0, desde=-1):
    """Personaje con los pies en (x, pies). lt = segundos desde que empezó la escena; desde = lado por el que entra."""
    g = POSES.get(gesto, POSES["neutro"])
    andando = lt < ENTRA
    k = clamp((lt - ENTRA) / MEZCLA)                      # 0 = andar, 1 = gesto
    k = k * k * (3 - 2 * k)
    if andando:
        x = x + desde * 620 * (1 - lt / ENTRA) ** 1.4
    ciclo = math.sin(pose * math.pi / 3)                  # paso de andar/correr (6 poses por zancada)
    corre = gesto == "corre"
    paso = ciclo if (andando or corre) else 0.0
    mov = 1 - k if not corre else 1.0                     # cuánto «andar» queda

    salto = 0.0
    if g[5] and not andando:
        salto = (0, -26, -44, -26, 0, 0)[pose % 6] * (1.0 if g[5] == 2 else (1.0 if lt - ENTRA < 0.9 else 0.0)) * s
    bote = (3 if pose % 8 < 4 else 0) * s + abs(paso) * 10 * s * mov
    y0 = pies + salto - bote

    alto_pierna, torso = 120 * s, 150 * s
    cadera_y = y0 - alto_pierna
    hombro_y = cadera_y - torso + 26 * s
    cab_r = 92 * s
    cab = (x + g[4] * 0.6 * s * k, hombro_y - cab_r * 0.78)

    # piernas (detrás del cuerpo)
    for lado, fase in ((-1, 1), (1, -1)):
        a = lado * 6 * (1 - mov) + fase * paso * (34 if corre else 24) * mov      # al andar, las dos van adelante/atrás
        rod = max(0.0, -fase * paso) * (60 if corre else 30) * mov
        fin = _miembro(ctx, (x + lado * 30 * s, cadera_y), alto_pierna * 0.5, alto_pierna * 0.5, a, -rod, 1, 26 * s, PANTALON)
        piece(ctx, P_ell(fin[0] + 10 * s, fin[1], 26 * s, 14 * s), ZAPATO, lw=3, shadow=False)

    # brazo izquierdo (detrás)
    def brazo(lado, ang):
        a1 = ang[0] * k + (lado * -1 * paso * 30 + 10) * (1 - k if not corre else 0)
        a2 = ang[1] * k + 12 * (1 - k)
        if gesto == "saluda" and lado == 1 and k > 0.9:
            a2 += 28 * math.sin(pose * math.pi / 2)
        if gesto == "explica" and k > 0.9:
            a1 += 14 * math.sin(pose * math.pi / 4 + (0 if lado == 1 else math.pi))
        if corre:
            a1, a2 = ang[0] * lado * ciclo + 10, 80
        return _miembro(ctx, (x + lado * 62 * s, hombro_y + 14 * s), 62 * s, 58 * s, a1, a2, lado, 22 * s, CAMISETA,
                        (17 * s, 17 * s, PIEL))

    brazo(-1, g[0])
    # cuerpo
    piece(ctx, P_rrect(x - 72 * s, hombro_y - 8 * s, 144 * s, torso, 44 * s), CAMISETA, lw=5)
    piece(ctx, P_rrect(x - 66 * s, cadera_y - 34 * s, 132 * s, 52 * s, 20 * s), PANTALON, lw=4, shadow=False)
    mano = brazo(1, g[1])
    if gesto == "senala" and k > 0.9:                       # dedo índice
        line(ctx, [mano, (mano[0] + 30 * s, mano[1] - 4 * s)], 9 * s, INK)

    # cabeza
    piece(ctx, P_ell(cab[0], cab[1], cab_r, cab_r * 0.95), PIEL, lw=5)
    piece(ctx, P_ell(cab[0] - 6 * s, cab[1] - cab_r * 0.62, cab_r * 0.86, cab_r * 0.42), hexc("#4a2f1d"), lw=4, shadow=False)   # pelo
    parpadeo = pose % 34 in (0, 1)
    dx = mira * 9 * s
    for lado in (-1, 1):
        ex, ey = cab[0] + lado * 34 * s, cab[1] + 2 * s
        if parpadeo:
            line(ctx, [(ex - 13 * s, ey), (ex + 13 * s, ey)], 6 * s, INK)
        else:
            alto = 24 * s if g[2] != "o" else 28 * s
            piece(ctx, P_ell(ex, ey, 15 * s, alto), (1, 1, 1), lw=3, shadow=False)
            piece(ctx, P_ell(ex + dx, ey + 3 * s, 7 * s, 11 * s), INK, lw=0, shadow=False, outline=False)
        c = g[3] * k                                        # cejas: + arriba, − caídas, 2 = una levantada
        sube = (12 if c > 0 else 0) * s + (8 * s if (g[3] == 2 and lado == 1) else 0)
        incl = (-8 if g[3] < 0 else (4 if g[3] == 3 else 0)) * s * lado
        line(ctx, [(ex - 16 * s, ey - 38 * s - sube + incl), (ex + 16 * s, ey - 38 * s - sube - incl)], 7 * s, hexc("#4a2f1d"))
    bx, by = cab[0] + dx * 0.4, cab[1] + 46 * s
    boca = g[2] if k > 0.5 else "sonrisa"
    if boca == "o":
        piece(ctx, P_ell(bx, by + 2 * s, 14 * s, 18 * s), INK, lw=0, shadow=False, outline=False)
    elif boca == "abierta":
        ab = 16 * s if pose % 4 < 2 else 9 * s
        piece(ctx, P_ell(bx, by, 24 * s, ab), hexc("#7a1f2b"), lw=4, shadow=False)
    elif boca == "linea":
        line(ctx, [(bx - 16 * s, by + 2 * s), (bx + 16 * s, by - 2 * s)], 7 * s, INK)
    elif boca == "triste":
        line(ctx, [(bx - 22 * s, by + 10 * s), (bx, by), (bx + 22 * s, by + 10 * s)], 7 * s, INK)
    else:
        line(ctx, [(bx - 24 * s, by - 4 * s), (bx, by + 8 * s), (bx + 24 * s, by - 4 * s)], 7 * s, INK)
    if gesto == "piensa" and k > 0.9:                       # burbujas de pensar
        for i, (px, py, r) in enumerate(((95, -95, 9), (120, -125, 13), (150, -165, 18))):
            if (pose // 4) % 4 >= i:
                piece(ctx, P_ell(cab[0] + px * s, cab[1] + py * s, r * s), (1, 1, 1), lw=3, shadow=False)
    return cab
