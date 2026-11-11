"""
Mapa del mundo con zoom al país del caso (recortes de papel).

Uso en un short (después de definir SCENES):
    from mapa_mundo import con_mapa
    SCENES = con_mapa(SCENES, BLOQUES, pais="ESP", ciudad="MADRID", lon=-3.70, lat=40.42)

Sustituye la primera escena del bloque 2 (el que empieza con «Lugar, año») por: mapamundi → zoom
hasta el país resaltado → chincheta con la ciudad, y después corta a la escena original.
Datos: Natural Earth 1:110m (dominio público), en datos/paises.geojson.
"""
import json
import math
import os

from generar_short import INK, P_ell, P_poly, P_rrect, clamp, ease_io, hexc, lerp, line, piece, set_col
from generar_short_estafas import txt

_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "paises.geojson")
_CACHE = {}

MAR = hexc("#6fa8d6")
TIERRA = hexc("#efe2c0")
TIERRA_BORDE = hexc("#8a7a5a")
RESALTE = hexc("#ffd23f")
DUR_MAPA = 2.6


def _paises():
    if "p" not in _CACHE:
        feats = json.load(open(_DATOS))["features"]
        out = {}
        for f in feats:
            geo = f["geometry"]
            polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
            anillos = [p[0] for p in polys]
            out[f["properties"]["ADM0_A3"]] = anillos
        _CACHE["p"] = out
    return _CACHE["p"]


def _bbox_principal(iso):
    anillos = _paises()[iso]

    def area(r):
        return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2

    r = max(anillos, key=area)
    xs, ys = [p[0] for p in r], [p[1] for p in r]
    return min(xs), min(ys), max(xs), max(ys)


def _proy(lon, lat):
    return (lon + 180.0) * 3.0, (90.0 - lat) * 3.0        # mundo de 1080 x 540 unidades


def dibujar_mapa(ctx, t, pais, ciudad, lon, lat, pose=0):
    """t = segundos desde que aparece el mapa."""
    set_col(ctx, MAR)
    ctx.paint()
    # cámara: del mundo entero al país
    x0, y0, x1, y1 = _bbox_principal(pais)
    cx_w, cy_w = _proy((x0 + x1) / 2, (y0 + y1) / 2)
    ancho = max((x1 - x0) * 3.0, (y1 - y0) * 3.0 * 0.9, 30)
    escala_pais = min(820.0 / ancho, 14.0)
    k = ease_io(clamp((t - 0.35) / 1.25))
    escala = escala_pais ** k                        # zoom exponencial: velocidad constante a la vista
    sx = lerp(cx_w, 540.0, k)                        # el país va en línea recta hacia el centro
    sy = lerp(cy_w + 690.0, 960.0, k)
    ox, oy = sx - cx_w * escala, sy - cy_w * escala

    def P(lo, la):
        x, y = _proy(lo, la)
        return ox + x * escala, oy + y * escala

    lw = 2.0 + 1.5 * k
    for iso, anillos in _paises().items():
        if iso == "ATA":
            continue
        for r in anillos:
            pts = [P(lo, la) for lo, la in r]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if max(xs) < -50 or min(xs) > 1130 or max(ys) < -50 or min(ys) > 1970:
                continue
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.close_path()
            set_col(ctx, RESALTE if iso == pais else TIERRA)
            ctx.fill_preserve()
            set_col(ctx, INK if iso == pais else TIERRA_BORDE)
            ctx.set_line_width(lw * (1.8 if iso == pais else 1.0))
            ctx.stroke()
    # chincheta y nombre de la ciudad
    tp = t - 1.5
    if tp > 0:
        px, py = P(lon, lat)
        s = min(1.0, tp / 0.25)
        bote = 0 if tp > 0.25 else -40 * (1 - s)
        line(ctx, [(px, py), (px, py - 70 * s + bote)], 7, INK)
        piece(ctx, P_ell(px, py - 80 * s + bote, 28 * s), hexc("#e23b3b"), lw=4)
        piece(ctx, P_ell(px - 8 * s, py - 88 * s + bote, 8 * s), (1, 1, 1, 0.7), lw=0, shadow=False, outline=False)
        if tp > 0.3:
            w = 40 + len(ciudad) * 30
            lx = min(max(px, w / 2 + 30), 1080 - w / 2 - 30)
            ly = py + 70 if py < 1300 else py - 190
            piece(ctx, P_rrect(lx - w / 2, ly, w, 76, 14), (1, 1, 1), lw=4)
            txt(ctx, ciudad, lx, ly + 54, 46, INK, anchor="center")


def con_mapa(scenes, bloques, pais, ciudad, lon, lat, bloque=1):
    """Devuelve SCENES con la primera escena del bloque indicado precedida por el mapa."""
    escenas = bloques[bloque]["escenas"]
    cue, clave = escenas[0]
    original = scenes[clave]
    nueva = clave + "__mapa"

    def sc_mapa(ctx, pose, lt, ev):
        if lt < DUR_MAPA:
            dibujar_mapa(ctx, lt, pais, ciudad, lon, lat, pose)
        else:
            original(ctx, pose, lt, ev)

    scenes = dict(scenes)
    scenes[nueva] = sc_mapa
    escenas[0] = (cue, nueva)
    return scenes
