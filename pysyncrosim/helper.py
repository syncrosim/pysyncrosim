import pysyncrosim as ps
import os
import pandas as pd
import io

def library(name, session=None, packages=None,
            forceUpdate=False, overwrite=False, use_conda=None):
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
    packages : String, optional
        The SyncroSim packages to be added to the Library. If None, then the
        Library will be created without any packages. The default is None.
    forceUpdate : Logical, optional
        If False, then user is prompted to approve required updates. The 
        default is False.
    overwrite : Logical, optional
        Overwrite existing Library. The default is False.
    use_conda : Logical, optional
        If True, then runs the Library in a conda environment. The 
        default is None, meaning the Library properties determine whether
        the Library is run in a conda environment. When new Libraries are 
        created, the default for use_conda is `False`.

    Returns
    -------
    Library
        SyncroSim Library class instance.

    """
    _validate_library_inputs(name, session, packages,
                             forceUpdate, overwrite, use_conda)
    
    if session is None:
        session = ps.Session()

    name, loc = _configure_library_name(name)

    if os.path.exists(loc) and overwrite is False and packages is None:
        _check_library_update(session, loc, forceUpdate)
        return ps.Library(location=loc, session=session)
    
    args = ["--create", "--library", "--name=\"%s\"" % loc]
    
    if overwrite is True:      
        args += ["--force"]

    if forceUpdate is True:
        args += ["--update"]
        
    try:
    
        session._Session__call_console(args)
            
    except ValueError as ve:
        
        print(ve)
        
    except RuntimeError as re1:
        
        re1 = str(re1)
        if "The Library already exists" in re1:
            pass
        else:
            raise RuntimeError(re1)

    _check_library_update(session, loc, forceUpdate)
        
    return ps.Library(location=loc, session=session, use_conda=use_conda, packages=packages)

def _validate_library_inputs(name, session, packages, 
                             forceUpdate, overwrite, use_conda):
    """
    Validates input types for the create_library function
    """
    # Type checks
    if not isinstance(name, str):
        raise TypeError("name must be a String")
    if session is not None and not isinstance(session, ps.Session):
        raise TypeError("session must be None or pysyncrosim Session instance")
    if packages is not None and not isinstance(packages, str):
        if not isinstance(packages, list):
            raise TypeError("packages must be None, a String, or a List")
        if isinstance(packages, list):
            if not all(isinstance(package, str) for package in packages):
                raise TypeError("packages in list are not all strings")
    if not isinstance(forceUpdate, bool):
        raise TypeError("forceUpdate must be a Logical")
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a Logical")
    if use_conda is not None and not isinstance(use_conda, bool):
        raise TypeError("use_conda must be None or a Logical")
    
    # Check if packages currently installed
    if packages is not None:
        installed = session.packages()
        if isinstance(packages, str):
            if packages not in installed["Name"].values:
                raise ValueError(f'The package {packages} is not installed')
        elif isinstance(packages, list):
            for package in packages:
                if package not in installed["Name"].values:
                    raise ValueError(f'The package {package} is not installed')
    
def _configure_library_name(name):
        
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
    
    return name, loc

def _check_library_update(session, loc, forceUpdate):

    try:
        
        args = ["--list", "--library", "--lib=%s" % loc]
        session._Session__call_console(args)
        return
        
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
            elif answer == "N":
                raise Exception("Updates not applied and Library not loaded.")
            

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