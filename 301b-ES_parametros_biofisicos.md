---
title: Estimación de series temporales de rasgos biofísicos
subject: Ejercicio
subtitle: Ejercicio que muestra cómo obtener series temporales de rasgos biofísicos mediante imágenes Sentinel-2 en zonas de interés
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

# Introducción

En este ejercicios vamos a descargar series temporales imágenes de refletividad Sentinel-2 para cada una de nuestras áreas de interés, y generaremos los productos biofísicos mediante un algoritmo propio.

Usaremos para ello usando la librería Python de [openEO](https://openeo.org/) para generar los promedios zonales de cada imagen de reflectividad y a parti de ahí continuar con el procesamiento en local.

Este cuaderno puede ejecutarse en el [Jupyterhub de Copernicus Dataspace](https://jupyterhub.dataspace.copernicus.eu), en cuyo caso no se realizan descargas locales de datos, ya que tanto los datos como el entorno de ejecución están en CDSE y se mantienen en tu cuenta.

:::{warning} Atención
Si estás usando el entorno de CDSE debes seleccionar uno de los kernels con GDAL instalado, p. ej. "Geo science".
:::


::::{note} Nota
Las características de Sentinel-2 son las siguientes

:::{table} Características de la misión Sentinel-2
:label: s2
Plataformas | Rango espectral     | Número de bandas | Resolución espacial | Resolución temporal
:---        | :---                | :---             | :---                | :---            
A, B, C     | Visible, NIR, SWIR  | 10 (13)          | 10 -- 20 m          | 5 -- 10 días
:::
::::

```{code-cell} ipython3
from IPython.display import display
import datetime as dt
from pathlib import Path
import datetime as dt
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import openeo
from ipywidgets import interact, interactive, fixed, widgets
from ipyleaflet import Map, basemaps, basemap_to_tiles, DrawControl, Polygon
import multiprocessing as mp
import Py6S as sixs
from pypro4sail import machine_learning_regression as inv
from pyTSEB import meteo_utils as met
from sklearn.ensemble import RandomForestRegressor as rf_sklearn
from statsmodels.tsa.seasonal import MSTL
import warnings
print("Librerías importadas correctamente, puedes continuar")
```

### Seleccionar el Área de Interés
Para mantener los datos organizados y facilitar el procesamiento de series temporales, los datos de entrada y salida se guardan en carpetas de Área de Interés (AOI). Todos los datos dentro de una carpeta AOI tienen la misma extensión y cuadrícula.

En la celda siguiente, selecciona la ubicación donde deseas almacenar los datos y el nombre del AOI. Al ejecutar en el Jupyterhub de CDSE, se recomienda mantenerlo dentro de `./mystorage/301-biophysical`, de lo contrario los datos se borrarán entre sesiones.

Si estás configurando un nuevo AOI, tendrás que subir una capa de polígonos con las zonas de interés. Se recomienda seleccionar AOIs de pequeñas (unos pocos kilómetros) para agilizar el procesado y no usar los cŕeditos gratuitos rápidamente.

```{code-cell} ipython3
data_dir = "./mystorage/301b-biophysical"
aoi_name = "agramon"
aoi_data_dir = Path(data_dir) / aoi_name
if not aoi_data_dir.is_dir():
    aoi_data_dir.mkdir()
```

## Selecciona una capa vector con las zonas de interés
Selecciona de tu PC un archivo con los polígonos con las zonas de interés. Puede ser un archivo `shapefile` o `geojson`. Este se guardará para los siguientes procesos en 

:::{important} Importante
Asegúrate que tu capa está en coordenadas geográficas y que cada polígono tiene un `fid` único.
:::

```{code-cell} ipython3
w_shape = widgets.FileUpload(
    value = (),
    accept="geojson",
    multiple=False
)
display(w_shape)
```

### Visualiza el mapa

```{code-cell} ipython3
if len(w_shape.value) == 0:
    file = aoi_data_dir / f"{aoi_name}.geojson"
else:
    uploaded_file = w_shape.value[0]
    ext = uploaded_file.name.split(".")[-1]
    print(ext)
    file = aoi_data_dir / f"{aoi_name}.{ext}"
    with open(file, "wb") as fp:
        fp.write(uploaded_file.content.tobytes())

site_data = gpd.read_file(file).explode()
    
minx = site_data.bounds["minx"].min()
maxx = site_data.bounds["maxx"].max()
miny = site_data.bounds["miny"].min()
maxy = site_data.bounds["maxy"].max()
base_map = basemap_to_tiles(basemaps.Esri.WorldStreetMap)
m = Map(layers=(base_map,), center=(40, 10), zoom=2)
for i, feature in site_data.iterrows():
    # Simplify polygon with only the exterior coordinates
    polygon = feature["geometry"].exterior.coords.xy
    # Leaflet requires lat/lon order
    coords = list(zip(feature["geometry"].exterior.coords.xy[1], feature["geometry"].exterior.coords.xy[0]))
    polygon = Polygon(
        locations=coords, color="#6bc2e5", fill_color="#6bc2e5", fill_opacity=0.5)
    m.add_layer(polygon)
    
# Center map on AOI
m.center = [(miny + maxy) / 2, (minx + maxx) / 2]
m.zoom = 15
m
```

## Seleccionar el rango de fechas
En la siguiente celda selecciona el año hidrológico de inicio y de final que te interese procesar

```{code-cell} ipython3
w_years = widgets.IntRangeSlider(
    description="Años",
    tooltip='Selecciona el rango de años hidrológicos a procesar',
    disabled=False,
    min=2015,
    max=dt.datetime.today().year - 1,
    value=(2015, dt.datetime.today().year - 1),
)
display(w_years)
```

## Conectarse al backend de OpenEO

Las imágenes de Sentinel-2 serán procesadas y descargadas desde la interfaz OpenEO de CDSE. Ejecuta la celda siguiente para autenticarte en OpenEO.

:::{important} Importante
Es posible que debas hacer clic en un enlace de autenticación que aparecerá y seguir las instrucciones.
:::

```{code-cell} ipython3
connection = openeo.connect("https://openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()
```

## Descargar series temporales de Sentinel-2
Descargaremos la serie temporal de los datos de reflectividad de Sentinel-2, promediados espacialmente según los polígonos que hemos introducido anteriormente.

:::{important} Importante
Este proceso puede llevar un tiempo, ten paciencia o hazlo durante varios días.
:::

```{code-cell} ipython3
input_dir = aoi_data_dir / "input"
start_date = dt.datetime(w_years.value[0], 10, 1)
end_date = dt.datetime(w_years.value[1], 9, 30)

COLLECTION = "SENTINEL2_L2A"
S2_BANDS = ["B02", "B03", "B04", "B05", "B06",
            "B07", "B08", "B8A", "B11", "B12"]

BANDS = ["SCL", "AOT", "WVP"] + S2_BANDS
TEMP_CSV = Path() / "aggregation.csv"
OUT_VARS = ["TIMESTAMP_UTC", "AOT", "TCWV", ] + S2_BANDS


def download_sentinel2(coords, date_ini, date_end, out_file):

    connection.authenticate_oidc_refresh_token()
    s2l2a = connection.load_collection(
        COLLECTION,
        temporal_extent=[date_ini.strftime("%Y-%m-%d"),
                         date_end.strftime("%Y-%m-%d")],
        bands=BANDS
    )

    # Select the "SCL" band from the data cube
    s2l2a = s2l2a.mask(s2l2a.band("SCL") < 4).mask(s2l2a.band("SCL") > 5)
    s2l2a = s2l2a.aggregate_spatial(coords, "mean")
    print(f"Guardando datos en un archivo temporal para postprocesado")
    s2l2a.download(TEMP_CSV)
    df = pd.read_csv(TEMP_CSV)
    TEMP_CSV.unlink()
    df["TIMESTAMP_UTC"] = df["date"].values
    df.loc[:, "AOT"] = df["AOT"].values * 1e-3
    df["TCWV"] = df["WVP"].values * 1e-3
    for band in S2_BANDS:
        df.loc[:, band] = df[band].values * 1e-4

    df = df[OUT_VARS]
    df.sort_values("TIMESTAMP_UTC", inplace=True)    
    df.to_csv(out_file, index=False, sep=";")
    print(f"Serie temporal guardada en {out_file}")

for i, feature in site_data.iterrows():
    site = feature["fid"]
    polygon = feature["geometry"]
    out_file = input_dir / f"site-{site}_sentinel-2-l2a.csv"
    if out_file.exists():
        print(f"Serie temporal de Sentinel-2 para el obejto {site} ya extraída en {out_file}, omitiendo")
        continue

    print(f"Obteniendo serie temporal de Sentinel-2 para el objeto {site}")
    download_sentinel2(polygon, start_date, end_date, out_file)

print("Terminado con todas las tareas, puedes proseguir a la siguiente celda")
```

## Estimar rasgos biofísicos
Al contrario quen en la práctica [301a][301a-ES_parametros_biofisicos.md], vamos a generar nosotros mismos los productos biofísicos mediante la construcción de base de datos de parámetros biofísicos y espectros correspondientes simulados con ProspectD+4SAIL.

:::{seealso} Ver también
Puedes volver a recordar detalles sobre estos modelos en el cuaderno digital [102](./102-ES_espectro_vegetacion.md)
:::

```{code-cell} ipython3
# Puedes subir este valor (p.e. 10000 o 50000) para tener más robustez en las estimaciones a coste de un mayor tiempo de procesado
N_SIMULATIONS = 1000  

# Computación en paralelo, usaremos todas las CPUs disponibles
N_JOBS = -1

# Selecciona entre "Cab", "Car", "Cm", "Cw", "Ant", "Cbrown", "LAI", "leaf_angle"
OBJ_PARAM_NAMES = ["Cab", "Cw", "Ant", "LAI"]


S2_BANDS = ["B02", "B03", "B04", "B05", "B06",
            "B07", "B08", "B8A", "B11", "B12"]


# "Cab", "Car", "Cm", "Cw", "Ant", "Cbrown", "LAI", "leaf_angle"
# Path to the pyPro4SAIL soil library and SRF library
SOIL_LIBRARY = Path(inv.__file__).parent / "spectra" / "soil_spectral_library"
SRF_LIBRARY = Path(inv.__file__).parent / "spectra" / "sensor_response_functions"
WLS_SIM = np.arange(400, 2501)
SATELLITE = "2A"
ACQ_TIME = 10.5


def get_diffuse_radiation_6S(aot, wvp, sza, saa, date,
                             altitude=0.1, wls_step=10, n_jobs=None):
    warnings.simplefilter("ignore")
        
    s = sixs.SixS()
    s.atmos_profile = sixs.AtmosProfile.PredefinedType(
        sixs.AtmosProfile.MidlatitudeSummer)

    s.aeroprofile = sixs.AeroProfile.PredefinedType(
        sixs.AeroProfile.Continental)

    s.ground_reflectance = sixs.GroundReflectance.HomogeneousLambertian(0)

    if np.isfinite(wvp) and wvp > 0:
        s.atmos_profile = sixs.AtmosProfile.UserWaterAndOzone(wvp, 0.9)

    if np.isfinite(aot) and aot > 0:
        s.aot550 = aot

    s.geometry.solar_z = sza
    s.geometry.solar_a = saa
    s.geometry.view_z = 0
    s.geometry.view_a = 0
    s.geometry.day = date.day
    s.geometry.month = date.month

    s.altitudes.set_target_custom_altitude(altitude)
    s.wavelength = sixs.Wavelength(0.4, 2.5)

    wls = np.arange(400, 2501)
    wls_sim = np.arange(400, 2501, wls_step)

    wv, res = sixs.SixSHelpers.Wavelengths.run_wavelengths(s,
                                                           wls_sim / 1000.,
                                                           verbose=False,
                                                           n=n_jobs)

    eg_d = np.array(sixs.SixSHelpers.Wavelengths.extract_output(res,
                                                                'diffuse_solar_irradiance'))

    eg_s = np.array(sixs.SixSHelpers.Wavelengths.extract_output(res,
                                                                'direct_solar_irradiance'))

    eg_d = np.maximum(eg_d, 0)
    eg_s = np.maximum(eg_s, 0)
    skyl = np.full_like(wls, np.nan, dtype=np.float64)
    # Fill the diffuse values into a full wavelenght array
    valid = np.in1d(wls, wls_sim, assume_unique=True)
    skyl[valid] = eg_d / (eg_d + eg_s)
    # Fill nans by linear interpolation
    nans, x = np.isnan(skyl), lambda z: z.nonzero()[0]
    skyl[nans] = np.interp(x(nans), x(~nans), skyl[~nans])

    return skyl


def build_soil_database(soil_albedo_factor,
                        soil_library=SOIL_LIBRARY):
    soil_library = Path(soil_library)
    n_simulations = np.size(soil_albedo_factor)
    soil_files = list(soil_library.glob('jhu.*spectrum.txt'))
    n_soils = len(soil_files)
    soil_spectrum = []
    for soil_file in soil_files:
        r = np.genfromtxt(soil_file)
        soil_spectrum.append(r[:, 1])

    multiplier = int(np.ceil(float(n_simulations / n_soils)))
    soil_spectrum = np.asarray(soil_spectrum * multiplier)
    soil_spectrum = soil_spectrum[:n_simulations]
    soil_spectrum = soil_spectrum * soil_albedo_factor.reshape(-1, 1)
    soil_spectrum = np.clip(soil_spectrum, 0, 1)
    soil_spectrum = soil_spectrum.T
    return soil_spectrum


def biophysical_retrieval(lat, lon, l2a_df, out_file, n_simulations=40000, n_jobs=-1):
    warnings.simplefilter("ignore")        
    if n_jobs <= 0:
        n_jobs = mp.cpu_count()

    out_dict = {"TIMESTAMP_UTC" : []}
    for param in OBJ_PARAM_NAMES:
        out_dict[param] = []

    for _, row in l2a_df.iterrows():
        start_time = dt.datetime.now()
        # Starting biophysical retrival for {row['TIMESTAMP_UTC']}
        aot = row["AOT"]
        wvp = row["TCWV"]
        doy = row["TIMESTAMP_UTC"].dayofyear
        image_array = row[S2_BANDS].values.astype(float)
        if not np.all(np.isfinite(image_array)) or np.any(image_array < 0):
            # Date has not valid reflectance data
            continue

        image_array = image_array.reshape((1, -1))
        warnings.simplefilter("ignore")
        params_orig = inv.build_prosail_database(n_simulations,
                                                 distribution=inv.SALTELLI_DIST)

        scikit_regressor_opts = {"n_estimators": 100,
                                 "min_samples_leaf": 1,
                                 "n_jobs": n_jobs}

        # Get Solar angles
        sza, saa = met.calc_sun_angles(lat,
                                       lon,
                                       lon,
                                       doy,
                                       ACQ_TIME)

        sza, saa = map(float, [sza.item(), saa.item()])
        vza = 0
        # Running 6S for estimation of diffuse/direct irradiance
        skyl = get_diffuse_radiation_6S(
                aot, wvp, sza, saa, row["TIMESTAMP_UTC"],
                altitude=0.1, wls_step=100)

        # Stack spectral bands
        srf = []
        srf_file = SRF_LIBRARY / f'Sentinel{SATELLITE}.txt'
        srfs = np.genfromtxt(srf_file, dtype=None, names=True)
        for band in S2_BANDS:
            srf.append(srfs[band])

        # Builing standard soil database
        soil_spectrum = build_soil_database(params_orig["bs"])
        # Building {np.size(params_orig['bs'])} PROSPECTD+4SAIL simulations

        rho_canopy_vec, params = inv.simulate_prosail_lut_parallel(
            n_jobs,
            params_orig,
            WLS_SIM,
            soil_spectrum,
            skyl=skyl,
            sza=sza,
            vza=vza,
            psi=0,
            srf=srf,
            outfile=None,
            calc_FAPAR=False,
            reduce_4sail=True)

        params = pd.DataFrame(params)
        reg = rf_sklearn(**scikit_regressor_opts)
        # Apply model to Landsat image
        out_dict["TIMESTAMP_UTC"].append(row['TIMESTAMP_UTC'])
        for i, param in enumerate(OBJ_PARAM_NAMES):
            reg = reg.fit(rho_canopy_vec, params[param])
            output = reg.predict(image_array).item()

            min_value = inv.prosail_bounds[param][0]
            max_value = inv.prosail_bounds[param][1]
            out_dict[param].append(np.clip(output, min_value, max_value))

        elapsed = (dt.datetime.now() - start_time).total_seconds()
        print(f"Finalizado {row['TIMESTAMP_UTC']:%Y-%m-%d} en {elapsed :.0f} segundos")

    print(f"Guardando serie temporal de rasgos biofísicos en {out_file}")
    pd.DataFrame.from_dict(out_dict).to_csv(out_file, index=False, sep=";")


for i, feature in site_data.iterrows():
    site = feature["fid"]
    lon, lat = feature["geometry"].centroid.xy
    in_file = input_dir / f"site-{site}_sentinel-2-l2a.csv"
    l2a = pd.read_csv(in_file, sep=";")
    l2a["TIMESTAMP_UTC"] = pd.to_datetime(l2a["TIMESTAMP_UTC"])
    valid = np.isfinite(l2a["B8A"])
    l2a = l2a.loc[valid]
    out_file = input_dir / f"site-{site}_sentinel-2-l2b.csv"
    if out_file.exists():
        print(f"Rasgos biofísicos para el obejto {site} ya extraída en {out_file}, omitiendo")
        continue

    print(f"Obteniendo rasgos biofísicos para el objeto {site}")
    biophysical_retrieval(lat, lon, l2a, out_file,
                          n_simulations=N_SIMULATIONS, n_jobs=N_JOBS)

print("Terminado con todas las tareas, puedes proseguir a la siguiente celda")
```

# Extraer tendencias y estacionalidad

Con los rasgos biofísicos ya generados y guardados en una tabla csv, podemos extraer la estacionalidad de los datos de manera similar a la práctica [301a](./301-ES_parametros_biofisicos.md)

+++

### Selecciona variable a procesar

```{code-cell} ipython3
w_var = widgets.Dropdown(
    options=OBJ_PARAM_NAMES,
    value='LAI',
    description='Variable:',
    tooltip="Selecciona rasgo biofísico a procesar")
display(w_var)
```

## Descomposición estacional de las extracciones

```{code-cell} ipython3
out_dir = aoi_data_dir / "output"

stl_kwargs = {"seasonal_deg": 0,
              "trend_deg": 0}

var = w_var.value
out_file = out_dir / f"zonal_trends_{var}.csv"

if not out_dir.is_dir():
    out_dir.mkdir(parents=True)

daily_dates = pd.to_datetime(pd.date_range(start_date, end_date, freq="D")).date
fig = go.Figure()
ts_dict = {"fid": [], "date": [], "values": [], "trend": []}
sites = sorted(list(input_dir.glob(f"site-*_sentinel-2-l2b.csv")))
for site in sites:
    fid = site.stem.split("_")[0].split("-")[-1]
    df_s2 = pd.read_csv(site, sep=";")
    df_s2["date"] = pd.to_datetime(df_s2["TIMESTAMP_UTC"]).dt.date
    daily_df = pd.DataFrame({"date": daily_dates})
    daily_df = daily_df.merge(df_s2, on="date", how="left")
    daily_df["date"] = pd.to_datetime(daily_df["date"])
    daily_df = daily_df.set_index("date")    
    # Interpolate to daily values
    daily_df = daily_df[w_var.value].interpolate(method='time').bfill()
    dates = daily_df.index.to_pydatetime().tolist()
    ts = MSTL(daily_df,
              periods=365, windows=5 * 365, iterate=5,
              stl_kwargs=stl_kwargs).fit()

    ts_dict["date"] += ts.trend.index.tolist()
    ts_dict["values"] += ts.observed.values.tolist()
    ts_dict["trend"] += ts.trend.values.tolist()
    ts_dict["fid"] += np.full_like(ts.observed.values, fid).tolist()
    fig.add_trace(go.Scatter(x=ts.trend.index, y=ts.trend.values, name=f"site-{fid}", mode="lines"))

ts_dict = pd.DataFrame(ts_dict)
ts_dict.to_csv(out_file, sep=";")
print(f"Guardadas las tendencias en {out_file}")
fig.update_layout(title_text=f"Tendencia anual para {var}", xaxis_title="Fecha", yaxis_title=var)
```

:::{hint} Consejo
Esta gráfica es interactiva, puedes acercar y alejar el zoom para ver más en detalle unas fechas en particular. También puedes navegar el cursor a lo largo de las curvas para visualizar los valores de cada punto de la curva.

También puedes guardar la figura en `png`.
:::

+++

# Ejercicio
1. Genera tu propia capa con los polígonos/rodales que quieras evaluar.
2. Extrae las series temporales de reflectividad y genera los rasgos biofísicos.
3. Evalúa las series temporales mediante la descomposición estacional
4. Genera un pequeño informe de 1-2 págines detallando conclusiones sobre las tendencias observadas
5. Exporta todo el cuaderno en formato pdf

## Entregables
* Informe de las series temporales y las tendencias obsevadas
* El cuaderno digital en formato pdf
