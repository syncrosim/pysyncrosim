# pysyncrosim <img src="https://github.com/syncrosim/pysyncrosim/raw/main/docs/img/logo.png" align="right" width=140/>

The Python interface to [SyncroSim](https://syncrosim.com/)

## Installation

`pysyncrosim` can be installed using either the `conda` or `pip` package managers. `conda` is a general package manager capable of installing packages from many sources, but `pip` is strictly a Python package manager. While the installation instructions below are based on a Windows 10 operating system, similar steps can be used to install `pysyncrosim` for Linux.

Before beginning the installation of `pysyncrosim`, make sure you have the latest release of [SyncroSim](https://syncrosim.com/studio-download/) installed.

### Dependencies

`pysyncrosim v2.0` was tested and developed using **Python 3.12** and **SyncroSim 3.0.9**. Because `pysyncrosim` uses `rasterio` for integrating spatial data, it also requires a C library dependency: GDAL >=3.7.

```
python=3.12

pandas=2.2.2

numpy=2.1.0

rasterio=1.3.10
```

### Using `conda`

Follow these steps to get started with `conda` and use `conda` to install `pysyncrosim`. 

1. Install `conda` using the Miniconda or Anaconda installer (in this tutorial we use Miniconda). To install Miniconda, follow [this link](https://docs.conda.io/en/latest/miniconda.html) and under the **Latest Miniconda Installer Links**, download Miniconda for your operating system. Open the Miniconda installer and follow the default steps to install `conda`. For more information, see the [conda documentation](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

2. To use `conda`, open the command prompt that was installed with the Miniconda installer. To find this prompt, type "anaconda prompt" in the **Windows Search Bar**. You should see an option appear called **Anaconda Prompt (miniconda3)**. Select this option to open a command line window. All code in the next steps will be typed in this window. 

3. You can either install `pysyncrosim` and its dependencies into your base environment, or set up a new `conda` environment (recommended). Run the code below to set up and activate a new `conda` environment called "myenv" that uses Python 3.12.
```
# Create new conda environment
conda create -n myenv python=3.12

# Activate environment
conda activate myenv
```
You should now see that "(base)" has been replaced with "(myenv)" at the beginning of each prompt.

4. Set the package channel for `conda`. To be able to install the dependencies for `pysyncrosim`, you need to access the `conda-forge` package channel. To configure this channel, run the following code in the Anaconda Prompt.
```
# Set conda-forge package channel
conda config --add channels conda-forge
```

5. Install `pysyncrosim` using `conda install`. Installing `pysyncrosim` will also install its dependencies: `pandas`, `numpy`, and `rasterio`.
```
# Install pysyncrosim
conda install pysyncrosim
```

`pysyncrosim` should now be installed and ready to use!

### Using `pip`

Use `pip` to install `pysyncrosim` to your default python installation. You can install Python from https://www.python.org/downloads/. You can also find information on how to install `pip` from the [pip documentation](https://pip.pypa.io/en/stable/installation/).

Install `pysyncrosim` using `pip install`. Installing `pysyncrosim` will also install its dependencies: `pandas`, `numpy`, and `rasterio`.
```
# Make sure you are using the latest version of pip
pip install --upgrade pip

# Install pysyncrosim
pip install pysyncrosim
```

## Usage

### Getting Started

For a basic usage example with the [helloworldSpatialPy](https://apexrms.github.io/helloworldEnhanced/) package, see the [spatial_demo.py](https://github.com/syncrosim/pysyncrosim/blob/main/examples/spatial_demo.py) and [input-raster.tif](https://github.com/syncrosim/pysyncrosim/blob/main/examples/input-raster.tif) in the **examples** folder. To download the spatial_demo.py file, view the file on GitHub and select **Raw**. From the raw view, right-click and select **Save As...**. To run the spatial demo, you will also need to install the `matplotlib` Python package. You can install this package using the following code.

```
# Install matplotlib
conda install matplotlib
```

### SyncroSim Package Development

If you wish to design SyncroSim packages using python and `pysyncrosim`, you can follow the [Creating a Package](http://docs.syncrosim.com/how_to_guides/package_create_overview.html) and [Enhancing a Package](http://docs.syncrosim.com/how_to_guides/package_enhance_overview.html) tutorials on the [SyncroSim documentation website](http://docs.syncrosim.com/). Note that [SyncroSim v2.3.10](https://syncrosim.com/download/) is required to develop python-based SyncroSim packages.
