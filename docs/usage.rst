Usage
=====

Getting Started
---------------

For a basic usage example with the `helloworldSpatial`_ package, see the `spatial_demo.py`_ and `input-raster.tif`_ in the **examples** folder. To download the spatial_demo.py file, view the file on GitHub and select **Raw**. From the raw view, right-click and select **Save As...**. To run the spatial demo, you will also need to install the ``matplotlib`` Python package. You can install this package using the following code.

	.. _helloworldSpatial: https://apexrms.github.io/helloworldEnhanced/
	.. _spatial_demo.py: https://github.com/syncrosim/pysyncrosim/blob/main/examples/spatial_demo.py
	.. _input-raster.tif: https://github.com/syncrosim/pysyncrosim/blob/main/examples/input-raster.tif

.. code-block:: console

	# Install matplotlib
	conda install matplotlib


Running pysyncrosim in Spyder
-----------------------------

If using ``conda``, the ``spyder`` IDE is easy to install and straightforward to use.

1. First, install ``spyder`` either in your base environment or in your ``conda`` environment using the following code.

.. code-block:: console

	# Install spyder
	conda install spyder


2. Open the IDE by typing ``spyder`` in the command prompt.

.. code-block:: console

	# Open spyder
	spyder


.. note::

	you may get a pop-up saying you have a missing dependency, ``rtree``. You can safely ignore this warning.

3. Within the IDE, change the working directory to the directory containing your pysyncrosim scripts (e.g. `spatial_demo.py`_ and `input-raster.tif`_)

	.. _spatial_demo.py: https://github.com/syncrosim/pysyncrosim/blob/main/examples/spatial_demo.py
	.. _input-raster.tif: https://github.com/syncrosim/pysyncrosim/blob/main/examples/input-raster.tif

.. figure:: spyder.PNG
	:width: 800px
	:align: center
	:alt: alternate text

|

4. Open and run your pysyncrosim scripts from the left-hand window. You can run scripts line-by-line in ``spyder`` by selecting the line(s) you want to run and pressing F9.

SyncroSim Package Development
-----------------------------

If you wish to design SyncroSim packages using python and pysyncrosim, you can follow the `Creating a Package`_ and `Enhancing a Package`_ tutorials on the `SyncroSim documentation website`_. 

	.. _Creating a Package: http://docs.syncrosim.com/how_to_guides/package_create_overview.html
	.. _Enhancing a Package: http://docs.syncrosim.com/how_to_guides/package_enhance_overview.html
	.. _SyncroSim documentation website: http://docs.syncrosim.com/

.. note::

	`SyncroSim v2.3.6`_ is required to develop python-based SyncroSim packages.

		.. _SyncroSim v2.3.6: https://syncrosim.com/download/
