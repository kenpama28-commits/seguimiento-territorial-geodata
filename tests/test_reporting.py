import csv
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from src.reporting import run

class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'input.csv'
        self.rows = [
            [1,'001','A','01','USAQUEN','asignado','False','False'],
            [2,'002','B','','','sin_interseccion','True','True'],
        ]
        self.write(self.rows)

    def write(self, rows):
        with self.source.open('w', newline='', encoding='utf-8') as f:
            w=csv.writer(f)
            w.writerow(['fid_origen','cenefa','nombre','codigo_localidad','nombre_localidad','estado_territorial','geometria_corregida','revision_coordenadas'])
            w.writerows(rows)

    def test_repeat_load_and_unique_pending_count(self):
        a=run(self.source,self.root/'out')
        b=run(self.source,self.root/'out')
        self.assertEqual(a,b)
        self.assertEqual(a['paraderos'],2)
        self.assertEqual(a['pendientes'],1)  # Dos motivos no duplican la fila.
        with closing(sqlite3.connect(self.root/'out/inventario.sqlite')) as db:
            self.assertEqual(db.execute('SELECT SUM(paraderos) FROM kpi_localidad').fetchone()[0],2)

    def test_bad_load_preserves_previous_inventory(self):
        run(self.source,self.root/'out')
        self.write(self.rows + [self.rows[0]])
        with self.assertRaises(sqlite3.IntegrityError):
            run(self.source,self.root/'out')
        with closing(sqlite3.connect(self.root/'out/inventario.sqlite')) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM paradero').fetchone()[0],2)

    def test_invalid_boolean_is_rejected(self):
        self.rows[0][-1]='unknown'
        self.write(self.rows)
        with self.assertRaises(ValueError):
            run(self.source,self.root/'out')
