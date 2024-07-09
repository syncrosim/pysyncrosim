import pysyncrosim as ps
from pysyncrosim.environment import _environment
import os
import io
import re
import pandas as pd
import numpy as np

class Scenario(object):
    """
    A class representing a SyncroSim Scenario.
    
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
                temp_df["ScenarioId"] == self.__sid]["Name"].item()
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
    
    @property
    def folder_id(self):
        """
        Retrieves the ID of the folder the Scenario is contained within.

        Returns
        -------
        Int
            Folder ID of the folder that contains the Scenario.

        """
        self.__retrieve_scenario_folder_id()
        return self.__folder_id
    
    @folder_id.setter
    def folder_id(self, value):
        self.__add_scenario_to_folder(value)

    @property
    def dependencies(self):
        """
        Retrieves the dependencies of a Scenario.

        Returns
        -------
        pandas.DataFrame
            Returns a pandas DataFrame of existing dependencies for the 
            given Scenario.

        """
        
        return self.__init_dependencies()
            
    @dependencies.setter
    def dependencies(self, value):

        # Create list of dependencies to add
        if isinstance(value, list):
            dependencies = value
        else:
            dependencies = [value]

        did_list = []
        for d in dependencies:
            # Check types
            if d is None:
                continue

            elif isinstance(d, ps.Scenario):
                d_name = d.name
                d = d.sid
                
            elif isinstance(d, str):
                # check if scenario exists
                d_name = d
                d = self.library._Library__scenarios[
                    self.library._Library__scenarios.Name==d]               
                self.__validate_dependencies(d, name_or_id=d_name)
                d = d["ScenarioId"].item()
                
            elif isinstance(d, int) or isinstance(d, np.int64):
                # check if scenarios exists
                deps = self.library._Library__scenarios[
                       self.library._Library__scenarios["ScenarioId"]==d
                    ]
                self.__validate_dependencies(deps, name_or_id=d)
                d_name = deps.Name.item()
                
            else:
                raise TypeError(
                    "dependency must be a Scenario, String, Integer, or List")

            # Append dependency ID to list
            did_list.append(d)

        # Paste together did_list separated by comma
        value = ",".join(map(str, did_list))

        # Remove current dependencies
        self.__remove_all_dependencies() # TODO: replace remove_dependencies with remove_all_dependencies

        # Add new dependencies
        self.__add_dependencies(value) #TODO: replace add_dependency with add_dependencies
    
    def folders(self, folder=None, parent_folder=None, create=False):
        """
        Creates or retrieves a Folder in the parent Project of the Scenario.

        Parameters
        ----------
        folder : String or Int, optional
            Folder name or ID. If the Folder name does not currently exist in
            the Project, then a new Folder will be created. The default is None.
        parent_folder : String, Int, or Folder class instance, optional
            Parent Folder name, ID, or Folder object. If provided, then the
            current Folder will be nested within the parent Folder. The
            default is None.
        create : Logical, optional
            If True, creates the Folder if it does not exist. The default is 
            False.
        
        Returns
        -------
        Folder
            Folder class instance.
        """
        folder_object = ps.Folder(self, folder, parent_folder, create)
        return folder_object
    
    def datasheets(self, name=None, summary=True, optional=False, empty=False,
                   filter_column=None, filter_value=None, include_key=False,
                   show_full_paths=False, return_hidden=False):
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
        filter_column : String
            The column and value to filter the output Datasheet by 
            (e.g. "TransitionGroupID=20"). The default is None.
        include_key : Logical, optional
            Whether to include the primary key of the Datasheet, corresponding
            to the SQL database. Default is False.
        show_full_paths : Logical, optional
            Whether to show the full path of any external files in the Datasheet.
            Default is False.
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
        
        self.__datasheets = self.library.datasheets(name, summary, optional,
                                                    empty, "Scenario",
                                                    filter_column, 
                                                    filter_value, include_key,
                                                    show_full_paths,
                                                    return_hidden, self.sid)
        return self.__datasheets
    

    def datasheet_rasters(self, datasheet, column=None, iteration=None,
                         timestep=None, filter_column=None, filter_value=None,
                         path_only=False):
        """
        Retrieves spatial data columns from one or more SyncroSim Datasheets.

        Parameters
        ----------
        datasheet : String
            The name of a SyncroSim Datasheet containing raster data.
        column : String
            The column in the Datasheet containing the raster data. If no 
            column selected, then datasheet_rasters will attempt to find one.
        iteration : Int, List, or Range, optional
            The iteration to subset by. The default is None.
        timestep : Int, List, or Range, optional
            The timestep to subset by. The default is None.
        filter_column : String
            The column to filter the output rasters by 
            (e.g. "TransitionGroupID=20"). The default is None.
        filter_value : String, Int, Logical
            The value to filter the filter_column by. The default is None.
        path_only : Logical
            Instead of returning a Raster Class Instance, a filepath to the
            raster is returned. The default is False.

        Returns
        -------
        Raster or List of Rasters 
            Raster class instance or List of these.

        """
        # Type Checks
        if not isinstance(datasheet, str):
            raise TypeError("datasheet must be a String")
            
        if column is not None and not isinstance(column, str):
            raise TypeError("column must be a String")
            
        if iteration is not None and not isinstance(iteration, int)\
            and not isinstance(iteration, np.int64)\
                and not isinstance(iteration, list)\
                    and not isinstance(iteration, range):
            raise TypeError("iteration must be an Integer, List, or Range")
            
        if timestep is not None and not isinstance(timestep, int)\
            and not isinstance(timestep, np.int64)\
                and not isinstance(timestep, list)\
                    and not isinstance(timestep, range):
            raise TypeError("timestep must be an Integer, List, or Range")
            
        # Check that Datasheet has package prefix
        datasheet = self.library._Library__check_datasheet_name(datasheet)
        
        # Retrieve Datasheet as DataFrame
        d = self.datasheets(name = datasheet, filter_column = filter_column,
                            filter_value = filter_value, show_full_paths = False)
        
        if d.empty:
            raise ValueError(f"Datasheet {datasheet} does not contain data.")
        
        # Check if column is raster column
        args = ["--list", "--columns", "--allprops",
                "--sheet=%s" % datasheet, "--csv", 
                "--lib=%s" % self.library.location]
        props = self.library.session._Session__call_console(args, decode=True,
                                                            csv=True)
        props = pd.read_csv(io.StringIO(props))
        props["is_raster"] = props.Properties.str.contains(r"isRaster\^True")
        
        if (props.is_raster == False).all():
            raise ValueError(
                f"No raster columns found in Datasheet {datasheet}")
          
        # If no raster column specified, find the raster column
        if column is None:
            if len(props[props.is_raster == True]) > 1:
                raise ValueError(
                    "> 1 raster output column available, please specify.")
            column = props[props.is_raster == True].Name.values[0]
            
        if not (props.Name == column).any():
            raise ValueError(
               f"Column {column} not found in Datasheet {datasheet}")
            
        col_props = props[props.Name == column]
        
        if col_props.is_raster is False:
            raise ValueError(f"Column {column} is not a raster column")
            
        # TODO: Get band column if it exists
        # if col_props.Properties.str.contains("bandColumn").any():
        #     prop_split = col_props.Properties.str.split("!").values[0]
        #     band_column = [b for b in prop_split if b.startswith("bandColumn")]
        #     col_props["band_column"] = band_column[0].split("^")[1]
        
        if isinstance(iteration, range):
            iteration = list(iteration)
        
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
            
        if isinstance(timestep, range):
            timestep = list(timestep)
            
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
        
        # Search for the following raster tifs in all possible output places
        raster_tifs = d[column].values
        rpaths = []
        
        # Find folder with raster data - search in input, temp, and output
        if self.__env is None:
            
            for folder in [".data", ".temp"]:
                
                if folder != ".temp":
                    lib_dir = self.__find_output_fpath(
                        self.library.location + folder, datasheet)
                else:
                    lib_dir = self.library.location + folder
                
                for raster_tif in raster_tifs:
                    for root, dirs, files in os.walk(lib_dir):
                        if raster_tif in files:
                            rpaths.append(os.path.join(root, raster_tif))
                        else:
                            break
                        
                    if len(rpaths) == 0:
                        break
                    
                if len(rpaths) !=0:
                    break
                
        else:
            e = _environment()

            for folder in [".data", ".temp"]:
                
                if folder != ".temp":
                    lib_dir = self.__find_output_fpath(
                        e.library_filepath.item() + folder, datasheet)
                else:
                    lib_dir = e.library_filepath.item() + folder
                
                for raster_tif in raster_tifs:
                    for root, dirs, files in os.walk(lib_dir):
                        if raster_tif in files:
                            rpaths.append(os.path.join(root, raster_tif))
                        else:
                            break
                        
                    if len(rpaths) == 0:
                        break
                    
                if len(rpaths) !=0:
                    break
        
        # Return only filepaths to rasters if path_only is True
        if path_only:
            return rpaths
        
        # Iterate through all raster files in Datasheet
        for i in range(0, len(rpaths)):
            
            # Open and append each raster from the Datasheet
            if "Iteration" in d.columns:
                if "Timestep" in d.columns:
                    raster = ps.Raster(rpaths[i], iteration = d["Iteration"].loc[i],
                                       timestep = d["Timestep"].loc[i])
                else:
                    raster = ps.Raster(rpaths[i], iteration = d["Iteration"].loc[i])
            elif "Timestep" in d.columns:
                raster = ps.Raster(rpaths[i], timestep=d["Timestep"].loc[i])
            else:
                raster = ps.Raster(rpaths[i])

            raster_list.append(raster)
            
        if len(raster_list) == 1:
            return raster_list[0]
        else:
            return raster_list
    
    def save_datasheet(self, name, data, append=False):
        """
        Saves a pandas DataFrame as a SyncroSim Datasheet.

        Parameters
        ----------
        name : String
            Name of the SyncroSim Datasheet.
        data : pandas.DataFrame
            Data to be saved to SyncroSim Datasheet.
        append : Logical, optional
            If True, appends data to existing Datasheet. The default is 
            False.

        Returns
        -------
        None.

        """
        self.library.save_datasheet(name, data, append, False, "Scenario", self.sid)
    
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
        
        args = ["--copy", "--scenario", "--slib=%s" % self.library.location,
                "--sid=%d" % self.sid, "--name=%s" % name]
        
        self.library.session._Session__call_console(args)
        
        # Reset Scenarios
        self.library._Library__scenarios = None
        self.library._Library__init_scenarios()
        s = self.library._Library__scenarios
        s = s.loc[s["Name"] == name]

        if len(s) > 1:
            s = s[-1:]
        
        return ps.Scenario(s["ScenarioId"].values[0],
                           s["Name"].values[0], self.project, self.library)
    
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
                    "ScenarioId"] == self.sid]["IgnoreDependencies"].item()
        else:
            self.__validate_ignore_dependencies(value)
            args = ["--setprop", "--lib=%s" % self.library.location,
                    "--ignoredeps=%s" % value, "--sid=%d" % self.sid]
            self.library.session._Session__call_console(args)
            
            # Reset Scenario information
            self.library._Library__init_scenarios()
    
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
                "ScenarioId"] == self.sid]["MergeDependencies"].item()
        
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
        
    def run(self, copy_external_inputs=False):
        """
        Runs a Scenario.

        Parameters
        ----------
        copy_external_inputs : Logical, optional
            If False, then a copy of external input files (e.g. GeoTIFF files)
            is not created for each job. Otherwise, a copy of external inputs 
            is created for each job. Applies only when jobs > 1. The number of 
            jobs is set using the 'core_Multiprocessing' datasheet. The default is
            False.

        Returns
        -------
        Scenario
            SyncroSim Scenario class instance.

        """    
        # Runs the scenario
        args = ["--run", "--lib=%s" % self.library.location,
                "--sid=%d" % self.__sid]
        
        if copy_external_inputs is True:
            args += ["--copyextfiles=yes"]
            
        print(f"Running Scenario [{self.sid}] {self.name}")
        result = self.library.session._Session__call_console(args)
        
        if result.returncode == 0:
            print("Run successful")
        
        # Reset Project Scenarios
        self.project._Project__scenarios = None

        # Reset results
        self.__results = None
        
        # Retrieve Results Scenario ID
        # Also resets scenarios and results info
        result_id = self.results()["ScenarioId"].values[-1]
        
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
            args = ["--list", "--runlog", "--lib=%s" % self.library.location,
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
        
    def __retrieve_scenario_folder_id(self):

        lib_structure = self.library._Library__get_library_structure()   
        scn_ind = lib_structure.index[
            ((lib_structure['id'] == str(self.sid)) & (lib_structure["item"] == "Scenario"))
            ].tolist()[0]
        scn_level = lib_structure.iloc[scn_ind]['level']
        folder_id = None
        for i in reversed(range(scn_ind)):
            level = lib_structure.iloc[i]['level']
            item = lib_structure.iloc[i]['item']
            if (level < scn_level) & (item == "Folder"):
                folder_id = int(lib_structure.iloc[i]['id'])
                break
            elif (level < scn_level) & (item == "Project"):
                break          

        self.__folder_id = folder_id
        
    def __add_scenario_to_folder(self, folder_id):
        """
        Add a scenario to a folder within a SyncroSim project
        
        Parameters
        ----------
        session : pysyncrosim.Session
            pysyncrosim session object
        library : pysyncrosim.Library
            pysyncrosim library object
        project : pysyncrosim.Project
            pysyncrosim project object
        scenario : pysyncrosim.Scenario
            pysyncrosim scenario object
        folder_id : int 
            Folder id
        
        Returns
        -------
        None
        """
        lib = self.library
        pid = self.project.pid
        sid = self.sid

        args = ["--move", "--scenario", "--lib=%s" % lib.location, 
                "--sid=%d" % sid, "--tfid=%d" % folder_id, "--tpid=%d" % pid]

        result = lib.session._Session__call_console(args)

        if result.returncode == 0:
            self.__folder_id = folder_id
            print(f"Scenario {self.sid} added to folder with id {folder_id}")
                
    def __init_info(self):
        # Set Scenario information
        scn_info = self.library.scenarios(project=self.project.pid,
                                          optional=True)
        scn_info = scn_info[scn_info["ScenarioId"] == self.sid]
        self.__owner = scn_info["Owner"].item()
        self.__date_modified = scn_info["DateLastModified"].item()
        self.__readonly = scn_info["IsReadOnly"].item()
        self.__project_id = scn_info["ProjectId"].item()
        self.__info = scn_info.set_axis(
            ["Value"], axis=0
            ).T.rename_axis("Property").reset_index()
        
    def __init_description(self):
        args = ["--list", "--description", "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid]
        return self.library.session._Session__call_console(args, decode=True)
    
    def __init_is_result(self):
        
        # Find out if result scenario
        scn_info = self.library._Library__scenarios
        scn_info = scn_info[scn_info["ScenarioId"] == self.sid]
        return scn_info["IsResult"].values[0]
    
    def __init_parent_id(self):
        
        # Find out parent ID if result scenario
        scn_info = self.library._Library__scenarios
        scn_info = scn_info[scn_info["ScenarioId"] == self.sid]
        parent_id = scn_info["ParentId"].values[0]
        if type(parent_id) == float:
            return int(parent_id)
        else:
            return parent_id
    
    def __init_dependencies(self):
        
        # Find all dependencies for a Scenario
        args = ["--list", "--dependencies", "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid, ]
        return self.library._Library__console_to_csv(args) 

    def __validate_dependencies(self, dependencies, name_or_id):

        if len(dependencies) > 1:
            raise ValueError(
                "dependency name not unique, use ID or Scenario")
        elif len(dependencies) == 0:
            raise ValueError(f"Scenario dependency {name_or_id} does not exist")

    def __validate_ignore_dependencies(self, dependencies):

        if not isinstance(dependencies, str):
            raise TypeError("value must be a String")

        scenario_list = self.library._Library__scenarios
        scn = scenario_list["ScenarioId"].values[0]
        scn_obj = self.library.scenarios(
            project=self.project.pid, sid=scn)
        scn_datasheets = scn_obj.datasheets()
        datasheet_list = scn_datasheets["Name"].values.tolist()
        datasheet_list += [item.split(sep="_")[1] for item in datasheet_list]

        dep_list = dependencies.split(sep=",")
        for dep in dep_list:
            if dep not in datasheet_list:
                raise ValueError(f"Scenario dependency [{dep}] does not exist")

    def __remove_all_dependencies(self):

        args = ["--remove", "--dependency", 
                "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid, "--all", "--force"]
        
        try:
            self.library.session._Session__call_console(args)

        except RuntimeError as e:
                print(e)

    def __add_dependencies(self, d):

        if d == '':
            return
        
        args = ["--add", "--dependency",
                "--lib=%s" % self.library.location,
                "--sid=%d" % self.sid]
        
        if "," in d:
            args += ["--dids=%s" % d]
        else:
            args += ["--did=%s" % d]
                
        try:
            self.library.session._Session__call_console(args)
            
        except RuntimeError as e:
            print(e)
    
    def __find_output_fpath(self, f_base_path, datasheet):

        fpath = os.path.join(f_base_path, f"Scenario-{self.sid}", datasheet)
        
        return fpath