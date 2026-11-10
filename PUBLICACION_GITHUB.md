# Ejecutar en VS Code y actualizar GitHub

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

## Actualizar el repositorio publicado

El repositorio público ya está en [kenpama28-commits/seguimiento-territorial-geodata](https://github.com/kenpama28-commits/seguimiento-territorial-geodata). La rama local `main` sigue `origin/main`.

1. Desde esta carpeta comprobar `git status` y revisar los cambios con `git diff`.
2. Después de ejecutar las pruebas, registrar y subir cambios deliberados:

```powershell
git add README.md src tests docs
git commit -m "Describe el cambio realizado"
git push
```

El ejemplo de `git add` muestra carpetas frecuentes; incluir solo los archivos del cambio y revisar `git status` antes del commit. No utilizar `--force`. La autenticación se realiza con el administrador de credenciales de Git/GitHub; nunca escribir tokens en scripts o documentación.

3. Abrir la pestaña Actions y comprobar la ejecución de “Calidad de datos y pipeline”.
4. Confirmar que GitHub renderiza el README, mapa, notebook, atribuciones y reportes. Temas sugeridos: `gis`, `geodata`, `python`, `geopandas`, `bogota`, `data-quality`.

Se versionan los extractos ligeros y la evidencia de calidad. Los GeoPackage, bases grandes, `.env`, entornos virtuales y posibles registros privados quedan excluidos. No se necesita Git LFS para esta entrega.
