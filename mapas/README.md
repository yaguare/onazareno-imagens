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
- Angel Numbers y Twin Flames (13/11/2026): pilar `angel-numbers`, 40 números `{n}-angel-number` (con su hora espejo cuando existe, ej. "4:44"), 6 páginas de twin flame y 4 herramientas futuras (`angel-number-calculator`, `twin-flame-calculator`, `mirror-hours`, `twin-flame-reading`). Slugs comprometidos.
- Ascendentes (13/11/2026): pilares `{sign}-rising` ("Aries rising", "ascendant in Aries"…) y 144 combinaciones `{sun}-sun-{rising}-rising` ("Aries Sun Aries Rising", "Aries Sun with Aries rising"…). "ascendant" a secas sigue yendo a `rising-sign` (futura calculadora).

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
- Exportar: `python3 exportar_json.py fuentes/mapa-enlaces-iluminados-danimanja.xlsx danimanja.json <version> danimanja.com.br` y después subir `tope` a **55** en el JSON (los anuales por signo llegan a ~50 marcas: 13 títulos pendientes, fechas, signos y planetas).
- Familias (decisión de Daniel, 13/11/2026): planetas (`mercurio`…`plutao`, `planetas-astrologicos-o-sol`, `planetas-astrologicos-a-lua`, pilar `os-planetas-astrologicos`), horóscopos 2026-2028 por título, fechas -> "nascidos em" (post sin "(I)"), ángeles (`anjo-{nome}`), signos -> `signo-{signo}`, "O signo X e o Amor" y Horóscopo Chinês 2027 (solo por título).
- Futuros (compromiso de slug): `horoscopo-{signo}-{mes}-2028` y `horoscopo-do-amor-{signo}-2028`.
- Horas iguais (14/11/2026, mapa `2026-11-14.1`): 24 horas `HH-HH-significado` (formas "11:11", "11h11" y "1:01"…"9:09"), 9 números `NNN-significado` ("444" y "4:44"; "1:11"…"5:55"), `numeros-dos-anjos`, `horas-invertidas-significado` (también "horas espelhadas"), `horas-exatas-significado`, `horas-iguais-no-amor`. Sin formas de 4 cifras (se confunden con años). La superpilar `horas-iguais` es una página y el marcado solo resuelve posts: no va en el mapa.
