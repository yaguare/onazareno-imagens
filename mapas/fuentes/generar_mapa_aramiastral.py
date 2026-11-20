"""Genera el mapa de entidades (Enlaces iluminados) de aramiastral.com (castellano neutro) como .xlsx.

Uso: python3 generar_mapa_aramiastral.py

Decisión de Daniel (16/11/2026): mapa solo astrológico. Ángeles, horas espejo y números
quedan afuera por ahora. Todo es futuro salvo el horóscopo del amor 2027 (se escribe el 16/11).
Familias (slug fijo = compromiso):
- signos: signo-{signo}
- planetas: el-sol-en-astrologia, la-luna-en-astrologia, planeta-{planeta}; pilar planetas-en-astrologia
- retrógrados: {planeta}-retrogrado (Mercurio a Plutón)
- lunaciones y eclipses: luna-nueva, luna-llena, eclipses
- fechas: nacidos-el-{d}-de-{mes} (366, futuros; toda fecha completa enlaza ahí, también en horóscopos)
- amor 2027: pilar horoscopo-amor-2027 (post, categoría Amor 2027) y horoscopo-amor-{signo}-2027
- ascendentes (20/11/2026): pilar general que-es-el-ascendente (con los planetas), pilares
  {signo}-y-sus-ascendentes y 144 combinaciones {sol}-ascendente-{asc}, en la categoría del signo solar
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

SALIDA = "mapa-enlaces-iluminados-aramiastral.xlsx"

SIGNOS = [
    ("aries", "Aries", "ariano"), ("tauro", "Tauro", "taurino"), ("geminis", "Géminis", "geminiano"),
    ("cancer", "Cáncer", "canceriano"), ("leo", "Leo", "leonino"), ("virgo", "Virgo", "virginiano"),
    ("libra", "Libra", "libriano"), ("escorpio", "Escorpio", "escorpiano"),
    ("sagitario", "Sagitario", "sagitariano"), ("capricornio", "Capricornio", "capricorniano"),
    ("acuario", "Acuario", "acuariano"), ("piscis", "Piscis", "pisciano"),
]
PLANETAS = [("mercurio", "Mercurio"), ("venus", "Venus"), ("marte", "Marte"), ("jupiter", "Júpiter"),
            ("saturno", "Saturno"), ("urano", "Urano"), ("neptuno", "Neptuno"), ("pluton", "Plutón")]

filas = []  # (grupo, familia, entidad, formas, slug, categoria, estado, nota)


def add(grupo, familia, entidad, formas, slug, categoria="", estado="Futuro", nota=""):
    vistas = []
    for f in formas:
        if f not in vistas:
            vistas.append(f)
    filas.append((grupo, familia, entidad, " | ".join(vistas), slug, categoria, estado, nota))


# ---------- Signos ----------
for k, S, g in SIGNOS:
    gent = [g, g + "s", g[:-1] + "a", g[:-1] + "as"]
    add("Signos", "Pilar del signo", f"Signo {S}",
        [S, f"signo {S}", f"Signo {S}", f"signo de {S}", f"Signo de {S}"] + gent, f"signo-{k}",
        nota="Mayúsculas exactas: \"cáncer\", \"leo\", \"libra\" en minúscula no se marcan.")

# ---------- Planetas ----------
add("Planetas", "Pilar", "Los planetas en astrología",
    ["planetas en astrología", "planetas astrológicos", "planetas en la astrología"], "planetas-en-astrologia")
add("Planetas", "Luminar", "El Sol en astrología", ["el Sol", "El Sol"], "el-sol-en-astrologia",
    nota="Solo con mayúscula y artículo.")
add("Planetas", "Luminar", "La Luna en astrología", ["la Luna", "La Luna"], "la-luna-en-astrologia",
    nota="\"Luna nueva\" y \"Luna llena\" ganan por ser más largas.")
for k, P in PLANETAS:
    add("Planetas", "Planeta", P, [P, f"planeta {P}"], f"planeta-{k}")

# ---------- Retrógrados ----------
for k, P in PLANETAS:
    add("Retrógrados", "Planeta retrógrado", f"{P} retrógrado",
        [f"{P} retrógrado", f"{P} retrógrada", f"{P} en retrógrado", f"{P} retrogrado",
         f"retrogradación de {P}", f"retrógrado de {P}"], f"{k}-retrogrado")

# ---------- Lunaciones y eclipses ----------
add("Conceptos", "Lunación", "Luna nueva",
    ["Luna nueva", "luna nueva", "Luna Nueva", "Lunas nuevas", "lunas nuevas"], "luna-nueva")
add("Conceptos", "Lunación", "Luna llena",
    ["Luna llena", "luna llena", "Luna Llena", "Lunas llenas", "lunas llenas"], "luna-llena")
add("Conceptos", "Eclipse", "Eclipses",
    ["eclipses", "Eclipses", "eclipse", "eclipse solar", "eclipse lunar", "eclipse de Sol", "eclipse de Luna",
     "eclipses solares", "eclipses lunares"], "eclipses")

# ---------- Fechas -> nacidos el (futuros) ----------
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
for mi, M in enumerate(MESES):
    for d in range(1, DIAS_MES[mi] + 1):
        formas = []
        for mes in (M, M.capitalize()):
            formas += [f"{d} de {mes}", f"nacidos el {d} de {mes}", f"nacido el {d} de {mes}",
                       f"nacida el {d} de {mes}", f"quien nace el {d} de {mes}", f"Nacidos el {d} de {mes}"]
        add("Fechas", "Nacidos el", f"Nacidos el {d} de {M}", formas, f"nacidos-el-{d}-de-{M}",
            nota="Futuro. El título y la meta description dicen el signo (\"de qué signo es\").")

# ---------- Horóscopo del amor 2027 ----------
A = "Amor 2027"
add("Horóscopo del amor 2027", "Pilar", "Horóscopo del amor 2027",
    ["Horóscopo del amor 2027", "horóscopo del amor 2027", "horóscopo del amor para 2027",
     "horóscopo del amor de 2027", "Horóscopo del Amor 2027"], "horoscopo-amor-2027", A, "En curso")
for k, S, _ in SIGNOS:
    add("Horóscopo del amor 2027", "Amor del signo", f"Horóscopo del amor {S} 2027",
        [f"Horóscopo del amor {S} 2027", f"horóscopo del amor {S} 2027", f"horóscopo del amor de {S} 2027",
         f"Horóscopo del amor de {S} 2027", f"horóscopo del amor de {S} para 2027",
         f"horóscopo del amor para {S} en 2027"], f"horoscopo-amor-{k}-2027", A, "En curso")

# ---------- Ascendentes (20/11/2026, futuros) ----------
# Pilar general (se publica con la serie de los planetas, categoría Astrología):
add("Ascendentes", "Pilar general", "¿Qué es el ascendente?",
    ["qué es el ascendente", "Qué es el ascendente", "el ascendente", "El ascendente", "signo ascendente",
     "Signo ascendente", "tu ascendente", "Tu ascendente"], "que-es-el-ascendente",
    nota="Sin \"ascendente\" suelto. Futuro: se publica junto con los planetas.")
for k, S, _ in SIGNOS:
    # Pilar por signo solar, en la categoría del signo; cuelga de signo-{signo}.
    add("Ascendentes", "Pilar del signo", f"{S} y sus ascendentes",
        [f"{S} y sus ascendentes", f"ascendentes de {S}", f"los ascendentes de {S}", f"Los ascendentes de {S}"],
        f"{k}-y-sus-ascendentes", S)
    for k2, A, _ in SIGNOS:
        add("Ascendentes", "Combinación", f"{S} ascendente {A}",
            [f"{S} ascendente {A}", f"{S} Ascendente {A}", f"{S} ascendente en {A}", f"{S} con ascendente {A}",
             f"{S} con ascendente en {A}", f"Sol en {S} y ascendente en {A}", f"Sol en {S} con ascendente en {A}"],
            f"{k}-ascendente-{k2}", S)

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
ws.append(["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
           "Slug fijo", "Categoría", "Estado", "ID", "Notas"])
slugs, formas_vistas = set(), {}
for gr, fa, en, fo, sl, ca, es, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    for f in fo.split(" | "):
        assert formas_vistas.setdefault(f, sl) == sl, (f, sl, formas_vistas[f])
    ws.append([gr, fa, en, fo, sl, ca, es, "", no])
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
