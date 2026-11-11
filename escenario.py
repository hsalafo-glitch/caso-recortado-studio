"""Fondo «de estudio»: el aspecto profesional de los vídeos de motion graphics, sin la raya del suelo.

Capas (de atrás adelante):
  1. degradado vertical del color de la escena (arriba más claro, abajo más oscuro)
  2. luz principal suave detrás del centro de la escena
  3. manchas grandes desenfocadas (profundidad, «bokeh»), que se mueven muy despacio
  4. suelo «infinito»: el fondo se curva hacia el suelo con un degradado, sin línea
  5. foco en el suelo bajo la acción (los dibujos parecen apoyados)
  6. zona de subtítulos que se oscurece poco a poco (se leen mejor) y viñeta en los bordes
"""
import colorsys
import math

import cairo

W, H = 1080, 1920


def _rgb(c):
    return c[:3]


def _mezcla(c, d, k):
    return tuple(c[i] * (1 - k) + d[i] * k for i in range(3))


def _tono(c, dh=0.0, ds=0.0, dl=0.0):
    h, l, s = colorsys.rgb_to_hls(*_rgb(c))
    return colorsys.hls_to_rgb((h + dh) % 1, min(1, max(0, l + dl)), min(1, max(0, s + ds)))


def estudio(ctx, base, suelo=1330, pose=0, noche=False, intensidad=1.0, oscuro_abajo=True):
    """Pinta el fondo de estudio a partir del color base (r, g, b). suelo = altura a la que «apoyan» los dibujos."""
    base = _rgb(base)
    claro = _tono(base, dl=0.10 * intensidad, ds=0.05)
    hondo = _tono(base, dl=-0.16 * intensidad, ds=-0.05)
    # 1. degradado vertical
    gr = cairo.LinearGradient(0, 0, 0, H)
    gr.add_color_stop_rgb(0, *claro)
    gr.add_color_stop_rgb(0.55, *base)
    gr.add_color_stop_rgb(1, *hondo)
    ctx.set_source(gr)
    ctx.paint()
    # 2. luz principal detrás de la escena
    luz = _mezcla(claro, (1, 1, 1), 0.35)
    gr = cairo.RadialGradient(W / 2, 880, 40, W / 2, 880, 820)
    gr.add_color_stop_rgba(0, *luz, 0.42 * intensidad)
    gr.add_color_stop_rgba(0.55, *luz, 0.12 * intensidad)
    gr.add_color_stop_rgba(1, *luz, 0)
    ctx.set_source(gr)
    ctx.paint()
    # 3. manchas desenfocadas de color vecino (dan profundidad sin distraer)
    vecino = _tono(base, dh=0.08, dl=0.12, ds=0.1)
    otro = _tono(base, dh=-0.07, dl=0.06, ds=0.08)
    for i, (cx, cy, r, col, a) in enumerate(((150, 360, 330, vecino, 0.22), (940, 520, 260, otro, 0.18),
                                              (880, 1120, 360, vecino, 0.12), (120, 1000, 220, otro, 0.14))):
        cx += 18 * math.sin(pose / 40 + i * 1.7)
        cy += 14 * math.cos(pose / 46 + i * 2.3)
        gr = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
        gr.add_color_stop_rgba(0, *col, a * intensidad)
        gr.add_color_stop_rgba(0.6, *col, a * 0.45 * intensidad)
        gr.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(gr)
        ctx.paint()
    if noche:
        _estrellas(ctx, pose)
    if suelo is not None:
        # 4. suelo infinito: el fondo «se dobla» hacia el suelo con un degradado (sin borde)
        piso = _tono(base, dl=-0.10, ds=-0.04)
        gr = cairo.LinearGradient(0, suelo - 180, 0, suelo + 120)
        gr.add_color_stop_rgba(0, *piso, 0)
        gr.add_color_stop_rgba(0.6, *piso, 0.55)
        gr.add_color_stop_rgba(1, *piso, 0.85)
        ctx.set_source(gr)
        ctx.rectangle(0, suelo - 180, W, H - suelo + 180)
        ctx.fill()
        # 5. foco en el suelo bajo la acción
        ctx.save()
        ctx.translate(W / 2, suelo + 10)
        ctx.scale(1, 0.16)
        gr = cairo.RadialGradient(0, 0, 10, 0, 0, 520)
        gr.add_color_stop_rgba(0, *luz, 0.38 * intensidad)
        gr.add_color_stop_rgba(1, *luz, 0)
        ctx.arc(0, 0, 520, 0, 2 * math.pi)
        ctx.set_source(gr)
        ctx.fill()
        ctx.restore()
    # 6. zona de subtítulos (oscurece poco a poco) y viñeta
    if oscuro_abajo:
        gr = cairo.LinearGradient(0, 1380, 0, H)
        gr.add_color_stop_rgba(0, 0, 0, 0, 0)
        gr.add_color_stop_rgba(0.35, 0, 0, 0, 0.28)
        gr.add_color_stop_rgba(1, 0, 0, 0, 0.5)
        ctx.set_source(gr)
        ctx.rectangle(0, 1380, W, H - 1380)
        ctx.fill()
    vineta(ctx, 0.32 * intensidad)


def vineta(ctx, fuerza=0.3):
    ctx.save()
    ctx.translate(W / 2, H * 0.47)
    ctx.scale(1, H / W)
    gr = cairo.RadialGradient(0, 0, W * 0.42, 0, 0, W * 0.78)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0)
    gr.add_color_stop_rgba(1, 0, 0, 0, fuerza)
    ctx.set_source(gr)
    ctx.arc(0, 0, W * 0.9, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def _estrellas(ctx, pose):
    for i in range(46):
        x = ((i * 7919) % 1013) / 1013 * W                  # repartidas sin formar líneas
        y = 40 + ((i * 104729 + 31) % 997) / 997 * 1100
        r = 1.6 + (i * 7) % 4 * 0.9
        a = 0.35 + 0.45 * (0.5 + 0.5 * math.sin(pose / 5 + i))
        ctx.new_path()
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.95, a)
        ctx.fill()


def sombra_contacto(ctx, x, y, ancho, fuerza=0.32):
    """Sombra suave en el suelo bajo un dibujo o un personaje (sustituye a la línea del suelo)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.22)
    gr = cairo.RadialGradient(0, 0, 2, 0, 0, ancho)
    gr.add_color_stop_rgba(0, 0, 0, 0, fuerza)
    gr.add_color_stop_rgba(0.7, 0, 0, 0, fuerza * 0.35)
    gr.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.new_path()
    ctx.arc(0, 0, ancho, 0, 2 * math.pi)
    ctx.set_source(gr)
    ctx.fill()
    ctx.restore()
