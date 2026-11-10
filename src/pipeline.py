"""Valida, repara y cruza la base territorial; no genera visitas ficticias."""
import argparse
import json
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from shapely import make_valid
from shapely.geometry import Point

from .extract import ROOT, sha256


def plausible(x, y):
    """Ventana conservadora Bogotá/región, en grados MAGNA-SIRGAS."""
    return math.isfinite(x) and math.isfinite(y) and -75 < x < -73 and 3 < y < 6


def repair_point(x, y, longitude, latitude):
    if plausible(x, y):
        return Point(x, y), False
    if not plausible(longitude, latitude):
        raise ValueError("Geometría fuera de rango y atributos sin coordenadas utilizables.")
    return Point(longitude, latitude), True


def run(inputs, output, reports):
    inputs, output, reports = map(Path, (inputs, output, reports))
    manifest = json.loads((inputs / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["archivos"].items():
        if sha256(inputs / name) != expected:
            raise ValueError(f"El insumo cambió sin actualizar su manifiesto: {name}")
    table = pd.read_csv(inputs / "paraderos_origen.csv", dtype={"cenefa": str}, float_precision="round_trip")
    zones = gpd.read_file(inputs / "localidades_origen.geojson")
    if zones.crs.to_epsg() != 4686:
        raise ValueError("CRS de localidades diferente al esperado EPSG:4686.")
    for key in ["fid_origen", "objectid", "cenefa"]:
        if table[key].isna().any() or not table[key].is_unique:
            raise ValueError(f"Identificador nulo o duplicado: {key}")
    if zones.codigo_localidad.isna().any() or not zones.codigo_localidad.is_unique:
        raise ValueError("Los códigos de localidad deben ser únicos y completos.")
    if zones.geometry.isna().any() or zones.geometry.is_empty.any():
        raise ValueError("Localidades con geometría ausente o vacía.")
    polygon_repairs = []
    for index in zones.index[~zones.is_valid]:
        before = zones.loc[index, "geometry"]
        after = make_valid(before)
        if after.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError("Reparación de localidad requiere revisión manual.")
        zones.loc[index, "geometry"] = after
        polygon_repairs.append({"codigo_localidad": str(zones.loc[index, "codigo_localidad"]), "metodo": "shapely.make_valid", "wkb_antes": before.wkb_hex, "wkb_despues": after.wkb_hex})
    geometries, repairs = [], []
    for row in table.itertuples():
        point, changed = repair_point(row.x_origen, row.y_origen, row.longitud, row.latitud)
        geometries.append(point)
        if changed:
            repairs.append({"fid_origen": row.fid_origen, "cenefa": row.cenefa, "x_antes": row.x_origen, "y_antes": row.y_origen, "x_despues": point.x, "y_despues": point.y, "crs": "EPSG:4686", "motivo": "coordenadas_fuera_de_rango", "metodo": "reconstruccion_desde_longitud_latitud_fuente"})
    points = gpd.GeoDataFrame(table, geometry=geometries, crs=4686)
    points["geometria_corregida"] = points.fid_origen.isin([r["fid_origen"] for r in repairs])
    geod = Geod(ellps="GRS80")
    distances = []
    for row in points.itertuples():
        if not plausible(row.longitud, row.latitud):
            raise ValueError(f"Atributos de coordenadas fuera de rango: {row.cenefa}")
        distances.append(geod.inv(row.geometry.x, row.geometry.y, row.longitud, row.latitud)[2])
    points["diferencia_atributos_m"] = distances
    joined = gpd.sjoin(points, zones, how="left", predicate="intersects")
    hits = joined.groupby(joined.index).index_right.count()
    ambiguous = set(hits[hits > 1].index)
    joined = joined.loc[~joined.index.duplicated()].copy()
    joined.loc[joined.index.isin(ambiguous), ["codigo_localidad", "nombre_localidad"]] = None
    joined["estado_territorial"] = ["interseccion_multiple" if i in ambiguous else "sin_interseccion" if pd.isna(code) else "asignado" for i, code in zip(joined.index, joined.codigo_localidad)]
    joined["revision_coordenadas"] = joined.diferencia_atributos_m > 10
    joined = joined.drop(columns=["index_right"])
    if len(joined) != len(table) or not joined.is_valid.all() or joined.geometry.is_empty.any():
        raise ValueError("Falló el control de conservación o geometría final.")
    if not zones.is_valid.all():
        raise ValueError("Persisten geometrías de localidad inválidas.")
    output.mkdir(parents=True, exist_ok=True)
    (reports / "figures").mkdir(parents=True, exist_ok=True)
    joined.to_crs(4326).to_file(output / "paraderos.geojson", driver="GeoJSON", layer_options={"RFC7946": "YES"})
    zones.to_crs(4326).to_file(output / "localidades.geojson", driver="GeoJSON", layer_options={"RFC7946": "YES"})
    joined.to_file(output / "base_territorial.gpkg", layer="paraderos", driver="GPKG")
    zones.to_file(output / "base_territorial.gpkg", layer="localidades", driver="GPKG")
    joined.drop(columns="geometry").to_csv(output / "paraderos.csv", index=False)
    pd.DataFrame(repairs, columns=["fid_origen", "cenefa", "x_antes", "y_antes", "x_despues", "y_despues", "crs", "motivo", "metodo"]).to_csv(reports / "correcciones_geometria.csv", index=False)
    (reports / "correcciones_poligonos.json").write_text(json.dumps(polygon_repairs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending = joined[(joined.estado_territorial != "asignado") | joined.revision_coordenadas]
    pending.drop(columns="geometry").to_csv(reports / "pendientes_revision.csv", index=False)
    counts = zones[["codigo_localidad", "nombre_localidad"]].merge(joined.groupby("codigo_localidad").size().rename("paraderos"), on="codigo_localidad", how="left")
    counts["paraderos"] = counts.paraderos.fillna(0).astype(int)
    counts.to_csv(reports / "paraderos_por_localidad.csv", index=False)
    metrics = {
        "paraderos_entrada": len(table), "paraderos_salida": len(joined), "localidades": len(zones),
        "puntos_corregidos": len(repairs), "poligonos_corregidos": len(polygon_repairs),
        "geometrias_finales_validas": int(joined.is_valid.sum()),
        "coordenadas_finales_en_rango": sum(plausible(p.x, p.y) for p in joined.geometry),
        "asignados_localidad": int((joined.estado_territorial == "asignado").sum()),
        "sin_interseccion": int((joined.estado_territorial == "sin_interseccion").sum()),
        "interseccion_multiple": len(ambiguous),
        "diferencias_mayores_10_m": int(joined.revision_coordenadas.sum()),
        "registros_pendientes_revision": len(pending), "visitas_reales": 0,
        "crs_analisis": "EPSG:4686", "crs_geojson_salida": "EPSG:4326",
        "metodo_distancia": "geodésica sobre elipsoide GRS80, metros",
        "hashes_insumos": manifest["archivos"]
    }
    (reports / "calidad.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    create_map(joined, zones, reports / "figures/base_territorial.png")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


def create_map(points, zones, destination):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    p, z = points.to_crs(9377), zones.to_crs(9377)
    fig, axes = plt.subplots(1, 2, figsize=(13, 8), gridspec_kw={"width_ratios": [2, 1]})
    z.plot(ax=axes[0], color="#eef2f7", edgecolor="#8794a7", linewidth=0.6)
    p.plot(ax=axes[0], color="#225ea8", markersize=2, alpha=0.6)
    fixed = p[p.geometria_corregida]
    review = p[(p.estado_territorial != "asignado") | p.revision_coordenadas]
    fixed.plot(ax=axes[0], color="#00875a", markersize=80, marker="*", zorder=5)
    if len(review):
        review.plot(ax=axes[0], color="#c53427", markersize=40, marker="x", zorder=6)
    xmin, ymin, xmax, ymax = p.total_bounds
    axes[0].set_xlim(xmin - 2000, xmax + 2000)
    axes[0].set_ylim(ymin - 2000, ymax + 2000)
    axes[0].set_title("Inventario y excepciones · detalle urbano", loc="left")
    axes[0].set_aspect("equal")
    axes[0].axis("off")
    axes[0].legend(handles=[Line2D([], [], color="#225ea8", marker="o", linestyle="", label="Paradero"), Line2D([], [], color="#00875a", marker="*", linestyle="", label="Coordenadas reconstruidas"), Line2D([], [], color="#c53427", marker="x", linestyle="", label="Pendiente de revisión")], loc="upper left", fontsize=8)
    counts = points.groupby("nombre_localidad").size().reindex(zones.nombre_localidad, fill_value=0).sort_values()
    counts.plot.barh(ax=axes[1], color="#225ea8")
    axes[1].set_title("Paraderos con localidad asignada", fontsize=10)
    axes[1].set_ylabel("")
    axes[1].set_xlabel("Número de paraderos")
    axes[1].tick_params(axis="y", labelsize=8)
    fig.suptitle("Seguimiento territorial GeoData | Base geográfica validada", fontsize=16, weight="bold")
    fig.text(0.05, 0.025, "Fuentes: IDECA / TransMilenio · Mapa de Referencia V.12.25 · Elaboración propia\nMapa: MAGNA-SIRGAS / Origen-Nacional (EPSG:9377). Inventario histórico; no representa visitas de campo.", fontsize=9)
    fig.tight_layout(rect=(0.02, 0.07, 0.98, 0.94))
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=ROOT / "data/sample")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--reports", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    run(args.inputs, args.output, args.reports)
