"""Genera el mapa de entidades (enlaces iluminados) de horoscopoalfa.com como .xlsx."""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation

# Posts que ya existen en el sitio (slug -> (estado, id)), leídos por el conector el 07/11/2026
EXISTENTES = json.load(open("existentes.json"))
ESTADO_TXT = {"publish": "Publicado", "future": "Programado", "draft": "Borrador"}

SIGNOS = [  # clave, nombre, gentilicio (masc. sing.), elemento
    ("aries", "Aries", "ariano"), ("tauro", "Tauro", "taurino"), ("geminis", "Géminis", "geminiano"),
    ("cancer", "Cáncer", "canceriano"), ("leo", "Leo", "leonino"), ("virgo", "Virgo", "virginiano"),
    ("libra", "Libra", "libriano"), ("escorpio", "Escorpio", "escorpiano"),
    ("sagitario", "Sagitario", "sagitariano"), ("capricornio", "Capricornio", "capricorniano"),
    ("acuario", "Acuario", "acuariano"), ("piscis", "Piscis", "pisciano"),
]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

filas = []  # (grupo, familia, entidad, formas, slug, categoria, nota)


def add(grupo, familia, entidad, formas, slug, categoria, nota=""):
    filas.append((grupo, familia, entidad, " | ".join(formas), slug, categoria, nota))


def g_formas(g):
    return [g, g[:-1] + "a", g + "s", g[:-1] + "as"]


# ---------- Signos: 9 familias x 12 ----------
for k, S, g in SIGNOS:
    nota_ambig = {"Leo": "Solo con mayúscula (\"leo\" es verbo).",
                  "Cáncer": "Solo con mayúscula (\"cáncer\" es la enfermedad).",
                  "Libra": "Solo con mayúscula (\"libra\" es moneda/peso).",
                  "Leonino": ""}.get(S, "")
    add("Signos", "Pilar del signo", f"Signo {S}",
        [S, f"signo {S}", f"signo de {S}"] + g_formas(g), f"signo-{k}", S, nota_ambig)
    add("Signos", "En el amor", f"{S} en el amor",
        [f"{S} en el amor", f"{S} enamorado", f"{S} enamorada"], f"{k}-en-el-amor", S)
    add("Signos", "Mujer", f"La mujer {S}",
        [f"mujer {S}", f"mujer de {S}", f"mujeres {S}", f"mujeres de {S}"], f"mujer-{k}", S)
    add("Signos", "Hombre", f"El hombre {S}",
        [f"hombre {S}", f"hombre de {S}", f"hombres {S}", f"hombres de {S}"], f"hombre-{k}", S)
    add("Signos", "Niño", f"El niño {S}",
        [f"niño {S}", f"niña {S}", f"niños {S}", f"niño de {S}", f"niña de {S}", f"niños de {S}"],
        f"nino-{k}", S)
    add("Signos", "En el trabajo", f"{S} en el trabajo y la profesión",
        [f"{S} en el trabajo", f"{S} en la profesión", f"{S} y la profesión", f"profesiones para {S}"],
        f"{k}-en-el-trabajo", S)
    add("Signos", "En la amistad", f"{S} en la amistad",
        [f"{S} en la amistad", f"{S} como amigo", f"{S} como amiga"], f"{k}-en-la-amistad", S)
    add("Signos", "Compatibilidad general", f"Compatibilidad de {S}",
        [f"compatibilidad de {S}", f"compatibilidad con {S}", f"{S} y los demás signos"],
        f"compatibilidad-{k}", S)
    # Ascendentes: pilar por signo + 12 combinaciones
    add("Ascendentes", "Pilar de ascendentes del signo", f"{S} y sus ascendentes",
        [f"{S} y sus ascendentes", f"ascendentes de {S}", f"{S} según el ascendente"],
        f"{k}-y-sus-ascendentes", S)
    for k2, A, _ in SIGNOS:
        add("Ascendentes", "Signo + ascendente", f"{S} ascendente {A}",
            [f"{S} ascendente {A}", f"{S} con ascendente {A}", f"{S} con ascendente en {A}"],
            f"{k}-ascendente-{k2}", S)
    add("Ascendentes", "Ascendente en el signo", f"Ascendente en {S}",
        [f"ascendente en {S}", f"ascendente {S}", f"Ascendente {S}"], f"ascendente-en-{k}", S,
        "A CONFIRMAR: ascendente en el signo para cualquier signo solar. Si no va a haber post, "
        "estas formas se redirigen a la pilar del signo o al concepto.")

# Parejas de compatibilidad: 78, orden zodiacal en el slug
for i, (ka, A, _) in enumerate(SIGNOS):
    for kb, B, _ in SIGNOS[i:]:
        formas = [f"compatibilidad entre {A} y {B}", f"compatibilidad de {A} y {B}",
                  f"compatibilidad de {A} con {B}", f"{A} y {B} en el amor",
                  f"pareja de {A} y {B}", f"{A} y {B} son compatibles"]
        if A != B:
            formas += [f"compatibilidad entre {B} y {A}", f"compatibilidad de {B} y {A}",
                       f"compatibilidad de {B} con {A}", f"{B} y {A} en el amor",
                       f"pareja de {B} y {A}", f"{B} y {A} son compatibles"]
        add("Compatibilidad", "Pareja de signos", f"Compatibilidad {A} y {B}", formas,
            f"compatibilidad-{ka}-y-{kb}", "Compatibilidad",
            "\"A y B\" a secas NO se marca: en los horóscopos aparecen listas de signos que no hablan de pareja.")

add("Signos", "Pilar general", "Los signos del zodiaco",
    ["signos del zodiaco", "signos del zodíaco", "los 12 signos", "los doce signos", "zodiaco", "zodíaco"],
    "signos-del-zodiaco", "Astrología")

# ---------- Planetas y puntos ----------
A = "Astrología"
add("Planetas", "Pilar", "Los planetas en astrología",
    ["planetas en astrología", "planetas astrológicos", "los planetas"], "planetas-en-astrologia", A)
add("Planetas", "Luminar", "El Sol en astrología", ["el Sol", "Sol natal"], "el-sol-en-astrologia", A,
    "Solo con mayúscula.")
add("Planetas", "Luminar", "La Luna en astrología", ["la Luna"], "la-luna-en-astrologia", A,
    "Solo con mayúscula. \"Luna llena\"/\"Luna nueva\" ganan por ser más largas.")
PLANETAS = [("mercurio", "Mercurio"), ("venus", "Venus"), ("marte", "Marte"), ("jupiter", "Júpiter"),
            ("saturno", "Saturno"), ("urano", "Urano"), ("neptuno", "Neptuno"), ("pluton", "Plutón")]
for k, P in PLANETAS:
    add("Planetas", "Planeta", P, [P, f"planeta {P}"], f"planeta-{k}", A)
for k, P, f in [("nodo-norte", "Nodo Norte", ["Nodo Norte", "nodo norte", "Nodo Lunar Norte"]),
                ("nodo-sur", "Nodo Sur", ["Nodo Sur", "nodo sur", "Nodo Lunar Sur"]),
                ("quiron", "Quirón", ["Quirón"]),
                ("lilith", "Lilith", ["Lilith", "Luna Negra"])]:
    add("Planetas", "Punto", P, f, k, A)
add("Planetas", "Concepto", "Planeta regente", ["planeta regente", "planetas regentes", "regente"],
    "planeta-regente", A)
add("Planetas", "Concepto", "Dignidades planetarias",
    ["dignidades planetarias", "en domicilio", "en exaltación", "en exilio"], "dignidades-planetarias", A,
    "\"en caída\" no se marca (frase común).")
add("Retrógrados", "Pilar", "Planetas retrógrados",
    ["planetas retrógrados", "retrogradación", "retrogradaciones", "retrógrado", "retrógrada"],
    "planetas-retrogrados", A)
for k, P in PLANETAS:
    add("Retrógrados", "Planeta retrógrado", f"{P} retrógrado",
        [f"{P} retrógrado", f"{P} retrógrada", f"{P} en retrogradación", f"retrogradación de {P}"],
        f"{k}-retrogrado", A)

# ---------- Casas ----------
add("Casas", "Pilar", "Las casas astrológicas",
    ["casas astrológicas", "casa astrológica", "casas del zodiaco", "las doce casas", "las 12 casas"],
    "casas-astrologicas", A)
ROM = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
ORD = [["primera"], ["segunda"], ["tercera"], ["cuarta"], ["quinta"], ["sexta"], ["séptima"], ["octava"],
       ["novena"], ["décima"], ["undécima", "onceava"], ["duodécima", "doceava"]]
APODOS = [
    ["casa del yo", "casa de la personalidad", "casa de la identidad"],
    ["casa del dinero", "casa de los recursos", "casa de las posesiones"],
    ["casa de la comunicación", "casa de los hermanos"],
    ["casa del hogar", "casa de la familia", "casa de las raíces"],
    ["casa del placer", "casa de la creatividad", "casa de los hijos", "casa del romance"],
    ["casa de la salud", "casa del trabajo diario", "casa de la rutina"],
    ["casa de la pareja", "casa del matrimonio", "casa de las asociaciones"],
    ["casa de la transformación", "casa de la sexualidad", "casa de los recursos compartidos"],
    ["casa de los viajes", "casa de la filosofía", "casa de los estudios superiores"],
    ["casa de la profesión", "casa de la carrera", "casa de la vocación", "casa del estatus"],
    ["casa de la amistad", "casa de los amigos", "casa de los proyectos"],
    ["casa del inconsciente", "casa del karma", "casa de lo oculto"],
]
for n in range(1, 13):
    formas = [f"casa {n}", f"Casa {n}", f"casa {ROM[n-1]}", f"Casa {ROM[n-1]}"]
    formas += [f"{o} casa" for o in ORD[n-1]] + APODOS[n-1]
    add("Casas", "Casa", f"Casa {n}", formas, f"casa-{n}", A)

# ---------- Aspectos ----------
add("Aspectos", "Pilar", "Aspectos astrológicos",
    ["aspectos astrológicos", "aspectos planetarios", "aspecto astrológico"], "aspectos-astrologicos", A)
for k, nom, f, nota in [
    ("conjuncion", "Conjunción", ["conjunción", "en conjunción", "conjunciones"], ""),
    ("oposicion", "Oposición", ["aspecto de oposición", "en oposición a", "oposición entre"],
     "\"oposición\" sola NO se marca (frase común)."),
    ("trigono", "Trígono", ["trígono", "trígonos", "en trígono"], ""),
    ("cuadratura", "Cuadratura", ["cuadratura", "cuadraturas", "en cuadratura"], ""),
    ("sextil", "Sextil", ["sextil", "sextiles", "en sextil"], ""),
    ("quincuncio", "Quincuncio", ["quincuncio", "en quincuncio"], ""),
]:
    add("Aspectos", "Aspecto", nom, f, k, A, nota)

# ---------- Elementos y modalidades ----------
add("Elementos", "Pilar", "Los elementos del zodiaco",
    ["elementos del zodiaco", "elementos del zodíaco", "los cuatro elementos", "los 4 elementos"],
    "elementos-del-zodiaco", A)
for k, E in [("fuego", "fuego"), ("tierra", "tierra"), ("aire", "aire"), ("agua", "agua")]:
    add("Elementos", "Elemento", f"Signos de {E}",
        [f"signos de {E}", f"signo de {E}", f"elemento {E}"],
        f"signos-de-{k}", A, f"\"{E}\" sola NO se marca. \"elemento {E.capitalize()}\" con mayúscula es del horóscopo chino.")
add("Modalidades", "Pilar", "Modalidades del zodiaco",
    ["modalidades del zodiaco", "modalidades astrológicas", "las tres modalidades"],
    "modalidades-del-zodiaco", A)
for k, sing, plur in [("cardinales", "cardinal", "cardinales"), ("fijos", "fijo", "fijos"),
                      ("mutables", "mutable", "mutables")]:
    add("Modalidades", "Modalidad", f"Signos {plur}",
        [f"signos {plur}", f"signo {sing}", f"modalidad {sing}" if sing != "fijo" else "modalidad fija"],
        f"signos-{k}", A)
add("Modalidades", "Concepto", "Signos opuestos", ["signos opuestos", "signo opuesto"], "signos-opuestos", A)

# ---------- Conceptos ----------
for k, nom, f, nota in [
    ("carta-natal", "Carta natal", ["carta natal", "carta astral", "mapa astral", "mapa natal"], ""),
    ("que-es-el-ascendente", "Qué es el ascendente", ["ascendente", "signo ascendente", "tu ascendente"],
     "Las formas con signo (\"ascendente en Aries\", \"Capricornio ascendente Aries\") ganan por ser más largas."),
    ("como-calcular-el-ascendente", "Cómo calcular el ascendente",
     ["calcular el ascendente", "calcular tu ascendente", "calcula tu ascendente"], ""),
    ("descendente", "Descendente", ["descendente", "signo descendente"], ""),
    ("medio-cielo", "Medio Cielo", ["Medio Cielo", "medio cielo"], ""),
    ("fondo-del-cielo", "Fondo del Cielo", ["Fondo del Cielo", "fondo del cielo", "Imum Coeli"], ""),
    ("signo-solar", "Signo solar", ["signo solar"], ""),
    ("signo-lunar", "Signo lunar", ["signo lunar", "Luna natal"], ""),
    ("decanatos", "Decanatos", ["decanato", "decanatos"], ""),
    ("cuspide-astrologica", "Cúspide", ["cúspide", "nacidos en la cúspide", "nacidos en cúspide"], ""),
    ("transitos-planetarios", "Tránsitos planetarios", ["tránsitos planetarios", "tránsito", "tránsitos"], ""),
    ("fases-lunares", "Fases lunares", ["fases lunares", "fase lunar", "fases de la Luna"], ""),
    ("luna-nueva", "Luna nueva", ["Luna nueva", "luna nueva", "Lunas nuevas", "lunas nuevas"], ""),
    ("luna-llena", "Luna llena", ["Luna llena", "luna llena", "Lunas llenas", "lunas llenas"], ""),
    ("luna-vacia-de-curso", "Luna vacía de curso", ["Luna vacía de curso", "luna vacía de curso"], ""),
    ("eclipses", "Eclipses", ["eclipse", "eclipses"], ""),
    ("eclipse-solar", "Eclipse solar", ["eclipse solar", "eclipses solares", "eclipse de Sol"], ""),
    ("eclipse-lunar", "Eclipse lunar", ["eclipse lunar", "eclipses lunares", "eclipse de Luna"], ""),
    ("revolucion-solar", "Revolución solar", ["revolución solar"], ""),
    ("retorno-de-saturno", "Retorno de Saturno", ["retorno de Saturno", "regreso de Saturno"], ""),
    ("sinastria", "Sinastría", ["sinastría"], ""),
    ("carta-compuesta", "Carta compuesta", ["carta compuesta"], ""),
]:
    add("Conceptos", "Concepto", nom, f, k, A, nota)

# ---------- Horóscopo chino ----------
ANIMALES = [("rata", "Rata", "la"), ("buey", "Buey", "el"), ("tigre", "Tigre", "el"), ("conejo", "Conejo", "el"),
            ("dragon", "Dragón", "el"), ("serpiente", "Serpiente", "la"), ("caballo", "Caballo", "el"),
            ("cabra", "Cabra", "la"), ("mono", "Mono", "el"), ("gallo", "Gallo", "el"), ("perro", "Perro", "el"),
            ("cerdo", "Cerdo", "el")]
C = "Horóscopo chino"
add("Horóscopo chino", "Pilar", "Qué es el horóscopo chino",
    ["horóscopo chino", "zodiaco chino", "zodíaco chino", "los 12 animales"], "que-es-el-horoscopo-chino", C)
for k, An, art in ANIMALES:
    de = "de la" if art == "la" else "del"
    add("Horóscopo chino", "Signo chino", f"Signo chino {An}",
        [f"signo {de} {An}", f"año {de} {An}", f"nativos {de} {An}", f"nacidos en el año {de} {An}"],
        f"signo-chino-{k}", C, "Solo con mayúscula.")
for k, E in [("madera", "Madera"), ("fuego", "Fuego"), ("tierra", "Tierra"), ("metal", "Metal"), ("agua", "Agua")]:
    add("Horóscopo chino", "Elemento chino", f"Elemento {E} (horóscopo chino)",
        [f"elemento {E}", f"elemento chino {E}"], f"elemento-{k}-horoscopo-chino", C,
        "Choca con \"elemento Fuego\" occidental: marcar solo en textos de horóscopo chino.")
add("Horóscopo chino", "2027", "Horóscopo chino 2027",
    ["horóscopo chino 2027", "año de la Cabra de Fuego"], "horoscopo-chino-2027", C)
for k, An, art in ANIMALES:
    add("Horóscopo chino", "2027 por animal", f"Horóscopo chino 2027 para {art} {An}",
        [f"horóscopo chino 2027 para {art} {An}", f"{An} en 2027", f"{art} {An} en 2027"],
        f"horoscopo-chino-2027-{k}", C)

# ---------- Horóscopo 2027 ----------
H = "Horóscopo 2027"
add("Horóscopo 2027", "Superpilar", "Predicciones y horóscopo 2027",
    ["horóscopo 2027", "Horóscopo 2027", "predicciones 2027", "predicciones para 2027"],
    "predicciones-horoscopo-2027", H)
add("Horóscopo 2027", "Pilar amor", "Horóscopo del amor 2027",
    ["horóscopo del amor 2027", "Horóscopo del amor 2027", "amor en 2027"], "horoscopo-amor-2027", H)
for k, S, _ in SIGNOS:
    add("Horóscopo 2027", "Anual por signo", f"Horóscopo {S} 2027",
        [f"horóscopo de {S} 2027", f"Horóscopo {S} 2027", f"horóscopo {S} 2027", f"{S} en 2027"],
        f"horoscopo-{k}-2027", H)
    add("Horóscopo 2027", "Amor por signo", f"Horóscopo del amor {S} 2027",
        [f"horóscopo del amor {S} 2027", f"Horóscopo del amor {S} 2027", f"amor de {S} en 2027"],
        f"horoscopo-amor-{k}-2027", H)
for m in MESES:
    add("Horóscopo 2027", "Mes", f"Horóscopo {m} 2027",
        [f"horóscopo de {m} 2027", f"horóscopo de {m} de 2027", f"Horóscopo {m} 2027"],
        f"horoscopo-{m}-2027", H, "Rangos de fechas (\"enero de 2027\") NO se marcan.")
for k, S, _ in SIGNOS:
    for m in MESES:
        add("Horóscopo 2027", "Signo por mes", f"Horóscopo {S} {m} 2027",
            [f"horóscopo de {S} de {m} 2027", f"horóscopo de {S} de {m} de 2027", f"Horóscopo {S} {m} 2027",
             f"{S} en {m} de 2027"], f"horoscopo-{k}-{m}-2027", H)

# ---------- Fechas de nacimiento ----------
LIM = [  # (mes, día desde el que empieza el signo, signo que empieza)
    (1, 20, "Acuario"), (2, 19, "Piscis"), (3, 21, "Aries"), (4, 20, "Tauro"), (5, 21, "Géminis"),
    (6, 21, "Cáncer"), (7, 23, "Leo"), (8, 23, "Virgo"), (9, 23, "Libra"), (10, 23, "Escorpio"),
    (11, 22, "Sagitario"), (12, 22, "Capricornio")]


def signo_fecha(mes, dia):
    ini_mes, ini_dia, S = LIM[mes - 1]
    if dia >= ini_dia:
        return S
    return LIM[mes - 2][2]


for mi, m in enumerate(MESES, 1):
    for d in range(1, DIAS_MES[mi - 1] + 1):
        S = signo_fecha(mi, d)
        cusp = abs(d - LIM[mi - 1][1]) <= 1
        add("Fecha de nacimiento", "Nacidos el", f"Signo {S} nacidos el {d} de {m}", [f"{d} de {m}"],
            f"signo-nacidos-el-{d}-de-{m}", "Fecha de nacimiento",
            "Cúspide: confirmar el signo al escribir." if cusp else "")

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
cols = ["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
        "Slug fijo", "Categoría", "Estado", "ID", "Notas"]
ws.append(cols)
slugs = set()
for gr, fa, en, fo, sl, ca, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    st, pid = EXISTENTES.get(sl, (None, None))
    ws.append([gr, fa, en, fo, sl, ca, ESTADO_TXT.get(st, "Pendiente"), pid, no])

F = "Arial"
hdr_fill = PatternFill("solid", start_color="1F3A5F")
for c in ws[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = hdr_fill
    c.alignment = Alignment(vertical="center", wrap_text=True)
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, size=10)
        c.alignment = Alignment(vertical="top", wrap_text=c.column in (4, 9))
for col, w in zip("ABCDEFGHI", [16, 22, 38, 70, 38, 18, 12, 8, 50]):
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

# Resumen con fórmulas
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

# Reglas
rg = wb.create_sheet("Reglas")
reglas = [
    "Cómo se usa este mapa",
    "Cada fila es un post (existente o futuro). Al escribir cualquier post, el script busca en el HTML las 'Formas que se marcan' y las envuelve en [enlace_iluminado slug=\"...\"]…[/enlace_iluminado]. Mientras el post no existe se ve solo el texto; al publicarse, Enlaces iluminados escribe el enlace solo.",
    "El slug es un compromiso: cuando se escriba ese post, tiene que llevar EXACTAMENTE ese slug.",
    "",
    "Reglas del marcado",
    "1. Gana la forma más larga: si se superponen \"la Luna\" y \"Luna llena\", o \"Capricornio\" y \"mujer Capricornio\", se marca la más larga.",
    "2. Solo la primera aparición de cada slug en cada post.",
    "3. Un post nunca se enlaza a sí mismo.",
    "4. Nunca dentro de títulos H1-H6, del JSON-LD (<script>), de otro shortcode ni de un <a>.",
    "5. Se distinguen mayúsculas: las formas con mayúscula (Leo, Cáncer, Libra, el Sol, la Luna, animales chinos) solo se marcan así escritas.",
    "6. Tope de marcas por post: 20 (a ajustar).",
    "7. En rangos de fechas (\"1 al 7 de enero\") solo se marca la parte con mes completo.",
    "",
    "Columna Estado",
    "Se completó el 07/11/2026 con los posts que ya hay en el sitio. Al publicar un post nuevo, pasarlo a Publicado.",
    "",
    "Fase 2 (no está en el mapa todavía)",
    "Planeta en signo (120), planeta en casa (120), decanatos por signo (36), compatibilidad del horóscopo chino (78), combinaciones animal + elemento chino (60).",
]
for r in reglas:
    rg.append([r])
for row in rg.iter_rows():
    for c in row:
        bold = c.value in ("Cómo se usa este mapa", "Reglas del marcado", "Columna Estado",
                           "Fase 2 (no está en el mapa todavía)")
        c.font = Font(name=F, bold=bold, size=12 if bold else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
rg.column_dimensions["A"].width = 120

wb.save("mapa-enlaces-iluminados-horoscopoalfa.xlsx")
print(len(filas), "filas;", sum(1 for f_ in filas if f_[4] in EXISTENTES), "ya existen")
