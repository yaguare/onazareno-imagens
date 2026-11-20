"""Genera el mapa de entidades (Enlaces iluminados) de horoscopo777.com.br (PT-BR) como .xlsx.

Uso: python3 generar_mapa_horoscopo777.py

Lee existentes-horoscopo777.json (inventario de la REST pública, 19/11/2026: 974 posts publicados) y
usa SOLO slugs reales del sitio, salvo los futuros comprometidos de la serie 2028.

Familias:
- signos -> signo-{signo} (y gentilicios: ariano, taurina...).
- fechas completas ("5 de março", "1º de julho") -> su "nascidos em" (slugs reales, con las excepciones
  nascidos-en de Libra, 1o-de-julho y el 6 de janeiro en signo-capricornio-...).
- casas -> casa-{n}-astrologia ("casa 3", "Casa 3", "terceira casa") y casas-astrologicas.
- os planetas astrológicos (pilar), signos do zodíaco, data de nascimento (buscador).
- horóscopos 2027 y 2028 por título: pilar del año, pilar del amor, meses, anuales, mensuales, amor por signo.
- por signo: "X e o Amor", "A personalidade de X", "Homem de X", "Mulher de X", "X e a comunicação",
  "Como tratar com um {gentilicio}", horóscopo de hoje.
- compatibilidades por título ("compatibilidade entre Áries e Touro") y ascendentes ("Áries ascendente Touro").
Futuros (slug fijo = compromiso): horoscopo-{signo}-{mes}-2028 (julho a dezembro), horoscopo-do-amor-{signo}-2028.
"""
import json
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "mapa-enlaces-iluminados-horoscopo777.xlsx")
EXIST = json.load(open(os.path.join(AQUI, "existentes-horoscopo777.json"), encoding="utf-8"))
SLUGS = {x["slug"]: x for x in EXIST}

SIGNOS = [
    ("aries", "Áries", ["ariano", "arianos", "ariana", "arianas"]),
    ("touro", "Touro", ["taurino", "taurinos", "taurina", "taurinas"]),
    ("gemeos", "Gêmeos", ["geminiano", "geminianos", "geminiana", "geminianas"]),
    ("cancer", "Câncer", ["canceriano", "cancerianos", "canceriana", "cancerianas"]),
    ("leao", "Leão", ["leonino", "leoninos", "leonina", "leoninas"]),
    ("virgem", "Virgem", ["virginiano", "virginianos", "virginiana", "virginianas"]),
    ("libra", "Libra", ["libriano", "librianos", "libriana", "librianas"]),
    ("escorpiao", "Escorpião", ["escorpiano", "escorpianos", "escorpiana", "escorpianas"]),
    ("sagitario", "Sagitário", ["sagitariano", "sagitarianos", "sagitariana", "sagitarianas"]),
    ("capricornio", "Capricórnio", ["capricorniano", "capricornianos", "capricorniana", "capricornianas"]),
    ("aquario", "Aquário", ["aquariano", "aquarianos", "aquariana", "aquarianas"]),
    ("peixes", "Peixes", ["pisciano", "piscianos", "pisciana", "piscianas"]),
]
NOME = {k: S for k, S, _ in SIGNOS}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
MSLUG = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
ORD = ["primeira", "segunda", "terceira", "quarta", "quinta", "sexta", "sétima", "oitava", "nona",
       "décima", "décima primeira", "décima segunda"]

filas = []  # (grupo, familia, entidad, formas, slug, estado, id, nota)


def add(grupo, familia, entidad, formas, slug, nota="", futuro=False):
    vistas = []
    for f in formas:
        if f not in vistas:
            vistas.append(f)
    if slug in SLUGS:
        estado, pid = "Publicado", SLUGS[slug]["id"]
    elif futuro:
        estado, pid = "Futuro", ""
    else:
        return  # destino inexistente: no entra
    filas.append((grupo, familia, entidad, " | ".join(vistas), slug, estado, pid, nota))


def cap(s):
    return s[0].upper() + s[1:]


# ---------- Signos ----------
for k, S, gent in SIGNOS:
    add("Signos", "Pilar do signo", f"Signo {S}",
        [S, f"signo de {S}", f"Signo de {S}", f"signo {S}", f"Signo {S}"] + gent, f"signo-{k}",
        "Mayúsculas exactas: \"câncer\", \"touro\", \"peixes\", \"libra\" en minúscula no se marcan.")
add("Signos", "Pilar", "Signos do Zodíaco",
    ["signos do zodíaco", "Signos do Zodíaco", "signos do Zodíaco", "Signos do zodíaco"], "signos-do-zodiaco")
add("Signos", "Ferramenta", "Data de nascimento",
    ["data de nascimento", "Data de nascimento"], "data-de-nascimento")

# ---------- Planetas ----------
add("Planetas", "Pilar", "Os planetas astrológicos",
    ["planetas astrológicos", "Planetas astrológicos", "planetas na astrologia"],
    "os-planetas-astrologicos-as-forcas-arquetipicas-que-moldam-a-experiencia-humana")

# ---------- Casas ----------
add("Casas", "Pilar", "Casas astrológicas",
    ["casas astrológicas", "Casas astrológicas", "Casas Astrológicas", "casas da astrologia"],
    "casas-astrologicas")
for n in range(1, 13):
    add("Casas", "Casa", f"Casa {n}",
        [f"casa {n}", f"Casa {n}", f"{ORD[n - 1]} casa", f"{cap(ORD[n - 1])} casa", f"Casa {n} na astrologia"],
        f"casa-{n}-astrologia")

# ---------- Nascidos em (slugs reales del inventario) ----------
rx = re.compile(r"^signo-([a-z]+)-nascidos-e[mn]-(\d+)(o?)-de-([a-z]+)$")
fechas = {}
for s in SLUGS:
    m = rx.match(s)
    if m:
        d, mes = int(m.group(2)), MSLUG.index(m.group(4)) + 1
        assert (d, mes) not in fechas, (s, fechas.get((d, mes)))
        fechas[(d, mes)] = s
assert len(fechas) == 366, len(fechas)
for (d, mi), slug in sorted(fechas.items(), key=lambda t: (t[0][1], t[0][0])):
    M = MESES[mi - 1]
    dias = [str(d)] + (["1º"] if d == 1 else [])
    formas = []
    for dd in dias:
        for mes in (M, cap(M)):
            formas += [f"{dd} de {mes}", f"nascidos em {dd} de {mes}", f"nascido em {dd} de {mes}",
                       f"nascida em {dd} de {mes}", f"quem nasce em {dd} de {mes}"]
    add("Nascidos em", "Dia", f"Nascidos em {d} de {M}", formas, slug)

# ---------- Por signo (series atemporales) ----------
for k, S, gent in SIGNOS:
    add("Signo", "Amor", f"{S} e o Amor", [f"{S} e o Amor", f"{S} e o amor"], f"{k}-e-o-amor")
    add("Signo", "Personalidade", f"A personalidade de {S}",
        [f"A personalidade de {S}", f"a personalidade de {S}", f"personalidade de {S}"],
        f"a-personalidade-de-{k}")
    add("Signo", "Homem", f"Homem de {S}", [f"Homem de {S}", f"homem de {S}", f"O homem de {S}", f"o homem de {S}"],
        f"o-homem-de-{k}")
    mulher = f"a-mulher-de-{k}" if f"a-mulher-de-{k}" in SLUGS else f"a-mulher-{k}"
    add("Signo", "Mulher", f"Mulher de {S}", [f"Mulher de {S}", f"mulher de {S}", f"A mulher de {S}", f"a mulher de {S}"],
        mulher)
    add("Signo", "Comunicação", f"{S} e a comunicação", [f"{S} e a comunicação"], f"{k}-e-a-comunicacao")
    g = gent[0]
    trat = f"como-tratar-com-um-{g}" if f"como-tratar-com-um-{g}" in SLUGS else f"como-tratar-com-um-{k}"
    add("Signo", "Como tratar", f"Como tratar com um {g}",
        [f"como tratar com um {g}", f"Como tratar com um {g}", f"Como Tratar com um {cap(g)}",
         f"como tratar um {g}", f"como lidar com um {g}"], trat)
    add("Signo", "Horóscopo de hoje", f"Horóscopo de {S} hoje",
        [f"Horóscopo de {S} hoje", f"horóscopo de {S} hoje", f"horóscopo do dia de {S}",
         f"Horóscopo do dia de {S}", f"horóscopo do dia para {S}"], f"horoscopo-do-dia-para-{k}")
add("Signo", "Horóscopo de hoje", "Horóscopo de hoje",
    ["Horóscopo de hoje", "horóscopo de hoje", "Horóscopo do dia", "horóscopo do dia"], "horoscopo-do-dia")

# ---------- Compatibilidades y ascendentes (solo los que existen) ----------
ESP_COMPAT = {("capricornio", "gemeos"): "compatibilidade-capricornio-e-gemini", ("cancer", "touro"): "cancer-e-touro"}
for a, A, _ in SIGNOS:
    for b, B, _ in SIGNOS:
        slug = ESP_COMPAT.get((a, b), f"compatibilidade-{a}-e-{b}")
        add("Compatibilidade", "Par", f"Compatibilidade {A} e {B}",
            [f"Compatibilidade {A} e {B}", f"compatibilidade {A} e {B}", f"compatibilidade entre {A} e {B}",
             f"Compatibilidade entre {A} e {B}", f"compatibilidade de {A} e {B}", f"compatibilidade de {A} com {B}"],
            slug)
        add("Ascendente", "Combinação", f"{A} ascendente {B}",
            [f"{A} ascendente {B}", f"{A} com ascendente {B}", f"{A} com ascendente em {B}"],
            f"{a}-ascendente-{b}")
add("Compatibilidade", "Pilar", "Compatibilidade Libra",
    ["compatibilidade de Libra", "Compatibilidade de Libra", "compatibilidade do signo de Libra"],
    "compatibilidade-libra")

# ---------- Horóscopos 2027 y 2028 ----------
for ano in (2027, 2028):
    G = f"Horóscopo {ano}"
    formas = [f"Horóscopo {ano}", f"horóscopo {ano}", f"horóscopo de {ano}", f"horóscopo para {ano}",
              f"Horóscopo de {ano}", f"previsões {ano}", f"Previsões {ano}", f"previsões para {ano}"]
    if ano == 2027:
        formas = [f"Horóscopo e Astrologia {ano}", f"horóscopo e astrologia {ano}"] + formas
    add(G, "Pilar do ano", f"Horóscopo {ano}", formas, f"horoscopo-{ano}")
    add(G, "Pilar do amor", f"Horóscopo do Amor {ano}",
        [f"Horóscopo do Amor {ano}", f"Horóscopo do amor {ano}", f"horóscopo do amor {ano}",
         f"horóscopo do amor de {ano}", f"horóscopo do amor para {ano}"], f"horoscopo-do-amor-{ano}")
    for mi, M in enumerate(MESES, 1):
        add(G, "Mês geral", f"Horóscopo {cap(M)} {ano}",
            [f"Horóscopo {cap(M)} {ano}", f"Horóscopo {M} {ano}", f"horóscopo {M} {ano}",
             f"Horóscopo de {cap(M)} de {ano}", f"horóscopo de {M} de {ano}", f"Horóscopo de {M} de {ano}"],
            f"horoscopo-{MSLUG[mi - 1]}-{ano}", f"\"{M} de {ano}\" solo NO se marca.")
    for k, S, _ in SIGNOS:
        add(G, "Anual do signo", f"Horóscopo {S} {ano}",
            [f"Horóscopo {S} {ano}", f"horóscopo {S} {ano}", f"horóscopo de {S} {ano}",
             f"horóscopo de {S} para {ano}", f"Horóscopo de {S} para {ano}", f"horóscopo de {S} em {ano}"],
            f"horoscopo-{k}-{ano}")
        add(G, "Amor do signo", f"Horóscopo do Amor {S} {ano}",
            [f"Horóscopo do Amor {S} {ano}", f"Horóscopo do amor {S} {ano}", f"horóscopo do amor {S} {ano}",
             f"horóscopo do amor de {S} {ano}", f"horóscopo do amor de {S} para {ano}"],
            f"horoscopo-do-amor-{k}-{ano}", futuro=(ano == 2028))
        for mi, M in enumerate(MESES, 1):
            add(G, "Mensal do signo", f"Horóscopo {S} {cap(M)} {ano}",
                [f"Horóscopo {S} {cap(M)} {ano}", f"Horóscopo {S} {M} {ano}", f"horóscopo {S} {M} {ano}",
                 f"horóscopo de {S} para {M} de {ano}", f"horóscopo de {S} em {M} de {ano}",
                 f"Horóscopo de {S} em {M} de {ano}"],
                f"horoscopo-{k}-{MSLUG[mi - 1]}-{ano}", futuro=(ano == 2028))

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
ws.append(["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
           "Slug fijo", "Categoría", "Estado", "ID", "Notas"])
slugs, formas_vistas = set(), {}
for gr, fa, en, fo, sl, es, pid, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    for f in fo.split(" | "):
        assert formas_vistas.setdefault(f, sl) == sl, (f, sl, formas_vistas[f])
    ws.append([gr, fa, en, fo, sl, "", es, pid, no])
F = "Arial"
for c in ws[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", start_color="3D2C6B")
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, size=10)
        c.alignment = Alignment(vertical="top", wrap_text=c.column in (4, 9))
for col, w in zip("ABCDEFGHI", [16, 20, 40, 70, 44, 14, 12, 8, 50]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:I{ws.max_row}"
wb.save(SALIDA)
fut = sum(1 for f_ in filas if f_[5] == "Futuro")
print(len(filas), "filas (", fut, "futuras );", sum(len(f_[3].split(" | ")) for f_ in filas), "formas")
