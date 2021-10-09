Installation
============
pysyncrosim can be installed using either the ``conda`` or ``pip`` package managers. ``conda`` is a general package manager capable of installing packages from many sources, but ``pip`` is strictly a Python package manager. For this reason, using ``pip`` requires downloading and installing dependency binaries, so we recommend using the ``conda`` installation method. While the installation instructions below are based on a Windows 10 operating system, similar steps can be used to install pysyncrosim for Linux.

Before beginning the installation of pysyncrosim, make sure you have the latest release of `SyncroSim`_ installed.

	.. _SyncroSim: https://syncrosim.com/download/

Dependencies
------------

pysyncrosim was tested and developed using **Python 3.8** and **SyncroSim 2.3.5**. Because pysyncrosim uses ``rasterio`` for integrating spatial data, it also requires a C library dependency: ``GDAL >=2.3``.

* python>=3.8

* pandas=1.3.2

* numpy=1.21.2

* rasterio>=1.2.6

Using conda
-----------

Follow these steps to get started with ``conda`` and use ``conda`` to install pysyncrosim. 

1. Install ``conda`` using the Miniconda or Anaconda installer (in this tutorial we use Miniconda). To install Miniconda, follow `this link`_ and under the **Latest Miniconda Installer Links**, download Miniconda for your operating system. Open the Miniconda installer and follow the default steps to install ``conda``. For more information, see the `conda documentation`_.

	.. _this link: https://docs.conda.io/en/latest/miniconda.html
	.. _conda documentation: https://conda.io/projects/conda/en/latest/user-guide/install/index.html

2. To use ``conda``, open the command prompt that was installed with the Miniconda installer. To find this prompt, type "anaconda prompt" in the **Windows Search Bar**. You should see an option appear called **Anaconda Prompt (miniconda3)**. Select this option to open a command line window. All code in the next steps will be typed in this window. 

3. You can either install pysyncrosim and its dependencies into your base environment, or set up a new ``conda`` environment (recommended). Run the code below to set up and activate a new ``conda`` environment called "myenv" that uses Python 3.8.

.. code-block:: console

	# Create new conda environment
	conda create -n myenv python=3.8

	# Activate environment
	conda activate myenv

You should now see that "(base)" has been replaced with "(myenv)" at the beginning of each prompt.

4. Set the package channel for ``conda``. To be able to install the dependencies for pysyncrosim, you need to access the ``conda-forge`` package channel. To configure this channel, run the following code in the Anaconda Prompt.

.. code-block:: console

	# Set conda-forge package channel
	conda config --add channels conda-forge

5. Install pysyncrosim dependencies, ``numpy``, ``pandas``, and ``rasterio``, using the following code.

.. code-block:: console

	# Install numpy requirement
	conda install numpy

	# Install pandas requirement
	conda install pandas

	# Install rasterio requirement
	conda install rasterio

6. Install pysyncrosim from GitHub using ``pip``. If you do not have ``git`` or ``pip`` installed already, use ``conda`` to install these packages. Then, use ``pip`` and ``git`` to install the latest GitHub release of pysyncrosim. Run the following code to install ``git``, ``pip``, and pysyncrosim.

.. code-block:: console

	# Install git and pip
	conda install git pip

	# Install pysyncrosim
	pip install git+https://github.com/syncrosim/pysyncrosim

pysyncrosim should now be installed and ready to use!

Using pip
---------

Use ``pip`` to install pysyncrosim to your default python installation. You can install Python from `www.python.org`_. You can also find information on how to install ``pip`` from the `pip documentation`_.

	.. _www.python.org: https://www.python.org/downloads/
	.. _pip documentation: https://pip.pypa.io/en/stable/installation/

Before installing pysyncrosim, you must install ``GDAL`` and ``rasterio`` separately. To do this, download the binaries for `GDAL`_ and `rasterio`_. Note that the **cp39** in the wheel name refers to Python 3.9. Then use ``pip`` to install these binaries from your **Downloads** folder. You must also install the dependencies ``numpy`` and ``pandas``.

	.. _GDAL: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
	.. _rasterio: https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio 

.. code-block:: console

	# Make sure you are using the latest version of pip
	pip install --upgrade pip

	# Install GDAL before rasterio
	pip install GDAL-3.3.2-cp39-cp39-win_amd64.whl

	# Install rasterio
	pip install rasterio-1.2.8-cp39-cp39-win_amd64.whl

	# Install numpy
	pip install numpy

	# Install pandas
	pip install pandas

	# Install pysyncrosim
	pip install git+https://github.com/syncrosim/pysyncrosim
