"""Web de Caso Recortado Studio: cuentas, creador de vídeos, planes y pagos con Stripe.

Desarrollo (todo en uno, con el obrero dentro):
    CR_DEMO=1 python web/app.py                 → http://localhost:8000   (modo demo: sin IA)
Servidor (ver despliegue/LEEME.md):
    gunicorn -w 2 -k gthread --threads 8 -b 127.0.0.1:8000 app:app   (web)   +   python worker.py   (vídeos)

Ajustes en web/.env (plantilla: web/.env.example): SECRET_KEY, ANTHROPIC_API_KEY, STRIPE_*, CR_CLAVE (beta privada).
"""
import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import uuid

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request, send_from_directory,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from entorno import cargar_env, datos  # noqa: E402

cargar_env()
import correo  # noqa: E402
import db  # noqa: E402
import editar  # noqa: E402
import fabrica  # noqa: E402
import guionista  # noqa: E402
import voces  # noqa: E402
sys.path.insert(0, fabrica.RAIZ)
import personaje  # noqa: E402  (el narrador animado: opciones y dibujo para la vista previa)

SALIDA = datos("salida") if os.environ.get("CR_DATOS") else os.path.join(fabrica.RAIZ, "salida")
DEMO = os.environ.get("CR_DEMO") == "1"
CLAVE = os.environ.get("CR_CLAVE")                     # opcional: beta privada (?clave=... una vez)
URL_BASE = os.environ.get("CR_URL", "http://localhost:8000").rstrip("/")
SOLO_LISTA = os.environ.get("CR_SOLO_LISTA") == "1"
# Datos del titular para los textos legales: se ponen en las variables de la nube, no en el código
LEGAL = {k: os.environ.get(v, "").strip() for k, v in dict(
    titular="CR_TITULAR", nif="CR_NIF", domicilio="CR_DOMICILIO", email="CR_EMAIL_CONTACTO",
    registro="CR_REGISTRO_MERCANTIL", hosting="CR_ALOJAMIENTO", proveedor_email="CR_PROVEEDOR_EMAIL").items()}   # la web solo enseña la lista de espera (antes de abrir)
ADMIN = os.environ.get("CR_ADMIN_EMAIL", "").strip().lower()   # quien puede descargar la lista de espera


def _secreto():
    s = os.environ.get("SECRET_KEY")
    if s:
        return s
    ruta = datos(".secret_key")                      # en desarrollo se genera uno y se guarda
    if not os.path.exists(ruta):
        with open(ruta, "w") as f:
            f.write(secrets.token_hex(32))
    return open(ruta).read().strip()


app = Flask(__name__)
app.config.update(SECRET_KEY=_secreto(), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_SECURE=URL_BASE.startswith("https"), PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
                  MAX_CONTENT_LENGTH=1024 * 1024)
db.crear_tablas()

# ───────────────────────────── Stripe (opcional) ─────────────────────────────
STRIPE = {k: os.environ.get(k) for k in ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "STRIPE_PRECIO_CREADOR", "STRIPE_PRECIO_PRO")}
PRECIOS = {"creador": STRIPE["STRIPE_PRECIO_CREADOR"], "pro": STRIPE["STRIPE_PRECIO_PRO"]}
PAGOS_ACTIVOS = bool(STRIPE["STRIPE_SECRET_KEY"] and all(PRECIOS.values()))
if STRIPE["STRIPE_SECRET_KEY"]:
    import stripe
    stripe.api_key = STRIPE["STRIPE_SECRET_KEY"]
else:
    stripe = None
if STRIPE["STRIPE_WEBHOOK_SECRET"] and stripe is None:
    import stripe as _stripe_webhook                   # para verificar firmas aunque no haya clave secreta
else:
    _stripe_webhook = stripe


# ───────────────────────────── base de datos por petición ─────────────────────────────
def con():
    if "con" not in g:
        g.con = db.conectar()
    return g.con


@app.teardown_appcontext
def cerrar(_):
    c = g.pop("con", None)
    if c:
        c.close()


def usuario_actual():
    uid = session.get("uid")
    if not uid:
        return None
    if "usuario" not in g:
        g.usuario = con().execute("SELECT * FROM usuarios WHERE id=?", (uid,)).fetchone()
    return g.usuario


# ───────────────────────────── seguridad ─────────────────────────────
def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(24)
    return session["csrf"]


app.jinja_env.globals["csrf"] = token_csrf
SIN_CSRF = {"/stripe/webhook"}


# en modo «solo lista» quedan abiertas la lista, lo legal y lo que necesita el administrador para entrar y descargarla
ABIERTAS_SOLO_LISTA = ("/lista-espera", "/static/", "/aviso-legal", "/privacidad", "/condiciones", "/admin/",
                       "/entrar", "/salir", "/recuperar", "/registro", "/cuenta")


@app.before_request
def proteger():
    if request.path in SIN_CSRF:
        return None
    if SOLO_LISTA and not request.path.startswith(ABIERTAS_SOLO_LISTA):
        return redirect("/lista-espera")
    if CLAVE and request.cookies.get("clave") != CLAVE:      # beta privada
        if request.args.get("clave") == CLAVE:
            r = redirect(request.path)
            r.set_cookie("clave", CLAVE, max_age=7 * 24 * 3600, httponly=True, samesite="Lax")
            return r
        return "Acceso privado: abre el enlace completo con la clave.", 403
    if request.method == "POST":
        enviado = request.headers.get("X-CSRF") or request.form.get("csrf", "")
        if not hmac.compare_digest(enviado, session.get("csrf", "-")):
            abort(400, "La sesión ha caducado: recarga la página.")
    return None


@app.context_processor
def contexto():
    u = usuario_actual()
    datos = dict(demo=DEMO, usuario=u, planes=db.PLANES, pagos_activos=PAGOS_ACTIVOS, voces=voces.VOCES,
                 narrador=personaje.OPCIONES, narrador_def=personaje.POR_DEFECTO,
                 solo_lista=SOLO_LISTA, admin=bool(ADMIN and u and u["email"] == ADMIN), legal=LEGAL)
    if u:
        usados, limite = db.uso(con(), u)
        datos.update(usados=usados, limite=limite, plan=db.PLANES.get(u["plan"], db.PLANES["gratis"]))
    return datos


# ───────────────────────────── páginas ─────────────────────────────
@app.get("/")
def inicio():
    if request.args.get("pago") == "ok":
        flash("Pago recibido. Tu plan nuevo se activa en unos segundos: recarga la página si aún no lo ves.")
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if SOLO_LISTA and request.method == "GET" and not request.args.get("admin"):
        return redirect("/lista-espera")                 # aún no abrimos: solo el administrador crea su cuenta
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        clave = request.form.get("clave", "")
        if SOLO_LISTA and email != ADMIN:
            flash("Todavía no hemos abierto. Apúntate a la lista de espera y te avisamos.")
            return redirect("/lista-espera")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Escribe un email válido.")
        elif len(clave) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.")
        elif not request.form.get("acepto"):
            flash("Para crear la cuenta tienes que aceptar las condiciones y la política de privacidad.")
        else:
            try:
                with con() as c:
                    cur = c.execute("INSERT INTO usuarios (email, clave_hash, creado) VALUES (?, ?, ?)",
                                    (email, generate_password_hash(clave), db.ahora()))
                session.clear()
                session.permanent = True
                session["uid"] = cur.lastrowid
                return redirect("/cuenta" if SOLO_LISTA else url_for("inicio") + "#crear-sec")
            except sqlite3.IntegrityError:
                flash("Ya hay una cuenta con ese email. Entra con tu contraseña.")
        return render_template("cuenta.html", modo="registro", email=email), 400
    return render_template("cuenta.html", modo="registro")


FALLOS = {}            # (ip, email) → [momentos de intentos fallidos]; por proceso, suficiente para frenar ataques


def bloqueado(clave):
    ahora = db.ahora()
    FALLOS[clave] = [t for t in FALLOS.get(clave, []) if ahora - t < 900]
    return len(FALLOS[clave]) >= 8


@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        clave_fallo = (request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0], email)
        if bloqueado(clave_fallo):
            flash("Demasiados intentos. Espera 15 minutos y vuelve a probar.")
            return render_template("cuenta.html", modo="entrar", email=email), 429
        u = con().execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
        if u and check_password_hash(u["clave_hash"], request.form.get("clave", "")):
            session.clear()
            session.permanent = True
            session["uid"] = u["id"]
            return redirect("/cuenta" if SOLO_LISTA else url_for("inicio") + "#crear-sec")
        FALLOS.setdefault(clave_fallo, []).append(db.ahora())
        flash("El email o la contraseña no son correctos.")
        return render_template("cuenta.html", modo="entrar", email=email), 401
    return render_template("cuenta.html", modo="entrar")


@app.post("/salir")
def salir():
    session.clear()
    return redirect(url_for("inicio"))


@app.get("/aviso-legal")
def aviso_legal():
    return render_template("legal.html", doc="aviso")


@app.get("/privacidad")
def privacidad():
    return render_template("legal.html", doc="privacidad")


@app.get("/condiciones")
def condiciones():
    return render_template("legal.html", doc="condiciones")


# ───────────────────────────── API de vídeos ─────────────────────────────
@app.post("/api/crear")
def crear():
    u = usuario_actual()
    if not u:
        return jsonify(error="Entra en tu cuenta para crear vídeos.", entrar=url_for("registro")), 401
    datos = request.get_json(silent=True) or {}
    tema = str(datos.get("tema", "")).strip()
    estilo = datos.get("estilo") if datos.get("estilo") in guionista.ESTILOS else "equilibrado"
    visual = datos.get("visual") if datos.get("visual") in guionista.estilos.ESTILOS else "recortes"
    voz = voces.valida(datos.get("voz"))
    narrador = json.dumps(personaje.valida(datos.get("personaje")), ensure_ascii=False) if datos.get("personaje") else None
    revisar = 1 if datos.get("revisar") else 0
    if not 3 <= len(tema) <= 200:
        return jsonify(error="Escribe un tema de entre 3 y 200 caracteres."), 400
    c = con()
    with c:
        c.execute("BEGIN IMMEDIATE")                       # comprobar y reservar el crédito de una vez
        usados, limite = db.uso(c, u)
        if usados >= limite:
            plan = db.PLANES[u["plan"]]["nombre"]
            return jsonify(error=f"Has usado los {limite} vídeos de este mes del plan {plan}. "
                                 "Pásate a un plan superior para seguir creando.", mejorar=True), 402
        pendientes = c.execute("SELECT COUNT(*) FROM trabajos WHERE usuario_id=? AND estado IN ('en cola','trabajando','revisar')",
                               (u["id"],)).fetchone()[0]
        if pendientes >= 3:
            return jsonify(error="Tienes 3 vídeos en marcha. Espera a que acabe alguno."), 429
        tid = uuid.uuid4().hex[:12]
        marca = 1 if db.PLANES.get(u["plan"], db.PLANES["gratis"])["marca"] else 0
        c.execute("INSERT INTO trabajos (id, usuario_id, tema, estilo, visual, marca, voz, revisar, personaje, estado, paso, "
                  "inicio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'en cola', 'Esperando turno', ?)",
                  (tid, u["id"], tema, estilo, visual, marca, voz, revisar, narrador, db.ahora()))
    return jsonify(id=tid)


@app.get("/api/trabajos")
def lista():
    u = usuario_actual()
    if not u:
        return jsonify([])
    c = con()
    filas = c.execute("SELECT * FROM trabajos WHERE usuario_id=? ORDER BY inicio DESC LIMIT 50", (u["id"],)).fetchall()
    cola = [r["id"] for r in c.execute("SELECT id FROM trabajos WHERE estado='en cola' ORDER BY inicio")]
    usados, limite = db.uso(c, u)
    out = []
    for r in filas:
        t = {k: r[k] for k in ("id", "tema", "estilo", "visual", "estado", "paso", "titulo", "descripcion", "marca", "voz")}
        if r["id"] in cola:
            t["delante"] = cola.index(r["id"])
        out.append(t)
    return jsonify(trabajos=out, usados=usados, limite=limite)


_DIBUJO = threading.Lock()


@app.get("/api/narrador.png")
def vista_narrador():
    """Vista previa del narrador con las opciones elegidas (se dibuja con el mismo motor que el vídeo)."""
    d = personaje.valida({k: request.args.get(k) for k in personaje.POR_DEFECTO})
    clave = tuple(sorted(d.items()))
    if clave not in _VISTAS:
        import cairo
        import generar_short as G
        with _DIBUJO:                                   # el aspecto es global del motor: un dibujo cada vez
            G.ESTILO = "recortes"
            personaje.aspecto(d)
            sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, 340, 470)
            ctx = cairo.Context(sup)
            ctx.translate(170, 452)
            ctx.scale(0.62, 0.62)
            personaje.dibujar(ctx, 0, 0, 1.0, "saluda", 3.0, 12)
            personaje.aspecto(None)
            buf = io.BytesIO()
            sup.write_to_png(buf)
        if len(_VISTAS) > 3000:
            _VISTAS.clear()
        _VISTAS[clave] = buf.getvalue()
    return _VISTAS[clave], 200, {"Content-Type": "image/png", "Cache-Control": "public, max-age=86400"}


_VISTAS = {}


def trabajo_propio(tid, estado=None):
    u = usuario_actual()
    if not u or not re.fullmatch(r"[a-f0-9]{12}", tid):
        abort(404)
    r = con().execute("SELECT * FROM trabajos WHERE id=? AND usuario_id=?", (tid, u["id"])).fetchone()
    if not r or (estado and r["estado"] != estado):
        abort(404)
    return r


@app.get("/api/guion/<tid>")
def ver_guion(tid):
    r = trabajo_propio(tid, "revisar")
    return jsonify(editar.resumen(json.loads(r["guion"])))


@app.post("/api/guion/<tid>")
def confirmar_guion(tid):
    """Guarda las correcciones y manda el vídeo a hacer."""
    r = trabajo_propio(tid, "revisar")
    try:
        caso, avisos = editar.aplicar(json.loads(r["guion"]), request.get_json(silent=True) or {})
    except ValueError as e:
        return jsonify(error=str(e)), 400
    with con() as c:
        n = c.execute("UPDATE trabajos SET guion=?, titulo=?, descripcion=?, estado='en cola', paso='Esperando turno' "
                      "WHERE id=? AND estado='revisar'",
                      (json.dumps(caso, ensure_ascii=False), caso["titulo_youtube"], caso["descripcion"], tid)).rowcount
    if not n:
        return jsonify(error="Este guion ya se había enviado."), 409
    return jsonify(ok=True, avisos=avisos)


@app.post("/api/cancelar/<tid>")
def cancelar(tid):
    """Descartar un guion que no gusta: el vídeo no se hace y no gasta crédito."""
    trabajo_propio(tid, "revisar")
    with con() as c:
        c.execute("UPDATE trabajos SET estado='cancelado', paso='Descartado' WHERE id=? AND estado='revisar'", (tid,))
    return jsonify(ok=True)


@app.get("/archivo/<tid>/<tipo>")
def archivo(tid, tipo):
    u = usuario_actual()
    if tipo not in ("video", "miniatura") or not re.fullmatch(r"[a-f0-9]{12}", tid):
        abort(404)
    if not u:
        abort(403)
    r = con().execute("SELECT slug, estado FROM trabajos WHERE id=? AND usuario_id=?", (tid, u["id"])).fetchone()
    if not r or r["estado"] != "listo" or not r["slug"]:
        abort(404)                                         # de otro usuario o aún no está: no existe para ti
    nombre = f"{r['slug']}.mp4" if tipo == "video" else f"miniatura-{r['slug']}.png"
    return send_from_directory(SALIDA, nombre, as_attachment="descargar" in request.args)



# ───────────────────────────── lista de espera ─────────────────────────────
ENVIOS_LISTA = {}          # ip → [momentos]: frena a quien intente llenar la lista con basura


@app.route("/lista-espera", methods=["GET", "POST"])
def lista_espera():
    if request.method == "POST":
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0]).strip()
        ahora = db.ahora()
        ENVIOS_LISTA[ip] = [t for t in ENVIOS_LISTA.get(ip, []) if ahora - t < 3600]
        if len(ENVIOS_LISTA[ip]) >= 5:
            flash("Demasiados envíos seguidos. Prueba dentro de un rato.")
            return render_template("lista.html"), 429
        email = request.form.get("email", "").strip().lower()
        if not re.fullmatch(r"[^@\s]{1,64}@[^@\s]{1,190}\.[a-z]{2,}", email) or not request.form.get("acepto"):
            flash("Escribe un email válido y acepta la política de privacidad.")
            return render_template("lista.html"), 400
        canal = request.form.get("canal", "").strip()[:120]
        pagaria = request.form.get("pagaria") if request.form.get("pagaria") in ("si", "quiza", "no") else None
        ENVIOS_LISTA[ip].append(ahora)
        with con() as c:
            c.execute("INSERT INTO lista_espera (email, canal, pagaria, creado) VALUES (?, ?, ?, ?) "
                      "ON CONFLICT(email) DO UPDATE SET canal=excluded.canal, pagaria=excluded.pagaria",
                      (email, canal, pagaria, ahora))
        return render_template("lista.html", hecho=True)
    total = con().execute("SELECT COUNT(*) FROM lista_espera").fetchone()[0]
    return render_template("lista.html", total=total)


@app.get("/admin/lista.csv")
def exportar_lista():
    """La lista de espera en CSV (se abre con Excel o Google Sheets). Solo para CR_ADMIN_EMAIL."""
    u = usuario_actual()
    if not ADMIN or not u or u["email"] != ADMIN:
        abort(404)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["email", "canal", "pagaria", "fecha"])
    import datetime
    for r in con().execute("SELECT * FROM lista_espera ORDER BY creado"):
        w.writerow([r["email"], r["canal"] or "", r["pagaria"] or "",
                    datetime.datetime.fromtimestamp(r["creado"]).strftime("%Y-%m-%d %H:%M")])
    return out.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8",
                                 "Content-Disposition": "attachment; filename=lista-espera.csv"}


# ───────────────────────────── recuperar contraseña ─────────────────────────────
def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        clave_fallo = ("recuperar", (request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0]))
        if bloqueado(clave_fallo):
            flash("Demasiadas peticiones. Espera 15 minutos.")
            return render_template("cuenta.html", modo="recuperar"), 429
        FALLOS.setdefault(clave_fallo, []).append(db.ahora())
        u = con().execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
        if u:
            token = secrets.token_urlsafe(32)
            with con() as c:
                c.execute("INSERT INTO recuperar (token_hash, usuario_id, caduca) VALUES (?, ?, ?)",
                          (_hash(token), u["id"], db.ahora() + 3600))
            enlace = f"{URL_BASE}/recuperar/{token}"
            try:
                correo.enviar(email, "Cambia tu contraseña de Caso Recortado Studio",
                              f"Hola:\n\nPara poner una contraseña nueva, abre este enlace (caduca en 1 hora):\n\n{enlace}\n\n"
                              "Si no lo has pedido tú, ignora este email: tu contraseña no cambia.\n")
            except Exception:
                app.logger.exception("No se pudo enviar el email de recuperación")
        # siempre el mismo mensaje: así nadie puede averiguar qué emails tienen cuenta
        flash("Si ese email tiene cuenta, te hemos enviado un enlace para cambiar la contraseña. Mira también en spam.")
        return redirect(url_for("entrar"))
    return render_template("cuenta.html", modo="recuperar")


@app.route("/recuperar/<token>", methods=["GET", "POST"])
def nueva_clave(token):
    c = con()
    r = c.execute("SELECT * FROM recuperar WHERE token_hash=?", (_hash(token),)).fetchone()
    if not r or r["usado"] or r["caduca"] < db.ahora():
        flash("El enlace ha caducado o ya se usó. Pide otro.")
        return redirect(url_for("recuperar"))
    if request.method == "POST":
        clave = request.form.get("clave", "")
        if len(clave) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.")
            return render_template("cuenta.html", modo="nueva"), 400
        with c:
            c.execute("UPDATE usuarios SET clave_hash=? WHERE id=?", (generate_password_hash(clave), r["usuario_id"]))
            c.execute("UPDATE recuperar SET usado=1 WHERE usuario_id=?", (r["usuario_id"],))
        session.clear()
        session.permanent = True
        session["uid"] = r["usuario_id"]
        flash("Contraseña cambiada. Ya estás dentro.")
        return redirect(url_for("inicio"))
    return render_template("cuenta.html", modo="nueva")


# ───────────────────────────── mi cuenta ─────────────────────────────
@app.get("/cuenta")
def mi_cuenta():
    u = usuario_actual()
    if not u:
        return redirect(url_for("entrar"))
    lista = None
    if ADMIN and u["email"] == ADMIN:
        c = con()
        lista = dict(total=c.execute("SELECT COUNT(*) FROM lista_espera").fetchone()[0],
                     si=c.execute("SELECT COUNT(*) FROM lista_espera WHERE pagaria='si'").fetchone()[0],
                     quiza=c.execute("SELECT COUNT(*) FROM lista_espera WHERE pagaria='quiza'").fetchone()[0])
    return render_template("micuenta.html", lista=lista)


@app.post("/cuenta/clave")
def cambiar_clave():
    u = usuario_actual()
    if not u:
        abort(403)
    if not check_password_hash(u["clave_hash"], request.form.get("actual", "")):
        flash("La contraseña actual no es correcta.")
        return redirect(url_for("mi_cuenta"))
    nueva = request.form.get("nueva", "")
    if len(nueva) < 8:
        flash("La contraseña nueva debe tener al menos 8 caracteres.")
        return redirect(url_for("mi_cuenta"))
    with con() as c:
        c.execute("UPDATE usuarios SET clave_hash=? WHERE id=?", (generate_password_hash(nueva), u["id"]))
    flash("Contraseña cambiada.")
    return redirect(url_for("mi_cuenta"))


@app.post("/cuenta/borrar")
def borrar_cuenta():
    """Borra la cuenta, sus vídeos y cancela la suscripción (derecho de supresión del RGPD)."""
    u = usuario_actual()
    if not u:
        abort(403)
    if request.form.get("confirmo") != "BORRAR" or not check_password_hash(u["clave_hash"], request.form.get("clave", "")):
        flash("Para borrar la cuenta escribe BORRAR y tu contraseña.")
        return redirect(url_for("mi_cuenta"))
    if u["stripe_suscripcion"] and stripe:
        try:
            stripe.Subscription.cancel(u["stripe_suscripcion"])
        except Exception:
            app.logger.exception("No se pudo cancelar la suscripción al borrar la cuenta")
            flash("No hemos podido cancelar tu suscripción automáticamente. Escríbenos y la cancelamos a mano; "
                  "tu cuenta no se ha borrado todavía.")
            return redirect(url_for("mi_cuenta"))
    c = con()
    for r in c.execute("SELECT slug FROM trabajos WHERE usuario_id=? AND slug IS NOT NULL", (u["id"],)).fetchall():
        for ruta in (os.path.join(SALIDA, f"{r['slug']}.mp4"), os.path.join(SALIDA, f"miniatura-{r['slug']}.png"),
                     os.path.join(fabrica.CASOS, f"{r['slug']}.json")):
            if os.path.exists(ruta):
                os.remove(ruta)
    with c:
        c.execute("DELETE FROM recuperar WHERE usuario_id=?", (u["id"],))
        c.execute("DELETE FROM trabajos WHERE usuario_id=?", (u["id"],))
        c.execute("DELETE FROM usuarios WHERE id=?", (u["id"],))
    session.clear()
    flash("Tu cuenta y tus vídeos se han borrado. ¡Gracias por probar Caso Recortado Studio!")
    return redirect(url_for("inicio"))

# ───────────────────────────── pagos (Stripe) ─────────────────────────────
@app.post("/pago/<plan>")
def pagar(plan):
    u = usuario_actual()
    if not u:
        return redirect(url_for("registro"))
    if plan not in PRECIOS or not PAGOS_ACTIVOS:
        flash("Los pagos aún no están activos.")
        return redirect(url_for("inicio") + "#precios")
    datos = dict(
        mode="subscription",
        line_items=[{"price": PRECIOS[plan], "quantity": 1}],
        client_reference_id=str(u["id"]),
        metadata={"plan": plan, "usuario_id": str(u["id"])},
        subscription_data={"metadata": {"plan": plan, "usuario_id": str(u["id"])}},
        success_url=URL_BASE + "/?pago=ok#crear-sec",
        cancel_url=URL_BASE + "/#precios",
        allow_promotion_codes=True,
    )
    if u["stripe_cliente"]:
        datos["customer"] = u["stripe_cliente"]           # o uno o el otro, nunca los dos
    else:
        datos["customer_email"] = u["email"]
    s = stripe.checkout.Session.create(**datos)
    return redirect(s.url, code=303)


@app.post("/pago/portal")
def portal():
    u = usuario_actual()
    if not u or not u["stripe_cliente"] or not PAGOS_ACTIVOS:
        return redirect(url_for("inicio") + "#precios")
    s = stripe.billing_portal.Session.create(customer=u["stripe_cliente"], return_url=URL_BASE + "/#precios")
    return redirect(s.url, code=303)


def _plan_de(obj):
    """Plan de una suscripción o pago: primero por el precio contratado (así funciona el cambio de plan desde el
    portal de Stripe, que no toca los metadatos) y, si no, por los metadatos que pusimos al crear el pago."""
    por_precio = {v: k for k, v in PRECIOS.items() if v}
    for item in ((obj.get("items") or {}).get("data") or []):
        pid = (item.get("price") or {}).get("id")
        if pid in por_precio:
            return por_precio[pid]
    p = (obj.get("metadata") or {}).get("plan")
    return p if p in PRECIOS else None


@app.post("/stripe/webhook")
def webhook():
    secreto = STRIPE["STRIPE_WEBHOOK_SECRET"]
    if not secreto or _stripe_webhook is None:
        abort(404)
    try:
        ev = _stripe_webhook.Webhook.construct_event(request.get_data(), request.headers.get("Stripe-Signature", ""), secreto)
    except Exception:
        abort(400)
    ev = ev.to_dict() if hasattr(ev, "to_dict") else dict(ev)
    obj, tipo = ev["data"]["object"], ev["type"]
    c = con()
    with c:
        try:
            c.execute("INSERT INTO pagos (evento_id, tipo, recibido) VALUES (?, ?, ?)", (ev["id"], tipo, db.ahora()))
        except sqlite3.IntegrityError:
            return jsonify(ok=True, repetido=True)       # Stripe puede reenviar un evento: se ignora
        uid = None
        if tipo == "checkout.session.completed":
            uid = int(obj.get("client_reference_id") or (obj.get("metadata") or {}).get("usuario_id") or 0) or None
            plan = _plan_de(obj)
            if uid and plan:
                c.execute("UPDATE usuarios SET plan=?, periodo_inicio=?, stripe_cliente=?, stripe_suscripcion=? WHERE id=?",
                          (plan, db.ahora(), obj.get("customer"), obj.get("subscription"), uid))
        elif tipo in ("customer.subscription.updated", "customer.subscription.deleted"):
            r = c.execute("SELECT id FROM usuarios WHERE stripe_cliente=?", (obj.get("customer"),)).fetchone()
            if r:
                uid = r["id"]
                activo = tipo.endswith("updated") and obj.get("status") in ("active", "trialing")
                plan = _plan_de(obj) if activo else None
                c.execute("UPDATE usuarios SET plan=?, stripe_suscripcion=? WHERE id=?",
                          (plan or "gratis", obj.get("id") if activo else None, uid))
        elif tipo == "invoice.paid":
            r = c.execute("SELECT id FROM usuarios WHERE stripe_cliente=?", (obj.get("customer"),)).fetchone()
            if r:                                          # nuevo mes pagado: se renuevan los vídeos
                uid = r["id"]
                c.execute("UPDATE usuarios SET periodo_inicio=? WHERE id=?", (db.ahora(), uid))
        c.execute("UPDATE pagos SET usuario_id=? WHERE evento_id=?", (uid, ev["id"]))
    return jsonify(ok=True)


if __name__ == "__main__":
    import worker                                         # en desarrollo, el obrero va dentro (en un hilo)
    threading.Thread(target=worker.bucle, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), threaded=True)
