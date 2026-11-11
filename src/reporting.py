"""Carga transaccional y reportes SQL del inventario validado; biblioteca estándar."""
import csv
from contextlib import closing
import hashlib
import html
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def flag(value):
    if value not in ('True', 'False'):
        raise ValueError(f'Booleano inválido: {value!r}')
    return int(value == 'True')


def run(source=None, output=None):
    source = Path(source or ROOT / 'data/processed/paraderos.csv')
    output = Path(output or ROOT / 'reports/analitica')
    rows = []
    with source.open(encoding='utf-8-sig', newline='') as stream:
        for r in csv.DictReader(stream):
            rows.append((int(r['fid_origen']), r['cenefa'], r['nombre'],
                         r['codigo_localidad'] or None, r['nombre_localidad'] or None,
                         r['estado_territorial'], flag(r['geometria_corregida']),
                         flag(r['revision_coordenadas'])))
    if not rows:
        raise ValueError('La fuente no contiene registros')
    output.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(output / 'inventario.sqlite')) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript((ROOT / 'sql/03_reporting.sql').read_text(encoding='utf-8'))
        # Reemplazo atómico del inventario: una carga inválida conserva la anterior.
        with db:
            db.execute('DELETE FROM paradero')
            db.executemany('INSERT INTO paradero VALUES (?,?,?,?,?,?,?,?)', rows)
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        result = db.execute('SELECT * FROM kpi_localidad ORDER BY paraderos DESC, localidad')
        columns = [c[0] for c in result.description]
        data = result.fetchall()
        with (output / 'kpi_localidad.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(data)
        metrics = dict(zip(('paraderos', 'asignados', 'pendientes', 'corregidos'), db.execute(
            "SELECT COUNT(*), SUM(estado='asignado'), SUM(estado<>'asignado' OR revisar=1), SUM(corregido) FROM paradero"
        ).fetchone()))
        metrics['sha256_fuente'] = hashlib.sha256(source.read_bytes()).hexdigest()
        (output / 'metricas.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
        table = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in row) + '</tr>' for row in data)
        document = '''<!doctype html><html lang="es"><meta charset="utf-8"><title>Calidad del inventario SITP</title>
<style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;color:#111}table{border-collapse:collapse;width:100%}td,th{padding:9px;text-align:left;border-bottom:1px solid #bbb}h1{font-size:28px}</style>
<h1>Inventario SITP: indicadores de calidad</h1><p>Fuente: Mapa de Referencia IDECA V.12.25, procesado por GeoData. Indicadores de inventario, sin mediciones de visitas ni servicio.</p>'''
        document += '<p>' + ' | '.join(f'{k}: <b>{v}</b>' for k, v in metrics.items() if k != 'sha256_fuente') + '</p>'
        document += '<table><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in columns) + '</tr></thead><tbody>' + table + '</tbody></table></html>'
        (output / 'dashboard.html').write_text(document, encoding='utf-8')
    return metrics


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
