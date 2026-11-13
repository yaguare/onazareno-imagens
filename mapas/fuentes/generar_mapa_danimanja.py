"""Genera el mapa de entidades (Enlaces iluminados) de danimanja.com.br (PT-BR) como .xlsx.

Uso: python3 generar_mapa_danimanja.py   (lee existentes-danimanja.json, inventario del 13/11/2026)

Familias elegidas por Daniel (13/11/2026):
- Horóscopos 2026, 2027 y 2028 por título (pilar del año, amor del año, mes general, anual por signo,
  amor por signo, mensual por signo). Slugs reales del inventario (con sus irregularidades, ej.
  horoscopo-janerio-2027); los 2028 que faltan van por patrón (compromiso de slug):
  horoscopo-{signo}-{mes}-2028 y horoscopo-do-amor-{signo}-2028.
- Fechas -> "nascidos em" (post principal, el que no lleva "(I)"): signo-{signo}-nascidos-em-{d}-de-{mes}.
- Ángeles cabalísticos: anjo-{nome} (nombre suelto o "Anjo X").
- Signos -> pilar del signo: signo-{signo} (nombre con mayúscula y gentilicios).
- "O signo X e o Amor" (slug real de cada signo) y Horóscopo Chinês 2027 (pilar y animales, solo por título).
"""
import json, re, unicodedata
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

SALIDA = "mapa-enlaces-iluminados-danimanja.xlsx"
INV = json.load(open("existentes-danimanja.json", encoding="utf-8"))
POR_SLUG = {p["slug"]: p for p in INV}

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
DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def cap(s):
    return s[0].upper() + s[1:]


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"\s+", " ", "".join(ch for ch in s if not unicodedata.combining(ch))).strip()


filas = []  # (grupo, familia, entidad, formas, slug, nota)


def add(grupo, familia, entidad, formas, slug, nota=""):
    vistas = []
    for f in formas:
        if f not in vistas:
            vistas.append(f)
    filas.append((grupo, familia, entidad, " | ".join(vistas), slug, nota))


# ---------- Signos ----------
for k, S, gent in SIGNOS:
    add("Signos", "Pilar do signo", f"Signo {S}",
        [f"Signo {S}", f"signo {S}", f"signo de {S}", f"Signo de {S}", S] + gent, f"signo-{k}",
        "Mayúsculas exactas: el nombre solo con mayúscula.")

# ---------- O signo X e o Amor ----------
for k, S, _ in SIGNOS:
    slug = next(s for s in (f"o-signo-{k}-e-o-amor", f"{k}-e-o-amor") if s in POR_SLUG)
    add("Signos", "Signo e o Amor", f"O signo {S} e o Amor",
        [f"O signo {S} e o Amor", f"O signo {S} e o amor", f"o signo {S} e o amor", f"{S} e o Amor",
         f"{S} e o amor", f"signo {S} no amor", f"{S} no amor"], slug)

# ---------- Ángeles ----------
for p in INV:
    if 37 in p["cats"] and p["slug"].startswith("anjo-"):
        m = re.match(r"Anjo ([^:]+):", p["title"])
        nome = m.group(1).strip()
        add("Anjos", "Anjo cabalístico", f"Anjo {nome}", [f"Anjo {nome}", f"anjo {nome}", nome], p["slug"])

# ---------- Nascidos em ----------
nasc = {}
for p in INV:
    m = re.match(r"Signo [^:]+: nascidos em (\d+)º? de (\w+)$", p["title"])
    if 8 in p["cats"] and m:
        nasc[(int(m.group(1)), norm(m.group(2)))] = p["slug"]
for mi, M in enumerate(MESES, 1):
    for d in range(1, DIAS_MES[mi - 1] + 1):
        slug = nasc.get((d, norm(M)))
        assert slug, (d, M)
        formas = []
        for dd in [str(d)] + (["1º"] if d == 1 else []):
            for mes in (M, cap(M)):
                formas += [f"{dd} de {mes}", f"nascidos em {dd} de {mes}", f"nascidas em {dd} de {mes}",
                           f"nascido em {dd} de {mes}", f"nascida em {dd} de {mes}", f"quem nasce em {dd} de {mes}"]
        add("Nascidos em", "Dia", f"Nascidos em {d} de {M}", formas, slug)

# ---------- Horóscopos 2026, 2027, 2028 ----------
CAT_ANO = {2026: 2, 2027: 30, 2028: 41}
titulos = {}
for p in INV:
    for ano, c in CAT_ANO.items():
        if c in p["cats"]:
            titulos[(ano, norm(p["title"]))] = p["slug"]


def real(ano, *tits, patron=None):
    for t in tits:
        s = titulos.get((ano, norm(t)))
        if s:
            return s, "Existe"
    assert patron and ano == 2028, (ano, tits)
    return patron, "Futuro"


for ano in (2026, 2027, 2028):
    G = f"Horóscopo {ano}"
    sl, est = real(ano, f"Astrologia e Horóscopo {ano}")
    add(G, "Pilar do ano", f"Astrologia e Horóscopo {ano}",
        [f"Astrologia e Horóscopo {ano}", f"astrologia e horóscopo {ano}", f"Horóscopo {ano}",
         f"horóscopo {ano}", f"horóscopo de {ano}", f"horóscopo para {ano}"], sl, est)
    sl, est = real(ano, f"Horóscopo do amor {ano}")
    add(G, "Pilar do amor", f"Horóscopo do amor {ano}",
        [f"Horóscopo do amor {ano}", f"Horóscopo do Amor {ano}", f"horóscopo do amor {ano}",
         f"horóscopo do amor de {ano}", f"horóscopo do amor para {ano}"], sl, est)
    for mi, M in enumerate(MESES, 1):
        ms = norm(M).replace(" ", "")
        sl, est = real(ano, f"Horóscopo {M} {ano}", patron=f"horoscopo-{ms}-{ano}")
        add(G, "Mês geral", f"Horóscopo {cap(M)} {ano}",
            [f"Horóscopo {cap(M)} {ano}", f"horóscopo {M} {ano}", f"Horóscopo de {cap(M)} de {ano}",
             f"horóscopo de {M} de {ano}"], sl, est)
    for k, S, _ in SIGNOS:
        sl, est = real(ano, f"Horóscopo {S} {ano}", f"Previsões e Horóscopo {S} {ano}",
                       patron=f"horoscopo-{k}-{ano}")
        add(G, "Anual do signo", f"Horóscopo {S} {ano}",
            [f"Previsões e Horóscopo {S} {ano}", f"Horóscopo {S} {ano}", f"horóscopo {S} {ano}",
             f"horóscopo de {S} {ano}", f"horóscopo de {S} para {ano}"], sl, est)
        sl, est = real(ano, f"Horóscopo do amor {S} {ano}", patron=f"horoscopo-do-amor-{k}-{ano}")
        add(G, "Amor do signo", f"Horóscopo do amor {S} {ano}",
            [f"Horóscopo do amor {S} {ano}", f"Horóscopo do Amor {S} {ano}", f"horóscopo do amor {S} {ano}",
             f"horóscopo do amor de {S} {ano}", f"horóscopo do amor de {S} para {ano}"], sl, est)
        for mi, M in enumerate(MESES, 1):
            ms = norm(M).replace(" ", "")
            sl, est = real(ano, f"Horóscopo {S} {M} {ano}", patron=f"horoscopo-{k}-{ms}-{ano}")
            add(G, "Mensal do signo", f"Horóscopo {S} {cap(M)} {ano}",
                [f"Horóscopo {S} {cap(M)} {ano}", f"horóscopo {S} {M} {ano}",
                 f"horóscopo de {S} para {M} de {ano}", f"horóscopo de {S} em {M} de {ano}"], sl, est)

# ---------- Horóscopo Chinês 2027 ----------
add("Horóscopo Chinês 2027", "Pilar", "Horóscopo Chinês 2027",
    ["Horóscopo Chinês 2027", "horóscopo chinês 2027", "horóscopo chinês de 2027"], "horoscopo-chines-2027")
for p in INV:
    if 36 in p["cats"] and p["slug"] != "horoscopo-chines-2027":
        A = re.sub(r"^Horóscopo Chinês 2027:? ", "", p["title"]).strip()
        add("Horóscopo Chinês 2027", "Animal", p["title"],
            [f"Horóscopo Chinês 2027: {A}", f"Horóscopo Chinês 2027 {A}", f"horóscopo chinês 2027 {A}",
             f"horóscopo chinês 2027 {A.lower()}"], p["slug"], "Animal suelto NO se marca (cambia cada año).")

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
    p = POR_SLUG.get(sl)
    estado = "Existe" if p else ("Bloqueo" if sl.startswith("ei-bloqueo") else "Futuro")
    ws.append([gr, fa, en, fo, sl, "", estado, p["id"] if p else "", "" if no in ("Existe", "Futuro") else no])
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
est = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    est[r[6]] = est.get(r[6], 0) + 1
print(len(filas), "filas;", sum(len(f_[3].split(" | ")) for f_ in filas), "formas;", est)
