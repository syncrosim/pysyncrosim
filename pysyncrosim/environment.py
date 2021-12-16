import os
import pandas as pd
import numpy as np
import re

def runtime_input_folder(scenario, datasheet_name):
    # Creates and returns a SyncroSim Datasheet input folder
    _validate_environment()
    parent_folder = _environment.input_directory.item()
    return _create_scenario_folder(scenario, parent_folder, datasheet_name)

def runtime_output_folder(scenario, datasheet_name):
    # Creates and returns a SyncroSim Datasheet output folder
    _validate_environment()
    parent_folder = _environment.output_directory.item()
    return _create_scenario_folder(scenario, parent_folder, datasheet_name)

def runtime_temp_folder(folder_name):
    # Creates and returns a SyncroSim Temporary Folder
    _validate_environment()
    return _create_temp_folder(folder_name)

def progress_bar(report_type="step", iteration=None, timestep=None,
                 total_steps=None):
    # Begins, steps, ends, and reports progress for a SyncroSim simulation
    _validate_environment()
    
    # Begin progress bar tracking
    if report_type == "begin": 
        if isinstance(total_steps, int) or isinstance(total_steps, np.int64):
            print("ssim-task-start=%d\r\n" % total_steps, flush=True)
        else:
            raise TypeError("total_steps must be an Integer")
            
    # End progress bar tracking
    elif report_type == "end":
        print("ssim-task-end=True\r\n", flush=True)
        
    # Step progress bar
    elif report_type == "step":
        print("ssim-task-step=1\r\n", flush=True)
    
    # Report iteration and timestep
    elif report_type == "report":
        if isinstance(iteration, int) or isinstance(iteration, np.int64) or \
            isinstance(timestep, int) or isinstance(timestep, np.int64):
                print(
                    f"ssim-task-status=Simulating -> Iteration is {iteration} - Timestep is {timestep}\r\n",
                    flush=True)
        else:
            raise TypeError("iteration and timestep must be Integers")
    else:
        raise ValueError("Invalid report_type")
                                

def _environment():
    env_df = pd.DataFrame(
        {"package_directory": [os.getenv("SSIM_PACKAGE_DIRECTORY")],
         "program_directory": [os.getenv("SSIM_PROGRAM_DIRECTORY")],
         "library_filepath": [os.getenv("SSIM_LIBRARY_FILEPATH")],
         "project_id": [int(os.getenv("SSIM_PROJECT_ID", default=-1))],
         "scenario_id": [int(os.getenv("SSIM_SCENARIO_ID", default=-1))],
         "input_directory": [os.getenv("SSIM_INPUT_DIRECTORY")],
         "output_directory": [os.getenv("SSIM_OUTPUT_DIRECTORY")],
         "temp_directory": [os.getenv("SSIM_TEMP_DIRECTORY")],
         "transfer_directory": [os.getenv("SSIM_TRANSFER_DIRECTORY")],
         "before_iteration": [
             int(os.getenv("SSIM_STOCHASTIC_TIME_BEFORE_ITERATION",
                           default=-1))],
         "after_iteration": [
             int(os.getenv("SSIM_STOCHASTIC_TIME_AFTER_ITERATION",
                           default=-1))],
         "before_timestep": [
             int(os.getenv("SSIM_STOCHASTIC_TIME_BEFORE_TIMESTEP",
                           default=-1))],
         "after_timestep": [
             int(os.getenv("SSIM_STOCHASTIC_TIME_AFTER_TIMESTEP",
                           default=-1))]})
    return env_df
    
def _validate_environment():
    e = _environment()
    
    if e.program_directory.item() is None:
        raise RuntimeError("This function requires a SyncroSim environment")
        
def _create_scenario_folder(scenario, parent_folder, datasheet_name):
    sidpart = "Scenario-" + str(scenario.sid)
    # p = re.sub("\\", "/", parent_folder)
    f = os.path.join(parent_folder, sidpart, datasheet_name)
    
    if not os.path.isdir(f):
        os.mkdir(f)
        
    return f

def _create_temp_folder(folder_name):
    t = _environment().temp_directory.item()
    # p = re.sub("\\\\", "/", t)
    f = os.path.join(t, folder_name)
    
    if not os.path.isdir(f):
        os.mkdir(f)
        
    return f

