"""Revisar y corregir el guion antes de hacer el vídeo.

El usuario solo cambia textos (lo que dice la voz en cada parte, el título y la descripción). Las escenas se
sincronizan con palabras de la voz («cues»): si una corrección borra una de esas palabras, la escena o el rótulo
que dependía de ella se quita o se mueve al principio de su parte, para que el vídeo nunca se rompa.
"""
import copy
import re
import unicodedata

MAX_PALABRAS_TOTAL = 150          # ≈ 59 s de voz
MAX_PALABRAS_PARTE = 60


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^\w\-]", "", s)


def contiene(voz, cue):
    """¿Aparece la frase clave (palabras seguidas) en el texto de la voz?"""
    if not cue:
        return True
    t = [norm(w) for w in voz.split()]
    c = [norm(w) for w in cue.split()]
    c = [w for w in c if w]
    return any(t[i:i + len(c)] == c for i in range(len(t) - len(c) + 1)) if c else True


def resumen(caso):
    return dict(titulo=caso.get("titulo_youtube", ""), descripcion=caso.get("descripcion", ""),
                partes=[b[0] for b in caso["bloques"]])


def aplicar(caso, cambios):
    """Devuelve (caso_nuevo, avisos). Lanza ValueError con un mensaje para el usuario si algo no vale."""
    partes = cambios.get("partes")
    if not isinstance(partes, list) or len(partes) != len(caso["bloques"]):
        raise ValueError("El guion tiene que tener las mismas partes.")
    partes = [re.sub(r"\s+", " ", str(p)).strip() for p in partes]
    for i, p in enumerate(partes, 1):
        n = len(p.split())
        if n < 3:
            raise ValueError(f"La parte {i} está casi vacía: escribe al menos una frase.")
        if n > MAX_PALABRAS_PARTE:
            raise ValueError(f"La parte {i} es muy larga ({n} palabras). Máximo {MAX_PALABRAS_PARTE}.")
    total = sum(len(p.split()) for p in partes)
    if total > MAX_PALABRAS_TOTAL:
        raise ValueError(f"El guion tiene {total} palabras y no cabría en un short de 59 s. Quita unas "
                         f"{total - MAX_PALABRAS_TOTAL}.")
    titulo = re.sub(r"\s+", " ", str(cambios.get("titulo", caso.get("titulo_youtube", "")))).strip()[:100]
    desc = str(cambios.get("descripcion", caso.get("descripcion", ""))).strip()[:2000]
    if len(titulo) < 3:
        raise ValueError("Escribe un título.")

    nuevo = copy.deepcopy(caso)
    nuevo["titulo_youtube"], nuevo["descripcion"] = titulo, desc
    avisos = []
    for i, (bloque, voz) in enumerate(zip(nuevo["bloques"], partes), 1):
        bloque[0] = voz
        escenas, rotulos, eventos = bloque[1], bloque[2], bloque[3]
        # eventos (sellos, sacudidas…): si su frase ya no está, se quitan
        perdidos = {k for k, cue in eventos.items() if not contiene(voz, cue)}
        for k in perdidos:
            del eventos[k]
        # escenas: la primera siempre empieza con la parte; las demás, si pierden su frase, se quitan
        quedan = []
        for j, (cue, tipo, p) in enumerate(escenas):
            if j > 0 and not contiene(voz, cue):
                avisos.append(f"Parte {i}: se ha quitado una escena porque ya no se dice «{cue}».")
                continue
            if p.get("st") and p["st"][0] in perdidos:
                p = dict(p)
                p.pop("st")
            if p.get("sacudida") in perdidos:
                p = dict(p)
                p.pop("sacudida")
            quedan.append([None if j == 0 else cue, tipo, p])
        bloque[1] = quedan
        bloque[2] = [[cue, txt] for k, (cue, txt) in enumerate(rotulos) if k == 0 or contiene(voz, cue)]
        if len(bloque[2]) < len(rotulos):
            avisos.append(f"Parte {i}: se ha quitado un rótulo porque ya no se dice su frase.")
    return nuevo, avisos
