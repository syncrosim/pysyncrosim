import os
import io
import subprocess
import pandas as pd
import pysyncrosim as ps
from pysyncrosim._version import __version__

class Session(object):
    """
    A class to represent a SyncroSim Session.
    
    """    
    def __init__(self, location=None, silent=True, print_cmd=False, conda_filepath=None):
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
        conda_filepath : Str, optional
            Filepath to conda executable. If None, then uses default location

        Raises
        ------
        ValueError
            Raises error if the location given does not exist.
        RuntimeError
            Raises error if the version of the SyncroSim installation is 
            incompatible with the current version of pysyncrosim.

        Returns
        -------
        None.

        """
        self.__location = self.__init_location(location)
        self.console_exe = self.__init_console(console=True)
        self.__silent = silent
        self.__print_cmd = print_cmd
        self.__conda_filepath = conda_filepath
        self.__is_windows = os.name == 'nt'
        
        # Add check to make sure that correct version of SyncroSim is being used
        ssim_required_version = "3.0.0"
        ssim_current_version = self.version().split(" ")[-1]
        ssim_required_bits = ssim_required_version.split(".")
        ssim_current_bits = ssim_current_version.split(".")
        
        for i in range(0, len(ssim_required_bits)):
            if int(ssim_current_bits[i]) > int(ssim_required_bits[i]):
                status = True
                break
            status = int(ssim_current_bits[i]) == int(ssim_required_bits[i])
        
        if not status:
            raise RuntimeError(f"SyncroSim v{ssim_required_version} " + 
                               "is required to run pysyncrosim v" +
                               __version__ + ", but you have SyncroSim v" + 
                               ssim_current_version + " installed")
     
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

    @property
    def conda_filepath(self):
        """
        Gets or sets the filepath to the conda executable.

        Returns
        -------
        String
            Filepath to conda executable.

        """
        self.__retrieve_conda_filepath()

        return self.__conda_filepath

    @conda_filepath.setter
    def conda_filepath(self, value):
        self.__set_conda_filepath(value)
        
        
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
    
    def packages(self, installed=True, list_templates=None):
        """
        Retrieves DataFrame of installed packages.
        
        Parameters
        ----------
        installed : Logical or String, optional
            If False, then shows all available packages. If True, then shows
            all installed packages. The default is True.
        list_templates : String, optional
            The name a SyncroSim package. If provided, then will return a
            DataFrame of all templates in the package. The default is None.

        Returns
        -------
        pkgs : pandas.DataFrame
            DataFrame listing the Name, Display Name, and Version of all
            installed base packages.

        """
        if not isinstance(installed, bool):
            raise TypeError("installed must be Logical'")
        if not isinstance(list_templates, str) and list_templates is not None:
            raise TypeError("list_templates must be a String")
            
        if installed is False:
            self.console_exe = self.__init_console(pkgman=True)
            try:
                args = ["--available"]
                pkgs = self.__call_console(args, decode=True, csv=True)
                return pd.read_csv(io.StringIO(pkgs))
            finally:
                self.console_exe = self.__init_console(console=True)

        if installed is True:
            args = ["--list", "--packages"]
            pkgs = self.__call_console(args, decode=True, csv=True)
            pkgs = pd.read_csv(io.StringIO(pkgs))

        if list_templates is not None:
            if list_templates not in pkgs["Name"].values:
                raise ValueError(f"SyncroSim Package {list_templates} is not installed")
            args = ["--list", "--templates", f"--package={list_templates}"]
            templates = self.__call_console(args, decode=True, csv=True)
            return pd.read_csv(io.StringIO(templates))

        return pkgs       
    
    def install_packages(self, packages):
        """
        Installs one or more SyncroSim packages.
        
        Parameters
        ----------
        packages : List or String
            Name or list of names of packages to install. Can also be a 
            filepath (or list of filepaths) to a local package.

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
        pkgs_installed = []
        try:
        
            if not isinstance(packages, list):
                packages = [packages]
                
            for pkg in packages:
                if pkg in installed:
                    print(f'{pkg} already installed')
                    continue
                
                if os.path.exists(pkg):
                    args = ["--finstall=%s" % pkg]
                else:
                    args = ["--install=%s" % pkg]
                self.__call_console(args)
                pkgs_installed.append(pkg)
                
            # Reset packages
            self.console_exe = self.__init_console(console=True)
                
        except RuntimeError as e:
            print(e)
            
        else:
            exception = False
        
        finally:
            
            if exception is False:
                print(f"{pkgs_installed} installed successfully")
                
            # Set executable back to console
            if os.path.split(self.console_exe)[-1] != "SyncroSim.Console.exe":
                self.console_exe = self.__init_console(console=True)
    
    def uninstall_packages(self, packages):
        """
        Uninstalls one or more SyncroSim packages.

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
        pkgs_removed = []
        try:
        
            if not isinstance(packages, list):
                packages = [packages]
                
            for pkg in packages:
                if pkg not in installed:
                    print(f'{pkg} not installed')
                    continue
                args = ["--uninstall=%s" % pkg]
                self.__call_console(args)
                pkgs_removed.append(pkg)
                
            # Reset packages
            self.console_exe = self.__init_console(console=True)
            if len(pkgs_removed) == 0:
                return
            else:
                self.__pkgs = self.packages()
            
        except RuntimeError as e:
            print(e)
            
        else:
            exception = False
        
        finally:
            
            if exception is False:
                print(f"{pkgs_removed} removed successfully")
                
            # Set executable back to console
            if os.path.split(self.console_exe)[-1] != "SyncroSim.Console.exe":
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

    def install_conda(self):
        """
        Installs the Miniconda to the default installation path
        within the SyncroSim installation folder. If you already
        have conda installed in a non-default location, then you
        can point SyncroSim towards that installation using the 
        conda_filepath argument when loading the Session class.
        
        Returns
        -------
        None.

        """        
        args = ["--conda", "--install"]
        result = self.__call_console(args)

        if result.returncode == 0:
            print("Miniconda installed successfully")
        else:
            print(result.stdout.decode('utf-8'))

         
    def __init_location(self, location):
        # Initializes the location of the SyncroSim executable
        e = ps.environment._environment()
        if location is None:
            if e.program_directory.item() is None:
                return "C:/Program Files/SyncroSim"
            else:
                return e.program_directory.item()
        else:
            self.__location = os.path.expanduser(location)

        if not os.path.isdir(self.__location):
            raise ValueError("The location is not valid")
        else :
            return self.__location
                        
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

        if not self.__is_windows:
            final_args = ["mono"] + final_args

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

    def __retrieve_conda_filepath(self):        
        result = self.__call_console(["--conda", "--config"])
        self.__conda_filepath = result.stdout.decode('utf-8').strip().split(": ")[1]
            
    def __set_conda_filepath(self, filepath):
        
        self.__conda_filepath = None

        if filepath is None:
            self.__call_console(["--conda", "--clear"])
        else:
            result = self.__call_console(["--conda", "--path=" + filepath])
            if result.returncode != 0:
                raise RuntimeError(result.stderr.decode('utf-8'))
            else:
                self.__conda_filepath = filepath

    def __validate_packages(self, packages):

        if isinstance(packages, str):
            packages = [packages]
        elif not isinstance(packages, list):
            raise TypeError("packages must be a String or List of Strings")
        elif not all(isinstance(item, str) for item in packages):
            raise TypeError("packages must be a String or List of Strings")
        
        return packages