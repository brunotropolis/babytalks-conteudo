# -*- coding: utf-8 -*-
"""Galeria visual de TODAS as peças produzidas — pra revisar as artes de uma vez."""
import json, pathlib
D = pathlib.Path(__file__).parent
BASE = "https://conteudo.babytalks.com.br/midia/"
posts = json.loads((D/"posts.json").read_text(encoding="utf-8"))["posts"]

EH_VIDEO = lambda f: f.lower().endswith((".mp4", ".mov", ".webm"))

def url(f):
    return f if f.startswith("http") else BASE + f

def card(p):
    midia = p.get("midia") or []
    if not midia:
        return ""
    capa = midia[0]
    n, fmt = p["n"], p["formato"]
    cap = (p.get("caption") or p.get("hook") or "").strip()
    resumo = cap.split("\n")[0][:110]
    if EH_VIDEO(capa):
        thumb = f'<video src="{url(capa)}#t=2" muted preload="metadata" playsinline></video><span class="pl">&#9654;</span>'
    else:
        thumb = f'<img src="{url(capa)}" loading="lazy">'
    extra = f'<span class="qtd">{len(midia)} slides</span>' if len(midia) > 1 else ""
    esc = cap.replace("&", "&amp;").replace("<", "&lt;")
    return f"""      <div class="peca">
        <a class="thumb" href="{url(capa)}" target="_blank">{thumb}{extra}</a>
        <div class="meta">
          <span class="id">#{n}</span><span class="fmt">{fmt}</span>
        </div>
        <p class="res">{resumo}</p>
        <details><summary>legenda</summary><div class="cap">{esc}</div></details>
      </div>"""

fases = {}
for p in posts:
    if p["status"] == "AGUARDANDO_MIDIA":
        continue
    fases.setdefault(p["fase_titulo"] or "Outros", []).append(p)

secoes = []
for titulo, ps in fases.items():
    aberta = "" if "Memes" in titulo else " open"
    cards = "\n".join(c for c in (card(p) for p in ps) if c)
    secoes.append(f"""  <details class="sec"{aberta}>
    <summary><h2>{titulo}</h2><span class="cont">{len(ps)}</span></summary>
    <div class="grade">
{cards}
    </div>
  </details>""")

html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="robots" content="noindex, nofollow">
<title>Baby Talks · Galeria de artes</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..600&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
 :root{{--lilas:#8E9BD1;--lilas-esc:#6F7EB8;--magenta:#C95FA3;--azul:#1F2A56;--branco:#F8F7F4;--lavanda:#E4E6F2;--azul-suave:#4A5578}}
 *{{box-sizing:border-box;margin:0;padding:0}}
 body{{font-family:'DM Sans',sans-serif;background:var(--branco);color:var(--azul);padding:0 20px 80px;line-height:1.5}}
 .wrap{{max-width:1180px;margin:0 auto}}
 .back{{display:inline-flex;gap:7px;font-size:14px;font-weight:700;color:var(--lilas-esc);text-decoration:none;margin:22px 0 8px}}
 .back:hover{{color:var(--magenta)}}
 header.top{{text-align:center;margin:8px 0 26px}}
 .eyebrow{{font-size:11px;letter-spacing:2.5px;text-transform:uppercase;color:var(--magenta);font-weight:700}}
 header.top h1{{font-family:'Fraunces',serif;font-size:36px;line-height:1.1;margin-top:6px}}
 header.top p{{font-size:14px;color:var(--azul-suave);margin-top:8px}}
 .sec{{background:#fff;border:1px solid var(--lavanda);border-radius:16px;margin-bottom:14px;overflow:hidden}}
 .sec>summary{{list-style:none;cursor:pointer;display:flex;align-items:center;gap:12px;padding:18px 22px}}
 .sec>summary::-webkit-details-marker{{display:none}}
 .sec>summary h2{{font-family:'Fraunces',serif;font-size:21px;flex:1}}
 .cont{{font-size:12px;font-weight:700;color:#fff;background:var(--lilas-esc);padding:4px 11px;border-radius:100px}}
 .sec[open]>summary{{border-bottom:1px solid var(--lavanda)}}
 .grade{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px;padding:18px 22px 24px}}
 .peca{{display:flex;flex-direction:column}}
 .thumb{{position:relative;display:block;width:100%;aspect-ratio:4/5;border-radius:12px;overflow:hidden;
   background:linear-gradient(150deg,#EAE2F1,#F4EEF4);border:1px solid var(--lavanda)}}
 .thumb img,.thumb video{{width:100%;height:100%;object-fit:cover;display:block}}
 .thumb:hover{{border-color:var(--magenta);box-shadow:0 10px 24px rgba(201,95,163,.18)}}
 .pl{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:40px;color:#fff;
   text-shadow:0 3px 10px rgba(0,0,0,.5);background:rgba(31,42,86,.12)}}
 .qtd{{position:absolute;right:8px;bottom:8px;font-size:11px;font-weight:700;background:rgba(31,42,86,.85);
   color:#fff;padding:3px 9px;border-radius:100px}}
 .meta{{display:flex;gap:6px;align-items:center;margin-top:8px}}
 .id{{font-size:12px;font-weight:700;color:var(--azul)}}
 .fmt{{font-size:10.5px;font-weight:700;color:var(--azul-suave);background:var(--lavanda);padding:2px 8px;border-radius:100px}}
 .res{{font-size:12px;color:var(--azul-suave);margin-top:5px;line-height:1.35}}
 details.peca-cap,.peca details{{margin-top:6px}}
 .peca summary{{font-size:11.5px;color:var(--magenta);cursor:pointer;font-weight:700}}
 .cap{{white-space:pre-wrap;font-size:11.5px;color:#2b3556;background:var(--branco);border:1px dashed var(--lilas);
   border-radius:10px;padding:9px;margin-top:6px;max-height:190px;overflow:auto}}
 footer{{text-align:center;margin-top:30px;font-size:12.5px;color:var(--lilas-esc)}}
</style></head><body>
<div class="wrap">
  <a class="back" href="index.html">← Central de Conteúdo</a>
  <header class="top">
    <span class="eyebrow">Revisão visual</span>
    <h1>Galeria de artes</h1>
    <p>Todas as peças produzidas, por fase. Clique na arte pra abrir em tamanho cheio; clique em "legenda" pra ler o texto.</p>
  </header>
{chr(10).join(secoes)}
  <footer>Central interna · não indexada</footer>
</div>
</body></html>"""
(D/"galeria.html").write_text(html, encoding="utf-8")
total = sum(len(v) for v in fases.values())
print("galeria.html:", total, "peças em", len(fases), "fases ·", len(html), "bytes")
