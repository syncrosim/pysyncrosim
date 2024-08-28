Installation
============
``pysyncrosim`` can be installed using either the ``conda`` or ``pip`` package managers. ``conda`` is a general package manager capable of installing packages from many sources, but ``pip`` is strictly a Python package manager. While the installation instructions below are based on a Windows 11 operating system, similar steps can be used to install pysyncrosim for Linux.

Before beginning the installation of ``pysyncrosim``, make sure you have the latest release of `SyncroSim`_ installed.

	.. _SyncroSim: https://syncrosim.com/download/

Dependencies
------------

``pysyncrosim`` was tested and developed using **Python 3.12.4** and **SyncroSim 3.0.4**. Because ``pysyncrosim`` uses ``rasterio`` for integrating spatial data, it also requires a C library dependency: ``GDAL >=2.3``.

* python=3.12.4

* pandas=2.2.2

* numpy=2.1.0

* rasterio=1.3.10

Using conda
-----------

Follow these steps to get started with ``conda`` and use ``conda`` to install ``pysyncrosim``. 

1. Install ``conda`` using the Miniconda or Anaconda installer (in this tutorial we use Miniconda). To install Miniconda, follow `this link`_ and under the **Latest Miniconda Installer Links**, download Miniconda for your operating system. Open the Miniconda installer and follow the default steps to install ``conda``. For more information, see the `conda documentation`_.

	.. _this link: https://docs.conda.io/en/latest/miniconda.html
	.. _conda documentation: https://conda.io/projects/conda/en/latest/user-guide/install/index.html

2. To use ``conda``, open the command prompt that was installed with the Miniconda installer. To find this prompt, type "anaconda prompt" in the **Windows Search Bar**. You should see an option appear called **Anaconda Prompt (miniconda3)**. Select this option to open a command line window. All code in the next steps will be typed in this window. 

3. You can either install ``pysyncrosim`` and its dependencies into your base environment, or set up a new ``conda`` environment (recommended). Run the code below to set up and activate a new ``conda`` environment called "myenv" that uses Python 3.8.

.. code-block:: console

	# Create new conda environment
	conda create -n myenv python=3.12.4

	# Activate environment
	conda activate myenv

You should now see that "(base)" has been replaced with "(myenv)" at the beginning of each prompt.

4. Set the package channel for ``conda``. To be able to install ``pysyncrosim``, you need to access the ``conda-forge`` package channel. To configure this channel, run the following code in the Anaconda Prompt.

.. code-block:: console

	# Set conda-forge package channel
	conda config --add channels conda-forge

5. Install ``pysyncrosim`` using ``conda install``. Installing ``pysyncrosim`` will also install its dependencies: ``pandas``, ``numpy``, and ``rasterio``.

.. code-block:: console

	# Install pysyncrosim
	conda install pysyncrosim

``pysyncrosim`` should now be installed and ready to use!

Using pip
---------

Use ``pip`` to install ``pysyncrosim`` to your default python installation. You can install Python from `www.python.org`_. You can also find information on how to install ``pip`` from the `pip documentation`_.

	.. _www.python.org: https://www.python.org/downloads/
	.. _pip documentation: https://pip.pypa.io/en/stable/installation/

Install ``pysyncrosim`` using ``pip install``. Installing ``pysyncrosim`` will also install its dependencies: ``pandas``, ``numpy``, and ``rasterio``.

.. code-block:: console

	# Make sure you are using the latest version of pip
	pip install --upgrade pip

	# Install pysyncrosim
	pip install pysyncrosim
