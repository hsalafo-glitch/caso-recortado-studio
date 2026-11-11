"""El guionista: convierte un tema en un guion de short listo para la fábrica (formato de lote14).

Usa Claude con salida estructurada. Después comprueba que el guion encaja con el motor
(cues que existen en la voz, sellos con su evento, longitud...) y, si algo falla, se lo
devuelve a Claude una vez para que lo corrija.
"""
import json
import os
import re
import unicodedata
from typing import List, Literal, Optional

import sys

import anthropic
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import animaciones  # noqa: E402  (entradas, movimientos y cámara)
import estilos  # noqa: E402  (estilo visual del vídeo entero)
import iconos  # noqa: E402  (biblioteca de dibujos generales)
import personaje  # noqa: E402  (el narrador animado)

# Claude Sonnet: buenos guiones a la mitad de precio que Opus (lo eligió el dueño para que salga rentable).
# Para volver a Opus, en web/.env: CR_MODELO_GUION=claude-opus-5-5
MODELO = os.environ.get("CR_MODELO_GUION", "claude-sonnet-5-5")
ICONOS_CASOS = ["joya", "corona", "saco", "oro", "cuadro", "grito", "trofeo", "billetes", "carta", "tren",
                "avion", "carrito", "taladro", "nota", "edificio", "rejas", "camion", "graficas", "lupa"]
NOMBRES = ICONOS_CASOS + [k for k in iconos.DIBUJOS if k not in ICONOS_CASOS]
ICONOS = Literal[tuple(NOMBRES)]
LISTA_ICONOS = "\n".join(f"- {cat}: {', '.join(n.split())}" for cat, n in iconos.CATEGORIAS.items())


# ───────────── forma del guion que debe devolver Claude ─────────────
class Sello(BaseModel):
    evento: str = Field(description="clave de uno de los eventos del mismo bloque")
    texto: str = Field(description="texto del sello, MAYÚSCULAS, máx. 18 caracteres")


class Item(BaseModel):
    texto: str = Field(description="lista: frase corta (máx. 22 car.); barras: nombre corto (máx. 10); linea: año o fecha")
    ico: Optional[ICONOS] = Field(default=None, description="lista y linea: dibujo del elemento")
    valor: Optional[float] = Field(default=None, description="solo barras: el número de la barra")


class Escena(BaseModel):
    cue: Optional[str] = Field(default=None, description="null en la primera escena del bloque; si no, 1-3 palabras exactas de la voz donde empieza")
    tipo: Literal["personaje", "texto", "icono", "comparar", "proceso", "lista", "barras", "linea", "siluetas", "contador", "carcel", "pregunta"]
    ico: Optional[ICONOS] = None
    ico2: Optional[ICONOS] = Field(default=None, description="comparar y proceso: segundo icono")
    ico3: Optional[ICONOS] = Field(default=None, description="solo proceso: tercer icono (opcional)")
    label2: Optional[str] = Field(default=None, description="solo comparar: etiqueta del segundo icono")
    sello: Optional[Sello] = None
    label: Optional[str] = Field(default=None, description="icono, comparar o proceso: texto corto bajo el dibujo")
    n: Optional[int] = Field(default=None, description="solo siluetas: cuántas (1-4)")
    cada: Optional[str] = Field(default=None, description="solo siluetas: sello sobre cada una, p. ej. DETENIDO")
    valor: Optional[float] = Field(default=None, description="solo contador: número que sube")
    unidad: Optional[str] = Field(default=None, description="solo contador: p. ej. MILLONES €")
    noche: Optional[bool] = None
    dia: Optional[bool] = Field(default=None, description="fondo de color alegre en vez de azul oscuro")
    items: Optional[List[Item]] = Field(default=None, description="lista, barras y linea: 2-4 elementos")
    entrada: Optional[Literal[tuple(animaciones.ENTRADAS)]] = Field(default=None, description="cómo aparecen los dibujos")
    movimiento: Optional[Literal[tuple(animaciones.MOVIMIENTOS)]] = Field(default=None, description="qué hacen los dibujos después")
    camara: Optional[Literal[tuple(animaciones.CAMARAS)]] = Field(default=None, description="zoom lento de toda la escena")
    gesto: Optional[Literal[tuple(personaje.GESTOS)]] = Field(default=None, description="solo personaje: qué hace el narrador")
    bocadillo: Optional[str] = Field(default=None, description="solo personaje: lo que dice, MAYÚSCULAS, máx. 20 caracteres")
    lineas: Optional[List[str]] = Field(default=None, description="solo texto: 1-4 líneas, MAYÚSCULAS, máx. 14 caracteres cada una")
    transicion: Optional[Literal[tuple(animaciones.TRANSICIONES)]] = Field(default=None, description="cómo se entra a esta escena desde la anterior")
    sacudida: Optional[str] = Field(default=None, description="clave de un evento del bloque: la escena tiembla al decirlo")


class Rotulo(BaseModel):
    cue: Optional[str] = Field(default=None, description="null el primero del bloque; si no, 1-3 palabras exactas de la voz")
    texto: str = Field(description="MAYÚSCULAS, máx. 26 caracteres")


class Evento(BaseModel):
    clave: str = Field(description="nombre corto, una palabra")
    cue: str = Field(description="1-3 palabras exactas de la voz de este bloque")


class Bloque(BaseModel):
    voz: str
    escenas: List[Escena]
    rotulos: List[Rotulo]
    eventos: List[Evento]


class Pronuncia(BaseModel):
    palabra: str
    como_suena: str


class Mapa(BaseModel):
    pais_iso3: str
    ciudad: str = Field(description="MAYÚSCULAS")
    lon: float
    lat: float


class Guion(BaseModel):
    rechazo: Optional[str] = Field(default=None, description="solo si el tema no se puede hacer: motivo breve; entonces el resto puede ir vacío")
    slug: str = Field(description="minúsculas y guiones, 2-4 palabras")
    titulo_miniatura: List[str] = Field(description="exactamente 3 líneas cortas en MAYÚSCULAS")
    titulo_youtube: str
    descripcion: str = Field(description="2 frases + 4-5 hashtags")
    estilo_visual: Optional[Literal[tuple(estilos.ESTILOS)]] = Field(default=None, description="lo elige el usuario; si no, null")
    mapa: Optional[Mapa] = Field(default=None, description="solo si el tema ocurre en un lugar concreto")
    bloques: List[Bloque]
    pronuncia: List[Pronuncia]


SISTEMA = f"""Eres el guionista de «Caso Recortado Studio»: shorts verticales de 35-45 segundos con animación de \
recortes de papel y voz en off en español de España. El tema puede ser cualquiera que pida el usuario: casos reales, \
historia, ciencia, curiosidades, negocios, deporte, explicaciones, «qué pasaría si»... Si es ficción o hipotético, \
dilo claramente en la voz.

Formato de cada guion: EXACTAMENTE 5 bloques y entre 95 y 120 palabras de voz en total.
1. Gancho: una pregunta o frase que obligue a seguir viendo (sin fecha ni lugar).
2. Contexto. Si el tema ocurre en un lugar concreto, rellena «mapa» y empieza este bloque con el lugar y el año \
(«París, octubre de 2025.»): se muestra un mapa ~3 s, así que la primera escena de este bloque no tiene sello y no \
hay eventos ni rótulos en sus primeras 6 palabras. Si no hay un lugar concreto, deja «mapa» en null.
3. Desarrollo: cómo pasó / cómo funciona.
4. El dato más impactante y cómo terminó.
5. Cierre con una pregunta al espectador para que comente.

Escenas (cada bloque tiene 1-2; la primera con cue null). Tipos disponibles:
- personaje: el narrador del canal entra andando y hace un gesto (gesto: saluda, senala, piensa, sorpresa, celebra, \
triste, explica, corre). Opcional: ico (lo que enseña o señala, a su derecha) y bocadillo (lo que dice). Úsalo en el \
gancho y en 1-2 momentos más: un personaje constante hace que la gente se quede.
- texto: texto cinético, 1-4 líneas enormes que entran una tras otra (lineas). Para la frase clave o el dato del vídeo; \
la última línea sale destacada. No repitas el rótulo: el rótulo de esa escena debe decir otra cosa o ser muy corto.
- icono: un dibujo grande (ico obligatorio). Opcional label y sello.
- comparar: dos dibujos frente a frente con un «VS» (ico, ico2, label, label2). Ideal para «antes/después», «mito/realidad», «A contra B».
- proceso: 2-3 dibujos que aparecen uno tras otro con flechas (ico, ico2, ico3, label). Ideal para «cómo funciona» o causa → efecto.
- lista: un top de 2-4 filas numeradas que entran una tras otra (items con texto + ico). Ideal para «3 razones», «los 4 más…».
- barras: gráfica de 2-4 barras que crecen (items con texto + valor; unidad opcional). Ideal para comparar cifras.
- linea: línea del tiempo con 2-4 hitos (items con texto = año + ico). Ideal para historia o evolución.
- siluetas: personas sin rasgos (n 1-4); opcional ico encima y cada (sello sobre cada persona).
- contador: un número que sube (valor y unidad obligatorios, ico opcional).
- carcel: unos barrotes; sello opcional.
- pregunta: un gran «?» con un icono; úsala en el bloque 5.
Varía los tipos de escena: no pongas solo «icono».
Dibujos disponibles (ico, ico2, ico3), elige el que mejor ilustre lo que dice la voz en ese momento:
- crimen y dinero: joya, corona, saco, oro, cuadro, grito (el cuadro de El Grito), trofeo, billetes, carta, tren, \
avion, carrito, taladro, nota, edificio, rejas, camion, graficas, lupa
{LISTA_ICONOS}
(zancuda = ave de patas largas como flamenco o garza; senal = wifi/señal; sube/baja = flechas; check/cruz = sí/no.)
Si ningún dibujo encaja, usa el más cercano y concreta con label, rótulos y sellos.
Animación (opcional en cada escena; si no la pones, el dibujo entra con «pop» y se queda quieto):
- entrada: pop (salta), cae (cae y rebota), desliza (entra de lado), sube (desde abajo), gira, zoom (de grande a normal), \
aparece (sin efecto), rebota (crece como un muelle), voltea (gira como una carta: revelaciones), despliega (se abre como \
un papel doblado: listas, mapas, documentos), lanza (entra volando en arco: objetos que se tiran o llegan), estira (goma \
elástica: cosas blandas o graciosas).
- movimiento: ninguno, flota, late (como un corazón), balancea, gira (planetas, engranajes, relojes), tiembla (miedo, frío, \
peligro), salta (alegría, con impulso y aterrizaje), respira (vida tranquila: animales, plantas, personas), pendulo \
(colgado: relojes, columpios, dudas), orbita (alrededor de algo: lunas, electrones), brinca (botecitos alegres).
- camara: acercar o alejar (zoom lento; tensión o calma), deriva (cámara en mano, muy sutil: misterio, documental), paneo \
(recorre la escena de lado: paisajes, comparaciones).
- sacudida: la clave de un evento del bloque; la pantalla tiembla cuando la voz lo dice (impactos, explosiones, sorpresas).
- transicion: cómo se pasa de la escena anterior a esta: corte (por defecto), barrido (cortinilla diagonal), empuje \
(la nueva empuja a la vieja), zoom (se atraviesa la anterior), iris (círculo que se abre), fundido, flash (golpe de luz), \
persiana (tiras que se cierran: listas, pasos), rasgado (la escena se rompe como un papel: giros de guion, «pero…»), \
glitch (corte digital: tecnología, errores, internet), sube (la nueva empuja desde abajo: «y además…»), giro (la \
anterior se va girando: cambios de época o de tema). \
Usa transiciones en los cambios de idea (2-4 por vídeo) y variadas; corte seco dentro de una misma idea.
El movimiento debe acompañar a la frase: acércate (camara) en la tensión, sacude en el impacto y deja la escena \
QUIETA en el remate, para que se lea. Si todo se mueve igual, es ruido.
Elige la animación que refuerce lo que dice la voz (lo que cae, cae; lo que late, late) y varía entre escenas: \
una sacudida o una cámara por vídeo como mucho en 2-3 escenas, para que no canse.
Fondo: en crímenes, misterios y temas serios deja «dia» en null (azul oscuro); en ciencia, curiosidades, animales \
y temas alegres pon dia = true.

Rótulos: 1-2 por bloque, el primero con cue null.
Un sello aparece cuando la voz dice el cue de su evento: el evento debe existir en los eventos del MISMO bloque.

Reglas de los cues (muy importantes, el programa falla si no se cumplen):
- Son 1-3 palabras copiadas EXACTAMENTE de la voz de su mismo bloque.
- Dentro de un bloque, cada cue de escenas, rótulos y eventos debe aparecer en la voz en un punto único: si la \
palabra se repite en el bloque, alarga el cue con la de al lado.
- Escribe los porcentajes pegados («65%»).

Hechos: usa solo datos reales y bien establecidos; si dudas de una cifra, redondea \
(«más de 200») o no la des. No inventes nombres ni citas.
Contenido: no describas violencia explícita ni a víctimas; las personas aparecen como siluetas. No hagas vídeos \
sobre personas privadas o menores, ni acusaciones contra alguien que no sean hechos públicos, ni contenido sexual, \
de odio, peligroso (armas, drogas, autolesiones) o desinformación. Si el tema pide eso, rellena «rechazo» con el motivo.
pronuncia: nombres extranjeros escritos como suenan en español («Louvre» → «Luvre»)."""


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return [w for w in (re.sub(r"[^\w\-]", "", x) for x in s.split()) if w]


def _pos(voz, cue):
    """Índice de palabra donde empieza el cue en la voz, o -1."""
    v, c = _norm(voz), _norm(cue)
    for i in range(len(v) - len(c) + 1):
        if c and v[i:i + len(c)] == c:
            return i
    return -1


def revisar(g: Guion):
    """Lista de problemas que harían fallar a la fábrica (vacía si está bien)."""
    err = []
    if len(g.bloques) != 5:
        err.append(f"Hay {len(g.bloques)} bloques; deben ser 5.")
    total = sum(len(b.voz.split()) for b in g.bloques)
    if not 85 <= total <= 130:
        err.append(f"La voz tiene {total} palabras; deben ser 95-120.")
    if len(g.titulo_miniatura) != 3:
        err.append("titulo_miniatura debe tener 3 líneas.")
    for bi, b in enumerate(g.bloques, 1):
        claves = {e.clave for e in b.eventos}
        cues = [("evento", e.cue) for e in b.eventos]
        for k, lista in (("escena", b.escenas), ("rótulo", b.rotulos)):
            if not lista:
                err.append(f"Bloque {bi}: no tiene ninguna {k}.")
                continue
            if lista[0].cue is not None:
                err.append(f"Bloque {bi}: la primera {k} debe tener cue null.")
            cues += [(k, x.cue) for x in lista[1:]]
        for k, c in cues:
            if not c or _pos(b.voz, c) < 0:
                err.append(f"Bloque {bi}: el cue de {k} «{c}» no está en la voz.")
        for e in b.escenas:
            if e.sello and e.sello.evento not in claves:
                err.append(f"Bloque {bi}: el sello «{e.sello.texto}» usa el evento «{e.sello.evento}», que no existe.")
            if e.tipo == "icono" and not e.ico:
                err.append(f"Bloque {bi}: una escena icono no tiene ico.")
            if e.tipo == "texto" and not (e.lineas and 1 <= len(e.lineas) <= 4):
                err.append(f"Bloque {bi}: una escena texto necesita entre 1 y 4 lineas.")
            if e.tipo == "texto" and e.lineas and any(len(x) > 16 for x in e.lineas):
                err.append(f"Bloque {bi}: en la escena texto hay líneas de más de 16 caracteres.")
            if e.bocadillo and len(e.bocadillo) > 22:
                err.append(f"Bloque {bi}: el bocadillo «{e.bocadillo}» pasa de 22 caracteres.")
            if e.tipo in ("comparar", "proceso") and not (e.ico and e.ico2):
                err.append(f"Bloque {bi}: una escena {e.tipo} necesita ico e ico2.")
            if e.tipo in ("lista", "barras", "linea") and not (e.items and 2 <= len(e.items) <= 4):
                err.append(f"Bloque {bi}: una escena {e.tipo} necesita entre 2 y 4 items.")
            if e.tipo == "barras" and e.items and any(it.valor is None for it in e.items):
                err.append(f"Bloque {bi}: todas las barras necesitan valor.")
            if e.sacudida and e.sacudida not in claves:
                err.append(f"Bloque {bi}: la sacudida usa el evento «{e.sacudida}», que no existe.")
            if e.tipo == "contador" and e.valor is None:
                err.append(f"Bloque {bi}: un contador no tiene valor.")
    return err


def _pedir(client, mensajes):
    r = client.beta.messages.parse(
        model=MODELO,
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        # Las instrucciones son siempre iguales: se guardan en caché y en las siguientes llamadas cuestan ~10 %
        system=[{"type": "text", "text": SISTEMA, "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
        messages=mensajes,
        output_format=Guion,
    )
    if r.stop_reason == "refusal":
        raise ValueError("La IA no ha querido hacer este tema. Prueba con otro caso.")
    texto = next(b.text for b in r.content if b.type == "text")
    return r.parsed_output, texto


ESTILOS = {
    "equilibrado": "",
    "muy animado": "Estilo pedido: MUY ANIMADO, tipo showreel de motion design: una técnica distinta en cada escena, "
                   "entradas variadas (cae, desliza, gira, zoom, voltea, lanza, rebota), una transición en casi cada cambio de escena, 1-2 "
                   "escenas de texto cinético, 2-3 sacudidas en los datos impactantes y alguna cámara.",
    "tranquilo": "Estilo pedido: TRANQUILO, tipo documental: entradas suaves (aparece, sube, pop), movimientos lentos "
                 "(flota, balancea, respira) o ninguno, cámara «deriva» suave, transiciones solo fundido, sin sacudidas; cámara «acercar» como mucho en una escena.",
}


def escribir(tema: str, estilo: str = "equilibrado", client=None) -> Guion:
    """Tema → Guion revisado. Lanza ValueError con un mensaje para el usuario si no se puede."""
    if client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("Falta la clave de Claude: ponla en web/.env (ANTHROPIC_API_KEY=...) o arranca en modo demo.")
        client = anthropic.Anthropic(base_url="https://api.anthropic.com")
    extra = ESTILOS.get(estilo, "")
    mensajes = [{"role": "user", "content": f"Tema del short: {tema}" + (f"\n{extra}" if extra else "")}]
    g, texto = _pedir(client, mensajes)
    if g.rechazo:
        raise ValueError(g.rechazo)
    err = revisar(g)
    if err:  # una segunda oportunidad con la lista de fallos
        mensajes += [{"role": "assistant", "content": texto},
                     {"role": "user", "content": "Corrige estos problemas y devuelve el guion completo:\n- " + "\n- ".join(err)}]
        g, _ = _pedir(client, mensajes)
        err = revisar(g)
        if err:
            raise ValueError("El guion no ha salido bien; vuelve a intentarlo. (" + err[0] + ")")
    return g


def a_lote14(g: Guion) -> dict:
    """Guion → el diccionario que entiende lote14.cargar()."""
    bloques = []
    for b in g.bloques:
        escenas = []
        for e in b.escenas:
            p = {k: v for k, v in dict(ico=e.ico, ico2=e.ico2, ico3=e.ico3, label=e.label, label2=e.label2, n=e.n,
                                         cada=e.cada, valor=e.valor, u=e.unidad, noche=e.noche, dia=e.dia,
                                         entrada=e.entrada, movimiento=e.movimiento, camara=e.camara, sacudida=e.sacudida,
                                         gesto=e.gesto, bocadillo=e.bocadillo, lineas=e.lineas, transicion=e.transicion,
                                         items=[it.model_dump(exclude_none=True) for it in e.items] if e.items else None).items()
                 if v is not None}
            if e.sello:
                p["st"] = [e.sello.evento, e.sello.texto]
            escenas.append([e.cue, e.tipo, p])
        bloques.append([b.voz, escenas, [[r.cue, r.texto] for r in b.rotulos], {e.clave: e.cue for e in b.eventos}])
    return dict(titulo=g.titulo_miniatura, mapa=[g.mapa.pais_iso3, g.mapa.ciudad, g.mapa.lon, g.mapa.lat] if g.mapa else None, bloques=bloques,
                pron={p.palabra: p.como_suena for p in g.pronuncia}, estilo=g.estilo_visual or "recortes",
                titulo_youtube=g.titulo_youtube, descripcion=g.descripcion)


if __name__ == "__main__":
    import sys
    print(json.dumps(a_lote14(escribir(" ".join(sys.argv[1:]))), ensure_ascii=False, indent=1))
