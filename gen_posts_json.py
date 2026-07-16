# -*- coding: utf-8 -*-
# Gera posts.json a partir do calendario.html (fonte única: FASES + MIDIA).
# posts.json é o feed que o studio (studio.babytalks.com.br) consome via /api/plano.
# Sem datas — o calendário virou repositório; o Bruno programa um a um no studio.
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
D = Path(__file__).parent

async def go():
    html = (D/"calendario.html").read_text(encoding="utf-8")
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        await pg.set_content(html)
        await pg.wait_for_timeout(600)
        posts = await pg.evaluate("""() => {
          const out=[];
          for (const f of FASES) for (const p of f.posts) {
            const m = (MIDIA[p.n]||[]).map(s => s.replace(/^midia\\//,''));
            out.push({
              n:p.n, fase:f.num, fase_titulo:f.titulo, formato:p.fmt,
              pilar:p.pilar, hook:p.hook, caption:p.cap,
              midia:m, status: m.length ? 'PRONTO' : 'AGUARDANDO_MIDIA'
            });
          }
          return out;
        }""")
        await b.close()
    # preserva o writeback do studio (status POSTADO + permalink + postado_em)
    pj = D/"posts.json"
    if pj.exists():
        try:
            antigo = {p["n"]: p for p in json.loads(pj.read_text(encoding="utf-8")).get("posts", [])}
        except Exception:
            antigo = {}
        for p in posts:
            a = antigo.get(p["n"])
            if a and a.get("status") == "POSTADO":
                p["status"] = "POSTADO"
                if a.get("permalink"): p["permalink"] = a["permalink"]
                if a.get("postado_em"): p["postado_em"] = a["postado_em"]
    obj = {"gerado_de":"calendario.html","total":len(posts),"posts":posts}
    (D/"posts.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    pr = sum(1 for p in posts if p["status"]=="PRONTO")
    print(f"posts.json: {len(posts)} posts, {pr} PRONTO")
    for p in posts:
        if p["status"]=="PRONTO":
            print("  PRONTO n"+str(p["n"]), p["formato"], "->", p["midia"])

asyncio.run(go())
