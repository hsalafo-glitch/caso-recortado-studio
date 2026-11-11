#!/usr/bin/env python3
"""Alineación texto-audio sin servicios externos (plan B si la transcripción de ElevenLabs no está disponible).

Detecta los silencios reales del audio (ffmpeg silencedetect), los empareja con los signos de
puntuación del guion (programación dinámica monótona) y reparte cada tramo entre sus palabras
según su número de sílabas. Precisión típica: ±0,1-0,2 s por palabra, suficiente para
subtítulos palabra a palabra y cambios de escena.

Uso: python alinear_texto.py audio.mp3 salida.json  "texto completo..."
     (o desde código: alinear(mp3, texto) -> lista de {text,start,end})
"""
import json
import math
import re
import subprocess
import sys
import unicodedata

NUM = {"500": "quinientos", "10": "diez", "14": "catorce", "16": "dieciseis", "6": "seis", "13": "trece",
       "1989": "mil novecientos ochenta y nueve", "2002": "dos mil dos",
       "65": "sesenta y cinco por ciento", "450": "cuatrocientos cincuenta", "1961": "mil novecientos sesenta y uno",
       "2006": "dos mil seis", "200": "doscientos", "54": "cincuenta y cuatro por ciento",
       "2012": "dos mil doce", "100": "cien", "50": "cincuenta"}
SIGLAS = {"sms": 4, "adn": 3}


UNI = "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis \
diecisiete dieciocho diecinueve veinte".split()
DEC = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
CEN = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos",
       7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def numero(n):
    """Número en palabras (aprox., solo para contar sílabas)."""
    if n <= 20:
        return UNI[n]
    if n < 30:
        return "veinti" + UNI[n - 20]
    if n < 100:
        return DEC[n // 10] + ("" if n % 10 == 0 else " y " + UNI[n % 10])
    if n < 1000:
        return ("cien" if n == 100 else CEN[n // 100]) + ("" if n % 100 == 0 else " " + numero(n % 100))
    mil = "mil" if n // 1000 == 1 else numero(n // 1000) + " mil"
    return mil + ("" if n % 1000 == 0 else " " + numero(n % 1000))


def silabas(w):
    core = re.sub(r"[^\w]", "", w.lower())
    if core in NUM:
        core = NUM[core]
    elif core.isdigit() and len(core) <= 6:
        core = numero(int(core))
    if "%" in w:
        core += " por ciento"
    if core in SIGLAS:
        return SIGLAS[core]
    core = "".join(c for c in unicodedata.normalize("NFD", core) if unicodedata.category(c) != "Mn")
    n = len(re.findall(r"[aeiouy]+", core))
    return max(1, n)


def silencios(mp3, db=-36, d=0.14):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp3, "-af", f"silencedetect=noise={db}dB:d={d}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = float(re.findall(r"Duration: (\d+):(\d+):([\d.]+)", out)[0][2]) + \
        60 * float(re.findall(r"Duration: (\d+):(\d+):([\d.]+)", out)[0][1])
    sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
    return sil, dur


def alinear(mp3, texto):
    words = texto.split()
    wts = [silabas(w) + 0.35 for w in words]
    sil, dur = silencios(mp3)
    t0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    t1 = sil[-1][0] if sil and sil[-1][1] >= dur - 0.05 else dur
    inner = [s for s in sil if s[0] > t0 + 0.05 and s[1] < t1 - 0.05]
    # fronteras candidatas: tras palabras con puntuación (peso según signo)
    bnd = []
    for i, w in enumerate(words[:-1]):
        if re.search(r"[.?!…]\"?$|\.\"$", w):
            bnd.append((i, 3.0))
        elif re.search(r"[:;]\"?$", w):
            bnd.append((i, 2.0))
        elif re.search(r",\"?$", w):
            bnd.append((i, 1.2))
        elif w.endswith('"'):
            bnd.append((i, 0.8))
    total_w = sum(wts)
    cum = []
    acc = 0
    for x in wts:
        acc += x
        cum.append(acc / total_w)
    speech = (t1 - t0) - sum(e - s for s, e in inner)

    def frac_time(t):
        sp = (t - t0) - sum(min(e, t) - s for s, e in inner if s < t)
        return sp / speech

    cw = [0.0]
    for x in wts:
        cw.append(cw[-1] + x)

    def emparejar(bnd_sub, sil_sub, aw, at, rate):
        """Cada silencio se asigna a la frontera cuya hora prevista (ritmo `rate` desde el último
        ancla) está más cerca; si ninguna encaja, es una pausa dentro de la frase."""
        pares = []
        for sj in sil_sub:
            ss, se = inner[sj]
            best = None
            for bi, pw in bnd_sub:
                if bi <= aw:
                    continue
                pred = at + (cw[bi + 1] - cw[aw + 1]) * rate
                sd = se - ss
                err = abs(pred - ss) - 0.12 * pw + 0.6 * abs(min(pw, 3) / 3 - min(sd, 0.6) / 0.6)
                if pred > ss + 2.5:
                    break
                if best is None or err < best[0]:
                    best = (err, bi, pred)
            if best is None:
                continue
            if abs(best[2] - ss) <= 0.45 + 0.2 * (ss - at):
                pares.append((best[1], sj))
                aw, at = best[1], se
        return pares

    # Programación dinámica: elige qué pausas reales corresponden a qué signos de puntuación.
    # Coste = ritmo irregular entre anclas + pausas largas «tragadas» dentro de una frase
    #       + puntos sin pausa + desajuste entre la fuerza del signo y la duración de la pausa.
    rate = speech / total_w
    nS = len(inner)
    durs = [b - a for a, b in inner]
    pw_de = dict(bnd)
    B = [b[0] for b in bnd]

    def coste_tramo(aw, at, bw, bt, s_lo, s_hi, b_lo, b_hi):
        w = cw[bw + 1] - cw[aw + 1]
        habla = (bt - at) - sum(durs[k] for k in range(s_lo, s_hi))
        if w <= 0 or habla <= 0.05:
            return 1e9
        c = 6.0 * math.log(habla / (w * rate)) ** 2
        c += sum(1.5 * min(durs[k], 0.8) for k in range(s_lo, s_hi))          # pausas dentro de frase
        c += sum({3.0: 0.9, 2.0: 0.5}.get(bnd[k][1], 0.08) for k in range(b_lo, b_hi))  # signos sin pausa
        return c

    INF = float("inf")
    best = {(-1, -1): (0.0, None)}          # (índice en bnd, índice en inner) → (coste, previo)
    estados = [(-1, -1)]
    for bi in range(len(B)):
        for sj in range(nS):
            sd = durs[sj]
            ajuste = 0.8 * abs(min(pw_de[B[bi]], 3) / 3 - min(sd, 0.6) / 0.6)
            mejor = (INF, None)
            for (pb, ps) in estados:
                if pb >= bi or ps >= sj:
                    continue
                c0 = best[(pb, ps)][0]
                if c0 >= mejor[0]:
                    continue
                aw = -1 if pb < 0 else B[pb]
                at = t0 if ps < 0 else inner[ps][1]
                c = c0 + ajuste + coste_tramo(aw, at, B[bi], inner[sj][0], ps + 1, sj, pb + 1, bi)
                if c < mejor[0]:
                    mejor = (c, (pb, ps))
            if mejor[0] < INF:
                best[(bi, sj)] = mejor
                estados.append((bi, sj))
    fin = (INF, None)
    for (pb, ps), (c0, _) in best.items():
        aw = -1 if pb < 0 else B[pb]
        at = t0 if ps < 0 else inner[ps][1]
        c = c0 + coste_tramo(aw, at, len(words) - 1, t1, ps + 1, nS, pb + 1, len(B))
        if c < fin[0]:
            fin = (c, (pb, ps))
    pairs = []
    cur = fin[1]
    while cur and cur != (-1, -1):
        pairs.append((B[cur[0]], cur[1]))
        cur = best[cur][1]
    pairs.reverse()
    # tramos: [t0 .. silencio1] [fin silencio1 .. silencio2] ...
    anchors = [(-1, t0)] + [(wi, inner[sj]) for wi, sj in pairs] + [(len(words) - 1, t1)]
    out = []
    for a in range(len(anchors) - 1):
        wa, A = anchors[a]
        wb, B = anchors[a + 1]
        start = A if a == 0 else A[1]
        end = B[0] if isinstance(B, tuple) else B
        seg = list(range(wa + 1, wb + 1))
        sw = sum(wts[k] for k in seg)
        t = start
        for k in seg:
            d = (end - start) * wts[k] / sw
            out.append(dict(text=words[k], start=round(t, 3), end=round(t + d * 0.92, 3)))
            t += d
    return out


if __name__ == "__main__":
    mp3, js, texto = sys.argv[1], sys.argv[2], sys.argv[3]
    w = alinear(mp3, texto)
    json.dump(dict(fuente="alineación local (silencios + sílabas)", palabras=w), open(js, "w"),
              ensure_ascii=False, indent=1)
    print(len(w), "palabras")
