import os
import pysyncrosim as ps
import pytest
import pandas as pd
import math
import numpy as np
import rasterio
import tempfile

temp_path = tempfile.TemporaryDirectory()
session_path = None
test_lib_name = os.path.join(temp_path.name, "stsimLibrary.ssim")
existing_lib_name = os.path.join("C:/gitprojects/pysyncrosim/tests", "spatial-example.ssim")

def test_session_attributes():
    
    mySession = ps.Session(session_path)
    
    # Test init
    assert isinstance(mySession, ps.Session)
    
    with pytest.raises(ValueError, match="The location is not valid"):
        mySession = ps.Session(location="bad/location")
        
    # Test version method
    assert isinstance(mySession.version(), str)
    assert "Version is:" in mySession.version()
    
    # Test packages method
    assert isinstance(mySession.packages(), pd.DataFrame)
    assert isinstance(mySession.packages(installed=False), pd.DataFrame)
    
    with pytest.raises(TypeError,
                       match="installed must be Logical"):
        mySession.packages(installed=1)

    # Test conda_filepath
    conda_fp = mySession.conda_filepath
    assert isinstance(conda_fp, str) or conda_fp is None  

def test_session_package_functions():
    
    mySession = ps.Session(session_path)
    
    # Test install_packages, uninstall_packages methods
    with pytest.raises(TypeError, match="packages must be a String or List"):
        mySession.install_packages(1)
    with pytest.raises(TypeError, match="packages must be a String or List"):
        mySession.uninstall_packages(1)
        
    with pytest.raises(TypeError, match="all packages must be Strings"):
        mySession.install_packages(["helloworld", 1])
    with pytest.raises(TypeError, match="all packages must be Strings"):
        mySession.uninstall_packages(["helloworld", 1])
        
    # Test with no version
    mySession.install_packages("helloworld")
    assert "helloworld" in mySession.packages()["Name"].values
    
    mySession.uninstall_packages("helloworld")
    assert "helloworld" not in mySession.packages()["Name"].values
    
    # Test with version - this requires v2.0.0 and v2.0.2 to be on package repo
    mySession.install_packages("helloworld", version="2.0.0")
    pkg_subset = mySession.packages()[mySession.packages()["Name"] == "helloworld"]
    assert "2.0.0" in pkg_subset["Version"].values

    # Should now have two versions of the package
    mySession.install_packages("helloworld", version="2.0.1")
    pkg_subset = mySession.packages()[mySession.packages()["Name"] == "helloworld"]
    assert "2.0.0" in pkg_subset["Version"].values
    assert "2.0.1" in pkg_subset["Version"].values

    # Test uninstall with version
    mySession.uninstall_packages("helloworld", version="2.0.0")
    pkg_subset = mySession.packages()[mySession.packages()["Name"] == "helloworld"]
    assert "2.0.0" not in pkg_subset["Version"].values
    assert "2.0.1" in pkg_subset["Version"].values
    
def test_helper():
    
    mySession = ps.Session(session_path)
    mySession.install_packages("stsim")
    mySession.install_packages("stsimecodep")
    
    # Type checking
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument"):
        ps.library()
        
    with pytest.raises(TypeError, match="name must be a String"):
        ps.library(name=1)
        
    with pytest.raises(
            TypeError,
            match="session must be None or pysyncrosim Session instance"):
        ps.library(name=test_lib_name, session=1)
        
    with pytest.raises(TypeError, match="packages must be None, a String, or a List"):
        ps.library(name=test_lib_name, packages=1, session=mySession)

    with pytest.raises(TypeError, match="packages in list are not all strings"):
        ps.library(name=test_lib_name, packages=["package", 1], session=mySession)
        
    with pytest.raises(TypeError, match="forceUpdate must be a Logical"):
        ps.library(name=test_lib_name, forceUpdate="True", session=mySession)
        
    with pytest.raises(TypeError, match="overwrite must be a Logical"):
        ps.library(name=test_lib_name, overwrite="False", session=mySession)

    # Test package installation
    mySession.install_packages("demosales")
    mySession.uninstall_packages("demosales")
    with pytest.raises(ValueError, match="The package demosales is not installed"):
        ps.library(name=test_lib_name, packages="demosales", session=mySession)
    mySession.install_packages("stsim")
        
    # Test Library path
    with pytest.raises(ValueError, match="Path to Library does not exist"):
        ps.library("path/to/library", session=mySession)
      
    # Test output
    myLibrary = ps.library(name=test_lib_name, forceUpdate=True, session=mySession)
    assert isinstance(myLibrary, ps.Library)

    # Test packages argument
    myLibrary = ps.library(name = test_lib_name,
                       session = mySession,
                       packages = ["stsim", "stsimecodep"],
                       overwrite = True)
    pkg_list = myLibrary.packages["Name"].tolist()
    assert "core" in pkg_list
    assert "stsim" in pkg_list
    assert "stsimecodep" in pkg_list
    assert len(pkg_list) == 3
    
def test_library_attributes():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, overwrite=True, session=mySession)
    
    # Check attributes
    assert isinstance(myLibrary.name, str)
    assert isinstance(myLibrary.session, ps.Session)
    assert isinstance(myLibrary.location, str)
    assert os.path.isfile(myLibrary.location)

    # Check environment error
    with pytest.raises(RuntimeError,
            match="Not in a SyncroSim environment."):
        ps.Library()

def test_library_projects():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, overwrite=True, session=mySession)
    
    # Test inputs
    with pytest.raises(TypeError, match="name must be a String"):
        myLibrary.projects(name=1)
        
    with pytest.raises(TypeError, match="pid must be an Integer"):
        myLibrary.projects(pid="1")
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myLibrary.projects(summary="False")
        
    with pytest.raises(TypeError, match="overwrite must be a Logical"):
        myLibrary.projects(overwrite="False")
        
    with pytest.raises(ValueError,
                       match="pid specified, but no Projects created yet"):
        myLibrary.projects(pid=2)
    
    with pytest.raises(ValueError,
                       match="Project ID 1 does not match Project name test2"):
        myLibrary.projects(name="test")
        myLibrary.projects(name="test2", pid=1)
        
    with pytest.raises(ValueError, match="Project ID 3 does not exist"):
        myLibrary.projects(pid=3)
        
    # Test outputs
    assert isinstance(myLibrary.projects(), pd.DataFrame)
    assert isinstance(myLibrary.projects(name="test"), ps.Project)  
    assert isinstance(myLibrary.projects(summary=False), list)
        
def test_library_scenarios():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, overwrite=True, session=mySession)
    myLibrary.projects(name="test")
    
    with pytest.raises(
            TypeError, 
            match="name must be a String, Integer, or List of these"):
        myLibrary.scenarios(name=pd.DataFrame())
        
    with pytest.raises(
            TypeError,
            match="project must be Project instance, String, or Integer"):
        myLibrary.scenarios(project=[1])
        
    with pytest.raises(TypeError, match="sid must be an Integer"):
        myLibrary.scenarios(sid="1")
    
    with pytest.raises(TypeError, match="pid must be an Integer"):
        myLibrary.scenarios(pid="1")
    
    with pytest.raises(TypeError, match="overwrite must be a Logical"):
        myLibrary.scenarios(overwrite="False")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myLibrary.scenarios(optional=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myLibrary.scenarios(summary="True")
        
    with pytest.raises(ValueError, match="Scenario ID 2 does not exist"):
        myLibrary.scenarios(sid=2)
        
    # Test scenarios method outputs
    assert myLibrary.scenarios(name="test").name == "test"
    assert myLibrary.scenarios(name="test2", sid=1).name == "test"
    assert isinstance(myLibrary.scenarios(name="test"), ps.Scenario)
    assert isinstance(myLibrary.scenarios(name="test", sid=1), ps.Scenario)
    assert isinstance(myLibrary.scenarios(), pd.DataFrame)
    
    myLibrary.projects(name="project2")
    with pytest.raises(ValueError, match="More than one Project in Library"):
        myLibrary.scenarios(summary=False)
    
    assert isinstance(myLibrary.scenarios(), pd.DataFrame) 
    assert isinstance(myLibrary.scenarios(pid=1, summary=False), ps.Scenario)
    assert len(myLibrary.scenarios(pid=1).columns) == 4
    assert len(myLibrary.scenarios(pid=1, optional=True).columns) == 10
    assert myLibrary.scenarios(name="test", pid=1, overwrite=True).sid != 1
    assert all(myLibrary.scenarios(project=1) == myLibrary.scenarios(pid=1))
    assert all(
        myLibrary.scenarios(project="test") == myLibrary.scenarios(pid=1))
    myProject = myLibrary.projects("test")
    assert all(myLibrary.scenarios(
        project=1) == myLibrary.scenarios(project=myProject))
    
def test_library_datasheets():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, overwrite=True, 
                           packages=["stsim"], session=mySession)
    
    # Test datasheets method inputs
    with pytest.raises(TypeError, match="name must be a String"):
        myLibrary.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myLibrary.datasheets(summary=1)
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myLibrary.datasheets(optional=[1, 2, 3])
        
    with pytest.raises(TypeError, match="filter_column must be a String"):
        myLibrary.datasheets(filter_column=1)
    
    with pytest.raises(
            RuntimeError,
            match="The scope must be 'Library', 'Project, or 'Scenario'"):
        myLibrary.datasheets(scope="test")
        
    with pytest.raises(
            ValueError,
            match="datasheet name must be prefixed with package name"):
        myLibrary.datasheets(name="test")
        
    with pytest.raises(
            ValueError,
            match="filter column Test not in Datasheet core_Option"):
        myLibrary.datasheets(name="core_Option", filter_column="Test",
                             filter_value=1)
        
    # Test datasheets method outputs
    assert isinstance(myLibrary.datasheets(), pd.DataFrame)
    assert isinstance(myLibrary.datasheets(name="core_Backup"), pd.DataFrame)
    assert isinstance(myLibrary.datasheets(summary=False), list)
    assert len(myLibrary.datasheets().columns) == 3
    assert len(myLibrary.datasheets(optional=True).columns) == 6
    assert myLibrary.datasheets(name="core_Backup", empty=True).empty
    assert not myLibrary.datasheets().equals(
        myLibrary.datasheets(scope="Project"))
    assert not myLibrary.datasheets().equals(
        myLibrary.datasheets(scope="Scenario"))
    
def test_library_delete():

    mySession = ps.Session(session_path)   
    myLibrary = ps.library(name=test_lib_name, overwrite=True, session=mySession)
    myLibrary.projects(name="test")
    
    # Test delete method
    with pytest.raises(
            TypeError,
            match="project must be a Project instance, Integer, or String"):
        myLibrary.delete(project=1.5)
    
    with pytest.raises(
            TypeError,
            match="scenario must be a Scenario instance, Integer, or String"):
        myLibrary.delete(scenario=1.5)
        
    with pytest.raises(TypeError, match="force must be a Logical"):
        myLibrary.delete(force="True")
        
    with pytest.raises(ValueError, match="Project ID 2 does not exist"):
        myLibrary.delete(project=2)
        
    with pytest.raises(ValueError, match="project dne does not exist"):
        myLibrary.delete(project="dne")
        
    with pytest.raises(ValueError, match="Scenario ID 50 does not exist"):
        myLibrary.delete(scenario=50)
        
    with pytest.raises(ValueError, match="scenario dne does not exist"):
        myLibrary.delete(scenario="dne")
        
    myLibrary.delete(project="test", force=True)
    assert myLibrary._Library__projects.empty
    assert "test" not in myLibrary.projects().Name.values
    
    myLibrary.scenarios(name="test")
    myLibrary.delete(scenario="test", force=True)
    assert "test" not in myLibrary.scenarios().Name.values
    
def test_library_save_datasheet():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, overwrite=True, forceUpdate=True, session=mySession)
    
    # Test save_datasheet method
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument:"):
        myLibrary.save_datasheet(name=1)
    
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument:"):
        myLibrary.save_datasheet(data=1)
        
    with pytest.raises(TypeError, match="name must be a String"):
        myLibrary.save_datasheet(name=1, data=1)
        
    with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
        myLibrary.save_datasheet(name="test", data=1)

    with pytest.raises(TypeError, match="append must be a Logical"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame(), append="True")

    with pytest.raises(TypeError, match="force must be a Logical"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame(), force="True")
        
    with pytest.raises(TypeError, match="scope must be a String"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame(), scope=1)
        
    with pytest.raises(ValueError,
                       match="datasheet name must be prefixed with package name"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame(), force=True)
        
    with pytest.raises(
            RuntimeError,
            match="The header references a column that does not belong"):
        random_df = pd.DataFrame({"col1": [1], "col2": [2]})
        myLibrary.save_datasheet(name="core_Backup", data=random_df)

    with pytest.raises(
        RuntimeError,
        match ="The transfer method is not valid for a single row data sheet."
    ):
        myLibDF = pd.DataFrame({"IncludeData": ["Yes"],
                                "BeforeUpdate": ["Yes"]})
        myLibrary.save_datasheet(name="core_Backup", data=myLibDF, append=True)
    
    initial_core_backup = myLibrary.datasheets(name="core_Backup")
    assert (initial_core_backup["IncludeData"] == "Yes").item()
    
    initial_core_backup["IncludeData"] = "No"
    myLibrary.save_datasheet(name="core_Backup", data=initial_core_backup)
    modified_core_backup = myLibrary.datasheets(name="core_Backup")
    assert (modified_core_backup["IncludeData"] == "No").item()   

    initial_core_backup["IncludeData"] = True
    myLibrary.save_datasheet(name="core_Backup", data=initial_core_backup)
    modified_core_backup = myLibrary.datasheets(name="core_Backup")
    assert (modified_core_backup["IncludeData"] == "Yes").item() 

    myLibDF = pd.DataFrame({"IncludeData": ["Yes"],
                            "BeforeUpdate": ["Yes"]})
    myLibrary.save_datasheet(name="core_Backup", data=myLibDF)
    assert myLibrary.datasheets(name="core_Backup").equals(myLibDF)

    myLibrary.save_datasheet(name="core_Backup", data=pd.DataFrame())
    assert myLibrary.datasheets(name="core_Backup").equals(myLibDF)

    myLibrary.save_datasheet(name="core_Backup", data=pd.DataFrame(), force=True)
    assert myLibrary.datasheets(name="core_Backup").empty
    
def test_library_run():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=existing_lib_name, 
                           session=mySession,
                           forceUpdate=True)
    all_scns = myLibrary.scenarios()
    num_parent_scns = len(all_scns[all_scns["IsResult"] == "No"])
    num_scns = len(all_scns)
    scn_id = myLibrary.scenarios().iloc[1].ScenarioId
    proj_id = myLibrary.projects().iloc[0].ProjectId
    
    # Test run method
    with pytest.raises(
            TypeError,
            match="must be Scenario instance, String, Integer, or List"):
        myLibrary.run(scenarios=pd.DataFrame())

    with pytest.raises(
            TypeError,
            match="project must be Project instance, String, or Integer"):
        myLibrary.run(project=[proj_id])
    
    myLibrary.run()
    num_scns += num_parent_scns
    assert len(myLibrary.scenarios()) == num_scns
    assert myLibrary.scenarios().iloc[-1]["IsResult"] == "Yes"
    
    myLibrary.run(project=proj_id)
    num_scns += num_parent_scns
    assert len(myLibrary.scenarios()) == num_scns
    assert myLibrary.scenarios().iloc[-1]["IsResult"] == "Yes"
    
    myLibrary.run(project=proj_id, scenarios=scn_id)
    num_scns += 1
    assert len(myLibrary.scenarios()) == num_scns     
    assert myLibrary.scenarios().iloc[-1]["IsResult"] == "Yes"
    
    myLibrary.projects(name="New Project")
    with pytest.raises(
            ValueError,
            match="Must specify project when > 1 Project in the Library"):
        myLibrary.run()

    myLibrary.delete(project="New Project", force=True)
    
def test_project_attributes():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, packages=["helloworld"],
                           overwrite=True, session=mySession)
    myProject = myLibrary.projects(name="Definitions")
    
    # Check attributes
    assert isinstance(myProject.pid, int)
    assert myProject.pid == 1
    assert isinstance(myProject.name, str)
    assert myProject.name == "Definitions"
    assert isinstance(myProject.library, ps.Library)
    
def test_project_scenarios():  
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, packages=["helloworld"],
                           overwrite=True, session=mySession)
    myProject = myLibrary.projects(name="Definitions")
    
    # Test scenarios method
    with pytest.raises(
            TypeError,
            match="name must be a String, Integer, or List of these"):
        myProject.scenarios(name=pd.DataFrame())
        
    with pytest.raises(TypeError, match="sid must be an Integer"):
        myProject.scenarios(sid="1")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myProject.scenarios(optional=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myProject.scenarios(summary="1")
      
    assert isinstance(myProject.scenarios(), pd.DataFrame)
    assert isinstance(myProject.scenarios(summary=False), list)
    assert myProject.scenarios().empty
    assert len(myProject.scenarios().columns) == 4
    assert len(myProject.scenarios(optional=True).columns) == 10    
    assert isinstance(myProject.scenarios(name="test"), ps.Scenario)
    assert len(myProject.scenarios()) == 1
    assert isinstance(myProject.scenarios(sid=1), ps.Scenario)    

def test_project_datasheets():

    mySession = ps.Session(session_path)
    pkgs_to_add = ["stsim", "stsimecodep", "dgsim", "helloworld"]
    for pkg in pkgs_to_add:
        if pkg not in mySession.packages()["Name"].values:
            mySession.install_packages(pkg)

    myLibrary = ps.library(name=test_lib_name, packages=["helloworld"], 
                           overwrite=True, session=mySession)
    myProject = myLibrary.projects(name="Definitions")
    
    # Test Datasheets
    with pytest.raises(TypeError, match="name must be a String"):
        myProject.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myProject.datasheets(summary="1")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myProject.datasheets(optional=1)
        
    with pytest.raises(TypeError, match="empty must be a Logical"):
        myProject.datasheets(empty=1)
        
    assert isinstance(myProject.datasheets(), pd.DataFrame)
    assert isinstance(myProject.datasheets(summary=False), list)
    assert len(myProject.datasheets().columns) == 3
    assert len(myProject.datasheets(optional=True).columns) == 6
    assert myProject.datasheets(name="core_Transformer").empty is False
    assert myProject.datasheets(name="core_Transformer", empty=True).empty

    # Test Addon Datasheet return
    myLibrary = ps.library(name = "Test",
                          package = "stsim",
                          addons = ["stsimsf", "stsimcbmcfs3"],
                          overwrite=True)

    myProject = myLibrary.projects(name = "Definitions")
    ds = myProject.datasheets(name = "stsimsf_FlowGroup")
    assert isinstance(ds, pd.DataFrame)
    
def test_project_save_datasheet():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, packages=["helloworld"],
                           overwrite=True, forceUpdate=True, 
                           session=mySession)
    myProject = myLibrary.projects(name="Definitions")
    myLibrary.scenarios(name="test")
    myLibrary.scenarios(name="test2")
    myLibrary.scenarios(name="test3")
    
    # Test save_datasheet
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument"):
        myProject.save_datasheet(name=1)
        
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument:"):
        myProject.save_datasheet(data=1)
        
    with pytest.raises(TypeError, match="name must be a String"):
        myProject.save_datasheet(name=1, data=1)
        
    with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
        myProject.save_datasheet(name="test", data=1)
        
    assert myProject.datasheets(name="core_DistributionType").empty
    test_datasheet = pd.DataFrame({"Name": ["Test"], 
                                   "Description": ["Test Distribution Type"],
                                   "IsInternal": [False]})
    myProject.save_datasheet(name="core_DistributionType", data=test_datasheet)
    assert myProject.datasheets(name="core_DistributionType").empty is False
    assert myProject.datasheets(name = "core_DistributionType").equals(test_datasheet)

    myProjDF2 = pd.DataFrame({"Name": ["Test2"], 
                              "Description": ["Test Distribution Type2"],
                              "IsInternal": [False]})
    myProject.save_datasheet(name = "core_DistributionType", data = myProjDF2, append=False, force=True)
    assert len(myProject.datasheets(name = "core_DistributionType")) == 1

    myProjDF2 = pd.DataFrame({"Name": ["Test3"], 
                              "Description": ["Test Distribution Type3"],
                              "IsInternal": [False]})    
    myProject.save_datasheet(name = "core_DistributionType", data = myProjDF2, append=True, force=True)
    assert len(myProject.datasheets(name = "core_DistributionType")) == 2

    myProjDF2 = pd.DataFrame({"Name": ["Test4"], 
                              "Description": ["Test Distribution Type4"],
                              "IsInternal": [False]})    
    myProject.save_datasheet(name = "core_DistributionType", data = myProjDF2, append=False)
    assert len(myProject.datasheets(name = "core_DistributionType")) == 2

    myProject.save_datasheet(name = "core_DistributionType", data = pd.DataFrame())
    assert len(myProject.datasheets(name = "core_DistributionType")) == 2

    myProject.save_datasheet(name = "core_DistributionType", data = pd.DataFrame(), force=True)
    assert myProject.datasheets(name = "core_DistributionType").empty

def test_project_copy_delete():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, packages=["helloworld"], 
                           overwrite=True, session=mySession)
    myProject = myLibrary.projects(name="Definitions")

    # Test copy
    with pytest.raises(TypeError, match="name must be a String"):
        myProject.copy(name=1)

    test_datasheet = pd.DataFrame({"Name": ["Test"], 
                                   "Description": ["Test Distribution Type"],
                                   "IsInternal": [False]})
    myProject.save_datasheet(name="core_DistributionType", data=test_datasheet)
        
    myNewProj = myProject.copy()
    assert myNewProj.name == "Definitions - Copy"
    assert myNewProj.datasheets(name="core_DistributionType").empty is False
    
    myNewerProj = myProject.copy(name="Definitions 2")
    assert myNewerProj.name == "Definitions 2"
    assert myNewerProj.datasheets(name="core_DistributionType").empty is False
    
    # Test delete    
    with pytest.raises(
            TypeError,
            match="scenario must be a Scenario instance, Integer, or String"):
        myNewProj.delete(scenario=[1])  
        
    with pytest.raises(RuntimeError, match="The project does not exist"):
        myNewProj.delete(force=True)
        myNewProj.scenarios()

def test_project_run():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=existing_lib_name, 
                           session=mySession,
                           forceUpdate=True)
    myProject = myLibrary.projects(name="Definitions")
    all_scns = myProject.scenarios()
    num_parent_scns = len(all_scns[all_scns["IsResult"] == "No"])
    num_scns = len(all_scns)
    scn_id = myProject.scenarios().iloc[1].ScenarioId

    myProject.run([scn_id])
    num_scns += 1
    assert len(myProject.scenarios()) == num_scns
    assert myProject.scenarios().iloc[-1]["IsResult"] == "Yes"

    myProject.run()
    num_scns += num_parent_scns
    assert len(myProject.scenarios()) == num_scns
    assert myProject.scenarios().iloc[-1]["IsResult"] == "Yes"

    myProject.run(scn_id)
    num_scns += 1
    assert len(myProject.scenarios()) == num_scns
    assert myProject.scenarios().iloc[-1]["IsResult"] == "Yes"

    scenarios = myProject.scenarios()
    result_scenarios = scenarios[
    scenarios["IsResult"] == "Yes"].ScenarioId.tolist()
    for result_scn in result_scenarios:
        myProject.delete(scenario=result_scn, force=True)
    assert len(myProject.scenarios()) == 2

def test_scenarios_attributes():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, packages="helloworld",
                           overwrite=True, session=mySession)
    myScenario = myLibrary.scenarios("Test Scenario")
    
    # Check attributes
    assert isinstance(myScenario.sid, int) or isinstance(
        myScenario.sid, np.int64)
    assert myScenario.sid == 1
    assert isinstance(myScenario.name, str)
    assert myScenario.name == "Test Scenario"
    assert isinstance(myScenario.project, ps.Project)
    assert isinstance(myScenario.library, ps.Library)
    assert isinstance(myScenario.is_result, str)
    assert myScenario.is_result == "No"
    assert math.isnan(myScenario.parent_id)
    
def test_scenario_datasheets():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, 
                           packages=["stsim"],
                           overwrite=True,
                           session=mySession)
    myScenario = myLibrary.scenarios("test")
    
    # Test datasheets
    with pytest.raises(TypeError, match="name must be a String"):
        myScenario.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical"):
        myScenario.datasheets(summary="1")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myScenario.datasheets(optional=1)
        
    with pytest.raises(TypeError, match="empty must be a Logical"):
        myScenario.datasheets(empty=1)
        
    assert isinstance(myScenario.datasheets(), pd.DataFrame)
    assert isinstance(myScenario.datasheets(summary=False), list)
    assert len(myScenario.datasheets().columns) == 3
    assert len(myScenario.datasheets(optional=True).columns) == 7

    runcontrol = myScenario.datasheets(name="stsim_RunControl")
    runcontrol = pd.DataFrame({"MaximumTimestep": [2], 
                               "MaximumIteration": [2]})
    myScenario.save_datasheet("stsim_RunControl", runcontrol)

    assert isinstance(myScenario.datasheets(
        name="stsim_RunControl",
        filter_column="MinimumIteration", 
        filter_value="1"), pd.DataFrame)
    assert len(myScenario.datasheets(
        name="stsim_RunControl",
        filter_column="MinimumIteration",
        filter_value="1") == 1)
    assert myScenario.datasheets(
        name="stsim_RunControl",
        filter_column="MinimumIteration",
        filter_value="2").empty    
    assert myScenario.datasheets(name="stsim_RunControl").empty is False
    assert myScenario.datasheets(name="stsim_RunControl", empty=True).empty

def test_scenario_save_datasheet():

    mySession = ps.Session(session_path)
    mySession.install_packages("helloworld")
    myLibrary = ps.library(name=test_lib_name, 
                           packages="helloworld",
                           overwrite=True,
                           session=mySession)
    myScenario = myLibrary.scenarios(name="test")    

    # Test save_datasheet
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument"):
        myScenario.save_datasheet(name=1)
        
    with pytest.raises(
            TypeError,
            match="missing 1 required positional argument:"):
        myScenario.save_datasheet(data=1)
        
    with pytest.raises(TypeError, match="name must be a String"):
        myScenario.save_datasheet(name=1, data=1)
        
    with pytest.raises(TypeError, match="data must be a pandas DataFrame"):
        myScenario.save_datasheet(name="test", data=1)

    myDataFrame = pd.DataFrame({'x': [1.5], 'a': [2]})
    myScenario.save_datasheet(name="helloworld_InputDatasheet", data=myDataFrame)
    assert myScenario.datasheets(name="helloworld_InputDatasheet").equals(myDataFrame)

    myDataFrame2 = pd.DataFrame({'x': [2.5], 'a': [2]})
    myScenario.save_datasheet(name="helloworld_InputDatasheet", data=myDataFrame2, append=True)
    assert len(myScenario.datasheets(name="helloworld_InputDatasheet")) == 2

    myScenario.save_datasheet(name="helloworld_InputDatasheet", data=myDataFrame2, append=False)
    assert len(myScenario.datasheets(name="helloworld_InputDatasheet")) == 1

    myScenario.save_datasheet(name="helloworld_InputDatasheet", data=pd.DataFrame())
    assert myScenario.datasheets(name="helloworld_InputDatasheet").empty
    
def test_scenario_run_and_results():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=existing_lib_name, 
                           session=mySession,
                           forceUpdate=True)
    all_scns = myLibrary.scenarios()
    num_scns = len(all_scns)
    scn_id = myLibrary.scenarios().iloc[1].ScenarioId
    myScenario = myLibrary.scenarios(sid=scn_id)
    runcontrol = myScenario.datasheets(name="stsim_RunControl")
    runcontrol["MaximumIteration"] = 2
    runcontrol["MinimumTimestep"] = 2000
    runcontrol["MaximumTimestep"] = 2020
    myScenario.save_datasheet("stsim_RunControl", runcontrol)
    
    # Test run
    myScenario.run()    
    assert len(myLibrary.scenarios()) == num_scns + 1 
    assert myLibrary.scenarios().iloc[-1]["IsResult"] == "Yes"
    
    # Test results
    with pytest.raises(TypeError, match="Scenario ID must be an Integer"):
        myScenario.results(sid="5")
        
    with pytest.raises(ValueError, match="not a Results Scenario"):
        myScenario.results(sid=scn_id)
        
    assert isinstance(myScenario.results(), pd.DataFrame)
    assert (myScenario.results()["IsResult"] == "Yes").all()
    res_sid = myLibrary.scenarios().iloc[-1]["ScenarioId"].item()
    assert isinstance(myScenario.results(sid=res_sid), ps.Scenario) 
    
    # Test run_log
    myResultsScenario = myScenario.results(sid=res_sid)
    assert isinstance(myResultsScenario.run_log(), pd.DataFrame)
    assert not isinstance(myScenario.run_log(), pd.DataFrame)
    
    # Test datasheet_rasters
    with pytest.raises(TypeError, match="datasheet must be a String"):
        myResultsScenario.datasheet_rasters(datasheet=1, column="test")
        
    with pytest.raises(TypeError, match="column must be a String"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_test", column=1)
        
    with pytest.raises(TypeError, match="iteration must be an Integer"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_test", column="test",
                                           iteration="test")
        
    with pytest.raises(TypeError, match="timestep must be an Integer"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_test", column="test",
                                           timestep="test")
        
    with pytest.raises(RuntimeError,
                       match="The datasheet does not belong to this library: stsim_test"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_test", column="test")
        
    with pytest.raises(ValueError,
                       match="No raster columns found in Datasheet"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_OutputStratum")
    
    with pytest.raises(
            ValueError,
            match="Column test not found in Datasheet"):
        myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                           column="test")
        
    with pytest.raises(
            ValueError, 
            match="Specified iteration above range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          iteration=1000) 
       
    with pytest.raises(ValueError, match="iteration cannot be below 1"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          iteration=0)
       
    with pytest.raises(ValueError,
                       match="Some iteration values outside of range"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          iteration=[1, 2, 1000])  
       
    with pytest.raises(
            ValueError, 
            match="Specified timestep above range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          timestep=9999) 
       
    with pytest.raises(
            ValueError, 
            match="Specified timestep below range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          timestep=0) 
       
    with pytest.raises(ValueError,
                       match="Some timestep values outside of range"):
       myResultsScenario.datasheet_rasters(datasheet="stsim_OutputSpatialState",
                                          column="Filename",
                                          timestep=[1999, 2002, 2003])  
       
    with pytest.raises(
            ValueError, 
            match = "Must specify a filter_value to filter the filter_column"):
        myResultsScenario.datasheet_rasters(
            datasheet="stsim_OutputSpatialState",
            column = None,
            filter_column="OutputSpatialStateId") 
        
    with pytest.raises(
            ValueError, 
            match = "filter column test not in Datasheet"
            ):
        myResultsScenario.datasheet_rasters(
            datasheet="stsim_OutputSpatialState",
            column = None,
            filter_column="test",
            filter_value="test") 
       
    with pytest.raises(
            RuntimeError, 
            match="Cannot find a value for: test"):
        myResultsScenario.datasheet_rasters(
            datasheet="stsim_OutputSpatialState",
            column = None,
            filter_column="OutputSpatialStateId",
            filter_value="test") 
      
    raster1 = myResultsScenario.datasheet_rasters(
        datasheet="stsim_OutputSpatialState", column="Filename",
        iteration=1, timestep=2001)
    assert isinstance(raster1, ps.Raster)
    
    raster2 = myResultsScenario.datasheet_rasters(
        datasheet="stsim_OutputSpatialState", column="Filename")
    assert len(raster2) > 1
    assert all([isinstance(x, ps.Raster) for x in raster2])
    
    raster3 = myResultsScenario.datasheet_rasters(
        datasheet = "stsim_OutputSpatialState", 
        column = None,
        filter_column="Timestep",
        filter_value=2001)
    assert isinstance(raster3[0], ps.Raster)
    
    # Test raster class attributes
    assert os.path.isfile(raster1.source)
    assert isinstance(raster1.name, str)
    assert raster1.name.endswith(".it1.ts2001")
    assert isinstance(raster1.dimensions, dict)
    assert all([
        x in raster1.dimensions.keys() for x in [
            "height", "width", "cells"]])
    assert isinstance(raster1.extent, dict)
    assert all([
        x in raster1.extent.keys() for x in [
            "xmin", "xmax", "ymin", "ymax"]])    
    assert isinstance(raster1.crs, rasterio.crs.CRS)
    assert isinstance(raster1.values(), np.ndarray)
    assert isinstance(raster1.values(band=1), np.ndarray)
    
def test_scenario_copy_dep_delete():
    
    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=existing_lib_name, 
                           session=mySession,
                           forceUpdate=True)
    myScenario = myLibrary.scenarios(name="My Scenario")
    runcontrol = pd.DataFrame({
        "MinimumTimestep": [2000],
        "MaximumTimestep": [2015], 
        "MaximumIteration": [5]})
    myScenario.save_datasheet("stsim_RunControl", runcontrol)
    
    # Test copy
    with pytest.raises(TypeError, match="name must be a String"):
        myScenario.copy(name=1)
        
    myNewScn = myScenario.copy()
    assert myNewScn.name == "My Scenario - Copy"
    assert myNewScn.datasheets(name="stsim_RunControl").empty is False
    assert myNewScn.datasheets(
        name="stsim_RunControl")["MaximumIteration"].item() == 5
    
    myNewerScn = myScenario.copy(name="My Scenario 2")
    assert myNewerScn.name == "My Scenario 2"
    assert myNewerScn.datasheets(name="stsim_RunControl").empty is False
    assert myNewerScn.datasheets(
        name="stsim_RunControl")["MaximumIteration"].item() == 5
    
    # Test dependencies
    with pytest.raises(
            TypeError,
            match="dependency must be a Scenario, String, Integer, or List"):
        myNewScn.dependencies = 1.5
    
    assert myNewScn.dependencies.empty is True
    myNewScn.dependencies = myNewerScn
    assert myNewScn.dependencies.empty is False
    assert myNewScn.dependencies.Name.item() == "My Scenario 2"
    
    myNewScn.dependencies = None
    assert myNewScn.dependencies.empty is True
    
    myNewScn.dependencies = myNewerScn.name
    assert myNewScn.dependencies.empty is False

    myNewScn.dependencies = myNewerScn.name # should not throw error

    with pytest.raises(
            ValueError,
            match="Scenario dependency My Scenario 3 does not exist"):
        myNewScn.dependencies = [myNewerScn.name, "My Scenario 3"]
    
    sameNameScn = myScenario.copy(name="My Scenario 2")
    with pytest.raises(
            ValueError,
            match="dependency name not unique, use ID or Scenario"):
        myNewScn.dependencies = sameNameScn.name

    myNewScn.dependencies = [myNewerScn, sameNameScn]
    assert len(myNewScn.dependencies) == 2

    myNewScn.dependencies = None
    assert myNewScn.dependencies.empty is True
        
    # Test ignore_dependencies
    with pytest.raises(TypeError, match="value must be a String"):
        myNewScn.ignore_dependencies(value=1)
    
    assert math.isnan(myNewScn.ignore_dependencies())
    
    myNewScn.ignore_dependencies(value="stsim_RunControl")
    myNewScn.ignore_dependencies()
    
    assert myNewScn.ignore_dependencies() == "stsim_RunControl"
    
    myNewScn.ignore_dependencies(value="stsim_RunControl,stsim_DeterministicTransition")
    assert myNewScn.ignore_dependencies() == "stsim_RunControl,stsim_DeterministicTransition"
    
    # Test merge_dependencies
    with pytest.raises(TypeError, match="value must be a Logical"):
        myNewScn.merge_dependencies(value=1)
    
    assert myNewScn.merge_dependencies() == "No"
    
    myNewScn.merge_dependencies(value=True)
    assert myNewScn.merge_dependencies() == "Yes"
    
    # Test delete            
    myNewScn.delete(force=True)
    emptyResScn = myNewScn.run()
    assert emptyResScn is None
    
    # Delete other scenarios
    sameNameScn.delete(force=True)
    myNewerScn.delete(force=True)

def test_folder_functions():

    mySession = ps.Session(session_path)
    myLibrary = ps.library(name=test_lib_name, 
                           overwrite=True, 
                           session=mySession)
    myProject = myLibrary.projects("Definitions")

    df = myLibrary.folders()
    assert df.empty is True

    # Create folder object
    my_folder = myProject.folders(folder = "test")
    df = myLibrary.folders()
    assert df.empty is False
    assert len(df) == 1
    assert my_folder.name == "test"
    assert my_folder.parent_id is None
    assert my_folder.project_id is myProject.pid

    fid = my_folder.folder_id
    my_nested_folder = myProject.folders(folder = "test2", parent_folder = fid)
    df = myLibrary.folders()
    assert len(df) == 2
    assert my_nested_folder.name == "test2"
    assert my_nested_folder.parent_id is not None
    assert my_nested_folder.project_id is myProject.pid

    fid = my_folder.folder_id
    nested_fid = my_nested_folder.folder_id

    # Grab existing folder from id
    my_folder = myProject.folders(folder = fid)
    df = myLibrary.folders()
    assert len(df) == 2
    assert my_folder.name == "test"
    assert my_folder.folder_id == fid

    # Grab existing folder from name
    my_nested_folder = myProject.folders(folder = "test2")
    df = myLibrary.folders()
    assert len(df) == 2
    assert my_nested_folder.name == "test2"
    assert my_nested_folder.folder_id == nested_fid
    assert my_nested_folder.parent_id is not None

    # Move scenario into a folder
    my_scenario = myProject.scenarios(name = "test")
    scn_id = my_scenario.sid
    myScenario = myProject.scenarios(sid=scn_id)
    assert myScenario.folder_id is None
    myScenario.folder_id = fid
    assert myScenario.folder_id == fid

    # Create a new project and add a folder
    myProject2 = myLibrary.projects(name = "New Project")
    my_folder2 = myProject2.folders(folder = "test3")
    df = myLibrary.folders()
    assert len(df["ProjectId"].unique()) == 2
    assert my_folder2.project_id == myProject2.pid

    # Test project-subsetted folder data
    proj1_df = myProject.folders()
    proj2_df = myProject2.folders()
    assert proj1_df.empty is False
    assert proj2_df.empty is False
    assert proj1_df.equals(proj2_df) is False
    assert proj1_df["Id"].unique().tolist() != proj2_df["Id"].unique().tolist()
    assert proj1_df["ProjectId"].unique().item() == myProject.pid
    assert proj2_df["ProjectId"].unique().item() == myProject2.pid

    # Test readonly and publish attributes
    assert my_folder.readonly == "No"
    my_folder.readonly = "Yes"
    assert my_folder.readonly == "Yes"
    my_folder.readonly = False
    assert my_folder.readonly == "No"