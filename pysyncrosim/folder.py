import pysyncrosim as ps
from pysyncrosim.environment import _environment
import os
import io
import pandas as pd
import numpy as np

class Folder(object):
    """
    A class representing a SyncroSim Folder.
    
    """
    def __init__(self, ssimobject, folder = None, parent_folder = None, create = False):

        self.__validate_inputs(create)

        self.__create = create
        self.__parent_folder = parent_folder

        self.__set_ssimobject_prop(ssimobject)
        self.__data = self.__get_folder_data()
        self.__set_folder_id_name(folder)

        # Return data if no folder specified
        if (self.__scenario is None) and (self.__project is None):
            return self.__data
        if (self.__scenario is None) and (folder is None):
            return self.__data[self.__data["ProjectID"] == self.__project.pid]
        
        # Create folder objects if folder provided and ssimobject is project or scenario
        if (self.__name is not None) and (create is True):
            self.__create_folder()     
        
    @property
    def folder_id(self):
        """
        Retrieves Folder ID.

        Returns
        -------
        Int
            Folder ID.

        """
        return self.__folder_id
    
    @property 
    def parent_id(self):
        """
        Retrieves Parent Folder ID.

        Returns
        -------
        Int
            Parent ID.
        """
        return self.__parent_id
    
    @property
    def project_id(self):
        """
        Retrieves ID of the Project containing the folder
        
        Returns 
        -------
        Int
            Project ID
        """
        return self.__project.pid
    
    @property
    def name(self):
        """
        Retrieves or sets Folder Name.

        Returns
        -------
        String
            Folder ID.

        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        name = info_subset["Name"].values[0]
        return name
    
    @name.setter
    def name(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--name=%s" % value, "--fid=%d" % self.folder_id]
        self.library.session._Session__call_console(args)

    @property
    def owner(self):
        """
        Retrieves or sets the Folder Owner.
        
        Returns
        -------
        String
            Folder Owner
        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        owner = info_subset["Owner"].values[0]
        return owner
    
    @owner.setter
    def owner(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--owner=%s" % value, "--fid=%d" % self.folder_id]
        self.library.session._Session__call_console(args)

    @property
    def readonly(self):
        """
        Retrieves or sets the read-only status of a Folder.
        
        Returns
        -------
        Bool
            Folder read-only status
        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        readonly = info_subset["IsReadOnly"].values[0]
        return readonly
    
    @readonly.setter
    def readonly(self, value):
        if value is True:
            value = "yes"
        elif value is False:
            value = "no"
        else:
            raise TypeError("value must be a Logical")
        args = ["--setprop", "--lib=%s" % self.library.location, 
                "--readonly=%s" % value, "--fid=%d" % self.folder_id]
        self.library.session._Session__call_console(args)

    @property
    def description(self):
        """
        Gets or sets the Folder description.

        Returns
        -------
        String
            Folder description.

        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        description = info_subset["Description"].values[0]
        return description
    
    @description.setter
    def description(self, value):
        args = ["--setprop", "--lib=%s" % self.library.location,
                "--description=%s" % value, "--fid=%d" % self.folder_id]
        self.library.session._Session__call_console(args)

    @property
    def date_modified(self):
        """
        Gets the date the Folder was last modified.
        
        Returns
        -------
        String
            Date the Folder was last modified.
        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        date_modified = info_subset["DateLastModified"].values[0]
        return date_modified

    @property
    def published(self):
        """
        Gets or sets whether the Folder is tagged for publication.

        Returns
        -------
        String
            "yes" if the Folder is tagged for publication and "no" otherwise.
        """
        info = self.__get_folder_data()
        info_subset = info[info["FolderID"] == self.folder_id]
        published = info_subset["IsLite"].values[0]
        return published
    
    @published.setter
    def published(self, value):

        if (value is True) or (value.tolower() == "yes"):
            value = "yes"
        else:
            value = "no"

        args = ["--setprop", "--lib=%s" % self.library.location,
                "--islite=%s" % value, "--fid=%d" % self.folder_id]
        self.library.session._Session__call_console(args)

    def __validate_inputs(self, create):
        if not isinstance(create, bool):
            raise ValueError("create must be a boolean value.")

    def __set_ssimobject_prop(self, ssimobject):
        if isinstance(ssimobject, ps.Library):
            self.__scenario = None
            self.__project = None
            self.__library = ssimobject
        elif isinstance(ssimobject, ps.Project):
            self.__scenario = None
            self.__project = ssimobject
            self.__library = ssimobject.library
        elif isinstance(ssimobject, ps.Scenario):
            self.__scenario = ssimobject
            self.__project = ssimobject.project
            self.__library = ssimobject.library

    def __get_folder_data(self):
        args = ["--lib=%s" % self.__library.location, "--list", "--folders"]
        data = self.__library.session._Session__call_console(args, decode=True, csv=True)
        return data
    
    def __set_folder_id_name(self, folder):

        if folder is None:
            self.__name = None
            self.__folder_id = None

        if isinstance(folder, str):
            self.__name = folder
            data_subset = self.__data[self.data["FolderID"] == self.__name]
            if len(data_subset) == 1:
                self.__folder_id = data_subset["FolderID"].values[0]
            elif (len(data_subset) > 0) & (self.__create is False):
                raise ValueError("Multiple folders with the same name exist. " +
                                 "Use Folder ID instead to retrieve the desired " +
                                 "folder or set create=True to create another folder " + 
                                 "with the same name.")
            
        elif (isinstance(folder, int)) or (isinstance(folder, np.int64)):
            self.__folder_id = folder
            data_subset = self.__data[self.data["FolderID"] == self.__folder_id]
            if len(data_subset) == 1:
                self.__name = data_subset["FolderName"].values[0]
            elif len(data_subset) == 0:
                raise ValueError("Folder ID does not exist.")
            
        else:
            raise ValueError("folder must be a String or Integer.")
        
    def __create_folder(self):
        args = ["--lib=%s" % self.__library.location, "--create", "--folder", 
                "--name=%s" % self.__name]
        
        if self.__parent_folder is not None:
            self.__retrieve_parent_id()
            args += ["--tfid=%s" % str(self.__parent_id)]
        else:
            args += ["--tpid=%s" % str(self.__project.pid)]
            
        out = self.__library.session._Session__call_console(args, decode=True)
        # TODO: Check regex to find folder ID from output
        folderId = out.split(": ")[0]
        self.__folder_id = folderId

    def __retrieve_parent_id(self):
        if (isinstance(self.__parent_folder, int)) or\
                (isinstance(self.__parent_folder, np.int32)):
            data_subset = self.__data[self.data["FolderID"] == self.__parent_folder]
            if len(data_subset) == 1:
                self.__parent_id = self.__parent_folder
                return 
            
        elif isinstance(self.__parent_folder, str):
            data_subset = self.__data[self.data["Name"] == self.__parent_folder]
            if len(data_subset) == 1:
                self.__parent_id = data_subset["Name"].values[0]
                
        elif isinstance(self.__parent_folder, ps.Folder):
            self.__parent_id = self.__parent_folder.folder_id
            return
        
        raise ValueError("parent_folder not found.")   
