# Sesión 3: Prácticas

En esta sesión los estudiantes utilizarán herramientas de código abierto y libre para generar información relevante que pueda ser utilada para evaluar el estado de la vegetación y/o las prácticas de restauración que hayan sido aplicadas.

## Requisitos previos

### Registro en servicios gratuitos
Para poder acceder a los datos Copernicus (imágenes Sentinel, datos meteorológicos del ECMWF y otros productos auxiliares) debes registrarte en las siguientes plataformas:

* Copernicus Data Space Ecosystem: [](https://dataspace.copernicus.eu/)
* European Center for Medium-Range Weather Forecast: [](https://www.ecmwf.int/user/login)
* `Opcional pero recomendado` CDSE JupyterHub: [](https://jupyterhub.dataspace.copernicus.eu/hub)
* `Opcional` OpenEO platform: [](https://docs.openeo.cloud/join/free_trial.html)

### Instalación en el JupyterHub del Ecosistema de Datos Copernicus [Recomendado]
Al ejecutarse en el [entorno JupyterHub de CDSE](https://jupyterhub.dataspace.copernicus.eu), las descargas de datos se minimizan, ya que los datos y el cómputo se encuentran en la misma infraestructura de nube.

1. Accede a [https://jupyterhub.dataspace.copernicus.eu](https://jupyterhub.dataspace.copernicus.eu) e inicia un servidor.
2. En el servidor, sube los cuadernos manualmente o clona este repositorio abriendo una terminal y ejecutando:
    ```
    git clone https://github.com/hectornieto/microcredencial-uclm.git mystorage/microcredencial
    ```
    
3. Instala todas las librerías requeridas usando los siguientes comandos en una terminal
    ```bash
    cd mystorage/microcredencial
    conda activate geo    
    pip install -r requirements.txt
    ```  
4. Ejecuta los cuadernos usando un kernel que tenga GDAL instalado, p. ej. *Geo science*. Este paquete se instala en la primera celda de los cuadernos.

:::{warning} Aviso
 Deberías poder ejecutar los cuadernos sin ninguna configuración adicional si usas un kernel con GDAL instalado, pero a veces pueden surgir conflictos con paquetes existentes en el entorno. En ese caso, se recomienda hacer una instalación limpia del kernel siguiendo los pasos a continuación.
1. Crea un nuevo kernel limpio usando los siguientes comandos en una terminal de Jupyterhub:
    ```
    conda create -n gdal_env python=3.11 \
    conda activate gdal_env \
    conda install -c conda-forge gdal \
    pip install senet_toolbox@git+https://github.com/DHI/Sen-ET-OpenEO-toolbox.git \
    python -m ipykernel install --user --name=gdal_env --display-name "Sen-ET Kernel" 
    ```
2. Ahora puedes seleccionar el kernel "Sen-ET Kernel" para ejecutar los cuadernos.
:::


### Instalación en local [Opcional]
En caso de que quieras instalar el material en tu ordenador personal debes tener los siguientes programas instalados:

* Python y/o [Anaconda](https://www.anaconda.com/download/success). 
* [Git](https://git-scm.com/downloads)

Y seguir las instrucciones descritas en [](./intro.md)

## Temario    
1. Caso práctico: Extracción de información temporales de rasgos biofísicos

    * [Generación de imágenes mensuales de rasgos biofísicos](./301a-ES_parametros_biofisicos.ipynb)
    * [Generación de series temporales de rasgos biofísicos](./301b-ES_parametros_biofisicos.ipynb)
    
2. [Caso práctico: Estimación de ET fusionando imágenes Sentinel](./302-ES_SenET-OpenEO.ipynb)

3. [Caso práctico: Evaluación de la severidad de un incencio forestal](./303-ES_Severidad.ipynb)

## Ejercicio
Cada estudiante delimitará una o varias zonas de interés donde ejecutarán los cudadernos digitales. Para el caso práciico 1 el alumnado podrá escoger entre generar imágenes mensuales o extraer series temporales (o ambas).

### Entregables
* Pequeño informe (1-2 páginas) con los resultados y conclusiones más relevantes de cada una de las dos prácticas.
* Exporta cada uno de los cuadernos digitales en formato `pdf` y entrégalos junto con el informe.
