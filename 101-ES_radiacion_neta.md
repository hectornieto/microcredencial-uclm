---
title: Principios físicos en la interceptación y absprción de radiación
subject: Teoría 
subtitle: Cuaderno digital que muestra los procesos físicos de absorción de radiación por la vegetación
authors:
  - name: Héctor Nieto
    affiliation: 
      - Instituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0003-4250-6424
    email: hector.nieto@ica.csic.es
  - name: Benjamin Mary
    affiliation:
      - Instituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0003-0815-842X
label: nb-radiation
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

# Resumen
Este cuaderno digital interactivo tiene como objetivo evaluar las relaciones y procesos básicos entre la radiación incidente.

Para ello haremos uso de modelos de simulación, en particular de modelos de transferencia radiativa tanto a nivel de hoja individual como a nivel de dosel vegetal.

+++

# Instrucciones
Lee con detenimiento todo el texto, y sigue sus instrucciones.

Una vez leida cada sección de texto ejecuta la celda de código siguiente (marcada como `In []`) presionando el icono de `Run`/`Ejecutar` o presionando en el teclado ALT + ENTER. Aparecerá una interfaz gráfica con la que poder realizar las tareas asignadas.

Como ejemplo ejectuta la siguiente celda para importar todas  las librerías necesarias para el correcto funcionamiento del cuaderno. Una vez ejecutada debería aparecer un mensaje de agradecimiento.

```{code-cell} ipython3
%matplotlib inline
from ipywidgets import interact, interactive, fixed
from IPython.display import display
from functions import radiation_and_available_energy as fn
import numpy as np
```

# Ecuación básica
La evapotranspiración es básicamente un intercambio de energía y vapor de agua entre la superficie y la atmósfera. Es por ello que una variable fundamental para su cálculo es la estimación de la energía disponible de la superficie. 

:::{figure} ./input/figures/radiation_balance.png
:alt:The Earth energy balance
:name:fig-energy-balance
El balance de energía de la Tierra
:::
Seǵun el estado hídrico de la superficie, esta energía disponible es utilizada tanto en evaporar el agua (la ET o $\lambda E$) como en aumentar su temperatura ($H$).

:::{math}
\lambda E + H = R_n - G
:::

donde $G$ es el calor transmitido por conducción y almacenado en el suelo y $R_n$ es la radiación neta

La radiación neta ($R_n$) puede calcularse como:

:::{math}
R_n = S^\downarrow \left(1 - \alpha\right) +  \epsilon \left(L^\downarrow - \sigma LST^4\right)
:::

donde $S\downarrow$ y $L\downarrow$ son las radiaciones entrantes de onda corta y larga respectivamente y pueden obtenerse a través de estaciones o modelos meteorológicos, $\alpha$ y $\epsilon$ son el albedo y la emisividad del superficie, $LST$ es la temperatura de superficie, y $\sigma\approx5.67E-8$ (W/m²K⁴) es la constante de Boltzman. $\alpha$, $\epsilon$ y $LST$ pueden estimarse con mayor o menor grado de incertidumbre mediante datos y productos de teledetección.

Teniendo en cuenta la mayor magnitud de la radiación de onda corta ($S$) con respecto a la onda larga ($L$), en este cuaderno nos centraremos sobre todo a las propiedades del dosel vegetal que influyen en el albedo y en la fracción de radiación fotosintéticamente activa absorbida por la vegetación.

Por otro lado $G$ suele ser de menor magnitud, tendiendo a 0 cuando trabajamos en escalas diarias o más largas, o estimándose como una porcentaje de la radiación neta ($G \approx 0.1 R_n$ para supeficies vegetales densas; $G \approx 0.4 R_n$ para suelos desnudos) para escalas horarias o instantáneas.

+++

# La ley de Beer-Lambert
La ley de Beer-Lambert es la ley física fundamental que permite describir e interpretar la mayoría de los procesos y fenómenos radiativos que nos interesan. Cuando un haz de luz atraviesa un medio que contiene un elemento absorbente de radiación, esta luz se atenúa de manera proporcional a la concentración del elemento ($\kappa$) y la longitud del camino que recorre la luz ($\ell$). La transmisión de luz o de radiación electromagnética:

:::{math}
\tau = e^{-\kappa\ell}
:::

En el siguiente gráfico interactivo podrás ver el efecto de esta ley. 

Puedes modificar los valores de absorción $\kappa$, que aumenta cuanta mayor sea la concentración del material abosrbente en el medio. El gráfico mostrará el porcentaje de luz que se transmite a través del medio conforme su recorrido se va haciendo más largo:

```{code-cell} ipython3
w_lambert = interactive(fn.beer_lambert_law, kappa=fn.w_kappa, length=fixed(np.linspace(0, 10, 50)))
display(w_lambert)
```

Esta ley permite explicar por ejemplo la atenuación de la radiación solar desde la estratosfera hasta la superficie de la tierra: El aire está formado por gases y partículas que abosrben radiación (es más, la mayoría absorben sólo radiación en ciertas longides de onda, como es el ozono que abosrbe rayos UV). Cuanto más alto esté el sol en el cielo, el recorrido a través de la atmósfera es menor y por tanto la radiación solar que nos llega a la superficie será mayor.
:::{figure} ./input/figures/airmass.png
:alt:Sun optical path length
:name:fig-path-length
The camino óptico del sol en una esfera (la Tierra) y su simplificación planar
:::

+++

## Aplicación a la Fracción de Radiación Interceptada (fIPAR)
La ley de Beer-Lambert nos permite también analizar la interceptación (y absorción) de radiación del dosel vegetal y equivalentemente la radiacion que finalmente llega al suelo.

Asumiendo que un dosel vegetal está formado en su mayoría por hojas, y que éstas interceptan y absorben radiación (sobre todo radiación fotosintéticamente activa, PAR), podemos ver cuánta radiación es inteceptada según la cantidad de hojas o la densidad foliar del dosel. Ésta suele definirse mediante el Índice de Área Foliar (LAI), la superficie de hojas por unidad de superficie de suelo. Cuanto mayor sea el LAI más probabilidades hay de que los rayos solares sean interceptados por la vegetación, y por tanto lleguen menos al suelo. De igual modo, el ángulo de elevación solar $\beta$, o su complemntario el ángulo zenital solar (SZA), juega también un papel importante, ya que cuanto más bajo esté el sol máyor camino tendrá que recorrer la luz a través del dosel y mayor será su atenuación. 

Como las hojas son elementos sólidos con un tamaño finito (al contrario que los gases atmosféricos), su orientación con respecto a la vertical también juega un rol importante, por lo que la ley de Beer-Lambert ha de modificarse para reflejar este fenómeno. En el siguiente gráfico puedes experimentar con este efecto. Puedes variar tanto la cantidad de hojas (en términos de LAI) como la orientación dominante de las hojas, desde hojas predominantemente verticales ($\approx$90º) a hojas predominantemente horizontales ($\approx$0º).

```{code-cell} ipython3
w_fipar = interactive(fn.plot_fipar, lai=fn.w_lai, leaf_angle=fn.w_leaf_angle)
display(w_fipar)
```

Observa en el gráfico cómo las mayores atenuaciones de la luz (o lo que es lo mismo mayor fracción interceptada de radiación) ocurren siempre con ángulos de elevación solar menores, pero que esa tasa de atenuación depende en mayor medido de la cantidad de hojas y de su disposición angular.

El LAI depende en gran medida del desarrollo fenológico y del aumento de biomasa de la planta, mientras que su disposición angular suele ser específica de la especie, habiendo plantas con una disposición más erectófila (hojas predominantemente verticales) como pueden ser algunas gramíneas y plantas con una disposición más planófila (hojas predominantemente horizontales. Generalmente podemos asumir que especies erectófilas están más adaptadas a sobervivir en climas con altos niveles de insolación, con el fin de evitar condiciones extremas de irradiancia solar en las horas centrales del día, mientras que plantas planófilas tienen a desarrollarse en condiciones más de penumbra o de poca exposición, de manera que intercepten el máximo posible de radiación durante todo el día. 

Entre esos dos extremos la mayoría de las plantas presentan una diposición angular de las hojas más o menos aleatoria. Para estos casos el cálculo de la interceptación de radiación se simplifica como:

:::{math}
fIPAR = 1 - \exp \left(\frac{-0.5 LAI}{\cos\theta_s}\right)
:::
siendo $\theta_s$ el ángulo zenital solar.

:::{seealso} Ver también
Si tienes interés en cómo realizar los cálculos para cualquier otro tipo de disposición angular de las hojas y tienes conocimientos de programación, picha [aquí](https://github.com/hectornieto/pyTSEB/blob/6dd5dffff08bc1f08edb3e89b4a79879e348146b/pyTSEB/TSEB.py#L1587)
:::

+++

# El albedo
Como hemos comentado anteriormente el albedo ($\alpha$) es la variable fundamental que determina la cantidad de radiación solar que es absorbida por la superficie. Se definie como la proporción de radiación de onda corta que es reflejada por la superficie. La radiación neta de onda corta es un balance entre la radación de onda corta incidente ($S\downarrow$) y la saliente o reflejada ($S\uparrow = \alpha S\downarrow$)

Las propiedades espectrales de la superficie terrestre son claves en la determinación de su albedo, por ejemplo la nieve tiene valores muy altos de albedo ($\approx 0.9$), y por tanto reflejan la mayoría de la radiación solar. Los océanos por el contrario tienen valores muy bajos de albedo ($\approx0.05$) por lo que aborben la mayoría de la energía solar que les llega. 

Las hojas, debido a la actividad fotosinténtica absorben una gran proporción luz por parte de las clorofilas y otros pigmentos, es por ello que también presentan valores relativamente bajos de albedo ($\approx0.15$). Por otro lado, el suelo según su composición mineralógica puede tener valores de albedo entre 0.20 y 0.40 o incluso más. Por tanto el albedo de un dosel vegetal dependerá sobre todo de la concentración de clorofilas de sus hojas pero también de la cantidad o densidad foliar del dosel, luego en menor medida del albedo del suelo, pero sólo en situaciones de escasa vegetación o estados fenológicos iniciales.

:::{note}
Profundizaremos más sobre este tema en la sesión sobre el [comportamiento espectral de la vegetación][.102-ES_espectro_vegetación.ipynb].
:::

## Anisotropía de la vegetación
La mayoría de las superficies terrestres presentan cierta anisotropía a la hora de reflejar la radiación. Es decir, reflejan más radiación en unas direcciones que en otras. El caso más extremos son las superficies especulares (espejos y algunas láminas de agua y hielo) que reflejan la mayoría de la radiación en la dirección contraria a la posición del sol. El caso contrario son las superficies lambertianes, las  cuales dan la aparencia de reflejar por igual en todas las direcciones.

:::{figure} ./input/figures/lambertian_and_specular_reflection.png
:alt:Lambertian and specular scattering
:name:fig-anisotropy
Reflexión Lambertiana (flechas de trazo fino) y dispersión especular (flecha de trazo grueso)
:::

:::{note} Nota
La madera sin pulir es un ejemplo superficie lambertiana, mientras que la madera pulida y barnizada presenta por el contrario comportamientos especulares 
:::

La vegetación, al estar formada prinpicalmente de un cojunto más o menos agrupado de hojas, no se libra de este comportamieno anisotrópico, que provoca que según las geometría de iluminación, es decir según al posición del sol, refleja de manera distinta según la dirección, e incluso pueda variar el albedo global.

En el siguiente gráfico podrás ver este efecto. Se trata de un gráfico polar que simula la reflectividad de una superficie vegetal en todas direcciones, tanto para la región del PAR como para todo el espectro solar. Los anillos concéntricos representan los distintos ángulos cenitales con respecto al nadir (0 para el punto central del gráfico y 90º para el anillo más externo). Las radiales del gráfico polar representa la dirección azimultal (0º hacia el Norte, 90º hacia el Este, 180º hacia el Sur y 270º hacia el Oeste). Tambien se muestra el valor integrado de la reflectividad, que reulta en el albedo.

La posición del sol está representada en el gráfico por una estrella. Por defecto al ejecutar el gráfico el sol está situado al sur con un ángulo cenital de 37 grados, lo que implica un día tipico de verano en el hemisferio Norte al mediodía.

```{code-cell} ipython3
w_bidirectional = interactive(fn.bidirectional_reflectance,
                              cab=fn.w_cab, cw=fn.w_cw, lai=fn.w_lai, leaf_angle=fn.w_leaf_angle, 
                              sza=fn.w_sza, saa=fn.w_saa, skyl=fn.w_skyl, soil_type=fn.w_soil)
display(w_bidirectional)                              
```

* Modifica sustancialmente la concentración de clorofila. ¿Cómo varía la reflectividad y el albedo tanto en el PAR como en el espectro completo solar?
* Modifica la posición del sol. Por un lado podrás ver que siempre hay un pico de reflectividad alrededor de la posición solar. Esto se trata del la zona de la vegetación que está más illuminada por el sol. Por el contrario, en la dirección opuesta se ecuentran los valores de reflectividad menores, al estar las hojas más ocluidas de los rayos de sol. Además los valores de albedo también varían según la posición del sol, es decir, según la hora del día.
* Esta variación es más significativa cuanta menor sea la proporción de radiación difusa. Aumenta la proporción de radación difusa, simulando días con mayor cobertura nubosa, verás que la posición del sol, como es de esperar ya no es relevante.

+++

# Radiación neta de onda corta en un dosel
Teniendo en cuenta lo visto hasta hora, el LAI, la distribución angular de las hojas la concentración de colorofila son las variables fundamentales que determinan la abosorción de radiación del cultivo. En el siguiente gráfico podemos ver la evolución de la radiación solar neta de un cultivo herbáceo ($C_{a+b}\approx40\mu g/cm^2$} a lo largo un día típico de verano para una latitud dada (independientemente de que sea el hemisferio Sur o Norte). Este gráfico asume que las condiciones de nubosidad permanecen constantes durante el día, con una proporción de radiación difusa fija, y por tanto la evolución de radiación incidente presenta una curva sinusoidal. Si las condiciones de nubosidad fueran cambiantes la curva presentaría una forma más aserrada, formando valles y crestas en los momentos en los que el sol estuviese visible u oculto tas las nubes.

El gráfico muestra tanto la radiación neta de onda corta de la superficie (curva de color negro, $S_n$) como el reparto de esa radiación entre la radiación absorbida por el cultivo (en verde, $S_{n,C}$) como el suelo (en amarillo, $S_{n,S}$)

::::{important} Importante
En estas simulaciones asumimos una proporción constante entre la radiación directa y la difusa (determinada por la variable `Skyl`). Esto no es realista en la mayoría de los casos, ya que debido a la distinta dispersión atmosférica (principalmente aerosoles) la proporcion de radiación difusa incrementa a longitudes de onda más cortas. 
:::{hint} Curiosidad
Es por esto que el cielo es azul durante el día
:::

Por simplifidad en este caso asumimos que la proporción entre radiación directa y difusaBut for simplicity in these simulations, we made this assumption.
::::


:::{math}
S_{n,C}+S_{n,S}=S_n\\
\alpha = 1 - S_n/S\downarrow
:::

```{code-cell} ipython3
w_sn = interactive(fn.plot_net_solar_radiation,
                   lai=fn.w_lai, leaf_angle=fn.w_leaf_angle, h_c=fixed(1), f_c=fixed(1),
                   sdn_day=fn.w_sdn,
                   row_distance=fixed(1), row_direction=fixed(1), skyl=fn.w_skyl, 
                   fvis=fixed(0.55), lat=fn.w_lat, cab=fn.w_cab, cw=fn.w_cw, soil_type=fn.w_soil)
display(w_sn)
```

:::{important} Importante
Todos los parámetros de todos los gráficos usados en este cuaderno están sincronizados: cualquier cambio de una variable en uno de los gráficos interactivos también cambia para los otros gráficos, actualizando todos los gráficos en consecuencia. Esto permite una rápida intercomparación entre gráficos y simulaciones.
:::

Observa que al forzar la clorofila constante, las variaciones de radiación neta son apenas perceptibles con variaciones de LAI. Sin embargo el reparto de radiación entre el suelo y la vegetación varían considerablemente con el LAI. Esto tiene implicaciones importantes ya que el LAI influye en el reparto de energía entre suelo y vegetación y por lo tanto en la capacidad de la superficie de evaporar el agua del suelo y/o la capacidad transpirativa y fotosintética del cultivo.

Mantén valores relativavente bajos de LAI ($<$1.5) y observa de nuevo el efecto de la distribución angular de las hojas en el dosel. Hojas más verticales (`Leaf Angle`\approx$90) provocarían una disminución de la radiación absorbida por la vegetación en las horas centrales del día, cuando el sol está más elevado y la irradiancia solar es mayor. Observa que este efecto sin embargo ya no ocurre cuando hay una mayor proporción de radiacion difusa. En ese caso casi toda la radiaicón viene indistintamente de todas direcciones y por tanto la distribución angular de la hoja no juega un papel importante.

+++

# La radiación neta de onda larga
La radiación de onda larga corresponde a la emisión y absorción de energía proveniente del calor propio de la atmósfera y la superficie. La emisión de energía de un cuerpo depende de su temperatura interna y de la emisividad del mismo. Por tanto, en este caso la radiación neta de onda larga viene determinada por la emisividad y temperatura atmosférica y la emisividad y temperatura de la superficie.

:::{math}
L_n = \left(1 - \epsilon_{surf}\right) L\downarrow - \epsilon_{surf} \sigma T_{surf}^4
:::

Este gráfico muestra cómo varia la radiación neta de onda larga en función de las condiciones atmosféricas (temperatura y humedad relativa) y de la temperatura de la superficie y su emisividad. Ya que la temperatura de superficie depende en cierto grado también de las condiciones atmosféricas, asi como del estado hídrico del cultivo, vamos a mostrar cómo cambia $L_n$ a distintos niveles de estrés hídrico, desde un cultivo bien hidratado en el que su temperatura de superficie está en torno a la temperatura del aire, hasta un cultivo estresado, donde su temperatura está significativamente varios grados por encima de la temperatura del aire.

:::{attention} Atención
En estas prácticas trabajaremos con el sistema internacional de medidas para las temperaturas (Kelvin). Para convertin Kelvin a grados Celsius tan sólo tienes que restar 273 (273 K = 0ºC y 293K = 20ºC)
:::

```{code-cell} ipython3
w_ln = interactive(fn.plot_longwave_radiation, t_air=fn.w_tair, hr=fn.w_hr, delta_t=fixed(np.linspace(-1, 20, 50)),
                   emiss=fn.w_emiss)
display(w_ln)
```

Podrás observar que la radiación neta de onda larga suele resultar en valores significativamente menores que la radiación neta de onda corta. Sólo en casos de muy altas temperaturas y mucha humedad la radiación neta de onda larga excede los 400 W/m².

Además la radiación neta disminuye según aumenta el nivel de estrés del cultivo (es decir a mayores diferencias entre su temperatura y la temperatura del aire). Esto es uno de los dos mecanismos que permiten al cultivo regular su exceso de calor. Al aumentar su temperatura emite más energía radiante, lo que produce un efecto de retroalimentación para liberar el exceso de calor.

:::{seealso} Ver también
La otra estrategia está relacionada con el flujo de calor sensible y la disipación de exceso de energía por convección. Este fenómeno lo veremos en la práctica de mañana sobre el [calor sensible y la turbulencia](./102-ES_turbulencia_y_calor_sensible.ipynb)
:::

Finalmente la emisividad de la superficie, la cual suele estar en torno a valores de 0.95 para zonas áridas y con escasa vegetación a valores de 0.99 para vegetación densa, tiene un efecto menor en el cálculo de la radiación neta. Por lo que su estimación no requiere de gran precisión.

+++

# Conclusiones
En esta práctica hemos visto que la radiación neta de onda corta depende principalmente de:
1. la radiacíón incidente, la cual puede obtenerse a partir de estaciones o modelos meteorológicos (p.ej. [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)).
2. El albedo de la superficie

Por otro lado el albedo depende principalmente de
1. Las propiedades espectrales de la vegetación, principalmente la clorofila como principal pigmento absorbente de radiación PAR.
2. Las propiedades estructurales de la vegetación, principalmente el LAI pero también de la distribución angular de la hoja. Además en cultivos en hilera la estructura de la hilera puede resultar determinante en el reparto de radiaicón entre suelo y vegetación.

La radiación neta de onda larga tiene un mayor peso en la radiación neta global, y además su modelización suele resultar más sencilla, necisitando
1. la radiacíón incidente de onda larga, la cual puede obtenerse a partir de estaciones o modelos meteorológicos (p.ej. [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
2. La emisividad y temperatura de superficie, que pueden otenerse mediante datos de teledetección.

Los análisis realizados te permitirán además poder evaluar el coste/beneficio de usar modelos más o menos complejos a la hora de estimar las radiación neta y el reparto de energía en cultivos complejos.

En prácticas futuras veremos cómo estimar el albedo y las otras propiedades biofísicas de la vegetación a partir de datos de teledetección.

:::{tip} ¿Preguntas?
¿Algún comentario?
:::
