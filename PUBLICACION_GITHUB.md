# Ejecutar en VS Code y publicar

## Trabajo local

1. Abrir **la carpeta `seguimiento-territorial-geodata`** con Archivo → Abrir carpeta. No abrir todo el proyecto de empleo como raíz de este repositorio.
2. Instalar la extensión Python de Microsoft si no está disponible. Crear `.venv` e instalar `requirements.txt` con los comandos del README.
3. Ejecutar “Python: Select Interpreter” y elegir `.venv`. La configuración incluida permite ejecutar `src.pipeline` con F5 y descubrir pruebas con unittest.
4. Ejecutar el pipeline y las pruebas. Revisar `reports/calidad.json`, bitácora, pendientes y mapa. Los archivos procesados locales se abren en QGIS y están excluidos de Git.

Alternativa local si ya se dispone de QGIS 3.44.1 y sus módulos Python:

```powershell
& 'C:\Program Files\QGIS 3.44.1\bin\python-qgis.bat' -m src.pipeline
& 'C:\Program Files\QGIS 3.44.1\bin\python-qgis.bat' -m unittest discover -s tests -v
```

## Publicación inicial

La preparación local no crea ni publica un repositorio remoto. La cuenta observada durante el diagnóstico es [kenpama28-commits](https://github.com/kenpama28-commits).

1. Crear en GitHub un repositorio vacío `seguimiento-territorial-geodata`, sin README, licencia ni `.gitignore` adicionales.
2. Desde esta carpeta comprobar `git status` y `git log -1 --oneline`. Revisar los archivos del commit inicial con `git show --stat`.
3. Copiar la URL HTTPS que GitHub muestre y ejecutar:

```powershell
git remote add origin https://github.com/kenpama28-commits/seguimiento-territorial-geodata.git
git push -u origin main
```

Si `origin` ya existe, consultar `git remote -v` y comprobar su destino antes de modificarlo. No utilizar `--force`. La autenticación se realiza con el administrador de credenciales de Git/GitHub; nunca escribir tokens en scripts o documentación.

4. Abrir la pestaña Actions y comprobar la ejecución de “Calidad de datos y pipeline”. La configuración está preparada, pero el resultado remoto no se conoce hasta publicar.
5. Confirmar que GitHub renderiza el README, mapa, notebook, atribuciones y reportes. Descripción sugerida: “Inventario territorial SITP Bogotá: control de coordenadas, reparación trazable, cruce por localidad y base para seguimiento en campo”. Temas sugeridos: `gis`, `geodata`, `python`, `geopandas`, `bogota`, `data-quality`.

Se versionan los extractos ligeros y la evidencia de calidad. Los GeoPackage, bases grandes, `.env`, entornos virtuales y posibles registros privados quedan excluidos. No se necesita Git LFS para esta entrega.
