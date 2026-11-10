-- Consultas SQLite sobre data/processed/base_territorial.gpkg.
SELECT estado_territorial, COUNT(*) AS paraderos
FROM paraderos GROUP BY estado_territorial;

SELECT cenefa, localidad AS localidad_declarada, estado_territorial,
       diferencia_atributos_m, geometria_corregida
FROM paraderos WHERE estado_territorial <> 'asignado' OR revision_coordenadas = 1;

SELECT l.codigo_localidad, l.nombre_localidad, COUNT(p.cenefa) AS paraderos
FROM localidades AS l LEFT JOIN paraderos AS p
ON l.codigo_localidad = p.codigo_localidad
GROUP BY l.codigo_localidad, l.nombre_localidad;
