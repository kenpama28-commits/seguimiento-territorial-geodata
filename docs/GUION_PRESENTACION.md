# Demostración de tres minutos

**0:00–0:30 · Problema.** Abrir README y mapa. “Preparé una base territorial de paraderos SITP para apoyar la planeación y el control de visitas en Bogotá. El objetivo de esta fase es asegurar que el inventario geográfico sea utilizable antes de capturar información en campo”.

**0:30–1:00 · Fuentes.** Mostrar `data/README.md` y manifiesto. “Utilicé dos capas públicas de una misma copia del Mapa de Referencia V.12.25: 7.623 paraderos y 20 localidades. Conservo la procedencia, los identificadores y el sistema de coordenadas”.

**1:00–1:45 · Hallazgo y corrección.** Mostrar la bitácora y el mapa. “Detecté dos puntos con coordenadas extremas. La validación topológica no bastaba; añadí controles de rango y reconstruí estos puntos desde atributos de la propia fuente. La corrección conserva evidencia del antes y después y no se presenta como una actualización oficial”.

**1:45–2:15 · Resultados y límites.** Mostrar `reports/calidad.json` y pendientes. “Los 7.623 puntos quedan con coordenadas utilizables; 7.620 intersectan una localidad. Tres siguen sin intersección y otro difiere unos 14 metros de sus atributos. Los cuatro quedan para revisión, sin ajustes arbitrarios”.

**2:15–2:45 · Reproducibilidad.** En terminal de VS Code, ejecutar `python -m src.pipeline` y mostrar las pruebas. Abrir `data/processed/base_territorial.gpkg` en QGIS si se desea. “El procesamiento se reproduce con los extractos incluidos y genera cartografía, tablas y evidencia de calidad”.

**2:45–3:00 · Continuidad.** “La siguiente fase es implementar captura de visitas e incidencias sobre este inventario. Ya propuse el esquema de datos, pero todavía no existen visitas reales ni indicadores de ejecución en campo”.

Antes de grabar: seleccionar el intérprete correcto, ejecutar las pruebas, dejar abiertos README/mapa/bitácora y ocultar cualquier ventana ajena al proyecto. No describir la base histórica como un inventario vigente.
