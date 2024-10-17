import pandas as pd
import numpy as np
#import sys
import os
import io
import tempfile
import shutil
import pysyncrosim as ps
from pysyncrosim import helper
from pysyncrosim.environment import _environment

pd.set_option("display.max_columns", 50)

class Library(object):
    """
    A class to represent a SyncroSim Library. 
        
    """
    __projects = None
    __scenarios = None
    __datasheets = None
    
    def __init__(self, location=None, session=None, use_conda=None, packages=None):
        """
        Initializes a pysyncrosim Library instance.

        Parameters
        ----------
        location : String
            Filepath to Library location on disk.
        session : Session
            pysyncrosim Session instance.
        use_conda : Logical, optional
            If True, then uses Conda environment for this Library. If False, 
            then does not use Conda environment. If None, then uses the 
            Conda environment specified in the SyncroSim Library. The default 
            is None.
        packages : String or List of Strings, optional
            List of package names to add to the Library. The default is None.

        Returns
        -------
        None.

        """
        self.__location = location
        self.__session = session
        self.__use_conda = use_conda

        # Initialize when in a SyncroSim environment
        if location is None and session is None:
            e = _environment()
            if e.program_directory.item() is not None:
                self.__location = e.library_filepath.item()
                self.__session = ps.Session(e.program_directory.item())
            else:
                raise RuntimeError("Not in a SyncroSim environment." +
                                   " Please specify a location and session.")

        if self.__session is None:
            self.__session = ps.Session()

        if self.__use_conda is not None:
            self.__init_conda()

        self.__name = os.path.basename(self.__location)
        self.__info = None
        self.__owner = None
        self.__date_modified = None
        self.__readonly = None
        # All above attributes get created by below function
        self.__init_info()
        self.__description = self.__init_description()

        # Initialize packages
        if packages is not None:
            self.add_packages(packages)
        
        # Initialize projects and scenarios
        self.scenarios()
        self.projects()

    @property
    def session(self):
        """
        Retrieves the Session associated with this Library.

        Returns
        -------
        Session
            The Session for this Library.

        """
        return self.__session
    
    @property
    def name(self):
        """
        Retrieves or sets the name of this Library.

        Returns
        -------
        String
            Library name.

        """
        return self.__name
    
    @name.setter
    def name(self, value):
        args = ["--setprop", "--lib=%s" % self.location, "--name=%s" % value]
        self.session._Session__call_console(args)
        self.__name = value
        
    @property
    def location(self):
        """
        Retrieves the file path to this Library.

        Returns
        -------
        String
            Library file path.

        """
        return self.__location

    @property
    def use_conda(self):
        """
        Retrieves the Conda environment for this Library.

        Returns
        -------
        String
            Conda environment name.

        """
        return self.__use_conda

    @use_conda.setter
    def use_conda(self, value):
        self.__use_conda = value
        self.__init_conda()
    
    @property
    def packages(self):
        """
        Retrieves the package(s) this Library is using.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the package name(s) and versions.

        """
        args = ["--list", "--packages", "--lib=%s" % self.location, "--csv"]
        pkgs = self.session._Session__call_console(args, decode=True, csv=True)
        pkgs =  pd.read_csv(io.StringIO(pkgs))
        return pkgs
    
    @property
    def info(self):
        """
        Retrieves information about this Library.

        Returns
        -------
        pd.DataFrame
            General library information.

        """
        return self.__info
    
    @property
    def owner(self):
        """
        Gets or sets the owner of this Library.

        Returns
        -------
        String
            Owner of this Library.

        """
        return self.__owner
    
    @owner.setter
    def owner(self, value):
        if not isinstance(value, str):
            raise AttributeError("owner must be a String")
        self.__owner = value
        args = ["--setprop", "--lib=%s" % self.location, "--owner=%s" % value]
        self.session._Session__call_console(args)
        self.__owner = value
        self.__init_info()
        
    @property
    def readonly(self):
        """
        Gets or sets the read-only status of this Library.

        Returns
        -------
        String
            "yes" if this Project is read-only, "no" otherwise.

        """
        return self.__readonly
    
    @readonly.setter
    def readonly(self, value):
        if not isinstance(value, bool):
            raise AttributeError("readonly must be a Logical")
        elif value is True or value == "yes":
            self.__readonly = "yes"
        elif value is False or value == "no":
            self.__readonly = "no"
        else:
            raise TypeError("value must be a Logical")
        args = ["--setprop", "--lib=%s" % self.location,
                "--readonly=%s" % self.__readonly]
        self.session._Session__call_console(args)
        self.__init_info()
        
    @property
    def description(self):
        """
        Gets or sets the description for this Library.

        Returns
        -------
        String
            Library description.

        """
        return self.__description
    
    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise AttributeError("description must be a String")
        args = ["--setprop", "--lib=%s" % self.location,
                "--description=%s" % value]
        self.session._Session__call_console(args)
        self.__description = self.__init_description()
        
    @property
    def date_modified(self):
        """
        Retrieves the last date this Library was modified.

        Returns
        -------
        String
            Last date modified.

        """
        return self.__date_modified

    def add_packages(self, packages, versions=None):
        """
        Adds one or more SyncroSim packages to this Library.

        Parameters
        ----------
        packages : String or List of Strings
            Name of package or list of package names to add to the Library.
        versions : String or List of Strings, optional
            Version of package or list of package versions to add to the 
            Library. If None (default) then uses the latest installed version 
            of the package.

        Returns
        -------
        None.

        """
        installed_pkgs = self.session.packages(installed = True)
        library_pkgs = self.packages

        if installed_pkgs.empty:
            raise AttributeError("No packages are installed in this Library")

        if not isinstance(packages, list):
            packages = [packages]

        self.session._Session__validate_packages(packages, versions)

        if versions is None:
            installed_pkgs = installed_pkgs[installed_pkgs.Name.isin(packages)]
            versions = []
            for pkg in packages:
                versions.append(installed_pkgs[installed_pkgs.Name == pkg].Version.tolist()[-1])

        for pkg, ver in zip(packages, versions):

            pkg_rows = installed_pkgs[installed_pkgs.Name == pkg]
            if len(pkg_rows) == 0:
                print(f"{pkg} is not among the available installed packages")
                continue

            pkg_row = pkg_rows[pkg_rows.Version == ver]

            if len(pkg_row) == 0:
                print(f"{pkg} version {ver} is not among the available installed packages")
                continue

            pkg_name = pkg_row.Name.item()
            pkg_ver = pkg_row.Version.item()

            pkg_already_added = library_pkgs[library_pkgs.Name == pkg_name]
            if not pkg_already_added.empty:
                if pkg_already_added[pkg_already_added.Version == pkg_ver].empty:
                    # Remove old package version in use by library
                    args = ["--remove", "--package", "--lib=%s" % self.location,
                            "--pkg=%s" % pkg_name]
                    self.session._Session__call_console(args)
                else:
                    print(f"{pkg_name} v{pkg_ver} has already been added to the Library.")
                    return

            args = ["--add", "--package", "--lib=%s" % self.location,
                    "--pkg=%s" % pkg_name, "--ver=%s" % pkg_ver]

            self.session._Session__call_console(args)
            print(f"Package <{pkg} v{ver}> added")

    def remove_packages(self, packages):
        """
        Removes one or more SyncroSim packages from this Library.

        Returns
        -------
        None.

        """
        library_pkgs = self.packages
        packages = self.session._Session__validate_packages(packages)

        for pkg in packages:
            if pkg in library_pkgs.Name.values:
                args = ["--remove", "--package", "--lib=%s" % self.location,
                        "--pkg=%s" % pkg, "--force"]
                self.session._Session__call_console(args)
                print(f"Package <{pkg}> removed")
            else:
                print(f"{pkg} does not exist in the Library")
    
    def projects(self, name=None, pid=None, summary=True, overwrite=False):
        """
        Creates or opens one or more SyncroSim Projects in the Library.

        Parameters
        ----------
        name : String, optional
            Name of Project. The default is None.
        pid : Int, optional
            Project ID. The default is None.
        summary : Logical, optional
            If True, returns a DataFrame of Project information. If False, 
            returns a list of Project objects. Default is True.
        overwrite : Logical, optional
            If True, then overwrites an existing Project. Default is False.

        Returns
        -------
        Project, List of Projects, or pandas.DataFrame
            DataFrame containing Project information, including ID, Name, 
            Owner, Last Modified, and Read Only, or List of Projects if 
            `summary=False`.

        """
        
        self.__validate_projects_inputs(name, pid, summary, overwrite)
        
        if overwrite is True:
            self.delete(project=name)
        
        if self.__projects is None:
            self.__init_projects()
          
        p = self.__get_project(name=name, pid=pid)
        
        if p is None:
            
            if summary is True:
                
                # Return DataFrame of Project information
                project_summary = self.__extract_project_summary(name, pid)
                
                return project_summary
                
            if summary is False:
                
                project_list = self.__extract_projects()
        
                return project_list  
            
        elif p.empty:
            
            new_project = self.__create_new_project(name)
            
            return new_project
                
        else:
            
            existing_project = self.__open_existing_project(p)
             
            return existing_project
                
        
    def scenarios(self, name=None, project=None, sid=None, pid=None,
                  overwrite=False, optional=False, summary=None,
                  results=False):
        """
        Retrieves a Scenario or DataFrame of Scenarios in this Library.

        Parameters
        ----------
        name : String, Int, or List of these, optional
            Scenario name. If an integer is given, the value will be parsed as
            as Scenario ID. The default is None.
        project : Project, String, or Int, optional
            Project the Scenario belongs to. If no Project is specified when
            creating a new Scenario, the "Definitions" default Project is used.
            The default is None.
        sid : Int or List of Ints, optional
            Scenario ID. If both name and sid are specified, the sid is used. 
            The default is None.
        pid : Int, optional
            Project ID. The default is None.
        overwrite : Logical, optional
            Overwrites an existing Scenario. The default is False.
        optional : Logical, optional
            Return optional information. The default is False.
        summary : Logical, optional
            When name and sid is None, if True, returns a DataFrame of 
            information on existing Scenarios. Otherwise returns a list of 
            Scenario class instances.
        results : Logical, optional
            Return only a list of Results Scenarios. The default is False.

        Returns
        -------
        Scenario, List of Scenarios, or pandas.DataFrame
            If a name or sid is specified, returns a Scenario class instance.
            If no name or sid is specified, and summary is set to False,
            returns a list of Scenario class instances. If no name or sid is
            specified and summary is set to True, returns a pandas.DataFrame
            of Scenario information for this Library.

        """
        
        self.__validate_scenarios_inputs(name, sid, project, pid, overwrite,
                                         optional, summary, results)
          
        # Set the summary argument
        if summary is None:
            if name is not None or sid is not None:
                summary = False
            else:
                summary = True
                
        if sid is not None:
            if not isinstance(sid, list):
                sid = [sid]
            if name is not None:
                print("Both name and sid specified - using sid")
                name = None
            output = [self.__extract_scenario(
                name, project, s, pid, overwrite, optional, summary, results
                ) for s in sid]
            
        elif name is not None:
            if not isinstance(name, list):
                name = [name]
            output = [self.__extract_scenario(
                n, project, sid, pid, overwrite, optional, summary, results
                ) for n in name]
            
        else:
            output = self.__extract_scenario(None, project, None, pid,
                                             overwrite, optional, summary,
                                             results)
        if isinstance(output, list) and len(output) == 1:
            return output[0]
        else:
            return output


    def folders(self):
        """
        Retrieves a dataframe of folder information for this Library.

        Returns
        -------
        pandas.DataFrame
            Dataframe of folder information.
        """
        folder_data = ps.Folder(self)
        return folder_data._Folder__data
        
        
    def datasheets(self, name=None, summary=True, optional=False, empty=False,
                   scope="Library", filter_column=None, filter_value=None,
                   include_key=False, show_full_paths=False, return_hidden=False, *ids):
        """
        Retrieves a DataFrame of Library Datasheets.

        Parameters
        ----------
        name : String, optional
            Datasheet name. The default is None.
        summary : Logical, optional
            When set to True return a dataframe of all available package and
            SyncroSim core Datasheets. When set to False returns a list of 
            Datasheet dataframes. The default is True.
        optional : Logical, optional
            Return optional columns. The default is False.
        empty : Logical, optional
            Return an empty Datasheet. The default is False.
        scope : String, optional
            Datasheet scope. Options include "Library", "Project", or 
            "Scenario". The default is "Library".
        filter_column : String
            The column to filter the output Datasheet by. The default is None.
        filter_value : String, Int, or Logical
            The value to filter the filter_column by. The default is None.
        include_key : Logical, optional
            Whether to include the primary key of the Datasheet, corresponding
            to the SQL database. Default is False.
        show_full_paths : Logical, optional
            If set to True, returns the full path of any external files in the 
            Datasheet. Default is False.
        return_hidden : Logical, optional
            If set to True, returns all records in a Datasheet, including those
            hidden from the user. Results in a slower query. Default is False. 

        Returns
        -------
        pandas.DataFrame
            If `optional=False`, then returns a DataFrame of Datasheet 
            information including Package, Name, and Display Name.
            If `optional=True`, also returns Scope, Is Single, and Is Output.

        """
        
        self.__validate_datasheets_inputs(name, summary, optional, empty,
                                          filter_column, include_key,
                                          return_hidden)
        
        # TODO: Instead of setting to None here, make sure datasheets are 
        # refreshed when updates are made - saves computational time
        self.__datasheets = None        
        # TODO: Check if datasheet exists in desired scope
        
        args = self.__initialize_export_args(scope, ids, empty, include_key, show_full_paths)
        
        if name is None:
            
            if summary is True:
                
                ds_frame = self.__return_summarized_datasheets(
                    scope, summary, optional, ids)
                
                return ds_frame
        
            if summary is False:
                
                ds_list = self.__return_list_of_full_datasheets(
                    scope, args, return_hidden, ids)
                    
                return ds_list
        
        else:
            
            # If package is not included in name, add it
            name = self.__check_datasheet_name(name)
            
            if filter_column is not None:
            
                filter_column, filter_value = self.__find_filter_column_args(
                    filter_column, filter_value, name, scope, ids)
                
                args += ["--filtercol=%s" % filter_column + "=" + filter_value]
                        
            if return_hidden:
                ds = self.__slow_query_datasheet(name, scope, ids)               
            else:
                ds = self.__fast_query_datasheet(name, scope, args)            
            
            return ds
        
    def delete(self, project=None, scenario=None, force=False):
        """
        Deletes a SyncroSim class instance.

        Parameters
        ----------
        project : Project, String, or Int, optional
            If called from a Library class instance, specify the Project to 
            delete. The default is None.
        scenario : Scenario, String, or Int, optional
            If called from a Scenario class instance, specify the Scenario to
            delete. The default is None.
        force : Logical, optional
            If set to True, does not ask user before deleting SyncroSim class
            instance. The default is False.

        Returns
        -------
        None.

        """
        # after delete, can still access the instance attributes - should
        # create function to set to None?
        # Also, should have method to delete list of Projects or Scenarios?
        
        # type checks
        if project is not None and not isinstance(project, ps.Project):
            if not isinstance(project, int) and not isinstance(
                    project, str) and not isinstance(project, np.int64):
                raise TypeError(
                    "project must be a Project instance, Integer, or String")
        if scenario is not None and not isinstance(scenario, ps.Scenario):
            if not isinstance(scenario, int) and not isinstance(
                    scenario, str) and not isinstance(scenario, np.int64):
                raise TypeError(
                    "scenario must be a Scenario instance, Integer, or String")
        if not isinstance(force, bool):
            raise TypeError("force must be a Logical")
        
        if project is None and scenario is None:
            
            helper._delete_library(name = self.location, session=self.session,
                               force=force)
        
        elif project is not None and scenario is None:
            
            # turn project into project class instance if str or int
            if type(project) is int:
                p = self.projects(pid = project)
            if type(project) is str:
                if project in self.__projects["Name"].values:
                    p = self.projects(name = project)
                else:
                    raise ValueError(f'project {project} does not exist')
            if isinstance(project, ps.Project):
                p = project
            
            helper._delete_project(library=self, name=p.name,
                                   pid=p.pid, session=self.session,
                                   force=force)
            
        elif scenario is not None:
            
            # turn scenario into scenario class instance if str or int
            if type(scenario) is int:
                s = self.scenarios(sid = scenario, project = project)
            if type(scenario) is str:
                if scenario in self.__scenarios["Name"].values:
                    s = self.scenarios(name = scenario, project = project)
                else:
                    raise ValueError(f'scenario {scenario} does not exist')
            if isinstance(scenario, ps.Scenario):
                s = scenario
            
            helper._delete_scenario(library=self, project=s.project, 
                                    name=s.name, sid=s.sid,
                                    session=self.session,
                                    force=force)
    
    def save_datasheet(self, name, data, append=False, force=False, 
                       scope="Library", *ids):
        """
        Saves a pandas DataFrane as a SyncroSim Datasheet.

        Parameters
        ----------
        name : String
            Name of the Datasheet.
        data : pandas DataFrame
            DataFrame of Datasheet values.
        append : Logical, optional
            If set to True, appends the DataFrame to the existing 
            Datasheet (if the Datasheet accepts multiple rows). If False,
            then the user must also specify force as True to overwrite
            the existing Datasheet. Default is False.
        force : Logical, optional
            If set to True while append is False, overwrites the existing
            Datasheet. The user should be aware that this may also delete 
            other definitions and results, so this argument should be used 
            with care. Default is False.
        scope : String, optional
            Scope of the Datasheet. The default is "Library".
        *ids : Int
            If Project- or Scenario-scoped, requires the Project or Scenario
            IDs.

        Returns
        -------
        None.

        """
        # Type checks
        if not isinstance(name, str):
            raise TypeError("name must be a String")
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        if not isinstance(append, bool):
            raise TypeError("append must be a Logical")
        if not isinstance(force, bool):
            raise TypeError("force must be a Logical")
        if not isinstance(scope, str):
            raise TypeError("scope must be a String")
          
        # Check if datasheet name is valid
        self.__check_datasheet_name(name)

        # Convert boolean values to "Yes"/"No"
        for col in data:
            if data[col].dtype == bool:
                data[col] = data[col].map({True: "Yes", False: "No"})
            
        # Check if running in a SyncroSim environment from the user interface
        e = _environment()
        transfer_dir = e.transfer_directory.item()
        
        # If running from user interface, save data to transfer directory
        if (transfer_dir is not None) & (append is False):
            fpath = '{}\\SSIM_OVERWRITE-{}.csv'.format(transfer_dir, name)
            data.to_csv(fpath, index=False)
            return
        elif (transfer_dir is not None) & (append is True):
            fpath = '{}\\SSIM_APPEND-{}.csv'.format(transfer_dir, name)
            data.to_csv(fpath, index=False)
            return
        
        # Otherwise export the data to SyncroSim
        else:
            try:
                fpath = None
                delete_or_warn = self.__validate_delete_datasheet(force, append, scope, data)

                if delete_or_warn == "delete":
                    self.__delete_datasheet(scope, name, ids)
                    if data.empty:
                        return
                elif delete_or_warn == "warn":
                    print("WARNING: The force argument must be set to True " 
                          "to overwrite or delete an existing Project or Library "
                          "Datasheet.")
                    return

                fpath = self.__save_datasheet_to_temp(data)

                args = ["--import", "--lib=%s" % self.location,
                        "--sheet=%s" % name, 
                        "--file=%s" % fpath]

                if append:
                    args += ["--append"]
                if scope == "Project":
                    args += ["--pid=%d" % ids]
                if scope == "Scenario":
                    args += ["--sid=%d" % ids]

                result = self.__session._Session__call_console(args)
                
                if result.returncode == 0:
                    print(f"{name} saved successfully")                

            finally:
                if fpath is not None:
                    shutil.rmtree(os.path.dirname(fpath), ignore_errors=True)
            
    def run(self, scenarios=None, project=None,
            copy_external_inputs=False):
        """
        Runs a list of Scenario objects.

        Parameters
        ----------
        scenarios : Scenario, String, Int, or List
            List of Scenrios, SyncroSim Scenario instance, name of Scenario,
            or Scenario ID.
        project : Project, optional
            SyncroSim Project instance, name of Project, or Project ID.
        copy_external_inputs : Logical, optional
            If False, then a copy of external input files (e.g. GeoTIFF files)
            is not created for each job. Otherwise, a copy of external inputs 
            is created for each job. Applies only when jobs > 1. The number of 
            jobs is set using the 'core_Multiprocessing' datasheet. The default is
            False.

        Returns
        -------
        result_dict : Dictionary
            Dictionary of Results Scenarios.

        """

        self.__validate_run_inputs(scenarios, project,
                                   copy_external_inputs)
        
        scenario_list = self.__generate_scenarios_list_to_run(scenarios,
                                                              project)

        # Collect output from all runs
        result_list = [scn.run(
            copy_external_inputs=copy_external_inputs
            ) for scn in scenario_list]
            
        if len(result_list) == 1:
            return result_list[0]
        else:                
            return result_list
        
    def update(self):
        """
        Updates a SyncroSim Library.

        Returns
        -------
        None.

        """
        try:
            args = ["--update", "--lib=%s" % self.location]
            self.session._Session__call_console(args)
        
        except RuntimeError as e:
            print(e)
        
    def backup(self):
        """
        Creates a backup of a SyncroSim Library.

        Returns
        -------
        None.

        """
        ds = self.datasheets(name = "core_Backup")
        args = ["--lib=%s" % self.location, "--backup"]
        
        if ds.IncludeData[0] == "Yes":
            args += ["--extdata"]
        
        self.session._Session__call_console(args)

    def __init_conda(self):
        args = ["--setprop", "--lib=%s" % self.location]

        if self.__use_conda is True:
            args += ["--useconda=yes"]
            current_packages = self.__retrieve_lib_packages()
            self.__create_conda_env(current_packages)
        else:
            args += ["--useconda=no"]
        
        self.session._Session__call_console(args)
        
    def __retrieve_lib_packages(self):
        # Retrieves current packages being used by the library
        args = ["--list", "--datasheets", "--lib=%s" % self.location]
        result = self.session._Session__call_console(args, decode=True, csv=True)
        result =  pd.read_csv(io.StringIO(result))
        return np.unique(result["Package"]).tolist()

    def __create_conda_env(self, packages):

        for p in packages:
            args = ["--conda", "--createenv", "--pkg=%s" % p]
            result = self.session._Session__call_console(args)
            result_message = result.stdout.decode('utf-8')
            if (result.returncode != 0) | \
                ("this package does not use Conda environments" in result_message):
                print(result_message)
                self.__use_conda = False
                self.__init_conda()
    
    def __init_info(self):
        # Retrieves Library info
        args = ["--list", "--library", "--lib=%s" % self.location]
        lib_info = self.__console_to_csv(args)
        self.__info = lib_info
        
        # Set index and retrieve all properties
        lib_info = lib_info.set_index("Property")
        self.__owner = lib_info.loc["Owner:"].item()
        self.__readonly = lib_info.loc["Read Only:"].item()
        self.__date_modified = lib_info.loc["Last Modified:"].item()
        
    def __init_description(self):  
        # Retrieves the Library description
        args = ["--list", "--description", "--lib=%s" % self.__location]
        return self.session._Session__call_console(args, decode=True)
                
    def __init_projects(self): 
        # Retrieves a list of Projects
        args = ["--list", "--projects", "--lib=%s" % self.__location]
        self.__projects = self.__console_to_csv(args)
        self.__projects.rename(columns={"Id": "ProjectId"}, inplace=True)
            
    def __init_scenarios(self, pid=None):
        # Retrieves a list of Scenarios
        args = ["--list", "--scenarios", "--lib=%s" % self.__location]
        if pid is not None:
            args += ["--pid=%d" % pid]
        self.__scenarios = self.__console_to_csv(args)
        self.__scenarios.rename(columns={"Id": "ScenarioId"}, inplace=True)
            
    def __init_datasheets(self, scope, summary, name=None, args=None):
        # Retrieves a list of Datasheets
        if self.__datasheets is None:
            if summary is True:
                args = ["--list", "--datasheets", "--lib=%s" % self.__location,
                        "--scope=%s" % scope, "--includesys"]
            self.__datasheets = self.__console_to_csv(args)    
            
    def __check_datasheet_name(self, name):
        # Appends package name to Datasheet name
        if "_" not in name:
            raise ValueError("datasheet name must be prefixed with package name")

        return name
            
    def __get_project(self, name=None, pid=None):
        # Retrieves Project info from the name or ID
        if name is None and pid is None:
            return None
        if name is not None:
            return self.__projects[self.__projects["Name"] == name]
        else:
            return self.__projects[self.__projects["ProjectId"] == pid]
        
    def __refresh_projects(self):
        # Call SyncroSim DB to refresh project list
        self.__projects = None
        self.__init_projects()
            
    def __get_scenario(self, name=None, sid=None):
        # Retrieves Scenario info from the name or ID
        if name is None and sid is None:
            return None
        if name is not None and sid is not None:
            return self.__scenarios[
                (self.__scenarios["Name"] == name) & (self.__scenarios["ScenarioId"] == sid)]
        if name is not None:
            return self.__scenarios[self.__scenarios["Name"] == name]
        else:
            return self.__scenarios[self.__scenarios["ScenarioId"] == sid]
        
    def __refresh_scenarios(self):
        # Call SyncroSim DB to refresh scenario list
        self.__scenarios = None
        self.__init_scenarios()
        
    def __extract_scenario(self, name, project, sid, pid, overwrite, optional,
                           summary, results):
        
        # Find out if first argument is a Scenario ID
        if isinstance(name, int):
            
            if sid is not None:
                raise ValueError("Name is specified as a Scenario ID, but " + 
                                 "sid is already given")
                
            sid = name
            name = None
        
        # Find project if not specified
        if summary is False:
            
            if pid is None:
                
                pid = self.__find_project_id(project)
                
            if overwrite is True:
                if project is None:                
                    self.delete(project=pid, scenario=name, force=True)
                else:
                    self.delete(project=project, scenario=name, force=True)
                    
        # Retrieve Scenario DataFrame
        self.__init_scenarios(pid=pid)
        
        # If sid provided, check that sid exists
        if sid is not None:
            
            self.__validate_sid(sid, name)
        
        s = self.__get_scenario(name=name, sid=sid)
        
        if (s is None) or (summary is True):
            
            # Retrieve DataFrame of available Scenarios
            if summary:
                
                scenario_summary = self.__extract_scenario_summary(optional,
                                                                   results,
                                                                   name, sid)
                
                return scenario_summary
              
            # Return list of Scenario objects    
            if summary is False:
                
                scenario_list = self.__extract_scenario_list(project, pid) # better name needed
                
                return scenario_list                
    
        # Create a Scenario
        if s.empty:
            
            if project is None:
                project = pid
            
            new_scenario = self.__create_new_scenario(project, name, sid)
            
            return new_scenario
        
        # Open a Scenario
        else:
            
            if project is None:
                project = pid
            
            existing_scenario = self.__open_existing_scenario(s, project)
                            
            return existing_scenario

        
    def __console_to_csv(self, args, index_col=None):
        # Turns console output into a pd.DataFrame
        console_output = self.session._Session__call_console(
            args,
            decode=True,
            csv=True)
        
        return pd.read_csv(io.StringIO(console_output), index_col=index_col)
    
    def __validate_pid(self, pid, name):
        
        # If Scenario specified before project, then project should be created
        # if (self.__scenarios is not None and not self.__scenarios.empty):
        #     if pid == self.__scenarios["ProjectId"].item():
        #         return
        
        if self.__projects is None or self.__projects.empty:
            raise ValueError("pid specified, but no Projects created yet")
        elif pid not in self.__projects["ProjectId"].values:
            raise ValueError(f"Project ID {pid} does not exist")
        elif name is not None and name != self.__projects[
                self.__projects["ProjectId"] == pid]["Name"].values[0]:
            raise ValueError(
                f"Project ID {pid} does not match Project name {name}")
            
    def __validate_sid(self, sid, name):
    
        if self.__get_scenario(sid=sid).empty:
            raise ValueError(f"Scenario ID {sid} does not exist")
        elif name is not None and name != self.__get_scenario(
                sid=1).Name.item():
            raise ValueError(
                f"Scenario ID {sid} does not match Scenario name {name}")
            
    def __extract_project_summary(self, name, pid):
    
        if name is not None:
            return self.__projects[self.__projects.Name == name]
        if pid is not None:
            return self.__projects[self.__projects.ProjectId == pid]
        else:
            return self.__projects
        
    def __extract_projects(self):
        
        self.__refresh_projects()

        proj_list = []
        
        for i in range(0, len(self.__projects)):
            
            proj = ps.Project(self.__projects["ProjectId"].loc[i],
                              self.__projects["Name"].loc[i],
                              self)
            
            proj_list.append(proj)
    
        return proj_list
        
    def __create_new_project(self, name):
     
        # If specified Project does not exist, then create it    
        args = ["--create", "--project", "--lib=%s" % self.__location,
                "--name=%s" % name]
        self.session._Session__call_console(args)
        
        # Reset Projects
        self.__refresh_projects()
        p = self.__get_project(name, pid=None)
        
        # Convert np.int64 to native int
        pid = p["ProjectId"].values[0].tolist()
        
        new_project = ps.Project(pid, p["Name"].values[0], self)
        
        return new_project
    
    def __open_existing_project(self, project):
    
        # Convert np.int64 to native int
        pid = project["ProjectId"].values[0].tolist()
         
        return ps.Project(pid, project["Name"].values[0], self)
    
    def __find_project_from_scenario(self, sid, name):
            
        if sid is not None and self.__get_scenario(sid=sid).empty is False:
            pid = self.__get_scenario(sid=sid)["ProjectId"].item()
            project = self.projects(pid=pid)
        elif name is not None and len(self.__get_scenario(name=name)) == 1:
            pid = self.__get_scenario(name=name)["ProjectId"].item()
            project = self.projects(pid=pid)
        elif self.__projects is None or self.__projects.empty:
            project = self.projects(name = "Definitions")
            pid = project.pid
        elif len(self.__projects) == 1:
            pid = self.__projects.ProjectId.item()
            project = self.projects(pid=pid)     
        else:
            raise ValueError("More than one Project in Library." + 
                             " Please specify a Project.")
            
        return project
    
    def __find_project_id(self, project):
    
        if isinstance(project, int) or isinstance(project, np.int64):
            pid = project
        elif isinstance(project, str):
            # may need to refresh project here
            pid = self.__projects[
                self.__projects.Name == project].ProjectId.item()
        elif isinstance(project, ps.Project):
            pid = project.pid
        elif project is None:
            self.projects()
            if len(self.__projects) > 1:
                raise ValueError("More than one Project in Library." +
                                 " Please specify a Project.")
            elif len(self.__projects) == 0:
                self.__create_new_project("Definitions")
            pid = self.__projects["ProjectId"].item()
            
        return pid
    
    def __extract_scenario_summary(self, optional, results, name, sid):
    
        if optional is False:
            ds =  self.__scenarios[['ScenarioId',
                                    'ProjectId',
                                    'Name',
                                    'IsResult']]
        else:
            ds = self.__scenarios
            
        if results:
            ds = ds[ds["IsResult"] == "Yes"]
        
        if name is not None:
            return ds[ds.Name == name]
        
        if sid is not None:
            return ds[ds["ScenarioId"] == sid]
        
        return ds
    
    def __extract_scenario_list(self, project, pid): # better name needed
    
        s_summary = self.__scenarios
        s_summary = s_summary[s_summary["IsResult"] == "No"]
        s_summary.reset_index(inplace=True)
        
        if not isinstance(project, ps.Project):
            project = self.projects(pid=pid) 
                        
        scn_list = []
        
        for i in range(0, len(s_summary)):
            
            scn = ps.Scenario(s_summary["ScenarioId"].loc[i],
                              s_summary["Name"].loc[i],
                              project, self)
            
            scn_list.append(scn)
    
        return scn_list
    
    def __create_new_scenario(self, project, name, sid):
    
        pid = self.__find_project_id(project)
         
        # Create Scenario using console    
        args = ["--create", "--scenario", "--pid=%d" % pid,
                "--lib=%s" % self.__location, "--name=%s" % name]
        self.session._Session__call_console(args)
        
        # Reset Scenarios
        self.__refresh_scenarios()
        s = self.__get_scenario(name=name, sid=sid)
        
        if not isinstance(project, ps.Project):
            project = self.projects(pid=pid)
        
        return ps.Scenario(s["ScenarioId"].values[0],
                           s["Name"].values[0], project, self)
    
    def __open_existing_scenario(self, scenarios, project):
                    
        # Retrieve the name of a Scenario using only the sid
        pid = scenarios["ProjectId"].values[0].tolist()
    
        if not isinstance(project, ps.Project):
            project = self.projects(pid=pid)
    
        sid = scenarios["ScenarioId"].values[0].tolist()
        
        return ps.Scenario(sid, scenarios["Name"].values[0], project, self)
    
    def __validate_projects_inputs(self, name, pid, summary, overwrite):
        
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        if pid is not None and not isinstance(
                pid, int) and not isinstance(pid, np.int64):
            raise TypeError("pid must be an Integer")
        if not isinstance(summary, bool):
            raise TypeError("summary must be a Logical")
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a Logical")
            
        if pid is not None:
            self.__validate_pid(pid, name)
    
    def __validate_scenarios_inputs(self, name, sid, project, pid, overwrite,
                                    optional, summary, results):

        if name is not None and not isinstance(name, str)\
            and not isinstance(name, int)\
                and not isinstance(name, np.int64)\
                    and not isinstance(name, list):
            raise TypeError("name must be a String, Integer, or List of these")
            
        if isinstance(name, list) and isinstance(sid, list):
            name = None
            
        if isinstance(name, list):
           if not all(isinstance(item, int) for item in name)\
               and not all(isinstance(item, str) for item in name):
               raise TypeError("All values in name list must be either" + 
                               " Strings or Integers")
               
        if project is not None and project.__class__.__name__ != "Project":
            if not isinstance(project, str) and not isinstance(project, int):
                raise TypeError(
                    "project must be Project instance, String, or Integer")
                
        if sid is not None and not isinstance(sid, int)\
            and not isinstance(sid, np.int64)\
                and not isinstance(sid, list):
            raise TypeError("sid must be an Integer or List of Integers")
            
        if isinstance(sid, list):
            if not all(isinstance(item, int) for item in sid):
                raise TypeError("All values in sid list must be Integers")
                
        if pid is not None and not isinstance(
                pid, int) and not isinstance(pid, np.int64):
            raise TypeError("pid must be an Integer")
            
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a Logical")
            
        if not isinstance(optional, bool):
            raise TypeError("optional must be a Logical")
            
        if not isinstance(summary, bool) and summary is not None:
            raise TypeError("summary must be a Logical or None")
            
        if not isinstance(results, bool):
            raise TypeError("results must be a Logical")
    
    def __validate_datasheets_inputs(self, name, summary, optional, empty,
                                     filter_column, include_key, 
                                     return_hidden):
            
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        if not isinstance(summary, bool):
            raise TypeError("summary must be a Logical")
        if not isinstance(optional, bool):
            raise TypeError("optional must be a Logical")
        if not isinstance(empty, bool):
            raise TypeError("empty must be a Logical")
        if not isinstance(filter_column, str) and filter_column is not None:
            raise TypeError("filter_column must be a String")
        if not isinstance(include_key, bool):
            raise TypeError("include_key must be a Logical")
        if not isinstance(return_hidden, bool):
            raise TypeError("return_hidden must be a Logical")
            
    def __validate_run_inputs(self, scenarios, project,
                               copy_external_inputs):
    
        if scenarios is not None and not isinstance(
                scenarios, ps.Scenario) and not isinstance(
                    scenarios, int) and not isinstance(
                    scenarios, np.int64) and not isinstance(
                        scenarios, str) and not isinstance(
                            scenarios, list):
            raise TypeError(
                "scenarios must be Scenario instance, String, Integer, or List")
        if project is not None and not isinstance(
                project, ps.Project) and not isinstance(
                    project, int) and not isinstance(
                    project, np.int64) and not isinstance(project, str):
            raise TypeError(
                "project must be Project instance, String, or Integer")
        if not isinstance(copy_external_inputs, bool):
            raise TypeError("copy_external_inputs must be a Logical")
            
    
    def __initialize_export_args(self, scope, ids, empty, include_key, show_full_paths):
    
        args = ["--export", "--lib=%s" % self.__location]
        
        if scope == "Project" and len(ids) > 0:
            args += ["--pid=%d" % ids]
        
        if scope == "Scenario" and len(ids) > 0:               
            args += ["--sid=%d" % ids]
            
        if empty:
            args += ["--schemaonly"]
            
        if include_key:
            args += ["--includepk"]
        
        if show_full_paths:
            args += ["--extfilepaths"]
            
        return args
    
    def __find_filter_column_args(self, filter_column, filter_value, name, scope,
                                ids):
        
        # Check that filter_value is not None
        if filter_value is None:
            raise ValueError("Must specify a filter_value to filter the " +
                             "filter_column by")
        
        # Check if filter_column exists in Datasheet
        check_args = ["--list", "--columns",
                      "--lib=%s" % self.location, 
                      "--sheet=%s" % name]
        ds_cols = self.__console_to_csv(check_args)
        
        if filter_column not in ds_cols.Name.values:
            raise ValueError(
                f"filter column {filter_column} not in Datasheet {name}")
           
        try:
            
            filter_value = int(filter_value)
            
        except ValueError:
                
            # Initialize Datasheets summary
            # TODO: find out why Library and project scoped datasheets not showing up
            self.__init_datasheets(scope=scope, summary=True)
            
            ds_row = self.__datasheets[self.__datasheets.Name == name]
            
            if ds_row["Is Output"].values[0] == "Yes":
                input_sheet_name = ds_cols[
                    ds_cols.Name == filter_column].Formula1.values[0]
                filter_column = "Name" # TODO: Check if this is true for all cases
                
            else:
                input_sheet_name = name
            
            input_datasheet = self.__slow_query_datasheet(input_sheet_name,
                                                          scope, ids)
            
            if (input_datasheet[filter_column] != filter_value).all():
                raise ValueError(f"filter_value {filter_value} does not "+
                                 f"exist in filter_column {filter_column}")
            
            # Get primary key and ID for filter column/value
            primary_key = input_datasheet.columns[0]
            primary_value = input_datasheet[
                input_datasheet[filter_column] == filter_value
                ][primary_key].values[0]
            filter_column = primary_key
            filter_value = primary_value
        
        finally:

            self.__datasheets = None
            
            return filter_column, str(filter_value)
        
    def __find_datasheets_with_all_cols(self, ids):
        
        # Find out if datasheets contain any data
        optional_args = ["--list", "--datasources",
                         "--lib=%s" % self.location,
                         "--sid=%d" % ids]
        optional_cols = self.__console_to_csv(optional_args)
        optional_cols = optional_cols.replace({"No": False, 
                                               "Yes": True})
        
        if optional_cols["DataInherited"].sum() > 0:
            add_cols = ["Name", "Data", "DataInherited",
                        "DataSource"]
        else:
            add_cols = ["Name", "Data"]
        
        # Only retain relevant optional columns
        optional_cols = optional_cols[add_cols]
        
        # Merge optional columns with datasheets and return
        optional_ds = self.__datasheets.merge(optional_cols)
        
        return optional_ds
    
    def __return_summarized_datasheets(self, scope, summary, optional, ids):
    
        self.__init_datasheets(scope=scope, summary=summary)
        
        if optional is False:
            
            return self.__datasheets.iloc[:, 1:4]
        
        elif scope != "Scenario":
            
            return self.__datasheets
        
        else:
            
            optional_ds = self.__find_datasheets_with_all_cols(ids)
    
            return optional_ds
    
    def __return_list_of_full_datasheets(self, scope, args, return_hidden,
                                         ids):

        self.__init_datasheets(scope=scope, summary=True)
        d_summary = self.__datasheets.copy()
                        
        ds_list = []
        
        
        for ds in d_summary["Name"]:
            
            ds = self.__check_datasheet_name(ds)

            # Core LNG package datasheet cannot be exported
            if ds == "core_LNGPackage":
                continue
            
            if return_hidden:
                ds_full = self.__slow_query_datasheet(ds, scope, ids)
            else:
                ds_full = self.__fast_query_datasheet(ds, scope, args)
                
            ds_list.append(ds_full)
            
        return ds_list
    
    def __fast_query_datasheet(self, name, scope, args):
        
        # Refresh datasheets
        self.__datasheets=None
        
        # Add arguments
        fast_query_args = list(args)
        fast_query_args.append("--sheet=%s" % name)
        
        if name.startswith("core"):
            fast_query_args += ["--includesys"]
            
        self.__init_datasheets(scope=scope, summary=False,
                               name=name, args=fast_query_args)
        
        return self.__datasheets
    
    def __slow_query_datasheet(self, input_sheet_name, scope, ids):
        
        tempfile_path = self.__generate_tempfile_path()
        
        try:
            
            # Get datasheet
            args = ["--export", "--lib=%s" % self.location,
                    "--sheet=%s" % input_sheet_name, 
                    "--file=%s" % tempfile_path, "--includepk",
                    "--valsheets", "--extfilepaths", "--force"]
            
            if input_sheet_name.startswith("core"):
                args += ["--includesys"]
            
            # Check the scope of the input_sheet_name
            self.__init_datasheets(scope=scope, summary=True)
            args = self.__find_scope_id_args(input_sheet_name, scope, ids,
                                             args)
            
            self.session._Session__call_console(args)
            ds = pd.read_csv(tempfile_path)
            # ds = self.__remove_unnecessary_datasheet_columns(ds,
            #                                                  input_sheet_name)
        
        finally:
            
            if tempfile_path is not None and os.path.exists(tempfile_path):
                os.remove(tempfile_path)
            
        return ds

    def __delete_datasheet(self, scope, name, ids):

        args = ["--delete", "--data", "--lib=%s" % self.location,
                "--sheet=%s" % name, "--force"]
        if scope == "Project":
            args += ["--pid=%d" % ids]
        if scope == "Scenario":
            args += ["--sid=%d" % ids]
        
        result = self.__session._Session__call_console(args)

        if result.returncode == 0:
            print(f"{name} successfully deleted")
        else:
            raise RuntimeError(result.stderr)

    def __validate_delete_datasheet(self, force, append, scope, data):

        delete_or_warn = None

        if (data.empty) & (scope == "Scenario"):
            delete_or_warn = "delete"
        elif (data.empty) & (force is True):
            delete_or_warn = "delete"
        elif (append is False) & (force is True):
            delete_or_warn = "delete"

        if (force is False) & (append is False) & (scope == "Project"):
            delete_or_warn = "warn"
        elif (force is False) & (data.empty) & (scope == "Project"):
            delete_or_warn = "warn"
        elif (force is False) & (data.empty) & (scope == "Library"):
            delete_or_warn = "warn"

        return delete_or_warn

    def __save_datasheet_to_temp(self, data):

        temp_folder = tempfile.mkdtemp(prefix="SyncroSim-")
        fpath = '{}\\export.csv'.format(temp_folder)
        data.to_csv(fpath, index=False)

        if not os.path.isfile(fpath):
            raise RuntimeError(f"file path {fpath} does not exist")

        return fpath
    
    def __generate_tempfile_path(self):
        
        temp_folder = self.location + "temp"

        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        
        tempfile_path = os.path.join(temp_folder,
                                     "temp.csv")
        
        return tempfile_path
    
    def __find_scope_id_args(self, input_sheet_name, scope, ids, args):
        
        scope_list = ["Project", "Scenario", "Library"]

        if (self.__datasheets.Name == input_sheet_name).any():
            
            input_scope = scope
            
            if input_scope == "Project" and len(ids) > 0:
                args += ["--pid=%d" % ids[0]]
            
            if input_scope == "Scenario" and len(ids) > 0:               
                args += ["--sid=%d" % ids[0]]
                
        else:
            scope_list.remove(scope)
            input_scope = scope_list[0]
                
            if input_scope == "Project" and len(ids) > 0:
                if scope == "Scenario":
                    pid = self.scenarios(sid=ids[0]).project.pid
                else:
                    pid = ids[0]
                args += ["--pid=%d" % pid]
            
            if input_scope == "Scenario" and len(ids) > 0:               
                args += ["--sid=%d" % ids[0]]
                
        return args
    
    def __remove_unnecessary_datasheet_columns(self, ds, input_sheet_name):
        
        ds = ds.dropna(axis=1)
        id_column = input_sheet_name.split("_")[1] + "ID"
        ds = ds.drop([id_column], axis=1)
        
        return ds
    
    def __generate_scenarios_list_to_run(self, scenarios, project):
    
        if scenarios is None:
            
            scenario_list = self.__find_scenarios_from_project(project)
            
            return scenario_list
                    
        elif scenarios is not None:
                
            if not isinstance(scenarios, list):
                scenarios = [scenarios]
                
            if isinstance(scenarios[0], int) or isinstance(scenarios[0], np.int64):
                scenario_list = [
                    self.scenarios(sid=scn) for scn in scenarios]
            elif isinstance(scenarios[0], str):
                scenario_list = [
                    self.scenarios(
                        name=scn, project=project) for scn in scenarios]
            else:
                scenario_list = scenarios
    
            return scenario_list
        
    def __find_scenarios_from_project(self, project):
        
        if project is None:
            
            if len(self.projects()) == 1:
                project = self.projects(
                    pid=self.__projects.ProjectId.item())
                
            else:
                raise ValueError(
                    "Must specify project when > 1 Project in the Library")
        
        # Convert project to Project instance
        if isinstance(project, int) or isinstance(project, np.int64):
            project = self.projects(pid=project)
            
        if isinstance(project, str):
            project = self.projects(name=project)
            
        # Run all Scenarios in a Project
        scenario_list = project.scenarios(summary=False)
        
        if not isinstance(scenario_list, list):
            scenario_list = [scenario_list]
            
        return scenario_list
    
    def __get_library_structure(self):

        args = ["--list", "--library", "--lib=%s" % self.location,
                "--tree"]
        lib_structure = self.session._Session__call_console(args, decode=True)
        lib_structure = lib_structure.replace("|", " ")
        lib_structure = lib_structure.split("\r\n")
        lib_structure.remove('')

        level = []
        item = []
        ssim_id = []

        for i in range(0, len(lib_structure)):
            if i == 0:
                level.append(i)
                item.append("Library")
                ssim_id.append(0)
            else:
                l = (len(lib_structure[i]) - len(lib_structure[i].lstrip())) / 3

                start = "+- "
                end = " ["
                it = lib_structure[i][lib_structure[i].find(start) + len(start):lib_structure[i].find(end)]
                it = it.replace("*", "")

                start = "["
                end = "]"
                obj_id = lib_structure[i][lib_structure[i].find(start) + len(start):lib_structure[i].find(end)]

                level.append(l)
                item.append(it)
                ssim_id.append(obj_id)

        return pd.DataFrame({"level": level, "item": item, "id": ssim_id})