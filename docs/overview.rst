Overview
========
``pysyncrosim`` is the Python interface to the `SyncroSim software framework`_.

	.. _SyncroSim software framework: https://syncrosim.com

Overview of SyncroSim
---------------------
`SyncroSim`_ is an open science tool for organizing tabular and spatial data, running geospatial simulation code, and visualizing model results. Its flexible framework supports the integration of code across multiple scripting languages and the use and creation of customizable packages, allowing you to tailor the platform to your specific needs.

    .. _SyncroSim: https://syncrosim.com

For more details, please consult the `SyncroSim online documentation`_.

    .. _SyncroSim online documentation: https://docs.syncrosim.com/

Overview of ``pysyncrosim``
---------------------------

``pysyncrosim`` is an open-source python package that leverages the **SyncroSim** command-line interface to simplify scripting model workflows for **SyncroSim** in python. This python package provides functions for building models from scratch, running those models, and accessing both spatial and tabular model outputs. The ``pysyncrosim`` package is designed to work with any **SyncroSim** package. 

A key feature of the ``pysyncrosim`` package is its seamless integration with `SyncroSim Studio`_, allowing you to interactively explore and validate your models in the user interface as you step through your python code. Additionally, ``pysyncrosim`` facilitates the creation of a permanent, reproducible record of the entire modeling workflow – including pre- and post-processing of model inputs and outputs – in a python script. 

    .. _SyncroSim Studio: https://syncrosim.com/studio/

.. note::

	`SyncroSim v3.0.9`_ or higher is required to use ``pysyncrosim v2.0.0`` or higher.

		.. _SyncroSim v3.0.9: https://syncrosim.com/studio-download/