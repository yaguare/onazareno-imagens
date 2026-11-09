"""Genera el mapa de entidades (Enlaces iluminados) de orbelis.com.br (portugués de Brasil) como .xlsx.

Uso: python3 generar_mapa_orbelis.py   (lee existentes-orbelis.json: {slug: [estado, id]})

Familias existentes (slugs reales del sitio, con sus excepciones):
- pilar de signo: {signo} (Virgem: signo-virgem)
- nascidos em: signo-{signo}-nascidos-em-{N}-de-{mes} (21 de Libra con "nascidos-en"; 1 de julho = ID 19571)
- compatibilidade-{a}-e-{b} en los dos órdenes (excepciones: capricornio-e-gemini, cancer-e-touro)
- o-homem-de-{signo}, a-mulher[-de]-{signo}, {signo}-e-o-amor, a-personalidade-de-{signo}
- horóscopos 2027: horoscopo-{signo}-2027, horoscopo-{signo}-{mes}-2027, horoscopo-{mes}-2027,
  horoscopo-do-amor-{signo}-2027, horoscopo-2027, horoscopo-do-amor-2027
Familias futuras (slug fijo = compromiso): planetas, casas, aspectos, modalidades, conceptos.
"""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation

EXISTENTES = json.load(open("existentes-orbelis.json"))
ESTADO_TXT = {"publish": "Publicado", "future": "Programado", "draft": "Borrador"}
SALIDA = "mapa-enlaces-iluminados-orbelis.xlsx"

SIGNOS = [  # clave, nombre, gentilicios
    ("aries", "Áries", ["ariano", "arianos", "ariana", "arianas"]),
    ("touro", "Touro", ["taurino", "taurinos", "taurina", "taurinas"]),
    ("gemeos", "Gêmeos", ["geminiano", "geminianos", "geminiana", "geminianas"]),
    ("cancer", "Câncer", ["canceriano", "cancerianos", "canceriana", "cancerianas"]),
    ("leao", "Leão", ["leonino", "leoninos", "leonina", "leoninas"]),
    ("virgem", "Virgem", ["virginiano", "virginianos", "virginiana", "virginianas"]),
    ("libra", "Libra", ["libriano", "librianos", "libriana", "librianas"]),
    ("escorpiao", "Escorpião", ["escorpiano", "escorpianos", "escorpiana", "escorpianas",
                                "escorpiniano", "escorpinianos"]),
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
ANO = 2027

filas = []  # (grupo, familia, entidad, formas, slug, categoria, nota)


def add(grupo, familia, entidad, formas, slug, categoria, nota=""):
    vistas = []
    for f in formas:
        if f not in vistas:
            vistas.append(f)
    filas.append((grupo, familia, entidad, " | ".join(vistas), slug, categoria, nota))


def existente(*candidatos):
    for c in candidatos:
        if c in EXISTENTES:
            return c
    raise SystemExit(f"No existe ninguno de {candidatos}")


def cap(s):
    return s[0].upper() + s[1:]


A = "Astrologia"

# ---------- Signos (existentes) ----------
for k, S, gent in SIGNOS:
    add("Signos", "Pilar do signo", f"Signo {S}",
        [S, f"signo de {S}", f"Signo de {S}", f"signo {S}", f"Signo {S}", f"signo do {S}"] + gent,
        existente(k, f"signo-{k}"), S,
        "Mayúsculas exactas: \"câncer\", \"touro\", \"peixes\", \"libra\" en minúscula no se marcan.")
    add("Signos", "Personalidade", f"A personalidade de {S}",
        [f"personalidade de {S}", f"personalidade do signo de {S}", f"personalidade {gent[0]}",
         f"personalidade {gent[2]}"], existente(f"a-personalidade-de-{k}"), S)
    add("Signos", "Homem", f"O homem de {S}",
        [f"homem de {S}", f"homens de {S}", f"Homem de {S}", f"homem {gent[0]}", f"homens {gent[1]}"],
        existente(f"o-homem-de-{k}"), S)
    add("Signos", "Mulher", f"A mulher de {S}",
        [f"mulher de {S}", f"mulheres de {S}", f"Mulher de {S}", f"mulher {S}", f"mulher {gent[2]}",
         f"mulheres {gent[3]}"], existente(f"a-mulher-de-{k}", f"a-mulher-{k}"), S)
    add("Signos", "Amor", f"{S} e o Amor",
        [f"{S} no amor", f"{S} e o amor", f"{S} e o Amor", f"{S} nos relacionamentos"],
        existente(f"{k}-e-o-amor"), S, "\"A e B no amor\" gana y va a la compatibilidad.")
    if f"{k}-e-a-comunicacao" in EXISTENTES:
        add("Signos", "Comunicação", f"{S} e a comunicação",
            [f"{S} e a comunicação", f"comunicação de {S}", f"comunicação do signo de {S}"],
            f"{k}-e-a-comunicacao", S)
    tratar = [s for s in (f"como-tratar-com-um-{k}", f"como-tratar-com-um-{gent[0]}") if s in EXISTENTES]
    if tratar:
        add("Signos", "Como tratar", f"Como tratar com um {S}",
            [f"como tratar com um {gent[0]}", f"como tratar com um {S}", f"como lidar com um {gent[0]}",
             f"como lidar com {gent[1]}"], tratar[0], S)

add("Signos", "Pilar geral", "Signos do Zodíaco",
    ["signos do zodíaco", "Signos do Zodíaco", "os doze signos", "os 12 signos", "doze signos do zodíaco",
     "zodíaco"], existente("signos-do-zodiaco"), A)
add("Signos", "Pilar geral", "Data de nascimento",
    ["signo pela data de nascimento", "signo por data de nascimento", "signos por data de nascimento"],
    existente("data-de-nascimento"), A, "\"data de nascimento\" sola NO se marca (frase común).")
add("Signos", "Compatibilidade", "Compatibilidade Libra",
    ["compatibilidade de Libra", "compatibilidade do signo de Libra", "compatibilidade dos librianos"],
    existente("compatibilidade-libra"), "Libra")

# ---------- Compatibilidade (144, en los dos órdenes) ----------
for ka, Sa, ga in SIGNOS:
    for kb, Sb, gb in SIGNOS:
        slug = existente(f"compatibilidade-{ka}-e-{kb}",
                         f"compatibilidade-{ka}-e-gemini" if kb == "gemeos" else "-",
                         f"{ka}-e-{kb}")
        formas = [f"compatibilidade entre {Sa} e {Sb}", f"Compatibilidade entre {Sa} e {Sb}",
                  f"compatibilidade de {Sa} e {Sb}", f"compatibilidade {Sa} e {Sb}",
                  f"Compatibilidade {Sa} e {Sb}", f"{Sa} e {Sb} no amor", f"casal {Sa} e {Sb}",
                  f"combinação de {Sa} com {Sb}", f"combinação entre {Sa} e {Sb}", f"{Sa} com {Sb} no amor"]
        if ka == kb:
            formas += [f"dois {ga[1]}", f"duas {ga[3]}"]
        add("Compatibilidade", "Par", f"Compatibilidade {Sa} e {Sb}", formas, slug,
            Sa, "\"A e B\" a secas NO se marca (listas de signos). Cada orden va a su propio post.")

# ---------- Nascidos em (366, existentes) ----------
INICIOS = [((1, 21), "aquario"), ((2, 20), "peixes"), ((3, 21), "aries"), ((4, 21), "touro"),
           ((5, 22), "gemeos"), ((6, 22), "cancer"), ((7, 23), "leao"), ((8, 24), "virgem"),
           ((9, 23), "libra"), ((10, 24), "escorpiao"), ((11, 22), "sagitario"), ((12, 22), "capricornio")]


def signo_fecha(m, d):
    s = "capricornio"
    for (mm, dd), k in INICIOS:
        if (m, d) >= (mm, dd):
            s = k
    return s


for mi, M in enumerate(MESES, 1):
    for d in range(1, DIAS_MES[mi - 1] + 1):
        k = signo_fecha(mi, d)
        base = f"signo-{k}-nascidos-%s-{d}-de-{MSLUG[mi - 1]}"
        slug = existente(base % "em", base % "en")
        dias = [str(d)] + (["1º"] if d == 1 else [])
        formas = []
        for dd in dias:
            for mes in (M, cap(M)):
                formas += [f"{dd} de {mes}", f"nascidos em {dd} de {mes}", f"nascido em {dd} de {mes}",
                           f"nascida em {dd} de {mes}", f"nascidas em {dd} de {mes}",
                           f"quem nasce em {dd} de {mes}", f"quem nasceu em {dd} de {mes}"]
        S = dict((x[0], x[1]) for x in SIGNOS)[k]
        add("Nascidos em", "Dia", f"Signo {S}: nascidos em {d} de {cap(M)}", formas, slug, S,
            "Regla de Orbelis: toda fecha completa se enlaza al \"nascidos em\" (también en los horóscopos).")

# ---------- Horóscopos 2027 (existentes) ----------
H = f"Horóscopo {ANO}"
add("Horóscopo 2027", "Pilar do ano", f"Horóscopo e Previsões {ANO}",
    [f"Horóscopo {ANO}", f"horóscopo {ANO}", f"horóscopo de {ANO}", f"horóscopo para {ANO}",
     f"previsões {ANO}", f"Previsões {ANO}", f"previsões para {ANO}", f"previsões astrológicas para {ANO}"],
    existente(f"horoscopo-{ANO}"), H)
add("Horóscopo 2027", "Pilar do amor", f"Horóscopo do amor {ANO}",
    [f"horóscopo do amor {ANO}", f"Horóscopo do amor {ANO}", f"Horóscopo do Amor {ANO}",
     f"horóscopo do amor para {ANO}", f"amor em {ANO}"],
    existente(f"horoscopo-do-amor-{ANO}"), "Horóscopo do Amor 2027")
for mi, M in enumerate(MESES, 1):
    add("Horóscopo 2027", "Mês geral", f"Horóscopo {cap(M)} {ANO}",
        [f"horóscopo de {M} de {ANO}", f"Horóscopo de {cap(M)} de {ANO}", f"Horóscopo {cap(M)} {ANO}",
         f"horóscopo {M} {ANO}", f"horóscopo de {M} {ANO}", f"previsões de {M} de {ANO}"],
        existente(f"horoscopo-{MSLUG[mi - 1]}-{ANO}"), H,
        f"\"{M} de {ANO}\" solo NO se marca: le ganaría a la fecha \"N de {M}\".")
for k, S, _ in SIGNOS:
    add("Horóscopo 2027", "Anual do signo", f"Horóscopo {S} {ANO}",
        [f"Horóscopo {S} {ANO}", f"horóscopo {S} {ANO}", f"horóscopo de {S} {ANO}",
         f"horóscopo de {S} para {ANO}", f"Horóscopo de {S} para {ANO}", f"previsões de {S} para {ANO}",
         f"{S} em {ANO}", f"ano de {ANO} para {S}"], existente(f"horoscopo-{k}-{ANO}"), H)
    add("Horóscopo 2027", "Amor do signo", f"Horóscopo do amor {S} {ANO}",
        [f"horóscopo do amor {S} {ANO}", f"Horóscopo do amor {S} {ANO}", f"horóscopo do amor de {S} {ANO}",
         f"horóscopo do amor de {S} para {ANO}", f"{S} no amor em {ANO}", f"amor de {S} em {ANO}"],
        existente(f"horoscopo-do-amor-{k}-{ANO}"), "Horóscopo do Amor 2027")
    for mi, M in enumerate(MESES, 1):
        add("Horóscopo 2027", "Mensal do signo", f"Horóscopo {S} {cap(M)} {ANO}",
            [f"Horóscopo {S} {cap(M)} {ANO}", f"horóscopo {S} {M} {ANO}",
             f"horóscopo de {S} para {M} de {ANO}", f"horóscopo de {S} em {M} de {ANO}",
             f"{S} em {M} de {ANO}", f"previsões de {S} para {M} de {ANO}"],
            existente(f"horoscopo-{k}-{MSLUG[mi - 1]}-{ANO}"), H)

# ---------- Elementos ----------
for k, E, slug in [("fogo", "Fogo", "signos-de-fogo-aries-leao-e-sagitario"),
                   ("terra", "Terra", "signos-de-terra-touro-virgem-e-capricornio"),
                   ("ar", "Ar", "signos-de-ar-gemeos-libra-e-aquario"),
                   ("agua", "Água", "signos-de-agua-cancer-escorpiao-e-peixes")]:
    e = E.lower()
    add("Elementos", "Elemento", f"Signos de {E}",
        [f"signos de {e}", f"Signos de {E}", f"signos de {E}", f"signo de {e}", f"signo de {E}",
         f"elemento {e}", f"elemento {E}", f"elemento de {e}", f"elemento {E.lower()}"],
        existente(slug), A, f"\"{e}\" sola NO se marca.")
add("Elementos", "Pilar", "Os elementos na astrologia",
    ["quatro elementos", "os 4 elementos", "elementos do zodíaco", "elementos dos signos",
     "elementos na astrologia"], "elementos-na-astrologia", A)

# ---------- Modalidades ----------
add("Modalidades", "Pilar", "As modalidades dos signos",
    ["modalidades dos signos", "modalidades", "as três modalidades", "qualidades dos signos"],
    "modalidades-dos-signos", A)
for k, f in [("cardinais", ["signo cardinal", "signos cardinais", "modalidade cardinal"]),
             ("fixos", ["signo fixo", "signos fixos", "modalidade fixa"]),
             ("mutaveis", ["signo mutável", "signos mutáveis", "modalidade mutável"])]:
    add("Modalidades", "Modalidade", f"Signos {k}", f, f"signos-{k}", A)
add("Modalidades", "Conceito", "Signos opostos",
    ["signos opostos", "signo oposto", "signo complementar", "signos complementares"], "signos-opostos", A)

# ---------- Planetas ----------
add("Planetas", "Pilar", "Os planetas na astrologia",
    ["planetas na astrologia", "planetas astrológicos", "os planetas"], "planetas-na-astrologia", A)
add("Planetas", "Luminar", "O Sol na astrologia", ["o Sol", "O Sol"], "sol-na-astrologia", A,
    "Solo con mayúscula.")
add("Planetas", "Luminar", "A Lua na astrologia", ["a Lua", "A Lua"], "lua-na-astrologia", A,
    "Solo con mayúscula. \"Lua Nova\", \"Lua Cheia\" y \"signo lunar\" ganan por ser más largas.")
PLANETAS = [("mercurio", "Mercúrio"), ("venus", "Vênus"), ("marte", "Marte"), ("jupiter", "Júpiter"),
            ("saturno", "Saturno"), ("urano", "Urano"), ("netuno", "Netuno"), ("plutao", "Plutão")]
for k, P in PLANETAS:
    add("Planetas", "Planeta", f"{P} na astrologia", [P, f"planeta {P}"], f"{k}-na-astrologia", A)
for k, nom, f in [("nodo-norte", "Nodo Norte", ["Nodo Norte", "nodo norte", "Nodos Lunares", "nodos lunares"]),
                  ("nodo-sul", "Nodo Sul", ["Nodo Sul", "nodo sul"]),
                  ("quiron", "Quíron", ["Quíron"]),
                  ("lilith", "Lilith", ["Lilith", "Lua Negra"])]:
    add("Planetas", "Ponto", nom, f, k, A)
add("Planetas", "Conceito", "Planetas regentes",
    ["planeta regente", "planetas regentes", "regente do signo", "regência planetária"], "planetas-regentes", A)
add("Retrógrados", "Pilar", "Planetas retrógrados",
    ["planetas retrógrados", "planeta retrógrado", "retrogradação", "retrogradações", "retrógrado",
     "retrógrada"], "planetas-retrogrados-e-seus-efeitos", A)  # post 21854 (slug con todas las palabras del título)
# Slugs reales de los posts ya escritos (regla: el slug lleva todas las palabras del título)
SLUG_RETRO = {"mercurio": "o-que-significa-mercurio-retrogrado"}  # post 21853
for k, P in PLANETAS:
    add("Retrógrados", "Planeta", f"{P} retrógrado",
        [f"{P} retrógrado", f"{P} Retrógrado", f"retrogradação de {P}", f"{P} fica retrógrado",
         f"{P} entra em movimento retrógrado"], SLUG_RETRO.get(k, f"{k}-retrogrado"), A)

# ---------- Casas ----------
add("Casas", "Pilar", "As casas astrológicas",
    ["casas astrológicas", "casa astrológica", "as doze casas", "as 12 casas", "casas do mapa astral"],
    "casas-astrologicas", A)
ORD = ["primeira", "segunda", "terceira", "quarta", "quinta", "sexta", "sétima", "oitava", "nona",
       "décima", "décima primeira", "décima segunda"]
for n in range(1, 13):
    o = ORD[n - 1]
    add("Casas", "Casa", f"Casa {n} na astrologia",
        [f"Casa {n}", f"casa {n}", f"{o} casa", f"{cap(o)} Casa", f"{n}ª casa", f"{n}ª Casa"],
        f"casa-{n}-na-astrologia", A)

# ---------- Aspectos ----------
add("Aspectos", "Pilar", "Os aspectos astrológicos",
    ["aspectos astrológicos", "aspecto astrológico", "aspectos planetários", "aspectos na astrologia"],
    "aspectos-astrologicos", A)
for k, nom, f, nota in [
    ("conjuncao", "Conjunção", ["conjunção", "conjunções", "em conjunção"], ""),
    ("sextil", "Sextil", ["sextil", "sextis", "em sextil"], ""),
    ("quadratura", "Quadratura", ["quadratura", "quadraturas", "em quadratura"], ""),
    ("trigono", "Trígono", ["trígono", "trígonos", "em trígono"], ""),
    ("oposicao", "Oposição", ["em oposição a", "aspecto de oposição", "faz oposição"],
     "\"oposição\" sola NO se marca (palabra común)."),
    ("quincuncio", "Quincúncio", ["quincúncio", "inconjunção"], ""),
]:
    add("Aspectos", "Aspecto", nom, f, f"{k}-na-astrologia", A, nota)

# ---------- Conceitos ----------
for k, nom, f, nota in [
    ("mapa-astral", "Mapa astral", ["mapa astral", "mapas astrais", "mapa natal", "carta natal",
                                    "Mapa Astral", "mapa de nascimento"], ""),
    ("ascendente", "Ascendente", ["ascendente", "Ascendente", "signo ascendente"], ""),
    ("descendente", "Descendente", ["Descendente", "signo descendente"],
     "\"descendente\" en minúscula NO se marca."),
    ("meio-do-ceu", "Meio do Céu", ["Meio do Céu", "meio do céu", "Meio-do-Céu"], ""),
    ("fundo-do-ceu", "Fundo do Céu", ["Fundo do Céu", "fundo do céu"], ""),
    ("signo-solar", "Signo solar", ["signo solar", "signos solares"], ""),
    ("signo-lunar", "Signo lunar", ["signo lunar", "signos lunares", "Lua natal"], ""),
    ("decanatos", "Decanatos", ["decanato", "decanatos"], ""),
    ("cuspide", "Cúspide", ["cúspide", "cúspides", "nascidos na cúspide"], ""),
    ("transitos-planetarios", "Trânsitos planetários", ["trânsitos planetários", "trânsito", "trânsitos"], ""),
    ("fases-da-lua", "Fases da Lua", ["fases da Lua", "fases da lua", "fase da Lua", "fase lunar",
                                      "fases lunares"], ""),
    ("lua-nova", "Lua Nova", ["Lua Nova", "Lua nova", "lua nova", "Luas Novas"], ""),
    ("lua-crescente", "Lua Crescente", ["Lua Crescente", "Lua crescente", "lua crescente"], ""),
    ("lua-cheia", "Lua Cheia", ["Lua Cheia", "Lua cheia", "lua cheia", "Luas Cheias"], ""),
    ("lua-minguante", "Lua Minguante", ["Lua Minguante", "Lua minguante", "lua minguante"], ""),
    ("lua-fora-de-curso", "Lua fora de curso", ["Lua fora de curso", "lua fora de curso",
                                                "Lua vazia de curso"], ""),
    ("eclipses", "Eclipses", ["eclipse", "eclipses", "temporada de eclipses"], ""),
    ("eclipse-solar", "Eclipse solar", ["eclipse solar", "eclipses solares", "Eclipse Solar"], ""),
    ("eclipse-lunar", "Eclipse lunar", ["eclipse lunar", "eclipses lunares", "Eclipse Lunar"], ""),
    ("revolucao-solar", "Revolução solar", ["revolução solar", "Revolução Solar"], ""),
    ("retorno-de-saturno", "Retorno de Saturno", ["retorno de Saturno", "Retorno de Saturno"], ""),
    ("sinastria", "Sinastria", ["sinastria", "Sinastria", "mapa de sinastria"], ""),
    ("mapa-composto", "Mapa composto", ["mapa composto", "mapas compostos"], ""),
]:
    add("Conceitos", "Conceito", nom, f, k, A, nota)

# ---------- Workbook ----------
wb = Workbook()
ws = wb.active
ws.title = "Mapa"
ws.append(["Grupo", "Familia", "Entidad (título de trabajo)", "Formas que se marcan (separadas por | )",
           "Slug fijo", "Categoría", "Estado", "ID", "Notas"])
slugs, formas_vistas = set(), {}
for gr, fa, en, fo, sl, ca, no in filas:
    assert sl not in slugs, sl
    slugs.add(sl)
    for f in fo.split(" | "):
        assert formas_vistas.setdefault(f, sl) == sl, (f, sl, formas_vistas[f])
    st, pid = EXISTENTES.get(sl, (None, None))
    ws.append([gr, fa, en, fo, sl, ca, ESTADO_TXT.get(st, "Pendiente"), pid, no])

F = "Arial"
hdr_fill = PatternFill("solid", start_color="3D2C6B")
for c in ws[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = hdr_fill
    c.alignment = Alignment(vertical="center", wrap_text=True)
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, size=10)
        c.alignment = Alignment(vertical="top", wrap_text=c.column in (4, 9))
for col, w in zip("ABCDEFGHI", [16, 20, 40, 70, 44, 20, 12, 8, 50]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:I{ws.max_row}"
n = ws.max_row
ws.conditional_formatting.add(f"G2:G{n}", CellIsRule(operator="equal", formula=['"Publicado"'],
                              fill=PatternFill("solid", start_color="D9EAD3")))
ws.conditional_formatting.add(f"G2:G{n}", CellIsRule(operator="equal", formula=['"Pendiente"'],
                              fill=PatternFill("solid", start_color="FFF2CC")))
dv = DataValidation(type="list", formula1='"Pendiente,Borrador,Programado,Publicado,Descartado"')
ws.add_data_validation(dv)
dv.add(f"G2:G{n}")

rs = wb.create_sheet("Resumen")
rs.append(["Grupo", "Posts en el mapa", "Publicados", "Pendientes"])
grupos = []
for f_ in filas:
    if f_[0] not in grupos:
        grupos.append(f_[0])
for i, g in enumerate(grupos, 2):
    rs.append([g, f'=COUNTIF(Mapa!$A$2:$A${n},A{i})',
               f'=COUNTIFS(Mapa!$A$2:$A${n},A{i},Mapa!$G$2:$G${n},"Publicado")',
               f'=COUNTIFS(Mapa!$A$2:$A${n},A{i},Mapa!$G$2:$G${n},"Pendiente")'])
t = len(grupos) + 2
rs.append(["Total", f"=SUM(B2:B{t-1})", f"=SUM(C2:C{t-1})", f"=SUM(D2:D{t-1})"])
for c in rs[1]:
    c.font = Font(name=F, bold=True, color="FFFFFF")
    c.fill = hdr_fill
rs.column_dimensions["A"].width = 22

rg = wb.create_sheet("Reglas")
for r in [
    "Cómo se usa este mapa",
    "Cada fila es un post (existente o futuro) de orbelis.com.br. El plugin envuelve las 'Formas que se marcan' en [enlace_iluminado slug=\"...\"]; al publicarse el destino, escribe el enlace solo.",
    "El slug es un compromiso: cuando se escriba ese post, tiene que llevar EXACTAMENTE ese slug.",
    "",
    "Reglas del marcado",
    "1. Gana la forma más larga (\"compatibilidade entre Áries e Leão\" gana sobre \"Áries\"; \"Lua Nova\" sobre \"a Lua\").",
    "2. Solo la primera aparición de cada slug en cada post; un destino = un texto ancla.",
    "3. Un post nunca se enlaza a sí mismo.",
    "4. Nunca en H1-H6, JSON-LD, shortcodes ni dentro de un <a>.",
    "5. Mayúsculas exactas (Câncer, Touro, Peixes, Libra, o Sol, a Lua).",
    "6. Tope: 30 marcas por post, contando las que ya tenía.",
    "7. Fechas: toda fecha completa (\"5 de março\") va al post \"nascidos em\" (regla propia de Orbelis).",
]:
    rg.append([r])
for row in rg.iter_rows():
    for c in row:
        b = c.value in ("Cómo se usa este mapa", "Reglas del marcado")
        c.font = Font(name=F, bold=b, size=12 if b else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
rg.column_dimensions["A"].width = 120

wb.save(SALIDA)
print(len(filas), "filas;", sum(1 for f_ in filas if f_[4] in EXISTENTES), "ya existen;",
      sum(len(f_[3].split(" | ")) for f_ in filas), "formas;",
      "existentes fuera del mapa:", len(set(EXISTENTES) - slugs))
