-- SQLite: reconstrucción de inventario en transacción desde Python.
CREATE TABLE IF NOT EXISTS paradero (
    fid INTEGER PRIMARY KEY,
    cenefa TEXT NOT NULL CHECK(length(cenefa)>0),
    nombre TEXT NOT NULL,
    codigo_localidad TEXT,
    localidad TEXT,
    estado TEXT NOT NULL CHECK(estado IN ('asignado','sin_interseccion','interseccion_multiple')),
    corregido INTEGER NOT NULL CHECK(corregido IN (0,1)),
    revisar INTEGER NOT NULL CHECK(revisar IN (0,1)),
    CHECK(estado <> 'asignado' OR (codigo_localidad IS NOT NULL AND localidad IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_paradero_localidad ON paradero(codigo_localidad);
CREATE VIEW IF NOT EXISTS kpi_localidad AS
WITH resumen AS (
    SELECT COALESCE(codigo_localidad,'SIN_ASIGNAR') AS codigo,
           COALESCE(localidad,'SIN ASIGNAR') AS localidad,
           COUNT(*) AS paraderos,
           SUM(estado<>'asignado' OR revisar=1) AS pendientes,
           SUM(corregido) AS corregidos
    FROM paradero GROUP BY codigo_localidad, localidad
)
SELECT *, ROUND(100.0*pendientes/paraderos,4) AS porcentaje_pendientes,
       DENSE_RANK() OVER (ORDER BY paraderos DESC) AS rango_inventario
FROM resumen;
