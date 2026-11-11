# Analítica de inventario y calidad de datos

## Ejecución y alcance

Desde la raíz: `python -m src.pipeline`, seguido de `python -m src.reporting`.
La segunda etapa usa únicamente la biblioteca estándar de Python y el CSV validado de la primera.
Abre `reports/analitica/dashboard.html` para visualizar resultados. Es un reporte HTML estático.
Se conservan las carpetas src, sql, tests, reports y docs del proyecto original.

El módulo reemplaza el inventario de SQLite dentro de una transacción, aplica restricciones de integridad,
indexa la localidad y usa una CTE y DENSE_RANK para resumir el inventario.
Una segunda carga no acumula registros. Una carga con identificadores duplicados revierte la transacción.
La base SQLite se regenera localmente; los reportes pequeños y el hash de entrada sí se versionan.

## Indicadores

- Paraderos: COUNT de identificadores de origen.
- Asignados: estado territorial igual a asignado.
- Pendientes: sin asignación única O discrepancia de coordenadas. Cada paradero cuenta una sola vez.
- Corregidos: reconstrucción geométrica realizada por el pipeline geográfico.
- Porcentaje pendiente: pendientes/paraderos de cada grupo; la fila SIN ASIGNAR se conserva.
- Rango: posición por volumen de inventario; no es calidad del servicio ni prioridad de inversión.

## Power BI y Excel

Importar `reports/analitica/kpi_localidad.csv` como UTF-8, conservar codigo como texto
y convertir conteos a enteros. Hay una fila por localidad presente más SIN ASIGNAR.
No promediar porcentajes entre localidades; calcular el total ponderado:

```dax
Total paraderos = SUM(kpi_localidad[paraderos])
Pendientes = SUM(kpi_localidad[pendientes])
Porcentaje pendiente = DIVIDE([Pendientes], [Total paraderos], 0)
```

Visuales sugeridos: tarjetas de total y pendientes; barras por localidad; tabla de excepciones.
La integración Power BI queda preparada mediante CSV y medidas DAX; no se entrega ni se afirma un PBIX construido para este módulo.

## Demostración de 90 segundos

1. Explicar que el insumo es un inventario público, corte V.12.25, sin visitas de campo.
2. Mostrar el pipeline geográfico y sus cuatro excepciones.
3. Ejecutar reporting y abrir el HTML: 7.623 registros, 7.620 asignados y cuatro pendientes.
4. Abrir SQL para explicar restricciones, transacción, agregación y ranking.
5. Ejecutar las pruebas y explicar cómo se evita duplicar una carga.
6. Cerrar con la exportación para BI y la limitación: no mide operación real ni ventas.

## Límites frente a vacantes

Evidencia Python, SQL, automatización y calidad. SQLite no equivale a administrar un servidor PostgreSQL,
MongoDB, backups de producción o permisos de usuarios. Tampoco acredita experiencia en turismo,
retail o Google Sheets. El proyecto es de portafolio y no trabajo contratado por una empresa.
