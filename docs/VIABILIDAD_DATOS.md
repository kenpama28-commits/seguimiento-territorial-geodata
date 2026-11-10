# Diagnóstico para reiniciar Seguimiento Territorial GeoData

Fecha de revisión: 10 de noviembre de 2026. Se inspeccionaron en modo lectura el proyecto local `colombia-mercado-inmobiliario_v2`, su GeoPackage V.12.25, Shapefiles y salidas procesadas. También se revisaron los tres repositorios públicos de `kenpama28-commits` en GitHub. Este documento conserva el **diagnóstico previo** a la implementación.

**Actualización de implementación:** ya se extrajeron las dos capas, se reconstruyeron los dos puntos fuera de rango y se ejecutó el cruce espacial. Resultado: 7.623 puntos conservados, 7.620 asignados y cuatro casos pendientes de revisión (tres sin intersección y una discrepancia de coordenadas). La topología por sí sola no detecta los dos valores extremos. El estado vigente, la atribución del extracto y los comandos están en el README, `data/README.md`, `docs/METODOLOGIA.md` y `reports/calidad.json`. Los pasos sobre visitas continúan pendientes.

## Decisión

**Sí podemos reutilizar las bases geográficas para un proyecto de seguimiento territorial de paraderos SITP.** La copia local incluye puntos de paraderos, polígonos de localidades, red vial y capas de contexto. Los registros de visita, novedad, responsable, fecha y resultado no existen en esas bases: deben capturarse de manera autorizada o generarse y rotularse como simulados. El proyecto nuevo no debe presentar métricas operativas simuladas como resultados reales.

## Estructura observada en GitHub

La cuenta pública [`kenpama28-commits`](https://github.com/kenpama28-commits) muestra tres repositorios: [`colombia-mercado-inmobiliario_v2`](https://github.com/kenpama28-commits/colombia-mercado-inmobiliario_v2), [`colombia-mercado-inmobiliario`](https://github.com/kenpama28-commits/colombia-mercado-inmobiliario) y [`credit-risk-analysis`](https://github.com/kenpama28-commits/credit-risk-analysis). Los tres usan `README.md`, `data/`, `notebooks/` y `requirements.txt`. Los dos proyectos inmobiliarios separan `src/`, `sql/` y `reports/figures/`; la versión 2 añade `avaluo/`, `models/`, `.env.example`, `.gitignore` y una guía de publicación. Su README público documenta pregunta, hallazgos, estructura, metodología, reproducibilidad, fuentes y límites.

La carpeta local inmobiliaria no contiene `.git` y su README es anterior al README publicado. Es una copia de trabajo, no una fuente confiable de la estructura exacta del último commit de GitHub. Su código local tiene rutas absolutas y credenciales de PostgreSQL incrustadas en scripts; **no copiar esos archivos al repositorio nuevo**. La conexión del nuevo pipeline debe depender de variables de entorno, con `.env.example` sin secretos. Si la contraseña incrustada sigue activa, debe cambiarse.

El README público de la versión 2 advierte que no hay un remoto DVC configurado y que la ejecución completa depende de datos y una base local. Para GeoData, conviene incluir una muestra ligera y un procedimiento de reconstrucción verificable desde fuentes oficiales.

## Inventario útil del proyecto local

| Fuente local | Registros observados | Uso propuesto | Decisión |
| --- | ---: | --- | --- |
| `data/external/GPKG_MR_V1225.gpkg` → `PSITP` | 7.623 puntos | Inventario maestro de paraderos y atributos `cenefa`, nombre, vía, localidad y coordenadas | Núcleo, tras control de geometría |
| Mismo GeoPackage → `Loca` | 20 polígonos | Asignación y reporte por localidad | Núcleo |
| Mismo GeoPackage → `MVI` | 139.107 líneas | Contexto vial y vinculación exploratoria por `MVICIV` | Segunda etapa |
| Mismo GeoPackage → `UPL` | 33 polígonos | Nivel territorial adicional | Opcional |
| Mismo GeoPackage → `ETro` | 149 puntos | Proximidad a estaciones troncales | Opcional |
| Mismo GeoPackage → `Calz` | 103.628 polígonos | Características de calzada; interpretar códigos antes de usarlos | Opcional |
| `data/external/transporte/paraderos_SITP/PSITP.shp` | 7.693 puntos | Comparación entre copias con esquemas distintos | No mezclar con el inventario principal sin reconciliar IDs y fechas |
| `data/processed/analisis_espacial_2026.gpkg` | 41.862 manzanas | Contexto territorial de valor de suelo y clúster | Opcional, no mide operación de campo |
| `data/processed/valor_manzana_limpio.parquet` | 299.482 filas, 2020–2026 | Serie de valor de referencia por manzana, enlazable mediante código de manzana | Contexto, no indicador de inspecciones |

El GeoPackage completo pesa **4,4 GB** (4.408.311.808 bytes) y contiene 37 capas/tablas. Existe otra copia del mismo tamaño en la raíz local, `base_de_datos_generales-006.gpkg`; no se ha comprobado identidad binaria. Hay además respaldos de PostGIS de aproximadamente 2,0 GB. Ninguno debe copiarse entero al repositorio de portafolio. Las salidas procesadas del proyecto inmobiliario responden a otra pregunta y no sustituyen las tablas de visitas.

## Hallazgos de calidad comprobados

- `PSITP` tiene 7.623 `objectid` y 7.623 `cenefa` distintos; los campos numéricos de longitud y latitud están completos y caen dentro de rangos plausibles para Bogotá.
- **Dos** geometrías de `PSITP` tienen valores centinela extremos en vez de coordenadas utilizables. Sus atributos de latitud/longitud sí contienen valores plausibles, pero la corrección debe quedar registrada y validarse contra la fuente.
- Un cruce espacial `ST_Intersects` entre `PSITP` y `Loca` ubica **7.618** paraderos; **cinco** quedan sin localidad geométrica: los dos anteriores y tres puntos adicionales. No se debe asignar automáticamente la localidad de texto a esos tres sin revisión.
- Entre las 7.621 geometrías con coordenadas plausibles, una difiere más de 10 m de sus campos de longitud/latitud (máximo aproximado: 13,9 m). Se debe definir una tolerancia y revisar ese registro.
- El Shapefile `PSITP.shp` tiene **70 paraderos más** que la capa `PSITP` del GeoPackage y un esquema distinto. El GeoPackage declara `EPSG:4686` (MAGNA-SIRGAS); las capas procesadas del proyecto inmobiliario usan `EPSG:4326`. Las distancias deben calcularse en un CRS proyectado en metros, no en grados.
- Los metadatos internos del GeoPackage indican fechas de actualización de capa distintas: `Loca` 2023-08-29, `MVI` 2024-02-06, `UPL` 2025-05-07 y `PSITP` 2026-02-09. La publicación oficial de V.12.25 señala corte general al 30 de diciembre de 2025; no se debe interpretar una fecha de archivo o metadato como fecha de visita en campo.

Los conteos se obtuvieron de consultas de lectura al GeoPackage y al encabezado DBF de los Shapefiles; el cruce espacial se ejecutó con GDAL/OGR. La comprobación espacial usa `ST_Intersects`, por lo que exige una revisión manual de los cinco casos sin intersección y de posibles fronteras.

## Fuentes, vigencia y atribución

IDECA publicó el [Mapa de Referencia V.12.25](https://www.ideca.gov.co/node/6476) como dato abierto bajo CC BY 4.0. IDECA también anunció la [versión 06.26](https://www.ideca.gov.co/node/6626), con corte al 30 de junio de 2026. La copia local V.12.25 sirve como línea base reproducible; antes de presentar un inventario como vigente, comparar contra 06.26.

El [conjunto específico de Paraderos Zonales del SITP](https://datosabiertos.bogota.gov.co/dataset/paraderos-zonales-del-sitp/resource/73f38900-ee51-4f5c-a7b5-9ca2bc2dca9e) declara CC BY-SA 4.0. La licencia del paquete de referencia y la del conjunto individual difieren; antes de distribuir una extracción, registrar exactamente de qué recurso proviene y conservar la atribución y condiciones aplicables. No atribuir los eventos simulados a TransMilenio ni a IDECA.

## Estructura recomendada para el nuevo GitHub

```text
seguimiento-territorial-geodata/
├── README.md                  # pregunta, alcance, demo, resultados y límites
├── .env.example               # nombres de variables, sin credenciales
├── .gitignore                 # bases grandes y datos privados excluidos
├── requirements.txt
├── data/
│   ├── README.md              # procedencia, versiones, licencias y descargas
│   ├── sample/                # muestra pública pequeña y validada
│   ├── raw/                   # datos originales locales, fuera de Git
│   ├── external/              # extractos locales de capas oficiales
│   └── processed/             # salidas reproducibles
├── src/                       # extracción, validación, cruce y métricas
├── sql/                       # esquema de paraderos, visitas e incidencias
├── notebooks/                 # exploración explicativa, no pipeline principal
├── tests/                     # QA de CRS, IDs, geometría y agregados
├── reports/figures/           # mapas y gráficos legibles para portafolio
└── docs/                      # metodología, fuentes y guion de demo
```

La estructura conserva las convenciones de los repositorios actuales y añade pruebas y trazabilidad. El README debe distinguir: **dato oficial**, **dato derivado** y **evento simulado o capturado**. Una muestra pequeña y un comando de reconstrucción deben permitir evaluar el repositorio sin descargar 4,4 GB.

## Flujo mínimo a implementar

1. Extraer `PSITP` y `Loca` de **una misma versión** oficial a un archivo pequeño; guardar URL, fecha de descarga, versión, licencia, CRS y hash. Incluir `MVI` solo cuando el caso vial esté definido.
2. Validar IDs, coordenadas, geometrías, duplicados y pertenencia a localidad. Emitir una tabla de hallazgos, no descartar silenciosamente los cinco casos detectados.
3. Crear tablas separadas `paradero`, `visita`, `incidencia` y `zona`; cada visita requiere identificador de paradero, fecha, resultado y origen. Si se generan eventos, fijar semilla y marcar cada fila como **simulada**.
4. Calcular cobertura de visitas con ventana temporal y denominador explícitos; agregar por localidad y verificar que mapa, CSV y SQL concuerden.
5. Publicar mapa, informe de calidad, ejemplos de consulta, pruebas y una demo breve. Incluir una nota visible sobre qué datos son oficiales y cuáles simulados.

**Criterio de viabilidad:** las fuentes geográficas son suficientes para iniciar el pipeline y demostrar georreferenciación/cartografía. Para afirmar resultados reales de operación en campo faltan observaciones reales autorizadas. Los valores inmobiliarios y la seguridad agregada son contexto opcional, no evidencia de ejecución de visitas.
