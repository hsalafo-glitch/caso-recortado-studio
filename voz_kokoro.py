#!/usr/bin/env python3
"""Voz en off con Kokoro (modelo abierto, Apache 2.0, CPU, sin cuentas ni créditos).

Plan C cuando no hay ElevenLabs ni se pueden descargar los modelos de Qwen/Chatterbox: Kokoro se baja
de GitHub (≈350 MB, una vez) y genera ~4 s de voz por segundo de CPU.

    python voz_kokoro.py --instalar                   # pip install kokoro-onnx + modelos en ~/kokoro
    python voz_kokoro.py short_<nombre>.py            # → cache_audio/<slug>/narracion.mp3 + narracion_palabras.json
    VOZ_KOKORO=ef_dora python voz_kokoro.py ...       # voz femenina (por defecto em_alex, hombre, España)

Los tiempos por palabra salen exactos en los cortes de frase (cada frase se genera por separado y se
mide) y dentro de cada frase se reparten por sílabas: lo bastante preciso para subtítulos y escenas.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from voz_gratis import para_hablar  # noqa: E402  (números en letra, siglas, pronuncia)

DIR = os.path.expanduser("~/kokoro")
URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
VOZ = os.environ.get("VOZ_KOKORO", "em_alex")
VELOCIDAD = float(os.environ.get("VOZ_KOKORO_VELOCIDAD", "1.08"))
PAUSA_FRASE, PAUSA_COMA, PAUSA_BLOQUE = 0.30, 0.14, 0.45


def instalar():
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "kokoro-onnx", "soundfile"], check=True)
    os.makedirs(DIR, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not os.path.exists(os.path.join(DIR, f)):
            subprocess.run(["curl", "-sSL", "-o", os.path.join(DIR, f), URL + f], check=True)
    print("✔ Kokoro instalado en", DIR)


def silabas(w):
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w.lower())))


def trozos(voz):
    """Parte la voz en frases (y las largas por la coma). Devuelve [(palabras, pausa_despues)]."""
    out = []
    for frase in re.findall(r"[^.?!]+[.?!]*", voz):
        ws = frase.split()
        if not ws:
            continue
        if len(ws) > 14:
            comas = [i for i, w in enumerate(ws[:-1]) if w.endswith(",")]
            if comas:
                c = min(comas, key=lambda i: abs(i - len(ws) / 2))
                out += [(ws[:c + 1], PAUSA_COMA), (ws[c + 1:], PAUSA_FRASE)]
                continue
        out.append((ws, PAUSA_FRASE))
    return out


def recortar(a, sr, umbral=0.012):
    idx = np.where(np.abs(a) > umbral)[0]
    if not len(idx):
        return a
    i0, i1 = max(0, idx[0] - int(0.03 * sr)), min(len(a), idx[-1] + int(0.06 * sr))
    return a[i0:i1]


def narrar(bloques, extra, d, voz=VOZ, velocidad=VELOCIDAD):
    """Lista de textos (uno por bloque) → d/narracion.mp3 + d/narracion_palabras.json. Devuelve la duración."""
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(os.path.join(DIR, "kokoro-v1.0.onnx"), os.path.join(DIR, "voices-v1.0.bin"))
    os.makedirs(d, exist_ok=True)
    sr, partes, palabras, t = 24000, [], [], 0.0
    for bi, texto in enumerate(bloques):
        tz = trozos(texto)
        for ti, (ws, pausa) in enumerate(tz):
            hablado = para_hablar(" ".join(ws), extra)
            a, sr = k.create(hablado, voice=voz, speed=velocidad, lang="es")
            a = recortar(np.asarray(a, np.float32), sr)
            dur = len(a) / sr
            pesos = [silabas(para_hablar(w, extra)) + (0.6 if w[-1] in ",;:" else 0) for w in ws]
            tot, acc = sum(pesos), 0.0
            for w, p in zip(ws, pesos):
                ini = t + dur * acc / tot
                acc += p
                palabras.append(dict(text=w, start=round(ini, 3), end=round(t + dur * acc / tot, 3), bloque=bi))
            partes.append(a)
            ultima = ti == len(tz) - 1
            sil = PAUSA_BLOQUE if ultima else pausa
            if not (ultima and bi == len(bloques) - 1):
                partes.append(np.zeros(int(sil * sr), np.float32))
            t += dur + sil
            print(f"· [{bi + 1}] {hablado}", flush=True)
    wav = os.path.join(d, "narracion_kokoro.wav")
    sf.write(wav, np.concatenate(partes), sr)
    mp3 = os.path.join(d, "narracion.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af",
                    "highpass=f=70,bass=g=2:f=140,loudnorm=I=-16", "-ar", "44100", "-b:a", "192k", mp3], check=True)
    json.dump({"palabras": palabras, "origen": "kokoro-silabas"},
              open(os.path.join(d, "narracion_palabras.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"✔ {mp3} ({t:.1f} s, voz {voz})")
    return t


def main():
    if "--instalar" in sys.argv:
        return instalar()
    script = next(a for a in sys.argv[1:] if a.endswith(".py"))
    spec = importlib.util.spec_from_file_location("short_mod", script)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    spec.loader.exec_module(mod)
    narrar([b["voz"] for b in mod.BLOQUES], getattr(mod, "PRONUNCIA", {}),
           os.path.join(AQUI, "cache_audio", mod.SLUG))


if __name__ == "__main__":
    main()
