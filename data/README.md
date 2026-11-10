# Datos, atribución y diccionario

## Procedencia

Fuente de esta extracción: `GPKG_MR_V1225.gpkg`, copia local del Mapa de Referencia V.12.25, 4.408.311.808 bytes. Solo se reutilizan `PSITP` y `Loca`. No se incluyen avalúos, información personal, credenciales ni las bases completas del proyecto inmobiliario.

La [publicación de IDECA de V.12.25](https://www.ideca.gov.co/node/6476) identifica corte general al 30 de diciembre de 2025 y licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Atribución: IDECA / UAECD y entidades productoras del Mapa de Referencia; paraderos zonales aportados por TransMilenio S.A. Se conservan los nombres y códigos originales. No existe afiliación ni respaldo oficial al proyecto.

La ficha independiente de [Paraderos Zonales del SITP](https://datosabiertos.bogota.gov.co/dataset/paraderos-zonales-del-sitp/resource/73f38900-ee51-4f5c-a7b5-9ca2bc2dca9e) fue identificada en el diagnóstico con CC BY-SA 4.0. **No se descargó ni mezcló ese recurso independiente**: el insumo aquí es el paquete V.12.25. Para preservar la atribución y la condición de compartir adaptaciones, las aportaciones derivadas de datos de este proyecto se ofrecen bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). El código tiene licencia MIT por separado. No se atribuye la autoría de los datos de origen al desarrollador.

## Archivos versionados

| Archivo | Contenido | CRS |
| --- | --- | --- |
| `sample/paraderos_origen.csv` | 7.623 registros completos de PSITP; atributos seleccionados y coordenadas originales | EPSG:4686 |
| `sample/localidades_origen.geojson` | 20 polígonos de Loca, sin simplificación, códigos y nombres | EPSG:4686 explícito en el archivo |
| `sample/manifest.json` | Conteos, fechas internas, tamaño de la fuente y hashes SHA-256 de extractos | EPSG:4686 |

`sample` significa selección de capas y columnas para el portafolio; **no es un muestreo de paraderos**. La fecha de descarga original no está disponible y se declara nula. Los hashes permiten detectar cambios en los extractos; no prueban identidad binaria con una descarga oficial. `last_change` describe metadatos de la capa, nunca una visita en campo.

El GeoJSON de entrada conserva el CRS original mediante un miembro `crs`; usarlo con software SIG. Los GeoJSON de salida se reproyectan a EPSG:4326 para intercambio web conforme a RFC 7946.

## Campos principales

| Campo | Significado |
| --- | --- |
| `fid_origen` | Identificador de fila en el GeoPackage original |
| `objectid` | Identificador de objeto en PSITP |
| `cenefa` | Identificador textual del paradero; conservar como texto |
| `nombre`, `via`, `direccion_` | Atributos descriptivos de la fuente |
| `localidad` | Localidad declarada por la fuente; no reemplaza el cruce espacial |
| `longitud`, `latitud` | Coordenadas en atributos de origen |
| `x_origen`, `y_origen` | Coordenadas de la geometría original; preservan los dos valores extremos |
| `codigo_localidad`, `nombre_localidad` | Localidad derivada de la intersección, o nula si no se resuelve |
| `geometria_corregida` | Indica reconstrucción desde atributos |
| `diferencia_atributos_m` | Distancia geodésica entre punto final y atributos, en metros |
| `estado_territorial` | `asignado`, `sin_interseccion` o `interseccion_multiple` |
| `revision_coordenadas` | Diferencia superior al umbral exploratorio de 10 m |

## Almacenamiento

`raw/`, `external/`, `processed/` y `campo_privado/` quedan fuera de Git. El pipeline crea `processed/`. No subir el GeoPackage original ni registros reales de captura con datos personales. Las salidas grandes se reconstruyen a partir de los insumos versionados. La representación PNG y los CSV de control sí forman parte del portafolio.

Cambios realizados: selección de capas y campos, extracción de coordenadas, reconstrucción de dos puntos, cruce espacial, indicadores y reproyección de salidas. El insumo fuente permanece intacto.
