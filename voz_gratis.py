#!/usr/bin/env python3
"""
Voz en off GRATUITA para los shorts de «Caso Recortado» (plan B cuando ElevenLabs no tiene créditos).

Genera la narración con Chatterbox Multilingual (modelo abierto, licencia MIT, funciona en CPU),
comprueba con Whisper que se ha dicho todo el texto (si un bloque falla, prueba otra toma),
monta el mp3 y saca los tiempos de cada palabra para los subtítulos.

Uso:
    python voz_gratis.py --instalar               # una sola vez (≈3 GB: torch CPU + modelos)
    python voz_gratis.py short_<nombre>.py        # → cache_audio/<slug>/narracion.mp3 + narracion_palabras.json
    python voz_gratis.py short_<nombre>.py --muestra   # solo el primer bloque, para escuchar el tono
    python voz_gratis.py short_<nombre>.py --rehacer 4  # rehace solo el bloque 4 (o «2,4») con otras tomas

La voz de referencia (voz_ref.wav) es una voz sintética (Kokoro, em_alex): no copia a ninguna persona real.
En el short se puede definir PRONUNCIA = {"Heilbronn": "Jáilbron", ...} para palabras difíciles.
Tarda ≈ 6 s de CPU por cada segundo de audio (un short de 50 s ≈ 5-6 min).
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
# Motor de voz: «qwen» (Qwen3-TTS, Apache 2.0: la voz A «narrador», más humana; la elegida por el usuario)
# o «chatterbox» (el anterior, más rápido). Se cambia con la variable de entorno VOZ_MOTOR=chatterbox.
MOTOR = os.environ.get("VOZ_MOTOR", "qwen")
VENVS = {"qwen": os.path.expanduser("~/.voz_qwen_venv"), "chatterbox": os.path.expanduser("~/.voz_gratis_venv")}
VENV = os.environ.get("VOZ_GRATIS_VENV", VENVS[MOTOR])
PY_VENV = os.path.join(VENV, "bin", "python")
REF = os.path.join(AQUI, "voz_ref.wav")
# Voz A: diseñada con Qwen3-TTS VoiceDesign a partir de una descripción (no copia a ninguna persona real):
VOCES_QWEN = {
    # «usuario»: la voz del propio usuario (grabación suya, con su permiso), elegida en nov-2026
    "usuario": (os.path.join(AQUI, "voz_ref_usuario.wav"),
                "Hola, soy de Caso Recortado. ¿Sabías que en Venus un día dura más que un año? Parece imposible, pero es real. "
                "En mil novecientos sesenta y nueve el ser humano pisó la Luna por primera vez y las huellas siguen ahí porque "
                "no hay viento que las borre. ¡Esto es increíble! Un pulpo tiene tres corazones y la sangre azul. ¿Y tú? ¿Lo sabías?"),
}
# «usuario_animado»: el inicio de una toma con la voz del usuario (el tono que él quiere «todo el rato»)
VOCES_QWEN["usuario_animado"] = (os.path.join(AQUI, "voz_ref_usuario_animado.wav"),
                                 "Este vídeo lo ha hecho una inteligencia artificial. Pero mira lo que pasa si le cambio el estilo.")
# Por defecto, la voz del dueño del canal si su archivo está (su ordenador); si no (la nube), la del narrador
VOZ_QWEN = os.environ.get("VOZ_QWEN") or ("usuario_animado" if os.path.exists(VOCES_QWEN["usuario_animado"][0]) else "narrador")     # «usuario» o «narrador» (voz A)
QWEN_REF = os.path.join(AQUI, "voz_ref_qwen.wav")
QWEN_REF_TEXTO = ("Este vídeo lo ha hecho una inteligencia artificial. Pero mira lo que pasa si le cambio el estilo. "
                  "En papel recortado. Con palitos. O como un cómic. ¿Cuál te gusta más? Comenta tu favorito.")
VOCES_QWEN["narrador"] = (QWEN_REF, QWEN_REF_TEXTO)
# Voces para los clientes de la web (diseñadas por descripción con VoiceDesign; no copian a nadie real)
for _v in ("cercano", "narradora", "cercana"):
    VOCES_QWEN[_v] = (os.path.join(AQUI, f"voz_ref_{_v}.wav"), QWEN_REF_TEXTO)
QWEN_TEMPERATURA = 0.6       # más baja = tono más estable entre frases (por defecto 0,9)
SEGUIDO = True               # Qwen: toda la narración en una sola toma (tono constante de principio a fin)
IGUALAR_TONO = True          # cada trozo se lleva al tono medio de la voz de referencia (±2 semitonos como mucho)
QWEN_INSTRUCCION = ("Hombre español de unos cuarenta años, castellano de España (acento peninsular, pronuncia la z y la c), "
                    "voz grave, cálida y profunda, narrador de documentales de misterio: habla despacio, con pausas "
                    "naturales, entonación expresiva y un punto de intriga.")

# Ajustes de «humanidad»: más expresividad y ritmo algo más pausado que los valores por defecto (0,5 / 0,5)
EXAGERACION = 0.7
CFG = 0.3
TEMPERATURA = 0.8
PAUSA_BLOQUE = 0.55          # silencio entre bloques (s)
PAUSA_FRASE = 0.38           # silencio entre frases: se genera cada frase por separado, como quien respira
PAUSA_COMA = 0.18            # silencio cuando una frase larga se parte por una coma
MAX_FRASE = 13               # palabras: una frase más larga se parte por la coma más cercana al centro
RITMO = 0.93                 # <1 = más pausado (sin cambiar el tono); el modelo tiende a hablar deprisa
SEMILLAS = (7, 31, 11, 23)   # tomas que se prueban si un bloque no supera la verificación
MIN_PARECIDO = 0.97          # parecido mínimo entre el texto y lo que entiende Whisper

PRONUNCIA_BASE = {"ADN": "a de ene", "%": " por ciento", "EE. UU.": "Estados Unidos", "km": "kilómetros"}

UNI = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis "
       "diecisiete dieciocho diecinueve veinte").split()
DEC = ["", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
CEN = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos",
       "ochocientos", "novecientos"]
VEINTI = {2: "veintidós", 3: "veintitrés", 6: "veintiséis"}


def numero(n):
    if n <= 20:
        return UNI[n]
    if n < 30:
        return VEINTI.get(n - 20, "veinti" + UNI[n - 20])
    if n < 100:
        return DEC[n // 10] + ("" if n % 10 == 0 else " y " + UNI[n % 10])
    if n < 1000:
        return ("cien" if n == 100 else CEN[n // 100]) + ("" if n % 100 == 0 else " " + numero(n % 100))
    if n < 1_000_000:
        mil = "mil" if n // 1000 == 1 else numero(n // 1000) + " mil"
        return mil + ("" if n % 1000 == 0 else " " + numero(n % 1000))
    mill = "un millón" if n // 1_000_000 == 1 else numero(n // 1_000_000) + " millones"
    return mill + ("" if n % 1_000_000 == 0 else " " + numero(n % 1_000_000))


def para_hablar(t, extra):
    """Texto tal cual lo debe leer la voz: números en letra, siglas deletreadas, sin comillas."""
    for a, b in {**PRONUNCIA_BASE, **extra}.items():
        t = re.sub(rf"(?<!\w){re.escape(a)}(?!\w)" if a[0].isalnum() else re.escape(a), b, t)
    t = re.sub(r"(\d+)\.(\d{3})\b", r"\1\2", t)
    t = re.sub(r"\d+", lambda m: numero(int(m.group())), t)
    t = t.replace('"', "").replace("«", "").replace("»", "").replace("…", ",")
    t = re.sub(r"\s+", " ", t).strip()
    return t[:1].upper() + t[1:]


def norm(t):
    t = unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t)


# ─────────────────────────── parte que corre dentro del venv ───────────────────────────
def worker(job_path):
    import difflib

    import numpy as np
    import soundfile as sf
    import torch
    from faster_whisper import WhisperModel

    job = json.load(open(job_path))

    class Voz:
        """Misma interfaz para los dos motores: sr y decir(texto) → numpy mono."""
        def __init__(self, motor):
            self.motor = motor
            if motor == "qwen":
                from qwen_tts import Qwen3TTSModel
                torch.set_num_threads(os.cpu_count() or 4)
                # con tarjeta gráfica (p. ej. en Modal) va ~20 veces más rápido; si no, procesador
                gpu = torch.cuda.is_available()
                self.m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0" if gpu else "cpu",
                                                       dtype=torch.bfloat16 if gpu else torch.float32)
                self.prompt = self.m.create_voice_clone_prompt(ref_audio=job["qwen_ref"], ref_text=job["qwen_ref_texto"])
                self.sr = 24000
            else:
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS
                self.m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
                self.sr = self.m.sr

        def decir(self, texto):
            if self.motor == "qwen":
                wavs, self.sr = self.m.generate_voice_clone(
                    text=texto, language="Spanish", voice_clone_prompt=self.prompt, temperature=QWEN_TEMPERATURA,
                    top_p=0.85, subtalker_temperature=QWEN_TEMPERATURA)
                return np.asarray(wavs[0], dtype=np.float32)
            wav = self.m.generate(texto, language_id="es", audio_prompt_path=job["ref"], exaggeration=job.get("exag", EXAGERACION),
                                  cfg_weight=job.get("cfg", CFG), temperature=job.get("temp", TEMPERATURA))
            return wav.squeeze(0).cpu().numpy()

    tts = Voz(job.get("motor", "chatterbox"))
    gpu = torch.cuda.is_available()
    asr = WhisperModel(os.environ.get("VOZ_WHISPER", "medium"), device="cuda" if gpu else "cpu",
                       compute_type="float16" if gpu else "int8")  # «small» no oía palabras tragadas

    def oir(path, prompt=None, palabras=False):
        pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        segs, _ = asr.transcribe(np.frombuffer(pcm, np.float32), language="es", word_timestamps=palabras,
                                 initial_prompt=prompt)
        return list(segs)

    def parecido(a, b):
        return difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()

    def numeros_ok(texto, oido, hablado=""):
        """Una cifra mal dicha (1903 por 1913) apenas baja el parecido, así que se comprueba aparte."""
        nt = {int(n) for n in re.findall(r"\d+", re.sub(r"(\d)\.(\d{3})", r"\1\2", texto))}
        dicho = " " + " ".join(norm(w) for w in hablado.split()) + " "
        for n in re.findall(r"\d+", re.sub(r"(\d)[.,](\d{3})", r"\1\2", oido)):
            n = int(n)
            if n in nt or n * 1000 in nt or n * 1_000_000 in nt:
                continue
            if n < 1_000_000 and " " + " ".join(norm(w) for w in numero(n).split()) + " " in dicho:
                continue   # el número estaba escrito en letra en el guion («cincuenta»)
            return False
        return True

    el_path = os.path.join(job["tmp"], "elegidas.json")
    elegidas = json.load(open(el_path)) if os.path.exists(el_path) else {}
    rehacer = set(job.get("rehacer") or [])

    igualar_on = bool(job.get("igualar") and job.get("motor") == "qwen")
    tonos_elegidos = []                      # tono (Hz) de cada trozo ya elegido: el objetivo es su mediana

    def tono(path):
        """Tono medio de la voz con Praat (parselmouth): fiable, no confunde la voz con sus armónicos."""
        import parselmouth
        p = parselmouth.Sound(path).to_pitch_ac(pitch_floor=70, pitch_ceiling=350)
        v = p.selected_array["frequency"]
        v = v[v > 0]
        return float(np.median(v)) if len(v) > 10 else None

    def objetivo():
        return float(np.median(tonos_elegidos)) if tonos_elegidos else None

    def semitonos(a, b):
        return 12 * np.log2(a / b) if a and b else 0.0

    def igualar(path):
        """Corrige un poco el tono (±1,5 semitonos como mucho) y deja el volumen fijo, para que no cambie entre frases."""
        if not igualar_on:
            return path
        import librosa
        t = tono(path)
        obj = objetivo() or t
        st = float(np.clip(semitonos(obj, t), -1.5, 1.5)) if not job.get("seguido") else 0.0
        out = path[:-4] + f"_ig{st:+.1f}.wav"
        if not os.path.exists(out):
            y, sr = sf.read(path, dtype="float32")
            if abs(st) >= 0.4:
                y = librosa.effects.pitch_shift(y, sr=sr, n_steps=st)
            voz = np.abs(y) > 0.01
            rms = float(np.sqrt(np.mean(y[voz] ** 2))) if voz.any() else 0.1
            sf.write(out, np.clip(y * (0.1 / max(rms, 1e-4)), -1, 1), sr)
        if t:
            tonos_elegidos.append(t)
        print(f"    tono {t or 0:.0f} Hz · objetivo {obj or 0:.0f} Hz · corrección {st if abs(st) >= 0.4 else 0:+.1f} st", flush=True)
        return out

    def generar(texto, hablado, clave, etiqueta, rehacer_esta):
        return igualar(_generar(texto, hablado, clave, etiqueta, rehacer_esta))

    def _generar(texto, hablado, clave, etiqueta, rehacer_esta):
        """Genera una unidad (bloque o trozo de bloque), verificándola con Whisper.
        Con igualado: entre las tomas bien dichas, la de tono más cercano al resto del vídeo."""
        previa = elegidas.get(clave)
        if previa and previa["texto"] == hablado and os.path.exists(previa["wav"]) and not rehacer_esta:
            print(f"  {etiqueta}: reutilizo la toma anterior", flush=True)
            return previa["wav"]
        semillas = [sd for sd in SEMILLAS if not (rehacer_esta and previa and previa["wav"].endswith(f"_s{sd}.wav"))]
        mejor, nota_mejor = None, None
        for semilla in semillas:
            torch.manual_seed(semilla)
            wav = tts.decir(hablado)
            out = os.path.join(job["tmp"], f"b{clave}_s{semilla}.wav")
            sf.write(out, wav, tts.sr)
            oido = "".join(s.text for s in oir(out))
            oido_letras = re.sub(r"\d+", lambda m: numero(int(m.group())) if len(m.group()) < 7 else m.group(),
                                 re.sub(r"(\d)[.,](\d{3})", r"\1\2", oido))
            p = max(parecido(texto, oido), parecido(hablado, oido), parecido(hablado, oido_letras))
            if not numeros_ok(texto, oido, hablado):
                p = min(p, 0.9)
                print(f"  {etiqueta} toma {semilla}: ⚠ una cifra no coincide", flush=True)
            dif = abs(semitonos(tono(out), objetivo())) if igualar_on and objetivo() else 0.0
            print(f"  {etiqueta} toma {semilla}: parecido {p:.2f} · tono {dif:.1f} st del resto · «{oido.strip()}»", flush=True)
            nota = (p >= MIN_PARECIDO, -dif if p >= MIN_PARECIDO else p)
            if mejor is None or nota > nota_mejor:
                mejor, nota_mejor = (p, out), nota
            if p >= MIN_PARECIDO and dif <= 1.5:
                break
        if mejor[0] < MIN_PARECIDO:
            print(f"  ⚠ {etiqueta}: ninguna toma pasó la verificación; uso la mejor ({mejor[0]:.2f})", flush=True)
        elegidas[clave] = {"texto": hablado, "wav": mejor[1]}
        json.dump(elegidas, open(el_path, "w"), ensure_ascii=False)
        return mejor[1]

    def trocear(t):
        """Lista de (trozo, pausa_despues): una frase por trozo; las largas se parten por una coma.
        El modelo atropella las frases largas y se come o cambia palabras al final."""
        frases = [f for f in re.split(r"(?<=[.?!:])\s+", t.strip()) if f]
        trozos = []
        for f in frases:
            pal = f.split()
            comas = [k for k, w in enumerate(pal[:-1]) if w.endswith(",") and 3 <= k + 1 <= len(pal) - 3]
            if len(pal) > MAX_FRASE and comas:
                k = min(comas, key=lambda k: abs(k + 1 - len(pal) / 2))
                trozos += [(" ".join(pal[:k + 1]), PAUSA_COMA), (" ".join(pal[k + 1:]), PAUSA_FRASE)]
            else:
                trozos.append((f, PAUSA_FRASE))
        if job.get("motor") == "qwen":
            # Qwen aguanta bien frases largas: se juntan hasta ~22 palabras para que la entonación siga igual
            juntos = []
            for tr, pausa in trozos:
                if juntos and juntos[-1][1] == PAUSA_FRASE and len((juntos[-1][0] + " " + tr).split()) <= 22:
                    juntos[-1] = (juntos[-1][0] + " " + tr, pausa)
                else:
                    juntos.append((tr, pausa))
            trozos = juntos
        return trozos

    silencios = {}

    def silencio(seg):
        if seg not in silencios:
            silencios[seg] = os.path.join(job["tmp"], f"sil_{int(seg * 1000)}.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={tts.sr}:cl=mono",
                            "-t", str(seg), silencios[seg]], check=True)
        return silencios[seg]

    wavs = []
    if job.get("seguido") and job.get("motor") == "qwen" and not job.get("muestra"):
        # TODO EN UNA SOLA TOMA: la voz no cambia de tono ni de estilo a mitad (el usuario lo quiere «como el inicio»).
        # Los bloques van en párrafos separados para que el modelo haga la pausa natural entre ellos.
        texto = " ".join(job["textos"])
        hablado = "\n".join(job["hablados"])
        wavs.append(generar(texto, hablado, "todo", "narración completa", bool(rehacer)))
    for i, (texto, hablado) in enumerate([] if wavs else zip(job["textos"], job["hablados"])):
        rh = (i + 1) in rehacer
        tt, th = trocear(texto), trocear(hablado)
        if len(tt) != len(th) or len(tt) == 1:
            wavs.append(generar(texto, hablado, str(i), f"bloque {i + 1}", rh))
        else:
            partes = [(generar(a, b, f"{i}.{j}", f"bloque {i + 1}.{j + 1}", rh), pausa)
                      for j, ((a, pausa), (b, _)) in enumerate(zip(tt, th))]
            lista_b = os.path.join(job["tmp"], f"lista_b{i}.txt")
            with open(lista_b, "w") as f:
                for j, (w, pausa) in enumerate(partes):
                    f.write(f"file '{w}'\n")
                    if j < len(partes) - 1:
                        f.write(f"file '{silencio(pausa)}'\n")
            out_b = os.path.join(job["tmp"], f"bloque{i}.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista_b, "-c", "copy",
                            out_b], check=True)
            wavs.append(out_b)
        if job.get("muestra"):
            break

    # montaje: bloques + silencios + un poco de «sala» y cuerpo en graves
    lista = os.path.join(job["tmp"], "lista.txt")
    sil = os.path.join(job["tmp"], "sil.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={tts.sr}:cl=mono",
                    "-t", str(PAUSA_BLOQUE), sil], check=True)
    with open(lista, "w") as f:
        for k, w in enumerate(wavs):
            f.write(f"file '{w}'\n")
            if k < len(wavs) - 1:
                f.write(f"file '{sil}'\n")
    ritmo = f"atempo={job.get('ritmo', RITMO)}," if job.get("ritmo", RITMO) != 1 else ""
    filtro = ritmo + ("highpass=f=70,bass=g=3:f=130,aecho=0.85:0.6:18|31:0.10|0.06,loudnorm=I=-17" if job.get("eco", True)
              else "highpass=f=70,bass=g=2:f=140,loudnorm=I=-17")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-af", filtro,
                    "-ar", "44100", "-b:a", "192k", job["mp3"]], check=True)
    if job.get("muestra"):
        print("FIN", flush=True)
        return

    # tiempos por palabra: el mismo Whisper ya cargado, sin «pista» de texto (con pista se equivocaba y había
    # que repetir la escucha en otro proceso); empareja con el guion y reparte por sílabas lo que no case
    sys.path.insert(0, AQUI)
    import tiempos_whisper
    pal, ok = tiempos_whisper.tiempos(job["mp3"], " ".join(job["textos"]), asr=asr)
    json.dump({"palabras": pal, "coincidencia": round(ok, 3), "origen": "whisper"}, open(job["json"], "w"), ensure_ascii=False)
    print(f"✔ tiempos: {len(pal)} palabras ({ok:.0%} emparejadas con lo oído)", flush=True)
    print("FIN", flush=True)


# ─────────────────────────── parte que corre con el python normal ───────────────────────────
def instalar():
    if not os.path.exists(PY_VENV):
        subprocess.run([sys.executable, "-m", "venv", VENV], check=True)
    pip = [PY_VENV, "-m", "pip", "install", "-q"]
    subprocess.run(pip + ["torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
    subprocess.run(pip + (["qwen-tts", "soundfile", "faster-whisper", "praat-parselmouth", "librosa"] if MOTOR == "qwen"
                          else ["chatterbox-tts", "faster-whisper", "soundfile"]), check=True)
    print("✔ voz gratuita instalada en", VENV)


def main():
    if "--worker" in sys.argv:
        return worker(sys.argv[sys.argv.index("--worker") + 1])
    if "--instalar" in sys.argv:
        return instalar()
    script = next(a for a in sys.argv[1:] if a.endswith(".py"))
    spec = importlib.util.spec_from_file_location("short_mod", script)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    spec.loader.exec_module(mod)
    if not os.path.exists(PY_VENV):
        sys.exit("Falta instalar la voz gratuita: python voz_gratis.py --instalar")
    textos = [b["voz"] for b in mod.BLOQUES]
    extra = getattr(mod, "PRONUNCIA", {})
    hablados = [para_hablar(t, extra) for t in textos]
    d = os.path.join("cache_audio", mod.SLUG)
    tmp = os.path.join(d, "tomas_gratis" if MOTOR == "chatterbox" else f"tomas_{MOTOR}_{VOZ_QWEN}")
    os.makedirs(tmp, exist_ok=True)
    muestra = "--muestra" in sys.argv
    rehacer = []
    if "--rehacer" in sys.argv:
        rehacer = [int(n) for n in sys.argv[sys.argv.index("--rehacer") + 1].split(",")]
    for k, v in getattr(mod, "VOZ_AJUSTES", {}).items():   # p. ej. {"EXAGERACION": 0.5, "ECO": False}
        globals()[k] = v
    ref = getattr(mod, "VOZ_REF", None)
    ref = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(script)), ref)) if ref else REF
    job = dict(exag=EXAGERACION, cfg=CFG, temp=TEMPERATURA, eco=globals().get("ECO", True), motor=MOTOR,
               qwen_ref=VOCES_QWEN[VOZ_QWEN][0], qwen_ref_texto=VOCES_QWEN[VOZ_QWEN][1], igualar=IGUALAR_TONO, seguido=SEGUIDO, ritmo=1.0 if MOTOR == "qwen" else RITMO,
               textos=textos, hablados=hablados, ref=ref, tmp=os.path.abspath(tmp), muestra=muestra, rehacer=rehacer,
               mp3=os.path.abspath(os.path.join(d, "muestra_voz.mp3" if muestra else "narracion.mp3")),
               json=os.path.abspath(os.path.join(d, "narracion_palabras.json")))
    jp = os.path.join(tmp, "job.json")
    json.dump(job, open(jp, "w"), ensure_ascii=False)
    for h in hablados:
        print("·", h)
    subprocess.run([PY_VENV, os.path.abspath(__file__), "--worker", jp], check=True)
    if not muestra:
        # Si Whisper no oyó bien alguna parte, sus tiempos se reparten a ojo y los subtítulos se retrasan:
        # entonces se usan los silencios reales entre frases (alinear_texto.py, error medio ≈0,1 s).
        datos = json.load(open(job["json"]))
        if datos.get("coincidencia", 1) < 0.95:
            # 1.º Whisper «medium» palabra a palabra, emparejando con el guion; 2.º si tampoco, los silencios
            txt = os.path.join(tmp, "texto.txt")
            open(txt, "w", encoding="utf-8").write(" ".join(textos))
            subprocess.run([PY_VENV, os.path.join(AQUI, "tiempos_whisper.py"), job["mp3"], txt, job["json"]], check=True)
            datos = json.load(open(job["json"]))
            if datos.get("coincidencia", 0) < 0.85:
                sys.path.insert(0, AQUI)
                import alinear_texto
                datos = {"palabras": alinear_texto.alinear(job["mp3"], " ".join(textos)), "origen": "silencios"}
                json.dump(datos, open(job["json"], "w"), ensure_ascii=False)
                print("✔ tiempos rehechos con los silencios de la voz (Whisper no lo oyó todo)")
    print("✔", job["mp3"])


if __name__ == "__main__":
    main()
