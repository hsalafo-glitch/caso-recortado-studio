"""Tiempos de cada palabra del guion escuchando la voz con Whisper (modelo «medium»).

Empareja las palabras del guion con las que oye Whisper (aunque alguna se oiga distinta: «3D» → «tres de»)
y reparte por sílabas solo los huecos que no se emparejan. Se ejecuta con el Python de la voz gratuita:
    ~/.voz_gratis_venv/bin/python tiempos_whisper.py narracion.mp3 texto.txt salida.json
"""
import difflib
import json
import re
import subprocess
import sys
import unicodedata

import numpy as np


def norm(t):
    t = unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t)


def silabas(w):
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w.lower())))


def tiempos(mp3, texto, modelo="medium", asr=None):
    """asr: un WhisperModel ya cargado (para no cargarlo dos veces)."""
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    asr = asr or WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = asr.transcribe(audio, language="es", beam_size=5, word_timestamps=True, vad_filter=False)
    oidas = [w for s in segs for w in s.words]
    # cada palabra oída se trocea en sus letras normalizadas para emparejar aunque cambie la forma de escribirla
    propias = texto.split()
    A = [norm(w) for w in propias]
    B = [norm(w.word) for w in oidas]
    res = [None] * len(propias)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                w = oidas[j1 + k]
                res[i1 + k] = [w.start, w.end]
        elif tag == "replace" and j2 > j1:
            # p. ej. «3D» ↔ «tres de»: el tramo oído se reparte entre las palabras del guion por sílabas
            t0, t1 = oidas[j1].start, oidas[j2 - 1].end
            pesos = [silabas(propias[k]) for k in range(i1, i2)]
            acc = t0
            for k, p in zip(range(i1, i2), pesos):
                d = (t1 - t0) * p / sum(pesos)
                res[k] = [acc, acc + d]
                acc += d
    # huecos sin emparejar: entre el final de la anterior y el inicio de la siguiente
    fin = float(len(audio) / 16000)
    i = 0
    while i < len(res):
        if res[i] is None:
            j = i
            while j < len(res) and res[j] is None:
                j += 1
            t0 = res[i - 1][1] if i > 0 else 0.0
            t1 = res[j][0] if j < len(res) else fin
            pesos = [silabas(propias[k]) for k in range(i, j)]
            acc = t0
            for k, p in zip(range(i, j), pesos):
                d = max(0.0, t1 - t0) * p / sum(pesos)
                res[k] = [acc, acc + d]
                acc += d
            i = j
        else:
            i += 1
    emparejadas = sum(b - a for t, a, b, _, _ in sm.get_opcodes() if t == "equal")
    return [{"text": w, "start": round(a, 3), "end": round(b, 3)} for w, (a, b) in zip(propias, res)], emparejadas / max(1, len(A))


if __name__ == "__main__":
    mp3, txt, salida = sys.argv[1:4]
    pal, ok = tiempos(mp3, open(txt, encoding="utf-8").read())
    json.dump({"palabras": pal, "coincidencia": round(ok, 3), "origen": "whisper-medium"}, open(salida, "w"), ensure_ascii=False)
    print(f"✔ tiempos: {len(pal)} palabras, {ok:.0%} emparejadas con lo oído")
