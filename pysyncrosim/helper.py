import pysyncrosim as ps
import os
import pandas as pd
import io

def library(name, session=None, package="stsim", addons=None, template=None,
            forceUpdate=False, overwrite=False):
    """
    Creates a new SyncroSim Library and opens it as a Library
    class instance.

    Parameters
    ----------
    name : String
        Name of new Library to create.
    session : Session, optional
        Connects the Python session to the SyncroSim executable. If None, then
        creates a Session class instance using the default installation path
        to the SyncroSim executable. The default is None.
    package : String, optional
        The package type. The default is "stsim".
    addons : String, optional
        One or more addon packages. The default is None.
    template : String, optional
        Creates Library with specified template. The default is None.
    forceUpdate : Logical, optional
        If False, then user is prompted to approve required updates. The 
        default is False.
    overwrite : Logical, optional
        Overwrite existing Library. The default is False.

    Returns
    -------
    Library
        SyncroSim Library class instance.

    """
    # Unit tests for type checking
    if not isinstance(name, str):
        raise TypeError("name must be a String")
    if session is not None and not isinstance(session, ps.Session):
        raise TypeError("session must be None or pysyncrosim Session instance")
    if not isinstance(package, str):
        raise TypeError("package must be a String")
    if addons is not None and not isinstance(addons, str):
        raise TypeError("addons must be a String")
    if template is not None and not isinstance(template, str):
        raise TypeError("templates must be a String")
    if not isinstance(forceUpdate, bool):
        raise TypeError("forceUpdate must be a Logical")
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a Logical")
    
    if session is None:
        session = ps.Session()
        
    # Test that package specified is installed
    installed = session._Session__pkgs
    if package not in installed["Name"].values:
        raise ValueError(f'The package {package} is not installed')
        
    # Add Library extension if not already included
    if name.endswith(".ssim") is False:
        name += ".ssim"
    
    # Check if name is path and if it exists already
    if os.path.split(name)[0] == '':
        loc = os.path.join(os.getcwd(), name)
    elif os.path.isdir(os.path.split(name)[0]):
        loc = name
        name = os.path.split(name)[-1]
    else:
        raise ValueError(f"Path to Library does not exist: {name}")
    
    args = ["--create", "--library", "--package=%s" % package,
            "--name=\"%s\"" % loc]
    
    if overwrite is True:
        
        args += ["--force"]
    
    if template is not None: 
        
        if template.endswith(".ssim") is True:
            template = os.path.splitext(template)[0]
        
        # Check if template exists in base package
        base_temp_args = ["--list", "--templates", "--package=%s" % package]
        base_temps = session._Session__call_console(base_temp_args,
                                                    decode=True,
                                                    csv=True)
        base_temps = pd.read_csv(io.StringIO(base_temps))
        base_temp = package + "_" + template
        
        # TODO: check for case when more than one addon package is included
        if addons is not None:
            addon_temp_args = ["--list", "--templates", "--package=%s" % addons]
            addon_temps = session._Session__call_console(addon_temp_args,
                                                        decode=True,
                                                        csv=True)
            addon_temps = pd.read_csv(io.StringIO(addon_temps))
            addon_temp = addons + "_" + template
        
        if base_temp in base_temps["Name"].values:
            args += ["--template=\"%s\"" % base_temp]
        elif addons is not None and addon_temp in addon_temps["Name"].values:
            args += ["--template=\"%s\"" % addons]
        else:
            raise ValueError(
                f"Template {template} does not exist in package {package}")
        
    try:
    
        session._Session__call_console(args)
        
        if addons is not None:
            # Check if addons exists
            if addons not in installed["Name"].values:
                raise ValueError(
                    f'The addon package {addons} is not installed')
            
            args = ["--create", "--addon", "--lib=%s" % loc,
                    "--name=%s" % addons]
            session._Session__call_console(args)
            
    except ValueError as ve:
        
        print(ve)
        
    except RuntimeError as re1:
        
        re1 = str(re1)
        if "The Library already exists" in re1:
            pass
        else:
            raise RuntimeError(re1)

    
    library_up_to_date = False
    try:
        
        # Find out if there are any unapplied updates to the library
        args = ["--list", "--addons", "--lib=%s" % loc]
        session._Session__call_console(args)
        library_up_to_date = True
        
    except RuntimeError as re2:
        
        re2 = str(re2)
        if "The library has unapplied updates" in re2:
            if forceUpdate is False:
                answer = input(f"The Library has unapplied updates. Would you\
                               like to update the library with path {loc}? \
                               (Y/N)")
            else:
                answer = "Y"
                
            if answer == "Y":
                args = ["--update", "--lib=%s" % loc]
                session._Session__call_console(args)
                library_up_to_date = True
            elif answer == "N":
                print("Updates not applied and Library not loaded.")
    
    finally:
        
        if library_up_to_date is True:
            return ps.Library(location=loc, session=session)

def _delete_library(name, session=None, force=False):
    """
    Deletes a SyncroSim Library.

    Parameters
    ----------
    name : String
        Name of SyncroSim Library to delete.
    session : Session, optional
        Connects the Python session to the SyncroSim executable. If None, then
        creates a Session class instance using the default installation path
        to the SyncroSim executable. The default is None.

    Returns
    -------
    None.

    """
    if session is None:
        session = ps.Session()

    if force is False:
        answer = input (f"Are you sure you want to delete {name} (Y/N)?")
    else:
        answer = "Y"
    
    try:
        lib = ps.Library(name, session)
        
        files = [lib._Library__location,
                 lib._Library__location + ".backup",
                 lib._Library__location + ".input",
                 lib._Library__location + ".output",
                 lib._Library__location + ".temp"]
        
        if answer == "Y":
            for f in files:
                if os.path.exists(f):
                    os.remove(f)  
                    
    except (RuntimeError):
        pass
    
def _delete_project(library, name=None, pid=None, session=None,
                    force=False):
    
    if session is None:
        session = ps.Session()
        
    # force statement moved to delete function
    if force is False:
        answer = input (f"Are you sure you want to delete {name} (Y/N)?")
    else:
        answer = "Y"
    
    if answer == "Y":
        
        # Retrieve Project DataFrame
        library._Library__init_projects()
        p = library._Library__get_project(name, pid)
        
        if p.empty:
            if name is not None: 
                raise RuntimeError("The Project does not exist: %s" % name)
            else: 
                raise RuntimeError("The Project does not exist: %d" % pid)
                
        # Delete Project using console   
        if pid is None:
            pid = p["ID"].values[0]
        args = ["--delete", "--project", "--lib=\"%s\"" % library.location,
                "--pid=%d" % pid, "--force"]
        session._Session__call_console(args)
        
        # Reset Projects
        library._Library__projects = None
        library._Library__init_projects()

def _delete_scenario(library, project, name=None, sid=None, session=None,
                     force=False):
    
    # force statement moved to delete function
    if force is False:
        answer = input (f"Are you sure you want to delete {name} (Y/N)?")
    else:
        answer = "Y"
    
    if answer == "Y":
    
        # Retrieve Scenario DataFrame
        library._Library__init_scenarios()
        s = library._Library__get_scenario(name=name, sid=sid)
        
        if s.empty:
            if name is not None: 
                raise RuntimeError("The Scenario does not exist: %s" % name)
            else: 
                raise RuntimeError("The Scenario does not exist: %d" % sid)
                                        
        # Delete Scenario using console   
        if sid is None:
            sid = s["Scenario ID"].values[0]
        args = ["--delete", "--scenario", "--lib=\"%s\"" % library.location,
                "--sid=%d" % sid, "--force"]
        session._Session__call_console(args)
        
        # Reset Scenarios
        library._Library__scenarios = None
        library._Library__init_scenarios()