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

## orbelis.com.br
- Fuente editable: `fuentes/mapa-enlaces-iluminados-orbelis.xlsx` (portugués de Brasil; slugs reales del sitio con sus excepciones).
- Regenerar la hoja: `python3 generar_mapa_orbelis.py` (lee `existentes-orbelis.json`, inventario del 07/11/2026: 776 posts).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-orbelis.xlsx orbelis.json <version> orbelis.com.br`.
- Regla propia: toda fecha completa ("5 de março") se enlaza a su post "nascidos em", también en los horóscopos.
- Excepciones respetadas: 21 slugs de Libra con "nascidos-en", `compatibilidade-capricornio-e-gemini`, `cancer-e-touro`, `signo-virgem`; el 1 de julho va al post 19571 (el `-1o-` queda fuera del mapa).

## horoscopobrasileiro.com.br
- Fuente editable: `fuentes/mapa-enlaces-iluminados-horoscopobrasileiro.xlsx` (portugués de Brasil).
- Regenerar la hoja: `python3 generar_mapa_horoscopobrasileiro.py` (sin inventario; slugs por patrón con sus excepciones).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-horoscopobrasileiro.xlsx horoscopobrasileiro.json <version> horoscopobrasileiro.com.br`.
- Destinos: pilares de signo (`signo-{signo}`), planetas (`sol`, `lua`, `venus`...), "nascidos em" (con excepciones de agosto y dezembro), horóscopos 2027 y 2028. Futuros: `lua-nova`, `lua-cheia`, `nascidos-em-3/4-de-setembro`.

## danimanja.com.br
- Fuente editable: `fuentes/mapa-enlaces-iluminados-danimanja.xlsx` (portugués de Brasil; slugs reales del inventario).
- Regenerar la hoja: `python3 generar_mapa_danimanja.py` (lee `existentes-danimanja.json`, inventario del 13/11/2026: 1.454 posts de horóscopo, nascidos em, ángeles, chino y signos).
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-danimanja.xlsx danimanja.json <version> danimanja.com.br` y después subir `tope` a **45** en el JSON (los anuales por signo tienen 13 títulos pendientes más fechas y signos).
- Familias (decisión de Daniel, 13/11/2026): horóscopos 2026-2028 por título, fechas -> "nascidos em" (post sin "(I)"), ángeles (`anjo-{nome}`), signos -> `signo-{signo}`, "O signo X e o Amor" y Horóscopo Chinês 2027 (solo por título).
- Futuros (compromiso de slug): `horoscopo-{signo}-{mes}-2028` y `horoscopo-do-amor-{signo}-2028`.
