"""El narrador: un personaje articulado original (cabeza grande, cuerpo pequeño) que entra andando y gesticula.

    dibujar(ctx, x, pies, s, gesto, lt, pose, mira=0)

Gestos: neutro · saluda · senala · piensa · sorpresa · celebra · triste · explica · corre
Brazos y piernas tienen dos tramos (hombro→codo→mano, cadera→rodilla→pie); cada gesto es un juego de ángulos y
el personaje pasa del andar al gesto mezclando ángulos. Se dibuja con piece()/line(), así que respeta el estilo
visual activo (papel, palitos, 3D, neón...).
"""
import math

import generar_short as G
from generar_short import INK, P_ell, P_poly, P_rrect, clamp, hexc, line, piece

GESTOS = ["neutro", "saluda", "senala", "piensa", "sorpresa", "celebra", "triste", "explica", "corre"]

PIEL, CAMISETA, PANTALON, ZAPATO = hexc("#f2c9a0"), hexc("#e63946"), hexc("#2b3a67"), hexc("#1d1f29")
PELO, MEJILLA, SUELA = hexc("#3b2416"), hexc("#ff8a8a"), hexc("#f4f1ea")

# ── Personalización (la elige el usuario en la web): opciones sencillas, cada una con su nombre para la web ──
OPCIONES = {
    "pelo": {"corto": "Corto", "largo": "Largo", "rizado": "Rizado", "coleta": "Coleta", "calvo": "Calvo"},
    "color_pelo": {"castano": ("Castaño", "#3b2416"), "negro": ("Negro", "#16161c"), "rubio": ("Rubio", "#e0b45a"),
                   "pelirrojo": ("Pelirrojo", "#b5462a"), "canoso": ("Canoso", "#c4c4ca")},
    "piel": {"clara": ("Clara", "#f2c9a0"), "media": ("Media", "#d9a273"), "morena": ("Morena", "#a8704a"),
             "oscura": ("Oscura", "#6b4430")},
    "ropa": {"rojo": ("Roja", "#e63946"), "azul": ("Azul", "#2f6fd6"), "verde": ("Verde", "#2a9d6f"),
             "negro": ("Negra", "#2b2b33"), "amarillo": ("Amarilla", "#f2b632"), "morado": ("Morada", "#7b4fd6")},
    "gafas": {"no": "Sin gafas", "si": "Con gafas"},
    "barba": {"no": "Sin barba", "si": "Con barba"},
}
POR_DEFECTO = {"pelo": "corto", "color_pelo": "castano", "piel": "clara", "ropa": "rojo", "gafas": "no", "barba": "no"}
ASPECTO = dict(POR_DEFECTO)


def valida(d):
    """Devuelve un aspecto válido: cualquier valor desconocido se cambia por el de por defecto."""
    d = d if isinstance(d, dict) else {}
    return {k: (d.get(k) if d.get(k) in OPCIONES[k] else v) for k, v in POR_DEFECTO.items()}


def aspecto(d=None):
    """Elige el aspecto del narrador para los dibujos que vengan después."""
    global PIEL, CAMISETA, PELO
    ASPECTO.clear()
    ASPECTO.update(valida(d))
    PIEL = hexc(OPCIONES["piel"][ASPECTO["piel"]][1])
    CAMISETA = hexc(OPCIONES["ropa"][ASPECTO["ropa"]][1])
    PELO = hexc(OPCIONES["color_pelo"][ASPECTO["color_pelo"]][1])
SIN_VOLUMEN = ("palitos", "neon", "holograma", "pixel")    # estilos de línea: sin sombreado ni rubor


def _volumen(ctx, camino, lado=1, fuerza=0.16, ancho=0.4, x0=None, w=None):
    """Sombra de volumen (luz desde arriba a la izquierda): oscurece el lado derecho de una forma."""
    if G.ESTILO in SIN_VOLUMEN:
        return
    ctx.save()
    ctx.new_path()
    camino(ctx)
    ctx.clip()
    x1, y1, x2, y2 = ctx.clip_extents()
    ctx.new_path()
    if lado > 0:
        ctx.rectangle(x2 - (x2 - x1) * ancho, y1, (x2 - x1) * ancho, y2 - y1)
    else:
        ctx.rectangle(x1, y1, (x2 - x1) * ancho, y2 - y1)
    ctx.set_source_rgba(0.05, 0.03, 0.12, fuerza)
    ctx.fill()
    ctx.restore()

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


def _pelo_delante(ctx, cab, cab_r, s, estilo):
    """Pelo encima de la cabeza según el estilo elegido."""
    px, py = cab[0] - 4 * s, cab[1] - cab_r * 0.55
    if estilo == "calvo":                                     # solo los lados y un brillo en la cabeza
        for lado in (-1, 1):
            piece(ctx, P_ell(cab[0] + lado * cab_r * 0.86, cab[1] - cab_r * 0.12, cab_r * 0.17, cab_r * 0.3), PELO, lw=3,
                  shadow=False)
        if G.ESTILO not in SIN_VOLUMEN:
            line(ctx, [(cab[0] - cab_r * 0.4, cab[1] - cab_r * 0.7), (cab[0] - cab_r * 0.05, cab[1] - cab_r * 0.82)],
                 9 * s, (1, 1, 1, 0.35))
        return
    if estilo == "rizado":                                    # nube de rizos
        for i in range(9):
            a = math.pi * (1.05 + i * 0.9 / 8)
            piece(ctx, P_ell(cab[0] + cab_r * 0.82 * math.cos(a), cab[1] - cab_r * 0.25 + cab_r * 0.72 * math.sin(a),
                             cab_r * 0.3, cab_r * 0.3), PELO, lw=4, shadow=False)
        piece(ctx, P_ell(cab[0], cab[1] - cab_r * 0.66, cab_r * 0.72, cab_r * 0.36), PELO, lw=0, shadow=False, outline=False)
        return
    pelo = [(px - cab_r * 0.95, py + 34 * s), (px - cab_r * 0.98, py - 6 * s), (px - cab_r * 0.7, py - 46 * s),
            (px - cab_r * 0.2, py - 62 * s), (px + cab_r * 0.45, py - 58 * s), (px + cab_r * 0.88, py - 28 * s),
            (px + cab_r * 0.98, py + 22 * s), (px + cab_r * 0.72, py + 12 * s),               # lado derecho
            (px + cab_r * 0.48, py + 16 * s), (px + cab_r * 0.30, py - 2 * s),                # flequillo (mechones)
            (px + cab_r * 0.05, py + 18 * s), (px - cab_r * 0.18, py - 2 * s),
            (px - cab_r * 0.45, py + 20 * s), (px - cab_r * 0.62, py + 2 * s), (px - cab_r * 0.82, py + 26 * s)]
    if estilo == "largo":                                     # raya al lado, cae por los dos lados de la cara
        pelo = [(px - cab_r * 1.02, py + 90 * s), (px - cab_r * 0.98, py - 6 * s), (px - cab_r * 0.7, py - 46 * s),
                (px - cab_r * 0.2, py - 62 * s), (px + cab_r * 0.45, py - 58 * s), (px + cab_r * 0.9, py - 28 * s),
                (px + cab_r * 1.04, py + 90 * s), (px + cab_r * 0.84, py + 60 * s), (px + cab_r * 0.66, py + 4 * s),
                (px - cab_r * 0.2, py + 22 * s), (px - cab_r * 0.72, py + 14 * s), (px - cab_r * 0.84, py + 60 * s)]
    piece(ctx, P_poly(pelo), PELO, lw=4, shadow=False)
    if G.ESTILO not in SIN_VOLUMEN:                          # brillo del pelo
        line(ctx, [(px - cab_r * 0.45, py - 30 * s), (px - cab_r * 0.05, py - 44 * s)], 7 * s, (1, 1, 1, 0.25))


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

    # sombra en el suelo (más pequeña y suave cuanto más alto salta)
    import escenario
    alto = max(0.0, pies - y0 - 3 * s)
    escenario.sombra_contacto(ctx, x + 6 * s, pies + 4 * s, 120 * s * (1 - min(0.5, alto / (300 * s))),
                              0.30 * (1 - min(0.6, alto / (200 * s))))
    # piernas (detrás del cuerpo)
    for lado, fase in ((-1, 1), (1, -1)):
        a = lado * 6 * (1 - mov) + fase * paso * (34 if corre else 24) * mov      # al andar, las dos van adelante/atrás
        rod = max(0.0, -fase * paso) * (60 if corre else 30) * mov
        fin = _miembro(ctx, (x + lado * 30 * s, cadera_y), alto_pierna * 0.5, alto_pierna * 0.5, a, -rod, 1, 26 * s, PANTALON)
        zx, zy = fin[0] + 12 * s, fin[1]
        piece(ctx, P_rrect(zx - 30 * s, zy - 15 * s, 62 * s, 26 * s, 13 * s), ZAPATO, lw=3, shadow=False)
        line(ctx, [(zx - 22 * s, zy + 6 * s), (zx + 24 * s, zy + 6 * s)], 4 * s, SUELA)   # suela

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
    tronco = P_rrect(x - 72 * s, hombro_y - 8 * s, 144 * s, torso, 44 * s)
    piece(ctx, tronco, CAMISETA, lw=5)
    _volumen(ctx, tronco, 1, 0.18, 0.32)
    piece(ctx, P_rrect(x - 62 * s, cadera_y - 16 * s, 124 * s, 36 * s, 14 * s), PANTALON, lw=4, shadow=False)
    line(ctx, [(x - 56 * s, cadera_y - 8 * s), (x + 56 * s, cadera_y - 8 * s)], 6 * s, hexc("#1a2140"))   # cinturón
    piece(ctx, P_rrect(x - 9 * s, cadera_y - 14 * s, 18 * s, 13 * s, 3 * s), hexc("#d9b44a"), lw=2, shadow=False)  # hebilla
    # cuello: piel en V con el borde de la camiseta
    piece(ctx, P_poly([(x - 30 * s, hombro_y - 6 * s), (x + 30 * s, hombro_y - 6 * s), (x, hombro_y + 30 * s)]), PIEL, lw=4, shadow=False)
    if G.ESTILO not in SIN_VOLUMEN:
        line(ctx, [(x - 34 * s, hombro_y - 8 * s), (x, hombro_y + 34 * s), (x + 34 * s, hombro_y - 8 * s)], 7 * s,
             tuple(c * 0.78 for c in CAMISETA[:3]))
    mano = brazo(1, g[1])
    if gesto == "senala" and k > 0.9:                       # dedo índice
        line(ctx, [mano, (mano[0] + 30 * s, mano[1] - 4 * s)], 9 * s, INK)

    # cabeza: pelo de detrás (largo, coleta), orejas, cara con volumen, pelo de delante
    estilo_pelo = ASPECTO["pelo"]
    if estilo_pelo == "largo":
        piece(ctx, P_rrect(cab[0] - cab_r * 1.08, cab[1] - cab_r * 0.75, cab_r * 2.16, cab_r * 2.05, cab_r * 0.7),
              PELO, lw=4, shadow=False)
    elif estilo_pelo == "coleta":
        piece(ctx, P_ell(cab[0] + cab_r * 1.0, cab[1] + cab_r * 0.15, cab_r * 0.32, cab_r * 0.62), PELO, lw=4, shadow=False)
        piece(ctx, P_ell(cab[0] + cab_r * 0.86, cab[1] - cab_r * 0.42, cab_r * 0.16, cab_r * 0.16), hexc("#e63946"), lw=3,
              shadow=False)
    for lado in (-1, 1):
        piece(ctx, P_ell(cab[0] + lado * cab_r * 0.96, cab[1] + 8 * s, 17 * s, 24 * s), PIEL, lw=4, shadow=False)
    cara = P_ell(cab[0], cab[1], cab_r, cab_r * 0.95)
    piece(ctx, cara, PIEL, lw=5)
    _volumen(ctx, cara, 1, 0.13, 0.3)
    _pelo_delante(ctx, cab, cab_r, s, estilo_pelo)
    parpadeo = pose % 34 in (0, 1)
    dx = mira * 9 * s
    for lado in (-1, 1):
        ex, ey = cab[0] + lado * 34 * s, cab[1] + 2 * s
        if parpadeo:
            line(ctx, [(ex - 13 * s, ey), (ex + 13 * s, ey)], 6 * s, INK)
        else:
            alto = 24 * s if g[2] != "o" else 28 * s
            piece(ctx, P_ell(ex, ey, 15 * s, alto), (1, 1, 1), lw=3, shadow=False)
            piece(ctx, P_ell(ex + dx, ey + 3 * s, 8 * s, 12 * s), INK, lw=0, shadow=False, outline=False)
            piece(ctx, P_ell(ex + dx + 3 * s, ey - 2 * s, 3 * s, 3.5 * s), (1, 1, 1), lw=0, shadow=False, outline=False)
        c = g[3] * k                                        # cejas: + arriba, − caídas, 2 = una levantada
        sube = (12 if c > 0 else 0) * s + (8 * s if (g[3] == 2 and lado == 1) else 0)
        incl = (-8 if g[3] < 0 else (4 if g[3] == 3 else 0)) * s * lado
        line(ctx, [(ex - 16 * s, ey - 30 * s - sube + incl), (ex + 16 * s, ey - 30 * s - sube - incl)], 8 * s, hexc("#24150c"))
    if ASPECTO["barba"] == "si":                            # barba: rodea la boca por debajo
        piece(ctx, P_poly([(cab[0] - cab_r * 0.86, cab[1] + 6 * s), (cab[0] - cab_r * 0.7, cab[1] + cab_r * 0.62),
                           (cab[0] - cab_r * 0.3, cab[1] + cab_r * 0.92), (cab[0] + cab_r * 0.3, cab[1] + cab_r * 0.92),
                           (cab[0] + cab_r * 0.7, cab[1] + cab_r * 0.62), (cab[0] + cab_r * 0.86, cab[1] + 6 * s),
                           (cab[0] + cab_r * 0.5, cab[1] + 34 * s), (cab[0] - cab_r * 0.5, cab[1] + 34 * s)]),
              PELO, lw=4, shadow=False)
        piece(ctx, P_ell(cab[0] + dx * 0.4, cab[1] + 48 * s, 30 * s, 17 * s), PIEL, lw=0, shadow=False, outline=False)
    if ASPECTO["gafas"] == "si":
        for lado in (-1, 1):
            ctx.new_path()
            ctx.arc(cab[0] + lado * 34 * s, cab[1] + 2 * s, 27 * s, 0, 2 * math.pi)
            G.set_col(ctx, (1, 1, 1, 0.12))
            ctx.fill_preserve()
            G.set_col(ctx, INK)
            ctx.set_line_width(7 * s)
            ctx.stroke()
        line(ctx, [(cab[0] - 8 * s, cab[1] - 2 * s), (cab[0] + 8 * s, cab[1] - 2 * s)], 6 * s, INK)
    if G.ESTILO not in SIN_VOLUMEN:                          # mejillas y nariz
        for lado in (-1, 1):
            piece(ctx, P_ell(cab[0] + lado * 58 * s, cab[1] + 34 * s, 16 * s, 9 * s), (*MEJILLA[:3], 0.45), lw=0,
                  shadow=False, outline=False)
        line(ctx, [(cab[0] + 2 * s + dx * 0.4, cab[1] + 14 * s), (cab[0] + 8 * s + dx * 0.4, cab[1] + 26 * s),
                   (cab[0] + dx * 0.4, cab[1] + 28 * s)], 4 * s, (0.55, 0.3, 0.2, 0.7))
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
