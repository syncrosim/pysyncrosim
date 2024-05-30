import os
import pandas as pd

def runtime_data_folder(scenario, datasheet_name):
    """
    Creates a SyncroSim Datasheet data folder.

    Parameters
    ----------
    scenario : Scenario
        Scenario class instance.
    datasheet_name : String
        Name of SyncroSim Datasheet.

    Returns
    -------
    String
        Path to data folder.

    """
    _validate_environment()
    parent_folder = _environment.data_directory.item()
    
    return _create_scenario_folder(scenario, parent_folder, datasheet_name)

def runtime_temp_folder(folder_name):
    """
    Creates a SyncroSim Datasheet temporary folder.

    Parameters
    ----------
    folder_name : String
        Name of temporary folder.

    Returns
    -------
    String
        Path to temporary folder.

    """
    _validate_environment()
    return _create_temp_folder(folder_name)

def progress_bar(report_type="step", iteration=None, timestep=None,
                 total_steps=None, message=None):
    """
    Begins, steps, ends, and reports progress for a SyncroSim simulation.

    Parameters
    ----------
    report_type : String, optional
        Directive to "begin", "end", "report", "message", or "step" the
        simulation. The default is "step".
    iteration : Int, optional
        Number of iterations. The default is None.
    timestep : Int, optional
        Number of timesteps. The default is None.
    total_steps : Int, optional
        Number of total steps in the simulation. The default is None.
    message : String, optional
        A message to print to the progress bar status. The default is None.

    Raises
    ------
    TypeError
        If iteration, timestep, or total_steps are not Integers.
    ValueError
        If report_type is not "begin", "end", "step", "report", or "message".

    Returns
    -------
    None.

    """
    _validate_environment()
    
    # Begin progress bar tracking
    if report_type == "begin": 
        try:
            assert total_steps % 1 == 0
            total_steps = int(total_steps)
            print("ssim-task-start=%d\r\n" % total_steps, flush=True)
        except AssertionError or TypeError:
            raise TypeError("total_steps must be an Integer")
            
    # End progress bar tracking
    elif report_type == "end":
        print("ssim-task-end=True\r\n", flush=True)
        
    # Step progress bar
    elif report_type == "step":
        print("ssim-task-step=1\r\n", flush=True)
    
    # Report iteration and timestep
    elif report_type == "report":
        try:
            assert iteration % 1 == 0
            assert timestep % 1 == 0
            print(
                f"ssim-task-status=Simulating -> Iteration is {iteration}" +
                " - Timestep is {timestep}\r\n",
                flush=True)
        except AssertionError or TypeError:
            raise TypeError("iteration and timestep must be Integers")

    # Print arbitrary message
    elif report_type == "message":
        print(
            "ssim-task-status=" + str(message) + "\r\n",
            flush=True)
    else:
        raise ValueError("Invalid report_type")

def update_run_log(*message, sep="", type="status"):
    """
    Updates the run log for a SyncroSim simulation.

    Parameters
    ----------
    *message : String
        Message to write to the run log. Can be provided as multiple arguments
        that will be concatenated together using sep.
    sep : String, optional
        String to use if concatenating multiple message arguments. The default
        is an empty String.
    type : String
        Type of message to send to the run log. The default is "status", but
        can also be "warning" or "info".

    Raises
    ------
    ValueError
        If no message is provided.

    Returns
    -------
    None.

    """
    _validate_environment()
    
    # Check that a message is provided
    if len(message) == 0:
        raise ValueError("Please include a message to send to the run log.")
    
    # Concatenate additional message pieces
    if len(message) > 1:
        full_message = ""
        for m in message:
            full_message = full_message + str(sep) + str(m)
    else:
        full_message = message[0]

    # Split the message at line breaks
    split_message = full_message.split("\n")

    # Standardize surrounding empty lines
    if split_message[0] == "":
        split_message = split_message[1:]
    if split_message[-1] != "":
        split_message.append("")

    # Annotate messages
    annotated_message = ["ssim-task-log=" + m + "\r\n" for m in split_message]

    # Set type
    if type not in ["status", "warning", "info"]:
        raise ValueError("Invalid type")
    
    if type == "info":
        annotated_message[0] = annotated_message[0].replace("ssim-task-log", "ssim-task-info")
    elif type == "warning":
        annotated_message[0] = annotated_message[0].replace("ssim-task-log", "ssim-task-warning")

    # Send to SyncroSim
    for m in annotated_message:
        print(m, flush=True)

def _environment():
    env_df = pd.DataFrame(
        {"package_directory": [os.getenv("SSIM_PACKAGE_DIRECTORY")],
         "program_directory": [os.getenv("SSIM_PROGRAM_DIRECTORY")],
         "library_filepath": [os.getenv("SSIM_LIBRARY_FILEPATH")],
         "project_id": [int(os.getenv("SSIM_PROJECT_ID", default=-1))],
         "scenario_id": [int(os.getenv("SSIM_SCENARIO_ID", default=-1))],
         "data_directory": [os.getenv("SSIM_DATA_DIRECTORY")],
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

