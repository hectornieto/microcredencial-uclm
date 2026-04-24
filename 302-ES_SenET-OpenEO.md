---
title: Estimación de la Evapotranspiración con imágenes Sentinel
subject: Ejercicio
subtitle: Ejercicio que muestra cómo obtener mapas de Evapotranspiración real y estrés hídrico mediante el fusionado de productos de Copernicus
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
label: nb-senet
license: CC-BY-SA-4.0
keywords: Evapotranspiration, TSEB, Sentinel-2, Sentinel-3, ECMWF
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

# La herramienta Sen-ET OpenEO toolbox
:::{note} Nota
Este proyecto está bajo desarrollo. Algunas funcionalidades pueden cambiar y pueden existir pequeños errores
:::

**Sen-ET** es un marco de trabajo de código abierto para modelar la evapotranspiración real (ET) con alta resolución espacio-temporal utilizando datos de Sentinel y otros productos de Copernicus. Este repositorio contiene cuadernos Jupyter y scripts de Python para el modelado de ET de extremo a extremo mediante el marco Sen-ET, con acceso a datos de Sentinel y preprocesamiento inicial proporcionados a través de la API [openEO](https://documentation.dataspace.copernicus.eu/APIs/openEO/openEO.html) del [Ecosistema de Datos Copernicus](https://dataspace.copernicus.eu/) (CDSE).

Esta implementación sigue el legado del [complemento SNAP Sen-ET](https://www.esa-sen4et.org/) original y de los paquetes Python de código abierto desarrollados para el modelado de ET. Actualmente se incluyen los siguientes módulos:
* [Data Mining Sharpener (pyDMS)](https://github.com/radosuav/pyDMS) - Implementación en Python del algoritmo Data Mining Sharpener (DMS): un algoritmo basado en árboles de decisión para el afilado (desagregación) de imágenes de baja resolución (p. ej., temperatura de superficie terrestre de Sentinel-3) usando imágenes de alta resolución (p. ej., reflectancia de Sentinel-2).
* [Two Source Energy Balance (TSEB)](https://github.com/hectornieto/pyTSEB) - Código Python para el modelo de Balance de Energía de Dos Fuentes (TSEB-PT) para estimar el flujo de calor sensible y latente (evapotranspiración) a partir de mediciones de temperatura radiométrica de la superficie.
* [Meteo Utils](https://github.com/hectornieto/meteo_utils/) - Métodos en Python que permiten la descarga y el procesamiento automático de datos de ECMWF relevantes para el modelado de la evapotranspiración.

## Instalación
### Instalación en el JupyterHub del Ecosistema de Datos Copernicus (CDSE)
Al ejecutarse en el [entorno JupyterHub de CDSE](https://jupyterhub.dataspace.copernicus.eu), las descargas de datos se minimizan, ya que los datos y el cómputo se encuentran en la misma infraestructura de nube.

1. Accede a [https://jupyterhub.dataspace.copernicus.eu](https://jupyterhub.dataspace.copernicus.eu) e inicia un servidor.
2. En el servidor, sube los cuadernos manualmente o clona este repositorio abriendo una terminal y ejecutando:
    ```
    git clone https://github.com/DHI/Sen-ET-OpenEO-toolbox.git mystorage/sen-et-toolbox
    ```
3. Ejecuta el primer cuaderno usando un kernel que tenga GDAL instalado, p. ej. *Geo science*. Este paquete se instala en la primera celda de los cuadernos.
   >💡**Nota**: Deberías poder ejecutar los cuadernos sin ninguna configuración adicional si usas un kernel con GDAL instalado, pero a veces pueden surgir conflictos con paquetes existentes en el entorno. En ese caso, se recomienda hacer una instalación limpia del kernel siguiendo los pasos a continuación.
3. Crea un nuevo kernel limpio usando los siguientes comandos en una terminal de Jupyterhub:
    ```
    conda create -n gdal_env python=3.11 \
    conda activate gdal_env \
    conda install -c conda-forge gdal \
    pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git \
    python -m ipykernel install --user --name=gdal_env --display-name "Sen-ET Kernel" 
    ```
4. Ahora puedes seleccionar el kernel "Sen-ET Kernel" para ejecutar los cuadernos.

### Instalación local
Para instalar el Sen-ET OpenEO Toolbox de forma local, sigue estos pasos:

1. Instala GDAL
Asegúrate de que GDAL esté instalado en tu sistema. Es una dependencia obligatoria para el procesamiento de datos geoespaciales.

2. Instala el Toolbox desde GitHub
Una vez instalado GDAL, puedes instalar el toolbox directamente con pip:
    ```
    pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git
    ```

+++

# Recopilación de datos de entrada para el modelado de la evapotranspiración

En este cuaderno se recopilan los datos necesarios para ejecutar el modelado de la evapotranspiración desde el Ecosistema de Datos Copernicus (CDSE) usando la interfaz openEO.

Este cuaderno puede ejecutarse en el [Jupyterhub de Copernicus Dataspace](https://jupyterhub.dataspace.copernicus.eu), en cuyo caso no se realizan descargas locales de datos, ya que tanto los datos como el entorno de ejecución están en CDSE.

**Nota**: Debes seleccionar uno de los kernels con GDAL instalado, p. ej. "Geo science".

Primero comprobamos que el Sen-ET Toolbox esté instalado (y lo instalamos si es necesario) y luego importamos todos los paquetes necesarios.

```{code-cell} ipython3
try:
    import senet_toolbox
except ModuleNotFoundError:
    !pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git
```

```{code-cell} ipython3
from pathlib import Path
import openeo
from senet_toolbox.utils import date_selector, visualization
from senet_toolbox.utils.general_utils import dump_area_date_info, read_area_date_info
from senet_toolbox.workflows import collect_input_data
```

## Seleccionar el Área de Interés
Para mantener los datos organizados y facilitar el procesamiento de series temporales, los datos de entrada y salida se guardan en carpetas de Área de Interés (AOI). Todos los datos dentro de una carpeta AOI tienen la misma extensión y cuadrícula.

En la celda siguiente, selecciona la ubicación donde deseas almacenar los datos y el nombre del AOI. Al ejecutar en el Jupyterhub de CDSE, se recomienda mantenerlo dentro de `./mystorage`, de lo contrario los datos se borrarán entre sesiones.

Si estás configurando un nuevo AOI, usa la celda siguiente para dibujar un polígono en el mapa con la extensión que deseas procesar. Se recomienda seleccionar AOIs de aproximadamente 30 km × 30 km para que el afilado de LST funcione correctamente y el consumo de memoria no sea excesivo.

Si estás trabajando con un AOI existente, la celda simplemente visualizará el área.

```{code-cell} ipython3
data_dir = "./mystorage/"
aoi_name = "botswana-2"
aoi_data_dir = Path(data_dir) / aoi_name
```

```{code-cell} ipython3
# Dibuja o visualiza la extensión del AOI al configurar uno nuevo
map, bboxs = visualization.select_aoi(aoi_data_dir)
map
```

## Seleccionar fecha a partir de las adquisiciones disponibles de Sentinel-3

**Nota**: `max_cloud_cover` hace referencia a la cobertura de nubes de toda la tesela, no solo del AOI, por lo que los resultados pueden variar. Se recomienda también usar el [Navegador de Copernicus](https://browser.dataspace.copernicus.eu) para comprobar la disponibilidad de datos de Sentinel-3 y Sentinel-2 sobre el AOI dentro del rango temporal especificado.

```{code-cell} ipython3
# Definir parámetros de búsqueda
start_date = "2023-05-01"
end_date = "2023-05-10"
max_cloud_cover = 10 # Filtrar escenas con alta cobertura de nubes

# Buscar imágenes Sentinel-3 disponibles
date_selection = date_selector.select_date(
    aoi_data_dir = aoi_data_dir,
    start_date=start_date,
    end_date=end_date,
    max_cloud_cover=max_cloud_cover
)
```

## Conectarse al backend de OpenEO

Las imágenes de Sentinel-3 y Sentinel-2, el mapa de cobertura del suelo Worldcover y el Modelo Digital de Elevación de Copernicus se descargan desde la interfaz OpenEO de CDSE. Ejecuta la celda siguiente para autenticarte en OpenEO.

**Nota:** Es posible que debas hacer clic en un enlace de autenticación que aparecerá y seguir las instrucciones.

```{code-cell} ipython3
connection = openeo.connect("https://openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()
```

## Descargar datos de Sentinel-2 y Sentinel-3 para el AOI y la fecha especificados

Descarga la Temperatura de Superficie Terrestre (LST) y el Ángulo Zenital de Visión (VZA) de Sentinel-3, y los datos de reflectancia de Sentinel-2.

Al descargar Sentinel-2, mantén el ajuste `use_biopar_processor=True` para descargar también el índice de área foliar y otros parámetros biofísicos. El parámetro `sentinel2_search_range` indica cuántas fechas anteriores a la especificada se deben buscar datos de Sentinel-2. El archivo de salida contendrá el compuesto de píxeles más próximo sin nubes creado a partir de las fechas disponibles de Sentinel-2. Para acelerar el procesamiento, se recomienda usar el [Navegador de Copernicus](https://browser.dataspace.copernicus.eu) para revisar las imágenes de Sentinel-2 en la fecha especificada y antes de ella, y establecer este número lo más bajo posible.

**Nota**: Para áreas grandes, la descarga y agregación de datos en OpenEO puede tardar bastante y podría fallar. Se recomienda procesar regiones más pequeñas a la vez.
Accede a [https://openeo.dataspace.copernicus.eu/](https://openeo.dataspace.copernicus.eu/) e inicia sesión para hacer seguimiento de los trabajos y ver posibles errores.

```{code-cell} ipython3
s3_lst_path,s3_vza_path,s3_mask_path = collect_input_data.collect_sentinel3_data(
    connection=connection,
    bbox=bboxs[-1],
    date=date_selection.value,
    aoi_name=aoi_name,
    out_dir=data_dir,
)
```

#### Ahora puedes visualizar la Temperatura de Superficie Terrestre (LST), el VZA o la Máscara de Sentinel-3

```{code-cell} ipython3
visualization.show_raster_map(
    s3_lst_path, # cambiar a s3_vza_path o s3_mask_path 
    cmap="inferno"
)
```

```{code-cell} ipython3
s2_path = collect_input_data.collect_sentinel2_data(
    connection=connection,
    bbox=bboxs[-1],
    date=date_selection.value,
    aoi_name=aoi_name,
    out_dir=data_dir,
    sentinel2_search_range = 5,
    use_biopar_processor = True
)
```

Visualiza los datos RGB de Sentinel-2 para confirmar que todo está correcto.

```{code-cell} ipython3
visualization.show_raster_map(
    s2_path,
    rgb=True
)
```

## Descargar datos estáticos del AOI

El mapa de cobertura del suelo Worldcover y el modelo digital de elevación no cambian con el tiempo, por lo que solo es necesario descargarlos una vez al configurar un nuevo AOI. Si estás trabajando con un AOI existente, puedes saltarte las dos celdas siguientes.

```{code-cell} ipython3
worldcover_path = collect_input_data.collect_worldcover_data(
    connection=connection,
    bbox=bboxs[-1],
    date=date_selection.value,
    aoi_name=aoi_name,
    s2_template_path=s2_path,
    out_dir=data_dir,
)
```

Visualiza los datos de World Cover (aquí solo vemos el color; cada color representa una clase diferente en el conjunto de datos Worldcover).

```{code-cell} ipython3
visualization.show_raster_map(
    worldcover_path,
    cmap="tab20c"
)
```

```{code-cell} ipython3
dem_path = collect_input_data.collect_dem_data(
    connection=connection,
    bbox=bboxs[-1],
    date=date_selection.value,
    aoi_name=aoi_name,
    s2_template_path=s2_path,
    out_dir=data_dir,
)
```

```{code-cell} ipython3
visualization.show_raster_map(
    dem_path,
    cmap="terrain",
    opacity=0.9
)
```

# Preparación de datos de entrada para el modelado de la evapotranspiración

En esta sección, los datos necesarios para el modelado de la evapotranspiración, recopilados en la sección anterior, se preprocesan para ser utilizados como entrada al modelo de evapotranspiración TSEB.

Este cuaderno puede ejecutarse en el [Jupyterhub de Copernicus Dataspace](https://jupyterhub.dataspace.copernicus.eu), en cuyo caso no se realizan descargas locales de datos, ya que tanto los datos como el entorno de ejecución están en CDSE.

**Nota**: Debes seleccionar uno de los kernels con GDAL instalado, p. ej. "Geo science".

Primero comprobamos que el Sen-ET Toolbox esté instalado (y lo instalamos si es necesario) y luego importamos todos los paquetes necesarios.

```{code-cell} ipython3
try:
    import senet_toolbox
except ModuleNotFoundError:
    !pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git
```

```{code-cell} ipython3
from pathlib import Path
from datetime import datetime
import re

from senet_toolbox import date_selector, visualization, raster_utils, read_area_date_info, load_lut
from senet_toolbox.workflows.decision_tree_sharpener import sharpen_lst
from senet_toolbox.workflows.prepare_ancillary_data import prepare_dem, prepare_lut_maps
from senet_toolbox.workflows.meteo_preprocessing import get_meteo_data
from senet_toolbox.workflows.biophysical_processing import biopar_biophysical_params
```

## 1. Seleccionar el Área de Interés
Para mantener los datos organizados y facilitar el procesamiento de series temporales, los datos de entrada y salida se guardan en carpetas de Área de Interés (AOI). Todos los datos dentro de una carpeta AOI tienen la misma extensión y cuadrícula.

En la celda siguiente, selecciona la ubicación de los datos y el nombre del AOI establecidos en el cuaderno de recopilación de datos de entrada. También se seleccionará automáticamente la última fecha procesada por ese cuaderno. Si deseas trabajar con una fecha diferente, usa la segunda celda para listar las fechas disponibles dentro del AOI para las que se han recopilado datos, selecciona la que desees en la lista desplegable y ejecuta la tercera celda para guardar tu elección.

```{code-cell} ipython3
data_dir = "./mystorage/"
aoi_name = "botswana"
aoi_data_dir = Path(data_dir) / aoi_name
date, bbox = read_area_date_info(dir=aoi_data_dir)
date = str(date)
date_data_dir = aoi_data_dir / date.replace("-", "")
s2_path = date_data_dir / f"s2_{date_data_dir.name}_data.nc"
worldcover_path = aoi_data_dir / "WorldCover2021.tif"
print(date)
```

```{code-cell} ipython3
# Ejecuta esta celda y la siguiente si deseas trabajar con una fecha diferente
date_selection = date_selector.get_collected_dates(
    aoi_data_dir = Path(data_dir) / aoi_name
)
```

```{code-cell} ipython3
date = date_selection.value
date_data_dir = aoi_data_dir / date.replace("-", "")
s2_path = date_data_dir / f"s2_{date_data_dir.name}_data.nc"
worldcover_path = aoi_data_dir / "WorldCover2021.tif"
```

## Preparar datos de entrada estáticos

Los datos de entrada derivados del Modelo Digital de Elevación (MDE) y del mapa de cobertura del suelo no cambian entre fechas, por lo que solo es necesario generarlos una vez al configurar un nuevo AOI.

**Nota:** Por defecto, los parámetros estáticos se establecen según el mapa de cobertura del suelo Worldcover y la [tabla de correspondencia (LUT) por defecto](https://github.com/DHI/Sen-ET-OpenEO-toolbox/blob/main/senet_toolbox/static_data/WorldCover10m_2020_LUT.csv). También puedes especificar rutas a tus propios mapas de cobertura del suelo y tablas de correspondencia personalizadas (p. ej., que cubran cultivos específicos). Las columnas de la tabla personalizada deben ser iguales a las de la predeterminada y las filas deben coincidir con las clases presentes en el mapa de cobertura del suelo.

```{code-cell} ipython3
prepare_dem(aoi_data_dir / "cdem.tif")
```

```{code-cell} ipython3
lut = load_lut()
prepare_lut_maps(worldcover_path, lut)
```

## Procesamiento biofísico de datos Sentinel-2

Muchos de los parámetros biofísicos derivados de Sentinel-2 ya fueron recopilados en el cuaderno anterior. Aquí se guardan como archivos GeoTiff individuales y se utilizan para derivar los parámetros biofísicos restantes, como la fracción de vegetación verde, la altura del dosel o la reflectancia del dosel.

```{code-cell} ipython3
biopar_biophysical_params(s2_path, worldcover_path) 
```

## Afilado de la Temperatura de Superficie Terrestre de Sentinel-3

La Temperatura de Superficie Terrestre (LST) de Sentinel-3 se adquiere con una resolución espacial de aproximadamente 1 km. En este paso, se realiza una fusión de datos con la reflectancia de alta resolución de Sentinel-2, el MDE y las condiciones de iluminación derivadas del MDE, para obtener una representación de alta resolución de la LST.

**Nota:** El parámetro `n_jobs` está establecido en 2 para acelerar el procesamiento. Sin embargo, para AOIs más grandes esto puede provocar un consumo excesivo de memoria y que el cuaderno falle. En ese caso, establece este parámetro en 1.

```{code-cell} ipython3
s2_refl_file = list(date_data_dir.glob("*_REFL.tif"))[0]
dem_path = aoi_data_dir / "cdem.tif"
for lst_file in date_data_dir.glob("*_LST.tif"):
    datetime_utc = datetime.strptime(re.search(r"_(\d{8}T\d{6})_", lst_file.stem).group(1), "%Y%m%dT%H%M%S")
    mask_file = Path(str(lst_file).replace("_LST.tif", "_mask.tif"))
    output_file = Path(str(lst_file).replace("_LST.tif", "_LST_sharpened.tif"))

    sharpened_data = sharpen_lst(
        high_res_optical_path=s2_refl_file,
        high_res_dem_path=dem_path,
        low_res_lst=lst_file,
        low_res_lst_mask=mask_file,
        mask_values=[1],
        datetime_utc=datetime_utc, 
        cv_homogeneity_threshold=0,
        moving_window_size=20,
        disaggregating_temperature=True,
        n_jobs=2,
        n_estimators=30,
        max_samples=0.8,
        max_features=0.8,
        output_path=output_file
    )

# Remuestrear VZA a la cuadrícula de Sentinel-2
for vza_file in date_data_dir.glob("*_VZA.tif"):
    raster_utils.resample_to_template(vza_file, vza_file, s2_refl_file)
```

#### Visualizar la LST afilada

```{code-cell} ipython3
map = visualization.show_raster_map(
    output_file,
    cmap="inferno"
)
map
```

## Recopilación y preparación de datos meteorológicos
Los datos meteorológicos son los únicos datos que no se recopilan de CDSE mediante la interfaz openEO. En su lugar, provienen del [Servicio de Datos Climáticos de Copernicus](https://cds.climate.copernicus.eu/) y del [Servicio de Datos de la Atmósfera](https://cds.climate.copernicus.eu/). Para acceder a los datos de estas dos fuentes necesitas una clave de API, tal como se describe en la documentación:
* [Guía de usuario de CDS](https://cds.climate.copernicus.eu/how-to-api) 

Una vez que hayas creado las claves, guárdalas en los archivos ```key.adsapirc``` y ```key.cdsapirc``` con el formato que se muestra a continuación, y súbelos a `./mystorage` si ejecutas en el Jupyterhub de CDSE:

``` bash
key.adsapirc
url: https://ads.atmosphere.copernicus.eu/api
key: <api_key>
```
y
```` bash
key.cdsapirc
url: https://cds.climate.copernicus.eu/api
key: <api_key>
````

La celda siguiente descarga los datos, aplica correcciones basadas en el MDE a algunos parámetros y los remuestrea a la cuadrícula de Sentinel-2.

```{code-cell} ipython3
template_file = list(date_data_dir.glob("*_LAI.tif"))[0]
for lst_file in date_data_dir.glob("*_LST.tif"):
    sentinel3_acq_datetime_str = re.search("_(\d{8}T\d{6})_", lst_file.stem).group(1)
    sentinel3_acq_datetime = datetime.strptime(sentinel3_acq_datetime_str, "%Y%m%dT%H%M%S")
    meteo_output_path = get_meteo_data(
        datetime = sentinel3_acq_datetime,
        bbox = bbox,
        dem_path = aoi_data_dir / "cdem_300.tif",
        template_path = template_file,
        data_dir=lst_file.parent,
        cds_credentials_file=".cdsapirc",
        ads_credentials_file=".adsapirc",
    )
```


# Implementación del Modelo de Balance de Energía de Dos Fuentes (TSEB)

Este cuaderno implementa el **modelo de Balance de Energía de Dos Fuentes (TSEB)** usando el paquete `pyTSEB`.
Procesa los datos de Temperatura de Superficie Terrestre (LST) afilados de Sentinel-3 junto con parámetros meteorológicos y de vegetación para calcular los flujos de energía de la superficie terrestre (incluyendo la evapotranspiración) a alta resolución espacial.

Este cuaderno puede ejecutarse en el [Jupyterhub de Copernicus Dataspace](https://jupyterhub.dataspace.copernicus.eu), en cuyo caso no se realizan descargas locales de datos, ya que tanto los datos como el entorno de ejecución están en CDSE.

**Nota**: Debes seleccionar uno de los kernels con GDAL instalado, p. ej. "Geo science".

Primero comprobamos que el Sen-ET Toolbox esté instalado (y lo instalamos si es necesario) y luego importamos todos los paquetes necesarios.

```{code-cell} ipython3
try:
    import senet_toolbox
except ModuleNotFoundError:
    !pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git
```

```{code-cell} ipython3
import datetime as dt
from pathlib import Path
import re

from pyTSEB.PyTSEB import PyTSEB
from senet_toolbox import read_area_date_info, date_selector, visualization
```

## Seleccionar el Área de Interés
Para mantener los datos organizados y facilitar el procesamiento de series temporales, los datos de entrada y salida se guardan en carpetas de Área de Interés (AOI). Todos los datos dentro de una carpeta AOI tienen la misma extensión y cuadrícula.

En la celda siguiente, selecciona la ubicación de los datos y el nombre del AOI establecidos en el cuaderno de recopilación de datos de entrada. También se seleccionará automáticamente la última fecha procesada por ese cuaderno. Si deseas trabajar con una fecha diferente, usa la segunda celda para listar las fechas dentro del AOI para las que se han recopilado datos, selecciona la que desees en la lista desplegable y ejecuta la tercera celda para guardar tu elección.

```{code-cell} ipython3
data_dir = "./mystorage/"
aoi_name = "botswana"
aoi_data_dir = Path(data_dir) / aoi_name
date, bbox = read_area_date_info(dir=aoi_data_dir)
date = str(date)
date = date.replace("-", "")
date_data_dir = aoi_data_dir / date
output_file = date_data_dir / "output" / f"TSEB-PT_{date}.vrt"
print(date)
```

```{code-cell} ipython3
date_selection = date_selector.get_collected_dates(
    aoi_data_dir = Path(data_dir) / aoi_name
)
```

```{code-cell} ipython3
date = date_selection.value
date = date.replace("-", "")
date_data_dir = aoi_data_dir / date
output_file = date_data_dir / "output" / f"TSEB-PT_{date}.vrt"
```

Comprueba que la preparación de los datos de entrada se ha realizado correctamente y extrae el día del año y la hora del día de la adquisición de Sentinel-3, ya que estos parámetros son necesarios para ejecutar el TSEB.

```{code-cell} ipython3
lst_files = list(date_data_dir.glob("s3_*_LST_sharpened.tif"))
if not lst_files:
    raise FileNotFoundError(f"No se encontró ningún LST afilado de Sentinel-3 en {date_data_dir}. Ejecuta primero el paso 2.")

match = re.search(r"s3_(\d{8}T\d{6})_", lst_files[0].name)
date_time = match.group(1)

print("Marca temporal de observación detectada:", date_time)

## Convertir marca temporal
dt_obj = dt.datetime.strptime(date_time, "%Y%m%dT%H%M%S")

doy = dt_obj.timetuple().tm_yday
time_utc = dt_obj.hour + dt_obj.minute/60 + dt_obj.second/3600

print("Día del año:", doy)
print("Hora UTC:", time_utc)
```

### Definir los parámetros del modelo TSEB
Aquí puedes especificar qué datos de entrada y otros parámetros debe usar el modelo TSEB. Puedes dejarlo tal cual si ejecutaste los demás cuadernos con los valores predeterminados y deseas usar la parametrización TSEB por defecto.

```{code-cell} ipython3
params = {
    "model": "TSEB_PT",
    "output_file": str(output_file),
    "T_R1": str(date_data_dir / f"s3_{date_time}_LST_sharpened.tif"),  # temperatura de superficie terrestre - debe ser el LST afilado de Sentinel-3
    "VZA": str(date_data_dir / f"s3_{date_time}_VZA.tif"),
    "input_mask": 1,
    "LAI": str(date_data_dir / f"{date}_LAI.tif"),
    "f_c": str(aoi_data_dir / "F_C.tif"),
    "h_C": str(date_data_dir / f"{date}_H_C.tif"),
    "w_C": str(aoi_data_dir / "W_C.tif"),
    "f_g": str(date_data_dir / f"{date}_F_G.tif"),
    "lat": str(aoi_data_dir / "lat.tif"),
    "lon": str(aoi_data_dir / "lon.tif"),
    "alt": str(aoi_data_dir / f"cdem.tif"),
    "stdlon": 0,
    "z_T": 100,
    "z_u": 100,
    "DOY": doy,
    "time": time_utc,
    "T_A1": str(date_data_dir / f"{date_time}_TA.tif"),
    "u": str(date_data_dir / f"{date_time}_WS.tif"),
    "p": str(date_data_dir / f"{date_time}_PA.tif"),
    "ea": str(date_data_dir / f"{date_time}_EA.tif"),
    "S_dn": str(date_data_dir / f"{date_time}_SW-IN.tif"),
    "S_dn_24": str(date_data_dir / f"{date}_SW-IN-DD.tif"),
    "emis_C": 0.99,
    "emis_S": 0.97,
    "tau_vis_C": str(date_data_dir / f"{date}_TAU_VIS_C.tif"),
    "rho_vis_C": str(date_data_dir / f"{date}_RHO_VIS_C.tif"),
    "rho_nir_C": str(date_data_dir / f"{date}_RHO_NIR_C.tif"),
    "tau_nir_C": str(date_data_dir / f"{date}_TAU_NIR_C.tif"),
    "rho_vis_S": 0.15,
    "rho_nir_S": 0.25,
    "alpha_PT": 1.26,
    "x_LAD": str(aoi_data_dir / "X_LAD.tif"),
    "z0_soil": 0.01,
    "landcover": str(aoi_data_dir / "IGBP.tif"),
    "leaf_width": str(aoi_data_dir/ "LEAF_WIDTH.tif"),
    "resistance_form": 0,
    "KN_b": 0.012,
    "KN_c": 0.0038,
    "KN_C_dash": 90,
    "G_form": [[1], 0.35], # Relación constante del 35% - válido cuando la adquisición de LST es alrededor del mediodía
    "water_stress": 0,
    "calc_row": [1, 90],
    "row_az": 90,
}
```

### Ejecutar el modelo TSEB

Finalmente podemos ejecutar el modelo de evapotranspiración TSEB. El archivo de salida `ET_day` representa la evapotranspiración diaria en unidades de mm/día.

```{code-cell} ipython3
model = PyTSEB(params)
results = model.process_local_image()
```

Visualiza el mapa de ET diaria.

```{code-cell} ipython3
map = visualization.show_raster_map(
    output_file.parent / f"{output_file.stem}.data/{output_file.stem}_ET_day.tif",
    cmap="YlGnBu"
)
map
```
