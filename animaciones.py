"""Animaciones de papel para las escenas genéricas (lote14 y la web).

Cada dibujo puede tener:
  entrada     cómo aparece:   pop · cae · desliza · sube · gira · zoom · aparece
  movimiento  qué hace luego: ninguno · flota · late · balancea · gira · tiembla · salta
Y cada escena entera:
  camara      acercar · alejar · ninguna   (zoom lento de toda la escena)
  sacudida    clave de un evento: la escena tiembla cuando la voz dice ese cue

El tiempo que llega ya está cuantizado a 12 poses/s, así que todo se mueve «a saltos», como el resto.
"""
import math

from generar_short import clamp, ease_out_back

ENTRADAS = ["pop", "cae", "desliza", "sube", "gira", "zoom", "aparece",
            "rebota", "voltea", "despliega", "lanza", "estira"]
MOVIMIENTOS = ["ninguno", "flota", "late", "balancea", "gira", "tiembla", "salta",
               "respira", "pendulo", "orbita", "brinca"]
CAMARAS = ["ninguna", "acercar", "alejar", "deriva", "paneo"]
DUR = 0.45  # duración de la entrada (s)


def _out(x):
    return 1 - (1 - x) ** 3


def _atras(x, s=1.9):
    """Sale, se pasa un poco y vuelve («overshoot»): más vivo que una curva suave."""
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def _elastico(x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 2 ** (-9 * x) * math.sin((x * 10 - 0.75) * 2 * math.pi / 3) + 1


def _rebote(x):
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d
        return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d
        return n * x * x + 0.9375
    x -= 2.625 / d
    return n * x * x + 0.984375


def _asienta(t, t0, dur=0.22, fuerza=0.16):
    """Aplastamiento que se recupera tras un golpe en t0 (squash & stretch): >0 aplasta, <0 estira."""
    u = (t - t0) / dur
    if u < 0 or u > 1:
        return 0.0
    return fuerza * math.sin(u * math.pi) * (1 - u) * 1.6


def entrada(nombre, t, j=0):
    """(dx, dy, ángulo, escala) de la entrada t segundos después de aparecer.
    La escala puede ser un número o (sx, sy) para aplastar y estirar como el papel elástico."""
    if nombre == "aparece" or t >= 1.2:
        return 0, 0, 0, 1
    x = clamp(t / DUR)
    lado = -1 if j % 2 == 0 else 1
    if nombre == "cae":
        y = -1100 * (1 - _rebote(clamp(t / 0.7)))
        # estirado mientras cae, aplastado al tocar el suelo
        ap = _asienta(t, 0.255, 0.2, 0.26) + _asienta(t, 0.5, 0.14, 0.10) - (0.12 if t < 0.24 else 0)
        return 0, y + ap * 50, 0, (1 + ap, 1 - ap)
    if nombre == "desliza":
        k = _atras(x, 1.4)
        ap = -0.10 * (1 - x) if x < 1 else 0           # se estira en la dirección del movimiento
        return lado * 1100 * (1 - k), 0, lado * math.radians(-10) * (1 - _out(x)), (1 - ap, 1 + ap * 0.6)
    if nombre == "sube":
        k = _atras(x, 1.5)
        ap = _asienta(t, DUR * 0.75, 0.25, 0.12)
        return 0, 1000 * (1 - k), 0, (1 + ap, 1 - ap)
    if nombre == "gira":
        k = _atras(x, 1.2)
        return 0, 0, (1 - k) * 2 * math.pi, max(0.05, k)
    if nombre == "zoom":
        return 0, 0, 0, max(0.05, 1 + 2.2 * (1 - _atras(x, 1.1)))
    if nombre == "rebota":
        k = _elastico(clamp(t / 0.9))
        return 0, 0, math.radians(8) * (1 - k) * lado, max(0.05, k)
    if nombre == "voltea":
        # gira como una carta sobre su eje vertical (se ve de canto a mitad de camino)
        # (a 12 poses/s tiene que durar ~0,45 s para que se vea girar: de canto → medio → pasada → en su sitio)
        u = clamp(t / 0.45)
        k = (u / 0.75) * 1.1 if u < 0.75 else 1.1 - 0.1 * (u - 0.75) / 0.25     # gira a ritmo constante y se pasa un poco
        return 0, 0, math.radians(-6) * (1 - u), (max(0.04, k), 1 + 0.07 * math.sin(u * math.pi))
    if nombre == "despliega":
        # se despliega de arriba abajo como un papel doblado
        k = _atras(clamp(t / 0.5), 1.6)
        return 0, -120 * (1 - k), 0, (1 + 0.05 * (1 - k), max(0.03, k))
    if nombre == "lanza":
        # entra lanzado desde abajo y un lado describiendo un arco y girando
        k = _out(clamp(t / 0.5))
        ap = _asienta(t, 0.42, 0.25, 0.16)              # se aplasta un poco al aterrizar
        giro = lado * (1 - k) * 3.5 - lado * math.radians(7) * math.sin(clamp((t - 0.42) / 0.3) * math.pi) * (t > 0.42)
        e = max(0.2, k)
        return lado * 700 * (1 - k), 600 * (1 - k) ** 2 - 260 * math.sin(k * math.pi) * (1 - k) + ap * 40, giro, (e * (1 + ap), e * (1 - ap))
    if nombre == "estira":
        # aparece muy estrecho y alto, y rebota hasta su forma
        if t < 0.17:                                   # primero se ve la tira alta y estrecha…
            u = t / 0.17
            return 0, 0, 0, (0.12 + 0.2 * u, 1.55 - 0.15 * u)
        k = _elastico(clamp((t - 0.17) / 0.75))         # …y luego recupera su forma rebotando como una goma
        return 0, 0, 0, (max(0.05, 0.32 + 0.68 * k), max(0.05, 1.4 - 0.4 * k))
    if x >= 1 and t > 0.8:
        return 0, 0, 0, 1
    # pop: crece pasándose de tamaño y se asienta con un pequeño temblor de goma
    k = ease_out_back(x) if x < 1 else 1 + 0.04 * math.sin((t - DUR) * 22) * math.exp(-(t - DUR) * 8)
    ap = 0.10 * math.sin(clamp(t / 0.5) * math.pi * 2) * (1 - clamp(t / 0.5))
    return 0, 0, 0, (max(0.05, k * (1 + ap)), max(0.05, k * (1 - ap)))


def movimiento(nombre, lt, pose, j=0):
    """(dx, dy, ángulo, escala) del movimiento continuo. La escala puede ser (sx, sy)."""
    f = pose + 3 * j                      # cada dibujo, desfasado
    if nombre == "flota":
        return 4 * math.sin(lt * 1.3 + j * 2), 16 * math.sin(lt * 2.2 + j), math.radians(2) * math.sin(lt * 1.7 + j), 1
    if nombre == "late":
        # latido doble (pum-pum) como un corazón, en vez de un salto de tamaño
        c = (lt * 1.25 + j * 0.3) % 1
        b = max(0, math.sin(c / 0.16 * math.pi)) * 0.09 if c < 0.16 else (max(0, math.sin((c - 0.2) / 0.14 * math.pi)) * 0.05 if 0.2 <= c < 0.34 else 0)
        return 0, 0, 0, 1 + b
    if nombre == "balancea":
        return 0, 0, math.radians(7) * math.sin(lt * 3.2 + j), 1
    if nombre == "gira":
        return 0, 0, lt * 1.2, 1
    if nombre == "tiembla":
        return (6, -5, 4, -6)[f % 4], (-4, 5, -6, 3)[f % 4], math.radians((2, -2, 1, -1)[f % 4]), 1
    if nombre == "salta":
        # salto con anticipación (se agacha), estirado en el aire y aplastado al caer
        c = (lt * 1.1 + j * 0.25) % 1
        if c < 0.12:
            ap = 0.12 * math.sin(c / 0.12 * math.pi)
            return 0, ap * 30, 0, (1 + ap, 1 - ap)
        if c < 0.5:
            u = (c - 0.12) / 0.38
            return 0, -70 * math.sin(u * math.pi), 0, (0.94, 1.07)
        if c < 0.62:
            ap = 0.16 * math.sin((c - 0.5) / 0.12 * math.pi)
            return 0, ap * 40, 0, (1 + ap, 1 - ap)
        return 0, 0, 0, 1
    if nombre == "respira":
        k = 0.03 * math.sin(lt * 2.4 + j)
        return 0, 0, 0, (1 - k * 0.5, 1 + k)
    if nombre == "pendulo":
        return 0, 0, math.radians(12) * math.sin(lt * 2.6 + j) * (0.6 + 0.4 * math.cos(lt * 0.5)), 1
    if nombre == "orbita":
        return 18 * math.cos(lt * 2 + j), 12 * math.sin(lt * 2 + j), 0, 1
    if nombre == "brinca":
        # botecitos cortos y alegres, cada dibujo a su ritmo
        u = (lt * 2.2 + j * 0.37) % 1
        return 0, -26 * abs(math.sin(u * math.pi)), math.radians(3) * math.sin(lt * 4.4 + j), 1
    return 0, 0, 0, 1


# Momento del golpe (s) de las entradas que «llegan» con fuerza: salen rayitas de impacto alrededor del dibujo
IMPACTO = {"cae": 0.27, "lanza": 0.42, "pop": 0.17, "rebota": 0.08, "zoom": 0.25}


def impacto(ctx, x, y, t0, t, j=0, radio=190):
    """Rayitas cortas que salen del centro del dibujo durante ~0,3 s tras el golpe (a saltos, como el resto)."""
    u = (t - t0) / 0.3
    if u < 0 or u >= 1:
        return
    try:
        import generar_short as g
        oscuro = getattr(g, "ESTILO", "") in ("palitos", "acuarela")
    except Exception:
        oscuro = False
    r0, r1 = radio * (0.85 + 0.55 * u), radio * (1.05 + 0.75 * u)
    ctx.save()
    ctx.new_path()
    ctx.set_line_width(9 * (1 - u) + 3)
    ctx.set_line_cap(1)
    ctx.set_source_rgba(*((0.1, 0.1, 0.15) if oscuro else (1, 0.92, 0.55)), 0.9 * (1 - u))
    for i in range(8):
        a = i * math.pi / 4 + 0.35 + j * 0.5
        ctx.move_to(x + r0 * math.cos(a), y + r0 * math.sin(a) * 0.8)
        ctx.line_to(x + r1 * math.cos(a), y + r1 * math.sin(a) * 0.8)
    ctx.stroke()
    ctx.restore()


def _esc(e):
    return e if isinstance(e, tuple) else (e, e)


def dibujo_animado(ctx, dibujar, x, y, t, lt, pose, ent="pop", mov=None, j=0):
    """Llama a dibujar() con la entrada y el movimiento aplicados alrededor de (x, y). t < 0 → aún no se ve."""
    if t < 0:
        return
    dx1, dy1, a1, e1 = entrada(ent or "pop", t, j)
    # el movimiento continuo entra suave en vez de arrancar de golpe al terminar la entrada
    m = clamp((t - DUR) / 0.35) if t >= DUR else 0.0
    dx2, dy2, a2, e2 = movimiento(mov, lt, pose, j) if m > 0 else (0, 0, 0, 1)
    sx1, sy1 = _esc(e1)
    sx2, sy2 = _esc(e2)
    sx2, sy2 = 1 + (sx2 - 1) * m, 1 + (sy2 - 1) * m
    if ent in IMPACTO:                         # detrás del dibujo; al caer, sale del suelo
        impacto(ctx, x, y + (90 if ent == "cae" else 0), IMPACTO[ent], t, j)
    ctx.save()
    ctx.translate(x + dx1 + dx2 * m, y + dy1 + dy2 * m)
    ctx.rotate(a1 + a2 * m)
    ctx.scale(sx1 * sx2, sy1 * sy2)
    ctx.translate(-x, -y)
    dibujar()
    ctx.restore()


def _suave(x):
    return x * x * (3 - 2 * x)


def con_camara(sc, p, since):
    """Envuelve una escena con zoom lento de cámara y/o sacudida en un evento."""
    cam, sac = p.get("camara"), p.get("sacudida")
    if cam in (None, "ninguna") and not sac:
        return sc

    def envuelta(ctx, pose, lt, ev):
        ctx.save()
        if cam in ("acercar", "alejar"):
            k = _suave(clamp(lt / 6.0))
            z = 1 + 0.12 * (k if cam == "acercar" else 1 - k)
            ctx.translate(540, 960)
            ctx.scale(z, z)
            ctx.translate(-540, -960)
        elif cam == "deriva":
            # cámara «en mano»: se mueve y gira muy poco, como si alguien la sujetara
            z = 1.05 + 0.015 * math.sin(lt * 0.7)
            ctx.translate(540 + 14 * math.sin(lt * 0.9), 960 + 10 * math.sin(lt * 0.63 + 1))
            ctx.rotate(math.radians(0.8) * math.sin(lt * 0.5))
            ctx.scale(z, z)
            ctx.translate(-540, -960)
        elif cam == "paneo":
            k = _suave(clamp(lt / 6.0))
            ctx.translate(540 + 50 - 100 * k, 960)
            ctx.scale(1.1, 1.1)
            ctx.translate(-540, -960)
        if sac:
            t = since(ev, sac, lt)
            if 0 <= t < 0.6:
                d = (1 - t / 0.6) ** 1.5                # se calma poco a poco
                ctx.translate(22 * d * math.sin(t * 70), 16 * d * math.sin(t * 53 + 1))
                ctx.translate(540, 960)
                ctx.rotate(math.radians(1.5) * d * math.sin(t * 41))
                ctx.translate(-540, -960)
        sc(ctx, pose, lt, ev)
        ctx.restore()
    return envuelta


# ───────────────────────────── transiciones entre escenas ─────────────────────────────
TRANSICIONES = ["corte", "barrido", "empuje", "zoom", "iris", "fundido", "flash",
                 "persiana", "rasgado", "glitch", "sube", "giro"]
DUR_TRANS = 0.34
DUR_TRANS_TIPO = {"persiana": 0.42, "rasgado": 0.40, "giro": 0.42}


def recordar(sc):
    """Envuelve una escena para recordar cómo se dibujó por última vez (lo usa la transición siguiente)."""
    def env(ctx, pose, lt, ev):
        env.ultimo = (pose, lt, ev)
        sc(ctx, pose, lt, ev)
    env.ultimo = None
    env.base = sc
    return env


def con_transicion(sc, previa, tipo):
    """Los primeros 0,34 s de la escena mezclan el último fotograma de la anterior con la nueva."""
    if previa is None or tipo in (None, "corte"):
        return sc
    import cairo

    def env(ctx, pose, lt, ev):
        dur = DUR_TRANS_TIPO.get(tipo, DUR_TRANS)
        if lt >= dur:
            return sc(ctx, pose, lt, ev)
        k = _out(clamp(lt / dur))
        dest = ctx.get_target()
        W, H = dest.get_width(), dest.get_height()
        a = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        b = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        p = previa.ultimo or (pose, 4.0, {})
        previa.base(cairo.Context(a), p[0], p[1], p[2])
        sc(cairo.Context(b), pose, lt, ev)
        ctx.save()
        ctx.identity_matrix()
        if tipo == "empuje":
            k = _atras(clamp(lt / dur), 0.9)
            ctx.set_source_surface(a, -W * k, 0); ctx.paint()
            ctx.set_source_surface(b, W * (1 - k), 0); ctx.paint()
            ctx.rectangle(W * (1 - k) - 18, 0, 18, H); ctx.set_source_rgba(0, 0, 0, 0.25 * (1 - k)); ctx.fill()
        elif tipo == "sube":
            ctx.set_source_surface(a, 0, -H * k * 0.35); ctx.paint()
            ctx.set_source_rgba(0, 0, 0, 0.35 * k); ctx.paint()
            ctx.set_source_surface(b, 0, H * (1 - k)); ctx.paint()
        elif tipo == "persiana":
            # tiras horizontales que se cierran una tras otra
            ctx.set_source_surface(a, 0, 0); ctx.paint()
            n, u = 8, clamp(lt / dur)
            for i in range(n):
                ki = _out(clamp(u * 1.6 - i * 0.6 / n))
                hi = H / n
                ctx.rectangle(0, i * hi + hi * (1 - ki) / 2, W, hi * ki + 1)
            ctx.save(); ctx.clip(); ctx.set_source_surface(b, 0, 0); ctx.paint(); ctx.restore()
        elif tipo == "rasgado":
            # la escena anterior se rompe como un papel por una línea en zigzag y las dos mitades se van
            u = _out(clamp(lt / dur))
            ctx.set_source_surface(b, 0, 0); ctx.paint()
            pts = [(-10, H * 0.47)] + [(x, H * 0.47 + (34 if i % 2 else -34) + ((x * 37) % 23 - 11))
                                       for i, x in enumerate(range(0, W + 80, 72))] + [(W + 10, H * 0.47)]
            for sgn in (-1, 1):
                ctx.save()
                ctx.translate(0, sgn * H * 0.6 * u)
                ctx.translate(W / 2, H / 2); ctx.rotate(sgn * math.radians(5) * u); ctx.translate(-W / 2, -H / 2)
                ctx.move_to(*pts[0])
                for q in pts[1:]:
                    ctx.line_to(*q)
                ctx.line_to(W + 10, -10 if sgn < 0 else H + 10); ctx.line_to(-10, -10 if sgn < 0 else H + 10); ctx.close_path()
                ctx.save(); ctx.clip_preserve(); ctx.set_source_surface(a, 0, 0); ctx.paint(); ctx.restore()
                ctx.new_path(); ctx.move_to(*pts[0])
                for q in pts[1:]:
                    ctx.line_to(*q)
                ctx.set_source_rgba(0.96, 0.93, 0.86, 1); ctx.set_line_width(10); ctx.stroke()      # filo de papel blanco
                ctx.restore()
        elif tipo == "glitch":
            # cortes digitales: franjas desplazadas y separación de color, muy rápido
            u = clamp(lt / dur)
            fuente = a if u < 0.45 else b
            ctx.set_source_surface(fuente, 0, 0); ctx.paint()
            fuerza = 1 - abs(u - 0.45) / 0.55
            for i in range(9):
                y0 = ((i * 397 + pose * 131) % H)
                hh = 30 + (i * 53 + pose * 17) % 120
                dx = ((i * 71 + pose * 29) % 160 - 80) * fuerza
                ctx.save(); ctx.rectangle(0, y0, W, hh); ctx.clip()
                ctx.set_source_surface(fuente, dx, 0); ctx.paint(); ctx.restore()
                ctx.save(); ctx.rectangle(0, y0, W, hh)
                ctx.set_source_rgba(*((1, 0.1, 0.4) if i % 2 else (0.1, 0.9, 1)), 0.16 * fuerza); ctx.fill(); ctx.restore()
        elif tipo == "giro":
            # la anterior se va girando y encogiendo; la nueva aparece detrás
            u = _out(clamp(lt / dur))
            ctx.set_source_surface(b, 0, 0); ctx.paint()
            ctx.save()
            ctx.translate(W / 2, H * 0.47); ctx.rotate(-u * math.radians(35)); z = max(0.01, 1 - u); ctx.scale(z, z)
            ctx.translate(-W / 2, -H * 0.47)
            ctx.set_source_surface(a, 0, 0); ctx.paint_with_alpha(1 - u * 0.3)
            ctx.restore()
        elif tipo == "barrido":
            ctx.set_source_surface(a, 0, 0); ctx.paint()
            x = (W + 500) * k - 250
            ctx.move_to(-10, -10); ctx.line_to(x + 250, -10); ctx.line_to(x - 250, H + 10); ctx.line_to(-10, H + 10); ctx.close_path()
            ctx.save(); ctx.clip(); ctx.set_source_surface(b, 0, 0); ctx.paint(); ctx.restore()
            ctx.move_to(x + 250, -10); ctx.line_to(x - 250, H + 10)                 # filo de color
            ctx.set_source_rgba(1, 0.82, 0.25, 1 - k * 0.6); ctx.set_line_width(26); ctx.stroke()
        elif tipo == "iris":
            ctx.set_source_surface(a, 0, 0); ctx.paint()
            r = math.hypot(W, H) * 0.56 * k
            ctx.arc(W / 2, H * 0.47, r, 0, 2 * math.pi)
            ctx.save(); ctx.clip(); ctx.set_source_surface(b, 0, 0); ctx.paint(); ctx.restore()
            ctx.arc(W / 2, H * 0.47, r, 0, 2 * math.pi)
            ctx.set_source_rgba(0.08, 0.09, 0.14, 1); ctx.set_line_width(18); ctx.stroke()
        elif tipo == "zoom":
            ctx.set_source_surface(b, 0, 0); ctx.paint()
            z = 1 + 1.6 * k
            ctx.translate(W / 2, H * 0.47); ctx.scale(z, z); ctx.translate(-W / 2, -H * 0.47)
            ctx.set_source_surface(a, 0, 0); ctx.paint_with_alpha(1 - k)
        elif tipo == "flash":
            ctx.set_source_surface(b if k > 0.25 else a, 0, 0); ctx.paint()
            ctx.set_source_rgba(1, 1, 1, max(0, 1 - abs(k - 0.25) * 2.2)); ctx.paint()
        else:                                                                       # fundido
            ctx.set_source_surface(a, 0, 0); ctx.paint()
            ctx.set_source_surface(b, 0, 0); ctx.paint_with_alpha(k)
        ctx.restore()
    return env


# ───────────────────────────── ambiente: motas flotando ─────────────────────────────
def ambiente(ctx, pose, n=14, col=(1, 1, 1), alfa=0.10):
    """Motas suaves que suben despacio por el fondo: da vida a la escena sin distraer."""
    for i in range(n):
        x = (i * 263 + 97) % 1080
        y = 1300 - ((i * 211 + pose * (5 + i % 4)) % 1150)
        r = 5 + (i * 7) % 11
        ctx.new_sub_path()
        ctx.arc(x + 14 * math.sin((pose + i * 9) / 14), y, r, 0, 2 * math.pi)
    ctx.set_source_rgba(col[0], col[1], col[2], alfa)
    ctx.fill()
