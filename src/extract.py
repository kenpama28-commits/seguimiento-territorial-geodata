"""Extrae dos capas públicas sin modificar el GeoPackage original."""
import argparse
from contextlib import closing
import hashlib
import json
import sqlite3
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extract(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination == source.parent:
        raise ValueError("La extracción debe guardarse en una carpeta distinta de la fuente.")
    destination.mkdir(parents=True, exist_ok=True)
    points = gpd.read_file(source, layer="PSITP", fid_as_index=True)
    zones = gpd.read_file(source, layer="Loca", fid_as_index=True)
    if points.crs.to_epsg() != 4686 or zones.crs.to_epsg() != 4686:
        raise ValueError("Esta versión del extractor requiere EPSG:4686 en ambas capas.")
    points.index.name = "fid_origen"
    table = points[["objectid", "cenefa", "nombre", "via", "direccion_", "localidad", "longitud", "latitud"]].copy()
    table["x_origen"] = points.geometry.x
    table["y_origen"] = points.geometry.y
    table.to_csv(destination / "paraderos_origen.csv", index=True, lineterminator="\n")
    zones = zones[["LocCodigo", "LocNombre", "geometry"]].rename(columns={"LocCodigo": "codigo_localidad", "LocNombre": "nombre_localidad"})
    # GeoJSON con miembro CRS explícito; se conserva MAGNA-SIRGAS para el análisis.
    (destination / "localidades_origen.geojson").write_text(zones.to_json(drop_id=True), encoding="utf-8")
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as connection:
        metadata = connection.execute("SELECT table_name,last_change,srs_id FROM gpkg_contents WHERE table_name IN ('PSITP','Loca') ORDER BY table_name").fetchall()
    manifest = {
        "version_fuente": "Mapa de Referencia V.12.25 (copia local)",
        "archivo_fuente": source.name,
        "bytes_fuente": source.stat().st_size,
        "url_fuente": "https://www.ideca.gov.co/node/6476",
        "fecha_descarga_original": None,
        "crs": "EPSG:4686",
        "capas": [{"nombre": n, "last_change": t, "srs_id": s} for n, t, s in metadata],
        "conteos": {"PSITP": len(points), "Loca": len(zones)},
        "archivos": {n: sha256(destination / n) for n in ["paraderos_origen.csv", "localidades_origen.geojson"]},
        "nota": "Los hashes identifican los extractos; no certifican identidad con la descarga oficial. Sin observaciones de campo."
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["conteos"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Ruta local al GPKG_MR_V1225.gpkg")
    parser.add_argument("--destination", type=Path, default=ROOT / "data/sample")
    args = parser.parse_args()
    extract(args.source, args.destination)
