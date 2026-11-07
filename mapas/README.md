# Mapas de Enlaces iluminados

Un mapa por sitio: `<sitio>.json` con `{"version", "tope", "entradas": [[forma, slug], ...]}`.
Se carga en el sitio con la ability `enlaces-iluminados/cargar-mapa` usando la URL raw **con hash de commit**.

## horoscopoalfa.com
- Fuente editable: `fuentes/mapa-enlaces-iluminados-horoscopoalfa.xlsx` (hoja Mapa: una fila por post, existente o futuro).
- Regenerar la hoja: `python3 generar_mapa.py` (lee `existentes.json` para la columna Estado).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-horoscopoalfa.xlsx horoscopoalfa.json <version>`.
- `marcar.py`: prototipo en Python de las reglas de marcado de la 1.3.0 (la limpieza de la 1.3.1 está solo en el plugin).
- Regla de oro: el slug de una fila es un compromiso; el post, cuando se escriba, lleva exactamente ese slug.

## venusreports.com
- Fuente editable: `fuentes/mapa-enlaces-iluminados-venusreports.xlsx` (en inglés; slugs propios del sitio).
- Regenerar la hoja: `python3 generar_mapa_venusreports.py` (lee `existentes-venusreports.json`).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-venusreports.xlsx venusreports.json <version> venusreports.com`.
- Fila de bloqueo: "Venus Reports" apunta a `ei-bloqueo-venus-reports`, un slug que nunca se publica, para que la marca no enlace al planeta Venus.
