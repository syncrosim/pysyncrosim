import pysyncrosim as ps
from pysyncrosim.environment import _environment
import os
# import pandas as pd
import numpy as np

class Scenario(object):
    """
    A class representing a SyncroSim Scenario.
    
    ...
    
    Attributes
    ----------
    sid : Int
        Retrieves Scenario ID.
    name : String
        Retrieves or sets a Scenario name.
    project : Project
        Retrieves Project class instance associated with this Scenario.
    library : Library
        Retrieves Library class instance associated with this Library.
    info : pandas DataFrame
        Retrieves Scenario information.
    owner : String
       Gets or sets the owner of this Scenario.
    date_modified : String
        Gets the last date this Scenario was modified.
    readonly : String
        Gets or sets the read-only status for this Scenario.
    project_id : Int
        Gets the Project ID associated with this Scenario.
    description : String
        Gets or sets the Scenario description.
    is_result : Logical
        Retrieves information about whether this Scenario is a Results
        Scenario or not
    parent_id : Int
        Retrieves the ID of the parent Scenario of a Results Scenario.
    
    Methods
    -------
    datasheets(name=None, summary=True, optional=False, empty=False):
        Retrieves a DataFrame of Scenario Datasheets.
    datasheet_raster(datasheet, column, iteration=None, timestep=None):
        Retrieves spatial data columns from one or more SyncroSim Datasheets.
    save_datasheet(name, data):
        Saves a pandas DataFrame as a SyncroSim Datasheet.
    delete(force=False):
        Deletes a Scenario.
    copy(name=None):
        Creates a copy of an existing Scenario class instance.
    dependencies(dependency=None, remove=False, force=False):
        Gets, sets, or removes dependencies from a Scenario.
    ignore_dependencies(value=None):
        Retrieves or sets the Datafeeds to ignore for a Scenario.
    merge_dependencies(value=None):
        Retrieves or sets whether or not a Scenario is configured to merge
        dependencies at run time.
    run(jobs=1):
        Runs a Scenario.
    run_log():
        Returns a run log for a Results Scenario.
    results(sid=None):
        Retrieves DataFrame of Results Scenarios or retrieves a Results 
        Scenario instance for this Scenario.
    
    """
    __datasheets = None
    __results = None
    
    def __init__(self, sid=None, name=None, project=None, library=None):
        self.__sid = sid
        self.__name = name
        self.__project = project
        self.__library = library
        
        # Initialize when in a SyncroSim environment
        if sid is None and name is None and project is None and \
            library is None:
            e = _environment()
            self.__library = ps.library(e.library_filepath.item())
            self.__project = self.__library.projects(
                pid=e.project_id.item())
            self.__sid = int(e.scenario_id.item())
            temp_df = self.__library.scenarios()
            self.__name = temp_df[
                temp_df["Scenario ID"] == self.__sid]["Name"].item()
            # revisit these!!
            self.__env = e.transfer_directory.item()
            self.__temp = e.temp_directory
        else:
            self.__env = None
        self.__owner = None
        self.__date_modified = None
        self.__readonly = None
        self.__project_id = None
        self.__info = None
        # All None attributes assigned in __init_info()
        self.__init_info()
        self.__description = self.__init_description()
        self.__is_result = self.__init_is_result()
        self.__parent_id = self.__init_parent_id()
        self.__dependencies = self.__init_dependencies()
        
    @property
    def sid(self):
        """
        Retrieves Scenario ID.

        Returns
        -------
        Int
            Scenario ID.

        """
        return self.__sid
    
    @property
    def name(self):
        """
        Retrieves or sets a Scenario name.
        
        Parameters
        ----------
        Value : String
            New Scenario name.

        Returns
        -------
        String
            Scenario name.

        """
        return self.__name
    
    @name.setter
    def name(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--name=%s" % value, "--sid=%d" % self.sid]
        self.library.session._Session__call_console(args)
        # Reset information
        self.__init_info()
        
    @property
    def project(self):
        """
        Retrieves Project class instance associated with this Scenario.

        Returns
        -------
        Project
            SyncroSim Project class instance.

        """
        return self.__project
    
    @property
    def library(self):
        """
        Retrieves Library class instance associated with this Library.

        Returns
        -------
        Library
            SyncroSim Library class instance.

        """
        return self.__library
    
    @property
    def info(self):
        """
        Retrieves Scenario information.

        Returns
        -------
        pandas DataFrame
            Scenario information.

        """
        return self.__info
    
    @property
    def owner(self):
        """
        Gets or sets the owner of this Scenario.

        Returns
        -------
        String
            Owner of this Scenario.

        """
        return self.__owner
    
    @owner.setter
    def owner(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--owner=%s" % value, "--sid=%d" % self.sid]
        self.library.session._Session__call_console(args)
        # Reset information
        self.__init_info()
        
    @property
    def date_modified(self):
        """
        Gets the last date this Scenario was modified.

        Returns
        -------
        String
            Last date modified.

        """
        return self.__date_modified
    
    @property
    def readonly(self):
        """
        Gets or sets the read-only status for this Scenario.

        Returns
        -------
        String
            "yes" if this Scenario is read-only, "no" otherwise.

        """
        return self.__readonly
    
    @readonly.setter
    def readonly(self, value):
        if value is True or value == "yes":
            ro = "yes"
        elif value is False or value == "no":
            ro = "no"
        else:
            raise TypeError("value must be a Logical")
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--readonly=%s" % ro, "--sid=%d" % self.sid]
        self.library.session._Session__call_console(args)
        # Reset information
        self.__init_info()
        
    @property
    def project_id(self):
        """
        Gets the Project ID associated with this Scenario.

        Returns
        -------
        Integer
            Project ID.

        """
        return self.__project_id
    
    @property
    def description(self):
        """
        Gets or sets the Scenario description.

        Returns
        -------
        String
            Scenario description.

        """
        return self.__description
    
    @description.setter
    def description(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location,
                "--description=%s" % value, "--sid=%d" % self.sid]
        self.library.session._Session__call_console(args)
        self.__description = self.__init_description()
    
    @property
    def is_result(self):
        """
        Retrieves information about whether this Scenario is a Results
        Scenario or not.

        Returns
        -------
        Logical
            Whether Scenario is a Results Scenario.

        """
        return self.__is_result
    
    @property
    def parent_id(self):
        """
        Retrieves the ID of the parent Scenario of a Results Scenario.

        Returns
        -------
        Int
            Parent ID of a Results Scenario.

        """
        return self.__parent_id
    
    def datasheets(self, name=None, summary=True, optional=False, empty=False):
        """
        Retrieves a DataFrame of Scenario Datasheets.
        
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
            If True, returns an empty Datasheet. The default is False.

        Returns
        -------
        pandas.DataFrame
            If `optional=False`, then returns a DataFrame of Datasheet 
            information including Package, Name, and Display Name.
            If `optional=True`, also returns Scope, Is Single, and Is Output.

        """
        
        self.__datasheets = self.library.datasheets(name, summary, optional,
                                                    empty, "Scenario", 
                                                    self.sid)
        return self.__datasheets
    
    def datasheet_raster(self, datasheet, column, iteration=None,
                          timestep=None):
        """
        Retrieves spatial data columns from one or more SyncroSim Datasheets.

        Parameters
        ----------
        datasheet : String
            The name of a SyncroSim Datasheet containing raster data.
        column : String
            The column in the Datasheet containing the raster data.
        iteration : Int or List, optional
            The iteration to subset by. The default is None.
        timestep : Int or List, optional
            The timestep to subset by. The default is None.

        Returns
        -------
        Raster or List of Rasters 
            Raster class instance or List of these.

        """
        # Type Checks
        if not isinstance(datasheet, str):
            raise TypeError("datasheet must be a String")
        if not isinstance(column, str):
            raise TypeError("column must be a String")
        if iteration is not None and not isinstance(
                iteration, int) and not isinstance(
                    iteration, np.int64) and not isinstance(iteration, list):
            raise TypeError("iteration must be an Integer or List")
        if timestep is not None and not isinstance(
                timestep, int) and not isinstance(
                    timestep, np.int64) and not isinstance(
                        timestep, list):
            raise TypeError("timestep must be an Integer or List")
        
        # Check that self is Results Scenario
        if self.is_result == "No":
            raise ValueError("Scenario must be a Results Scenario")
        
        # Retrieve Datasheet as DataFrame
        d = self.datasheets(name = datasheet)
        
        # Check that column exists in Datasheet
        if column not in d.columns:
            raise ValueError(f"column {column} does not exist in {datasheet}")
        
        if iteration is not None:
            if isinstance(iteration, int):
                
                if iteration > d.Iteration.max():
                    raise ValueError(
                        "Specified iteration above range of plausible values")
                elif iteration <= 0:
                    raise ValueError("iteration cannot be below 1")
                    
                d = d.loc[d["Iteration"] == iteration]
                
            if isinstance(iteration, list):
                
                if any(x > d.Iteration.max() for x in iteration) or any(
                        x < 1 for x in iteration):
                    raise ValueError("Some iteration values outside of range")
                    
                d = d.loc[d["Iteration"].isin(iteration)]
                
            d = d.reset_index()
            
        if timestep is not None:
            if isinstance(timestep, int):
                
                if timestep > d.Timestep.max():
                    raise ValueError(
                        "Specified timestep above range of plausible values")
                if timestep < d.Timestep.min():
                    raise ValueError(
                        "Specified timestep below range of plausible values")
                    
                d = d.loc[d["Timestep"] == timestep]
                
            if isinstance(timestep, list):
                
                if any(x > d.Timestep.max() for x in timestep) or any(
                        x < d.Timestep.min() for x in timestep):
                    raise ValueError("Some timestep values outside of range")
                
                d = d.loc[d["Timestep"].isin(timestep)]
                
            d = d.reset_index()
                
        # Create empty list to store raster objects
        raster_list = []
        
        # Find folder with raster data
        if self.__env is None:
            try:
                # fix this
                fpath = os.path.join(os.getcwd(), self.library.name + ".temp",
                                     os.listdir(self.library.name + ".temp")[0])
            except (FileNotFoundError, IndexError):
                
                f_base_path = os.path.join(os.getcwd(), self.library.name + ".output")
                fpath = self.__find_output_fpath(f_base_path, datasheet)

        else:
            e = _environment()
            f_base_path = e.input_directory.item()
            fpath = self.__find_output_fpath(f_base_path, datasheet)
        
        # Iterate through all raster files in Datasheet
        for i in range(0, len(d)):
            
            # Index column with raster data
            rpath = os.path.join(fpath, d[column].loc[i])
            
            # Open and append each raster from the Datasheet
            if "Iteration" in d.columns:
                if "Timestep" in d.columns:
                    raster = ps.Raster(rpath, iteration = d["Iteration"].loc[i],
                                       timestep = d["Timestep"].loc[i])
                else:
                    raster = ps.Raster(rpath, iteration = d["Iteration"].loc[i])
            elif "Timestep" in d.columns:
                raster = ps.Raster(rpath, timestep=d["Timestep"].loc[i])
            else:
                raster = ps.Raster(rpath)

            raster_list.append(raster)
            
        if len(raster_list) == 1:
            return raster_list[0]
        else:
            return raster_list
    
    def save_datasheet(self, name, data):
        """
        Saves a pandas DataFrame as a SyncroSim Datasheet.

        Parameters
        ----------
        name : String
            Name of the SyncroSim Datasheet.
        data : pandas.DataFrame
            Data to be saved to SyncroSim Datasheet.

        Returns
        -------
        None.

        """
        self.library.save_datasheet(name, data, "Scenario", self.sid)
    
    def delete(self, force=False):
        """
        Deletes a Scenario.

        Parameters
        ----------
        force : Logical, optional
            If True, does not ask the user for permission to delete the 
            Scenario. The default is False.

        Returns
        -------
        None.

        """
        
        self.library.delete(project=self.project, scenario=self, force=force)
    
    def copy(self, name=None):
        """
        Creates a copy of an existing Scenario class instance.

        Parameters
        ----------
        name : String
            Name of the new Scenario. If no name is provided, the copied 
            Scenario is named after the existing Scenario. The default is None.

        Returns
        -------
        Scenario
            SyncroSim Scenario class instance.

        """
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        
        if name is None:
            name = self.name + " - Copy"
        
        args = ["--copy", "--scenario", "--slib=%s" % self.library.name,
                "--sid=%d" % self.sid, "--name=%s" % name]
        
        self.library.session._Session__call_console(args)
        
        # Reset Scenarios
        self.library._Library__scenarios = None
        self.library._Library__init_scenarios()
        s = self.library._Library__get_scenario(name=name)
        
        return ps.Scenario(s["Scenario ID"].values[0],
                           s["Name"].values[0], self.project, self.library)
    
    def dependencies(self, dependency=None, remove=False, force=False):
        """
        Gets, sets, or removes dependencies from a Scenario.

        Parameters
        ----------
        dependency : Scenario, Int, String, or List, optional
            Scenario(s) to be added or removed as dependencies. If None, then 
            returns a DataFrame of dependencies. The default is None.
        remove : Logical, optional
            If False, adds the dependency. If True, removes the dependency. 
            The default is False.
        force : Logical, optional
            If True, then does not prompt the user when removing a dependency.
            The default is False.

        Raises
        ------
        TypeError
            If arguments are not of the correct Type, throws an error.

        Returns
        -------
        pandas.DataFrame
            If no dependencies are specified, then returns a pandas DataFrame
            of existing dependencies for the given Scenario.

        """
        
        if dependency is None:
            return self.__dependencies
        
        if not isinstance(dependency, list):
            dependency = [dependency]
        
        for d in dependency:
            # Check types
            if isinstance(d, ps.Scenario):
                d_name = d.name
                d = d.sid
                
            elif isinstance(d, str):
                # check if scenario exists
                d_name = d
                d = self.library._Library__scenarios[
                    self.library._Library__scenarios.Name==d]
                
                if len(d) > 1:
                    raise ValueError(
                        "dependency name not unique, use ID or Scenario")
                else:
                    d = d["Scenario ID"].item()
                
            elif isinstance(d, int) or isinstance(d, np.int64):
                # check if scenarios exists
                d_name = self.library._Library__scenarios[
                         self.library._Library__scenarios["Scenario ID"]==d
                         ].Name.item()
                
            else:
                raise TypeError(
                    "dependency must be a Scenario, String, Integer, or List")
            
            # Add dependency
            if remove is False:
                # Remove and re-add to guarantee order
                if d in self.__dependencies.ID.values:
                    args = ["--delete", "--dependency", 
                            "--lib=%s" % self.library.location,
                            "--sid=%d" % self.sid, "--did=%d" % d, "--force"]
                    self.library.session._Session__call_console(args)
                
                # Re-add now
                args = ["--create", "--dependency",
                        "--lib=%s" % self.library.location,
                        "--sid=%d" % self.sid, "--did=%d" % d]
                
                try:
                    self.library.session._Session__call_console(args)
                    # Reset dependencies
                    self.__dependencies = self.__init_dependencies()
                    
                except RuntimeError as e:
                    print(e)
                
            # Remove dependency
            elif remove is True:
                args = ["--delete", "--dependency",
                        "--lib=%s" % self.library.location,
                        "--sid=%d" % self.sid, "--did=%d" % d]
                
                if force is False:
                    answer = input (
                        f"Do you really want to remove dependency {d_name} \
                            (Y/N)?")
                elif force is True:
                    answer = "Y"
                else: 
                    raise TypeError("force must be a Logical")
                    
                if answer == "Y":
                    args += ["--force"]
                else:
                    print(f"dependency {d_name} not removed")
                    return
                try:
                    self.library.session._Session__call_console(args)
                    # Reset dependencies
                    self.__dependencies = self.__init_dependencies()
                except RuntimeError as e:
                    print(e)
                         
            else: 
                raise TypeError("remove must be a Logical")
    
    def ignore_dependencies(self, value=None):
        """
        Retrieves or sets the Datafeeds to ignore for a Scenario.

        Parameters
        ----------
        value : String, optional
            Datafeeds to ignore. If more than one, separate with a comma, but 
            keep contained within the same String. If None, then a String of 
            Datafeeds to ignore is returned. The default is None.

        Returns
        -------
        String
            List of Datafeeds to ignore.

        """
        
        # Set datafeeds to ignore from a Scenario's dependencies
        if value is None:
            scn_info = self.library._Library__scenarios
            return scn_info[
                scn_info[
                    "Scenario ID"] == self.sid]["Ignore Dependencies"].item()
        elif isinstance(value, str):
            args = ["--setprop", "--lib=%s" % self.library.location,
                    "--ignoredeps='%s'" % value, "--sid=%d" % self.sid]
            self.library.session._Session__call_console(args)
            
            # Reset Scenario information
            self.library._Library__init_scenarios()
        else:
            raise TypeError("value must be a String")
    
    def merge_dependencies(self, value=None):
        """
        Retrieves or sets whether or not a Scenario is configured to merge
        dependencies at run time.

        Parameters
        ----------
        value : Logical, optional
            If True, the Scenario will be configured to merge dependencies at
            run time. If None, then the current configuration of merge 
            dependencies is returned. The default is None.

        Returns
        -------
        String
            Whether or not the Scenario is configured to merge dependencies at 
            run time.

        """
        
        scn_info = self.library._Library__scenarios
        merge_dep_status =  scn_info[scn_info[
                "Scenario ID"] == self.sid]["Merge Dependencies"].item()
        
        if value is None:
            return merge_dep_status
        
        elif value is True:
            if merge_dep_status == "yes":
                print("Scenarios already configured to merge at runtime")
                return
            else:
                merge_deps = "yes"
            
        elif value is False:
            if merge_dep_status == "no":
                print("Scenarios already configured to not merge at runtime")
                return
            else:
                merge_deps = "no"
            
        else:
            raise TypeError("value must be a Logical")
            
        args = ["--setprop", "--lib=%s" % self.library.location,
                "--mergedeps=%s" % merge_deps, "--sid=%d" % self.sid]
        self.library.session._Session__call_console(args)
        
        # Reset Scenario information
        self.library._Library__init_scenarios()
        
    def run(self, jobs=1):
        """
        Runs a Scenario.

        Parameters
        ----------
        jobs : Int, optional
            Number of multiprocessors to use when running a Scenario. The 
            default is 1.

        Returns
        -------
        Scenario
            SyncroSim Scenario class instance.

        """
        if not isinstance(jobs, int) and not isinstance(jobs, np.int64):
            raise TypeError("jobs must be an Integer")
        
        # Runs the scenario
        args = ["--run", "--lib=%s" % self.library.location,
                "--sid=%d" % self.__sid, "--jobs=%d" % jobs]
        self.library.session._Session__call_console(args)
        
        # Reset Project Scenarios
        self.project._Project__scenarios = None
        
        # Have this print a statement based on output message of whether the 
        # run was successful or not

        # Reset results
        self.__results = None
        
        # Retrieve Results Scenario ID
        # Also resets scenarios and results info
        result_id = self.results()["Scenario ID"].values[-1]
        
        # Return Results Scenario
        result_scn = self.library.scenarios(project=self.project,
                                            name=None,
                                            sid=result_id)
        
        return result_scn
    
    def run_log(self):
        """
        Returns a run log for a Results Scenario.

        Returns
        -------
        pandas.DataFrame
            Information from the SyncroSim run of a Results Scenario.

        """
        try:
            args = ["--list", "--runlog", "--lib=%s" % self.library.name,
                    "--sid=%d" % self.sid]
            return self.library._Library__console_to_csv(args)
        except RuntimeError as e:
            print(e)
        
    def results(self, sid=None):
        """
        Retrieves DataFrame of Results Scenarios or retrieves a Results 
        Scenario instance for this Scenario.
        
        Parameters
        ----------
        sid : Int, optional
            Scenario ID of Results Scenario. Default is None.

        Returns
        -------
        pandas.DataFrame or Scenario
            DataFrame of Results Scenarios, including information about 
            Scenario ID, Project ID, Name, and Is Result, or SyncroSim
            Scenario class instance.

        """
        # Type checks
        if sid is not None and not isinstance(
                sid, int) and not isinstance(sid, np.int64):
            raise TypeError("Scenario ID must be an Integer")
        
        # Retrieve specified Results Scenario for this scenario
        if sid is not None:
            scn = self.library.scenarios(project=self.project,
                                         name=None,
                                         sid=sid)
            if scn.is_result == "Yes":
                return scn
            else:
                raise ValueError(f'Scenario [{sid}] is not a Results Scenario')
        
        elif self.__results is None:
            s = self.project.scenarios()
            pat = '['+str(self.__sid)+']'
            self.__results = s[s.Name.str.contains(pat)]
            return self.__results
        else:
            return self.__results
        
    def __init_info(self):
        # Set Scenario information
        scn_info = self.library.scenarios(project=self.project.pid,
                                          optional=True)
        scn_info = scn_info[scn_info["Scenario ID"] == self.sid]
        self.__owner = scn_info["Owner"].item()
        self.__date_modified = scn_info["Last Modified"].item()
        self.__readonly = scn_info["Read Only"].item()
        self.__project_id = scn_info["Project ID"].item()
        self.__info = scn_info.set_axis(
            ["Value"], axis=0, inplace=False
            ).T.rename_axis("Property").reset_index()
        
    def __init_description(self):
        args = ["--list", "--description", "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid]
        return self.library.session._Session__call_console(args, decode=True)
    
    def __init_is_result(self):
        
        # Find out if result scenario
        scn_info = self.library._Library__scenarios
        scn_info = scn_info[scn_info["Scenario ID"] == self.sid]
        return scn_info["Is Result"].values[0]
    
    def __init_parent_id(self):
        
        # Find out parent ID if result scenario
        scn_info = self.library._Library__scenarios
        scn_info = scn_info[scn_info["Scenario ID"] == self.sid]
        parent_id = scn_info["Parent ID"].values[0]
        if type(parent_id) == float:
            return int(parent_id)
        else:
            return parent_id
    
    def __init_dependencies(self):
        
        # Find all dependencies for a Scenario
        args = ["--list", "--dependencies", "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid, ]
        return self.library._Library__console_to_csv(args) 
    
    def __find_output_fpath(self, f_base_path, datasheet):
                
        # If package is not included in name, add it
        if datasheet.startswith(self.library.package) is False:
            if datasheet.startswith("core") is False:
                datasheet = self.library.package + "_" + datasheet

        fpath = os.path.join(f_base_path, f"Scenario-{self.sid}", datasheet)
        
        return fpath