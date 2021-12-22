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

pd.set_option("max_columns", 5)

class Library(object):
    """
    A class to represent a SyncroSim Library.
    
    ...
    
    Attributes
    ----------
    session : Session
        Retrieves the Session associated with this Library.
    name : String
        Retrieves or sets the name of this Library.
    location : String
        Retrieves the file path to this Library.
    package : String
        Retrieves the package this Library is using.
    addons : pandas DataFrame
        Retrieves the addon(s) this Library is using.
    info : pandas DataFrame
        Retrieves information about this Library.
    owner : String
        Gets or sets the owner of this Library.
    readonly : String
        Gets or sets the read-only status of this Library.
    description : String
        Gets or sets the description for this Library.
    date_modified : String
        Retrieves the last date this Library was modified.
    
    Methods
    -------
    projects(name=None, pid=None, summary=True, overwrite=False):
        Creates or opens one or more SyncroSim Projects in the Library.
    scenarios(name=None, project=None, sid=None, pid=None, overwrite=False,
              optional=False, summary=True):
        Retrieves a Scenario or DataFrame of Scenarios in this Library.
    datasheets(name=None, summary=True, optional=False, empty=False,
               scope="Library", filter_column=None, *ids):
        Retrieves a DataFrame of Library Datasheets.
    delete(project=None, scenario=None, force=False):
        Deletes a SyncroSim class instance.
    save_datasheet(name, data, scope="Library", *ids):
        Saves a pandas DataFrane as a SyncroSim Datasheet.
    run(scenarios=None, project=None, jobs=1):
        Runs a list of Scenario objects.
    update():
        Updates a SyncroSim Library.
    backup():
        Creates a backup of a SyncroSim Library.
    enable_addons(name):
        Enable addon package(s) of a SyncroSim Library.
    disable_addons(name):
        Disable addon package(s) of a SyncroSim Library.    
        
    """
    __projects = None
    __scenarios = None
    __datasheets = None
    
    def __init__(self, location, session): # dja make the name more intuitive as well as matching the docstring name and internal consistentcy
        """
        Initializes a pysyncrosim Library instance.

        Parameters
        ----------
        loc : String
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
        self.__readonly = value
        
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
        self.__description = value
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
            if pid not in self.__projects["ID"].values:
                raise ValueError(f"Project ID {pid} does not exist")
            elif name is not None and name != self.__projects[
                    self.__projects["ID"] == pid]["Name"].values[0]:
                raise ValueError(
                    f"Project ID {pid} does not match Project name {name}")
          
        p = self.__get_project(name=name, pid=pid)
        
        if p is None:
            
            if summary is True:
                
                # Return DataFrame of Project information
                if name is not None:
                    return self.__projects[self.__projects.Name == name]
                if pid is not None:
                    return self.__projects[self.__projects.ID == pid]
                else:
                    return self.__projects
                
            if summary is False:
        
                proj_list = []
                
                for i in range(0, len(self.__projects)):
                    
                    proj = ps.Project(self.__projects["ID"].loc[i],
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
            pid = p["ID"].values[0].tolist()
            
            return ps.Project(pid, p["Name"].values[0], self)
                
        else:
            
            # Convert np.int64 to native int
            pid = p["ID"].values[0].tolist()
             
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
            Scenario ID. The default is None.
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
        
        if (sid is not None and len(sid) == 1)\
            and (name is not None and len(name) == 1):
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
                   scope="Library", filter_column=None, include_key=False, 
                   *ids):
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
            The column and value to filter the output Datasheet by 
            (e.g. "TransitionGroupID=20"). The default is None.
        include_key : Logical, optional
            Whether to include the primary key of the Datasheet, corresponding
            to the SQL database. Default is False.

        Returns
        -------
        pandas.DataFrame
            If `optional=False`, then returns a DataFrame of Datasheet 
            information including Package, Name, and Display Name.
            If `optional=True`, also returns Scope, Is Single, and Is Output.

        """
        # Type checks
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        if not isinstance(summary, bool) and summary != "CORE":
            raise TypeError("summary must be a Logical or 'CORE'")
        if not isinstance(optional, bool):
            raise TypeError("optional must be a Logical")
        if not isinstance(empty, bool):
            raise TypeError("empty must be a Logical")
        
        self.__datasheets = None
        
        # Initialize base arguments
        args = ["--export", "--lib=%s" % self.__location]
        
        if scope == "Project" and len(ids) > 0:
            args += ["--pid=%d" % ids]
        
        if scope == "Scenario" and len(ids) > 0:               
            args += ["--sid=%d" % ids]
            
        if empty:
            args += ["--schemaonly"]
            
        if include_key:
            args += ["--includepk"]
         
        # Can only use filter_column arg if name of Datasheet is specified
        if (filter_column is not None) and (name is not None):
            # Check if filter_column exists in Datasheet
            col = filter_column.split("=")[0]
            col_id = filter_column.split("=")[1]
            check_args = ["--list", "--columns",
                          "--lib=%s" % self.location, 
                          "--sheet=%s" % name]
            ds_cols = self.__console_to_csv(check_args)
            
            if col not in ds_cols.Name.values:
                raise ValueError(
                    f"filter column {col} not in Datasheet {name}")
                
            try:
                
                col_id = int(col_id)
                
            except ValueError:
                    
                # Initialize Datasheets summary
                # TODO: find out why Library and project scoped datasheets not showing up
                self.__init_datasheets(scope=scope, summary=True)
                
                ds_row = self.__datasheets[self.__datasheets.Name == name]
                
                if ds_row["Is Output"].values[0] == "Yes":
                    input_sheet_name = ds_cols[
                        ds_cols.Name == col].Formula1.values[0]
                else:
                    input_sheet_name = name
                
                tempfile_path = os.path.join(self.location + ".temp",
                                             "temp.csv")
                check_args = ["--export", "--lib=%s" % self.location,
                              "--sheet=%s" % input_sheet_name, 
                              "--file=%s" % tempfile_path, "--includepk",
                              "--valsheets", "--extfilepaths", "--force"]
                
                # Check the scope of the input_sheet_name
                scope_list = ["Project", "Scenario"]
                
                if (self.__datasheets.Name == input_sheet_name).any():
                    
                    input_scope = scope
                    
                    if input_scope == "Project" and len(ids) > 0:
                        check_args += ["--pid=%d" % ids]
                    
                    if input_scope == "Scenario" and len(ids) > 0:               
                        check_args += ["--sid=%d" % ids]
                        
                else:
                    scope_list.remove(scope)
                    input_scope = scope_list[0]
                        
                    if input_scope == "Project" and len(ids) > 0:
                        if scope == "Scenario":
                            pid = self.scenarios(sid=121).project.pid
                        else:
                            pid = ids
                        check_args += ["--pid=%d" % pid]
                    
                    if input_scope == "Scenario" and len(ids) > 0:               
                        check_args += ["--sid=%d" % ids]
                
                self.session._Session__call_console(check_args)
                input_datasheet = pd.read_csv(tempfile_path)
                col_id = input_datasheet[
                    input_datasheet.Name == col_id][col].values[0]
                # TODO: subset to find correct column / ID
            
            finally:
                if os.path.exists(tempfile_path):
                    os.remove(tempfile_path)
                self.__datasheets = None
            
            # If all checks pass, then add filter_column to args
            args += ["--filtercol=%s" % col + "=" + str(col_id)]
        
        if name is None:
            
            # Return DataFrame of Datasheets
            if summary is True or summary == "CORE":
                self.__init_datasheets(scope=scope, summary=summary)
                if optional is False:
                    self.__datasheets = self.__datasheets.iloc[:, 1:4]
                    
                return self.__datasheets
        
            # Return List of DataFrames
            if summary is False:
            
                self.__init_datasheets(scope=scope, summary=True)
                d_summary = self.__datasheets.copy()
                self.__datasheets = None
                                
                ds_list = []
                
                # Add arguments
                args += ["--sheet"]
                
                for ds in d_summary["Name"]:
                    args[-1] = "--sheet=%s" % ds
                    self.__datasheets = None
                    self.__init_datasheets(scope=scope, summary=False,
                                           name=ds, args=args)
                    ds_list.append(self.__datasheets)
                    
                return ds_list
        
        if name is not None:
            
            # If package is not included in name, add it
            if name.startswith(self.package) is False:
                if name.startswith("core") is False:
                    name = self.package + "_" + name
            
            # Add arguments
            args += ["--sheet=%s" % name] 
            
            if name.startswith("core"):
                args += ["--includesys"]
                
            self.__init_datasheets(scope=scope, summary=False,
                                   name=name, args=args)
            
            return self.__datasheets
        
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
            
            helper._delete_library(name = self.name, session=self.session,
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
                args = ["--import", "--lib=%s" % self.name,
                        "--sheet=%s" % name, "--folder=%s" % temp_folder,
                        "--file=%s" % fpath]

                if scope == "Project":
                    args += ["--pid=%d" % ids]

                if scope == "Scenario":
                    args += ["--sid=%d" % ids]

                self.__session._Session__call_console(args)

            finally:
                shutil.rmtree(temp_folder, ignore_errors=True)
            
    def run(self, scenarios=None, project=None, jobs=1):
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
                    project = self.projects(pid=self.__projects.ID.item())
                    
                else:
                    raise ValueError(
                        "Must specify project when > 1 Project in the Library")
            
            # Convert project to Project instance
            if isinstance(project, int):
                project = self.projects(pid=project)
            if isinstance(project, str):
                project = self.projects(name=project)
                
            # Run all Scenarios in a Project
            result_list = [
                scn.run(
                    jobs=jobs) for scn in project.scenarios(summary=False)]
                    
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

            result_list = [scn.run(jobs=jobs) for scn in scenario_list]
            
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
            
    def __get_project(self, name=None, pid=None):
        # Retrieves Project info from the name or ID
        if name is None and pid is None:
            return None
        if name is not None:
            return self.__projects[self.__projects["Name"] == name]
        else:
            return self.__projects[self.__projects["ID"] == pid]
            
    def __get_scenario(self, name=None, sid=None):
        # Retrieves Scenario info from the name or ID
        if name is None and sid is None:
            return None
        if name is not None:
            return self.__scenarios[self.__scenarios["Name"] == name]
        else:
            return self.__scenarios[self.__scenarios["Scenario ID"] == sid]
        
    def __extract_scenario(self, name, project, sid, pid, overwrite, optional,
                           summary, results):
        
        # Find out if first argument is a Scenario ID
        if isinstance(name, int):
            
            if sid is not None:
                raise ValueError("Name is specified as a Scenario ID, but " + 
                                 "sid is already given")
                
            sid = name
            name = None
        
        # Set default summary argument
        if summary is None:
            
            if sid is None and name is None:
                summary = True
            else:
                summary = False
        
        # Find project if not specified
        if project is None and pid is None:
            
            self.__init_scenarios()
            if sid is not None and self.__get_scenario(sid=sid).empty is False:
                pid = self.__get_scenario(sid=sid)["Project ID"].item()
                project = self.projects(pid=pid)
            if name is not None and len(self.__get_scenario(name=name)) == 1:
                pid = self.__get_scenario(name=name)["Project ID"].item()
                project = self.projects(pid=pid)
            elif self.__projects is None or self.__projects.empty:
                project = self.projects(name = "Definitions")
                pid = project.pid
            elif len(self.__projects) == 1:
                pid = self.__projects.ID.item()
                project = self.projects(pid=pid)
            else:
                raise ValueError("More than one Project in Library." + 
                                 "Please specify a Project.")
                
        elif isinstance(project, int) or isinstance(project, np.int64):
            pid = project
        elif isinstance(project, str):
            pid = self.__projects[
                self.__projects.Name == project].ID.item()
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
                    ds =  self.__scenarios[['Scenario ID',
                                            'Project ID',
                                            'Name',
                                            'Is Result']]
                else:
                    ds = self.__scenarios
                    
                if results:
                    ds = ds[ds["Is Result"] == "Yes"]
                
                if name is not None:
                    return ds[ds.Name == name]
                
                if sid is not None:
                    return ds[ds["Scenario ID"] == sid]
                
                return ds
              
            # Return list of Scenario objects    
            if summary is False:
                
                s_summary = self.__scenarios
                s_summary = s_summary[s_summary["Is Result"] == "No"]
                
                if not isinstance(project, ps.Project):
                    project = self.projects(pid=pid) 
                                
                scn_list = []
                
                for i in range(0, len(s_summary)):
                    
                    scn = ps.Scenario(s_summary["Scenario ID"].loc[i],
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
                pid = p["ID"].values[0]
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
            
            return ps.Scenario(s["Scenario ID"].values[0],
                               s["Name"].values[0], project, self)
        
        # Open a Scenario
        else:
                            
            # Retrieve the name of a Scenario using only the sid
            pid = s["Project ID"].values[0].tolist()

            if not isinstance(project, ps.Project):
                project = self.projects(pid=pid)

            sid = s["Scenario ID"].values[0].tolist()
            
            return ps.Scenario(sid, s["Name"].values[0], project, self)
        
    def __console_to_csv(self, args, index_col=None):
        # Turns console output into a pd.DataFrame
        console_output = self.session._Session__call_console(
            args,
            decode=True,
            csv=True)
        
        return pd.read_csv(io.StringIO(console_output), index_col=index_col)
        
        
        
        

