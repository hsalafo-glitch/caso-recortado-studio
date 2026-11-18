#!/usr/bin/env python3
"""Fábrica de shorts con CLIPS de gameplay: tus vídeos horizontales → short vertical terminado.

    python canal_gta6/fabrica_clips.py 01                  # el guion 01 con los clips de canal_gta6/clips/01/
                                                           # (si esa carpeta no existe, usa los de canal_gta6/clips/)
    python canal_gta6/fabrica_clips.py todos               # los 10
    python canal_gta6/fabrica_clips.py 01 --clips carpeta  # otra carpeta de clips
    python canal_gta6/fabrica_clips.py 01 --demo           # sin clips: fondo de prueba (para revisar ritmo y textos)

Qué hace:
  1. Voz en off con Kokoro (gratis, en CPU) y tiempos de cada palabra  → cache_audio/<slug>/
  2. Corta los clips al ritmo de la voz (un plano nuevo en cada frase, máx. ~3 s), los pasa a 9:16 con
     un zoom lento o, si el bloque lo pide («marco»), el plano entero sobre su propio fondo desenfocado.
  3. Encima: gancho grande al principio, rótulo de cada bloque, subtítulos palabra a palabra y barra de progreso.
  4. Audio: voz delante y el sonido del juego por debajo (se agacha cuando habla la voz). Normalizado a −14 LUFS.
Salida: salida/gta6/<slug>.mp4 (1080x1920, 30 fps) + <slug>.txt con título y descripción para pegar.

Los clips: .mp4/.mov/.mkv de cualquier tamaño, en el orden que quieras (se usan por orden de nombre).
Solo clips que tengas derecho a usar: tu propia partida, o la de un creador que te haya dado permiso.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
sys.path.insert(0, AQUI)

W, H, FPS = 1080, 1920, 30
FUENTE_DIR = os.path.join(RAIZ, "fuentes")
FUENTE = "Inter Display Black"
SALIDA = os.path.join(RAIZ, "salida", "gta6")
MAX_PLANO = 3.0           # segundos máximos de un mismo plano
GANCHO_SEG = 2.6          # el gancho grande ocupa los primeros segundos
JUEGO_DB = -16            # volumen del juego bajo la voz
COLA = 0.9                # segundos tras la última palabra
EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v")


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"Falló: {' '.join(cmd[:6])}…\n{r.stderr[-1500:]}")
    return r.stdout


def duracion(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def tiene_audio(path):
    return bool(sh(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of",
                    "csv=p=0", path]).strip())


# ───────────────────────── planos ─────────────────────────
def cortes(palabras, total):
    """Momentos de corte: al empezar cada frase (y cada MAX_PLANO s dentro de frases largas)."""
    marcas = [0.0]
    for i, w in enumerate(palabras[1:], 1):
        prev = palabras[i - 1]["text"]
        if prev[-1] in ".?!:" or w.get("bloque") != palabras[i - 1].get("bloque"):
            marcas.append(max(0.0, w["start"] - 0.08))
    marcas.append(total)
    out = []
    for a, b in zip(marcas, marcas[1:]):
        n = max(1, round((b - a) / MAX_PLANO + 0.25))
        out += [(a + (b - a) * k / n, a + (b - a) * (k + 1) / n) for k in range(n)]
    return [(a, b) for a, b in out if b - a > 0.2]


class Cinta:
    """Reparte los clips sin repetir trozos: va avanzando por cada clip y salta al siguiente."""

    def __init__(self, clips):
        self.clips = [(c, duracion(c)) for c in clips]
        self.pos = {c: min(1.0, d * 0.05) for c, d in self.clips}   # salta el primer segundo (menús, fundidos)
        self.i = 0

    def tomar(self, dur):
        for _ in range(len(self.clips) * 2):
            c, d = self.clips[self.i % len(self.clips)]
            self.i += 1
            if self.pos[c] + dur <= d - 0.2:
                ini = self.pos[c]
                self.pos[c] += dur + 0.6
                return c, ini
            self.pos[c] = min(1.0, d * 0.05)                         # se acabó: vuelve a empezar ese clip
        c, d = self.clips[0]
        return c, max(0.0, min(d - dur, 0.0))


def render_plano(clip, ini, dur, encuadre, k, out, demo_txt=None):
    """Un plano 1080x1920 sin audio. encuadre: «lleno» (recorte 9:16 + zoom lento) o «marco» (16:9 entero)."""
    zin = k % 2 == 0                                          # alterna acercar / alejar
    z = f"(1.0+0.06*t/{dur:.3f})" if zin else f"(1.06-0.06*t/{dur:.3f})"
    zoom = (f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,crop={W}:{H}")
    if demo_txt is not None:
        src = ["-f", "lavfi", "-i", f"gradients=s=1920x1080:c0=0x1d4ed8:c1=0xe63946:c2=0xffb703:n=3:speed=0.02:d={dur:.3f}:r={FPS}"]
        ss = []
    else:
        src, ss = ["-i", clip], ["-ss", f"{ini:.3f}"]
    if encuadre == "marco":
        vf = (f"[0:v]fps={FPS},split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=30,eq=brightness=-0.12[fondo];"
              f"[b]scale={W - 40}:-2[fr];[fondo][fr]overlay=(W-w)/2:(H-h)/2-90")
    else:
        vf = f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{zoom}"
    if demo_txt is not None:
        vf += (f",drawtext=fontfile={os.path.join(FUENTE_DIR, 'InterDisplay-Black.otf')}:text='{demo_txt}':"
               f"fontsize=34:fontcolor=white@0.8:box=1:boxcolor=black@0.35:boxborderw=14:x=(w-tw)/2:y=h*0.36")
    sh(["ffmpeg", "-y", "-loglevel", "error", *ss, "-t", f"{dur:.3f}", *src, "-filter_complex", vf + ",format=yuv420p",
        "-an", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", out])


def audio_juego(planos, total, tmp):
    """El sonido de los clips, pegado en el mismo orden que los planos (silencio si un clip no tiene)."""
    partes = []
    for j, (clip, ini, dur) in enumerate(planos):
        p = os.path.join(tmp, f"a{j:03d}.wav")
        if clip and tiene_audio(clip):
            sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", clip, "-vn", "-ac", "2",
                "-ar", "44100", "-af", f"apad,atrim=0:{dur:.3f},afade=t=in:d=0.05,afade=t=out:st={max(0, dur - 0.06):.3f}:d=0.06", p])
        else:
            sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{dur:.3f}", p])
        partes.append(p)
    lista = os.path.join(tmp, "audio.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    out = os.path.join(tmp, "juego.wav")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-t", f"{total:.3f}", out])
    return out


# ───────────────────────── textos (ASS) ─────────────────────────
def t_ass(s):
    s = max(0.0, s)
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"


def esc(t):
    return t.replace("{", "(").replace("}", ")").replace("\n", "\\N")


def subtitulos(palabras, guion, total):
    """Gancho, rótulos de bloque y subtítulos de 1-3 palabras con la palabra que suena en amarillo."""
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,4,2,60,60,560,1
Style: Gancho,{FUENTE},118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,3,26,0,8,50,50,300,1
Style: Rotulo,{FUENTE},70,&H00101010,&H00101010,&H0000D7FF,&H00000000,1,0,0,0,100,100,0,0,3,18,0,8,60,60,250,1
Style: Marca,{FUENTE},34,&H50FFFFFF,&H50FFFFFF,&H64000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,9,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    # gancho: entra con un golpe de escala y se va al empezar el rótulo del bloque 2
    g1, g2 = guion["gancho"]
    fin_g = min(GANCHO_SEG, total)
    ev.append(f"Dialogue: 3,{t_ass(0)},{t_ass(fin_g)},Gancho,,0,0,0,,{{\\fscx130\\fscy130\\t(0,180,\\fscx100\\fscy100)\\3c&H1F39E6&}}{esc(g1)}")
    ev.append(f"Dialogue: 3,{t_ass(0.15)},{t_ass(fin_g)},Gancho,,0,0,0,,{{\\pos({W // 2},470)\\an8\\fscx130\\fscy130\\t(0,180,\\fscx100\\fscy100)\\3c&H00D7FF&\\c&H101010&}}{esc(g2)}")
    # rótulo de cada bloque (desde que empieza a hablarse hasta que empieza el siguiente)
    inicios = {}
    for w in palabras:
        inicios.setdefault(w["bloque"], w["start"])
    for bi, b in enumerate(guion["bloques"]):
        if not b.get("rotulo"):
            continue
        a = max(inicios.get(bi, 0), fin_g if bi == 0 else 0)
        z = inicios.get(bi + 1, total)
        if z - a > 0.4:
            ev.append(f"Dialogue: 2,{t_ass(a)},{t_ass(z)},Rotulo,,0,0,0,,{{\\fad(120,0)\\frz{(-2 if bi % 2 else 2)}}}{esc(b['rotulo'])}")
    # subtítulos: grupos de hasta 3 palabras (cortando en la puntuación)
    grupos, g = [], []
    for w in palabras:
        g.append(w)
        if len(g) == 3 or w["text"][-1] in ".,?!:;" or len(" ".join(x["text"] for x in g)) > 16:
            grupos.append(g)
            g = []
    if g:
        grupos.append(g)
    for gi, g in enumerate(grupos):
        fin_grupo = grupos[gi + 1][0]["start"] if gi + 1 < len(grupos) else g[-1]["end"] + 0.3
        for wi, w in enumerate(g):
            a = w["start"]
            z = g[wi + 1]["start"] if wi + 1 < len(g) else fin_grupo
            txt = " ".join((f"{{\\c&H00D7FF&}}{esc(x['text'].upper())}{{\\c&HFFFFFF&}}" if x is w else esc(x["text"].upper()))
                           for x in g)
            pop = "{\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
            ev.append(f"Dialogue: 1,{t_ass(a)},{t_ass(z)},Sub,,0,0,0,,{pop}{txt}")
    ev.append(f"Dialogue: 0,{t_ass(0)},{t_ass(total)},Marca,,0,0,0,,{esc(guion.get('marca', ''))}")
    return cab + "\n".join(ev) + "\n"


# ───────────────────────── montaje ─────────────────────────
def fabricar(guion, carpeta_clips, demo=False):
    import voz_kokoro
    slug = guion["slug"]
    d = os.path.join(RAIZ, "cache_audio", slug)
    tmp = os.path.join(d, "planos")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(SALIDA, exist_ok=True)
    textos = [b["voz"] for b in guion["bloques"]]
    pron = guion.get("pronuncia", {})
    pj = os.path.join(d, "narracion_palabras.json")
    firma = os.path.join(d, "texto.txt")
    if not (os.path.exists(pj) and os.path.exists(firma) and open(firma, encoding="utf-8").read() == json.dumps([textos, pron])):
        voz_kokoro.narrar(textos, pron, d)
        open(firma, "w", encoding="utf-8").write(json.dumps([textos, pron]))
    palabras = json.load(open(pj, encoding="utf-8"))["palabras"]
    total = palabras[-1]["end"] + COLA
    if total > 59:
        print(f"  ⚠ la voz dura {total:.1f} s: pasa de 59 s, recorta el guion")

    clips = [] if demo else sorted(os.path.join(carpeta_clips, f) for f in os.listdir(carpeta_clips)
                                   if f.lower().endswith(EXT)) if os.path.isdir(carpeta_clips) else []
    if not clips and not demo:
        raise SystemExit(f"No hay clips en {carpeta_clips}. Mete ahí tus vídeos (o usa --demo para una prueba).")
    cinta = None if demo else Cinta(clips)
    # bloque de cada instante, para saber el encuadre que pide
    inicio_b = {}
    for w in palabras:
        inicio_b.setdefault(w["bloque"], w["start"])

    def bloque_en(t):
        return max([b for b, s in inicio_b.items() if s <= t + 0.1] or [0])

    planos, vids = [], []
    for k, (a, b) in enumerate(cortes(palabras, total)):
        dur = b - a
        bl = guion["bloques"][bloque_en(a)]
        out = os.path.join(tmp, f"v{k:03d}.mp4")
        if demo:
            render_plano(None, 0, dur, bl.get("encuadre", "lleno"), k, out,
                         demo_txt=f"PLANO {k + 1}\\: {bl.get('grabar', '')[:34].upper()}")
            planos.append((None, 0, dur))
        else:
            clip, ini = cinta.tomar(dur)
            render_plano(clip, ini, dur, bl.get("encuadre", "lleno"), k, out)
            planos.append((clip, ini, dur))
        vids.append(out)
        print(f"  plano {k + 1:2d}: {a:5.2f}-{b:5.2f}s  " + (os.path.basename(planos[-1][0]) + f" @{planos[-1][1]:.1f}s" if planos[-1][0] else "demo"),
              flush=True)
    lista = os.path.join(tmp, "video.txt")
    open(lista, "w").write("".join(f"file '{v}'\n" for v in vids))
    juego = audio_juego(planos, total, tmp)
    ass = os.path.join(tmp, "textos.ass")
    open(ass, "w", encoding="utf-8").write(subtitulos(palabras, guion, total))
    mp4 = os.path.join(SALIDA, f"{slug}{'-demo' if demo else ''}.mp4")
    voz = os.path.join(d, "narracion.mp3")
    barra = f"drawbox=x=0:y={H - 14}:w='{W}*t/{total:.3f}':h=14:color=0xFFD700@0.95:t=fill"
    filtro = (f"[0:v]ass={ass}:fontsdir={FUENTE_DIR},{barra}[v];"
              f"[1:a]aformat=channel_layouts=stereo,asplit[voz][vozsc];"
              f"[2:a]volume={JUEGO_DB}dB[jg];[jg][vozsc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[jgd];"
              f"[voz][jgd]amix=inputs=2:duration=first:normalize=0,apad,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", voz, "-i", juego,
        "-filter_complex", filtro, "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", mp4])
    with open(os.path.join(SALIDA, f"{slug}.txt"), "w", encoding="utf-8") as f:
        f.write(f"TÍTULO:\n{guion['titulo']}\n\nALTERNATIVAS:\n" + "\n".join(guion.get("alternativas", [])) +
                f"\n\nDESCRIPCIÓN:\n{guion['descripcion']}\n\nQUÉ GRABAR:\n" +
                "\n".join(f"- Bloque {i + 1}: {b.get('grabar', '')}" for i, b in enumerate(guion["bloques"])) + "\n")
    print(f"✔ {mp4}  ({total:.1f} s, {len(vids)} planos)")
    return mp4


def main():
    import guiones
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    demo = "--demo" in sys.argv
    carpeta = sys.argv[sys.argv.index("--clips") + 1] if "--clips" in sys.argv else None
    quien = args[0] if args else "todos"
    for i, g in enumerate(guiones.GUIONES, 1):
        if quien == "todos" or quien in (f"{i:02d}", str(i), g["slug"]):
            print(f"\n■ {i:02d} {g['slug']}")
            propia = os.path.join(AQUI, "clips", f"{i:02d}")
            comun = os.path.join(AQUI, "clips")
            fabricar(g, carpeta or (propia if os.path.isdir(propia) and os.listdir(propia) else comun), demo=demo)


if __name__ == "__main__":
    main()
