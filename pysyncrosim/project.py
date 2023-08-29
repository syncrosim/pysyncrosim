import pysyncrosim as ps
import numpy as np
import re

class Project(object):
    """
    A class to represent a SyncroSim Project.
        
    """
    __scenarios = None
    __datasheets = None
    
    def __init__(self, pid, name, library):
        """
        Initializes a pysyncrosim Project instance.

        Parameters
        ----------
        pid : Int
            Project ID.
        name : String
            Project name.
        library : Library
            pysyncrosim Library instance.

        Returns
        -------
        None.

        """
        self.__pid = pid
        self.__name = name
        self.__library = library
        self.__owner = None
        self.__date_modified = None
        self.__readonly = None
        self.__info = None
        # All None attributes created by __init_info()
        self.__init_info()
        self.__description = self.__init_description()
        
    @property
    def pid(self):
        """
        Retrieves Project ID.

        Returns
        -------
        Int
            Project ID.

        """
        return self.__pid
    
    @property
    def name(self):
        """
        Retrieves or sets Project name.

        Returns
        -------
        String
            Project name.

        """
        return self.__name 
    
    @name.setter
    def name(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--name=%s" % value, "--pid=%d" % self.pid]
        self.library.session._Session__call_console(args)
        self.__init_info()
    
    @property
    def library(self):
        """
        Retrieves the Library the Project belongs to.

        Returns
        -------
        Library
            SyncroSim Library class instance.

        """
        return self.__library
    
    @property
    def info(self):
        """
        Retrieves Project information.

        Returns
        -------
        pandas DataFrame
            Project information.

        """
        return self.__info
    
    @property
    def owner(self):
        """
        Gets or sets the owner of this Project.

        Returns
        -------
        String
            Owner of this Project.

        """
        return self.__owner
    
    @owner.setter
    def owner(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--owner=%s" % value, "--pid=%d" % self.pid]
        self.library.session._Session__call_console(args)
        self.__init_info()
        
    @property
    def date_modified(self):
        """
        Gets the last date this Project was modified.

        Returns
        -------
        String
            Last date modified.

        """
        return self.__date_modified
    
    @property
    def readonly(self):
        """
        Gets or sets the read-only status for this Project.

        Returns
        -------
        String
            "yes" if this Project is read-only, "no" otherwise.

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
                "--readonly=%s" % ro, "--pid=%d" % self.pid]
        self.library.session._Session__call_console(args)
        self.__init_info()
    
    @property
    def description(self):
        """
        Gets or sets the Project description.

        Returns
        -------
        String
            Project description.

        """
        return self.__description
    
    @description.setter
    def description(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location,
                "--description=%s" % value, "--pid=%d" % self.pid]
        self.library.session._Session__call_console(args)
        self.__description = None
        self.__description = self.__init_description()

    def scenarios(self, name=None, sid=None, optional=False, summary=None,
                  results=False):
        """
        Retrieve a DataFrame of Scenarios in this Project.
        
        Parameters
        ----------
        name : String, optional
            Scenario name. The default is None.
        sid : Int, optional
            Scenario ID. The default is None.
        optional : Logical, optional
            Return optional information. The default is False.
        summary : Logical, optional
            If set to False, then returns all Scenarios as SyncroSim
            Scenario instances. The default is None.

        results : Logical, optional
            Return only a list of Results Scenarios. The default is False.
        
        Returns
        -------
        pandas.DataFrame
            If `optional=False`, then returns a DataFrame of Scenario 
            information including Scenario ID, Project ID, Name, and Is Result.
            If `optional=True`, also returns Parent ID, Owner, Last Modified, 
            Read Only, Merge Dependencies, Ignore Dependencies, and Auto Gen
            Tags.

        """
        
        self.__scenarios = self.library.scenarios(name=name, project=self, 
                                                  sid=sid,
                                                  pid=self.pid,
                                                  optional=optional,
                                                  summary=summary,
                                                  results=results)
        
        return self.__scenarios
    
    def folders(self, folder=None, parent_folder=None, create=False):
        """
        Retrieves a dataframe of Folder information for this Project if
        folder=None, otherwise creates or retrieves a SyncroSim Folder 
        object.
        
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
        pandas.DataFrame or pysyncrosim.Folder
            Dataframe of Folder information for this Project or
            Folder class instance.

        """
        folder_data = ps.Folder(ssimobject=self, folder=folder, 
                             parent_folder=parent_folder, create=create)
        return folder_data

    def datasheets(self, name=None, summary=True, optional=False, empty=False,
                   filter_column=None, filter_value=None, include_key=False,
                   show_full_paths=False, return_hidden=False):
        """
        Retrieves a DataFrame of Project Datasheets.
        
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
                                                    empty, "Project",
                                                    filter_column, 
                                                    filter_value, include_key,
                                                    show_full_paths,
                                                    return_hidden, self.pid)
        return self.__datasheets
    
    def delete(self, scenario=None, force=False):
        """
        Deletes a Project or Scenario.

        Parameters
        ----------
        scenario : Scenario, String, or Int, optional
            Scenario to delete. The default is None.
        force : Logical, optional
            If True, does not prompt the user to confirm deletion. The default
            is False.

        Returns
        -------
        None.

        """
        
        self.library.delete(project=self, scenario=scenario, force=force)

    def save_datasheet(self, name, data, append=True, force=False):
        """
        Saves a Project-scoped Datasheet.

        Parameters
        ----------
        name : String
            Name of Datasheet to save.
        data : pandas.DataFrame
            DataFrame to save as Datasheet.
        append : Logical, optional
            If True, appends to existing Datasheet. If False, then the
            user must also specify `force=True` to overwrite the existing
            Datasheet. The default is True.
        force : Logical, optional
            If True, overwrites existing Datasheet. The user should be aware that
            this may also delete other definitions and results, so this argument
            should be used with care. The default is False.

        Returns
        -------
        None.

        """
        
        self.library.save_datasheet(name, data, append, force, "Project", self.pid)
        
    def run(self, scenarios=None, jobs=1, copy_external_inputs=False):
        """
        Runs a list of Scenario objects.

        Parameters
        ----------
        scenarios : Scenario, String, Int, or List
            List of Scenrios, SyncroSim Scenario instance, name of Scenario,
            or Scenario ID.
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
        if not isinstance(jobs, int) and not isinstance(jobs, np.int64):
            raise TypeError("jobs must be an Integer")
        
        # Collect output in a dictionary
        result_list = []
        
        if scenarios is None:
                
            # Run all Scenarios in a Project
            scenarios = self.scenarios(summary=False)
            
            if not isinstance(scenarios, list):
                scenarios = [scenarios]

            scn_id_str = self.__create_scenario_id_string(scenarios)
                    
        elif scenarios is not None:
                
            if not isinstance(scenarios, list):
                scenarios = [scenarios]

            scn_id_str = self.__create_scenario_id_string(scenarios)

        args = ["--run", "--lib=%s" % self.library.location, "--jobs=%d" % jobs]
        
        if len(scenarios) > 1:
            args += ["--sids=%s" % scn_id_str]
        else:
            args += ["--sid=%s" % scn_id_str]

        if jobs > 1 and copy_external_inputs is True:
            args += ["--copyextfiles=yes"]

        print(f"Running Scenario(s)")  
        result = self.library.session._Session__call_console(args)

        if result.returncode == 0:
            print("Run successful")

        # Reset Project Scenarios
        self.__scenarios = None

        # Reset and retrieve Scenario results
        for scn in scenarios:
            if isinstance(scn, int) or isinstance(scn, np.int64):
                scn = self.scenarios(scn)
            elif isinstance(scn, str):
                scn = self.scenarios(scn)
            scn._Scenario__results = None
            result_id = scn.results()["ScenarioID"].values[-1]
            result_list.append(self.scenarios(sid=result_id))
            
        if len(result_list) == 1:
            return result_list[0]
        else:                
            return result_list
    
    def copy(self, name=None):
        """
        Creates a copy of an existing Project.

        Parameters
        ----------
        name : String, optional
            Name of the new Project. If no name is given, the copied 
            Project is named after the source Project. The default is None.

        Returns
        -------
        Project
            SyncroSim Project class instance.

        """
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a String")
        
        if name is None:
            name = self.name + " - Copy"
        
        args = ["--copy", "--project", "--slib=%s" % self.library.name,
                "--pid=%d" % self.pid, "--name=%s" % name, "--copychildren"]
        
        self.library.session._Session__call_console(args)
        
        # Reset Projects
        self.library._Library__projects = None
        self.library._Library__init_projects()
        p = self.library._Library__get_project(name=name)
        
        return ps.Project(p["ProjectID"].values[0],
                          p["Name"].values[0], self.library)
    
    def create_project_folder(self, folder_name):
        """
        Create a folder within a SyncroSim project
        
        Parameters
        ----------
        folder_name : str
            Name of folder to create
        
        Returns
        -------
        str
            Folder id
        """

        args = ["--create", "--folder", "--lib=%s" % self.library.location,
                "--name=%s" % folder_name, "--tpid=%d" % self.pid]
        out = self.library.session._Session__call_console(args, decode=True)
        folder_id = re.findall(r'\d+', out)[0]

        return folder_id

    def create_nested_folder(self, parent_folder_id, folder_name):
        """
        Create a folder within an existing folder.
        
        Parameters
        ----------
        parent_folder_id : int
            Parent folder id
        folder_name : str
            Name of folder to create
        
        Returns
        -------
        str
            Folder id
        """

        args = ["--create", "--folder", "--lib=%s" % self.library.location,
                "--name=%s" % folder_name, "--tfid=%d" % parent_folder_id]
        out = self.library.session._Session__call_console(args, decode=True)
        folder_id = re.findall(r'\d+', out)[0]

        return int(folder_id)
    
    def __init_info(self):
        # Set projects
        self.library.projects()
        proj_info = self.library._Library__projects
        proj_info = proj_info[proj_info["ProjectID"] == self.pid]
        self.__owner = proj_info["Owner"].item()
        self.__date_modified = proj_info["DateLastModified"].item()
        self.__readonly = proj_info["IsReadOnly"].item()
        self.__info = proj_info.set_axis(
            ["Value"], axis=0
            ).T.rename_axis("Property").reset_index()
        
    def __init_description(self):
        args = ["--list", "--description",
                "--lib=%s" % self.library.location,
                "--pid=%d" % self.pid]
        return self.library.session._Session__call_console(
            args, decode=True)
    
    def __create_scenario_id_string(self, scenarios):
        # Create string list of scenarios to provide SyncroSim
        scn_string_list = ""
        for scn in scenarios:
            if isinstance(scn, ps.Scenario):
                scn_string_list += str(scn.sid) + ","
            elif isinstance(scn, int) or isinstance(scn, np.int64):
                scn_string_list += str(scn) + ","
            elif isinstance(scn, str):
                scn_object = self.scenarios(name=scn)
                scn_string_list += str(scn_object.sid) + ","

        # Remove trailing comma
        scn_string_list = scn_string_list[:-1]

        return scn_string_list


