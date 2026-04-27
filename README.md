# Microcredencial en Inteligencia Artificial y Tecnologías Geoespaciales aplicadas a la Restauración de Ecosistemas Forestales afectados por incendios y sequías extremas: Teledetección aplicada a la restauración de espacios naturales

## Introducción
Este repositorio contiene el material online necesario para ejecutar los cuadernos digitales (**Jupyter Notebook**) desarrollados para el curso.

No necesitas instalar nada, tan sólo accede a la aplicación [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hectornieto/microcredencial-uclm/HEAD) para ejecutar y visualizar los cuadernos digitales


## Temario

1. Rasgos biofísicos de la vegetación asociado a la interceptación y absorción de radiación (2.5 horas).
    
    1. [Principios físicos](./101-ES_radiacion_neta.md)
    2. [Uso de modelos de transferencia radiativa para la estimación de parámetros biofísicos](./102-ES_espectro_vegetacion.md)
 
2. Importancia de la temperatura de la superficie para el seguimiento de la evapotranspiración y el estrés hídrico (2 horas)
    
    1. [Intercambio de calor y agua en el Continuo Suelo-Planta-Atmósfera](./201-ES_turbulencia_y_calor_sensible.md)

3. Ejercicios (2 horas)

    1. Caso práctico: Extracción de información temporales de rasgos biofísicos
        * [Generación de imágenes mensuales de rasgos biofísicos](./301a-ES_parametros_biofisicos.ipynb)
        * [Generación de series temporales de rasgos biofísicos](./301b-ES_parametros_biofisicos.ipynb)
    2. [Caso práctico: Estimación de ET fusionando imágenes Sentinel](./302-ES_SenET-OpenEO.ipynb)

## Instalación en local
En caso de que quieras instalar el material en tu ordenador personal debes tener los siguientes programas instalados:

* Python y/o [Anaconda](https://www.anaconda.com/download/success). 
* [Git](https://git-scm.com/downloads)

### Instala todas las librerías requeridas:

Abre un terminal y navega a la carpeta donde hayas descargado `microcredencial-UCLM`:

* En Windows
    1. Abre `Anaconda Prompt Terminal` 
    2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
    ```{code} bash
    cd C:\Users\<user>\Downloads\microcredencial-UCLM
    ```

* En Linux
    1. Abre un terminal (p.ej. teclea `CTRL+ALT+T`)
    2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
    ```{code} bash
    cd /home/<user>/downloads/microcredencial-UCLM
    ```

Instala los requisition bien con pip o crea un ambiente virtual con `conda/mamba` (recomendado)

* pip
```{code} bash
pip install ./
```

* conda
```{code} bash
mamba env create -f environment.yml
conda activate uclm
```


### Ejecuta el libro digital
* En Windows
    1. Abre `Anaconda Prompt Terminal` 
    2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
    ```{code} bash
    cd C:\Users\<user>\Downloads\microcredencial-UCLM
    ```
    3. Teclea y ejecuta este comando
    ```{code} bash
    jupyter book start
    ```
* En Linux
    1. Abre un terminal (p.ej. teclea `CTRL+ALT+T`)
    2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
    ```{code} bash
    cd /home/<user>/downloads/microcredencial-UCLM
    ```
    3. Teclea y ejecuta este comando
    ```{code} bash
    jupyter book start
    ```

Abre con tu navegador esta URL: [`http://localhost:3000`](http://localhost:3000)



## Licencia
Creative Commons Attribution-ShareAlike 4.0 International.

This work is licensed under Attribution-ShareAlike 4.0 International. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

This license requires that reusers give credit to the creator. It allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, even for commercial purposes. If others remix, adapt, or build upon the material, they must license the modified material under identical terms.

  - BY: Credit must be given to you, the creator.
  - SA: Adaptations must be shared under the same terms. 
