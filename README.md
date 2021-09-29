# pysyncrosim
The Python interface to [SyncroSim](https://syncrosim.com/)

## Installation

### Using `pip`

Use `pip` to install `pysyncrosim` to your default python installation. You can install Python from https://www.python.org/downloads/. You can also find information on how to install `pip` from the [pip documentation](https://pip.pypa.io/en/stable/installation/).

Before installing `pysyncrosim`, you must install `GDAL` and `rasterio` separately. To do this, download the binaries for [GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and [rasterio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio). Note that the **cp38** in the wheel name refers to Python 3.8. Then use `pip` to install these binaries from your **Downloads** folder. 
```
# Install GDAL before rasterio
pip install GDAL-3.3.2-cp38-cp38-win_amd64.whl

# Install rasterio
pip install rasterio-1.2.8-cp38-cp38-win_amd64.whl

# Install pysyncrosim
pip install git+https://github.com/syncrosim/pysyncrosim
```

### Using `conda` environments

If you use `conda` regulary as your package manager, you may want to install `pysyncrosim` in a `conda` environment. See the [conda documentation](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) for `conda` installation instructions.

```
# Create new conda environment
conda create -n myenv python=3.8

# Activate environment
conda activate myenv

# Install rasterio requirement
conda install rasterio

# Install git and pip
conda install git pip

# Install pysyncrosim
pip install git+https://github.com/syncrosim/pysyncrosim
```

## Dependencies

`pysyncrosim` was tested and developed using Python 3.8. Because `pysyncrosim` uses `rasterio` for integrating spatial data, it also requires a C library dependency: GDAL >=2.3.

```
python>=3.8

pandas=1.3.2

numpy=1.21.2

rasterio>=1.2.6
```

## Usage

For a basic usage example with the [helloworldSpatial](https://apexrms.github.io/helloworldEnhanced/) package, see [spatial_demo.py](https://github.com/syncrosim/pysyncrosim/blob/main/examples/spatial_demo.py) in the **examples** folder.