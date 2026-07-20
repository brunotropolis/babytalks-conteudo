# -*- coding: utf-8 -*-
# Injeta a fase "Memes de maternidade" (49 Reels) no calendario.html.
# Mídia hospedada no Supabase Storage (URLs absolutas em .memes-tmp/urls.json).
# Idempotente: remove um bloco meme anterior antes de reinserir.
import json, re
from pathlib import Path

D = Path(__file__).parent
# fonte das URLs: cópia local (auto-contida) com fallback pro temp do studio
_local = D / "memes-urls.json"
_tmp = D.parent / "babytalks-studio" / ".memes-tmp" / "urls.json"
urls = json.loads((_local if _local.exists() else _tmp).read_text(encoding="utf-8"))
nums = sorted(urls.keys(), key=lambda x: int(x))

# chamada genérica + variações pequenas
MAIN = [
 "Você está vivenciando isso na sua gestação? 😅🥰",
 "Conta aqui: já passou por isso? 😅",
 "Alguém mais se identifica? 🥰😂",
 "Marca aquela amiga grávida que VAI rir com esse 😂",
 "Isso é tão real que dói de rir 😅🥰",
 "Gestante entende, né? 🤰😂",
 "Quem viveu isso, levanta a mão 🙋‍♀️😅",
 "Só quem tá grávida entende 🥰",
 "Me diz que não é só comigo 😂",
 "A gravidez não avisa que ia ser assim 😅",
 "Real demais pra quem tá esperando bebê 🥰",
 "Rindo pra não chorar (de fofura e de sono) 😅",
 "Manda pro papai que ele vai entender 😂",
 "Ninguém te conta essas partes da gestação 😅🥰",
 "Se você riu, é porque tá vivendo isso 😂",
 "A maternidade começa antes do bebê nascer, né? 🥰",
 "Confessa: já aconteceu com você? 😅",
 "Grávida no modo: eu de novo 😂🤰",
 "Salva esse pra rir de novo depois 🥰",
 "Toda gestante tem um dia desses 😅",
 "Quem mais tá nessa fase? 🙋‍♀️🥰",
 "É rir ou chorar, e a gente escolhe rir 😂",
 "Alguém avisa que gravidez é isso aqui 😅🥰",
 "Manda pra uma grávida hoje e faz o dia dela 🥰",
 "Muito eu isso, e você? 😂",
]

HASH = [
 "#BabyTalks #Gestante #Maternidade #Gravidez #MãeDePrimeiraViagem #Curitiba",
 "#BabyTalks #Gravidez #Gestante #VidaDeGrávida #Maternidade #Curitiba",
 "#BabyTalks #Maternidade #Gestante #Grávida #BebêaCaminho #Curitiba",
 "#BabyTalks #Gestante #Gravidez #Gravidinha #MãeDeBebê #Curitiba",
]

EVENT = ("Ah, e se você é de Curitiba: dia 22/08 tem um encontro especial pra "
         "te preparar pra chegada do bebê. 💛")

def cap_for(i):
    main = MAIN[i % len(MAIN)]
    tags = HASH[i % len(HASH)]
    partes = [main]
    if i % 6 == 5:
        partes.append(EVENT)
    partes.append(tags)
    return "\n\n".join(partes)

# monta os posts e as entradas de MIDIA
posts_js = []
midia_js = []
for i, n in enumerate(nums):
    cap = cap_for(i)
    posts_js.append(
        "    {n:'M%s',pilar:'meme',fmt:'Reels',\n"
        "     hook:'Meme maternidade #%s',\n"
        "     criativo:'Meme de maternidade pra alcance e identificação. Vídeo curto, legenda leve com chamada genérica.',\n"
        "     cap:`%s`}" % (n, n, cap)
    )
    midia_js.append("  'M%s':['%s']," % (n, urls[n]))

fase = (
 "  {num:'06', titulo:'Memes de maternidade', range:'',\n"
 "   intro:'Vídeos curtos e engraçados pra gerar identificação, alcance e salvamento. Chamada genérica com variações pequenas. Programe na ordem que quiser.',\n"
 "   stories:'',\n"
 "   posts:[\n" + ",\n".join(posts_js) + "\n   ]}"
)

html = (D / "calendario.html").read_text(encoding="utf-8")

# limpa injeção anterior (idempotência)
html = re.sub(r",\n  \{num:'06', titulo:'Memes de maternidade'.*?\n   \]\}(?=\n\];)", "", html, flags=re.S)
html = re.sub(r"\n  // ==== MEMES ====.*?(?=\n\};)", "", html, flags=re.S)

# 1) pilar 'meme'
html = html.replace(
 "  conversao:{cor:'#2EA66C',nome:'Conversão'}\n};",
 "  conversao:{cor:'#2EA66C',nome:'Conversão'},\n  meme:{cor:'#F0A93B',nome:'Meme'}\n};",
)

# 2) fase nova (antes do fechamento do FASES)
html = html.replace("   ]}\n];", "   ]},\n" + fase + "\n];", 1)

# 3) entradas MIDIA (antes do fechamento do objeto MIDIA)
midia_block = "  // ==== MEMES ====\n" + "\n".join(midia_js) + "\n"
html = html.replace(
 "  'L4':['midia/lives/reels-paula-v1.mp4'],\n};",
 "  'L4':['midia/lives/reels-paula-v1.mp4'],\n" + midia_block + "};",
)

# 4) copy-links tolerante a URL absoluta
html = html.replace("media.map(s=>BASE+s)", "media.map(s=>s.startsWith('http')?s:BASE+s)")

(D / "calendario.html").write_text(html, encoding="utf-8")
print("memes injetados:", len(nums))
