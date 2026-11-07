# Mapas de Enlaces iluminados

Un mapa por sitio: `<sitio>.json` con `{"version", "tope", "entradas": [[forma, slug], ...]}`.
Se carga en el sitio con la ability `enlaces-iluminados/cargar-mapa` usando la URL raw **con hash de commit**.

## horoscopoalfa.com
- Fuente editable: `fuentes/mapa-enlaces-iluminados-horoscopoalfa.xlsx` (hoja Mapa: una fila por post, existente o futuro).
- Regenerar la hoja: `python3 generar_mapa.py` (lee `existentes.json` para la columna Estado).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-horoscopoalfa.xlsx horoscopoalfa.json <version>`.
- `marcar.py`: prototipo en Python de las mismas reglas que `ei_marcar()` del plugin (sirve para probar).
- Regla de oro: el slug de una fila es un compromiso; el post, cuando se escriba, lleva exactamente ese slug.
