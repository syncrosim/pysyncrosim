import os
import io
import subprocess
import pandas as pd
import pysyncrosim as ps

class Session(object):
    """
    A class to represent a SyncroSim Session.
    
    ...
    
    Attributes
    ----------
    location : String
        Retrieves the location for this Session.
    silent : Logical
        Gets or sets the silent status for this Session.
    print_cmd : Logical
        Gets or sets the print_cmd status of the SyncroSim Session.
        
    Methods
    -------
    version():
        Retrieves SyncroSim version.
    packages(installed=True):
        Retrieves DataFrame of installed packages.
    add_packages(packages):
        Installs a package.
    remove_packages(packages):
        Uninstalls a package.
    update_packages(packages=None):
        Updates a package to the newest version.
    
    """
    __pkgs = None
    
    def __init__(self, location=None, silent=True, print_cmd=False):
        """
        Initializes a pysyncrosim Session instance.

        Parameters
        ----------
        location : Str, optional
            Filepath to SyncroSim executable. If None, then uses default
            location on windows. The default is None.
        silent : Logical, optional
            If True, will not print warnings from the console. The default is 
            True.
        print_cmd : Logical, optional
            If True, arguments from the console command will be printed. The 
            default is False.

        Raises
        ------
        ValueError
            Raises error if the location given does not exist.

        Returns
        -------
        None.

        """
        self.__location = self.__init_location(location)
        self.console_exe = self.__init_console(console=True)
        self.__silent = silent
        self.__print_cmd = print_cmd
        self.__pkgs = self.packages()
     
    @property
    def location(self):
        """
        Retrieves the location for this Session.

        Returns
        -------
        String
            Filepath to SyncroSim Session.
            
        """
        return self.__location
    
    @property
    def silent(self):
        """
        Gets or sets the silent status for this Session.

        Returns
        -------
        Logical
            Silent status.
            
        """
        return self.__silent
    
    @silent.setter
    def silent(self, value):
        if value is None:
            raise AttributeError("The silent status cannot be None.")
        elif not isinstance(value, bool):
            raise AttributeError("silent must be a Logical")
        self.__silent = value
        
    @property
    def print_cmd(self):
        """
        Gets or sets the print_cmd status of the SyncroSim Session.

        Returns
        -------
        Logical
            print_cmd status.

        """
        
        return self.__print_cmd
    
    @print_cmd.setter
    def print_cmd(self, value):
        if value is None:
            raise AttributeError("The print_cmd status cannot be None.")
        elif not isinstance(value, bool):
            raise AttributeError("print_cmd must be a Logical")
        self.__print_cmd = value
        
        
    def version(self):
        """
        Retrieves SyncroSim version.

        Returns
        -------
        String
            Version number.

        """
        args = ["--version"]
        v = self.__call_console(args, decode=True)
        
        return v.rstrip()
    
    def packages(self, installed=True):
        """
        Retrieves DataFrame of installed packages.
        
        Parameters
        ----------
        installed : Logical or String, optional
            If False, then shows all available packages. If "BASE", only shows
            installed base packages. If True, then shows installed 
            addons in addition to base packages. The default is True.

        Returns
        -------
        pkgs : pandas.DataFrame
            DataFrame listing the Name, Display Name, and Version of all
            installed base packages.

        """
        if not isinstance(installed, bool) and installed != "BASE":
            raise TypeError("installed must be Logical or 'BASE'")
        
        if installed is True or installed == "BASE":
            args = ["--list", "--basepkgs"]
            self.__pkgs = self.__call_console(args, decode=True, csv=True)
            self.__pkgs = pd.read_csv(io.StringIO(self.__pkgs))
            
        if installed is True:    
            args = ["--list", "--addons"]
            addons = self.__call_console(args, decode=True, csv=True)
            addons = pd.read_csv(io.StringIO(addons))
            self.__pkgs = self.__pkgs.append(addons).reset_index()
            
        if installed is False:
            self.console_exe = self.__init_console(pkgman=True)
            try:
                args = ["--available"]
                pkgs = self.__call_console(args, decode=True, csv=True)
                return pd.read_csv(io.StringIO(pkgs))
            finally:
                self.console_exe = self.__init_console(console=True)

        return self.__pkgs        
    
    def add_packages(self, packages):
        """
        Installs a package.
        
        Parameters
        ----------
        packages : List or String
            Name or list of names of packages to install.

        Returns
        -------
        None.

        """
        # Unit tests for inputs
        if not isinstance(packages, str):
            if not isinstance(packages, list):
                raise TypeError("packages must be a String or List")
            elif all(isinstance(pkg, str) for pkg in packages) is False:
                raise TypeError("all packages must be Strings")            
        
        # Add some checks to see whether package is installed
        installed = self.packages()
        installed = installed["Name"].values
        
        # Set executable to package manager
        self.console_exe = self.__init_console(pkgman=True)
        
        exception = True
        try:
        
            if not isinstance(packages, list):
                packages = [packages]
                
            for pkg in packages:
                if pkg in installed:
                    print(f'{pkg} already installed')
                    continue
                args = ["--install=%s" % pkg]
                self.__call_console(args)
                
            # Reset packages
            self.console_exe = self.__init_console(console=True)
            self.__pkgs = self.packages()
                
        except RuntimeError as e:
            print(e)
            
        else:
            exception = False
        
        finally:
            if exception is False:
                print(f"{packages} installed successfully")
            # Set executable back to console
            self.console_exe = self.__init_console(console=True)
    
    def remove_packages(self, packages):
        """
        Uninstalls a package.

        Parameters
        ----------
        packages : List or String
            Name or list of names of packages to uninstall.

        Returns
        -------
        None.

        """
        # Unit tests for inputs
        if not isinstance(packages, str):
            if not isinstance(packages, list):
                raise TypeError("packages must be a String or List")
            elif all(isinstance(pkg, str) for pkg in packages) is False:
                raise TypeError("all packages must be Strings")   
        
        # Add some checks to see whether package is installed
        installed = self.packages()
        installed = installed["Name"].values
        
        # Set executable to package manager
        self.console_exe = self.__init_console(pkgman=True)
        
        exception = True
        try:
        
            if not isinstance(packages, list):
                packages = [packages]
                
            for pkg in packages:
                if pkg not in installed:
                    print(f'{pkg} not installed')
                    continue
                args = ["--uninstall=%s" % pkg]
                self.__call_console(args)
                
            # Reset packages
            self.console_exe = self.__init_console(console=True)
            self.__pkgs = self.packages()
            
        except RuntimeError as e:
            print(e)
            
        else:
            exception = False
        
        finally:
            if exception is False:
                print(f"{packages} removed successfully")
            # Set executable back to console
            self.console_exe = self.__init_console(console=True)
    
    def update_packages(self, packages=None):
        """
        Updates a package to the newest version.
        
        Parameters
        ----------
        packages : List or String
            Name or list of names of packages to update. If None, then
            updates all packages. Default is None.

        Returns
        -------
        None.

        """
        # Unit tests for inputs
        if packages is not None:
            if not isinstance(packages, str):
                if not isinstance(packages, list):
                    raise TypeError("packages must be a String or List")
                elif all(isinstance(pkg, str) for pkg in packages) is False:
                    raise TypeError("all packages must be Strings")   
        
        # Add some checks to see whether package is installed
        pkg_df = self.packages()
        installed = pkg_df["Name"].values
        
        self.console_exe = self.__init_console(pkgman=True)
            
        try:
            
            if packages is None:
                args = ["--updateall"]
                
            elif not isinstance(packages, list):
                packages = [packages]
                
            for pkg in packages:
                if pkg not in installed:
                    print(f'{pkg} not installed')
                    continue
                # Compare versions
                v1 = pkg_df[pkg_df["Name"] == pkg].Version.item()
                args = ["--updatepkg=%s" % pkg]
                self.__call_console(args)
                self.console_exe = self.__init_console(console=True)
                # Also resets packages below
                pkg_df2 = self.packages()
                v2 = pkg_df2[pkg_df2["Name"] == pkg].Version.item()
                if v1 == v2:
                    print(f"{pkg} already up to date")
                if v1 < v2:
                    print(f"{pkg} updated from v{v1} to v{v2}")
                self.console_exe = self.__init_console(pkgman=True)
                
        finally:
        
            # Set executable back to console
            self.console_exe = self.__init_console(console=True)
         
    def __init_location(self, location):
        # Initializes the location of the SyncroSim executable
        self.__location = location # dja  not working as expected,  The self.__location value set here is being over written when the function returns
        e = ps.environment._environment()
        if self.__location is None:
            if e.program_directory.item() is None:
                return "C:/Program Files/SyncroSim"
            else:
                return e.program_directory.item()
        elif not os.path.isdir(self.__location):
            raise ValueError("The location is not valid")
        else :
            return location # dja just added a statement to return the passed in location path assuming all the other tests were passed.
                        
    def __init_console(self, console=None, pkgman=None):
        
        if console is True:
            return os.path.join(self.__location,
                                "SyncroSim.Console.exe")
            
        elif pkgman is True:
            return os.path.join(self.__location,
                                "SyncroSim.PackageManager.exe")
            
        else:
            raise ValueError("No executable assigned")
    
    def __call_console(self, args, csv=False, decode=False):
        final_args = []
        
        final_args.append(self.console_exe)
        final_args += args
        
        if csv:
            final_args += ["--csv"]
            
        if self.__print_cmd:
            print(final_args)
        
        result = subprocess.run(
            final_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        
        if result.returncode !=0:
            if self.silent is False:
                print(final_args, flush=True)
            raise RuntimeError(result.stderr.decode('utf-8'))
            
        if decode is True:
            return result.stdout.decode('utf-8')
        else:    
            return result




