import os
import io
import time
import subprocess
import pandas as pd
import pysyncrosim as ps
from pysyncrosim._version import __version__
from pysyncrosim import helper

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
        ssim_required_version = "3.1.0"
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

    def sign_in(self):
        """
        Signs in to SyncroSim.

        Returns
        -------
        None.
        """
        is_signed_in = self.__check_signin()

        if is_signed_in:
            profile_info = self.__retrieve_profile()
            sign_in_status = "You are already signed in to the following SyncroSim account:\r\n"
            sign_in_status += f"{profile_info}\r\n"
            sign_in_status += "Use the sign_out() method to sign out of the current SyncroSim account."
            print(sign_in_status)

            return
        
        args = ["--signin", "--force"]
        self.__call_console_interactive(args)

        counter = 1
        counterMax = 60
        success = False

        while counter < counterMax and success is False:
            time.sleep(1)
            is_signed_in = self.__check_signin()
            if is_signed_in:
                success = True
            counter += 1

        if success:
            profile_info = self.__retrieve_profile()
            sign_in_status = "\r\nSuccessfully signed into SyncroSim account.\r\n"
            sign_in_status += f"{profile_info}"

        elif counter == counterMax:
            sign_in_status = "Sign in timed out.\r\n"

        else:
            sign_in_status = "Sign in failed.\r\n"

        print(sign_in_status)

    
    def sign_out(self):
        """
        Signs out of SyncroSim.
        
        Returns
        -------
        None.
        """
        is_signed_in = self.__check_signin()

        if not is_signed_in:
            sign_out_status = "You are not currently signed in.\r\n"
            print(sign_out_status)

            return
        
        else:
            args = ["--signout", "--force"]
            self.__call_console_interactive(args)

        counter = 1
        counterMax = 30
        success = False

        while counter < counterMax and success is False:
            time.sleep(1)
            is_signed_in = self.__check_signin()
            if not is_signed_in:
                success = True
            counter += 1

        if success:
            sign_out_status = "Successfully signed out of SyncroSim account."

        elif counter == counterMax:
            sign_out_status = "Sign out timed out."

        else:
            sign_out_status = "Sign out failed."

        print(sign_out_status)
    
    def view_profile(self):
        """
        Retrieves your SyncroSim profile information if signed in.
        
        Returns
        -------
        None.
        """
        profile_info = self.__retrieve_profile()

        print(profile_info)

    def __retrieve_profile(self):

        args = ["--profile"]
        p = self.__call_console(args, decode=True)

        return p
        
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
            If False, then shows all available packages. If True, then shows
            all installed packages. The default is True.

        Returns
        -------
        pkgs : pandas.DataFrame
            DataFrame listing the Name, Display Name, and Version of all
            installed base packages.

        """
        if not isinstance(installed, bool):
            raise TypeError("installed must be Logical'")
            
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

        return pkgs       
    
    def install_packages(self, packages, version=None):
        """
        Installs one or more SyncroSim packages.
        
        Parameters
        ----------
        packages : List or String
            Name or list of names of packages to install. Can also be a 
            filepath (or list of filepaths) to a local package.
        version : List or String, optional
            Version or list of versions to install. If None, then will
            install the latest version of the specified package(s).

        Returns
        -------
        None.

        """
        self.__validate_packages(packages, version)    

        # Set packages and corresponding versions
        pkgs_to_install = self.__create_install_package_list(packages, version)
        
        # Set executable to package manager
        self.console_exe = self.__init_console(pkgman=True)
        
        exception = True
        pkgs_installed = []
        try:
            for pkg, ver in pkgs_to_install:
                if os.path.exists(pkg):
                    args = ["--finstall=%s" % pkg]
                else:
                    args = [f"--install={pkg}", f"--version={ver}"]
                self.__call_console(args)
                pkgs_installed.append(f"{pkg} v{ver}")
                
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
    
    def uninstall_packages(self, packages, version=None):
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
        self.__validate_packages(packages, version)

        pkgs_to_uninstall = self.__create_uninstall_package_list(packages, version)
        
        # Set executable to package manager
        self.console_exe = self.__init_console(pkgman=True)
        
        exception = True
        pkgs_removed = []
        try:
            
            for pkg, ver in pkgs_to_uninstall:

                args = [f"--remove={pkg}", f"--version={ver}"]
                self.__call_console(args)
                pkgs_removed.append(f"{pkg} v{ver}")
                
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


    def install_conda(self, software="miniforge"):
        """
        Installs Miniforge or Miniconda to the default installation path
        within the SyncroSim installation folder. If you already
        have conda installed in a non-default location, then you
        can point SyncroSim towards that installation using the 
        conda_filepath argument when loading the Session class.

        Parameters
        ----------
        software : Str, optional
            The software to install. Options are "miniforge" (Default)
            or "miniconda".
        
        Returns
        -------
        None.

        """
        if software not in ["miniforge", "miniconda"]:
            raise ValueError("software must be 'miniforge' or 'miniconda'")

        args = ["--conda", "--install", f"--software={software}"]
        result = self.__call_console(args)

        if result.returncode == 0:
            print(f"{software} installed successfully")
        else:
            print(result.stdout.decode('utf-8'))

         
    def __init_location(self, location):
        # Initializes the location of the SyncroSim executable
        e = ps.environment._environment()
        if location is None:
            if e.program_directory.item() is None:
                location = "C:/Program Files/SyncroSim"

            else:
                location = e.program_directory.item()
        else:
            location = os.path.expanduser(location)

        if not os.path.isdir(location):
            raise ValueError("The location is not valid")
        else :
            return location
                        
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

    def __call_console_interactive(self, args):
        final_args = []
        
        final_args.append(self.console_exe)
        final_args += args
        
        if self.__print_cmd:
            print(final_args)
            
        if not self.__is_windows:
            final_args = ["mono"] + final_args
            process = subprocess.Popen(
                final_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
        else:
            process = subprocess.Popen(
                final_args,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
        
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
    def __retrieve_conda_filepath(self):        
        result = self.__call_console(["--conda", "--config"])
        
        if result.returncode != 0:
            cleaned_result = result.stderr.decode('utf-8').strip()
            if cleaned_result.contains("No conda configuration yet"):
                self.__conda_filepath = None
            else:
                self.__conda_filepath = cleaned_result.split(": ")[1]
            
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

    def __validate_packages(self, packages, version): 
        # Unit tests for inputs
        if not isinstance(packages, str):
            if not isinstance(packages, list):
                raise TypeError("packages must be a String or List")
            elif all(isinstance(pkg, str) for pkg in packages) is False:
                raise TypeError("all packages must be Strings")     
        if version is not None:
            if not isinstance(version, str):
                if not isinstance(version, list):
                    raise TypeError("version must be a String or List")
                elif all(isinstance(ver, str) for ver in version) is False:
                    raise TypeError("all versions must be Strings")   
            
    def __create_install_package_list(self, packages, version):

        # Get list of installed packages and versions
        installed = self.packages()
        installed = pd.DataFrame({"Name": installed["Name"].values,
                                  "Version": installed["Version"].values})

        # Get available packages and versions
        available = self.packages(installed=False)
        available = pd.DataFrame({"Name": available["Name"].values,
                                  "Version": available["Version"].values})

        # Set packages and corresponding versions
        if not isinstance(packages, list):
            packages = [packages]
        if version is not None:
            if not isinstance(version, list):
                version = [version]
            if len(packages) != len(version):
                raise ValueError("packages and version must have the same length")
        else:
            # Get latest version of package from available package list
            version = []
            for pkg in packages:
                if pkg in available["Name"].values:
                    avail_subset = available[available["Name"] == pkg]
                    ver = avail_subset.Version.values[len(avail_subset)-1]
                    version.append(ver)
                elif os.path.exists(pkg):
                    version.append(None)
                else:
                    raise ValueError(f"{pkg} not found in available packages")
        
        for pkg, ver in zip(packages, version):
            if pkg in installed["Name"].values:
                subset = installed[installed["Name"] == pkg]
                if subset["Version"].values[0] == ver:
                    print(f'{pkg} already installed')
                    continue
            else:
                continue

        return zip(packages, version)
    
    def __create_uninstall_package_list(self, packages, version):

        # Get list of installed packages and versions
        installed = self.packages()
        installed = pd.DataFrame({"Name": installed["Name"].values, 
                                 "Version": installed["Version"].values})

        # Set packages and corresponding versions
        if not isinstance(packages, list):
            packages = [packages]
        if version is not None:
            if not isinstance(version, list):
                version = [version]
            if len(packages) != len(version):
                raise ValueError("packages and version must have the same length")
        else:
            # If version is None, then remove all versions of the specified package
            version = []
            packages2 = []
            for pkg in packages:
                if pkg in installed["Name"].values:
                    subset = installed[installed["Name"] == pkg]
                    version.append(subset["Version"].values)
                    packages2.append(subset["Name"].values)
                else:
                    raise ValueError(f"{pkg} not found in installed packages")

            # Flatten lists  
            packages = [p for p2 in packages2 for p in p2]
            version = [v for v2 in version for v in v2]

        return zip(packages, version)
    
    def __check_signin(self):
        """
        Checks if the user is signed in to SyncroSim

        Parameters
        ----------
        session : Session
            SyncroSim Session class instance.

        Returns
        -------
        is_signed_in : Logical
            True if user is signed in, False if not.
        """

        profile_info = self.__retrieve_profile()
        is_signed_in = profile_info.startswith('Username')

        return is_signed_in