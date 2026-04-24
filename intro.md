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
Este repositorio contiene el material online necesario para ejecutar los cuadernos digitales (**Jupyter Notebook**) desarrollados para el curso.


# Instalación en local
En caso de que quieras instalar el material en tu ordenador personal:

:::{tip} Requisitos previos - Instalar Python
:class: dropdown

Debes tener los siguientes programas instalados:
* Python y/o [Anaconda](https://www.anaconda.com/download/success). 
* [Git](https://git-scm.com/downloads)
:::

## Instala todas las librerías requeridas:

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


# Contenido
:::{include} ./microcredencial-UCLM_curriculum.md

:::

# Licencia
Creative Commons Attribution-ShareAlike 4.0 International.

This work is licensed under Attribution-ShareAlike 4.0 International. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

This license requires that reusers give credit to the creator. It allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, even for commercial purposes. If others remix, adapt, or build upon the material, they must license the modified material under identical terms.

  - BY: Credit must be given to you, the creator.
  - SA: Adaptations must be shared under the same terms. 
