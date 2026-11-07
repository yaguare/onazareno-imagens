"""Exporta el mapa .xlsx a JSON para Enlaces iluminados (cargar-mapa)."""
import json, sys
from openpyxl import load_workbook
xlsx, salida, version = sys.argv[1], sys.argv[2], sys.argv[3]
ws = load_workbook(xlsx, read_only=True)["Mapa"]
ent = []
for fila in ws.iter_rows(min_row=2, values_only=True):
    formas, slug, estado = fila[3], fila[4], fila[6]
    if not slug or estado == "Descartado":
        continue
    for f in str(formas).split(" | "):
        if f.strip():
            ent.append([f.strip(), slug])
json.dump({"sitio": "horoscopoalfa.com", "version": version, "tope": 30, "entradas": ent},
          open(salida, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(ent), "formas")
