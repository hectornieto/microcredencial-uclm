---
title: Estimación de series temporales de rasgos biofísicos
subject: Ejercicio
subtitle: Ejercicio que muestra cómo obtener series temporales espacializadas de rasgos biofísicos mediante imágenes Sentinel-2
authors:
  - name: Héctor Nieto
    affiliations:
      - Instituto de Ciencias Agrarias, ICA
      - CSIC
    orcid: 0000-0003-4250-6424
    email: hector.nieto@ica.csic.es
  - name: Radoslaw Guzinski
    affiliations:
      - DHI
    orcid: 0000-0003-0044-6806
  - name: Benjamin Mary
    affiliation:
      - Instituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0003-0815-842X
label: nb-biophysical
license: CC-BY-SA-4.0
keywords: Prospect, 4SAIL, crop yield, Daisy crop model
myst:
  enable_extensions: ["deflist", "attrs_block", "attrs_inline"]
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++

# Recopilación de datos de entrada para el modelado de la evapotranspiración

En este cuaderno se recopilan los datos necesarios para ejecutar el modelado del rendimiento de cultivos desde el Ecosistema de Datos Copernicus (CDSE) usando la interfaz openEO.

Este cuaderno puede ejecutarse en el [Jupyterhub de Copernicus Dataspace](https://jupyterhub.dataspace.copernicus.eu), en cuyo caso no se realizan descargas locales de datos, ya que tanto los datos como el entorno de ejecución están en CDSE.

:::{warning}
Debes seleccionar uno de los kernels con GDAL instalado, p. ej. "Geo science".
:::

Primero comprobamos que el Sen-ET Toolbox esté instalado (y lo instalamos si es necesario) y luego importamos todos los paquetes necesarios.

```{code-cell} ipython3
try:
    import senet_toolbox
    print("senet_toolbox importado correctamente")
except ModuleNotFoundError:
    print("Falta la librería senet_toolbox, instalando desde Git")
    !pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git
```

```{code-cell} ipython3
import os
from pathlib import Path
from dateutil.relativedelta import relativedelta
from shapely import to_geojson
from shapely.geometry import box
from osgeo import gdal
import rasterio
import openeo
import pandas as pd
from joblib import load
from senet_toolbox.utils import visualization, date_selector
from senet_toolbox.utils.raster_utils import save_raster
from senet_toolbox.utils.general_utils import read_area_date_info
from senet_toolbox.workflows import collect_input_data
from senet_toolbox.workflows import biophysical_processing
from ipywidgets import interact, interactive, fixed, widgets
from IPython.display import display
import datetime as dt
print("Librerías importadas correctamente, puedes continuar")
```

### Seleccionar el Área de Interés
Para mantener los datos organizados y facilitar el procesamiento de series temporales, los datos de entrada y salida se guardan en carpetas de Área de Interés (AOI). Todos los datos dentro de una carpeta AOI tienen la misma extensión y cuadrícula.

En la celda siguiente, selecciona la ubicación donde deseas almacenar los datos y el nombre del AOI. Al ejecutar en el Jupyterhub de CDSE, se recomienda mantenerlo dentro de `./mystorage`, de lo contrario los datos se borrarán entre sesiones.

Si estás configurando un nuevo AOI, dibuja un polígono en el mapa con la extensión que deseas procesar. Se recomienda seleccionar AOIs de aproximadamente 30 km × 30 km para que el afilado de LST funcione correctamente y el consumo de memoria no sea excesivo.

Si estás trabajando con un AOI existente, el mapa mostrará su extensión.

```{code-cell} ipython3
data_dir = "./mystorage/"
aoi_name = "botswana-maize"
aoi_data_dir = Path(data_dir) / aoi_name
```

```{code-cell} ipython3
# Dibuja o visualiza la extensión del AOI al configurar uno nuevo
map, bboxs = visualization.select_aoi(aoi_data_dir)
map
```

## Seleccionar la fecha de inicio del año agrícola

```{code-cell} ipython3
w_date_ini = widgets.DatePicker(
    description='Selecciona la fecha de inicio del año agrícola',
    disabled=False,
    value=dt.datetime(2024, 1, 1),
)
display(w_date_ini)
```

## Conectarse al backend de OpenEO

Las imágenes de Sentinel-2 serán procesadas y descargadas desde la interfaz OpenEO de CDSE. Ejecuta la celda siguiente para autenticarte en OpenEO.

:::{important}
Es posible que debas hacer clic en un enlace de autenticación que aparecerá y seguir las instrucciones.
:::

```{code-cell} ipython3
connection = openeo.connect("https://openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()
```

## Descargar series temporales de Sentinel-2

Descargaremos medias mensuales y máximos anuales del LAI y del Contenido de Clorofila del Dosel, que se obtienen a partir del producto de reflectancia en el Fondo de la Atmósfera (BOA) de Sentinel-2 usando el [procesador BIOPAR de OpenEO](https://openeo.dataspace.copernicus.eu/openeo/1.1/processes/u:3e24e251-2e9a-438f-90a9-d4500e576574/BIOPAR):

Tanto el LAI como el CCC se definen en BIOPAR de la siguiente manera:
- **Índice de Área Foliar (LAI)**: la mitad del área total de los elementos verdes del dosel por unidad de superficie horizontal del suelo. El valor derivado por satélite corresponde al LAI verde total de todas las capas del dosel, incluido el sotobosque, que puede representar una contribución muy significativa, especialmente en bosques.

- **Contenido de Clorofila del Dosel (CCC)**: el contenido total de clorofila por unidad de superficie del suelo en un grupo continuo de plantas. Es muy adecuado para cuantificar el contenido de nitrógeno a nivel del dosel y estimar la producción primaria bruta.

La metodología BIOPAR fue desarrollada inicialmente para generar productos biofísicos a partir de los sensores SPOT-VEGETATION, ENVISAT-MERIS, SPOT-HRVIR y LANDSAT-OLI, y fue posteriormente adaptada para Sentinel-2. Consiste principalmente en simular una base de datos exhaustiva de reflectancias de dosel (BOA) a partir de las características de la vegetación y la geometría de observación e iluminación. A continuación, se entrenan redes neuronales para estimar una serie de estas características del dosel (BIOPARs) a partir de las reflectancias BOA simuladas junto con los ángulos que definen la configuración observacional.

:::{seealso}
[Weiss y Baret (2016). S2ToolBox Level 2 products: LAI, FAPAR, FCOVER Version 1.1](http://step.esa.int/docs/extra/ATBD_S2ToolBox_L2B_V1.1.pdf)
:::

:::{hint}
Para acelerar el procesamiento, se recomienda usar el [Navegador de Copernicus](https://browser.dataspace.copernicus.eu) para revisar las imágenes de Sentinel-2 en la fecha especificada y antes de ella, y establecer este número lo más bajo posible.
:::

:::{important}
Para áreas grandes, la descarga y agregación de datos en OpenEO puede tardar bastante y podría fallar. Se recomienda procesar regiones más pequeñas a la vez.
Accede a [https://openeo.dataspace.copernicus.eu/](https://openeo.dataspace.copernicus.eu/) e inicia sesión para hacer seguimiento de los trabajos y ver posibles errores.
:::

### Descargar LAI

```{code-cell} ipython3
date_ini = w_date_ini.value

date_end = date_ini + relativedelta(years=1)
bbox = bboxs[0]

bbox_polygon = eval(to_geojson(box(*bbox)))

input_dir = aoi_data_dir / "input"

if not input_dir.exists():
    input_dir.mkdir()

jobs = []
time_window = [str(date_ini),  str(date_ini + relativedelta(years=1))]

print(f"Procesando BIOPAR LAI desde {time_window[0]} hasta {time_window[1]}, esto puede tardar un momento")

lai = biophysical_processing.get_biopar(
    connection, "LAI", time_window, bbox_polygon
    )

lai_max = lai.reduce_dimension(dimension="t", reducer="max")

s2_path = input_dir / f"s2_{date_ini:%Y}_maxLAI.tif"
if not os.path.exists(s2_path):
    print(f"Creando trabajo para el LAI máximo anual de Sentinel-2")
    job = lai_max.create_job(out_format="GTiff")
    job.start()
    jobs.append([job, s2_path])
else:
    print("Se encontraron datos de Sentinel-2 en caché. Omitiendo descarga.")  

date = date_ini
while date < date_end:
    time_window = [str(date),  
                   str(date + relativedelta(months=1) - dt.timedelta(days=1))]    
    print(f"Calculando LAI medio desde {time_window[0]} hasta {time_window[1]}")
    lai_month = lai.filter_temporal(time_window).reduce_dimension(dimension="t", reducer="mean")  

    s2_path = input_dir / f"s2_{date:%Y%m}_LAI.tif"
    if not os.path.exists(s2_path):
        print(f"Creando trabajo para el LAI mensual de Sentinel-2")
        job = lai_month.create_job(out_format="GTiff")
        job.start()
        jobs.append([job, s2_path])
    else:
        print("Se encontraron datos de Sentinel-2 en caché. Omitiendo descarga.")  
    
    date += relativedelta(months=1)

for job, path in jobs:
    print(f"Descargando {path}") 
    collect_input_data.wait_and_download(job, path)
    print(f"Descargado") 

print("Todos los rasgos LAI procesados, puedes continuar")
```

### Descargar el Contenido de Clorofila del Dosel

```{code-cell} ipython3

jobs = []
time_window = [str(date_ini),  str(date_ini + relativedelta(years=1))]

print(f"Procesando BIOPAR CCC desde {time_window[0]} hasta {time_window[1]}, esto puede tardar un momento")

ccc = biophysical_processing.get_biopar(
    connection, "CCC", time_window, bbox_polygon
    )

ccc_max = ccc.reduce_dimension(dimension="t", reducer="max")
s2_path = input_dir / f"s2_{date_ini:%Y}_maxCCC.tif"
if not os.path.exists(s2_path):
    print(f"Creando trabajo para el CCC máximo anual de Sentinel-2")
    job = ccc_max.create_job(out_format="GTiff")
    job.start()
    jobs.append([job, s2_path])    
else:
    print("Se encontraron datos de Sentinel-2 en caché. Omitiendo descarga.") 


date = date_ini
while date < date_end:
    time_window = [str(date),  
                   str(date + relativedelta(months=1) - dt.timedelta(days=1))]    
    print(f"Calculando CCC medio desde {time_window[0]} hasta {time_window[1]}")
    ccc_month = ccc.filter_temporal(time_window).reduce_dimension(dimension="t", reducer="mean")  
     
    s2_path = input_dir / f"s2_{date:%Y%m}_CCC.tif"
    if not os.path.exists(s2_path):
        print(f"Creando trabajo para el CCC mensual de Sentinel-2")
        job = ccc_month.create_job(out_format="GTiff")
        job.start()
        jobs.append([job, s2_path])    
    else:
        print("Se encontraron datos de Sentinel-2 en caché. Omitiendo descarga.") 
    date += relativedelta(months=1)


for job, path in jobs:
    print(f"Descargando {path}") 
    collect_input_data.wait_and_download(job, path)
    print(f"Descargado")

print("Todos los rasgos CCC procesados, puedes continuar")
```
