"""Genera el mapa de entidades (Enlaces iluminados) de horoscopobrasileiro.com.br (PT-BR) como .xlsx.

Uso: python3 generar_mapa_horoscopobrasileiro.py

Familias (slugs reales del sitio, 08/11/2026):
- pilar de signo: signo-{signo} (URL /{signo}/signo-{signo}/). Ojo: los posts viejos "aries" y "gemeos"
  de la categoría Zodíaco NO son destino.
- planetas: sol, lua, mercurio, venus, marte, jupiter, saturno, urano, netuno, plutao (cat. Astrologia)
  y la pilar os-planetas-astrologicos.
- nascidos em: nascidos-em-{N}-de-{mes} (cat. Seu aniversário) con sus excepciones (ver ESPECIALES).
- horóscopos 2027: horoscopo-2027, previsao-{mes}-2027, horoscopo-{signo}-2027, horoscopo-{signo}-{mes}-2027,
  horoscopo-do-amor-2027, horoscopo-do-amor-{signo}-2027.
- horóscopos 2028: previsoes-horoscopo-2028, horoscopo-{mes}-2028, horoscopo-{signo}-2028,
  horoscopo-{signo}-{mes}-2028, horoscopo-do-amor-2028, horoscopo-do-amor-{signo}-2028.
Futuros (slug fijo = compromiso): lua-nova, lua-cheia; nascidos-em-3/4-de-setembro (pendientes).
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

SALIDA = "mapa-enlaces-iluminados-horoscopobrasileiro.xlsx"

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
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
MSLUG = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ESPECIALES = {  # (dia, mes) -> slug real
    (19, 8): "signo-leao-nascidos-em-19-de-agosto",
    (22, 8): "signo-leao-nascidos-em-22-de-agosto",
    (4, 12): "nascidos-em-de-dezembro",
}
for d in range(22, 32):
    ESPECIALES[(d, 12)] = f"nascidos-em-{d}-de-decembro"

filas = []  # (grupo, familia, entidad, formas, slug, nota)


def add(grupo, familia, entidad, formas, slug, nota=""):
    vistas = []
    for f in formas:
        if f not in vistas:
            vistas.append(f)
    filas.append((grupo, familia, entidad, " | ".join(vistas), slug, nota))


def cap(s):
    return s[0].upper() + s[1:]


# ---------- Signos ----------
for k, S, gent in SIGNOS:
    add("Signos", "Pilar do signo", f"Signo {S}",
        [S, f"signo de {S}", f"Signo de {S}", f"signo {S}", f"Signo {S}"] + gent,
        f"signo-{k}", "Mayúsculas exactas: \"câncer\", \"touro\", \"peixes\", \"libra\" en minúscula no se marcan.")

# ---------- Planetas (existentes) ----------
add("Planetas", "Pilar", "Os planetas astrológicos",
    ["planetas astrológicos", "planetas na astrologia"], "os-planetas-astrologicos")
add("Planetas", "Luminar", "Sol", ["o Sol", "O Sol"], "sol", "Solo con mayúscula y artículo.")
add("Planetas", "Luminar", "Lua", ["a Lua", "A Lua"], "lua",
    "\"Lua Nova\" y \"Lua Cheia\" ganan por ser más largas.")
for k, P in [("mercurio", "Mercúrio"), ("venus", "Vênus"), ("marte", "Marte"), ("jupiter", "Júpiter"),
             ("saturno", "Saturno"), ("urano", "Urano"), ("netuno", "Netuno"), ("plutao", "Plutão")]:
    add("Planetas", "Planeta", P, [P, f"planeta {P}"], k)

# ---------- Lunaciones (futuras) ----------
add("Conceitos", "Lunação", "Lua Nova", ["Lua Nova", "Lua nova", "lua nova", "Luas Novas"], "lua-nova",
    "Futuro: slug fijo.")
add("Conceitos", "Lunação", "Lua Cheia", ["Lua Cheia", "Lua cheia", "lua cheia", "Luas Cheias"], "lua-cheia",
    "Futuro: slug fijo.")

# ---------- Nascidos em ----------
for mi, M in enumerate(MESES, 1):
    for d in range(1, DIAS_MES[mi - 1] + 1):
        slug = ESPECIALES.get((d, mi), f"nascidos-em-{d}-de-{MSLUG[mi - 1]}")
        dias = [str(d)] + (["1º"] if d == 1 else [])
        formas = []
        for dd in dias:
            for mes in (M, cap(M)):
                formas += [f"{dd} de {mes}", f"nascidos em {dd} de {mes}", f"nascido em {dd} de {mes}",
                           f"nascida em {dd} de {mes}", f"quem nasce em {dd} de {mes}"]
        nota = "Pendiente de crear." if (d, mi) in ((3, 9), (4, 9)) else ""
        add("Nascidos em", "Dia", f"Nascidos em {d} de {M}", formas, slug, nota)

# ---------- Horóscopos 2027 y 2028 ----------
for ano in (2027, 2028):
    G = f"Horóscopo {ano}"
    pilar = "horoscopo-2027" if ano == 2027 else "previsoes-horoscopo-2028"
    formas = [f"Horóscopo {ano}", f"horóscopo {ano}", f"horóscopo de {ano}", f"horóscopo para {ano}",
              f"previsões {ano}", f"Previsões {ano}", f"previsões para {ano}"]
    if ano == 2028:
        formas = [f"Previsões e horóscopo {ano}", f"previsões e horóscopo {ano}"] + formas
    add(G, "Pilar do ano", f"Pilar {ano}", formas, pilar)
    add(G, "Pilar do amor", f"Horóscopo do amor {ano}",
        [f"Horóscopo do amor {ano}", f"horóscopo do amor {ano}", f"Horóscopo do Amor {ano}",
         f"horóscopo do amor para {ano}"], f"horoscopo-do-amor-{ano}")
    for mi, M in enumerate(MESES, 1):
        slug = f"previsao-{MSLUG[mi - 1]}-{ano}" if ano == 2027 else f"horoscopo-{MSLUG[mi - 1]}-{ano}"
        add(G, "Mês geral", f"Horóscopo {cap(M)} {ano}",
            [f"Horóscopo {cap(M)} {ano}", f"horóscopo {M} {ano}", f"Horóscopo de {cap(M)} de {ano}",
             f"horóscopo de {M} de {ano}", f"previsão de {M} de {ano}", f"Previsão {cap(M)} {ano}"],
            slug, f"\"{M} de {ano}\" solo NO se marca.")
    for k, S, _ in SIGNOS:
        add(G, "Anual do signo", f"Horóscopo {S} {ano}",
            [f"Horóscopo {S} {ano}", f"horóscopo {S} {ano}", f"horóscopo de {S} {ano}",
             f"horóscopo de {S} para {ano}", f"previsão {S} {ano}", f"previsões de {S} para {ano}"],
            f"horoscopo-{k}-{ano}")
        add(G, "Amor do signo", f"Horóscopo do amor {S} {ano}",
            [f"Horóscopo do amor {S} {ano}", f"horóscopo do amor {S} {ano}",
             f"horóscopo do amor de {S} {ano}", f"horóscopo do amor de {S} para {ano}"],
            f"horoscopo-do-amor-{k}-{ano}")
        for mi, M in enumerate(MESES, 1):
            add(G, "Mensal do signo", f"Horóscopo {S} {cap(M)} {ano}",
                [f"Horóscopo {S} {cap(M)} {ano}", f"horóscopo {S} {M} {ano}",
                 f"horóscopo de {S} para {M} de {ano}", f"horóscopo de {S} em {M} de {ano}"],
                f"horoscopo-{k}-{MSLUG[mi - 1]}-{ano}")

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
ws.append(["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
           "Slug fijo", "Categoría", "Estado", "ID", "Notas"])
slugs, formas_vistas = set(), {}
for gr, fa, en, fo, sl, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    for f in fo.split(" | "):
        assert formas_vistas.setdefault(f, sl) == sl, (f, sl, formas_vistas[f])
    ws.append([gr, fa, en, fo, sl, "", "", "", no])
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
print(len(filas), "filas;", sum(len(f_[3].split(" | ")) for f_ in filas), "formas")
