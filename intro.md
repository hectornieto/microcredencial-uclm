---
title: Microcredencial en Inteligencia Artificial y Tecnologías Geoespaciales aplicadas a la Restauración de Ecosistemas Forestales afectados por incendios y sequías extremas
subject: Microcredencial
subtitle: Teledetección aplicada a la restauración de espacios naturales
short_title: Teledetección
authors:
  - name: Héctor Nieto
    affiliations:
      - Insituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0003-4250-6424
    email: hector.nieto@ica.csic.es
  - name: María Burguet Marimón
    affiliation: 
      - Instituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0002-9748-8078 
  - name: Benjamin Mary
    affiliations:
      - Insituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0001-7199-2885

license: CC-BY-SA-4.0
keywords: myst, markdown, open-science, tseb
---

# Introducción
Este libro digital (*Jupyter Notebook*) contiene el material online necesario para cursar la parte `Teledetección aplicada a la restauración de espacios naturales` de la `Microcredencial en Inteligencia Artificial y Tecnologías Geoespaciales aplicadas a la Restauración de Ecosistemas Forestales afectados por incendios y sequías extremas`.

Puedes acceder at todo el contenido interactivo a través de este línk [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hectornieto/microcredencial-uclm/HEAD)

# Registro en servicios gratuitos
Para poder acceder a los datos Copernicus (imágenes Sentinel, datos meteorológicos del ECMWF y otros productos auxiliares) debes registrarte en las siguientes plataformas:

* Copernicus Data Space Ecosystem: [](https://dataspace.copernicus.eu/)
* European Center for Medium-Range Weather Forecast: [](https://www.ecmwf.int/user/login)
* `Opcional pero recomendado` CDSE JupyterHub: [](https://jupyterhub.dataspace.copernicus.eu/hub)
* `Opcional` OpenEO platform: [](https://docs.openeo.cloud/join/free_trial.html)

# Temario
:::{include} ./microcredencial-UCLM_curriculum.md

:::

# Entregables
Cada estudiante delimitará una o varias zonas de interés donde ejecutarán los cudadernos digitales de la sesión práctica [](dia-3.md). 

Para el caso prácico `1` el alumnado podrá escoger entre generar imágenes mensuales o extraer series temporales (o ambas).

* Pequeño informe (1-2 páginas) con los resultados y conclusiones más relevantes de cada una de las dos prácticas.
* Exporta cada uno de los cuadernos digitales en formato `pdf` y entrégalos junto con el informe.

# Instalación en local
En caso de que quieras instalar el material en tu ordenador personal:

:::{tip} Requisitos previos - Instalar Python
:class: dropdown

Debes tener los siguientes programas instalados:
* Python y/o [Anaconda](https://www.anaconda.com/download/success). 
* [Git](https://git-scm.com/downloads)
:::

## Instala todas las librerías requeridas

Abre un terminal y navega a la carpeta donde hayas descargado `microcredencial-UCLM`:

(navigation)=
:::::{tab-set}
::::{tab-item} Windows
:sync: win
1. Abre `Anaconda Prompt Terminal` 
2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
```{code} bash
cd C:\Users\<user>\Downloads\microcredencial-UCLM
```
::::
::::{tab-item} Linux
:sync: linux
1. Abre un terminal (p.ej. teclea `CTRL+ALT+T`)
2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
```{code} bash
cd /home/<user>/downloads/microcredencial-UCLM
```
::::
:::::

Instala los requisition bien con pip o crea un ambiente virtual con `conda/mamba` (recomendado)

(requirements)=
:::::{tab-set}
::::{tab-item} Pip
:sync: pip
```{code} bash
pip install ./
```
::::
::::{tab-item} Conda/Mamba
:sync: conda
```{code} bash
mamba env create -f environment.yml
conda activate uclm
```
::::
:::::

## Ejecuta el libro digital
:::::{tab-set}
::::{tab-item} Windows
:sync: win
1. Abre `Anaconda Prompt Terminal` 
2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
```{code} bash
cd C:\Users\<user>\Downloads\microcredencial-UCLM
```
3. Teclea y ejecuta este comando
```{code} bash
jupyter book start
```
::::
::::{tab-item} Linux
:sync: linux
1. Abre un terminal (p.ej. teclea `CTRL+ALT+T`)
2. en ese terminal navega a la carpeta `microcredencial-UCLM`:
```{code} bash
cd /home/<user>/downloads/microcredencial-UCLM
```
3. Teclea y ejecuta este comando
```{code} bash
jupyter book start
```
::::
:::::

Abre tu navegador esta URL: [`http://localhost:3000`](http://localhost:3000)



# Licencia
Creative Commons Attribution-ShareAlike 4.0 International.

This work is licensed under Attribution-ShareAlike 4.0 International. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

This license requires that reusers give credit to the creator. It allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, even for commercial purposes. If others remix, adapt, or build upon the material, they must license the modified material under identical terms.

  - BY: Credit must be given to you, the creator.
  - SA: Adaptations must be shared under the same terms. 
