-- Diseño ejecutable en SQLite; separado del GeoPackage de resultados.
-- Las tablas operativas se crean vacías. No representa operación implementada.
PRAGMA foreign_keys = ON;
CREATE TABLE localidad (
    codigo_localidad TEXT PRIMARY KEY,
    nombre TEXT NOT NULL
);
CREATE TABLE paradero (
    cenefa TEXT PRIMARY KEY,
    codigo_localidad TEXT REFERENCES localidad(codigo_localidad),
    longitud REAL NOT NULL CHECK (longitud BETWEEN -75 AND -73),
    latitud REAL NOT NULL CHECK (latitud BETWEEN 3 AND 6),
    crs TEXT NOT NULL DEFAULT 'EPSG:4686' CHECK (crs = 'EPSG:4686')
);
CREATE TABLE visita (
    id_visita TEXT PRIMARY KEY,
    cenefa TEXT NOT NULL REFERENCES paradero(cenefa),
    fecha TEXT NOT NULL,
    resultado TEXT NOT NULL CHECK (resultado IN ('observado','no_accesible','no_encontrado')),
    origen TEXT NOT NULL CHECK (origen IN ('capturado','simulado'))
);
CREATE TABLE incidencia (
    id_incidencia TEXT PRIMARY KEY,
    id_visita TEXT NOT NULL REFERENCES visita(id_visita),
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('abierta','en_revision','cerrada'))
);
CREATE INDEX idx_visita_paradero_fecha ON visita(cenefa, fecha);
