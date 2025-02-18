<div align="center">

![Logo](https://github.com/IMSY-DKFZ/simpa/raw/main/docs/source/images/simpa_logo.png?raw=true "SIMPA Logo")

[![Documentation Status](https://readthedocs.org/projects/simpa/badge/?version=develop)](https://simpa.readthedocs.io/en/develop/?badge=develop)
![Build Status](https://github.com/IMSY-DKFZ/simpa/actions/workflows/automatic_testing.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/IMSY-DKFZ/simpa/blob/main/LICENSE.md)
[![Pypi Badge](https://img.shields.io/pypi/v/simpa)](https://pypi.org/project/simpa/)
[![PyPI downloads](https://img.shields.io/pypi/dw/simpa?color=gr&label=pypi%20downloads)](https://pypi.org/project/simpa/)

</div>

# The toolkit for Simulation and Image Processing for Photonics and Acoustics (SIMPA)

SIMPA aims to facilitate realistic image simulation for optical and acoustic imaging modalities by
providing adapters to crucial modelling steps, such as volume generation; optical modelling; acoustic
modelling; and image reconstruction. SIMPA provides a communication layer between various modules
that implement optical and acoustic forward and inverse models.
Non-experts can use the toolkit to create sensible simulations from default parameters in an end-to-end fashion. Domain experts are provided with the functionality to set up a highly customisable
pipeline according to their specific use cases and tool requirements.
The paper that introduces SIMPA including visualisations and explanations can be found here: [https://doi.org/10.1117/1.JBO.27.8.083010](https://doi.org/10.1117/1.JBO.27.8.083010)

* [Getting started](#getting-started)
* [Simulation examples](#simulation-examples)
* [Documentation](#documentation)
* [Reproducibility](#reproducibility)
* [Contributing](#how-to-contribute)
* [Performance profiling](#performance-profiling)
* [Troubleshooting](#troubleshooting)
* [Citation](#citation)
* [Funding](#funding)

The toolkit is still under development and is thus not fully tested and may contain bugs. 
Please report any issues that you find in our Issue Tracker: https://github.com/IMSY-DKFZ/simpa/issues. 
Also make sure to double check all value ranges of the optical and acoustic tissue properties 
and to assess all simulation results for plausibility.

# Getting started

In order to use SIMPA in your project, SIMPA has to be installed as well as the external tools that make the actual simulations possible.
Finally, to connect everything, SIMPA has to find all the binaries of the simulation modules you would like to use.
The SIMPA path management takes care of that.

* [SIMPA installation instructions](#simpa-installation-instructions)
* [External tools installation instructions](#external-tools-installation-instructions)
* [Path Management](#path-management)
* [Testing](#run-manual-tests)

## SIMPA installation instructions

The recommended way to install SIMPA is a manual installation from the GitHub repository, please follow steps 1 - 3:

1. `git clone https://github.com/IMSY-DKFZ/simpa.git`
2. `cd simpa`
3. `git checkout main`
4. `git pull`

Now open a python instance in the 'simpa' folder that you have just downloaded. Make sure that you have your preferred
virtual environment activated (we also recommend python 3.10)
1. `pip install .` or `pip install -e .` for an editable mode. 
2. Test if the installation worked by using `python` followed by `import simpa` then `exit()`

If no error messages arise, you are now setup to use SIMPA in your project.

You can also install SIMPA with pip. Simply run:

`pip install simpa`

You also need to manually install the pytorch library to use all features of SIMPA.
To this end, use the pytorch website tool to figure out which version to install:
[https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

## External tools installation instructions

In order to get the full SIMPA functionality, you should install all third party toolkits that make the optical and 
acoustic simulations possible. 

### mcx (Optical Forward Model)

Download the latest nightly build of [mcx](http://mcx.space/) on [this page](http://mcx.space/nightly/github/) for your operating system:

- Linux: `mcx-linux-x64-github-latest.zip`
- MacOS: `mcx-macos-x64-github-latest.zip`
- Windows: `mcx-windows-x64-github-latest.zip`

Then extract the files and set `MCX_BINARY_PATH=/.../mcx/bin/mcx` in your path_config.env.

### k-Wave (Acoustic Forward Model)

Please follow the following steps and use the k-Wave install instructions 
for further (and much better) guidance under:

[http://www.k-wave.org/](http://www.k-wave.org/)

1. Install MATLAB with the core, image processing and parallel computing toolboxes activated at the minimum.
2. Download the kWave toolbox (version >= 1.4)
3. Add the kWave toolbox base path to the toolbox paths in MATLAB
4. If wanted: Download the CPP and CUDA binary files and place them in the k-Wave/binaries folder
5. Note down the system path to the `matlab` executable file.

## Path management

As a pipelining tool that serves as a communication layer between different numerical forward models and
processing tools, SIMPA needs to be configured with the paths to these tools on your local hard drive.
You have a couple of options to define the required path variables. 
### Option 1: 
Ensure that the environment variables defined in `simpa_examples/path_config.env.example` are accessible to your script during runtime. This can be done through any method you prefer, as long as the environment variables are accessible through `os.environ`. 
### Option 2:
Import the `PathManager` class to your project using
`from simpa.utils import PathManager`. If a path to a `.env` file is not provided, the `PathManager` looks for a `path_config.env` file (just like the
one we provided in the `simpa_examples/path_config.env.example`) in the following places, in this order:
1. The optional path you give the PathManager
2. Your $HOME$ directory
3. The current working directory
4. The SIMPA home directory path
   
For this option, please follow the instructions in the `simpa_examples/path_config.env.example` file. 

## Run manual tests
To check the success of your installation ot to assess how your contributions affect the Simpa simulation outcomes, you can run the manual tests automatically. Install the testing requirements by doing `pip install .[testing]` and run the `simpa_tests/manual_tests/generate_overview.py` file. This script runs all manual tests and generates both a markdown and an HTML file that compare your results with the reference results.

# Simulation examples

To get started with actual simulations, SIMPA provides an [example package](simpa_examples) of simple simulation 
scripts to build your custom simulations upon. The [minimal optical simulation](simpa_examples/minimal_optical_simulation.py)
is a nice start if you have MCX installed.

Generally, the following pseudo code demonstrates the construction and run of a simulation pipeline:

```python
import simpa as sp

# Create general settings 
settings = sp.Settings(general_settings)

# Create specific settings for each pipeline element 
# in the simulation pipeline
settings.set_volume_creation_settings(volume_creation_settings)
settings.set_optical_settings(optical_settings)
settings.set_acoustic_settings(acoustic_settings)
settings.set_reconstruction_settings(reconstruction_settings)

# Set the simulation pipeline
simulation_pipeline = [sp.VolumeCreationModule(settings),
                       sp.OpticalModule(settings),
                       sp.AcousticModule(settings),
                       sp.ReconstructionModule(settings)]
    
# Choose a PA device with device position in the volume
device = sp.CustomDevice()

# Simulate the pipeline
sp.simulate(simulation_pipeline, settings, device)
```

# Reproducibility

For reproducibility, we provide the exact version number including the commit hash in the simpa output file.
This can be accessed via `simpa.__version__` or by checking the tag `Tags.SIMPA_VERSION` in the output file.
This way, you can always trace back the exact version of the code that was used to generate the simulation results.

# Documentation

The updated version of the SIMPA documentation can be found at [https://simpa.readthedocs.io/en/develop](https://simpa.readthedocs.io/en/develop).

## Building the documentation

It is also easily possible to build the SIMPA documentation from scratch.
When the installation succeeded, and you want to make sure that you have the latest documentation
you should do the following steps in a command line:

1. Make sure that you've installed the optional dependencies needed for the documentation by running `pip install .[docs]`
2. Navigate to the `simpa/docs` directory
2. If you would like the documentation to have the https://readthedocs.org/ style, type `pip install sphinx-rtd-theme`
3. Type `make html`
4. Open the `index.html` file in the `simpa/docs/build/html` directory with your favourite browser.

# How to contribute

Please find a more detailed description of how to contribute as well as code style references in our
[contribution guidelines](CONTRIBUTING.md).

To contribute to SIMPA, please fork the SIMPA github repository and create a pull request with a branch containing your 
suggested changes. The core developers will then review the suggested changes and integrate these into the code 
base.

Please make sure that you have included unit tests for your code and that all previous tests still run through. Please also run the pre-commit hooks and make sure they are passing.
Details are found in our [contribution guidelines](CONTRIBUTING.md).

There is a regular SIMPA status meeting every Friday on even calendar weeks at 10:00 CET/CEST, and you are very welcome to participate and
raise any issues or suggest new features. If you want to join this meeting, write one of the core developers.

Please see the github guidelines for creating pull requests: [https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)


# Performance profiling

When changing the SIMPA core, e.g., by refactoring/optimizing, or if you are curious about how fast your machine runs
SIMPA, you can run the SIMPA [benchmarking scripts](simpa_examples/benchmarking/run_benchmarking.sh). Make sure to install the necessary dependencies via 
`pip install .[profile]` and then run:

```bash
bash ./run_benchmark.sh
```

once for checking if it works and then parse [--number 100] to run it at eg 100 times for actual benchmarking.
Please see [benchmarking.md](docs/source/benchmarking.md) for a complete explanation.


# Understanding SIMPA

**Tags** are identifiers in SIMPA used to categorize settings and components within simulations, making configurations
modular, readable, and manageable. Tags offer organizational, flexible, and reusable benefits by acting as keys in
configuration dictionaries.

**Settings** in SIMPA control simulation behavior. They include:

- **Global Settings**: Apply to the entire simulation, affecting overall properties and parameters.
- **Component Settings**: Specific to individual components, allowing for detailed customization and optimization of
each part of the simulation.

Settings are defined in a hierarchical structure, where global settings are established first, followed by
component-specific settings. This approach ensures comprehensive and precise control over the simulation process.
For detailed information, users can refer to the [understanding SIMPA documentation](./docs/source/understanding_simpa.md).

# Troubleshooting

In this section, known problems are listed with their solutions (if available):

## 1. Error reading hdf5-files when using k-Wave binaries:
   
If you encounter an error similar to:

    Error using h5readc
    The filename specified was either not found on the MATLAB path or it contains unsupported characters.

Look up the solution in [this thread of the k-Wave forum](http://www.k-wave.org/forum/topic/error-reading-h5-files-when-using-binaries).  

## 2. KeyError: 'time_series_data'

This is the error which will occur for ANY k-Wave problem. For the actual root of the problem, please either look above in
the terminal for the source of the bug or run the scripts in Matlab to find it manually.
      
# Citation

If you use the SIMPA tool, we would appreciate if you cite our Journal publication in the Journal of Biomedical Optics:

Gröhl, Janek, Kris K. Dreher, Melanie Schellenberg, Tom Rix, Niklas Holzwarth, Patricia Vieten, Leonardo Ayala, Sarah E. Bohndiek, Alexander Seitel, and Lena Maier-Hein. *"SIMPA: an open-source toolkit for simulation and image processing for photonics and acoustics."* **Journal of Biomedical Optics** 27, no. 8 (2022).

```Bibtex
@article{2022simpatoolkit,
  title={SIMPA: an open-source toolkit for simulation and image processing for photonics and acoustics},
  author={Gr{\"o}hl, Janek and Dreher, Kris K and Schellenberg, Melanie and Rix, Tom and Holzwarth, Niklas and Vieten, Patricia and Ayala, Leonardo and Bohndiek, Sarah E and Seitel, Alexander and Maier-Hein, Lena},
  journal={Journal of Biomedical Optics},
  volume={27},
  number={8},
  year={2022},
  publisher={SPIE}
}
```

# Funding

This project has received funding from the European Research Council (ERC) under the European Union’s Horizon 2020 research and innovation programme (grant agreement No. [101002198]).

![ERC](https://github.com/IMSY-DKFZ/simpa/raw/main/docs/source/images/LOGO_ERC-FLAG_EU_.jpg "ERC")
