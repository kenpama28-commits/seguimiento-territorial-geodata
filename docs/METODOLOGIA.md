# Metodología y criterios de aceptación

## Flujo ejecutado

1. Leer `PSITP` y `Loca` de la copia local V.12.25. Conservar todos sus registros, identificadores y CRS (EPSG:4686). Registrar tamaño, metadatos y hashes de extractos.
2. Verificar integridad del manifiesto, unicidad y presencia de identificadores, CRS y geometrías de localidades.
3. Validar coordenadas finitas dentro de la ventana conservadora de Bogotá/región: −75 < longitud < −73 y 3 < latitud < 6. Es una comprobación de plausibilidad, no de precisión catastral.
4. Reconstruir únicamente puntos fuera de rango cuando sus campos `longitud` y `latitud` sí superan la validación. Si no existe una alternativa utilizable, detener el proceso. Registrar valores anteriores/posteriores y método.
5. Validar topología de localidades. Aplicar `make_valid` solo si hace falta, conservando WKB anterior/posterior; rechazar resultados que no sean polígonos. En esta línea base las 20 localidades ya son válidas: no se reparó ninguna.
6. Cruzar puntos y localidades por intersección. Si hay cero o varias coincidencias, conservar el paradero y dejar la asignación sin resolver. No elegir arbitrariamente una localidad ni modificar puntos para hacerlos encajar.
7. Calcular discrepancia entre geometría final y atributos con `pyproj.Geod`, elipsoide GRS80, en metros. El umbral de 10 m activa revisión; es una regla exploratoria y no una tolerancia oficial.
8. Generar GeoPackage EPSG:4686, GeoJSON EPSG:4326, CSV, informe de calidad y mapa EPSG:9377. Comprobar conservación de registros y conciliación de conteos.

## Reparaciones trazables

| FID | Cenefa | Longitud final | Latitud final | Evidencia |
| --- | --- | ---: | ---: | --- |
| 7621 | 024B04 | -74.103042 | 4.717693 | Atributos de coordenadas del mismo registro |
| 7623 | 534C09 | -74.204501 | 4.630389 | Atributos de coordenadas del mismo registro |

Ambos puntos contenían aproximadamente −1,7976931348623157 × 10^308 en X/Y. Aunque GEOS/Shapely los considera topológicamente válidos, no son coordenadas geográficas utilizables. Por eso se aplican controles topológicos **y** de rango. La bitácora conserva los valores exactos.

## Casos que requieren revisión

- `272A09`, `365A10`, `366A10`: geometrías plausibles que no intersectan ninguna localidad de esta copia. La causa no se ha determinado. Se requiere contrastar límites/versiones y, si procede, validar en terreno.
- `680A08`: geometría válida con discrepancia aproximada de 13,9 m respecto a sus atributos. Se conserva el punto original; ninguna de las dos ubicaciones ha sido confirmada en terreno.

Las correcciones redujeron los casos sin intersección de cinco a tres. El total de cuatro pendientes incluye además la discrepancia de coordenadas. No confundir ausencia de intersección con ausencia física de un paradero.

## Alcance operativo

La base permite preparar zonas, inventarios y listas de revisión. `sql/01_esquema_operacion.sql` propone las entidades localidad, paradero, visita e incidencia con integridad referencial y origen `capturado`/`simulado`. Es un esquema ejecutable vacío; no se ha construido la captura móvil ni se ha cargado información operativa.

La siguiente fase deberá definir ventanas de tiempo, población elegible y protocolo de visitas. Solo entonces se podrá calcular cobertura operativa. Los conteos actuales son de inventario, no de inspecciones completadas.

## Validación reproducible

`python -m unittest discover -s tests -v` verifica puntos extremos, preservación de puntos válidos, fallos irrecuperables, integridad del manifiesto, IDs, conservación de 7.623 filas, correcciones exactas, excepciones, CRS, conciliación de localidades, repetición sin duplicados e integridad referencial del esquema propuesto. GitHub Actions ejecutará estas comprobaciones en Python 3.12 tras la publicación.
