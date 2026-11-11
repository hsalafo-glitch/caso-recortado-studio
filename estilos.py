"""Estilos visuales del vídeo entero. Cambian cómo se dibuja TODO (piezas, líneas, fondos y personas)
sin tocar las escenas:

  recortes   papel recortado (el de siempre): color plano, contorno negro, sombra corta, textura de papel
  palitos    pizarra / cuaderno: fondo blanco, trazo de rotulador a mano y personas de palitos
  3d         volumen tipo juguete o plastilina: piezas con grosor, luz, brillo y sombra suave
  plano      «motion graphics» moderno: colores planos sin contorno, sin sombra ni textura
  neon       fondo negro con contornos de luz de neón
  holograma  proyección azul translúcida con brillo y líneas de escaneo
  plastilina figuras de plastilina: formas blandas, mate, con relieve y grano
  pixel      pixel art de videojuego retro (la imagen se pixela entera)
  acuarela   manchas de acuarela sobre papel con trazo de lápiz
  comic      cómic: contorno negro grueso, sombra dura y tramas de puntos

Se elige con generar_short.ESTILO = "<nombre>" (el guion lo trae en «estilo_visual»).
"""
import math

import cairo

import generar_short as g

ESTILOS = ["recortes", "palitos", "3d", "plano", "neon", "holograma", "plastilina", "pixel", "acuarela", "comic"]
TEXTURA = {"recortes": 0.42, "palitos": 0.18, "plastilina": 0.55, "acuarela": 0.55, "comic": 0.12}
CLAROS = ("palitos", "acuarela")                      # estilos con fondo claro (los textos claros pasan a tinta)
HOLO = (0.35, 0.92, 1.0)


def _rgba(c):
    return tuple(c) if len(c) == 4 else tuple(c) + (1.0,)


def _mezcla(c, d, k):
    r = _rgba(c)
    return tuple(r[i] + (d[i] - r[i]) * k for i in range(3)) + (r[3],)


def _claro(c, k):
    return _mezcla(c, (1, 1, 1), k)


def _oscuro(c, k):
    return _mezcla(c, (0, 0, 0), k)


def _es_tinta(c):
    r = _rgba(c)
    return max(r[:3]) < 0.2


def _set(ctx, c):
    ctx.set_source_rgba(*_rgba(c))


# ───────────────────────────── piezas ─────────────────────────────
def piece(ctx, path, fill, lw=4.0, shadow=True, sh=(5, 7), outline=True):
    e = g.ESTILO
    if e == "palitos":
        oscuro = max(_rgba(fill)[:3]) < 0.25 and not _es_tinta(fill)   # cajas oscuras de etiquetas → papel claro
        f = fill if _es_tinta(fill) else ((0.93, 0.91, 0.86, 1) if oscuro else _claro(fill, 0.55))
        path(ctx)
        _set(ctx, f)
        if outline and lw > 0:
            ctx.fill_preserve()
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_source_rgba(0.08, 0.08, 0.1, 1)
            ctx.set_line_width(max(3.0, lw * 1.25))
            ctx.stroke()
            ctx.save()                     # segundo trazo, algo movido: parece dibujado a mano
            ctx.translate(1.8, -1.2)
            path(ctx)
            ctx.set_source_rgba(0.08, 0.08, 0.1, 0.45)
            ctx.set_line_width(max(1.5, lw * 0.6))
            ctx.stroke()
            ctx.restore()
        else:
            ctx.fill()
        return
    if e == "plano":
        path(ctx)
        _set(ctx, fill)
        ctx.fill()
        return
    if e == "neon":
        c = (0.9, 0.95, 1.0, 1) if _es_tinta(fill) else _claro(fill, 0.15)
        path(ctx)
        ctx.set_source_rgba(c[0], c[1], c[2], 0.16 if outline else 0.55)
        if not outline or lw <= 0:
            ctx.fill()
            return
        ctx.fill_preserve()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        for w, a in ((lw * 5, 0.08), (lw * 3, 0.16), (lw * 1.8, 0.35)):
            ctx.set_source_rgba(c[0], c[1], c[2], a)
            ctx.set_line_width(w)
            ctx.stroke_preserve()
        ctx.set_source_rgba(*_claro(c, 0.6)[:3], 1)
        ctx.set_line_width(max(1.5, lw * 0.7))
        ctx.stroke()
        return
    if e == "holograma":
        c = _mezcla(HOLO + (1,), _rgba(fill)[:3], 0.25)
        path(ctx)
        ctx.set_source_rgba(c[0], c[1], c[2], 0.14 if outline else 0.35)
        if not outline or lw <= 0:
            ctx.fill()
            return
        ctx.fill_preserve()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        for w, a in ((lw * 3.2, 0.12), (lw * 1.6, 0.3)):
            ctx.set_source_rgba(c[0], c[1], c[2], a)
            ctx.set_line_width(w)
            ctx.stroke_preserve()
        ctx.set_source_rgba(0.85, 1, 1, 0.95)
        ctx.set_line_width(max(1.2, lw * 0.5))
        ctx.stroke()
        return
    if e == "plastilina":
        path(ctx)
        x1, y1, x2, y2 = ctx.fill_extents()
        ctx.new_path()
        if x2 - x1 < 1 or y2 - y1 < 1:
            return
        f = _claro(fill, 0.12) if not _es_tinta(fill) else _rgba(fill)
        if shadow:
            for k, a in ((10, 0.08), (6, 0.12)):
                ctx.save(); ctx.translate(k * 0.5, k); path(ctx); ctx.set_source_rgba(0, 0, 0, a); ctx.fill(); ctx.restore()
        if outline and lw >= 3:
            for k in (3, 2, 1):
                ctx.save(); ctx.translate(k * 0.8, k * 1.4); path(ctx); _set(ctx, _oscuro(f, 0.35)); ctx.fill(); ctx.restore()
        cx, cy, r = x1 + (x2 - x1) * 0.35, y1 + (y2 - y1) * 0.3, max(x2 - x1, y2 - y1) * 0.9
        gr = cairo.RadialGradient(cx, cy, r * 0.05, cx, cy, r)
        gr.add_color_stop_rgba(0, *_claro(f, 0.35))
        gr.add_color_stop_rgba(0.5, *f)
        gr.add_color_stop_rgba(1, *_oscuro(f, 0.25))
        path(ctx)
        ctx.set_source(gr)
        if outline and lw > 0:
            ctx.fill_preserve()
            ctx.set_source_rgba(*_oscuro(f, 0.3)[:3], 0.9)
            ctx.set_line_width(lw * 2.2)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke()
        else:
            ctx.fill()
        return
    if e == "pixel":
        if shadow:
            ctx.save(); ctx.translate(8, 8); path(ctx); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill(); ctx.restore()
        path(ctx)
        _set(ctx, fill)
        if outline and lw > 0:
            ctx.fill_preserve()
            ctx.set_source_rgb(0.05, 0.05, 0.08)
            ctx.set_line_width(max(6, lw * 1.6))
            ctx.stroke()
        else:
            ctx.fill()
        return
    if e == "acuarela":
        path(ctx)
        x1, y1, x2, y2 = ctx.fill_extents()
        ctx.new_path()
        tinta = _es_tinta(fill)
        oscuro = max(_rgba(fill)[:3]) < 0.25 and not tinta
        f = (0.2, 0.2, 0.25, 0.85) if tinta else ((0.9, 0.86, 0.78, 1) if oscuro else _rgba(fill))
        semilla = int(x1 * 7 + y1 * 13) % 97
        for k in range(3 if not tinta else 1):                 # capas de agua que no coinciden del todo
            dx = ((semilla * (k + 3)) % 9 - 4) * 1.2
            dy = ((semilla * (k + 5)) % 9 - 4) * 1.2
            ctx.save(); ctx.translate(dx, dy); path(ctx)
            ctx.set_source_rgba(f[0], f[1], f[2], 0.32 if not tinta else f[3]); ctx.fill(); ctx.restore()
        if outline and lw > 0 and not tinta:
            path(ctx)
            ctx.set_source_rgba(*_oscuro(f, 0.25)[:3], 0.35)       # borde de agua más oscuro
            ctx.set_line_width(lw * 1.4)
            ctx.stroke()
            ctx.save(); ctx.translate(1.5, 1); path(ctx)
            ctx.set_source_rgba(0.25, 0.23, 0.28, 0.65)            # trazo de lápiz
            ctx.set_line_width(max(1.2, lw * 0.45))
            ctx.stroke(); ctx.restore()
        return
    if e == "comic":
        path(ctx)
        x1, y1, x2, y2 = ctx.fill_extents()
        ctx.new_path()
        grueso = outline and lw >= 3
        if shadow and grueso:
            ctx.save(); ctx.translate(10, 10); path(ctx); ctx.set_source_rgba(0.05, 0.05, 0.08, 0.85); ctx.fill(); ctx.restore()
        path(ctx)
        _set(ctx, fill)
        ctx.fill()
        if grueso and (x2 - x1) * (y2 - y1) > 900 and not _es_tinta(fill):     # trama de puntos en la zona de sombra
            ctx.save(); path(ctx); ctx.clip()
            ctx.set_source_rgba(*_oscuro(fill, 0.55)[:3], 0.55)
            paso = 14
            xa, ya = x1 + (x2 - x1) * 0.45, y1 + (y2 - y1) * 0.45
            yy = ya
            while yy < y2:
                xx = xa
                while xx < x2:
                    k = min(1.0, ((xx - xa) / max(1, x2 - xa) + (yy - ya) / max(1, y2 - ya)) * 0.6)
                    ctx.new_sub_path(); ctx.arc(xx, yy, 1 + 4.5 * k, 0, 2 * math.pi)
                    xx += paso
                yy += paso
            ctx.fill(); ctx.restore()
        if outline and lw > 0:
            path(ctx)
            ctx.set_source_rgb(0.05, 0.05, 0.08)
            ctx.set_line_width(lw * 2.0 + 2)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke()
        return
    if e == "3d":
        path(ctx)
        x1, y1, x2, y2 = ctx.fill_extents()
        ctx.new_path()
        if x2 - x1 < 1 or y2 - y1 < 1:
            return
        grueso = outline and lw >= 3
        if shadow:                                             # sombra suave
            for k, a in ((16, 0.06), (11, 0.08), (7, 0.1)):
                ctx.save()
                ctx.translate(k * 0.6, k)
                path(ctx)
                ctx.set_source_rgba(0, 0, 0, a)
                ctx.fill()
                ctx.restore()
        if grueso:                                             # grosor (extrusión)
            lado = _oscuro(fill, 0.45)
            for k in range(10, 0, -1):
                ctx.save()
                ctx.translate(k * 1.1, k * 1.8)
                path(ctx)
                _set(ctx, lado)
                ctx.fill()
                ctx.restore()
        grad = cairo.LinearGradient(x1, y1, x1 + (x2 - x1) * 0.3, y2)   # cara con luz desde arriba
        grad.add_color_stop_rgba(0, *_claro(fill, 0.5))
        grad.add_color_stop_rgba(0.55, *_rgba(fill))
        grad.add_color_stop_rgba(1, *_oscuro(fill, 0.18))
        path(ctx)
        ctx.set_source(grad)
        ctx.fill_preserve()
        brillo = grueso and (x2 - x1) < 420 and (y2 - y1) < 520 and (x2 - x1) < 3 * (y2 - y1)
        if grueso:
            ctx.set_source_rgba(*_oscuro(fill, 0.5)[:3], 0.9)
            ctx.set_line_width(max(1.5, lw * 0.45))
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
        if brillo:
            ctx.save()                                         # brillo (solo en piezas compactas)
            ctx.clip()
            w, h = x2 - x1, y2 - y1
            ctx.translate(x1 + w * 0.32, y1 + h * 0.22)
            ctx.scale(max(1, w * 0.28), max(1, h * 0.14))
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.45)
            ctx.fill()
            ctx.restore()
        ctx.new_path()
        return
    g._piece_recortes(ctx, path, fill, lw, shadow, sh, outline)


def line(ctx, pts, lw=4, col=g.INK, cap=cairo.LINE_CAP_ROUND):
    e = g.ESTILO
    def trazo():
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if e == "neon":
        c = (0.9, 0.95, 1.0, 1) if _es_tinta(col) else _claro(col, 0.15)
        for w, a in ((lw * 4, 0.1), (lw * 2.2, 0.22)):
            trazo()
            ctx.set_source_rgba(c[0], c[1], c[2], a)
            ctx.set_line_width(w)
            ctx.stroke()
        trazo()
        ctx.set_source_rgba(*_claro(c, 0.55)[:3], 1)
        ctx.set_line_width(max(1.5, lw * 0.8))
        ctx.stroke()
        return
    if e == "holograma":
        for w, a in ((lw * 3, 0.14), (lw * 1.6, 0.3)):
            trazo(); ctx.set_source_rgba(*HOLO, a); ctx.set_line_width(w); ctx.stroke()
        trazo(); ctx.set_source_rgba(0.85, 1, 1, 0.95); ctx.set_line_width(max(1.2, lw * 0.6)); ctx.stroke()
        return
    if e == "plastilina":
        trazo(); _set(ctx, _oscuro(col, 0.4)); ctx.set_line_width(lw + 4); ctx.stroke()
        trazo(); _set(ctx, col); ctx.set_line_width(lw); ctx.stroke()
        ctx.save(); ctx.translate(-lw * 0.15, -lw * 0.2); trazo()
        ctx.set_source_rgba(*_claro(col, 0.45)[:3], 0.6); ctx.set_line_width(max(1, lw * 0.25)); ctx.stroke(); ctx.restore()
        return
    if e == "acuarela":
        trazo(); c = _rgba(col); ctx.set_source_rgba(c[0], c[1], c[2], 0.75); ctx.set_line_width(lw); ctx.stroke()
        return
    if e in ("comic", "pixel") and not _es_tinta(col):
        trazo(); ctx.set_source_rgb(0.05, 0.05, 0.08); ctx.set_line_width(lw + (6 if e == "comic" else 5)); ctx.stroke()
    if e == "3d" and lw >= 6:
        ctx.save()
        ctx.translate(2, 3)
        trazo()
        _set(ctx, _oscuro(col, 0.45))
        ctx.set_line_width(lw)
        ctx.stroke()
        ctx.restore()
    if e == "palitos" and not _es_tinta(col):
        trazo()
        ctx.set_source_rgba(0.08, 0.08, 0.1, 1)
        ctx.set_line_width(lw + 3)
        ctx.stroke()
    trazo()
    _set(ctx, col)
    ctx.set_line_width(lw)
    ctx.stroke()


# ───────────────────────────── fondos ─────────────────────────────
def fondo(ctx, col, suelo, col_suelo, noche=False, pose=0):
    e = g.ESTILO
    W, H = g.W, g.H
    base = g.hexc(col)
    if e == "holograma":
        ctx.set_source_rgb(0.01, 0.04, 0.09)
        ctx.paint()
        gr = cairo.RadialGradient(W / 2, H * 0.45, 50, W / 2, H * 0.45, H * 0.6)
        gr.add_color_stop_rgba(0, *HOLO, 0.16)
        gr.add_color_stop_rgba(1, *HOLO, 0)
        ctx.set_source(gr); ctx.paint()
        ctx.set_source_rgba(*HOLO, 0.07); ctx.set_line_width(2)
        for x in range(0, W + 1, 72):
            ctx.move_to(x, 0); ctx.line_to(x, H)
        for y in range(0, H + 1, 72):
            ctx.move_to(0, y); ctx.line_to(W, y)
        ctx.stroke()
        if suelo is not None:                                   # base del proyector
            ctx.save(); ctx.translate(W / 2, suelo + 20); ctx.scale(1, 0.18)
            gr = cairo.RadialGradient(0, 0, 10, 0, 0, 480)
            gr.add_color_stop_rgba(0, *HOLO, 0.55); gr.add_color_stop_rgba(1, *HOLO, 0)
            ctx.arc(0, 0, 480, 0, 2 * math.pi); ctx.set_source(gr); ctx.fill(); ctx.restore()
        return
    if e == "acuarela":
        ctx.set_source_rgb(0.965, 0.945, 0.9)
        ctx.paint()
        c = _rgba(g.hexc("#2b3a67") if noche else base)
        for cx, cy, r, a in ((W * 0.3, H * 0.25, 700, 0.30), (W * 0.75, H * 0.45, 600, 0.22), (W * 0.45, H * 0.6, 500, 0.18)):
            gr = cairo.RadialGradient(cx, cy, 30, cx, cy, r)
            gr.add_color_stop_rgba(0, c[0], c[1], c[2], a); gr.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
            ctx.set_source(gr); ctx.paint()
        if suelo is not None:
            s_ = _claro(g.hexc(col_suelo), 0.45)
            ctx.set_source_rgba(s_[0], s_[1], s_[2], 0.3)
            ctx.rectangle(0, suelo, W, H - suelo); ctx.fill()
        return
    if e == "comic":
        c = _claro(g.hexc("#2b3a67") if noche else base, 0.15)
        _set(ctx, c); ctx.paint()
        ctx.set_source_rgba(*_claro(c, 0.3)[:3], 0.5)          # trama de fondo
        for y in range(0, (suelo or H), 26):
            for x in range((y // 26) % 2 * 13, W, 26):
                ctx.new_sub_path(); ctx.arc(x, y, 4, 0, 2 * math.pi)
        ctx.fill()
        if suelo is not None:
            _set(ctx, g.hexc(col_suelo)); ctx.rectangle(0, suelo, W, H - suelo); ctx.fill()
            ctx.set_source_rgb(0.05, 0.05, 0.08); ctx.set_line_width(10); ctx.move_to(0, suelo); ctx.line_to(W, suelo); ctx.stroke()
        return
    if e == "palitos":
        ctx.set_source_rgb(0.97, 0.965, 0.94)
        ctx.paint()
        ctx.set_source_rgba(0.45, 0.6, 0.85, 0.18)          # cuadrícula de cuaderno
        ctx.set_line_width(2)
        for x in range(0, W + 1, 60):
            ctx.move_to(x, 0)
            ctx.line_to(x, H)
        for y in range(0, H + 1, 60):
            ctx.move_to(0, y)
            ctx.line_to(W, y)
        ctx.stroke()
        if suelo is not None:
            ctx.set_source_rgb(0.92, 0.9, 0.85)
            ctx.rectangle(0, suelo, W, H - suelo)
            ctx.fill()
            line(ctx, [(20, suelo + 4), (W * 0.5, suelo - 2), (W - 20, suelo + 3)], 6, g.INK)
        return
    if e == "neon":
        ctx.set_source_rgb(0.03, 0.03, 0.07)
        ctx.paint()
        c = _claro(base, 0.35)
        ctx.set_source_rgba(c[0], c[1], c[2], 0.10)
        ctx.set_line_width(2)
        for x in range(0, W + 1, 90):
            ctx.move_to(x, 0)
            ctx.line_to(x, H)
        for y in range(0, H + 1, 90):
            ctx.move_to(0, y)
            ctx.line_to(W, y)
        ctx.stroke()
        if noche:
            g.stars(ctx, 40, 5, 1300, pose)
        if suelo is not None:
            ctx.set_source_rgb(0.02, 0.02, 0.05)
            ctx.rectangle(0, suelo, W, H - suelo)
            ctx.fill()
            line(ctx, [(0, suelo), (W, suelo)], 5, _claro(base, 0.3))
        return
    if noche:
        base = g.hexc("#141a33")
    if e in ("3d", "plastilina"):
        if e == "plastilina":
            base = _claro(base, 0.12)
        gr = cairo.LinearGradient(0, 0, 0, suelo or H)
        gr.add_color_stop_rgba(0, *_claro(base, 0.22))
        gr.add_color_stop_rgba(1, *_oscuro(base, 0.18))
        ctx.set_source(gr)
        ctx.paint()
        if noche:
            g.stars(ctx, 40, 5, 1300, pose)
        if suelo is not None:
            s = g.hexc(col_suelo)
            gr = cairo.LinearGradient(0, suelo, 0, H)
            gr.add_color_stop_rgba(0, *_claro(s, 0.15))
            gr.add_color_stop_rgba(1, *_oscuro(s, 0.35))
            ctx.set_source(gr)
            ctx.rectangle(0, suelo, W, H - suelo)
            ctx.fill()
            gr = cairo.LinearGradient(0, suelo - 60, 0, suelo)       # sombra de contacto en el horizonte
            gr.add_color_stop_rgba(0, 0, 0, 0, 0)
            gr.add_color_stop_rgba(1, 0, 0, 0, 0.18)
            ctx.set_source(gr)
            ctx.rectangle(0, suelo - 60, W, 60)
            ctx.fill()
        return
    # plano
    _set(ctx, base)
    ctx.paint()
    if noche:
        g.stars(ctx, 40, 5, 1300, pose)
    if suelo is not None:
        _set(ctx, g.hexc(col_suelo) if not noche else g.hexc("#0c1024"))
        ctx.rectangle(0, suelo, W, H - suelo)
        ctx.fill()


# ───────────────────────────── personas ─────────────────────────────
def palito(ctx, x, feet, s, pose=0, k=0):
    """Monigote de palitos (para «palitos» y «neon»)."""
    f = (pose + k) % 6 < 3
    col = g.INK if g.ESTILO == "palitos" else (HOLO if g.ESTILO == "holograma" else g.hexc("#7fe0ff"))
    h = 330 * s
    cabeza = (x, feet - h)
    cadera = (x, feet - h * 0.42)
    cuello = (x, feet - h * 0.78)
    w = 10 * s if g.ESTILO == "palitos" else 7 * s
    line(ctx, [cuello, cadera], w, col)
    for d in (-1, 1):
        line(ctx, [cadera, (x + d * h * 0.16, feet)], w, col)
        line(ctx, [cuello, (x + d * h * 0.2, feet - h * (0.5 if (d > 0) == f else 0.62))], w, col)
    ctx.new_path()
    ctx.arc(cabeza[0], cabeza[1] + h * 0.02, h * 0.13, 0, 2 * math.pi)
    if g.ESTILO == "palitos":
        ctx.set_source_rgb(0.97, 0.965, 0.94)
        ctx.fill_preserve()
    line_w = w
    ctx.set_line_width(line_w)
    _set(ctx, col)
    ctx.stroke()


# ───────────────────────────── efecto final de cada fotograma ─────────────────────────────
def post(surf, ctx, pose):
    """Se aplica a la escena ya dibujada (antes de rótulos y subtítulos)."""
    e = g.ESTILO
    W, H = surf.get_width(), surf.get_height()
    if e == "pixel":
        f = 8
        peq = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // f, H // f)
        c2 = cairo.Context(peq)
        c2.scale(1 / f, 1 / f)
        c2.set_source_surface(surf)
        c2.paint()
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.scale(f, f)
        ctx.set_source_surface(peq)
        ctx.get_source().set_filter(cairo.FILTER_NEAREST)
        ctx.paint()
        ctx.restore()
    elif e == "holograma":
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0.22)
        for y in range(pose % 3 * 2, H, 6):                       # líneas de escaneo
            ctx.rectangle(0, y, W, 2)
        ctx.fill()
        if pose % 29 == 0:                                         # parpadeo de vez en cuando
            ctx.set_source_rgba(*HOLO, 0.08)
            ctx.paint()
        ctx.restore()
