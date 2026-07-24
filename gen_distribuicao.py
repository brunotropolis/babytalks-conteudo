# -*- coding: utf-8 -*-
"""Distribuicao/agendamento dos posts Baby Talks.
Regra (definida pelo Bruno):
 - 3 posts por dia: manha (09h), tarde (13h), noite (19h).
 - GUIA: 2 cortes por dia (slots manha+tarde). Quando os cortes acabam, viram emocionais.
 - Slot noite alterna: dia par = MEME, dia impar = post EMOCIONAL.
 - Cortes nunca se repetem. Determinístico: nova leva entra no fim da fila e estende os dias.
Gera distribuicao.html (calendario) + contador (usado/faltando).
Uso: python gen_distribuicao.py [YYYY-MM-DD_inicio]  (default = hoje passado por --hoje)
"""
import json, sys, pathlib, datetime
D = pathlib.Path(__file__).parent
BASE = "https://conteudo.babytalks.com.br/midia/"
EVENTO = datetime.date(2026, 8, 22)
HORAS = [("manhã","09:00"), ("tarde","13:00"), ("noite","19:00")]

posts = {p["n"]: p for p in json.loads((D/"posts.json").read_text(encoding="utf-8"))["posts"]}
def pronto(n): return n in posts and posts[n]["status"] in ("PRONTO","POSTADO")

# ---- filas (ordem estavel; nova leva so acrescenta no fim) ----
# cortes intercalando as 3 palestrantes pra nao repetir a mesma em sequencia
CORTES = [n for n in ["KJ01","KP01","KL01","KJ02","KP02","KL02","KJ03","KP03","KL03","KJ04","KP04"] if pronto(n)]
EMO    = [f"P{i}" for i in range(1,40) if pronto(f"P{i}")]      # tematicos parto/puerperio/gestacao (+ futuros)
MEME   = [f"M{i}" for i in range(1,60) if pronto(f"M{i}")]

def rotulo(n):
    p = posts[n]; fmt = p["formato"]
    if str(n).startswith("K"): tipo = "Corte de live"
    elif str(n).startswith("M"): tipo = "Meme"
    else: tipo = "Conteúdo"
    linha = (p.get("caption") or p.get("hook") or "").strip().split("\n")[0][:82]
    m = p.get("midia") or []
    capa = m[0] if m else ""
    return dict(n=n, tipo=tipo, fmt=fmt, linha=linha, capa=capa,
                postado=(p["status"]=="POSTADO"), nmid=len(m))

def hoje():
    for a in sys.argv[1:]:
        try: return datetime.date.fromisoformat(a)
        except ValueError: pass
    return datetime.date.today()

def distribuir(inicio):
    ci = ei = mi = 0
    dias = []
    d = 0
    # roda enquanto houver cortes OU emocionais (memes so preenchem a noite)
    while ci < len(CORTES) or ei < len(EMO):
        data = inicio + datetime.timedelta(days=d)
        slots = []
        # manha + tarde: corte, senao emocional
        for _ in range(2):
            if ci < len(CORTES): slots.append(CORTES[ci]); ci += 1
            elif ei < len(EMO):  slots.append(EMO[ei]); ei += 1
            else:                slots.append(None)
        # noite: par = meme, impar = emocional (fallback meme)
        if d % 2 == 0 and mi < len(MEME): slots.append(MEME[mi]); mi += 1
        elif ei < len(EMO):               slots.append(EMO[ei]); ei += 1
        elif mi < len(MEME):              slots.append(MEME[mi]); mi += 1
        else:                             slots.append(None)
        dias.append((data, slots))
        d += 1
        if d > 60: break
    return dias, dict(cortes=ci, emo=ei, meme=mi)

def render():
    inicio = hoje()
    dias, usados = distribuir(inicio)
    fim = dias[-1][0] if dias else inicio
    faltam_dias = (EVENTO - fim).days
    total_slots = sum(1 for _,s in dias for x in s if x)
    postados = sum(1 for p in posts.values() if p["status"]=="POSTADO")

    linhas = []
    for data, slots in dias:
        cells = []
        for (nome,hora), n in zip(HORAS, slots):
            if not n:
                cells.append(f'<td class="vazio">—</td>'); continue
            r = rotulo(n)
            capa = r["capa"] if r["capa"].startswith("http") else BASE + r["capa"]
            vid = capa.lower().endswith((".mp4",".mov",".webm"))
            thumb = (f'<video src="{capa}#t=2" muted preload="metadata"></video><span class="pl">&#9654;</span>'
                     if vid else f'<img src="{capa}" loading="lazy">')
            badge = {"Corte de live":"corte","Meme":"meme","Conteúdo":"emo"}[r["tipo"]]
            done = ' feito' if r["postado"] else ''
            cells.append(
              f'<td class="slot{done}"><div class="hh">{nome} · {hora}</div>'
              f'<div class="mini"><a href="{capa}" target="_blank">{thumb}</a>'
              f'<div class="txt"><span class="b {badge}">{r["tipo"]}</span>'
              f'<span class="id">#{n} · {r["fmt"]}</span><p>{r["linha"]}</p></div></div></td>')
        dow = ["seg","ter","qua","qui","sex","sáb","dom"][data.weekday()]
        linhas.append(f'<tr><th>{data.strftime("%d/%m")}<span>{dow}</span></th>{"".join(cells)}</tr>')

    resumo = (f'<b>{total_slots}</b> posts distribuídos em <b>{len(dias)}</b> dias '
              f'(de {inicio.strftime("%d/%m")} a {fim.strftime("%d/%m")}). '
              f'Usados: {usados["cortes"]} cortes · {usados["emo"]} emocionais · {usados["meme"]} memes. '
              f'Já postados: {postados}.')
    aviso = (f'⚠️ O plano cobre até <b>{fim.strftime("%d/%m")}</b>. Faltam <b>{faltam_dias} dias</b> '
             f'até o evento (22/08) — precisamos produzir mais pra preencher (a nova leva entra no fim da fila).'
             if faltam_dias > 0 else 'Plano cobre até o evento. 🎉')

    html = f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="robots" content="noindex, nofollow">
<title>Baby Talks · Distribuição</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
 :root{{--lilas:#8E9BD1;--lilas-esc:#6F7EB8;--magenta:#C95FA3;--azul:#1F2A56;--branco:#F8F7F4;--lavanda:#E4E6F2;--verde:#2EA66C;--azul-suave:#4A5578}}
 *{{box-sizing:border-box;margin:0;padding:0}}
 body{{font-family:'DM Sans',sans-serif;background:var(--branco);color:var(--azul);padding:0 16px 80px;line-height:1.45}}
 .wrap{{max-width:1200px;margin:0 auto}}
 .back{{display:inline-flex;gap:7px;font-size:14px;font-weight:700;color:var(--lilas-esc);text-decoration:none;margin:22px 0 8px}}
 header.top{{text-align:center;margin:8px 0 18px}}
 .eyebrow{{font-size:11px;letter-spacing:2.5px;text-transform:uppercase;color:var(--magenta);font-weight:700}}
 header.top h1{{font-family:'Fraunces',serif;font-size:34px;margin-top:6px}}
 .resumo{{background:#fff;border:1px solid var(--lavanda);border-left:4px solid var(--verde);border-radius:12px;padding:12px 16px;font-size:13.5px;margin-bottom:8px}}
 .aviso{{background:#FFF6E9;border:1px solid #F1D9AD;border-radius:12px;padding:12px 16px;font-size:13px;color:#7a5a1e;margin-bottom:18px}}
 table{{border-collapse:separate;border-spacing:0 10px;width:100%}}
 th.dia{{}}
 tr th{{width:74px;text-align:left;font-family:'Fraunces',serif;font-size:20px;color:var(--azul);vertical-align:top;padding-top:14px}}
 tr th span{{display:block;font-family:'DM Sans';font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--azul-suave);font-weight:700}}
 td{{background:#fff;border:1px solid var(--lavanda);border-radius:12px;padding:10px;vertical-align:top;width:33%}}
 td.vazio{{color:var(--lilas-esc);text-align:center;font-size:22px}}
 td.feito{{background:#F1FBF5;border-color:#Bfe8cf}}
 .hh{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--azul-suave);margin-bottom:8px}}
 .mini{{display:flex;gap:10px}}
 .mini a{{position:relative;flex:0 0 64px;height:80px;border-radius:8px;overflow:hidden;border:1px solid var(--lavanda);display:block}}
 .mini img,.mini video{{width:100%;height:100%;object-fit:cover}}
 .pl{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:20px;text-shadow:0 2px 6px rgba(0,0,0,.5)}}
 .txt{{min-width:0;flex:1}}
 .b{{font-size:9.5px;font-weight:700;padding:2px 7px;border-radius:100px;text-transform:uppercase;letter-spacing:.05em;color:#fff}}
 .b.corte{{background:var(--magenta)}} .b.meme{{background:#F0A93B}} .b.emo{{background:var(--lilas-esc)}}
 .id{{display:block;font-size:11px;font-weight:700;color:var(--azul);margin-top:4px}}
 .txt p{{font-size:11.5px;color:var(--azul-suave);margin-top:3px}}
 @media(max-width:760px){{table,tbody,tr,td,th{{display:block;width:auto}}tr{{margin-bottom:12px}}tr th{{padding:6px 0}}td{{margin-bottom:8px}}}}
</style></head><body>
<div class="wrap">
  <a class="back" href="index.html">← Central de Conteúdo</a>
  <header class="top"><span class="eyebrow">Plano de postagem</span><h1>Distribuição</h1></header>
  <div class="resumo">{resumo}</div>
  <div class="aviso">{aviso}</div>
  <table><tbody>
    {"".join(linhas)}
  </tbody></table>
  <p style="text-align:center;margin-top:20px;font-size:12.5px;color:var(--lilas-esc)">
    Guia: 2 cortes/dia + noite alternando meme/emocional. Verde = já postado. Pode trocar/editar à vontade no studio.</p>
</div></body></html>"""
    (D/"distribuicao.html").write_text(html, encoding="utf-8")
    print(resumo.replace("<b>","").replace("</b>",""))
    print("plano cobre ate", fim.strftime("%d/%m"), "| faltam", faltam_dias, "dias ate 22/08")

render()
