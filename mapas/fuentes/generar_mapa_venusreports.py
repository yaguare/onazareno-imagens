"""Genera el mapa de entidades (enlaces iluminados) de venusreports.com (inglés) como .xlsx.

Basado en generar_mapa.py de horoscopoalfa, con los slugs propios de Venus Reports:
- pilares de signo: {sign}-zodiac-sign (categoría = signo)
- parejas: {a}-and-{b}-compatibility (orden zodiacal; categoría = los dos signos)
- amor anual: {sign}-love-horoscope-2027 y love-horoscope-2027 (categoría Love Horoscope)
"""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation

EXISTENTES = json.load(open("existentes-venusreports.json"))
ESTADO_TXT = {"publish": "Publicado", "future": "Programado", "draft": "Borrador"}
SALIDA = "mapa-enlaces-iluminados-venusreports.xlsx"

SIGNOS = [  # clave, nombre, gentilicios (sing., plural)
    ("aries", "Aries", ["Arian", "Arians"]),
    ("taurus", "Taurus", ["Taurean", "Taureans"]),
    ("gemini", "Gemini", ["Geminis"]),
    ("cancer", "Cancer", ["Cancerian", "Cancerians"]),
    ("leo", "Leo", ["Leos"]),
    ("virgo", "Virgo", ["Virgos", "Virgoan", "Virgoans"]),
    ("libra", "Libra", ["Libras", "Libran", "Librans"]),
    ("scorpio", "Scorpio", ["Scorpios"]),
    ("sagittarius", "Sagittarius", ["Sagittarian", "Sagittarians"]),
    ("capricorn", "Capricorn", ["Capricorns", "Capricornian", "Capricornians"]),
    ("aquarius", "Aquarius", ["Aquarian", "Aquarians"]),
    ("pisces", "Pisces", ["Piscean", "Pisceans"]),
]
MESES = ["January", "February", "March", "April", "May", "June", "July", "August",
         "September", "October", "November", "December"]
DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

filas = []  # (grupo, familia, entidad, formas, slug, categoria, nota)


def add(grupo, familia, entidad, formas, slug, categoria, nota=""):
    filas.append((grupo, familia, entidad, " | ".join(formas), slug, categoria, nota))


def ordinal(d):
    suf = "th" if 11 <= d % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{d}{suf}"


A = "Astrology"

# ---------- Signos ----------
for k, S, gent in SIGNOS:
    add("Signs", "Sign pillar", f"{S} Zodiac Sign",
        [S, f"{S} sign", f"{S} zodiac sign", f"{S} Zodiac Sign", f"sign of {S}"] + gent,
        f"{k}-zodiac-sign", S, "Mayúsculas exactas: \"cancer\" en minúscula (enfermedad) no se marca.")
    add("Signs", "Man", f"The {S} Man",
        [f"{S} man", f"{S} men", f"{S} Man"], f"{k}-man", S,
        "Mientras no exista, el bloque sigue en la pilar del signo.")
    add("Signs", "Woman", f"The {S} Woman",
        [f"{S} woman", f"{S} women", f"{S} Woman"], f"{k}-woman", S,
        "Mientras no exista, el bloque sigue en la pilar del signo.")
    add("Signs", "In love", f"{S} in Love",
        [f"{S} in love", f"{S} in Love", f"{S} lover", f"{S} lovers", f"{S} in relationships"],
        f"{k}-in-love", S, "\"A and B in love\" gana y va a la pareja.")

add("Signs", "General pillar", "The Zodiac Signs",
    ["zodiac signs", "signs of the zodiac", "the 12 signs", "the twelve signs", "zodiac"],
    "zodiac-signs", A)

# Parejas: 78, orden zodiacal en el slug
for i, (ka, Sa, _) in enumerate(SIGNOS):
    for kb, Sb, _ in SIGNOS[i:]:
        formas = []
        pares = [(Sa, Sb)] if Sa == Sb else [(Sa, Sb), (Sb, Sa)]
        for x, y in pares:
            formas += [f"{x} and {y} compatibility", f"{x} and {y} Compatibility",
                       f"compatibility between {x} and {y}", f"{x} and {y} in love",
                       f"{x} and {y} relationship", f"{x} and {y} couple",
                       f"{x} and {y} are compatible", f"{x}-{y} compatibility"]
        if Sa == Sb:
            formas += [f"two {Sa}", f"two {Sa}s" if not Sa.endswith("s") else f"two {Sa} partners"]
        add("Compatibility", "Pair", f"{Sa} and {Sb} Compatibility", formas,
            f"{ka}-and-{kb}-compatibility", f"{Sa}, {Sb}" if Sa != Sb else Sa,
            "\"A and B\" a secas NO se marca (listas de signos).")

# ---------- Amor 2027 ----------
L = "Love Horoscope"
add("Love Horoscope", "Pillar 2027", "Love Horoscope 2027",
    ["love horoscope 2027", "Love Horoscope 2027", "2027 love horoscope", "love horoscope for 2027"],
    "love-horoscope-2027", L)
for k, S, _ in SIGNOS:
    add("Love Horoscope", "Sign 2027", f"{S} Love Horoscope 2027",
        [f"{S} love horoscope 2027", f"{S} Love Horoscope 2027", f"{S} love horoscope for 2027",
         f"{S} love life in 2027", f"2027 {S} love horoscope"],
        f"{k}-love-horoscope-2027", L)

# ---------- Elementos ----------
add("Elements", "Pillar", "The Zodiac Elements",
    ["zodiac elements", "elements of the zodiac", "the four elements", "the 4 elements"],
    "zodiac-elements", A)
for E in ["fire", "earth", "air", "water"]:
    add("Elements", "Element", f"{E.capitalize()} Signs",
        [f"{E} sign", f"{E} signs", f"{E} element", f"{E.capitalize()} signs", f"element of {E}"],
        f"{E}-signs", A, f"\"{E}\" sola NO se marca.")

# ---------- Modalidades ----------
add("Modalities", "Pillar", "The Zodiac Modalities",
    ["modalities", "zodiac modalities", "the three modalities", "qualities of the signs"],
    "zodiac-modalities", A, "Solo en minúscula (la fila \"Modalities\" de la tabla de parejas no se marca).")
for k in ["cardinal", "fixed", "mutable"]:
    add("Modalities", "Modality", f"{k.capitalize()} Signs",
        [f"{k} sign", f"{k} signs", f"{k} modality", f"{k.capitalize()} signs"], f"{k}-signs", A,
        f"\"{k}\" sola NO se marca.")
add("Modalities", "Concept", "Opposite Signs", ["opposite signs", "opposite sign"], "opposite-signs", A)

# ---------- Aspectos ----------
add("Aspects", "Pillar", "Astrological Aspects",
    ["astrological aspects", "aspects in astrology", "planetary aspects", "astrological aspect"],
    "astrological-aspects", A)
for k, nom, f, nota in [
    ("conjunction-aspect", "Conjunction", ["conjunction", "conjunctions", "in conjunction"], ""),
    ("semi-sextile-aspect", "Semi-sextile", ["semi-sextile", "semisextile", "semi-sextiles"],
     "Gana sobre \"sextile\" por ser más larga."),
    ("sextile-aspect", "Sextile", ["sextile", "sextiles", "in sextile"], ""),
    ("square-aspect", "Square", ["square aspect", "a square", "in square", "squares"],
     "\"square\" sola NO se marca (palabra común)."),
    ("trine-aspect", "Trine", ["trine", "trines", "in trine"], ""),
    ("quincunx-aspect", "Quincunx", ["quincunx", "inconjunct"], ""),
    ("opposition-aspect", "Opposition", ["opposition aspect", "an opposition", "in opposition"],
     "\"opposition\" sola NO se marca."),
]:
    add("Aspects", "Aspect", nom, f, k, A, nota)

# ---------- Planetas y puntos ----------
add("Planets", "Pillar", "The Planets in Astrology",
    ["planets in astrology", "astrological planets", "the planets"], "planets-in-astrology", A)
add("Planets", "Luminary", "The Sun in Astrology", ["the Sun", "The Sun"], "the-sun-in-astrology", A,
    "Solo con mayúscula.")
add("Planets", "Luminary", "The Moon in Astrology", ["the Moon", "The Moon"], "the-moon-in-astrology", A,
    "Solo con mayúscula. \"full Moon\"/\"new Moon\"/\"Moon sign\" ganan por ser más largas.")
PLANETAS = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
for P in PLANETAS:
    nota = "\"Venus Reports\" (marca) queda bloqueada por la fila de bloqueo." if P == "Venus" else ""
    add("Planets", "Planet", f"{P} in Astrology", [P, f"planet {P}"], f"{P.lower()}-in-astrology", A, nota)
for k, nom, f in [("north-node", "North Node", ["North Node", "north node", "lunar nodes", "Lunar Nodes"]),
                  ("south-node", "South Node", ["South Node", "south node"]),
                  ("chiron", "Chiron", ["Chiron"]),
                  ("black-moon-lilith", "Black Moon Lilith", ["Black Moon Lilith", "Lilith"])]:
    add("Planets", "Point", nom, f, k, A)
add("Planets", "Concept", "Ruling Planets", ["ruling planet", "ruling planets", "planetary ruler"],
    "ruling-planets", A)
add("Planets", "Concept", "Planetary Dignities",
    ["planetary dignities", "in domicile", "in exaltation", "in detriment"], "planetary-dignities", A,
    "\"in fall\" no se marca (frase común).")
add("Retrogrades", "Pillar", "Retrograde Planets",
    ["retrograde planets", "retrograde", "retrogrades", "retrograde period"], "retrograde-planets", A)
for P in PLANETAS:
    add("Retrogrades", "Planet retrograde", f"{P} Retrograde",
        [f"{P} retrograde", f"{P} Retrograde", f"{P} in retrograde", f"retrograde {P}",
         f"{P} stations retrograde"], f"{P.lower()}-retrograde", A)

# ---------- Casas ----------
add("Houses", "Pillar", "The Astrological Houses",
    ["astrological houses", "houses in astrology", "the twelve houses", "the 12 houses", "astrological house"],
    "astrological-houses", A)
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
       "eleventh", "twelfth"]
APODOS = [
    ["house of self", "house of identity"],
    ["house of money", "house of possessions", "house of values"],
    ["house of communication", "house of siblings"],
    ["house of home", "house of family", "house of roots"],
    ["house of romance", "house of pleasure", "house of creativity", "house of children"],
    ["house of health", "house of daily work", "house of routine"],
    ["house of partnership", "house of partnerships", "house of marriage"],
    ["house of transformation", "house of sex", "house of shared resources", "house of intimacy"],
    ["house of travel", "house of philosophy", "house of higher learning"],
    ["house of career", "house of reputation", "house of public life"],
    ["house of friendship", "house of friends", "house of hopes and wishes"],
    ["house of the unconscious", "house of secrets", "house of karma"],
]
for n in range(1, 13):
    o = ORD[n - 1]
    formas = [f"{o} house", f"{o.capitalize()} House", f"{ordinal(n)} house", f"{ordinal(n)} House",
              f"house {n}", f"House {n}"] + APODOS[n - 1]
    add("Houses", "House", f"The {o.capitalize()} House", formas, f"{o}-house", A)

# ---------- Conceptos ----------
for k, nom, f, nota in [
    ("birth-chart", "Birth Chart", ["birth chart", "birth charts", "natal chart", "natal charts",
                                    "astrological chart", "astrology chart"], ""),
    ("rising-sign", "Rising Sign (Ascendant)", ["rising sign", "rising signs", "ascendant", "Ascendant",
                                                "your rising"], ""),
    ("descendant-sign", "Descendant", ["Descendant", "descendant sign"],
     "\"descendant\" en minúscula NO se marca (palabra común)."),
    ("midheaven", "Midheaven", ["Midheaven", "midheaven", "Medium Coeli"], ""),
    ("imum-coeli", "Imum Coeli", ["Imum Coeli", "imum coeli"], ""),
    ("sun-sign", "Sun Sign", ["sun sign", "Sun sign", "sun signs", "Sun signs"], ""),
    ("moon-sign", "Moon Sign", ["moon sign", "Moon sign", "moon signs", "Moon signs", "natal Moon"], ""),
    ("venus-sign", "Venus Sign", ["Venus sign", "Venus signs", "your Venus"], "Clave en un sitio de amor."),
    ("mars-sign", "Mars Sign", ["Mars sign", "Mars signs", "your Mars"], ""),
    ("decans", "Decans", ["decan", "decans", "decanate", "decanates"], ""),
    ("zodiac-cusp", "Zodiac Cusp", ["cusp", "cusps", "born on the cusp", "cusp sign", "cusp signs"], ""),
    ("planetary-transits", "Planetary Transits", ["planetary transits", "transit", "transits"], ""),
    ("moon-phases", "Moon Phases", ["moon phases", "Moon phases", "phases of the Moon", "lunar phases",
                                    "lunar phase"], ""),
    ("new-moon", "New Moon", ["new moon", "new Moon", "New Moon", "new moons", "new Moons", "New Moons"], ""),
    ("full-moon", "Full Moon", ["full moon", "full Moon", "Full Moon", "full moons", "full Moons",
                                "Full Moons"], ""),
    ("void-of-course-moon", "Void-of-Course Moon", ["void-of-course Moon", "void of course Moon",
                                                    "Moon void of course", "void-of-course"], ""),
    ("eclipses", "Eclipses", ["eclipse", "eclipses", "eclipse season"], ""),
    ("solar-eclipse", "Solar Eclipse", ["solar eclipse", "solar eclipses", "Solar Eclipse"], ""),
    ("lunar-eclipse", "Lunar Eclipse", ["lunar eclipse", "lunar eclipses", "Lunar Eclipse"], ""),
    ("solar-return", "Solar Return", ["solar return", "Solar Return"], ""),
    ("saturn-return", "Saturn Return", ["Saturn return", "Saturn Return", "return of Saturn"], ""),
    ("synastry", "Synastry", ["synastry", "Synastry", "synastry chart"], ""),
    ("composite-chart", "Composite Chart", ["composite chart", "composite charts"], ""),
]:
    add("Concepts", "Concept", nom, f, k, A, nota)

# Bloqueo: "Venus Reports" (la marca) no debe marcarse como el planeta Venus.
# Gana por ser más larga y apunta a un slug que NUNCA se publica: el lector ve solo el texto.
add("Site", "Bloqueo", "Venus Reports (marca, no es el planeta)", ["Venus Reports"], "ei-bloqueo-venus-reports", A,
    "BLOQUEO: no crear nunca un post con este slug. Solo impide que \"Venus\" de la marca enlace al planeta.")

# ---------- Fechas de nacimiento ----------
LIM = [(1, 20, "Aquarius"), (2, 19, "Pisces"), (3, 21, "Aries"), (4, 20, "Taurus"), (5, 21, "Gemini"),
       (6, 21, "Cancer"), (7, 23, "Leo"), (8, 23, "Virgo"), (9, 23, "Libra"), (10, 23, "Scorpio"),
       (11, 22, "Sagittarius"), (12, 22, "Capricorn")]


def signo_fecha(mes, dia):
    _, ini_dia, S = LIM[mes - 1]
    return S if dia >= ini_dia else LIM[mes - 2][2]


for mi, M in enumerate(MESES, 1):
    for d in range(1, DIAS_MES[mi - 1] + 1):
        S = signo_fecha(mi, d)
        cusp = abs(d - LIM[mi - 1][1]) <= 1
        add("Birthdays", "Born on", f"{M} {d} Zodiac Sign ({S})",
            [f"born on {M} {d}", f"born on {M} {ordinal(d)}", f"born {M} {d}", f"Born on {M} {d}",
             f"{M} {d} birthday", f"{M} {d} birthdays", f"{M} {ordinal(d)} birthday",
             f"birthday on {M} {d}", f"birthday is {M} {d}",
             f"{M} {d} zodiac sign", f"{M} {d} Zodiac Sign", f"{M} {d} zodiac", f"{M} {d} sign"],
            f"{M.lower()}-{d}-zodiac-sign", "Birthday",
            "Cúspide: confirmar el signo al escribir." if cusp else "")

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
cols = ["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
        "Slug fijo", "Categoría", "Estado", "ID", "Notas"]
ws.append(cols)
slugs, formas_vistas = set(), {}
for gr, fa, en, fo, sl, ca, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    for f in fo.split(" | "):
        assert formas_vistas.setdefault(f, sl) == sl, (f, sl, formas_vistas[f])
    st, pid = EXISTENTES.get(sl, (None, None))
    ws.append([gr, fa, en, fo, sl, ca, ESTADO_TXT.get(st, "Pendiente"), pid, no])
faltan = set(EXISTENTES) - slugs
assert not faltan, faltan

F = "Arial"
hdr_fill = PatternFill("solid", start_color="7A1F4B")
for c in ws[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = hdr_fill
    c.alignment = Alignment(vertical="center", wrap_text=True)
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, size=10)
        c.alignment = Alignment(vertical="top", wrap_text=c.column in (4, 9))
for col, w in zip("ABCDEFGHI", [16, 20, 38, 70, 38, 20, 12, 8, 50]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:I{ws.max_row}"
n = ws.max_row
ws.conditional_formatting.add(f"G2:G{n}", CellIsRule(operator="equal", formula=['"Publicado"'],
                              fill=PatternFill("solid", start_color="D9EAD3")))
ws.conditional_formatting.add(f"G2:G{n}", CellIsRule(operator="equal", formula=['"Programado"'],
                              fill=PatternFill("solid", start_color="FFF2CC")))
dv = DataValidation(type="list", formula1='"Pendiente,Borrador,Programado,Publicado,Descartado"')
ws.add_data_validation(dv)
dv.add(f"G2:G{n}")

rs = wb.create_sheet("Resumen")
rs.append(["Grupo", "Posts en el mapa", "Publicados", "Programados", "Pendientes"])
grupos = []
for f_ in filas:
    if f_[0] not in grupos:
        grupos.append(f_[0])
for i, gname in enumerate(grupos, 2):
    rs.append([gname,
               f'=COUNTIF(Mapa!$A$2:$A${n},A{i})',
               f'=COUNTIFS(Mapa!$A$2:$A${n},A{i},Mapa!$G$2:$G${n},"Publicado")',
               f'=COUNTIFS(Mapa!$A$2:$A${n},A{i},Mapa!$G$2:$G${n},"Programado")',
               f'=COUNTIFS(Mapa!$A$2:$A${n},A{i},Mapa!$G$2:$G${n},"Pendiente")'])
t = len(grupos) + 2
rs.append(["Total", f"=SUM(B2:B{t-1})", f"=SUM(C2:C{t-1})", f"=SUM(D2:D{t-1})", f"=SUM(E2:E{t-1})"])
for c in rs[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = hdr_fill
for row in rs.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, bold=(c.row == t))
rs.column_dimensions["A"].width = 22
for col in "BCDE":
    rs.column_dimensions[col].width = 16

rg = wb.create_sheet("Reglas")
reglas = [
    "Cómo se usa este mapa",
    "Cada fila es un post (existente o futuro) de venusreports.com. El plugin busca las 'Formas que se marcan' y las envuelve en [enlace_iluminado slug=\"...\"]; al publicarse el destino, escribe el enlace solo.",
    "El slug es un compromiso: cuando se escriba ese post, tiene que llevar EXACTAMENTE ese slug.",
    "",
    "Reglas del marcado",
    "1. Gana la forma más larga (\"Aries and Leo compatibility\" gana sobre \"Aries\"; \"Venus sign\" sobre \"Venus\").",
    "2. Solo la primera aparición de cada slug en cada post; un destino = un texto ancla.",
    "3. Un post nunca se enlaza a sí mismo.",
    "4. Nunca en H1-H6, JSON-LD (<script>), shortcodes ni dentro de un <a>.",
    "5. Mayúsculas exactas (Cancer, Leo, the Sun, the Moon, Descendant).",
    "6. Tope: 30 marcas por post, contando las que ya tenía.",
    "7. Fechas (decisión 07/11/2026): solo con contexto de cumpleaños (\"born on March 21\", \"March 21 birthday\", \"March 21 zodiac sign\"). Una fecha suelta (tránsitos de los horóscopos) NO se marca.",
    "",
    "Columna Estado",
    "Completada el 07/11/2026 con los 76 posts publicados.",
]
for r in reglas:
    rg.append([r])
for row in rg.iter_rows():
    for c in row:
        bold = c.value in ("Cómo se usa este mapa", "Reglas del marcado", "Columna Estado")
        c.font = Font(name=F, bold=bold, size=12 if bold else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
rg.column_dimensions["A"].width = 120

wb.save(SALIDA)
print(len(filas), "filas;", sum(1 for f_ in filas if f_[4] in EXISTENTES), "ya existen;",
      sum(len(f_[3].split(" | ")) for f_ in filas), "formas")
