"""Marca un post de horoscopoalfa con [enlace_iluminado] según el mapa de entidades.

Uso como módulo: marcar(html, slug_propio) -> (html_nuevo, lista_de_marcas)
Uso por línea de comandos: python3 marcar.py entrada.html slug-propio [salida.html]
"""
import re
import sys
from openpyxl import load_workbook

MAPA = "mapa-enlaces-iluminados-horoscopoalfa.xlsx"
TOPE = 20  # marcas por post, contando las que ya tenía

# Zonas donde nunca se marca
PROTEGIDAS = re.compile(
    r"<!--.*?-->"                                            # comentarios (bloques de Gutenberg)
    r"|<script\b.*?</script>"                                # JSON-LD
    r"|<style\b.*?</style>"
    r"|<h[1-6]\b.*?</h[1-6]>"                                # títulos
    r"|<a\b.*?</a>"                                          # enlaces existentes
    r"|\[enlaces_iluminados\b.*?\[/enlaces_iluminados\]"     # grillas
    r"|\[enlace_iluminado\b.*?\[/enlace_iluminado\]"         # marcas existentes
    r"|\[[^\]]*\]"                                           # cualquier otro shortcode
    r"|<[^>]+>",                                             # etiquetas HTML y sus atributos
    re.S | re.I,
)
YA_MARCADO = re.compile(r'\[enlace_iluminado\s+slug="([^"]+)"')


def cargar_mapa(ruta=MAPA):
    ws = load_workbook(ruta, read_only=True)["Mapa"]
    entradas = []
    for fila in ws.iter_rows(min_row=2, values_only=True):
        formas, slug, estado = fila[3], fila[4], fila[6]
        if not slug or estado == "Descartado":
            continue
        for f in str(formas).split(" | "):
            f = f.strip()
            if f:
                entradas.append((f, slug))
    # Un único regex por forma: límites de palabra Unicode, espacios flexibles, mayúsculas exactas
    return [(re.compile(r"(?<!\w)" + r"\s+".join(map(re.escape, f.split())) + r"(?!\w)"), f, slug)
            for f, slug in entradas]


_MAPA_CACHE = None


def marcar(html, slug_propio, tope=TOPE):
    global _MAPA_CACHE
    if _MAPA_CACHE is None:
        _MAPA_CACHE = cargar_mapa()

    usados = set(YA_MARCADO.findall(html))
    usados.add(slug_propio)
    existentes = len(YA_MARCADO.findall(html))

    # Tramos de texto libre (fuera de zonas protegidas)
    libres, pos = [], 0
    for m in PROTEGIDAS.finditer(html):
        if m.start() > pos:
            libres.append((pos, m.start()))
        pos = m.end()
    if pos < len(html):
        libres.append((pos, len(html)))

    # Todos los candidatos
    cand = []
    for a, b in libres:
        tramo = html[a:b]
        for rx, forma, slug in _MAPA_CACHE:
            for m in rx.finditer(tramo):
                cand.append((a + m.start(), a + m.end(), slug, forma))

    # 1) Gana la forma más larga en cada superposición
    cand.sort(key=lambda c: (-(c[1] - c[0]), c[0]))
    ganadores, ocupado = [], []
    for c in cand:
        if any(c[0] < e and s < c[1] for s, e in ocupado):
            continue
        ocupado.append((c[0], c[1]))
        ganadores.append(c)

    # 2) Primera aparición de cada slug, sin autoenlace, con tope
    ganadores.sort(key=lambda c: c[0])
    elegidos = []
    for c in ganadores:
        if c[2] in usados:
            continue
        if existentes + len(elegidos) >= tope:
            break
        usados.add(c[2])
        elegidos.append(c)

    # 3) Reescritura de atrás para adelante
    out = html
    for s, e, slug, forma in sorted(elegidos, key=lambda c: -c[0]):
        out = out[:s] + f'[enlace_iluminado slug="{slug}"]' + out[s:e] + "[/enlace_iluminado]" + out[e:]
    return out, [(html[s:e], slug) for s, e, slug, _ in elegidos]


if __name__ == "__main__":
    entrada, slug = sys.argv[1], sys.argv[2]
    html = open(entrada, encoding="utf-8").read()
    nuevo, marcas = marcar(html, slug)
    for texto, sl in marcas:
        print(f"{texto!r:40} -> {sl}")
    print(f"{len(marcas)} marcas nuevas")
    if len(sys.argv) > 3:
        open(sys.argv[3], "w", encoding="utf-8").write(nuevo)
