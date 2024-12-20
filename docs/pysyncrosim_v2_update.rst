Updating your pysyncrosim scripts to pysyncrosim v 2.0
========================================================
The introduction of `SyncroSim Studio`_ brought some structural changes and new functionalities, which get reflected in the ``pysyncrosim`` module. Use the guide below to update your ``pysyncrosim`` version 1 scripts to be compatible with ``pysyncrosim v2.0``.

        .. _SyncroSim Studio: https://syncrosim.com/studio/

.. note::

    `SyncroSim v3.0.9`_ or higher is required to use ``pysyncrosim v2.0.0`` or higher.

		.. _SyncroSim v3.0.9: https://syncrosim.com/studio-download/


Updated methods
-----------------

Installing/uninstalling packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Previously, the ``add_packages()`` and ``remove_packages()`` methods were used to install and uninstall packages from SyncroSim. Now to install and uninstall packages from SyncroSim, use::
        
        # Installs the selected package(s) to SyncroSim
        session.install_packages()

        # Uninstalls the selected package(s) from SyncroSim
        session.uninstall_packages()

You can also have multiple versions of a package installed. Use the ``version`` argument in the ``install_packages()`` method to specify which version of the package you would like to install. If you do not specify a version, then the latest version of the package will be installed.
::
        # Install St-Sim version 4.0.0
        mySession.install_packages(packages = "stsim", version = "4.0.0")

        # Install the latest version of ST-Sim on the package server
        mySession.install_packages(packages = "stsim")

You can also use the ``version`` argument in the ``uninstall_packages()`` method to specify which version you would like to uninstall. If you do not specify a version, then all versions of that package will be uninstalled.
::
        # Uninstall ST-Sim version 4.0.0
        mySession.uninstall_packages(packages = "stsim", version = "4.0.0")

        # Uninstall all installed versions of ST-Sim
        mySession.uninstall_packages(packages = "stsim")

Adding/removing packages
^^^^^^^^^^^^^^^^^^^^^^^^
Now you can use multiple SyncroSim packages in a single library. To add and remove packages from your library, use::

        # Adds package(s) to the library
        myLibrary.add_packages()

        # Removes package(s) from the library
        myLibrary.remove_packages()

**Note:** when you remove a package from your library any associated datasheets will be removed as well.

You can also choose which package version to use within a library. Use the ``versions`` argument in the ``add_package()`` method to load a specific version of a package in a library, or to change the version of a package that the library uses.
::
        # Add ST-Sim version 4.0.0 to your library
        myLibrary.add_packages(packages = "stsim", versions = "4.0.0")

        # Update the version of ST-Sim that your library uses
        myLibrary.add_packages(packages = "stsim", versions = "4.0.1")

You do not need to specify a version when removing a package using ``remove_package()`` because only one version of a package can be loaded in a library at a time.

Creating libraries
^^^^^^^^^^^^^^^^^^
In SyncroSim 3, the concept of *addon* packages no longer exists. All addon packages have either been converted to standalone packages (e.g., ``burnP3PlusPrometheus``), and can be added to a library without having to load a base package first, or incorporated directly into its base package (e.g., ``stsimsf`` is now part of ``stsim``).
Because of that, and since SyncroSim libraries can support multiple packages, the following changes have been made to the ``library()`` method:

* The ``addon`` argument has been removed.

* The ``package`` argument has been renamed to ``packages`` (plural).
::

        # pysyncrosim version 1:
        myLibrary = ps.library(package = "packageName", addon = "addonName")

        # pysyncrosim version 2:
        myLibrary = ps.library(packages = ["package1", "package2"])


Library information
^^^^^^^^^^^^^^^^^^^
Since multiple packages can be loaded in a library, ``myLibrary.info`` no longer returns the following library attributes:

* *Package name*

* *Current package version*

* *Minimum package version*

In addition, now that you can link models from various packages in a pipeline, and outputs from one transformer can be inputs to the next transformer in a pipeline, the *Input* and *Output* folders have been combined into a single *Data* folder. See `Access Model Metadata`_ in the `Quickstart`_ for details.

        .. _Access Model Metadata: https://pysyncrosim.readthedocs.io/en/latest/quickstart.html#access-model-metadata
        .. _Quickstart: https://pysyncrosim.readthedocs.io/en/latest/quickstart.html


Dependencies
^^^^^^^^^^^^

``myScenario.dependency()`` is no longer a method, but a scenario attribute. 

To view the existing dependencies attribute for a scenario, use:

.. code-block:: pycon
        
        >>> myScenario.dependencies
           Id        Name  Priority
        0  2  Scenario 1         1

To set dependencies attribute for a scenario, use:

.. code-block:: pycon

        >>> myScenario.dependencies = ["Scenario 2", "Scenario 3"]
        >>> myScenario.dependencies
           Id        Name  Priority
        0  3  Scenario 2         1
        0  4  Scenario 3         2

**Note:** this will remove any previously set dependencies unless the existing dependencies are also included in the list.
Also, the order in which the dependencies are listed can be important. In this example, ``Scenario 2`` takes precedence over ``Scenario 3``.


Multiprocessing
^^^^^^^^^^^^^^^
the ``run()`` method no longer has the ``jobs`` argument for setting the number of cores to use during a multiprocessing run. 
Instead, use the ``core_Multiprocessing`` library datasheet to set the number of cores to use.
::
        multiprocessing = pd.DataFrame({'EnableMultiprocessing': True,
                                        'MaximumJobs': [6]})

        myLibrary.save_datasheet(name = "core_Multiprocessing", data = multiprocessing)

**Note:** because the ``core_Multiprocessing`` datasheet is library-scoped, modifying this datasheet will affect every scenario run.

Deprecated methods
------------------

Addon methods
^^^^^^^^^^^^^^^
Since the *addon* concept no longer applies, the following methods have been removed::

        myLibrary.addons()
        myLibrary.enable_addons()
        myLibrary.disable_addons()

Package updates
^^^^^^^^^^^^^^^
``mySession.update_packages()``: You no longer need to update the installed versions of packages in your SyncroSim session because you can have multiple versions installed at the same time. To install or uninstall versions of a package from your SyncroSim session, use the ``version`` argument in ``install_packages()`` instead.

Variable naming
---------------
The primary key column for all SyncroSim datasheets has been modified slightly. The **ID** in the primary key is now **Id** for all datasheets. This also applies to column names in scenario-scoped datasheets that reference values taken from project-scoped datasheets. It is generally safe to substitute ``ID`` for ``Id`` throughout your script, but it’s recommended to check the datasheet’s variable names.

.. code-block:: pycon

        >>> myScenario.datasheets("stsim_FlowPathway", include_key = True)
        Empty DataFrame
        Columns: [FlowPathwayId, FromStockTypeId, ToStockTypeId, FlowTypeId, Multiplier]
        Index: []

Core datasheets
---------------
The `system datasheets`_, previously identified by the prefix ``corestime_``, are now prefixed by ``core_``.

        .. _system datasheets_: https://docs.syncrosim.com/reference/ds_overview.html


