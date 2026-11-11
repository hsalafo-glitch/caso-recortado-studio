"""Escenas de «anuncio de producto» para shorts promocionales: enseñan la web y vídeos reales dentro del vídeo.

Tipos nuevos (se registran en lote14.TIPOS al importar este módulo):
  montaje     cuadrícula de 3×3 shorts reales reproduciéndose, como tarjetas de papel que entran una a una
  telefono    un móvil con la web: el tema se escribe letra a letra, se elige estilo y se pulsa «Crear vídeo»
  progreso    tarjeta de progreso real: Guion → Voz → Animación → Subtítulos, cada paso se marca al decirlo
  resultado   el móvil reproduce un vídeo terminado, con sello «¡LISTO!»
  rejilla     10 vídeos a la vez, uno por estilo visual, con su nombre

Los clips se leen con ffmpeg a 12 fotogramas por segundo (el ritmo de poses del motor) y se guardan en memoria.
"""
import math
import os
import subprocess

import cairo
import numpy as np

import generar_short as g
import lote14
from generar_short import INK, P_ell, P_rrect, clamp, ease_out_back, hexc, line, piece
from generar_short_estafas import since, stamp, txt
import animaciones as A

RAIZ = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}
UI = dict(fondo=hexc("#0f121a"), tarjeta=hexc("#1a1f2e"), borde=hexc("#30374c"), texto=hexc("#eef1f8"),
          suave=hexc("#a3abc2"), acento=hexc("#ff4d5a"), acento2=hexc("#ff8a3d"), ok=hexc("#34d399"), amarillo=hexc("#ffd23f"))


def clip(ruta, inicio, dur, w, h, recorte=1.0):
    """Fotogramas (12/s) de un vídeo como superficies de cairo. recorte < 1 se queda con la parte de arriba
    (para quitar los subtítulos del vídeo original)."""
    clave = (ruta, inicio, dur, w, h, recorte)
    if clave in _CACHE:
        return _CACHE[clave]
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(inicio), "-t", str(dur), "-i", os.path.join(RAIZ, ruta),
                        "-vf", f"fps=12,crop=iw:ih*{recorte}:0:0,scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "bgra", "-"],
                       capture_output=True, check=True)
    n = len(r.stdout) // (w * h * 4)
    datos = np.frombuffer(r.stdout, dtype=np.uint8)[: n * w * h * 4].reshape(n, h, w, 4).copy()
    sups = []
    for i in range(n):
        a = np.ascontiguousarray(datos[i])
        s = cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_ARGB32, w, h, w * 4)
        sups.append((s, a))                      # guardamos el array para que no lo libere la memoria
    _CACHE[clave] = sups
    return sups


def imagen(ruta, w, h):
    clave = ("img", ruta, w, h)
    if clave not in _CACHE:
        from PIL import Image
        im = Image.open(os.path.join(RAIZ, ruta)).convert("RGBA").resize((w, h), Image.LANCZOS)
        a = np.array(im)[:, :, [2, 1, 0, 3]].copy()
        _CACHE[clave] = (cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_ARGB32, w, h, w * 4), a)
    return _CACHE[clave][0]


def pintar(ctx, sup, x, y, w, h, radio=0):
    ctx.save()
    if radio:
        P_rrect(x, y, w, h, radio)(ctx)
        ctx.clip()
    ctx.set_source_surface(sup, x, y)
    ctx.paint()
    ctx.restore()


def fotograma(frames, lt, desfase=0):
    return frames[int((lt * 12) + desfase) % len(frames)][0]


def fuente(ctx, tam, peso=cairo.FONT_WEIGHT_BOLD):
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, peso)
    ctx.set_font_size(tam)


def texto_ui(ctx, s, x, y, tam, col, peso=cairo.FONT_WEIGHT_BOLD, centro=False):
    fuente(ctx, tam, peso)
    e = ctx.text_extents(s)
    ctx.move_to(x - (e.width / 2 + e.x_bearing if centro else 0), y)
    ctx.set_source_rgb(*col[:3])
    ctx.show_text(s)
    return e


def movil(ctx, x, y, w, h):
    """Marco de móvil; devuelve el rectángulo de la pantalla."""
    ctx.save()
    for k, a in ((26, 0.10), (16, 0.14), (8, 0.18)):                     # sombra suave
        P_rrect(x - 14 + k * 0.3, y - 14 + k, w + 28, h + 28, 70)(ctx)
        ctx.set_source_rgba(0, 0, 0, a)
        ctx.fill()
    gr = cairo.LinearGradient(x, y, x + w, y + h)
    gr.add_color_stop_rgb(0, 0.20, 0.23, 0.32)
    gr.add_color_stop_rgb(1, 0.07, 0.08, 0.12)
    P_rrect(x - 14, y - 14, w + 28, h + 28, 70)(ctx)
    ctx.set_source(gr)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.12)
    ctx.set_line_width(3)
    ctx.stroke()
    P_rrect(x, y, w, h, 56)(ctx)
    ctx.set_source_rgb(*UI["fondo"][:3])
    ctx.fill()
    ctx.restore()
    return x, y, w, h


def isla(ctx, x, y, w):
    P_rrect(x + w / 2 - 70, y + 18, 140, 38, 19)(ctx)
    ctx.set_source_rgb(0.02, 0.02, 0.04)
    ctx.fill()


def fondo_promo(ctx, pose, tono="#151a2e"):
    """Fondo oscuro con brillo de color, como la web."""
    ctx.set_source_rgb(*hexc(tono)[:3])
    ctx.paint()
    for cx, cy, r, col, a in ((880, 420, 760, (1, 0.30, 0.35), 0.22), (160, 1500, 700, (0.39, 0.40, 0.95), 0.18)):
        gr = cairo.RadialGradient(cx, cy, 10, cx, cy, r)
        gr.add_color_stop_rgba(0, *col, a)
        gr.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(gr)
        ctx.paint()
    A.ambiente(ctx, pose, 12, (1, 1, 1), 0.06)


# ───────────────────────────── escenas ─────────────────────────────
def sc_montaje(p, i):
    vids = p["videos"][:9]

    def sc(ctx, pose, lt, ev):
        fondo_promo(ctx, pose)
        w, h, gap = 262, 300, 22
        x0, y0 = 540 - (3 * w + 2 * gap) / 2, 515
        for j, v in enumerate(vids):
            fr = clip(v, p.get("inicio", 9), 4, w, h, 0.71)
            x, y = x0 + (j % 3) * (w + gap), y0 + (j // 3) * (h + gap)
            t = lt - 0.12 * j
            ang = math.radians((-4, 3, -2, 2, -3, 4, -1, 3, -4)[j])

            def d(fr=fr, x=x, y=y, ang=ang, j=j):
                ctx.save()
                ctx.translate(x + w / 2, y + h / 2)
                ctx.rotate(ang)
                ctx.translate(-w / 2, -h / 2)
                P_rrect(-8, -8, w + 16, h + 16, 22)(ctx)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
                pintar(ctx, fotograma(fr, lt, j * 5), 0, 0, w, h, 16)
                ctx.restore()
            A.dibujo_animado(ctx, d, x + w / 2, y + h / 2, t, lt, pose, "cae" if j % 2 else "zoom", None, j)
        lote14._stamp(ctx, ev, lt, p.get("st"), 1250)
    return sc


def sc_telefono(p, i):
    tema = p.get("tema", "¿Por qué el cielo es azul?")
    estilos = [("recortes", "Papel"), ("palitos", "Palitos"), ("3d", "3D"), ("neon", "Neón"), ("comic", "Cómic"), ("pixel", "Pixel")]
    elegido = p.get("elegido", 4)

    def sc(ctx, pose, lt, ev):
        fondo_promo(ctx, pose)
        k = A.entrada("sube", lt)[1]
        ctx.save()
        ctx.translate(540, 980 + k)
        ctx.scale(1.13, 1.13)
        ctx.translate(-540, -950)
        x, y, w, h = movil(ctx, 300, 500, 480, 900)
        isla(ctx, x, y, w)
        texto_ui(ctx, "Caso Recortado Studio", x + 40, y + 120, 26, UI["suave"])
        texto_ui(ctx, "¿De qué quieres el vídeo?", x + 40, y + 180, 30, UI["texto"])
        # caja de texto con tecleo
        t_tema = since(ev, "tema", lt)
        n = 0 if t_tema < 0 else min(len(tema), int(t_tema * 16))
        P_rrect(x + 36, y + 210, w - 72, 86, 18)(ctx)
        ctx.set_source_rgb(0.04, 0.05, 0.08)
        ctx.fill_preserve()
        ctx.set_source_rgb(*(UI["acento2"] if 0 <= t_tema else UI["borde"])[:3])
        ctx.set_line_width(3)
        ctx.stroke()
        escrito = tema[:n]
        e = texto_ui(ctx, escrito if n else "Escribe un tema…", x + 60, y + 266, 30, UI["texto"] if n else UI["suave"], cairo.FONT_WEIGHT_NORMAL)
        if t_tema >= 0 and pose % 6 < 3:                                   # cursor
            cx = x + 62 + (e.x_advance if n else 0)
            line(ctx, [(cx, y + 234), (cx, y + 276)], 3, UI["texto"])
        # estilos
        texto_ui(ctx, "Estilo del vídeo", x + 40, y + 360, 26, UI["texto"])
        t_est = since(ev, "estilo", lt)
        for j, (clave, nombre) in enumerate(estilos):
            cw, ch = (w - 72 - 2 * 14) / 3, 150
            ex, ey = x + 36 + (j % 3) * (cw + 14), y + 384 + (j // 3) * (ch + 18)
            sel = t_est >= 0 and j == elegido
            pintar(ctx, imagen(f"web/static/estilo-{clave}.jpg", int(cw), 104), ex, ey, cw, 104, 12)
            P_rrect(ex, ey, cw, ch, 14)(ctx)
            ctx.set_source_rgb(*(UI["acento"] if sel else UI["borde"])[:3])
            ctx.set_line_width(6 if sel else 2)
            ctx.stroke()
            texto_ui(ctx, nombre, ex + cw / 2, ey + 136, 22, UI["texto"] if sel else UI["suave"], centro=True)
            if sel:
                kk = ease_out_back(clamp(t_est / 0.3))
                piece(ctx, P_ell(ex + cw - 18, ey + 18, 18 * kk), UI["acento"], lw=0, shadow=False, outline=False)
        # botón
        t_bot = since(ev, "crear", lt)
        pulsa = 0.94 if 0 <= t_bot < 0.25 else 1.0
        bx, by, bw, bh = x + 36, y + h - 170, w - 72, 96
        ctx.save()
        ctx.translate(bx + bw / 2, by + bh / 2)
        ctx.scale(pulsa, pulsa)
        ctx.translate(-bw / 2, -bh / 2)
        gr = cairo.LinearGradient(0, 0, bw, 0)
        gr.add_color_stop_rgb(0, *UI["acento"][:3])
        gr.add_color_stop_rgb(1, *UI["acento2"][:3])
        P_rrect(0, 0, bw, bh, 20)(ctx)
        ctx.set_source(gr)
        ctx.fill()
        texto_ui(ctx, "Crear vídeo", bw / 2, 62, 34, (1, 1, 1), centro=True)
        ctx.restore()
        if 0 <= t_bot < 0.6:                                                # onda del toque
            r = 30 + 260 * t_bot
            ctx.new_path()
            ctx.arc(bx + bw * 0.62, by + bh / 2, r, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, max(0, 0.45 - t_bot * 0.75))
            ctx.set_line_width(8)
            ctx.stroke()
        ctx.restore()
        lote14._stamp(ctx, ev, lt, p.get("st"), 1440)
    return sc


def sc_progreso(p, i):
    pasos = [("guion", "Escribiendo el guion"), ("voz", "Grabando la voz"), ("anima", "Animando las escenas"), ("subs", "Poniendo subtítulos")]

    def sc(ctx, pose, lt, ev):
        fondo_promo(ctx, pose, "#121726")
        k = A.entrada("zoom", lt)[3]
        ctx.save()
        ctx.translate(540, 960)
        ctx.scale(k, k)
        ctx.translate(-540, -960)
        x, y, w, h = 110, 560, 860, 720
        P_rrect(x, y, w, h, 40)(ctx)
        ctx.set_source_rgb(*UI["tarjeta"][:3])
        ctx.fill_preserve()
        ctx.set_source_rgb(*UI["borde"][:3])
        ctx.set_line_width(3)
        ctx.stroke()
        texto_ui(ctx, p.get("tema", "¿Por qué el cielo es azul?"), x + 56, y + 92, 40, UI["texto"])
        hechos = 0
        for j, (clave, nombre) in enumerate(pasos):
            t = since(ev, clave, lt)
            yy = y + 190 + j * 118
            if t >= 0:
                hechos = j + 1
            fin = since(ev, pasos[j + 1][0], lt) >= 0 if j < 3 else since(ev, "fin", lt) >= 0
            ctx.new_path()
            if t < 0:
                ctx.arc(x + 90, yy, 26, 0, 2 * math.pi)
                ctx.set_source_rgb(*UI["borde"][:3])
                ctx.set_line_width(5)
                ctx.stroke()
                col = UI["suave"]
            elif not fin:                                                       # girando
                a0 = (pose % 12) / 12 * 2 * math.pi
                ctx.new_path()
                ctx.arc(x + 90, yy, 26, a0, a0 + 4.2)
                ctx.set_source_rgb(*UI["amarillo"][:3])
                ctx.set_line_width(7)
                ctx.stroke()
                col = UI["texto"]
            else:
                kk = ease_out_back(clamp(t / 0.3))
                piece(ctx, P_ell(x + 90, yy, 30 * kk), UI["ok"], lw=0, shadow=False, outline=False)
                line(ctx, [(x + 76, yy), (x + 88, yy + 12), (x + 106, yy - 12)], 7, (1, 1, 1))
                col = UI["texto"]
            texto_ui(ctx, nombre, x + 150, yy + 14, 38, col)
        # barra
        bx, by, bw = x + 56, y + h - 90, w - 112
        P_rrect(bx, by, bw, 18, 9)(ctx)
        ctx.set_source_rgb(*UI["borde"][:3])
        ctx.fill()
        frac = clamp(hechos / 4 - (0.12 if hechos < 4 else 0))
        if since(ev, "fin", lt) >= 0:
            frac = 1.0
        gr = cairo.LinearGradient(bx, 0, bx + bw, 0)
        gr.add_color_stop_rgb(0, *UI["acento"][:3])
        gr.add_color_stop_rgb(1, *UI["amarillo"][:3])
        P_rrect(bx, by, max(18, bw * frac), 18, 9)(ctx)
        ctx.set_source(gr)
        ctx.fill()
        ctx.restore()
    return sc


def sc_resultado(p, i):
    def sc(ctx, pose, lt, ev):
        fondo_promo(ctx, pose)
        k = A.entrada("sube", lt)[1]
        ctx.save()
        ctx.translate(0, k)
        x, y, w, h = movil(ctx, 300, 500, 480, 853)
        fr = clip(p["video"], p.get("inicio", 4), 8, 480, 853)
        pintar(ctx, fotograma(fr, lt), x, y, w, h, 56)
        isla(ctx, x, y, w)
        ctx.restore()
        t = since(ev, "listo", lt) if p.get("st") is None else -1
        stamp(ctx, 860, 640, "¡LISTO!", t if t >= 0 else lt - 0.6, 58, col=hexc("#2fb35a"), ang=12)
    return sc


def sc_rejilla(p, i):
    estilos = [("", "Papel"), ("-palitos", "Palitos"), ("-3d", "3D"), ("-plano", "Plano"), ("-neon", "Neón"),
               ("-holograma", "Holograma"), ("-plastilina", "Plastilina"), ("-pixel", "Pixel art"), ("-acuarela", "Acuarela"), ("-comic", "Cómic")]

    def sc(ctx, pose, lt, ev):
        fondo_promo(ctx, pose, "#10131f")
        w, h, gap = 192, 246, 12
        x0, y0 = 540 - (5 * w + 4 * gap) / 2, 620
        for j, (suf, nombre) in enumerate(estilos):
            fr = clip(f"salida/espacio-raro{suf}.mp4", p.get("inicio", 16), p.get("dur", 5), w, h, 0.71)
            x, y = x0 + (j % 5) * (w + gap), y0 + (j // 5) * (h + 70)

            def d(fr=fr, x=x, y=y, nombre=nombre):
                pintar(ctx, fotograma(fr, lt), x, y, w, h, 14)
                P_rrect(x, y, w, h, 14)(ctx)
                ctx.set_source_rgba(1, 1, 1, 0.25)
                ctx.set_line_width(2)
                ctx.stroke()
                texto_ui(ctx, nombre, x + w / 2, y + h + 38, 26, UI["texto"], centro=True)
            A.dibujo_animado(ctx, d, x + w / 2, y + h / 2, lt - 0.09 * j, lt, pose, "pop", None, j)
        lote14._stamp(ctx, ev, lt, p.get("st"), 1420)
    return sc


lote14.TIPOS.update(montaje=sc_montaje, telefono=sc_telefono, progreso=sc_progreso, resultado=sc_resultado, rejilla=sc_rejilla)
