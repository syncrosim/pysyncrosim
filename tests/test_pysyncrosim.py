import pysyncrosim as ps
import pytest
import pandas as pd
import math
import numpy as np
import os
import rasterio
# import re

def test_session_attributes():
    
    mySession = ps.Session()
    
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
    assert isinstance(mySession.packages(installed="BASE"), pd.DataFrame)
    
    with pytest.raises(TypeError,
                       match="installed must be Logical or 'BASE'"):
        mySession.packages(installed=1)
        
        
def test_session_package_functions():
    
    mySession = ps.Session()
    
    # Test add_packages, remove_packages, update_packages methods
    with pytest.raises(TypeError, match="packages must be a String or List"):
        mySession.add_packages(1)
    with pytest.raises(TypeError, match="packages must be a String or List"):
        mySession.remove_packages(1)
    with pytest.raises(TypeError, match="packages must be a String or List"):
        mySession.update_packages(1)
        
    with pytest.raises(TypeError, match="all packages must be Strings"):
        mySession.add_packages(["helloworldSpatial", 1])
    with pytest.raises(TypeError, match="all packages must be Strings"):
        mySession.remove_packages(["helloworldSpatial", 1])
    with pytest.raises(TypeError, match="all packages must be Strings"):
        mySession.update_packages(["helloworldSpatial", 1])
        
    mySession.add_packages("helloworldSpatial")
    assert "helloworldSpatial" in mySession.packages()["Name"].values
    
    mySession.remove_packages("helloworldSpatial")
    assert "helloworldSpatial" not in mySession.packages()["Name"].values
    
    mySession.add_packages("helloworldSpatial")
    
def test_helper():
    
    mySession = ps.Session()
    mySession.add_packages("stsim")
    
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
        ps.library(name="Test", session=1)
        
    with pytest.raises(TypeError, match="package must be a String"):
        ps.library(name="Test", package=1)
        
    with pytest.raises(TypeError, match="addons must be a String"):
        ps.library(name="Test", addons=1)
        
    with pytest.raises(TypeError, match="templates must be a String"):
        ps.library(name="Test", template=1)
        
    with pytest.raises(TypeError, match="forceUpdate must be a Logical"):
        ps.library(name="Test", forceUpdate="True")
        
    with pytest.raises(TypeError, match="overwrite must be a Logical"):
        ps.library(name="Test", overwrite="False")

    # Test package installation
    mySession.remove_packages("stsim")
    with pytest.raises(ValueError, match="The package stsim is not installed"):
        ps.library(name="Test", package="stsim", session=mySession)
    mySession.add_packages("stsim")
        
    # Test Library path
    with pytest.raises(ValueError, match="Path to Library does not exist"):
        ps.library("path/to/library")
        
    # Test template
    with pytest.raises(ValueError,
                       match="Template test does not exist in package"):
        ps.library("Test", template="test")
      
    # Test output
    myLibrary = ps.library(name="Test", forceUpdate=True)
    assert isinstance(myLibrary, ps.Library)
    
def test_library_attributes():
    
    myLibrary = ps.library(name="Test", overwrite=True)
    
    # Check attributes
    assert isinstance(myLibrary.name, str)
    assert isinstance(myLibrary.session, ps.Session)
    assert isinstance(myLibrary.location, str)
    assert os.path.isfile(myLibrary.location)
    assert isinstance(myLibrary.package, str)
    assert isinstance(myLibrary.addons, pd.DataFrame)

def test_library_projects():
    
    myLibrary = ps.library(name="Test", overwrite=True)
    
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
    
    myLibrary = ps.library(name="Test", overwrite=True)
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
    assert len(myLibrary.scenarios(pid=1, optional=True).columns) == 11
    assert myLibrary.scenarios(name="test", pid=1, overwrite=True).sid != 1
    assert all(myLibrary.scenarios(project=1) == myLibrary.scenarios(pid=1))
    assert all(
        myLibrary.scenarios(project="test") == myLibrary.scenarios(pid=1))
    myProject = myLibrary.projects("test")
    assert all(myLibrary.scenarios(
        project=1) == myLibrary.scenarios(project=myProject))
    
def test_library_datasheets():
    
    myLibrary = ps.library(name="Test", overwrite=True)
    
    # Test datasheets method inputs
    with pytest.raises(TypeError, match="name must be a String"):
        myLibrary.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical or 'CORE'"):
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
            RuntimeError,
            match="The data sheet does not exist: stsim_test"):
        myLibrary.datasheets(name="test")
        
    with pytest.raises(
            ValueError,
            match="filter column Test not in Datasheet stsim_RunControl"):
        myLibrary.datasheets(name="RunControl", filter_column="Test",
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
    
    myLibrary = ps.library(name="Test", overwrite=True)
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
    
    myLibrary = ps.library(name="Test")
    
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
        
    with pytest.raises(TypeError, match="scope must be a String"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame(), scope=1)
        
    with pytest.raises(RuntimeError,
                       match="The data sheet does not exist: stsim_test"):
        myLibrary.save_datasheet(name="test", data=pd.DataFrame())
        
    with pytest.raises(
            RuntimeError,
            match="The header references a column that does not belong"):
        random_df = pd.DataFrame({"col1": [1], "col2": [2]})
        myLibrary.save_datasheet(name="core_Backup", data=random_df)
    
    initial_core_backup = myLibrary.datasheets(name="core_Backup")
    assert initial_core_backup["IncludeOutput"].isna().values[0]
    
    initial_core_backup["IncludeOutput"] = "Yes"
    myLibrary.save_datasheet(name="core_Backup", data=initial_core_backup)
    modified_core_backup = myLibrary.datasheets(name="core_Backup")
    assert (modified_core_backup["IncludeOutput"] == "Yes").item()   
    
def test_library_run():
    
    mySession = ps.Session()
    mySession.add_packages("helloworldSpatial")
    myLibrary = ps.library(name="Test", package="helloworldSpatial",
                           template="example-library", overwrite=True,
                           forceUpdate=True)
    
    # Test run method
    with pytest.raises(
            TypeError,
            match="must be Scenario instance, String, Integer, or List"):
        myLibrary.run(scenarios=pd.DataFrame())

    with pytest.raises(
            TypeError,
            match="project must be Project instance, String, or Integer"):
        myLibrary.run(project=[1])
        
    with pytest.raises(
            TypeError,
            match="jobs must be an Integer"):
        myLibrary.run(jobs="1")
    
    runcontrol = myLibrary.datasheets("RunControl", True, False, False,
                                      "Scenario", None, None, False, False, 1)
    runcontrol["MaximumIteration"] = 2
    runcontrol["MaximumTimestep"] = 2
    myLibrary.save_datasheet("RunControl", runcontrol, "Scenario", 1)
    
    myLibrary.run()
    assert len(myLibrary.scenarios()) == 2
    assert myLibrary.scenarios().iloc[1]["IsResult"] == "Yes"
    
    myLibrary.run(project=1)
    assert len(myLibrary.scenarios()) == 3
    assert myLibrary.scenarios().iloc[2]["IsResult"] == "Yes"
    
    myLibrary.run(project=1, scenarios=1)
    assert len(myLibrary.scenarios()) == 4     
    assert myLibrary.scenarios().iloc[3]["IsResult"] == "Yes"
    
    myLibrary.projects(name="New Project")
    with pytest.raises(
            ValueError,
            match="Must specify project when > 1 Project in the Library"):
        myLibrary.run()
        
def test_library_addons_functions():
    
    myLibrary = ps.library(name="stsim_test", package="stsim", overwrite=True)
    
    # Test enable_addons method
    with pytest.raises(TypeError,
                       match="name must be a String or List of Strings"):
        myLibrary.enable_addons(name=1)
    
    with pytest.raises(TypeError,
                       match="all elements in name must be Strings"):
        myLibrary.enable_addons(name=[1, True])
        
    myLibrary.enable_addons("stsimsf")
    stsimsf_info = myLibrary.addons[myLibrary.addons["Name"] == "stsimsf"]
    assert stsimsf_info["Enabled"].item() == "Yes"    
    
    # Test disable_addons method
    with pytest.raises(TypeError,
                       match="name must be a String or List of Strings"):
        myLibrary.disable_addons(name=1)
    
    with pytest.raises(TypeError,
                       match="all elements in name must be Strings"):
        myLibrary.disable_addons(name=[1, True])
        
    myLibrary.disable_addons("stsimsf")
    stsimsf_info = myLibrary.addons[myLibrary.addons["Name"] == "stsimsf"]
    assert stsimsf_info["Enabled"].item() == "No" 
    
def test_project_attributes():
    
    myLibrary = ps.library(name="Test", package="helloworldSpatial",
                           overwrite=True)
    myProject = myLibrary.projects(name="Definitions")
    
    # Check attributes
    assert isinstance(myProject.pid, int)
    assert myProject.pid == 1
    assert isinstance(myProject.name, str)
    assert myProject.name == "Definitions"
    assert isinstance(myProject.library, ps.Library)
    
def test_project_scenarios():  
    
    myLibrary = ps.library(name="Test", package="helloworldSpatial",
                           overwrite=True)
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
    assert len(myProject.scenarios(optional=True).columns) == 11    
    assert isinstance(myProject.scenarios(name="test"), ps.Scenario)
    assert len(myProject.scenarios()) == 1
    assert isinstance(myProject.scenarios(sid=1), ps.Scenario)    

def test_project_datasheets():

    myLibrary = ps.library(name="Test", package="helloworldSpatial")
    myProject = myLibrary.projects(name="Definitions")
    
    # Test Datasheets
    with pytest.raises(TypeError, match="name must be a String"):
        myProject.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical or 'CORE'"):
        myProject.datasheets(summary="1")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myProject.datasheets(optional=1)
        
    with pytest.raises(TypeError, match="empty must be a Logical"):
        myProject.datasheets(empty=1)
        
    assert isinstance(myProject.datasheets(), pd.DataFrame)
    assert isinstance(myProject.datasheets(summary=False), list)
    assert myProject.datasheets(
        summary='CORE')["Name"].iloc[0].startswith("core")
    assert len(myProject.datasheets().columns) == 3
    assert len(myProject.datasheets(optional=True).columns) == 6
    assert myProject.datasheets(name="core_Transformer").empty is False
    assert myProject.datasheets(name="core_Transformer", empty=True).empty
    
def test_project_save_datasheet():
    
    myLibrary = ps.library(name="Test", package="helloworldSpatial")
    myProject = myLibrary.projects(name="Definitions")
    
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
        
    assert myProject.datasheets(name="core_AutoGenTag").empty
    test_datasheet = pd.DataFrame({"Name": ["test"], "AutoGenTagKey": ["key"],
                                  "AutoGenTagValue": [1]})
    myProject.save_datasheet(name="core_AutoGenTag", data=test_datasheet)
    assert myProject.datasheets(name="core_AutoGenTag").empty is False

def test_project_copy_delete():
    
    myLibrary = ps.library(name="Test", package="helloworldSpatial")
    myProject = myLibrary.projects(name="Definitions")

    # Test copy
    with pytest.raises(TypeError, match="name must be a String"):
        myProject.copy(name=1)
        
    myNewProj = myProject.copy()
    assert myNewProj.name == "Definitions - Copy"
    assert myNewProj.datasheets(name="core_AutoGenTag").empty is False
    
    myNewerProj = myProject.copy(name="Definitions 2")
    assert myNewerProj.name == "Definitions 2"
    assert myNewerProj.datasheets(name="core_AutoGenTag").empty is False
    
    # Test delete    
    with pytest.raises(
            TypeError,
            match="scenario must be a Scenario instance, Integer, or String"):
        myNewProj.delete(scenario=[1])  
        
    with pytest.raises(RuntimeError, match="The project does not exist"):
        myNewProj.delete(force=True)
        myNewProj.scenarios()
    

def test_scenarios_attributes():

    myLibrary = ps.library(name="Test", package="helloworldSpatial",
                           overwrite=True)
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
    
    myLibrary = ps.library(name="ds_test", package="helloworldSpatial",
                           overwrite=True, template="example-library",
                           forceUpdate=True)
    myScenario = myLibrary.scenarios(sid=1)
    
    # Test datasheets
    with pytest.raises(TypeError, match="name must be a String"):
        myScenario.datasheets(name=1)
        
    with pytest.raises(TypeError, match="summary must be a Logical or 'CORE'"):
        myScenario.datasheets(summary="1")
        
    with pytest.raises(TypeError, match="optional must be a Logical"):
        myScenario.datasheets(optional=1)
        
    with pytest.raises(TypeError, match="empty must be a Logical"):
        myScenario.datasheets(empty=1)
        
    assert isinstance(myScenario.datasheets(), pd.DataFrame)
    assert isinstance(myScenario.datasheets(summary=False), list)
    assert myScenario.datasheets(
        summary='CORE')["Name"].iloc[0].startswith("core")
    assert len(myScenario.datasheets().columns) == 3
    assert len(myScenario.datasheets(optional=True).columns) == 7
    assert isinstance(myScenario.datasheets(
        name="RunControl",
        filter_column="MinimumIteration", 
        filter_value="1"), pd.DataFrame)
    assert len(myScenario.datasheets(
        name="RunControl",
        filter_column="MinimumIteration",
        filter_value="1") == 1)
    assert myScenario.datasheets(
        name="RunControl",
        filter_column="MinimumIteration",
        filter_value="2").empty    
    assert myScenario.datasheets(name="InputDatasheet").empty is False
    assert myScenario.datasheets(name="InputDatasheet", empty=True).empty

def test_scenario_save_datasheet():

    myLibrary = ps.library(name="ds_test", package="helloworldSpatial",
                           overwrite=True, template="example-library",
                           forceUpdate=True)
    myScenario = myLibrary.scenarios(sid=1)    

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
        
    runcontrol = myScenario.datasheets(name="RunControl")
    runcontrol["MaximumIteration"] = 2
    runcontrol["MaximumTimestep"] = 2
    myScenario.save_datasheet("RunControl", runcontrol)

    assert myScenario.datasheets(
        name="RunControl")["MaximumIteration"].item() == 2
    assert myScenario.datasheets(
        name="RunControl")["MaximumTimestep"].item() == 2
    
def test_scenario_run_and_results():
    
    myLibrary = ps.library(name="Test", overwrite=True,
                           package="helloworldSpatial",
                           template="example-library",
                           forceUpdate=True)
    myScenario = myLibrary.scenarios(sid=1)
    runcontrol = myScenario.datasheets(name="RunControl")
    runcontrol["MaximumIteration"] = 2
    runcontrol["MaximumTimestep"] = 2
    myScenario.save_datasheet("RunControl", runcontrol)
    
    # Test run
    with pytest.raises(TypeError, match="jobs must be an Integer"):
        myScenario.run(jobs="1")
        
    myScenario.run(jobs=2)
    assert len(myLibrary.scenarios()) == 2 
    assert myLibrary.scenarios().iloc[1]["IsResult"] == "Yes"
    
    # Test results
    with pytest.raises(TypeError, match="Scenario ID must be an Integer"):
        myScenario.results(sid="5")
        
    with pytest.raises(ValueError, match="not a Results Scenario"):
        myScenario.results(sid=1)
        
    assert isinstance(myScenario.results(), pd.DataFrame)
    assert (myScenario.results()["IsResult"] == "Yes").all()
    res_sid = myLibrary.scenarios().iloc[1]["ScenarioID"].item()
    assert isinstance(myScenario.results(sid=res_sid), ps.Scenario) 
    
    # Test run_log
    myResultsScenario = myScenario.results(sid=res_sid)
    assert isinstance(myResultsScenario.run_log(), pd.DataFrame)
    assert not isinstance(myScenario.run_log(), pd.DataFrame)
    
    # Test datasheet_rasters
    with pytest.raises(TypeError, match="datasheet must be a String"):
        myResultsScenario.datasheet_rasters(datasheet=1, column="test")
        
    with pytest.raises(TypeError, match="column must be a String"):
        myResultsScenario.datasheet_rasters(datasheet="test", column=1)
        
    with pytest.raises(TypeError, match="iteration must be an Integer"):
        myResultsScenario.datasheet_rasters(datasheet="test", column="test",
                                           iteration="test")
        
    with pytest.raises(TypeError, match="timestep must be an Integer"):
        myResultsScenario.datasheet_rasters(datasheet="test", column="test",
                                           timestep="test")
        
    with pytest.raises(ValueError,
                       match="Scenario must be a Results Scenario"):
        myScenario.datasheet_rasters(datasheet="test", column="test")
        
    with pytest.raises(RuntimeError,
                       match="The data sheet does not exist"):
        myResultsScenario.datasheet_rasters(datasheet="test", column="test")
        
    with pytest.raises(ValueError,
                       match="No raster columns found in Datasheet"):
        myResultsScenario.datasheet_rasters(datasheet="OutputDatasheet")
    
    with pytest.raises(
            ValueError,
            match="Column test not found in Datasheet"):
        myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                           column="test")
        
    with pytest.raises(
            ValueError, 
            match="Specified iteration above range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          iteration=3) 
       
    with pytest.raises(ValueError, match="iteration cannot be below 1"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          iteration=0)
       
    with pytest.raises(ValueError,
                       match="Some iteration values outside of range"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          iteration=[1, 2, 3])  
       
    with pytest.raises(
            ValueError, 
            match="Specified timestep above range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          timestep=3) 
       
    with pytest.raises(
            ValueError, 
            match="Specified timestep below range of plausible values"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          timestep=0) 
       
    with pytest.raises(ValueError,
                       match="Some timestep values outside of range"):
       myResultsScenario.datasheet_rasters(datasheet="IntermediateDatasheet",
                                          column="OutputRasterFile",
                                          timestep=[1, 2, 3])  
       
    with pytest.raises(
            ValueError, 
            match = "Must specify a filter_value to filter the filter_column"):
        myResultsScenario.datasheet_rasters(
            datasheet="IntermediateDatasheet",
            column = None,
            filter_column="IntermediateDatasheetID") 
        
    with pytest.raises(
            ValueError, 
            match = "filter column test not in Datasheet"
            ):
        myResultsScenario.datasheet_rasters(
            datasheet="IntermediateDatasheet",
            column = None,
            filter_column="test",
            filter_value="test") 
       
    with pytest.raises(
            RuntimeError, 
            match="Cannot find a value for: test"):
        myResultsScenario.datasheet_rasters(
            datasheet="IntermediateDatasheet",
            column = None,
            filter_column="IntermediateDatasheetID",
            filter_value="test") 
      
    raster1 = myResultsScenario.datasheet_rasters(
        datasheet="IntermediateDatasheet", column="OutputRasterFile",
        iteration=1, timestep=1)
    assert isinstance(raster1, ps.Raster)
    
    raster2 = myResultsScenario.datasheet_rasters(
        datasheet="IntermediateDatasheet", column="OutputRasterFile")
    assert len(raster2) == 4
    assert all([isinstance(x, ps.Raster) for x in raster2])
    
    raster3 = myResultsScenario.datasheet_rasters(
        datasheet = "IntermediateDatasheet", 
        column = None,
        filter_column="IntermediateDatasheetID",
        filter_value=2)
    assert isinstance(raster3, ps.Raster)
    
    # Test raster class attributes
    assert os.path.isfile(raster1.source)
    assert isinstance(raster1.name, str)
    assert raster1.name.endswith(".it1.ts1")
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
    
    myLibrary = ps.library(name="Test", package="helloworldSpatial",
                           overwrite=True, template="example-library",
                           forceUpdate=True)
    myScenario = myLibrary.scenarios(name="My Scenario")
    runcontrol = myScenario.datasheets(name="RunControl")
    runcontrol["MaximumIteration"] = 2
    runcontrol["MaximumTimestep"] = 2
    myScenario.save_datasheet("RunControl", runcontrol)
    
    # Test copy
    with pytest.raises(TypeError, match="name must be a String"):
        myScenario.copy(name=1)
        
    myNewScn = myScenario.copy()
    assert myNewScn.name == "My Scenario - Copy"
    assert myNewScn.datasheets(name="RunControl").empty is False
    assert myNewScn.datasheets(
        name="RunControl")["MaximumIteration"].item() == 2
    
    myNewerScn = myScenario.copy(name="My Scenario 2")
    assert myNewerScn.name == "My Scenario 2"
    assert myNewerScn.datasheets(name="RunControl").empty is False
    assert myNewerScn.datasheets(
        name="RunControl")["MaximumIteration"].item() == 2
    
    # Test dependencies
    with pytest.raises(
            TypeError,
            match="dependency must be a Scenario, String, Integer, or List"):
        myNewScn.dependencies(dependency=1.5)
        
    with pytest.raises(
            TypeError,
            match="remove must be a Logical"):
        myNewScn.dependencies(dependency=myNewerScn.sid, remove="True")
    
    assert myNewScn.dependencies().empty is True
    myNewScn.dependencies(dependency=myNewerScn)
    assert myNewScn.dependencies().empty is False
    assert myNewScn.dependencies().Name.item() == "My Scenario 2"
    
    myNewScn.dependencies(dependency=myNewerScn.sid, remove=True, force=True)
    assert myNewScn.dependencies().empty is True
    
    myNewScn.dependencies(dependency=myNewerScn.name)
    assert myNewScn.dependencies().empty is False
    
    sameNameScn = myScenario.copy(name="My Scenario 2")
    with pytest.raises(
            ValueError,
            match="dependency name not unique, use ID or Scenario"):
        myNewScn.dependencies(dependency=sameNameScn.name)
        
    # Test ignore_dependencies
    with pytest.raises(TypeError, match="value must be a String"):
        myNewScn.ignore_dependencies(value=1)
    
    assert math.isnan(myNewScn.ignore_dependencies())
    
    myNewScn.ignore_dependencies(value="RunControl")
    myNewScn.ignore_dependencies()
    
    assert myNewScn.ignore_dependencies() == "'RunControl'"
    
    myNewScn.ignore_dependencies(value="InputDatasheet,OutputDatasheet")
    assert myNewScn.ignore_dependencies() == "'InputDatasheet,OutputDatasheet'"
    
    # Test merge_dependencies
    with pytest.raises(TypeError, match="value must be a Logical"):
        myNewScn.merge_dependencies(value=1)
    
    assert myNewScn.merge_dependencies() == "No"
    
    myNewScn.merge_dependencies(value=True)
    assert myNewScn.merge_dependencies() == "Yes"
    
    # Test delete            
    with pytest.raises(RuntimeError, match="The scenario does not exist"):
        myNewScn.delete(force=True)
        myNewScn.run()
    