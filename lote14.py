"""Lote de 14 shorts con escenas genéricas. Cada short_l_<slug>.py hace: from lote14 import cargar; globals().update(cargar("<slug>"))"""
import math
import os

import cairo

import generar_short as g
from generar_short import INK, P_ell, P_poly, P_rect, P_rrect, card_text, clamp, draw_text, ease_io, ease_out_back, hexc, lerp, line, piece, rot, set_col
from generar_short_estafas import since, stamp, txt
from generar_marca import magnifier
from mapa_mundo import con_mapa
import iconos
import animaciones as A
import estilos as A_est
import personaje as PJ
from piezas_casos import ORO, ROJO, VERDE_BILLETE, avion_lado, billetes_fajo, fondo, marco, noche, retrato, silueta
from short_robo_siglo import saco
from short_hatton import taladro

VERDE, AZUL, AMAR, MOR = hexc("#2fb35a"), hexc("#1d4ed8"), hexc("#ffe14d"), hexc("#7b4dff")
FONDOS = ["#2d3557", "#3a3150", "#2f3c5a", "#4a3a5a", "#3a3f55"]
FONDOS_DIA = ["#4f8fd6", "#3fa58a", "#d9884a", "#7b6ad6", "#d6627a"]   # temas alegres (ciencia, curiosidades...)


def _fondo(ctx, pose, p, i):
    if p.get("noche"):
        noche(ctx, pose, suelo=1330)
    elif p.get("dia"):
        fondo(ctx, FONDOS_DIA[i % 5], 1330, "#2b3150")
    else:
        fondo(ctx, p.get("fondo", FONDOS[i % 5]), 1330, "#1d2440")
    if not p.get("noche") and g.ESTILO not in ("pixel", "palitos", "acuarela"):
        A.ambiente(ctx, pose)


# ─────────────────────────── iconos ───────────────────────────
def icono(ctx, k, x, y, s, pose=0):
    if k in iconos.DIBUJOS:          # biblioteca general (cualquier tema)
        return iconos.dibujar(ctx, k, x, y, s * 0.75, pose)   # son algo más grandes que los de casos
    if k == "joya":
        piece(ctx, P_poly([(x - 120 * s, y - 40 * s), (x - 60 * s, y - 110 * s), (x + 60 * s, y - 110 * s), (x + 120 * s, y - 40 * s), (x, y + 130 * s)]), hexc("#7fd6ff"), lw=5)
        line(ctx, [(x - 120 * s, y - 40 * s), (x + 120 * s, y - 40 * s)], 4, hexc("#3a8fbf"))
        line(ctx, [(x - 40 * s, y - 40 * s), (x, y + 130 * s), (x + 40 * s, y - 40 * s)], 3, hexc("#3a8fbf"))
    elif k == "corona":
        piece(ctx, P_poly([(x - 150 * s, y + 60 * s), (x - 150 * s, y - 70 * s), (x - 80 * s, y), (x, y - 110 * s), (x + 80 * s, y), (x + 150 * s, y - 70 * s), (x + 150 * s, y + 60 * s)]), ORO, lw=5)
        for dx in (-80, 0, 80):
            piece(ctx, P_ell(x + dx * s, y + 25 * s, 16 * s), hexc("#e23b3b") if dx else hexc("#2f8fd6"), lw=3, shadow=False)
    elif k == "saco":
        saco(ctx, x, y, 1.3 * s)
    elif k == "oro":
        for r in range(3):
            for c in range(3 - r):
                bx, by = x - 110 * s + c * 110 * s + r * 55 * s, y + 60 * s - r * 55 * s
                piece(ctx, P_poly([(bx - 50 * s, by + 25 * s), (bx + 50 * s, by + 25 * s), (bx + 35 * s, by - 25 * s), (bx - 35 * s, by - 25 * s)]), ORO, lw=4)
    elif k == "cuadro":
        marco(ctx, x - 150 * s, y - 190 * s, 300 * s, 380 * s, retrato, borde=28 * s)
    elif k == "grito":
        def grito(c, xx, yy, w, h):
            set_col(c, hexc("#e8743a"))
            c.paint()
            for i in range(5):
                line(c, [(xx, yy + h * (0.1 + i * 0.07)), (xx + w, yy + h * (0.15 + i * 0.07))], 6, hexc("#d94a2a") if i % 2 else hexc("#f2b33a"))
            piece(c, P_rect(xx, yy + h * 0.5, w, h), hexc("#2f5f88"), lw=0, shadow=False, outline=False)
            piece(c, P_ell(xx + w * 0.5, yy + h * 0.55, w * 0.16, h * 0.15), hexc("#e8d9a0"), lw=2, shadow=False)
            piece(c, P_ell(xx + w * 0.5, yy + h * 0.6, w * 0.04, h * 0.05), INK, lw=0, shadow=False, outline=False)
        marco(ctx, x - 150 * s, y - 190 * s, 300 * s, 380 * s, grito, borde=28 * s)
    elif k == "trofeo":
        piece(ctx, P_poly([(x - 90 * s, y - 150 * s), (x + 90 * s, y - 150 * s), (x + 50 * s, y + 20 * s), (x - 50 * s, y + 20 * s)]), ORO, lw=5)
        for d in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(x + d * 100 * s, y - 90 * s, 40 * s, 0, 2 * math.pi)
            set_col(ctx, INK)
            ctx.set_line_width(8 * s)
            ctx.stroke()
        piece(ctx, P_rect(x - 25 * s, y + 20 * s, 50 * s, 70 * s), ORO, lw=4)
        piece(ctx, P_rect(x - 80 * s, y + 90 * s, 160 * s, 50 * s), hexc("#5a3820"), lw=4)
    elif k == "billetes":
        for i in range(3):
            billetes_fajo(ctx, x - 120 * s + i * 120 * s, y + (i % 2) * 30 * s, 1.1 * s)
    elif k == "carta":
        piece(ctx, P_rect(x - 160 * s, y - 100 * s, 320 * s, 200 * s), (1, 1, 1), lw=5)
        line(ctx, [(x - 160 * s, y - 100 * s), (x, y + 10 * s), (x + 160 * s, y - 100 * s)], 4, INK)
        piece(ctx, P_rect(x + 90 * s, y - 85 * s, 55 * s, 65 * s), hexc("#e23b3b"), lw=3, shadow=False)
    elif k == "tren":
        piece(ctx, P_rrect(x - 260 * s, y - 120 * s, 520 * s, 200 * s, 20 * s), hexc("#2f6b45"), lw=5)
        for i in range(4):
            piece(ctx, P_rect(x - 220 * s + i * 120 * s, y - 90 * s, 80 * s, 70 * s), hexc("#bfe3f2"), lw=3, shadow=False)
        for i in range(4):
            piece(ctx, P_ell(x - 190 * s + i * 125 * s, y + 90 * s, 34 * s), INK, lw=3, shadow=False)
        txt(ctx, "CORREO", x, y + 50 * s, 34 * s, (1, 1, 1), anchor="center")
    elif k == "avion":
        avion_lado(ctx, x, y, 0.9 * s)
    elif k == "carrito":
        piece(ctx, P_rect(x - 150 * s, y - 120 * s, 300 * s, 200 * s), hexc("#c9ccd6"), lw=5)
        for i in range(4):
            piece(ctx, P_ell(x - 100 * s + i * 65 * s, y - 120 * s, 40 * s, 25 * s), (1, 1, 1), lw=3, shadow=False)
        for d in (-1, 1):
            piece(ctx, P_ell(x + d * 110 * s, y + 110 * s, 28 * s), INK, lw=3, shadow=False)
    elif k == "taladro":
        taladro(ctx, x - 100 * s, y + 60 * s, 1.0 * s, pose)
    elif k == "nota":
        with rot(ctx, x, y, math.radians(-5)):
            piece(ctx, P_rect(x - 170 * s, y - 120 * s, 340 * s, 240 * s), hexc("#fbf6e8"), lw=5)
            for i in range(4):
                line(ctx, [(x - 130 * s, y - 60 * s + i * 45 * s), (x + 130 * s, y - 60 * s + i * 45 * s)], 5, hexc("#1d3a8a"))
    elif k == "edificio":
        piece(ctx, P_rect(x - 260 * s, y - 260 * s, 520 * s, 420 * s), hexc("#e3e6ec"), lw=5)
        piece(ctx, P_poly([(x - 290 * s, y - 260 * s), (x + 290 * s, y - 260 * s), (x, y - 380 * s)]), hexc("#cfd5df"), lw=5)
        for i in range(4):
            piece(ctx, P_rect(x - 220 * s + i * 120 * s, y - 210 * s, 40 * s, 340 * s), (1, 1, 1), lw=3, shadow=False)
    elif k == "rejas":
        for i in range(7):
            line(ctx, [(x - 270 * s + i * 90 * s, y - 280 * s), (x - 270 * s + i * 90 * s, y + 280 * s)], 14 * s, hexc("#2b2d33"))
        line(ctx, [(x - 290 * s, y - 240 * s), (x + 290 * s, y - 240 * s)], 16 * s, hexc("#2b2d33"))
    elif k == "camion":
        piece(ctx, P_rect(x - 250 * s, y - 150 * s, 330 * s, 200 * s), hexc("#c9ccd6"), lw=5)
        piece(ctx, P_poly([(x + 80 * s, y + 50 * s), (x + 80 * s, y - 100 * s), (x + 170 * s, y - 100 * s), (x + 230 * s, y - 20 * s), (x + 230 * s, y + 50 * s)]), hexc("#e23b3b"), lw=5)
        for wx in (-170, 0, 160):
            piece(ctx, P_ell(x + wx * s, y + 60 * s, 40 * s), INK, lw=3, shadow=False)
    elif k == "graficas":
        piece(ctx, P_rect(x - 200 * s, y - 150 * s, 400 * s, 300 * s), (1, 1, 1), lw=5)
        line(ctx, [(x - 170 * s, y + 110 * s), (x - 80 * s, y + 20 * s), (x, y + 50 * s), (x + 90 * s, y - 60 * s), (x + 170 * s, y - 120 * s)], 10 * s, VERDE)
    elif k == "lupa":
        magnifier(ctx, x, y, 130 * s, math.radians(-30))


# ─────────────────────────── escenas genéricas ───────────────────────────
def _stamp(ctx, ev, lt, st, y=1230):
    if st:
        key, texto, col = (st + (ROJO,))[:3]
        col = hexc("#d97a00") if col == AMAR else col
        t = since(ev, key, lt) if key else lt - 0.8
        if t >= 0:
            stamp(ctx, 540, y, texto, t, 56, col=col, ang=-6)


def _ico(ctx, p, ic, x, y, s, t, lt, pose, j=0, mov=None):
    """Un dibujo con la entrada y el movimiento que pida la escena (p['entrada'], p['movimiento'])."""
    A.dibujo_animado(ctx, lambda: icono(ctx, ic, x, y, s, pose), x, y, t, lt, pose,
                     p.get("entrada", "pop"), p.get("movimiento", mov), j)


def _num(v):
    return f"{v:,.0f}".replace(",", ".") if abs(v) >= 100 else (f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}".replace(".", ","))


def sc_icono(p, i):
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        icos = p["ico"] if isinstance(p["ico"], list) else [p["ico"]]
        for j, ic in enumerate(icos):
            x = 540 + (j - (len(icos) - 1) / 2) * (900 / max(1, len(icos)))
            sc_ = p.get("s", 1.6) / (1 + 0.35 * (len(icos) - 1))
            _ico(ctx, p, ic, x, 870 if p.get("label") else 920, sc_, lt - j * 0.25, lt, pose, j)
        if p.get("label"):
            piece(ctx, P_rrect(240, 1170 - 140, 600, 90, 14), hexc("#1d2433"), lw=4)
            txt(ctx, p["label"], 540, 1090, 46, AMAR, anchor="center")
        _stamp(ctx, ev, lt, p.get("st"), 1250)
    return sc


def sc_siluetas(p, i):
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        if p.get("ico"):
            _ico(ctx, p, p["ico"], 540, 760, 0.9, lt, lt, pose)
        n = p.get("n", 3)
        for j in range(n):
            x = 540 + (j - (n - 1) / 2) * min(240, 900 / max(1, n))
            A.dibujo_animado(ctx, lambda x=x, j=j: silueta(ctx, x, 1330, 0.9 if n < 5 else 0.7, pose, j), x, 1100,
                             lt - j * 0.15, lt, pose, p.get("entrada", "aparece"), None, j)
            if p.get("cada"):
                stamp(ctx, x, 1010, p["cada"], lt - 0.6 - j * 0.15, 30, col=ROJO, ang=-8 + (j % 3) * 6)
        _stamp(ctx, ev, lt, p.get("st"), 600)
    return sc


def sc_contador(p, i):
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        _ico(ctx, p, p.get("ico", "billetes"), 540, 820, 1.2, lt, lt, pose)
        v = p["valor"] * ease_io(clamp(lt / 1.4))
        s = f"{v:,.0f}".replace(",", ".") if p["valor"] >= 100 else f"{v:.1f}".replace(".", ",")
        piece(ctx, P_rrect(140, 1080, 800, 150, 20), hexc("#1d2433"), lw=5)
        txt(ctx, f"{s} {p.get('u', '')}", 540, 1180, 70 if len(p.get("u", "")) < 10 else 56, hexc("#9fd6a0"), anchor="center")
        _stamp(ctx, ev, lt, p.get("st"), 620)
    return sc


def sc_carcel(p, i):
    def sc(ctx, pose, lt, ev):
        fondo(ctx, "#5b6475", 1330, "#3d3f4a")
        if not p.get("vacia"):
            silueta(ctx, 540, 1320, 1.2, pose)
        else:
            piece(ctx, P_ell(700, 1300, 90, 30), hexc("#1a1d24"), lw=3, shadow=False)
        A.dibujo_animado(ctx, lambda: icono(ctx, "rejas", 540, 930, 1.3), 540, 930, lt, lt, pose, p.get("entrada", "cae"))
        _stamp(ctx, ev, lt, p.get("st"), 700)
    return sc


def sc_pregunta(p, i):
    def sc(ctx, pose, lt, ev):
        if p.get("dia"):
            _fondo(ctx, pose, p, i)
        else:
            fondo(ctx, p.get("fondo", "#1d1a2e"), 1330, "#141223")
        if p.get("ico"):
            _ico(ctx, p, p["ico"], 540, 1060, 1.0, lt, lt, pose)
        bob = (pose // 4) % 2 * 10
        draw_text(ctx, "?", 540, 600 - bob, 200, AMAR, INK, 9)
        k = ease_io(clamp((lt - 0.5) / 0.6))
        magnifier(ctx, lerp(1000, 780, k), lerp(1400, 1150, k), 110, math.radians(-30))
        _stamp(ctx, ev, lt, p.get("st"), 1250)
    return sc


def _etiqueta(ctx, texto, x, y, w=400):
    piece(ctx, P_rrect(x - w / 2, y - 45, w, 90, 14), hexc("#1d2433"), lw=4)
    txt(ctx, texto, x, y + 16, 42 if len(texto) < 14 else 34, AMAR, anchor="center")


def sc_comparar(p, i):
    """Dos cosas frente a frente: ico (izquierda) VS ico2 (derecha)."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        for j, (ic, lab) in enumerate(((p["ico"], p.get("label")), (p.get("ico2", "cruz"), p.get("label2")))):
            t = lt - j * 0.35
            x = 290 if j == 0 else 790
            _ico(ctx, p, ic, x, 880, 1.25, t, lt, pose, j)
            if lab and t >= 0:
                _etiqueta(ctx, lab, x, 1130, 420)
        if lt > 0.5:
            A.dibujo_animado(ctx, lambda: (piece(ctx, P_ell(540, 880, 70), hexc("#e63946"), lw=5),
                                           txt(ctx, "VS", 540, 900, 56, (1, 1, 1), anchor="center")), 540, 880, lt - 0.5, lt, pose, "pop")
        _stamp(ctx, ev, lt, p.get("st"), 1250)
    return sc


def sc_proceso(p, i):
    """Pasos encadenados: ico → ico2 → ico3 (aparecen uno tras otro)."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        icos = [c for c in (p["ico"], p.get("ico2"), p.get("ico3")) if c]
        n = len(icos)
        xs = [540 + (j - (n - 1) / 2) * (345 if n == 3 else 450) for j in range(n)]
        for j, ic in enumerate(icos):
            t = lt - j * 0.6
            _ico(ctx, p, ic, xs[j], 900, 0.72 if n == 3 else 1.1, t, lt, pose, j)
            if j and t >= 0:
                xa = (xs[j - 1] + xs[j]) / 2
                piece(ctx, P_poly([(xa - 30, 888), (xa + 2, 888), (xa + 2, 868), (xa + 32, 900), (xa + 2, 932), (xa + 2, 912), (xa - 30, 912)]), AMAR, lw=4)
        if p.get("label"):
            _etiqueta(ctx, p["label"], 540, 1140, 640)
        _stamp(ctx, ev, lt, p.get("st"), 1260)
    return sc


COLS_BARRA = ["#ffd23f", "#2fb35a", "#e63946", "#7fc8f8"]


def sc_lista(p, i):
    """Top 3-4: filas numeradas que aparecen una tras otra (items: [{ico, texto}])."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        items = p.get("items", [])[:4]
        paso = 190 if len(items) == 4 else 240
        y0 = (965 if len(items) == 4 else 1010) - paso * (len(items) - 1) / 2
        for j, it in enumerate(items):
            t = lt - j * p.get("cada_s", 0.8)
            y = y0 + j * paso

            def fila(it=it, j=j, y=y):
                piece(ctx, P_rrect(90, y - 85, 900, 170, 24), hexc("#1d2433"), lw=5)
                piece(ctx, P_ell(170, y, 52), hexc(COLS_BARRA[j % 4]), lw=4)
                txt(ctx, str(j + 1), 170, y + 22, 64, INK, anchor="center")
                if it.get("ico"):
                    icono(ctx, it["ico"], 335, y, 0.62, pose)
                tx = it.get("texto", "")
                txt(ctx, tx, 450 if it.get("ico") else 260, y + 18, 54 if len(tx) < 14 else (44 if len(tx) < 18 else 38), (1, 1, 1))
            A.dibujo_animado(ctx, fila, 540, y, t, lt, pose, p.get("entrada", "desliza"), p.get("movimiento"), j)
        _stamp(ctx, ev, lt, p.get("st"), 1300)
    return sc


def sc_barras(p, i):
    """Gráfica de barras que crecen (items: [{texto, valor}]; u = unidad)."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        items = p.get("items", [])[:4]
        n = max(1, len(items))
        vmax = max([abs(it.get("valor") or 0) for it in items] + [1e-9])
        base, alto, ancho = 1230, 520, min(190, 760 / n)
        line(ctx, [(110, base), (970, base)], 8)
        for j, it in enumerate(items):
            x = 540 + (j - (n - 1) / 2) * (860 / n)
            k = _rebote_b(clamp((lt - j * 0.3) / 0.9))
            v = it.get("valor") or 0
            h = max(6, alto * abs(v) / vmax * k)
            piece(ctx, P_rect(x - ancho / 2, base - h, ancho, h), hexc(COLS_BARRA[j % 4]), lw=5)
            if k > 0.05:
                txt(ctx, _num(v * min(1, k)) + (" " + p["u"] if p.get("u") else ""), x, base - h - 30, 46 if n < 4 else 38, (1, 1, 1), anchor="center")
            tx = it.get("texto", "")
            txt(ctx, tx, x, base + 66, 50 if len(tx) < 9 else 40, AMAR, anchor="center")
        _stamp(ctx, ev, lt, p.get("st"), 560)
    return sc


def _rebote_b(x):
    return 0 if x <= 0 else (1 if x >= 1 else 1 - (1 - x) ** 3 + 0.08 * math.sin(x * math.pi) * (1 - x) * 3)


def sc_linea(p, i):
    """Línea del tiempo: hitos que aparecen de izquierda a derecha (items: [{texto: año, ico}])."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        items = p.get("items", [])[:4]
        n = max(1, len(items))
        xs = [540 + (j - (n - 1) / 2) * (820 / n) for j in range(n)]
        k = ease_io(clamp(lt / (0.7 * n)))
        line(ctx, [(110, 960), (110 + 860 * k, 960)], 14)
        line(ctx, [(110, 960), (110 + 860 * k, 960)], 7, AMAR)
        for j, it in enumerate(items):
            t = lt - 0.25 - j * 0.7
            if t < 0:
                continue
            x = xs[j]
            A.dibujo_animado(ctx, lambda x=x: piece(ctx, P_ell(x, 960, 26), hexc("#e63946"), lw=5), x, 960, t, lt, pose, "pop")

            def hito(it=it, x=x, j=j):
                card_text(ctx, it.get("texto", ""), x, 810, 62 if n < 4 else 50, hexc("#1d4ed8"), (1, 1, 1), math.radians(-3 if j % 2 else 3), 1.0)
                if it.get("ico"):
                    icono(ctx, it["ico"], x, 1140, 0.7 if n < 4 else 0.55, pose)
            A.dibujo_animado(ctx, hito, x, 960, t, lt, pose, p.get("entrada", "sube"), p.get("movimiento"), j)
        _stamp(ctx, ev, lt, p.get("st"), 1320)
    return sc


def _bocadillo(ctx, texto, x, y, t, cola_x):
    """Bocadillo de cómic que aparece con «pop»; la cola apunta hacia cola_x."""
    if t < 0:
        return
    w = min(900, max(340, 80 + len(texto) * 40))

    def d():
        piece(ctx, P_poly([(cola_x + 10, y + 150), (x - 40, y + 60), (x + 30, y + 60)]), (1, 1, 1), lw=5)
        piece(ctx, P_rrect(x - w / 2, y - 70, w, 140, 44), (1, 1, 1), lw=5)
        piece(ctx, P_poly([(cola_x + 12, y + 140), (x - 34, y + 64), (x + 24, y + 64)]), (1, 1, 1), lw=0, shadow=False, outline=False)
        txt(ctx, texto, x, y + 22, 66 if len(texto) < 13 else 52, INK, anchor="center")
    A.dibujo_animado(ctx, d, x, y, t, t, 0, "pop")


def sc_personaje(p, i):
    """El narrador entra andando, hace un gesto y, si se pide, muestra un dibujo y dice algo en un bocadillo."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        con_ico = bool(p.get("ico"))
        x = 330 if con_ico else 540
        if con_ico:
            _ico(ctx, p, p["ico"], 800, 940, 1.2, lt - PJ.ENTRA - 0.15, lt, pose, 1)
        if p.get("sofa"):                                   # sentado en el sofá: no entra andando
            PJ.sofa(ctx, x, 1318, 1.5, "detras")
            PJ.dibujar(ctx, x, 1318, 1.5, p.get("gesto", "explica"), max(lt + PJ.ENTRA + p.get("ya", 0.3), 0), pose,
                       mira=1 if con_ico else 0)
            PJ.sofa(ctx, x, 1318, 1.5, "delante")
            if p.get("manta"):
                PJ.sofa(ctx, x, 1318, 1.5, "manta")
        else:
            PJ.dibujar(ctx, x, 1318, 1.5, p.get("gesto", "explica"), lt, pose, mira=1 if con_ico else 0)
        if p.get("bocadillo"):
            _bocadillo(ctx, p["bocadillo"], 540 if not con_ico else 560, 585, lt - PJ.ENTRA - 0.2, x + 70)
        _stamp(ctx, ev, lt, p.get("st"), 1265 if p.get("bocadillo") else 600)
    return sc


COLS_TEXTO = ["#ffffff", "#ffd23f", "#ff4d5a", "#7fc8f8"]


def sc_texto(p, i):
    """Texto cinético: 1-4 líneas enormes que entran una tras otra, cada una con su golpe."""
    def sc(ctx, pose, lt, ev):
        _fondo(ctx, pose, p, i)
        lineas = [str(x) for x in p.get("lineas", [])][:4]
        n = max(1, len(lineas))
        paso = min(250, 760 / n)
        y0 = 930 - paso * (n - 1) / 2
        entradas = ("zoom", "desliza", "sube", "cae")
        for j, tx in enumerate(lineas):
            t = lt - j * p.get("cada_s", 0.42)
            if t < 0:
                continue
            size = min(230, 1500 / max(4, len(tx)), paso * 0.86)
            ultimo = j == n - 1 and n > 1
            col = hexc(COLS_TEXTO[1] if ultimo else COLS_TEXTO[0 if j % 2 == 0 else 3])
            y = y0 + j * paso

            def d(tx=tx, size=size, col=col, y=y, j=j):
                with rot(ctx, 540, y, math.radians((-3, 2, -2, 3)[j % 4])):
                    draw_text(ctx, tx, 540, y, size, col, INK, max(8, size * 0.09))
            A.dibujo_animado(ctx, d, 540, y, t, lt, pose, p.get("entrada") or entradas[j % 4],
                             p.get("movimiento") or ("late" if ultimo else None), j)
        _stamp(ctx, ev, lt, p.get("st"), 1280)
    return sc


TIPOS = dict(personaje=sc_personaje, texto=sc_texto, comparar=sc_comparar, proceso=sc_proceso, icono=sc_icono, siluetas=sc_siluetas, contador=sc_contador,
             carcel=sc_carcel, pregunta=sc_pregunta, lista=sc_lista, barras=sc_barras, linea=sc_linea)


# ─────────────────────────── los 14 casos ───────────────────────────
C = {}


def caso(slug, titulo, mapa, bloques, pron=None):
    C[slug] = dict(titulo=titulo, mapa=mapa, bloques=bloques, pron=pron or {})


caso("joyas-louvre", ("7 MINUTOS", "EN EL LOUVRE", "¡88 MILLONES!"), ("FRA", "PARÍS", 2.35, 48.86), [
    ("¿Qué pensarías si te dijera que robaron las joyas de la corona francesa del Louvre… en solo siete minutos?",
     [(None, "icono", dict(ico="corona", st=("siete", "7 MINUTOS")))], [("joyas", "LAS JOYAS DE LA CORONA"), ("siete minutos", "¿EN 7 MINUTOS?")], {"siete": "siete minutos"}),
    ("París, octubre de 2025. A plena luz del día, unos ladrones aparcan junto al museo un camión con una plataforma elevadora y suben hasta una ventana.",
     [(None, "icono", dict(ico="camion")), ("y suben", "icono", dict(ico="edificio", st=("ventana", "POR LA VENTANA")))], [(None, "PARÍS, 2025"), ("A plena", "A PLENA LUZ DEL DÍA")], {"ventana": "una ventana"}),
    ("Cortan el cristal, rompen dos vitrinas y se llevan ocho joyas históricas. En la huida, se les cae una corona.",
     [(None, "icono", dict(ico="joya", st=("ocho", "8 JOYAS"))), ("En la", "icono", dict(ico="corona", st=("cae", "¡SE CAE!", AMAR)))], [(None, "CRISTAL CORTADO"), ("ocho joyas", "8 JOYAS HISTÓRICAS")], {"ocho": "ocho joyas", "cae": "se les"}),
    ("El botín se calcula en unos 88 millones de euros. En pocas semanas hubo detenidos, pero las joyas no aparecieron.",
     [(None, "contador", dict(valor=88, u="MILLONES €", ico="joya")), ("En pocas", "siluetas", dict(n=3, cada="DETENIDO"))], [(None, "≈ 88 MILLONES €"), ("pero las", "¿Y LAS JOYAS?")], {}),
    ("El museo más visitado del mundo, robado en siete minutos. ¿Cómo crees que pudo pasar?",
     [(None, "pregunta", dict(ico="edificio"))], [(None, "7 MINUTOS"), ("Cómo", "¿CÓMO PUDO PASAR?")], {}),
], {"Louvre": "Luvre"})

caso("carcel-escobar", ("SE CONSTRUYÓ", "SU PROPIA CÁRCEL", "¡Y SE ESCAPÓ!"), ("COL", "ENVIGADO", -75.59, 6.17), [
    ("Imagina que el narcotraficante más buscado del mundo acepta entregarse… pero solo si puede construir su propia cárcel.",
     [(None, "icono", dict(ico="rejas", st=("propia", "SU PROPIA CÁRCEL")))], [("el narcotraficante", "EL MÁS BUSCADO"), ("pero solo", "¿SU PROPIA CÁRCEL?")], {"propia": "su propia"}),
    ("Colombia, 1991. Pablo Escobar se entrega a cambio de cumplir condena en una prisión en lo alto de un monte, cerca de Medellín. La llaman La Catedral.",
     [(None, "icono", dict(ico="edificio", label="LA CATEDRAL"))], [(None, "COLOMBIA, 1991"), ("La llaman", "«LA CATEDRAL»")], {}),
    ("Dentro, según los testimonios, había bar, jacuzzi y hasta un campo de fútbol. Los guardias, en la práctica, trabajaban para él.",
     [(None, "icono", dict(ico=["trofeo", "billetes"], st=("guardias", "GUARDIAS A SU SERVICIO")))], [(None, "BAR · JACUZZI · FÚTBOL"), ("Los guardias", "GUARDIAS COMPRADOS")], {"guardias": "Los guardias"}),
    ("En 1992, cuando el Gobierno intenta trasladarlo a otra prisión, Escobar se escapa sin que nadie lo detenga.",
     [(None, "carcel", dict(vacia=True, st=("escapa", "¡FUGADO!")))], [(None, "1992"), ("Escobar se", "SE ESCAPA")], {"escapa": "se escapa"}),
    ("Un preso que diseñó su propia cárcel… y luego salió por la puerta. ¿Crees que alguna vez estuvo preso de verdad?",
     [(None, "pregunta", dict(ico="rejas"))], [(None, "SU PROPIA CÁRCEL"), ("Crees", "¿PRESO DE VERDAD?")], {}),
])

caso("fuga-carrito", ("ESCAPÓ", "EN UN CARRITO", "DE ROPA SUCIA"), ("MEX", "JALISCO", -103.35, 20.67), [
    ("¿Qué pasaría si un preso de máxima seguridad escapara… escondido en un carrito de ropa sucia?",
     [(None, "icono", dict(ico="carrito", st=("carrito", "¿AQUÍ DENTRO?")))], [("máxima", "MÁXIMA SEGURIDAD"), ("escondido", "¿EN UN CARRITO?")], {"carrito": "un carrito"}),
    ("Jalisco, México, enero de 2001. Penal de Puente Grande. Según la versión oficial, un preso se esconde en un carrito de lavandería.",
     [(None, "icono", dict(ico="edificio", label="PUENTE GRANDE"))], [(None, "MÉXICO, 2001"), ("Según la", "LA VERSIÓN OFICIAL")], {}),
    ("Un empleado empuja el carrito por los pasillos, cruza varias puertas de seguridad… y lo saca del penal.",
     [(None, "icono", dict(ico="carrito", st=("saca", "¡FUERA!", VERDE)))], [(None, "POR LOS PASILLOS"), ("y lo", "¡FUERA DEL PENAL!")], {"saca": "lo saca"}),
    ("Era Joaquín Guzmán, El Chapo. Decenas de funcionarios fueron investigados, y él tardó trece años en volver a ser detenido.",
     [(None, "siluetas", dict(n=5, cada="INVESTIGADO")), ("y él", "contador", dict(valor=13, u="AÑOS LIBRE", ico="lupa"))], [(None, "DECENAS INVESTIGADOS"), ("y él", "13 AÑOS LIBRE")], {}),
    ("Una cárcel de máxima seguridad… vencida por un carrito de ropa sucia. ¿Te lo crees?",
     [(None, "pregunta", dict(ico="carrito"))], [(None, "UN CARRITO…"), ("Te lo", "¿TE LO CREES?")], {}),
])

caso("copa-mundial", ("ROBARON", "LA COPA DEL MUNDO", "¡Y NUNCA APARECIÓ!"), ("BRA", "RÍO DE JANEIRO", -43.2, -22.9), [
    ("Imagina que el trofeo más famoso del fútbol es robado… y nunca vuelve a aparecer.",
     [(None, "icono", dict(ico="trofeo", st=("nunca", "NUNCA APARECIÓ")))], [("el trofeo", "EL TROFEO MÁS FAMOSO"), ("y nunca", "¿NUNCA APARECIÓ?")], {"nunca": "y nunca"}),
    ("Río de Janeiro, diciembre de 1983. La Copa Jules Rimet, la que Brasil ganó para siempre al ser campeón tres veces, está en la sede de su federación.",
     [(None, "icono", dict(ico="trofeo", label="JULES RIMET"))], [(None, "BRASIL, 1983"), ("La Copa", "LA COPA JULES RIMET")], {}),
    ("Está detrás de un cristal blindado… pero el marco de la vitrina es de madera. Los ladrones lo fuerzan y se la llevan.",
     [(None, "icono", dict(ico="trofeo", st=("madera", "MARCO DE MADERA")))], [(None, "CRISTAL BLINDADO…"), ("pero el", "…MARCO DE MADERA")], {"madera": "de madera"}),
    ("Hubo detenidos, pero la copa nunca apareció. La policía cree que la fundieron para vender el oro.",
     [(None, "siluetas", dict(n=3, cada="DETENIDO")), ("La policía", "icono", dict(ico="oro", st=("fundieron", "¿FUNDIDA?")))], [(None, "DETENIDOS"), ("La policía", "¿FUNDIDA?")], {"fundieron": "la fundieron"}),
    ("Y no era la primera vez: en 1966 ya la habían robado en Londres, y la encontró un perro. ¿Lo sabías?",
     [(None, "pregunta", dict(ico="trofeo", st=("perro", "¡UN PERRO!", VERDE)))], [(None, "1966: OTRO ROBO"), ("Lo sabías", "¿LO SABÍAS?")], {"perro": "un perro"}),
], {"Jules Rimet": "Yul Rimé"})

caso("esquema-ponzi", ("50% EN 45 DÍAS", "LA ESTAFA", "QUE TIENE SU NOMBRE"), ("USA", "BOSTON", -71.06, 42.36), [
    ("¿Qué pensarías si te dijera que una estafa es tan famosa que lleva el nombre de su creador?",
     [(None, "icono", dict(ico="billetes", st=("nombre", "LLEVA SU NOMBRE")))], [("una estafa", "UNA ESTAFA FAMOSA"), ("lleva el", "CON SU NOMBRE")], {"nombre": "el nombre"}),
    ("Boston, 1920. Charles Ponzi promete a sus inversores un 50% de beneficio en solo 45 días, gracias a un negocio con cupones de correo.",
     [(None, "icono", dict(ico="carta", st=("cupones", "CUPONES DE CORREO")))], [(None, "BOSTON, 1920"), ("un 50%", "+50% EN 45 DÍAS")], {"cupones": "con cupones"}),
    ("Miles de personas le dan su dinero. Pero el negocio casi no existe: paga a los primeros con el dinero de los nuevos.",
     [(None, "siluetas", dict(n=6, ico="billetes")), ("Pero el", "icono", dict(ico="saco", st=("nuevos", "DINERO DE LOS NUEVOS")))], [(None, "MILES DE INVERSORES"), ("paga a", "PAGA CON DINERO NUEVO")], {"nuevos": "los nuevos"}),
    ("En agosto de 1920, un periódico destapa el engaño y todo se derrumba. Ponzi acaba en prisión.",
     [(None, "icono", dict(ico="graficas", st=("derrumba", "¡SE DERRUMBA!"))), ("Ponzi acaba", "carcel", dict())], [(None, "AGOSTO DE 1920"), ("Ponzi acaba", "A PRISIÓN")], {"derrumba": "se derrumba"}),
    ("Hoy, cuando alguien paga ganancias falsas con dinero nuevo, se llama esquema Ponzi. ¿Conocías el origen?",
     [(None, "pregunta", dict(ico="billetes"))], [(None, "EL «ESQUEMA PONZI»"), ("Conocías", "¿CONOCÍAS EL ORIGEN?")], {}),
], {"Ponzi": "Ponsi"})

caso("estafa-madoff", ("LA MAYOR", "ESTAFA", "DE LA HISTORIA"), ("USA", "NUEVA YORK", -74.0, 40.71), [
    ("Imagina que el hombre que dirigía la bolsa de Nueva York… estaba montando la mayor estafa de la historia.",
     [(None, "icono", dict(ico="graficas", st=("estafa", "LA MAYOR ESTAFA")))], [("el hombre", "UN GENIO DE LAS FINANZAS"), ("la mayor", "¿LA MAYOR ESTAFA?")], {"estafa": "la mayor"}),
    ("Nueva York, diciembre de 2008. Bernie Madoff, que había presidido el mercado Nasdaq, confiesa a sus hijos que su fondo es una mentira.",
     [(None, "siluetas", dict(n=3, st=("mentira", "¡ERA MENTIRA!")))], [(None, "NUEVA YORK, 2008"), ("confiesa", "LA CONFESIÓN")], {"mentira": "una mentira"}),
    ("Durante décadas pagó a sus clientes con el dinero de los nuevos. Las cuentas falsas sumaban unos 65 mil millones de dólares.",
     [(None, "contador", dict(valor=65000, u="MILLONES $", ico="billetes"))], [(None, "DÉCADAS DE ENGAÑO"), ("Las cuentas", "65.000 MILLONES $")], {}),
    ("Sus hijos lo denunciaron. En 2009 fue condenado a 150 años de prisión.",
     [(None, "carcel", dict(st=("condenado", "150 AÑOS")))], [(None, "LO DENUNCIAN SUS HIJOS"), ("En 2009", "150 AÑOS DE PRISIÓN")], {"condenado": "fue condenado"}),
    ("La mayor estafa de la historia la destaparon sus propios hijos. ¿Tú lo habrías hecho?",
     [(None, "pregunta", dict(ico="graficas"))], [(None, "SUS PROPIOS HIJOS"), ("Tú lo", "¿TÚ LO HABRÍAS HECHO?")], {}),
], {"Madoff": "Médof", "Nasdaq": "Násdak", "Bernie": "Berni"})

caso("el-lute", ("SE FUGÓ VARIAS VECES", "Y ACABÓ", "DE ABOGADO"), ("ESP", "EL PUERTO", -6.23, 36.6), [
    ("¿Qué pasaría si el fugitivo más famoso de un país… acabara siendo abogado?",
     [(None, "icono", dict(ico="rejas", st=("abogado", "¿ABOGADO?")))], [("el fugitivo", "EL FUGITIVO MÁS FAMOSO"), ("acabara", "¿ACABÓ DE ABOGADO?")], {"abogado": "siendo abogado"}),
    ("España, años sesenta. Eleuterio Sánchez, El Lute, es condenado por un atraco. Se convierte en el preso más buscado del país al fugarse de la cárcel.",
     [(None, "carcel", dict(vacia=True, st=("fugarse", "¡FUGADO!")))], [(None, "ESPAÑA, AÑOS 60"), ("Se convierte", "EL MÁS BUSCADO")], {"fugarse": "al fugarse"}),
    ("Lo detienen y se vuelve a escapar, varias veces. Su cara sale en todos los periódicos.",
     [(None, "icono", dict(ico="nota", st=("periódicos", "SE BUSCA")))], [(None, "OTRA FUGA…"), ("Su cara", "EN TODOS LOS PERIÓDICOS")], {"periódicos": "los periódicos"}),
    ("Pero en prisión hace algo inesperado: estudia Derecho. En 1981 recibe el indulto y sale libre.",
     [(None, "icono", dict(ico="nota", st=("Derecho", "ESTUDIA DERECHO", AZUL))), ("En 1981", "siluetas", dict(n=1, st=("indulto", "INDULTADO", VERDE)))], [(None, "ALGO INESPERADO"), ("En 1981", "1981: INDULTADO")], {"Derecho": "estudia Derecho", "indulto": "el indulto"}),
    ("De fugitivo a abogado. ¿Crees que una persona puede cambiar así?",
     [(None, "pregunta", dict(ico="nota"))], [(None, "DE FUGITIVO A ABOGADO"), ("Crees", "¿SE PUEDE CAMBIAR ASÍ?")], {}),
], {"Lute": "Lute"})

caso("oro-heathrow", ("BUSCABAN DINERO", "Y ENCONTRARON", "¡3 TONELADAS DE ORO!"), ("GBR", "LONDRES", -0.45, 51.47), [
    ("Imagina que unos ladrones entran a robar dinero… y se encuentran tres toneladas de oro.",
     [(None, "icono", dict(ico="oro", st=("oro", "¡3 TONELADAS!")))], [("unos ladrones", "IBAN A POR DINERO…"), ("tres toneladas", "…Y ERA ORO")], {"oro": "de oro"}),
    ("Londres, noviembre de 1983. Una banda entra en un almacén de seguridad junto al aeropuerto de Heathrow, con ayuda de un vigilante de dentro.",
     [(None, "icono", dict(ico="edificio", label="HEATHROW", st=("vigilante", "AYUDA DESDE DENTRO")))], [(None, "LONDRES, 1983"), ("con ayuda", "UN CÓMPLICE DENTRO")], {"vigilante": "un vigilante"}),
    ("Esperaban unos tres millones de libras en billetes. Pero en la cámara había casi siete mil lingotes de oro.",
     [(None, "icono", dict(ico="billetes")), ("Pero en", "icono", dict(ico="oro", s=2.0, st=("lingotes", "¡7.000 LINGOTES!", AMAR)))], [(None, "ESPERABAN 3 MILLONES"), ("Pero en", "CASI 7.000 LINGOTES")], {"lingotes": "lingotes de"}),
    ("Se llevaron oro por valor de 26 millones de libras de entonces. La mayor parte nunca se recuperó.",
     [(None, "contador", dict(valor=26, u="MILLONES £", ico="oro")), ("La mayor", "pregunta", dict(ico="oro"))], [(None, "26 MILLONES £"), ("La mayor", "NUNCA SE RECUPERÓ")], {}),
    ("Fueron a por billetes y salieron con tres toneladas de oro. ¿Dónde crees que acabó?",
     [(None, "pregunta", dict(ico="oro"))], [(None, "3 TONELADAS DE ORO"), ("Dónde", "¿DÓNDE ACABÓ?")], {}),
], {"Heathrow": "Jízrou"})

caso("asalto-tren", ("ASALTARON", "UN TREN CORREO", "Y UNO HUYÓ A BRASIL"), ("GBR", "INGLATERRA", -0.8, 51.9), [
    ("¿Qué pensarías si te dijera que unos ladrones pararon un tren… cambiando el color de un semáforo?",
     [(None, "icono", dict(ico="tren", st=("semáforo", "¿UN SEMÁFORO?")))], [("pararon un", "PARARON UN TREN"), ("cambiando", "¿CON UN SEMÁFORO?")], {"semáforo": "un semáforo"}),
    ("Inglaterra, agosto de 1963. Una banda tapa la luz verde de una señal de tren y enciende una roja. El tren correo se detiene en plena noche.",
     [(None, "icono", dict(ico="tren", noche=True, st=("detiene", "¡STOP!")))], [(None, "INGLATERRA, 1963"), ("enciende una", "LUZ ROJA FALSA")], {"detiene": "se detiene"}),
    ("En pocos minutos cargan más de cien sacas de dinero. Se llevan unos 2,6 millones de libras de la época.",
     [(None, "icono", dict(ico=["saco", "saco", "saco"])), ("Se llevan", "contador", dict(valor=2.6, u="MILLONES £", ico="saco"))], [(None, "+100 SACAS"), ("Se llevan", "2,6 MILLONES £")], {}),
    ("Casi todos acabaron detenidos. Uno de ellos se fugó de la cárcel y vivió más de treinta años en Brasil.",
     [(None, "siluetas", dict(n=5, cada="DETENIDO")), ("Uno de", "carcel", dict(vacia=True, st=("Brasil", "RUMBO A BRASIL", VERDE)))], [(None, "CASI TODOS DETENIDOS"), ("Uno de", "UNO HUYÓ A BRASIL")], {"Brasil": "en Brasil"}),
    ("Un robo enorme que empezó con un simple semáforo. ¿Te lo imaginabas?",
     [(None, "pregunta", dict(ico="tren"))], [(None, "UN SIMPLE SEMÁFORO"), ("Te lo", "¿TE LO IMAGINABAS?")], {}),
])

caso("joyas-dresde", ("APAGARON LA LUZ", "DE UN MUSEO", "Y SE LLEVARON JOYAS"), ("DEU", "DRESDE", 13.74, 51.05), [
    ("Imagina que unos ladrones dejan a oscuras un museo… para robar unas joyas de hace trescientos años.",
     [(None, "icono", dict(ico="joya", noche=True, st=("oscuras", "A OSCURAS")))], [("dejan a", "MUSEO A OSCURAS"), ("para robar", "JOYAS DE 300 AÑOS")], {"oscuras": "a oscuras"}),
    ("Dresde, Alemania, noviembre de 2019. De madrugada, alguien prende fuego a una caja eléctrica y el barrio se queda sin luz.",
     [(None, "icono", dict(ico="edificio", noche=True, st=("luz", "¡APAGÓN!", AMAR)))], [(None, "DRESDE, 2019"), ("alguien prende", "FUEGO EN LA CAJA ELÉCTRICA")], {"luz": "sin luz"}),
    ("Los ladrones entran por una ventana, rompen una vitrina con un hacha y se llevan joyas del siglo XVIII. Todo en pocos minutos.",
     [(None, "icono", dict(ico=["joya", "corona"], st=("vitrina", "¡CRAC!")))], [(None, "POR UNA VENTANA"), ("y se", "JOYAS DEL SIGLO XVIII")], {"vitrina": "una vitrina"}),
    ("En 2023, varios miembros de un clan criminal fueron condenados. Devolvieron gran parte de las joyas, pero no todas.",
     [(None, "siluetas", dict(n=5, cada="CONDENADO")), ("Devolvieron", "icono", dict(ico="joya", st=("todas", "FALTAN PIEZAS")))], [(None, "2023: CONDENADOS"), ("Devolvieron", "NO TODAS VOLVIERON")], {"todas": "no todas"}),
    ("Un apagón, un hacha y unos minutos. ¿Dónde crees que están las que faltan?",
     [(None, "pregunta", dict(ico="joya"))], [(None, "UN APAGÓN Y UN HACHA"), ("Dónde", "¿DÓNDE ESTÁN?")], {}),
], {"XVIII": "dieciocho", "Dresde": "Dresde"})

caso("robo-aeropuerto", ("EL MAYOR ROBO", "DE DINERO", "DE SU ÉPOCA"), ("USA", "NUEVA YORK", -73.78, 40.64), [
    ("¿Qué pasaría si el mayor robo de dinero en efectivo de un país… ocurriera en un aeropuerto?",
     [(None, "icono", dict(ico="avion", st=("aeropuerto", "¿EN UN AEROPUERTO?")))], [("el mayor", "EL MAYOR ROBO EN EFECTIVO"), ("ocurriera", "¿EN UN AEROPUERTO?")], {"aeropuerto": "un aeropuerto"}),
    ("Nueva York, diciembre de 1978. Una banda entra de madrugada en el almacén de carga de una aerolínea, en el aeropuerto JFK.",
     [(None, "icono", dict(ico="edificio", noche=True, label="CARGA AÉREA"))], [(None, "NUEVA YORK, 1978"), ("aeropuerto JFK", "AEROPUERTO JFK")], {}),
    ("En poco más de una hora se llevan unos cinco millones de dólares en efectivo y casi un millón en joyas.",
     [(None, "contador", dict(valor=5, u="MILLONES $", ico="billetes")), ("y casi", "icono", dict(ico="joya", st=("joyas", "+ JOYAS")))], [(None, "EN MENOS DE 2 HORAS"), ("unos cinco", "5 MILLONES $")], {"joyas": "en joyas"}),
    ("Fue el mayor robo en efectivo de su época en Estados Unidos. Casi todo el dinero desapareció para siempre.",
     [(None, "pregunta", dict(ico="billetes", st=("desapareció", "DESAPARECIDO")))], [(None, "EL MAYOR DE SU ÉPOCA"), ("Casi todo", "NUNCA APARECIÓ")], {"desapareció": "dinero desapareció"}),
    ("La historia inspiró una película famosa. ¿Sabías que estaba basada en un robo real?",
     [(None, "pregunta", dict(ico="avion"))], [(None, "INSPIRÓ UNA PELÍCULA"), ("Sabías", "¿SABÍAS QUE ERA REAL?")], {}),
], {"JFK": "jota efe ka"})

caso("fuga-dannemora", ("ESCAPARON", "Y DEJARON", "«QUE TENGAS UN BUEN DÍA»"), ("USA", "DANNEMORA", -73.72, 44.72), [
    ("Imagina que dos presos escapan de una cárcel de máxima seguridad… y dejan una nota que dice: que tengas un buen día.",
     [(None, "icono", dict(ico="nota", st=("nota", "«TEN UN BUEN DÍA»", AZUL)))], [("dos presos", "2 PRESOS FUGADOS"), ("y dejan", "…Y UNA NOTA")], {"nota": "una nota"}),
    ("Nueva York, junio de 2015. En la prisión de Dannemora, dos presos cortan las paredes de sus celdas con herramientas eléctricas que les pasó una empleada.",
     [(None, "icono", dict(ico="taladro", st=("empleada", "UNA EMPLEADA CÓMPLICE")))], [(None, "EE. UU., 2015"), ("dos presos", "HERRAMIENTAS ELÉCTRICAS")], {"empleada": "una empleada"}),
    ("Recorren los túneles bajo la cárcel y salen por una alcantarilla. En sus camas dejan bultos para engañar a los guardias.",
     [(None, "carcel", dict(vacia=True, st=("alcantarilla", "POR UNA ALCANTARILLA"))), ("En sus", "icono", dict(ico="nota", st=("camas", "BULTOS EN LA CAMA")))], [(None, "POR LOS TÚNELES"), ("En sus", "BULTOS EN LAS CAMAS")], {"alcantarilla": "una alcantarilla", "camas": "sus camas"}),
    ("Pegada a una tubería encuentran la nota. La búsqueda dura tres semanas y moviliza a más de mil agentes.",
     [(None, "icono", dict(ico="nota")), ("La búsqueda", "siluetas", dict(n=6, st=("agentes", "+1.000 AGENTES", AZUL)))], [(None, "«HAVE A NICE DAY»"), ("La búsqueda", "3 SEMANAS DE BÚSQUEDA")], {"agentes": "mil agentes"}),
    ("Una fuga de película… con nota de despedida incluida. ¿Te lo creerías?",
     [(None, "pregunta", dict(ico="nota"))], [(None, "CON NOTA INCLUIDA"), ("Te lo", "¿TE LO CREERÍAS?")], {}),
], {"Dannemora": "Danemora"})

caso("robo-el-grito", ("ROBARON EL GRITO", "EN 50 SEGUNDOS", "Y DEJARON UNA NOTA"), ("NOR", "OSLO", 10.75, 59.91), [
    ("¿Qué pensarías si te dijera que robaron uno de los cuadros más famosos del mundo… en menos de un minuto?",
     [(None, "icono", dict(ico="grito", st=("minuto", "< 1 MINUTO")))], [("uno de", "UN CUADRO FAMOSÍSIMO"), ("en menos", "¿EN MENOS DE 1 MINUTO?")], {"minuto": "un minuto"}),
    ("Oslo, febrero de 1994. Mientras Noruega inaugura los Juegos Olímpicos de invierno, dos hombres apoyan una escalera en la Galería Nacional.",
     [(None, "icono", dict(ico="edificio", noche=True, st=("escalera", "UNA ESCALERA", AMAR)))], [(None, "OSLO, 1994"), ("Mientras Noruega", "DÍA DE LOS JUEGOS OLÍMPICOS")], {"escalera": "una escalera"}),
    ("Rompen una ventana, descuelgan El Grito, de Munch, y se van. En el lugar dejan una nota: gracias por la mala seguridad.",
     [(None, "icono", dict(ico="grito")), ("En el", "icono", dict(ico="nota", st=("seguridad", "«GRACIAS POR LA MALA SEGURIDAD»", AZUL)))], [(None, "¡CRAC!"), ("En el", "UNA NOTA BURLONA")], {"seguridad": "mala seguridad"}),
    ("La policía montó una trampa con agentes que se hicieron pasar por compradores. Tres meses después, el cuadro apareció intacto.",
     [(None, "siluetas", dict(n=3, st=("compradores", "FALSOS COMPRADORES", AZUL))), ("Tres meses", "icono", dict(ico="grito", st=("intacto", "¡INTACTO!", VERDE)))], [(None, "UNA TRAMPA"), ("Tres meses", "3 MESES DESPUÉS")], {"compradores": "por compradores", "intacto": "apareció intacto"}),
    ("Robado en segundos, con nota de burla incluida. ¿Te lo esperabas?",
     [(None, "pregunta", dict(ico="grito"))], [(None, "CON NOTA DE BURLA"), ("Te lo", "¿TE LO ESPERABAS?")], {}),
], {"Munch": "Munk"})

caso("ladron-museos", ("ROBÓ +200 OBRAS", "DE MUSEOS", "SIN ARMAS"), ("FRA", "ALSACIA", 7.34, 47.75), [
    ("Imagina que un camarero robó más de doscientas obras de arte de museos de media Europa… sin usar ninguna arma.",
     [(None, "icono", dict(ico=["cuadro", "trofeo"], st=("doscientas", "+200 OBRAS")))], [("un camarero", "UN CAMARERO…"), ("más de", "+200 OBRAS ROBADAS")], {"doscientas": "más de"}),
    ("Francia, años noventa. Stéphane Breitwieser visita museos pequeños a la hora de comer, cuando hay menos vigilantes.",
     [(None, "icono", dict(ico="edificio", label="MUSEO", st=("vigilantes", "MENOS VIGILANTES")))], [(None, "FRANCIA, AÑOS 90"), ("a la", "A LA HORA DE COMER")], {"vigilantes": "menos vigilantes"}),
    ("Esconde las piezas bajo el abrigo y sale tan tranquilo. Durante años las guarda en su habitación, en casa de su madre.",
     [(None, "siluetas", dict(n=1, ico="cuadro")), ("Durante años", "icono", dict(ico=["cuadro", "trofeo", "cuadro"], st=("madre", "EN CASA DE SU MADRE", AZUL)))], [(None, "BAJO EL ABRIGO"), ("Durante años", "EN SU HABITACIÓN")], {"madre": "su madre"}),
    ("En 2001 lo detienen en Suiza. Y entonces su madre, según confesó ella misma, destruye muchas obras para que no lo incriminen.",
     [(None, "carcel", dict(st=("Suiza", "DETENIDO"))), ("Y entonces", "icono", dict(ico="cuadro", st=("destruye", "¡DESTRUIDAS!")))], [(None, "2001: DETENIDO"), ("Y entonces", "OBRAS DESTRUIDAS")], {"Suiza": "en Suiza", "destruye": "destruye muchas"}),
    ("Más de doscientas obras, sin un solo arma. ¿Crees que lo hacía por dinero… o por amor al arte?",
     [(None, "pregunta", dict(ico="cuadro"))], [(None, "SIN UN SOLO ARMA"), ("Crees", "¿DINERO O AMOR AL ARTE?")], {}),
], {"Breitwieser": "Bráitvizer", "Stéphane": "Estefan"})


def registrar(slug, d):
    """Añade un caso que llega como JSON (desde la web): listas → tuplas donde el motor lo necesita."""
    bloques = []
    for voz, escenas, pantalla, eventos in d["bloques"]:
        esc = []
        for cue, tipo, p in escenas:
            p = dict(p)
            if p.get("st"):
                p["st"] = tuple(p["st"])
            esc.append((cue, tipo, p))
        bloques.append((voz, esc, [tuple(x) for x in pantalla], dict(eventos)))
    caso(slug, tuple(d["titulo"]), tuple(d["mapa"]) if d.get("mapa") else None, bloques, d.get("pron"))
    C[slug]["estilo"] = d.get("estilo") or "recortes"
    C[slug]["personaje"] = d.get("personaje")             # aspecto del narrador elegido en la web


def cargar(slug):
    c = C[slug]
    PJ.aspecto(c.get("personaje"))                        # sin elegir: el narrador de siempre
    bloques, scenes = [], {}
    previa = None
    for bi, (voz, escenas, pantalla, eventos) in enumerate(c["bloques"]):
        esc = []
        for ei, (cue, tipo, p) in enumerate(escenas):
            nombre = f"b{bi}e{ei}"
            rec = A.recordar(A.con_camara(TIPOS[tipo](p, bi + ei), p, since))
            scenes[nombre] = A.con_transicion(rec, previa, p.get("transicion"))
            previa = rec
            esc.append((cue, nombre))
        bloques.append(dict(id=f"b{bi}", voz=voz, escenas=esc, pantalla=pantalla, eventos=eventos))
    if c.get("mapa"):  # los temas sin un lugar concreto no llevan mapa
        pais, ciudad, lon, lat = c["mapa"]
        scenes = con_mapa(scenes, bloques, pais=pais, ciudad=ciudad, lon=lon, lat=lat)

    def miniatura(path):
        g.ESTILO = c.get("estilo", "recortes")
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, g.W, g.H)
        ctx = cairo.Context(surf)
        scenes[bloques[0]["escenas"][0][1]](ctx, 0, 2.0, {})
        if g.ESTILO != "recortes":
            A_est.post(surf, ctx, 0)
        tex = 0.42 if g.ESTILO == "recortes" else A_est.TEXTURA.get(g.ESTILO, 0)
        if tex:
            ctx.set_operator(cairo.OPERATOR_OVERLAY)
            ctx.set_source_surface(g.make_paper_texture(7))
            ctx.paint_with_alpha(tex)
            ctx.set_operator(cairo.OPERATOR_OVER)
        t1, t2, t3 = c["titulo"]
        card_text(ctx, t1, 540, 220, 100, hexc("#e63946"), (1, 1, 1), math.radians(-2.5), 1.0)
        card_text(ctx, t2, 540, 380, 100, hexc("#1d4ed8"), (1, 1, 1), math.radians(2), 1.0)
        card_text(ctx, t3, 540, 1690, 92, hexc("#ffe14d"), INK, math.radians(-3), 1.0)
        surf.write_to_png(path)

    def configurar():
        g.ESTILO = c.get("estilo", "recortes")
        g.BLOQUES[:] = bloques
        g.SCENES.clear()
        g.SCENES.update(scenes)
        g.RECORTES_SUGERIDOS[:] = []
        g.SALIDA = slug
        d = os.path.join(g.CACHE_DIR, slug)
        os.makedirs(d, exist_ok=True)
        g.CACHE_DIR = d
        g.NARR_JSON = os.path.join(d, "narracion_palabras.json")
        g.NARR_MP3 = os.path.join(d, "narracion.mp3")
        g.thumbnail = miniatura

    return dict(SLUG=slug, BLOQUES=bloques, SCENES=scenes, PRONUNCIA=c["pron"], configurar=configurar, miniatura=miniatura)
