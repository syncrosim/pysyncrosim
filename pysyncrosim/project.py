import pysyncrosim as ps

class Project(object):
    """
    A class to represent a SyncroSim Project.
    
    ...
    
    Attributes
    ----------
    pid : Int
        Retrieves Project ID.
    name : String
        Retrieves or sets Project name.
    library : Library
        Retrieves the Library the Project belongs to.
    info : pandas DataFrame
        Retrieves Project information.
    owner : String
        Gets or sets the owner of this Project.
    date_modified : String
        Gets the last date this Project was modified.
    readonly : String
        Gets or sets the read-only status for this Project.
    description : String
        Gets or sets the Project description.
        
    Methods
    -------
    scenarios(name=None, sid=None, optional=False, summary=True):
        Retrieve a DataFrame of Scenarios in this Project.
    datasheets(name=None, summary=True, optional=False, empty=False,
               filter_column=None):
        Retrieves a DataFrame of Project Datasheets.
    delete(scenario=None, force=False):
        Deletes a Project or Scenario.    
    save_datasheet(name, data):
        Saves a Project-scoped Datasheet.
    copy(name=None):
        Creates a copy of an existing Project.
        
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
            Scenario instances.
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

    def datasheets(self, name=None, summary=True, optional=False, empty=False,
                   filter_column=None, include_key=False):
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

        Returns
        -------
        pandas.DataFrame
            If `optional=False`, then returns a DataFrame of Datasheet 
            information including Package, Name, and Display Name.
            If `optional=True`, also returns Scope, Is Single, and Is Output.

        """
        
        self.__datasheets = self.library.datasheets(name, summary, optional,
                                                    empty, "Project",
                                                    filter_column, include_key,
                                                    self.pid)
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

    def save_datasheet(self, name, data):
        """
        Saves a Project-scoped Datasheet.

        Parameters
        ----------
        name : String
            Name of Datasheet to save.
        data : pandas.DataFrame
            DataFrame to save as Datasheet.

        Returns
        -------
        None.

        """
        
        self.library.save_datasheet(name, data, "Project", self.pid)
    
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
    
    def __init_info(self):
        # Set projects
        self.library.projects()
        proj_info = self.library._Library__projects
        proj_info = proj_info[proj_info["ProjectID"] == self.pid]
        self.__owner = proj_info["Owner"].item()
        self.__date_modified = proj_info["DateLastModified"].item()
        self.__readonly = proj_info["IsReadOnly"].item()
        self.__info = proj_info.set_axis(
            ["Value"], axis=0, inplace=False
            ).T.rename_axis("Property").reset_index()
        
    def __init_description(self):
        args = ["--list", "--description",
                "--lib=%s" % self.library.location,
                "--pid=%d" % self.pid]
        return self.library.session._Session__call_console(
            args, decode=True)


