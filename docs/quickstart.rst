Quickstart
==========
``pysyncrosim`` is the Python interface to the `SyncroSim software framework`_, a program that structures and models your data. This tutorial will cover the basics of using the ``pysyncrosim`` package within the SyncroSim software framework.

	.. _SyncroSim software framework: https://syncrosim.com
	
To complete this tutorial, you must `install SyncroSim`_ and `install pysyncrosim`_. You will also need to install the `helloworldTime`_ SyncroSim Package.

	.. _install SyncroSim: https://syncrosim.com/download/
	.. _install pysyncrosim: https://pysyncrosim.readthedocs.io/en/latest/install.html
	.. _helloworldTime: https://apexrms.github.io/helloworldEnhanced/

Overview of SyncroSim
---------------------
`SyncroSim`_ is a software platform that helps you turn your data into forecasts. At the core of SyncroSim is an engine that automatically structures your existing data, regardless of its original format. SyncroSim transforms this structured data into forecasts by running it through a Pipeline of calculations (i.e. a suite of models). Finally, SyncroSim provides a rich interface to interact with your data and models, allowing you to explore and track the consequences of alternative “what-if” forecasting Scenarios. Within this software framework is the ability to use and create SyncroSim packages.

	.. _SyncroSim: https://syncrosim.com

For more details consult the `SyncroSim online documentation`_.

    .. _SyncroSim online documentation: https://docs.syncrosim.com/

Overview of ``pysyncrosim``
-----------------------
``pysyncrosim`` is a Python package designed to facilitate the development of modeling workflows for the SyncroSim software framework. Using the ``pysyncrosim`` interface, simulation models can be added and run through SyncroSim to transform Scenario-based datasets into model forecasts. This Python package takes advantage of general features of SyncroSim, such as defining Scenarios with spatial or non-spatial inputs, running Monte Carlo simulations, and summarizing model outputs. 

``pysyncrosim`` requires SyncroSim 2.3.6 or higher.

SyncroSim Package: `helloworldTime`
-----------------------------------
`helloworldTime`_ was designed to be a simple package to show off some key functionalities of SyncroSim, including the ability to add timesteps to SyncroSim modeling workflows.

	.. _helloworldTime: https://apexrms.github.io/helloworldEnhanced/

The package takes from the user two inputs, *m* and *b*, representing a slope and an intercept value. It then runs these input values through a linear model, *y=mt+b*, where *t* is *time*, and returns the *y* value as output.

    .. image:: img/infographic-basic.png

Set Up
------

Install SyncroSim
^^^^^^^^^^^^^^^^^
Before using ``pysyncrosim``, you will first need to `download and install`_ the SyncroSim software. Versions of SyncroSim exist for both Windows and Linux.

    .. _download and install: https://syncrosim.com/download/

Installing and Loading Python Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install ``pysyncrosim`` using either ``conda install`` or ``pip install``. See the `Installation`_ page for more detailed installation instructions.

    .. _Installation: https://pysyncrosim.readthedocs.io/en/latest/install.html

Then, in a new Python script, import ``pysyncrosim``.

.. code-block:: pycon

    >>> import pysyncrosim as ps
    
Connecting Python to SyncroSim 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The next step in setting up the Python environment for the ``pysyncrosim`` workflow is to create a SyncroSim Session instance in Python that provides the connection to your installed copy of the SyncroSim software. A new Session is created using the :class:`~pysyncrosim.session.Session()` class. The Session can be initialized with a path to the folder on your computer where SyncroSim has been installed. If no arguments are specified when the Session class is initialized, then the default install folder is used (Windows only).

.. code-block:: pycon

   # Load Session
   >>> mySession = ps.Session()
   
   # Load Session using path to SyncroSim Installation
   >>> mySession = ps.Session(location = "path/to/install_folder")
   
You can check to see which version of SyncroSim your Python script is connected to by running the :meth:`~pysyncrosim.session.Session.version()` method.
 
.. code-block:: pycon
   
   # Check SyncroSim version
   >>> mySession.version() 
   'Version is: 2.3.10'
   
Installing SyncroSim Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Finally, check if the ``helloworldTime`` package is already installed. Use the :meth:`~pysyncrosim.session.Session.packages()` method to first get a list of all currently installed SyncroSim Packages.
   
.. code-block:: pycon
   
    # Check which SyncroSim Packages are installed
    >>> mySession.packages()
    Empty DataFrame
    Columns: [index, Name, Description, Version, Extends]
    Index: [] 
    
Currently we do not have any packages installed! To see which packages are available from the SyncroSim package server, you can use the ``installed = False`` argument in the :meth:`~pysyncrosim.session.Session.packages()` method.

.. code-block:: pycon

    # Check out available SyncroSim Packages
    >>> available_packages = mySession.packages(installed=False)
    >>> available_packages.head()
                demosales  \
    0               dgsim   
    1          helloworld   
    2  helloworldPipeline   
    3   helloworldSpatial   
    4      helloworldTime   

      Example SyncroSim Base Package of a very simple sales forecasting model  \
    0     Simulates demographics of wildlife populations                        
    1      Example demonstrating how to create a package                        
    2                            Example using pipelines                        
    3                         Example using spatial data                        
    4                            Example using timesteps                        

       1.1.0  
    0  2.3.0  
    1  1.0.1  
    2  1.0.0  
    3  1.0.2  
    4  1.0.0 
    
Install ``helloworldTime`` using the :meth:`~pysyncrosim.session.Session.add_packages()` method from the Session class. This method takes a Package name as input and then queries the SyncroSim Package server for the specified Package.

.. code-block:: pycon
           
   # Install helloworldTime Package
   >>> mySession.add_packages("helloworldTime")
   ['helloworldTime'] installed successfully
   
To install a package from a *.ssimpkg* file on your local computer rather than installing directly from the server, you can use the Session :meth:`~pysyncrosim.session.Session.add_packages()` method with the ``packages`` argument set to the filepath to the local Package.
   
.. code-block:: pycon

    # Install helloworldTime Package locally
    >>> mySession.add_packages("path/to/helloworldTime.ssimpkg")

Now ``helloworldTime`` should be included in the Package list.

.. code-block:: pycon

   >>> mySession.packages()
           index                Name                                   Description Version Extends 
        0      0      helloworldTime    Example demonstrating how to use timesteps   1.0.0     NaN 
        
You can also update or remove a SyncroSim Package from your Session using the :meth:`~pysyncrosim.session.Session.update_packages()` method and the :meth:`~pysyncrosim.session.Session.remove_packages()` method.

.. code-block:: pycon

   # Update installed packages
   >>> mySession.update_packages("myPackage")
   
   # Remove installed packages 
   >>> mySession.remove_packages("myPackage")
   
Create a Modeling Workflow
--------------------------
When creating a new modeling workflow from scratch, we need to create class instances of the following scopes:

* `Library`_
* `Project`_
* `Scenario`_

    .. _Library: https://docs.syncrosim.com/how_to_guides/library_overview.html
    .. _Project: https://docs.syncrosim.com/how_to_guides/library_overview.html
    .. _Scenario: https://docs.syncrosim.com/how_to_guides/library_overview.html
   
These classes are hierarchical, such that a Library can contain many Projects, and each Project can contain many Scenarios. All parameters or configurations set in a Library are inherited by all Projects within the Library, and all parameters or configurations set in a Project are inherited by all Scenarios within that Project.

Create a New Library
^^^^^^^^^^^^^^^^^^^^
A SyncroSim `Library`_ is a file (with *.ssim* extension) that stores all of your model inputs and outputs. The format of each SyncroSim Library is unique to the SyncroSim Package with which it is associated. We create a new Library class instance using :func:`~pysyncrosim.helper.library()` that is connected (through your Session) to a SyncroSim Library file.

    .. _Library: https://docs.syncrosim.com/how_to_guides/library_overview.html

.. code-block:: pycon

    # Create a new Library
    >>> myLibrary = ps.library(name = "helloworldLibrary",
    >>>                        session = mySession, 
    >>>                        package = "helloworldTime")
    
    # Check Library information
    >>> myLibrary.info   
                        Property                                       Value  
    0                      Name:                           helloworldLibrary
    1                     Owner:                                         NaN
    2             Last Modified:                       2021-09-10 at 3:13 PM  
    3                      Size:                         196 KB  (200,704 B)
    4                 Read Only:                                          No
    5              Package Name:                              helloworldTime
    6       Package Description:  Example demonstrating how to use timesteps
    7   Current Package Version:                                       1.0.0
    8   Minimum Package Version:                                       1.0.0
    9      External input files:                helloworldLibrary.ssim.input
    10    External output files:               helloworldLibrary.ssim.output
    11          Temporary files:                 helloworldLibrary.ssim.temp
    12             Backup files:               helloworldLibrary.ssim.backup
    
We can also use the :func:`~pysyncrosim.helper.library()` function to open an existing Library. For instance, now that we have created a Library called "helloworldLibrary.ssim", we would simply specify that we want to open this Library using the ``name`` argument.    

.. code-block:: pycon

    # Open existing Library
    >>> myLibrary = ps.library(name = "helloworldLibrary")
                           
Note that if you want to create a new Library file with an existing Library name rather than opening the existing Library, you can use ``overwrite=True`` when initializing the Library class instance.

Create a New Project
^^^^^^^^^^^^^^^^^^^^
Each SyncroSim Library contains one or more SyncroSim `Projects`_, each represented by an instance of class Project in ``pysyncrosim``. Projects typically store model inputs that are common to all your Scenarios. In most situations you will need only a single Project for your Library; by default each new Library starts with a single Project named "Definitions" (with a unique ``project_id`` = 1). The :meth:`~pysyncrosim.library.Library.projects()` method of the Libarry class is used to both create and retrieve Projects for a specific Library.

    .. _Projects: https://docs.syncrosim.com/how_to_guides/library_overview.html

.. code-block:: pycon

    # Create (or open) a Project in this Library
    >>> myProject = myLibrary.projects(name = "Definitions")
    
    # Check Project information
    >>> myProject.info
               Property                   Value
    0         ProjectID                       1
    1              Name             Definitions
    2             Owner                     NaN
    3  DateLastModified  2021-12-21 at 10:48 PM
    4        IsReadOnly                      No
    
Create a New Scenario
^^^^^^^^^^^^^^^^^^^^^
Finally, each SyncroSim Project contains one or more `Scenarios`_, each represented by an instance of class Scenario in ``pysyncrosim``.

    .. _Scenarios: https://docs.syncrosim.com/how_to_guides/library_overview.html

Scenarios store the specific inputs and outputs associated with each Transformer in SyncroSim. SyncroSim models can be broken down into one or more of these Transformers. Each Transformer essentially runs a series of calculations on the input data to transform it into the output data. Scenarios can contain multiple Transformers connected by a series of Pipelines, such that the output of one Transformer becomes the input of the next.

Each Scenario can be identified by its unique ``scenario_id``. The :meth:`~pysyncrosim.library.Library.scenarios()` method of class Library or class Project is used to both create and retrieve Scenarios. Note that if using the Library class to generate a new Scenario, you must specify the Project to which the new Scenario belongs if there is more than one Project in the Library.

.. code-block:: pycon

    # Create a new Scenario using the Library class instance
    >>> myScenario = myLibrary.scenarios(name = "My First Scenario")
    
    # Open the newly-created Scenario using the Project class instance
    >>> myScenario = myProject.scenarios(name = "My First Scenario")
    
    # Check Scenario information
    >>> myScenario.info
                  Property                  Value
    0           ScenarioID                      1
    1            ProjectID                      1
    2                 Name      My First Scenario
    3             IsResult                     No
    4             ParentID                    NaN
    5                Owner                    NaN
    6     DateLastModified  2021-09-10 at 3:13 PM
    7           IsReadOnly                     No
    8    MergeDependencies                     No
    9   IgnoreDependencies                    NaN
    10         AutoGenTags                    NaN
    
View Model Inputs
^^^^^^^^^^^^^^^^^
Each SyncroSim Library contains multiple SyncroSim `Datasheets`_. A SyncroSim Datasheet is simply a table of data stored in the Library, and they represent the input and output data for Transformers. Datasheets each have a *scope*: either `Library`_, `Project`_, or `Scenario`_. Datasheets with a Library scope represent data that is specified only once for the entire Library, such as the location of the backup folder. Datasheets with a Project scope represent data that are shared over all Scenarios within a Project. Datasheets with a Scenario scope represent data that must be specified for each generated Scenario. We can view Datasheets of varying scopes using the :meth:`~pysyncrosim.library.Library.datasheets()` method from the Library, Project, and Scenario classes.

    .. _Datasheets: https://docs.syncrosim.com/how_to_guides/properties_overview.html
    .. _Library: https://docs.syncrosim.com/how_to_guides/library_overview.html
    .. _Project: https://docs.syncrosim.com/how_to_guides/library_overview.html
    .. _Scenario: https://docs.syncrosim.com/how_to_guides/library_overview.html

.. code-block:: pycon

    # View a summary of all Datasheets associated with the Scenario
    >>> myScenario.datasheets()
              Package                            Name     Display Name
    0  helloworldTime   helloworldTime_InputDatasheet   InputDatasheet
    1  helloworldTime  helloworldTime_OutputDatasheet  OutputDatasheet
    2  helloworldTime       helloworldTime_RunControl      Run Control
    
If we want to see more information about each Datasheet, such as the scope of the Datasheet or if it only accepts a single row of data, we can set the ``optional`` argument to ``True``.    

.. code-block:: pycon
    
    # View detailed summary of all Datasheets associated with a Scenario
    >>> myScenario.datasheets(optional=True)
          Scope         Package                            Name     Display Name  \
    0  Scenario  helloworldTime   helloworldTime_InputDatasheet   InputDatasheet   
    1  Scenario  helloworldTime  helloworldTime_OutputDatasheet  OutputDatasheet   
    2  Scenario  helloworldTime       helloworldTime_RunControl      Run Control   
    
      Is Single Is Output  
    0       Yes        No  
    1        No        No  
    2       Yes        No 
    
From this output we can see the the ``RunControl`` Datasheet and ``InputDatasheet`` only accept a single row of data (i.e. ``Is Single = Yes``). This is something to consider when we configure our model inputs.

To view a specific Datasheet rather than just a DataFrame of available Datasheets, set the ``name`` parameter in the :meth:`~pysyncrosim.scenario.Scenario.datasheets()` method to the name of the Datasheet you want to view. The general syntax of the name is: "<name of package>_<name of Datasheet>". From the list of Datasheets above, we can see that there are three Datasheets specific to the ``helloworldTime`` package.

.. code-block:: pycon

    # View the input Datasheet for the Scenario
    >>> myScenario.datasheets(name = "helloworldTime_InputDatasheet")
    Empty DataFrame
    Columns: [m, b]
    Index: []
    
Here, we are viewing the contents of a SyncroSim Datasheet as a Python ``pandas`` DataFrame. Although both SyncroSim Datasheets and ``pandas`` DataFrames are both represented as tables of data with predefined columns and an unlimited number of rows, the underlying structure of these tables differ.

Configure Model Inputs
^^^^^^^^^^^^^^^^^^^^^^
Currently our input Scenario Datasheets are empty! We need to add some values to our input Datasheet (``InputDatasheet``) and run control Datasheet (``RunControl``) so we can run our model.

First, assign the contents of the input Datasheet to a new ``pandas`` DataFrame using the Scenario :meth:`~pysyncrosim.scenario.Scenario.datasheets()` method, then check the columns that need input values.

.. code-block:: pycon

    # Load input Datasheet to a new pandas DataFrame
    >>> myInputDataframe = myScenario.datasheets(
    >>>     name = "helloworldTime_InputDatasheet")
            
    # Check the columns of the input DataFrame
    >>> myInputDataframe.info()
    <class 'pandas.core.frame.DataFrame'>
    Index: 0 entries
    Data columns (total 2 columns):
     #   Column  Non-Null Count  Dtype 
    ---  ------  --------------  ----- 
     0   m       0 non-null      object
     1   b       0 non-null      object
    dtypes: object(2)
    memory usage: 0.0+ bytes
    
The input Datasheet requires two values:

* *m* : the slope of the linear equation.
* *b* : the intercept of the linear equation.

Now we will update the input DataFrame. This can be done in many ways, such as creating a new ``pandas`` DataFrame with matching column names, or appending values as a dictionary to ``myInputDataframe``.

For this example, we will append values to ``myInputDataframe`` using a Python dictionary and the ``pandas`` ``append()`` function. Note that in the previous section we discovered that the input Datasheets only accept a single row of values, so we can only have one value each for our slope (*m*) and intercept (*b*).

.. code-block:: pycon

    # Create input data dictionary
    >>> myInputDict = {"m": 3, "b": 10}
                   
    # Append input data dictionary to myInputDataframe
    >>> myInputDataframe = myInputDataframe.append(myInputDict,
    >>>                                            ignore_index=True)
    
    # Check values
    >>> myInputDataframe
       m  b
    0  3  10
    
Saving Modifications to Datasheets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that we have a complete DataFrame of input values, we will save this DataFrame to a SyncroSim Datasheet using the Scenario :meth:`~pysyncrosim.scenario.Scenario.save_datasheet()` method. The :meth:`~pysyncrosim.scenario.Scenario.save_datasheet()` method exists for the Library, Project, and Scenario classes, so the class method chosen depends on the scope of the Datasheet.

.. code-block:: pycon

    >>> myScenario.save_datasheet(name = "helloworldTime_InputDatasheet",
    >>>                           data = myInputDataframe)
    
Configuring the RunControl Datasheet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There is one other Datasheet that we need to configure for our model to run. The ``RunControl`` Datasheet provides information about how many time steps to use in the model. Here, we set the minimum and maximum time steps for our model. Similar to above, we’ll add this information to a Python dictionary and then add it to the ``RunControl`` Datasheet using the ``pandas`` ``append()`` function. We need to specify data for the following two columns:

* *MinimumTimestep* : the starting time point of the simulation.
* *MaximumTimestep* : the end time point of the simulation.

.. code-block:: pycon

    # Load RunControl Datasheet to a ``pandas`` DataFrame
    >>> runSettings = myScenario.datasheets(
    >>>     name = "helloworldTime_RunControl")
    
    # Check the columns of the RunControl DataFrame
    >>> runSettings.info()
    <class 'pandas.core.frame.DataFrame'>
    Index: 0 entries
    Data columns (total 2 columns):
     #   Column           Non-Null Count  Dtype 
    ---  ------           --------------  ----- 
     0   MinimumTimestep  0 non-null      object
     1   MaximumTimestep  0 non-null      object
    dtypes: object(2)
    memory usage: 0.0+ bytes
    
    # Create RunControl data dictionary
    >>> runControlDict = {"MinimumTimestep": 1, "MaximumTimestep": 10}
    
    # Append RunControl data dictionary to RunControl DataFrame
    >>> runSettings = runSettings.append(runControlDict, ignore_index=True)
    
    # Check values
    >>> runSettings
      MinimumTimestep MaximumTimestep
    0               1              10
    
    # Save RunControl pandas DataFrame to a SyncroSim Datasheet
    >>> myScenario.save_datasheet(name = "helloworldTime_RunControl",
    >>>                           data = runSettings)
    
Run Scenarios
-------------

Setting Run Parameters
^^^^^^^^^^^^^^^^^^^^^^
We will now run our Scenario using the Scenario :meth:`~pysyncrosim.scenario.Scenario.run()` method. 

.. code-block:: pycon

    # Run the Scenario
    >>> myResultsScenario = myScenario.run()
    
Checking the Run Log
^^^^^^^^^^^^^^^^^^^^
For more information use the Scenario :meth:`~pysyncrosim.scenario.Scenario.run_log()` method. Note that this method can only be called when a Scenario is a *Results Scenario*.

.. code-block:: pycon

    # Get run details for My First Scenario
    >>> myResultsScenario.run_log()
                                                 Run Log
    0       STARTING SIMULATION: 2022-01-13 : 8:34:46 AM
    1          Parent Scenario is: [1] My First Scenario
    2  Result scenario is: [2] My First Scenario ([1]...
    3                               CONFIGURING: Primary
    4                                   RUNNING: Primary
    5       SIMULATION COMPLETE: 2022-01-13 : 8:34:54 AM
    6                    Total simulation time: 00:00:08
    
View Results
------------

Results Scenarios
^^^^^^^^^^^^^^^^^
A Results Scenario is generated when a Scenario is run, and is an exact copy of the original Scenario (i.e. it contains the original Scenario’s values for all input Datasheets). The Results Scenario is passed to the Transformer in order to generate model output, with the results of the Transformer’s calculations then being added to the Results Scenario as output Datsheets. In this way the Results Scenario contains both the output of the run and a snapshot record of all the model inputs.

Check out the current Scenarios in your Library using the Library :meth:`~pysyncrosim.library.Library.scenarios()` method.
    
.. code-block:: pycon

    # Check Scenarios that currently exist in your Library
    >>> myLibrary.scenarios()
       ScenarioID  ProjectID                                           Name  \
    0           1          1                              My First Scenario   
    1           2          1  My First Scenario ([1] @ 13-Jan-2022 8:34 AM)   

      IsResult  
    0       No  
    1      Yes 
    
The first Scenario is our original Scenario, and the second is the Results Scenario with a time and date stamp of when it was run. We can also see some other information about these Scenarios, such as whether or not the Scenario is a result or not (i.e. ``isResult`` column).

Viewing Results
^^^^^^^^^^^^^^^
The next step is to view the output Datasheets added to the Result Scenario when it was run. We can load the result tables using the Scenario :meth:`~pysyncrosim.scenario.Scenario.datasheets()` method, and setting the name parameter to the Datasheet with new data added.

.. code-block:: pycon

    # Results of Scenario
    >>> myOutputDataframe = myResultsScenario.datasheets(
    >>>     name = "helloworldTime_OutputDatasheet")
    
    # View results table
    >>> myOutputDataframe.head()
       Iteration  Timestep     y
    0        NaN         1  13.0
    1        NaN         2  16.0
    2        NaN         3  19.0
    3        NaN         4  22.0
    4        NaN         5  25.0
    
Working with Multiple Scenarios
-------------------------------
You may want to test multiple alternative Scenarios that have slightly different inputs. To save time, you can copy a Scenario that you’ve already made, give it a different name, and modify the inputs. To copy a completed Scenario, use the Scenario :meth:`~pysyncrosim.scenario.Scenario.copy()` method.

.. code-block:: pycon

    # Check which Scenarios you currently have in your Library
    >>> myLibrary.scenarios().Name
    0                                My First Scenario
    1    My First Scenario ([1] @ 13-Jan-2022 8:34 AM)
    Name: Name, dtype: object
    
    # Create a new Scenario as a copy of an existing Scenario
    >>> myNewScenario = myScenario.copy("My Second Scenario")
    
    # Make sure this new Scenario has been added to the Library
    >>> myLibrary.scenarios().Name
    0                                My First Scenario
    1    My First Scenario ([1] @ 13-Jan-2022 8:34 AM)
    2                               My Second Scenario
    Name: Name, dtype: object
    
To edit the new Scenario, let's first load the contents of the input Datasheet and assign it to a new ``pandas`` DataFrame using the Scenario :meth:`~pysyncrosim.scenario.Scenario.datasheets()` method. We will set the ``empty`` argument to ``True`` so that instead of getting the values from the existing Scenario, we can start with an empty DataFrame again.

.. code-block:: pycon

    # Load empty input Datasheets as a Pandas DataFrame
    >>> myNewInputDataframe = myNewScenario.datasheets(
    >>>     name = "helloworldTime_InputDatasheet", empty = True)
    
    # Check that we have an empty DataFrame
    >>> myNewInputDataframe.info()
    <class 'pandas.core.frame.DataFrame'>
    Index: 0 entries
    Data columns (total 2 columns):
     #   Column  Non-Null Count  Dtype 
    ---  ------  --------------  ----- 
     0   m       0 non-null      object
     1   b       0 non-null      object
    dtypes: object(2)
    memory usage: 0.0+ bytes
    
Now, all we need to do is add some new values the same way we did before, using the ``pandas`` ``append()`` function.

.. code-block:: pycon

    # Create an input data dictionary
    >>> newInputDict = {"m": 4, "b": 10}
    
    # Append new input data dictionary to new input DataFrame
    >>> myNewInputDataframe = myNewInputDataframe.append(newInputDict,
    >>>                                                  ignore_index=True)
    
    # View the new inputs
    >>> myNewInputDataframe
       m   b
    0  4  10
    
Finally, we will save the updated DataFrame to a SyncroSim Datasheet using the Scenario :meth:`~pysyncrosim.scenario.Scenario.save_datasheet()` method.

.. code-block:: pycon

    # Save pandas DataFrame to a SyncroSim Datasheet
    >>> myNewScenario.save_datasheet(name = "helloworldTime_InputDatasheet",
    >>>                              data = myNewInputDataframe)
    
We will keep the ``RunControl`` Datasheet the same as the first Scenario.

Run Scenarios
^^^^^^^^^^^^^
We now have two SyncroSim Scenarios. We can run all the Scenarios using Python list comprehension.

.. code-block:: pycon

    # Create a List of Scenarios
    >>> myScenarioList = [myScenario, myNewScenario]

    # Run all Scenarios
    >>> myResultsScenarioAll = [scn.run() for scn in myScenarioList]
    
View Results
^^^^^^^^^^^^
From running many Scenario at once we get a list of Result Scenarios. To view the results, we can use the Scenario :meth:`~pysyncrosim.scenario.Scenario.datasheets()` method on the indexed list.

.. code-block:: pycon

   # View results of second Scenario
   >>> myResultsScenarioAll[1].datasheets(
   >>>      name = "helloworldTime_OutputDatasheet") 
      Iteration  Timestep     y
   0        NaN         1  14.0
   1        NaN         2  18.0
   2        NaN         3  22.0
   3        NaN         4  26.0
   4        NaN         5  30.0
   5        NaN         6  34.0
   6        NaN         7  38.0
   7        NaN         8  42.0
   8        NaN         9  46.0
   9        NaN        10  50.0
   
Identifying the Parent Scenario of a Results Scenario
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you have many alternative Scenarios and many Results Scenarios, you can always find the parent Scenario that was run in order to generate the Results Scenario using the Scenario :attr:`~pysyncrosim.scenario.Scenario.parent_id` attribute.

.. code-block:: pycon

    # Find parent ID of first Results Scenario
    >>> myResultsScenarioAll[0].parent_id
    1.0
    
    # Find parent ID of second Results Scenario
    >>> myResultsScenarioAll[1].parent_id
    3.0
    
Access Model Metadata
---------------------

Getting SyncroSim Class Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Retrieve information about your Library, Project, or Scenario using the :attr:`~pysyncrosim.library.Library.info` attribute.

.. code-block:: pycon

    # Retrieve Library information
    >>> myLibrary.info
                        Property                                       Value  
    0                      Name:                           helloworldLibrary
    1                     Owner:                                         NaN
    2             Last Modified:                       2021-09-10 at 3:13 PM  
    3                      Size:                         196 KB  (200,704 B)
    4                 Read Only:                                          No
    5              Package Name:                              helloworldTime
    6       Package Description:  Example demonstrating how to use timesteps
    7   Current Package Version:                                       1.0.0
    8   Minimum Package Version:                                       1.0.0
    9      External input files:                helloworldLibrary.ssim.input
    10    External output files:               helloworldLibrary.ssim.output
    11          Temporary files:                 helloworldLibrary.ssim.temp
    12             Backup files:               helloworldLibrary.ssim.backup
        
    # Retrieve Project information
    >>> myProject.info
               Property                   Value
    0         ProjectID                       1
    1              Name             Definitions
    2             Owner                     NaN
    3  DateLastModified  2021-12-21 at 10:48 PM
    4        IsReadOnly                      No
    
    # Retrieve Scenario information
    >>> myScenario.info
                  Property                  Value
    0           ScenarioID                      1
    1            ProjectID                      1
    2                 Name      My First Scenario
    3             IsResult                     No
    4             ParentID                    NaN
    5                Owner                    NaN
    6     DateLastModified  2021-09-10 at 3:13 PM
    7           IsReadOnly                     No
    8    MergeDependencies                     No
    9   IgnoreDependencies                    NaN
    10         AutoGenTags                    NaN
    
The following attributes can also be used to get useful information about a Library, Project, or Scenario instance:

* :attr:`~pysyncrosim.library.Library.name`: used to retrieve or assign a name.
* :attr:`~pysyncrosim.library.Library.owner`: used to retrieve or assign an owner.
* :attr:`~pysyncrosim.library.Library.date_modified`: used to retrieve the timestamp when the last changes were made.
* :attr:`~pysyncrosim.library.Library.readonly`: used to retrieve or assign the read-only status.
* :attr:`~pysyncrosim.library.Library.description`: used to retrieve or add a description.

You can also find identification numbers of Projects or Scenarios using the following attributes:

* :attr:`~pysyncrosim.project.Project.project_id`: used to retrieve the Project Identification number.
* :attr:`~pysyncrosim.scenario.Scenario.scenario_id`: used to retrieve the Scenario Identification number.

Backup your Library
-------------------
Once you have finished running your models, you may want to backup the inputs and results into a zipped *.backup* subfolder. First, we want to modify the Library Backup Datasheet to allow the backup of model outputs. Since this Datasheet is part of the built-in SyncroSim core, the name of the Datasheet has the prefix "core". We can get a list of all the core Datasheets with a Library scope using the Library :meth:`~pysyncrosim.library.Library.datasheets()` method with ``summary`` set to ``"CORE"``.

.. code-block:: pycon

    # Find all Library-scoped Datasheets
    >>> myLibrary.datasheets(summary = "CORE")
          Package                       Name              Display Name
    0        core                core_Backup                    Backup
    1        core           core_CondaConfig       Conda Configuration
    2        core            core_LNGPackage  Last Known Good Packages
    3        core       core_Multiprocessing           Multiprocessing
    4        core               core_Options                   Options
    5        core  core_ProcessorGroupOption   Processor Group Options
    6        core   core_ProcessorGroupValue    Processor Group Values
    7        core              core_PyConfig      Python Configuration
    8        core               core_RConfig           R Configuration
    9        core              core_Settings                  Settings
    10       core             core_SysFolder                   Folders
    11  corestime          corestime_Options           Spatial Options
    
    # Get the current values for the Library's Backup Datasheet
    >>> myDataframe = myLibrary.datasheets(name = "core_Backup")
    
    # View current values for the Library's Backup Datasheet
    >>> myDataframe
      IncludeInput  IncludeOutput BeforeUpdate
    0          Yes            NaN          Yes
    
    # Add IncludeOutput to the Library's Backup Datasheet
    >>> myDataframe["IncludeOutput"] = "Yes"
    
    # Save the pandas DataFrame to a SyncroSim Datasheet
    >>> myLibrary.save_datasheet(name = "core_Backup", data = myDataframe)
    
    # Check to make sure IncludeOutput is now set to "Yes"
    >>> myLibrary.datasheets(name = "core_Backup")
    
Now, you can use the Library :meth:`~pysyncrosim.library.Library.backup()` method to backup your Library.

.. code-block:: pycon

    >>> myLibrary.backup()
    
``pysyncrosim`` and the SyncroSim Windows User Interface
----------------------------------------------------
It can be useful to work in both ``pysyncrosim`` and the SyncroSim Windows User Interface at the same time. You can easily modify Datasheets and run Scenarios in ``pysyncrosim``, while simultaneously refreshing the Library and plotting outputs in the User Interface as you go. To sync the Library in the User Interface with the latest changes from the ``pysyncrosim`` code, click the refresh icon (circled in red below) in the upper tool bar of the User Interface.

.. image:: img/pysyncrosim-with-UI.PNG

SyncroSim Package Development
-----------------------------
If you wish to design SyncroSim packages using python and pysyncrosim, you can follow the `Creating a Package`_ and `Enhancing a Package`_ tutorials on the `SyncroSim documentation website`_. 

	.. _Creating a Package: http://docs.syncrosim.com/how_to_guides/package_create_overview.html
	.. _Enhancing a Package: http://docs.syncrosim.com/how_to_guides/package_enhance_overview.html
	.. _SyncroSim documentation website: http://docs.syncrosim.com/

.. note::

	`SyncroSim v2.3.10`_ is required to develop python-based SyncroSim packages.

		.. _SyncroSim v2.3.10: https://syncrosim.com/download/

    
    