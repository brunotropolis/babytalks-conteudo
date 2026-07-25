# -*- coding: utf-8 -*-
"""Gemini escolhe o melhor frame de capa de cada reels -> capas.json (n -> ms)."""
import os, sys, json, time, pathlib, subprocess
from google import genai
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
FP = r"C:/Users/bruno/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin/ffprobe.exe"
PROMPT = ("Escolha a CAPA (thumbnail) deste Reels vertical de um evento de maternidade. "
 "Me diga o SEGUNDO do frame mais bonito pra capa: rosto/pessoa nítido e bem enquadrado, "
 "boa expressão, texto legível se houver na tela, evitando transições, fades, cortes e borrões. "
 "Prefira um momento com a pessoa em foco. Responda APENAS um JSON: "
 '{"segundo": <numero, ex 2.3>, "motivo": "<curto>"}.')

def dur(p):
    return float(subprocess.check_output([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)]).strip())

def escolher(path):
    f = client.files.upload(file=str(path))
    while f.state and str(f.state).endswith("PROCESSING"):
        time.sleep(2.5); f = client.files.get(name=f.name)
    t = client.models.generate_content(model="gemini-2.5-flash", contents=[f, PROMPT]).text.strip()
    if t.startswith("```"): t = t.strip("`"); t = t[4:] if t.lower().startswith("json") else t
    try: return float(json.loads(t).get("segundo", 1.5))
    except Exception: return 1.5

cp = pathlib.Path("capas.json")
capas = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
for arg in sys.argv[1:]:
    n, path = arg.split("=", 1)
    if n in capas: continue
    p = pathlib.Path(path)
    if not p.exists(): print("faltando:", path); continue
    seg = escolher(p)
    d = dur(p)
    seg = max(0.3, min(seg, d - 0.3))
    capas[n] = int(round(seg * 1000))
    cp.write_text(json.dumps(capas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {n}: {seg:.1f}s ({capas[n]}ms) de {d:.1f}s")
