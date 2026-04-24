---
title: Spectral properties and biophysical traits 
subject: Tutorial
subtitle: Use of PROSPECT-D and 4SAIL for estimating biophysical traits for TSEB
short_title: ProSAIL
authors:
  - name: Héctor Nieto
    affiliations:
      - Instituto de Ciencias Agrarias, ICA
      - CSIC
    orcid: 0000-0003-4250-6424
    email: hector.nieto@ica.csic.es
  - name: Benjamin Mary
    affiliations:
      - Insituto de Ciencias Agrarias
      - CSIC
    orcid: 0000-0001-7199-2885
label: nb-prosail
license: CC-BY-SA-4.0
keywords: TSEB, radiation, LAI, leaf pigments
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

# Summary
This interactive digital notebook aims to demonstrate the relationships between the physicochemical properties of vegetation and the solar spectrum.

To do so, we will use simulation models, particularly radiative transfer models both at the level of individual leaves and at the canopy level.

# Instructions
Read all the text carefully and follow its instructions.

Once you have read each section of text, run the following code cell (marked as `In []`) by clicking the `Run` icon or pressing ALT + ENTER on your keyboard. A graphical interface will appear allowing you to perform the assigned tasks.

As an example, run the following cell to import all the libraries required for the proper functioning of the notebook. Once executed, a thank‑you message should appear.


```{code-cell} ipython3
%matplotlib inline
from ipywidgets import interactive, fixed
from IPython.display import display
from functions import prosail_and_spectra as fn
```

# Leaf Spectrum
The spectral properties of a leaf (its transmittance, reflectance, and absorptance) depend on its pigment concentration, water content, specific dry weight, and the internal structure of its tissues.

We will use the ProspectD model, which is a simplified representation of reality that simulates the spectrum based on the concentration of chlorophylls (`Cab`), carotenoids (`Car`), anthocyanins (`Ant`), as well as the water content per unit area (`Cw`) and the dry matter content (`Cm`), which includes cellulose, lignin (main components of leaf biomass), and other protein components. It also includes a semi‑empirical parameter representing other pigments responsible for the color of senescent or diseased leaves. Additionally, to simulate leaves with different cellular structures, it includes a final parameter (`Nf`) that emulates the different layers and tissues of the leaf.

![Prospect model diagram](./input/figures/prospect.png "Schematic representation of the Prospect model. The leaf is represented by a number of layers (N ≥ 1) with identical spectral properties")

:::{seealso}
If you want to learn more about the ProspectD model refer to [Féret et al (2017)](https://doi.org/10.1016/j.rse.2017.03.004).
:::

:::{seealso}
If you want more details about the calculations and code of the model, click [here](https://github.com/hectornieto/pypro4sail/blob/b111891e0a2c01b8b3fa5ff41790687d31297e5f/pypro4sail/prospect.py#L46).
:::
Run the following cell to see a typical leaf spectrum. The graph shows reflectance (on the y‑axis), transmittance (on the secondary y‑axis, inverted), and absorptance (as the space between the reflectance and transmittance curves), where ρ + τ + α = 1.

Pay attention to how and in which regions the spectrum changes depending on the parameter you modify.

* Vary the chlorophyll content.
* Vary the water content.
* Vary the dry matter content.
* Vary the brown pigments from 0 (healthy leaf) to higher values (diseased or dry leaf).

```{code-cell} ipython3
w_rho_leaf = interactive(fn.update_prospect_spectrum, N_leaf=fn.w_nleaf, Cab=fn.w_cab, 
                         Car=fn.w_car, Ant=fn.w_ant, Cbrown=fn.w_cbrown, Cw=fn.w_cw, Cm=fn.w_cm)
display(w_rho_leaf)
```

Observe the following:
* Chlorophyll concentration (`Cab`) mainly affects the visible region (RGB) and the red‑edge (R‑E), with more absorption in the red and blue and more reflection in the green.
* Water content (`Cw`) mainly affects absorption in the shortwave infrared (SWIR), with absorption peaks around 1460 and 2100 nm.
* Dry matter (`Cm`) mainly affects absorption in the near‑infrared (NIR).
* Other pigments affect the visible spectrum to a lesser extent. For example, anthocyanins (`Ant`) shift the green reflectance peak toward the red, especially when chlorophyll decreases.
* The parameter `N` affects the relationship between reflectance and transmittance. More layers → more multiple scattering → higher reflectance.

:::{note}
This phenomenon can also be seen in double or triple‑glazed windows used as insulation. Unless viewed straight on, they appear more like mirrors than windows.
:::

+++

# Soil Spectrum
The spectrum of a canopy or vegetated surface depends not only on the spectrum and properties of the leaves but also on the canopy structure and the soil. In open or sparse canopies, such as early phenological stages, the soil’s spectral behavior can strongly influence the spectral signal captured by remote sensing sensors.

The soil spectrum depends on several factors, such as mineral composition, organic matter, texture, density, and surface moisture.

Run the following cell and observe the different spectral characteristics of various soil types.

```{code-cell} ipython3
w_rho_soil = interactive(fn.update_soil_spectrum, soil_name=fn.w_soil)
display(w_rho_soil)
```

Observe how different a soil spectrum can be compared to that of a leaf. This is key when classifying land cover types using remote sensing and when quantifying vegetation vigor or density.

Notice that more saline (`aridisol.salorthid`) or gypsiferous (`aridisol.gypsiorthd`) soils have higher reflectance, especially in the visible (RGB). In other words, they appear whiter than other soils.

# Canopy Spectrum
By integrating the spectral signature of a leaf and the underlying soil, we can obtain the spectrum of a vegetation canopy.

The surface spectrum also depends on canopy structure, mainly the Leaf Area Index (LAI) and the orientation of the leaves. Additionally, because incident and reflected light interact within the leaf–soil volume, the position of the sun and the sensor influences the spectral signal.

We combine the ProspectD leaf model with the 4SAIL canopy radiative transfer model. This model assumes a horizontally and vertically homogeneous canopy, so caution is advised when applying it to heterogeneous tree canopies.

:::{figure}./input/figures/4sail.png
:alt:4SAIL model diagram
:name:fig-4sail
Schematic representation of the 4SAIL model. Source: [Verhoef et al. (2007)](10.1109/TGRS.2007.895844) 
:::

:::{seealso}
If you want to learn more about the 4SAIL model, refer to [Verhoef et al. (2007)](10.1109/TGRS.2007.895844).
:::

:::{seealso}
For more details about the calculations and code, click [here](https://github.com/hectornieto/pypro4sail/blob/b111891e0a2c01b8b3fa5ff41790687d31297e5f/pypro4sail/four_sail.py#L245).
:::
Run the following cell to see how the previously generated leaf and soil spectra combine to produce a canopy spectrum.

:::{note}
You can modify the leaf and soil spectra, and this graph will update automatically.
:::

```{code-cell} ipython3
w_rho_canopy = interactive(fn.update_4sail_spectrum,
                           lai=fn.w_lai, hotspot=fn.w_hotspot, leaf_angle=fn.w_leaf_angle, 
                           sza=fn.w_sza, vza=fn.w_vza, psi=fn.w_psi, skyl=fn.w_skyl, 
                           leaf_spectrum=fixed(w_rho_leaf), soil_spectrum=fixed(w_rho_soil))
display(w_rho_canopy)
```

Remember from the net radiation exercise that a vegetated surface has anisotropic properties, meaning it reflects differently depending on illumination and viewing geometry.

Observe how the spectrum changes when varying the viewing zenith angle (VZA), solar zenith angle (SZA), and relative azimuth angle (PSI).

Set LAI to zero (no vegetation). The resulting spectrum should match the soil spectrum. Increase LAI slightly and observe how reflectance decreases in the red and blue (due to chlorophyll) and increases in the red‑edge and NIR.

Also examine the effect of leaf angular distribution. With nadir viewing (VZA = 0), vary the typical leaf angle from horizontal (0°) to vertical (90°).

# Parameter Sensitivity
In this task, you can explore how the vegetation spectrum responds to changes in physicochemical parameters and to observation/illumination conditions.

We will perform a sensitivity analysis by varying one parameter at a time while keeping the others constant. You can adjust the individual values of the other parameters. Then select which parameter you want to analyze and the minimum and maximum range.

```{code-cell} ipython3
w_sensitivity = interactive(fn.prosail_sensitivity,
                            N_leaf=fn.w_nleaf, Cab=fn.w_cab, Car=fn.w_car, Ant=fn.w_ant, Cbrown=fn.w_cbrown, 
                            Cw=fn.w_cw, Cm=fn.w_cm, lai=fn.w_lai, hotspot=fn.w_hotspot, leaf_angle=fn.w_leaf_angle, 
                            sza=fn.w_sza, vza=fn.w_vza, psi=fn.w_psi, skyl=fn.w_skyl, 
                            soil_name=fn.w_soil, var=fn.w_param, value_range=fn.w_range)
display(w_sensitivity)
```

Start with chlorophyll sensitivity. The largest variations occur in the green and red regions. In the red‑edge, a “shift” occurs, which is key for estimating chlorophyll and photosynthetic activity.

Evaluate the sensitivity to other pigments (`Car` or `Ant`). Their spectral response is smaller, making them harder to estimate via remote sensing. Brown pigments show strong spectral variation, representing chromatic changes in diseased or dead leaves.

Now examine LAI sensitivity when the range is small (e.g., 0 to 2). The spectrum changes significantly as LAI increases. When LAI spans higher values (e.g., 2 to 4), the spectral variation is much smaller. At high LAI the spectrum tends to “saturate,” making the signal less sensitive.

Now keep LAI fixed at a high value (e.g., 3) and vary the viewing zenith angle between 0° and 35°. Despite the high LAI, there are still significant spectral variations due to viewing geometry.

Now examine the dry matter content (`Cm`). As dry matter increases, important variations occur in the NIR and SWIR.

The `hotspot` parameter is related to the relative size of the leaf compared to canopy height. It affects how leaves cast shadows on each other, especially when the observer is aligned with the sun (similar VZA and SZA, PSI = 0°).

:::{figure} ./input/figures/hotspot.png 
:alt:Hotspot effect
:name:fig-hotspot
Effect of the hotspot on canopy reflectance. Taken from [](https://doi.org/10.3390/rs11192239)
:::

# Sensor Signal
Sensors onboard satellites, aircraft, and drones do not measure the full continuous spectrum. Instead, they sample it around specific spectral bands chosen to capture key biophysical properties.

The spectral response function describes how a sensor integrates the spectrum to produce band values. Each sensor and each band has its own response function.

In this task, we will examine the spectral responses of commonly used sensors: Landsat, Sentinel‑2, Sentinel‑3, and a typical UAV camera.

Select the sensor you want to simulate to see how each one “sees” the same spectra.

```{code-cell} ipython3
w_rho_sensor = interactive(fn.sensor_sensitivity,
                           sensor=fn.w_sensor, spectra=fixed(w_sensitivity))
display(w_rho_sensor)
```

Perform a sensitivity analysis for chlorophyll again and compare how Landsat, Sentinel‑2, and a UAV camera respond.


# Deriving Vegetation Parameters
So far, we have seen how the surface spectrum varies with biophysical parameters.

However, our final goal is the opposite: to estimate one or more biophysical variables of interest from a spectrum or from specific spectral bands. For evapotranspiration and water‑use efficiency, we may want to estimate LAI, absorbed PAR fraction, chlorophyll content, or other pigments.

One common approach is to develop empirical relationships between spectral bands (or vegetation indices) and field‑sampled data. This can provide reliable results for a specific study area, but the spectral signal depends on many factors, which may cause such locally calibrated relationships to fail when applied to other crops or regions.

Another alternative is to develop synthetic databases from simulations. This is what we will do in this task.

We will run 5000 simulations, randomly varying parameter values within plausible ranges for our study areas.

You may adjust ranges depending on whether you work with perennial crops (higher minimum LAI) or annual crops (LAI = 0 needed to represent early stages).

Since there are many parameters and we may not know the plausible range for most crops, leave the default values and focus on the parameters you are more confident about.

You can also choose one or several soil types depending on your region.

:::{hint}
You could even upload a typical soil spectrum from your area to the folder `./input/soil_spectral_library`. Make sure the file has two columns: wavelengths (400–2500 nm) and reflectance. To update the soil library, you must also run the first cell.
:::

Finally, select the sensor for which you want to generate the signal.

When your simulation environment is configured, click the `Run simulations` button. After a few minutes, a series of plots will appear.

:::{note}
You may receive a warning message; do not worry—everything should work normally.
:::

```{code-cell} ipython3
w_rho_sensor = interactive(fn.build_random_simulations, {"manual": True, "manual_name": "Generar simulaciones"},
                           n_sim=fixed(5000), n_leaf_range=fn.w_range_nleaf,
                           cab_range=fn.w_range_cab, car_range=fn.w_range_car,
                           ant_range=fn.w_range_ant, cbrown_range=fn.w_range_cbrown, 
                           cw_range=fn.w_range_cw, cm_range=fn.w_range_cm,
                           lai_range=fn.w_range_lai, hotspot_range=fn.w_range_hotspot, 
                           leaf_angle_range=fn.w_range_leaf_angle, 
                           sza=fn.w_sza, vza=fn.w_vza, psi=fn.w_psi, 
                           skyl=fn.w_skyl, soil_names=fn.w_soils, sensor=fn.w_sensor)
display(w_rho_sensor)
```


The simulations are saved in `./output/prosail_simulations_<sensor>.csv`. Download this file and develop statistical relationships between bands or indices and biophysical parameters using your preferred software.

You can run as many simulations as needed. Just remember that each new simulation overwrites the CSV file. 

:::{important}
Download or copy it before running new simulations.
:::


# Conclusions
In this exercise we have seen how the vegetation spectrum responds to surface biophysical variables.

* LAI is likely the variable with the strongest influence on vegetation spectral response.
* Chlorophyll concentration mainly affects the visible and red‑edge regions.
* Water content and dry matter mainly affect the spectrum from the NIR onward.
* Observation and illumination geometry, as well as soil spectral response, also influence the signal.
* Radiative transfer models can help estimate these parameters, although field data are ideally needed for validation and calibration.
* Sensors sample only parts of the spectrum around specific bands, so empirical relationships may not transfer between sensors.

```{code-cell} ipython3

```
