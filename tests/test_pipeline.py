import contextlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import geopandas as gpd
import pandas as pd

from src.pipeline import ROOT, plausible, repair_point, run


class CoordinateTests(unittest.TestCase):
    def test_sentinel_rebuilt_from_source_attributes(self):
        point, changed = repair_point(-1.7976931348623157e308, -1.7976931348623157e308, -74.103042, 4.717693)
        self.assertTrue(changed)
        self.assertEqual((point.x, point.y), (-74.103042, 4.717693))

    def test_valid_point_not_moved_to_disagreeing_attributes(self):
        point, changed = repair_point(-74.124108083, 4.619901333, -74.124231, 4.619924)
        self.assertFalse(changed)
        self.assertEqual(point.x, -74.124108083)

    def test_unrecoverable_point_stops_processing(self):
        with self.assertRaises(ValueError):
            repair_point(float("nan"), 4, 0, 0)

    def test_geographic_window_rejects_nonfinite_and_sentinel(self):
        for x, y in [(float("inf"), 4), (-74, float("nan")), (0, 0), (-1e308, -1e308)]:
            self.assertFalse(plausible(x, y))


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.output, cls.reports = cls.base / "output", cls.base / "reports"
        with contextlib.redirect_stdout(io.StringIO()):
            cls.metrics = run(ROOT / "data/sample", cls.output, cls.reports)
        cls.points = gpd.read_file(cls.output / "base_territorial.gpkg", layer="paraderos")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_no_records_lost_or_ids_duplicated(self):
        self.assertEqual(len(self.points), 7623)
        self.assertTrue(self.points.cenefa.is_unique)
        self.assertTrue(self.points.is_valid.all())
        self.assertTrue(all(plausible(p.x, p.y) for p in self.points.geometry))

    def test_repair_audit_identifies_exact_two_stops(self):
        audit = pd.read_csv(self.reports / "correcciones_geometria.csv")
        self.assertEqual(set(audit.cenefa), {"024B04", "534C09"})
        self.assertEqual(self.metrics["poligonos_corregidos"], 0)

    def test_unresolved_cases_preserved(self):
        pending = pd.read_csv(self.reports / "pendientes_revision.csv")
        self.assertEqual(set(pending.cenefa), {"272A09", "365A10", "366A10", "680A08"})
        self.assertEqual(self.metrics["sin_interseccion"], 3)
        self.assertEqual(self.metrics["interseccion_multiple"], 0)
        delta = pending.loc[pending.cenefa == "680A08", "diferencia_atributos_m"].iloc[0]
        self.assertGreater(delta, 13)
        self.assertLess(delta, 15)

    def test_crs_and_locality_totals(self):
        self.assertEqual(self.points.crs.to_epsg(), 4686)
        web = gpd.read_file(self.output / "paraderos.geojson")
        self.assertEqual(web.crs.to_epsg(), 4326)
        counts = pd.read_csv(self.reports / "paraderos_por_localidad.csv")
        self.assertEqual(len(counts), 20)
        self.assertEqual(int(counts.paraderos.sum()) + self.metrics["sin_interseccion"], len(web))

    def test_repeat_execution_does_not_append_rows(self):
        expected = (self.reports / "calidad.json").read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            run(ROOT / "data/sample", self.output, self.reports)
        self.assertEqual(expected, (self.reports / "calidad.json").read_bytes())
        with contextlib.closing(sqlite3.connect(self.output / "base_territorial.gpkg")) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM paraderos").fetchone()[0], 7623)

    def test_manifest_mismatch_is_rejected(self):
        folder = self.base / "altered"
        folder.mkdir()
        (folder / "paraderos_origen.csv").write_text("changed", encoding="utf-8")
        manifest = json.loads((ROOT / "data/sample/manifest.json").read_text(encoding="utf-8"))
        (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifiesto"):
            run(folder, self.output, self.reports)

    def test_operation_schema_has_referential_integrity(self):
        with contextlib.closing(sqlite3.connect(":memory:")) as db:
            db.executescript((ROOT / "sql/01_esquema_operacion.sql").read_text(encoding="utf-8"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO visita VALUES ('v1','inexistente','2026-11-10','observado','capturado')")
            self.assertEqual(db.execute("SELECT count(*) FROM visita").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
