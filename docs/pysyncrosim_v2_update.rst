Updating your pysyncrosim scripts to pysyncrosim v 2.0
========================================================
The introduction of `SyncroSim Studio`_ brought some structural changes and new functionalities, which get reflected in the ``pysyncrosim`` module. Use the guide below to update your ``pysyncrosim v1.5`` scripts to ``pysyncrosim v2.0``.

        .. _SyncroSim Studio: https://syncrosim.com/studio/

.. note::

    `SyncroSim v3.0.9`_ or higher is required to use ``pysyncrosim v2.0.1`` or higher.

		.. _SyncroSim v3.0.9: https://syncrosim.com/studio-download/


Updated functionalities
-----------------------

Packages
^^^^^^^^
To install and uninstall packages from your SyncroSim installation, use::
        
        session.install_packages()
        session.uninstall_packages()

Now you can use multiple SyncroSim packages in a single library. To add and remove packages from your library, use::

        myLibrary.add_packages()
        myLibrary.remove_packages()

And also for that reason, the package addons have been converted to standalone packages, or incorporated into the base packages. Therefore, the following methods no longer exist::

        myLibrary.addons()
        myLibrary.enable_addons()
        myLibrary.disable_addons()

Library
^^^^^^^
``myLibrary.info`` no longer shows the *Package name*, *Current package version* and *Minimum package version*, and the Input and Output folder paths have been combined into the *Data folder*.

The ``package`` argument in the library method has been renamed to ``packages``::

        myLibrary = ps.library(packages = [])

Dependencies
^^^^^^^^^^^^
``myScenario.dependency()`` is no longer a method. 
* To view the existing dependencies attribute for a scenario, use::

        myScenario.dependency

* To set dependencies attribute for a scenario, use::

        myScenario.dependency = ["Scenario 1", "Scenario 2"]

  Note that this will remove any previously set dependencies.
  Also, the order in which the dependencies are listed can be important. In this example, ``Scenario 1`` takes precedence over ``Scenario 2``.

Multiprocessing
^^^^^^^^^^^^^^^

the ``run()`` method no longer has the ``jobs`` argument. Use the ``core_Multiprocessing`` datasheet to set the number of cores to use. Note that this will affect every scenario run.


Variable naming
---------------
The **ID** in variable names have been changed to **Id**. It is generally safe to substitute ``ID`` for ``Id`` throughout your script, unless that affects any variables not related to SyncroSim.

Core datasheets
---------------
The ``corestime_`` datasheets are now simply called ``core_``.

stsimsf
-------
The ST-Sim Stock & Flow package, ``stsimsf`` have been incorporated into ST-Sim. Substitute all ``stsimsf_`` datasheets throghout your script for ``stsim_``.
The only exception is the ``stsimsf_OutputOptions`` that is now called ``stsim_OutputOptionsStockFlow``.
