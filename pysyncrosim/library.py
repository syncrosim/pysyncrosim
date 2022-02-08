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
    
    def __init__(self, location, session): # dja make the name more intuitive as well as matching the docstring name and internal consistentcy
        """
        Initializes a pysyncrosim Library instance.

        Parameters
        ----------
        location : String
            Filepath to Library location on disk.
        session : Session
            pysyncrosim Session instance.

        Returns
        -------
        None.

        """
        self.__name = os.path.basename(location) # dja Changed to use new parameter name.  Changed to using the os.path function basename as this makes script more understandable and pythonic 
        self.__session = session
        self.__location = location  # dja needed to match the name change in the class definition
        self.__addons = self.__init_addons()
        self.__info = None
        self.__package = None
        self.__owner = None
        self.__date_modified = None
        self.__readonly = None
        # All above attributes get created by below function
        self.__init_info()
        self.__description = self.__init_description()

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
    def package(self):
        """
        Retrieves the package this Library is using.

        Returns
        -------
        String
            Package name.

        """
        return self.__package
    
    @property
    def addons(self):
        """
        Retrieves the addon(s) this Library is using.

        Returns
        -------
        String
            Addon name(s).

        """
        return self.__addons
    
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
        
        # Add unit tests for argument types later
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        if pid is not None and not isinstance(
                pid, int) and not isinstance(pid, np.int64):
            raise TypeError("pid must be an Integer")
        if not isinstance(summary, bool):
            raise TypeError("summary must be a Logical")
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be a Logical")
        
        if overwrite is True:
            self.delete(project=name)
        
        self.__init_projects()
        
        # If pid provided, check that pid exists
        if pid is not None:
            if pid not in self.__projects["ProjectID"].values:
                raise ValueError(f"Project ID {pid} does not exist")
            elif name is not None and name != self.__projects[
                    self.__projects["ProjectID"] == pid]["Name"].values[0]:
                raise ValueError(
                    f"Project ID {pid} does not match Project name {name}")
          
        p = self.__get_project(name=name, pid=pid)
        
        if p is None:
            
            if summary is True:
                
                # Return DataFrame of Project information
                if name is not None:
                    return self.__projects[self.__projects.Name == name]
                if pid is not None:
                    return self.__projects[self.__projects.ProjectID == pid]
                else:
                    return self.__projects
                
            if summary is False:
        
                proj_list = []
                
                for i in range(0, len(self.__projects)):
                    
                    proj = ps.Project(self.__projects["ProjectID"].loc[i],
                                      self.__projects["Name"].loc[i],
                                      self)
                    
                    proj_list.append(proj)
    
                return proj_list   
            
        elif p.empty:
             
            # If specified Project does not exist, then create it    
            args = ["--create", "--project", "--lib=%s" % self.__location,
                    "--name=%s" % name]
            self.session._Session__call_console(args)
            
            # Reset Projects
            self.__projects = None
            self.__init_projects()
            p = self.__get_project(name, pid)
            
            # Convert np.int64 to native int
            pid = p["ProjectID"].values[0].tolist()
            
            return ps.Project(pid, p["Name"].values[0], self)
                
        else:
            
            # Convert np.int64 to native int
            pid = p["ProjectID"].values[0].tolist()
             
            return ps.Project(pid, p["Name"].values[0], self)
                
        
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
        # Check types
        if name is not None and not isinstance(name, str)\
            and not isinstance(name, int)\
                and not isinstance(name, list):
            raise TypeError("name must be a String, Integer, or List of these")
            
        if isinstance(name, list) and isinstance(sid, list):
            name = None
            
        if isinstance(name, list):
           if not all(isinstance(item, int) for item in name)\
               and not all(isinstance(item, str) for item in name):
               raise TypeError("All values in name list must be either" + 
                               " Strings or Integers")
        elif name is not None:
            name = [name]
               
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
        elif sid is not None:
            sid = [sid]
                
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
          
        # Set the summary argument
        if summary is None:
            if name is not None or sid is not None:
                summary = False
            else:
                summary = True
        
        if (sid is not None and len(sid) == 1)\
            and (name is not None and len(name) == 1):
                print("Both Scenario ID and name specified, using Scenario ID")
                output = self.__extract_scenario(None, project, sid[0], pid,
                                                 overwrite, optional, summary,
                                                 results)
        elif sid is not None:
            output = [self.__extract_scenario(
                name, project, s, pid, overwrite, optional, summary, results
                ) for s in sid]
        elif name is not None:
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
        
        
    def datasheets(self, name=None, summary=True, optional=False, empty=False,
                   scope="Library", filter_column=None, filter_value=None,
                   include_key=False, return_hidden=False, *ids):
        """
        Retrieves a DataFrame of Library Datasheets.

        Parameters
        ----------
        name : String, optional
            Datasheet name. The default is None.
        summary : Logical or String, optional
            Whether to list package Datasheets or core Datasheets. The default
            is True.
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
        
        args = self.__initialize_export_args(scope, ids, empty, include_key)
        
        if name is None:
            
            if summary is True or summary == "CORE":
                
                ds_frame = self.__return_summarized_datasheets(scope, summary,
                                                               optional, ids)
                
                return ds_frame
        
            if summary is False:
                
                ds_list = self.__return_list_of_full_datasheets(scope, args,
                                                                return_hidden,
                                                                ids)
                    
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
    
    def save_datasheet(self, name, data, scope="Library", *ids):
        """
        Saves a pandas DataFrane as a SyncroSim Datasheet.

        Parameters
        ----------
        name : String
            Name of the Datasheet.
        data : pandas DataFrame
            DataFrame of Datasheet values.
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
        if not isinstance(scope, str):
            raise TypeError("scope must be a String")
          
        # Add package name to Datasheet name if not included
        if name.startswith(self.package) is False:
            if name.startswith("core") is False:
                name = self.package + "_" + name
            
        # Check if running in a SyncroSim environment from the user interface
        e = _environment()
        transfer_dir = e.transfer_directory.item()
        
        # If running from user interface, save data to transfer directory
        if transfer_dir is not None:
            fpath = '{}\\SSIM_OVERWRITE-{}.csv'.format(transfer_dir, name)
            data.to_csv(fpath, index=False)
            return
        
        # Otherwise export the data to SyncroSim
        else:
            try:
                temp_folder = tempfile.mkdtemp(prefix="SyncroSim-")
                fpath = '{}\\export.csv'.format(temp_folder)
                data.to_csv(fpath, index=False)

                if not os.path.isfile(fpath):
                    raise RuntimeError(f"file path {fpath} does not exist")

                # Specify import arguments
                args = ["--import", "--lib=%s" % self.location,
                        "--sheet=%s" % name, "--folder=%s" % temp_folder,
                        "--file=%s" % fpath]

                if scope == "Project":
                    args += ["--pid=%d" % ids]

                if scope == "Scenario":
                    args += ["--sid=%d" % ids]

                result = self.__session._Session__call_console(args)
                
                if result.returncode == 0:
                    print(f"{name} saved successfully")

            finally:
                shutil.rmtree(temp_folder, ignore_errors=True)
            
    def run(self, scenarios=None, project=None, jobs=1,
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
        jobs : Int, optional
            Number of multiprocessors to use. The default is 1.
        copy_external_inputs : Logical, optional
            If False, then a copy of external input files (e.g. GeoTIFF files)
            is not created for each job. Otherwise, a copy of external inputs 
            is created for each job. Applies only when jobs > 1. The default is
            False.

        Returns
        -------
        result_dict : Dictionary
            Dictionary of Results Scenarios.

        """
        # Type checks
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
        if not isinstance(jobs, int) and not isinstance(jobs, np.int64):
            raise TypeError("jobs must be an Integer")
        
        # Collect output in a dictionary
        result_list = []
        
        if scenarios is None:
            
            if project is None:
                
                if len(self.projects()) == 1:
                    project = self.projects(
                        pid=self.__projects.ProjectID.item())
                    
                else:
                    raise ValueError(
                        "Must specify project when > 1 Project in the Library")
            
            # Convert project to Project instance
            if isinstance(project, int):
                project = self.projects(pid=project)
            if isinstance(project, str):
                project = self.projects(name=project)
                
            # Run all Scenarios in a Project
            scenarios = project.scenarios(summary=False)
            
            if not isinstance(scenarios, list):
                scenarios = [scenarios]
            
            result_list = [
                scn.run(
                    jobs=jobs, copy_external_inputs=copy_external_inputs
                    ) for scn in scenarios]
                    
        elif scenarios is not None:
                
            if not isinstance(scenarios, list):
                scenarios = [scenarios]
                
            if isinstance(scenarios[0], int):
                scenario_list = [
                    self.scenarios(sid=scn) for scn in scenarios]
            elif isinstance(scenarios[0], str):
                scenario_list = [
                    self.scenarios(
                        name=scn, project=project) for scn in scenarios]
            else:
                scenario_list = scenarios

            result_list = [scn.run(
                jobs=jobs, copy_external_inputs=copy_external_inputs
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
        
        if ds.IncludeInput[0] == "Yes":
            args += ["--input"]
            
        if ds.IncludeOutput[0] == "Yes":
            args += ["--output"]
        
        self.session._Session__call_console(args)
        
    def enable_addons(self, name):
        """
        Enable addon package(s) of a SyncroSim Library.

        Parameters
        ----------
        name : String or List
            Name of addon(s).

        Raises
        ------
        ValueError
            addon does not exist in available addons for this Library.

        Returns
        -------
        None.

        """
        
        # Type checks and convert to list
        if not isinstance(name, list):
            if not isinstance(name, str):
                raise TypeError("name must be a String or List of Strings")
            else:
                name = [name]
        elif all(isinstance(x, str) for x in name) is False:
            raise TypeError("all elements in name must be Strings")
            
            
        for a in name:
            args = ["--create", "--addon", "--lib=%s" % self.location,
                    "--name=%s" % a]
            try:
                self.session._Session__call_console(args)
                
            # Convert SyncroSim console error to print output
            except RuntimeError as e:
                print(e)
                return
         
        # Reset addons
        self.__addons = self.__init_addons()
    
    def disable_addons(self, name):
        """
        Disable addon package(s) of a SyncroSim Library.

        Parameters
        ----------
        name : String
            Name of addon package(s).

        Raises
        ------
        ValueError
            addon does not exist in available addons for this Library.

        Returns
        -------
        None.

        """
        
        # Type checks and convert to list
        if not isinstance(name, list):
            if not isinstance(name, str):
                raise TypeError("name must be a String or List of Strings")
            else:
                name = [name]
        elif all(isinstance(x, str) for x in name) is False:
            raise TypeError("all elements in name must be Strings")
            
        for a in name:
            args = ["--delete", "--addon", "--force",
                    "--lib=%s" % self.location, "--name=%s" % a]
            try:
                self.session._Session__call_console(args)
                
            # Convert SyncroSim console error to print output
            except RuntimeError as e:
                print(e)
                return
            
        # Reset addons
        self.__addons = self.__init_addons()
        
    def __init_addons(self):   
        # Retrieves addons information
        args = ["--list", "--addons", "--lib=%s" % self.location]
        return self.__console_to_csv(args)
    
    def __init_info(self):
        # Retrieves Library info
        args = ["--list", "--library", "--lib=%s" % self.location]
        lib_info = self.__console_to_csv(args)
        self.__info = lib_info
        
        # Set index and retrieve all properties
        lib_info = lib_info.set_index("Property")
        self.__package = lib_info.loc["Package Name:"].item()
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
            
    def __init_scenarios(self, pid=None):
        # Retrieves a list of Scenarios
        args = ["--list", "--scenarios", "--lib=%s" % self.__location]
        if pid is not None:
            args += ["--pid=%d" % pid]
        self.__scenarios = self.__console_to_csv(args)
            
    def __init_datasheets(self, scope, summary, name=None, args=None):
        # Retrieves a list of Datasheets
        if self.__datasheets is None:
            if summary is True:
                args = ["--list", "--datasheets", "--lib=%s" % self.__location,
                        "--scope=%s" % scope]
            if summary == "CORE":
                args = ["--list", "--datasheets", "--lib=%s" % self.__location,
                        "--scope=%s" % scope, "--includesys"]
            self.__datasheets = self.__console_to_csv(args)    
            
    def __check_datasheet_name(self, name):
        # Appends package name to Datasheet name
        if name.startswith(self.package) is False:
            if name.startswith("core") is False:
                name = self.package + "_" + name
        return name
            
    def __get_project(self, name=None, pid=None):
        # Retrieves Project info from the name or ID
        if name is None and pid is None:
            return None
        if name is not None:
            return self.__projects[self.__projects["Name"] == name]
        else:
            return self.__projects[self.__projects["ProjectID"] == pid]
            
    def __get_scenario(self, name=None, sid=None):
        # Retrieves Scenario info from the name or ID
        if name is None and sid is None:
            return None
        if name is not None:
            return self.__scenarios[self.__scenarios["Name"] == name]
        else:
            return self.__scenarios[self.__scenarios["ScenarioID"] == sid]
        
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
            if project is None and pid is None:
                
                self.__init_scenarios()
                if sid is not None and self.__get_scenario(sid=sid).empty is False:
                    pid = self.__get_scenario(sid=sid)["ProjectID"].item()
                    project = self.projects(pid=pid)
                if name is not None and len(self.__get_scenario(name=name)) == 1:
                    pid = self.__get_scenario(name=name)["ProjectID"].item()
                    project = self.projects(pid=pid)
                elif self.__projects is None or self.__projects.empty:
                    project = self.projects(name = "Definitions")
                    pid = project.pid
                elif len(self.__projects) == 1:
                    pid = self.__projects.ProjectID.item()
                    project = self.projects(pid=pid)
                else:
                    raise ValueError("More than one Project in Library." + 
                                     " Please specify a Project.")
                    
            elif isinstance(project, int) or isinstance(project, np.int64):
                pid = project
            elif isinstance(project, str):
                pid = self.__projects[
                    self.__projects.Name == project].ProjectID.item()
            elif isinstance(project, ps.Project):
                pid = project.pid
                
            if overwrite is True:
                self.delete(project=project, scenario=name, force=True)
                    
        # Retrieve Scenario DataFrame
        self.__init_scenarios(pid=pid)
        
        # If sid provided, check that sid exists
        if sid is not None:
            
            if self.__get_scenario(sid=sid).empty:
                raise ValueError(f"Scenario ID {sid} does not exist")
            elif name is not None and name != self.__get_scenario(
                    sid=1).Name.item():
                raise ValueError(
                    f"Scenario ID {sid} does not match Scenario name {name}")
        
        s = self.__get_scenario(name=name, sid=sid)
        
        if (s is None) or (summary is True):
            
            # Retrieve DataFrame of available Scenarios
            if summary:
                
                if optional is False:
                    ds =  self.__scenarios[['ScenarioID',
                                            'ProjectID',
                                            'Name',
                                            'IsResult']]
                else:
                    ds = self.__scenarios
                    
                if results:
                    ds = ds[ds["IsResult"] == "Yes"]
                
                if name is not None:
                    return ds[ds.Name == name]
                
                if sid is not None:
                    return ds[ds["ScenarioID"] == sid]
                
                return ds
              
            # Return list of Scenario objects    
            if summary is False:
                
                s_summary = self.__scenarios
                s_summary = s_summary[s_summary["IsResult"] == "No"]
                
                if not isinstance(project, ps.Project):
                    project = self.projects(pid=pid) 
                                
                scn_list = []
                
                for i in range(0, len(s_summary)):
                    
                    scn = ps.Scenario(s_summary["ScenarioID"].loc[i],
                                      s_summary["Name"].loc[i],
                                      project, self)
                    
                    scn_list.append(scn)
    
                return scn_list                
        
        
        # Create a Scenario
        if s.empty:
            
            if isinstance(project, int):
                pid = project
            elif isinstance(project, str):
                self.__init_projects()
                p = self.__get_project(name=project)
                pid = p["ProjectID"].values[0]
            elif isinstance(project, ps.Project):
                pid = project.pid
             
            # Create Scenario using console    
            args = ["--create", "--scenario", "--pid=%d" % pid,
                    "--lib=%s" % self.__location, "--name=%s" % name]
            self.session._Session__call_console(args)
            
            # Reset Scenarios
            self.__scenarios = None
            self.__init_scenarios()
            s = self.__get_scenario(name=name, sid=sid)
            
            if not isinstance(project, ps.Project):
                project = self.projects(pid=pid)
            
            return ps.Scenario(s["ScenarioID"].values[0],
                               s["Name"].values[0], project, self)
        
        # Open a Scenario
        else:
                            
            # Retrieve the name of a Scenario using only the sid
            pid = s["ProjectID"].values[0].tolist()

            if not isinstance(project, ps.Project):
                project = self.projects(pid=pid)

            sid = s["ScenarioID"].values[0].tolist()
            
            return ps.Scenario(sid, s["Name"].values[0], project, self)

        
    def __console_to_csv(self, args, index_col=None):
        # Turns console output into a pd.DataFrame
        console_output = self.session._Session__call_console(
            args,
            decode=True,
            csv=True)
        
        return pd.read_csv(io.StringIO(console_output), index_col=index_col)
    
    def __validate_datasheets_inputs(self, name, summary, optional, empty,
                                     filter_column, include_key, 
                                     return_hidden):
            
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        if not isinstance(summary, bool) and summary != "CORE":
            raise TypeError("summary must be a Logical or 'CORE'")
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
            
    
    def __initialize_export_args(self, scope, ids, empty, include_key):
    
        args = ["--export", "--lib=%s" % self.__location]
        
        if scope == "Project" and len(ids) > 0:
            args += ["--pid=%d" % ids]
        
        if scope == "Scenario" and len(ids) > 0:               
            args += ["--sid=%d" % ids]
            
        if empty:
            args += ["--schemaonly"]
            
        if include_key:
            args += ["--includepk"]
            
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
        
        if optional_cols["Data Inherited"].sum() > 0:
            add_cols = ["Name", "Data", "Data Inherited",
                        "Data Source"]
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
        self.__datasheets = None
                        
        ds_list = []
        
        # Add arguments
        args += ["--sheet"]
        
        for ds in d_summary["Name"]:
            
            ds = self.__check_datasheet_name(ds)
            
            if return_hidden:
                ds_full = self.__slow_query_datasheet(ds, scope, ids)
            else:
                ds_full = self.__fast_query_datasheet(ds, scope, args)
                
            ds_list.append(ds_full)
            
        return ds_list
    
    def __fast_query_datasheet(self, name, scope, args):
        
        # Add arguments
        args += ["--sheet=%s" % name] 
        
        if name.startswith("core"):
            args += ["--includesys"]
            
        self.__init_datasheets(scope=scope, summary=False,
                               name=name, args=args)
        
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
            args = self.__find_scope_id_args(input_sheet_name, scope, ids,
                                             args)
            
            self.session._Session__call_console(args)
            ds = pd.read_csv(tempfile_path)
            ds = self.__remove_unnecessary_datasheet_columns(ds,
                                                             input_sheet_name)
        
        finally:
            
            if tempfile_path is not None and os.path.exists(tempfile_path):
                os.remove(tempfile_path)
            
        return ds
    
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
            
            if input_scope == "Project" and len(ids[0]) > 0:
                args += ["--pid=%d" % ids[0]]
            
            if input_scope == "Scenario" and len(ids[0]) > 0:               
                args += ["--sid=%d" % ids[0]]
                
        else:
            scope_list.remove(scope)
            input_scope = scope_list[0]
                
            if input_scope == "Project" and len(ids[0]) > 0:
                if scope == "Scenario":
                    pid = self.scenarios(sid=ids[0]).project.pid
                else:
                    pid = ids[0]
                args += ["--pid=%d" % pid]
            
            if input_scope == "Scenario" and len(ids[0]) > 0:               
                args += ["--sid=%d" % ids[0]]
                
        return args
    
    def __remove_unnecessary_datasheet_columns(self, ds, input_sheet_name):
        
        ds = ds.dropna(axis=1)
        id_column = input_sheet_name.split("_")[1] + "ID"
        ds = ds.drop([id_column], axis=1)
        
        return ds