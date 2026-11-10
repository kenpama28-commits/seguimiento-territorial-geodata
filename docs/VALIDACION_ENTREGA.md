# Validación de la entrega local

Fecha: 10 de noviembre de 2026.

- Entorno utilizado: Windows, Python 3.12 distribuido con QGIS 3.44.1; GeoPandas 1.0.1, Shapely 2.0.6, PyProj 3.7.0, Pyogrio 0.9.0, Pandas 2.2.2, NumPy 1.26.4 y Matplotlib 3.10.0.
- Extracción de la fuente original completada en modo lectura. Se conservaron 7.623 paraderos y 20 localidades en extractos ligeros.
- Pipeline ejecutado y salidas GeoPackage/GeoJSON/CSV generadas. Conteos documentados en `reports/calidad.json`.
- **11 pruebas unittest aprobadas**, incluida repetición sin acumulación de filas, detección de insumos alterados, conservación de excepciones e integridad del esquema operativo.
- **Cinco celdas de código del notebook ejecutadas** en el entorno local. Se distribuye sin salidas incrustadas para evitar duplicar datos y facilitar su reproducción.
- Mapa generado y revisado visualmente; bitácora y listado de excepciones revisados.
- Insumos y reportes disponibles sin descargar la base original. Manifiesto con SHA-256 para detectar cambios en los extractos.

La instalación desde cero en un entorno virtual independiente no se ha comprobado todavía. El repositorio público está en `https://github.com/kenpama28-commits/seguimiento-territorial-geodata`; consultar Actions para el resultado de Linux.

Los cuatro casos de revisión geográfica continúan abiertos. No se registraron visitas reales ni se afirma cobertura operativa.
